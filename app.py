"""
app.py — the local server. Run this, open the dashboard, click Refresh, get real leads.

    python3 app.py

Then open http://127.0.0.1:5000 in your browser.

No cloud, no hosting bill, no n8n. Everything runs on your own machine and the
leads are stored in a local SQLite file (leads.db) so nothing is lost when you
close it.
"""

import csv
import io
import json
import os
import sqlite3
import traceback
from datetime import datetime

from flask import Flask, Response, jsonify, request, send_from_directory

import engine
import messages

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "leads.db")
CONFIG_PATH = os.path.join(HERE, "config.json")

app = Flask(__name__, static_folder=None)


# ─────────────────────────── settings (no terminal needed) ────────────────────

DEFAULT_CONFIG = {
    "name": "Agrajeet",
    "portfolio": "",
    "turnaround": "5 days",
    "email": "",
    "ai_provider": "openai",       # "openai" or "anthropic" — pick in Settings
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "anthropic_api_key": "",
    "anthropic_model": "claude-sonnet-5",
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


# ─────────────────────────── database ─────────────────────────────────────────

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT, niche TEXT, city TEXT, country TEXT, address TEXT,
                phone TEXT, email TEXT, website TEXT, socials TEXT,
                opening_hours TEXT, lat REAL, lon REAL, osm_url TEXT,
                reason TEXT, score INTEGER, reachability TEXT,
                stage TEXT DEFAULT 'New', notes TEXT DEFAULT '',
                found_at TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stage ON leads(stage)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_niche ON leads(niche)")
        # migrate old databases in place — safe to run every startup
        for col in ("owner TEXT DEFAULT ''", "verified_date TEXT DEFAULT ''",
                    "starred INTEGER DEFAULT 0", "links_ok TEXT DEFAULT '{}'"):
            try:
                conn.execute(f"ALTER TABLE leads ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass  # column already exists


def row_to_lead(r):
    d = dict(r)
    for jf in ("socials", "links_ok"):
        try:
            d[jf] = json.loads(d.get(jf) or "{}")
        except Exception:
            d[jf] = {}
    return d


def save_leads(leads):
    """Insert new leads. Existing ones are left alone so we never wipe your pipeline stage."""
    new = 0
    with db() as conn:
        for l in leads:
            exists = conn.execute("SELECT 1 FROM leads WHERE id=?", (l["id"],)).fetchone()
            if exists:
                continue
            conn.execute("""
                INSERT INTO leads (id,name,niche,city,country,address,phone,email,website,
                                   socials,opening_hours,lat,lon,osm_url,reason,score,
                                   reachability,owner,verified_date,links_ok,stage,found_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'New',?)
            """, (
                l["id"], l["name"], l["niche"], l["city"], l.get("country", ""),
                l.get("address", ""), l.get("phone", ""), l.get("email", ""),
                l.get("website", ""), json.dumps(l.get("socials", {})),
                l.get("opening_hours", ""), l.get("lat"), l.get("lon"),
                l.get("osm_url", ""), l.get("reason", ""), l.get("score", 0),
                l.get("reachability", ""), l.get("owner", ""), l.get("verified_date", ""),
                json.dumps(l.get("links_ok", {})),
                datetime.utcnow().isoformat(timespec="seconds"),
            ))
            new += 1
    return new


# ─────────────────────────── routes ───────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(HERE, "dashboard.html")


@app.route("/api/niches")
def api_niches():
    cfg = load_config()
    provider = cfg.get("ai_provider", "openai")
    key = cfg.get("anthropic_api_key") if provider == "anthropic" else cfg.get("openai_api_key")
    return jsonify({
        "niches": sorted(engine.NICHES.keys()),
        "has_openai": bool(key or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")),
    })


@app.route("/api/health")
def api_health():
    """Lets the dashboard tell 'server busy with a search' apart from 'server gone'."""
    return jsonify({"ok": True})


CITIES_CACHE = os.path.join(HERE, "cities_cache.json")
CITIES_SEED = os.path.join(HERE, "cities_seed.json")


def _load_json(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


@app.route("/api/cities")
def api_cities():
    """
    Towns + cities for the picked country (biggest first). Three tiers, fastest
    first: bundled seed file (instant, offline), local cache from an earlier
    live fetch, then a live OSM fetch that gets cached for next time.
    """
    country = (request.args.get("country") or "").strip()
    refresh = bool(request.args.get("refresh"))
    if not country:
        return jsonify({"error": "country required"}), 400

    cache = _load_json(CITIES_CACHE)
    if not refresh and country in cache and cache[country]:
        return jsonify({"cities": cache[country], "source": "cache"})

    seed = _load_json(CITIES_SEED)
    if not refresh and country in seed and seed[country]:
        return jsonify({"cities": seed[country], "source": "seed"})

    try:
        cities = engine.list_cities(country)
    except engine.LeadFinderError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Town lookup failed: {e}"}), 500
    cache[country] = cities
    try:
        with open(CITIES_CACHE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass
    return jsonify({"cities": cities, "source": "live"})


@app.route("/api/brief", methods=["POST"])
def api_brief():
    """One-click business brief — copy-paste it into any AI to build their site."""
    body = request.get_json(force=True) or {}
    with db() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id=?", (body.get("id"),)).fetchone()
    if not row:
        return jsonify({"error": "Lead not found"}), 404
    lead = row_to_lead(row)
    use_ai = bool(body.get("ai"))

    site_text = ""
    if use_ai and lead.get("website"):
        # only the AI mode scrapes their live site — local mode stays instant
        try:
            import re as _re
            raw = engine._http(lead["website"] if lead["website"].startswith("http")
                               else "http://" + lead["website"], timeout=8)
            raw = _re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=_re.S | _re.I)
            site_text = _re.sub(r"<[^>]+>", " ", raw)
            site_text = _re.sub(r"\s+", " ", site_text).strip()[:4000]
        except Exception:
            site_text = ""

    text, source = messages.build_brief(lead, site_text, use_ai=use_ai)
    return jsonify({"brief": text, "source": source})


@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    """Never sends raw keys back to the browser — only whether they're set."""
    cfg = load_config()
    return jsonify({
        "name": cfg.get("name", ""),
        "portfolio": cfg.get("portfolio", ""),
        "turnaround": cfg.get("turnaround", ""),
        "email": cfg.get("email", ""),
        "ai_provider": cfg.get("ai_provider", "openai"),
        "openai_model": cfg.get("openai_model", "gpt-4o-mini"),
        "anthropic_model": cfg.get("anthropic_model", "claude-sonnet-5"),
        "has_openai_key": bool(cfg.get("openai_api_key")),
        "has_anthropic_key": bool(cfg.get("anthropic_api_key")),
    })


@app.route("/api/settings", methods=["POST"])
def api_settings_post():
    """
    Saves settings from the dashboard's Settings panel — this is what replaces
    typing `export MY_NAME=...` etc. in a terminal.
    Leaving a key field blank keeps whatever key was saved before.
    """
    body = request.get_json(force=True) or {}
    cfg = load_config()
    for k in ("name", "portfolio", "turnaround", "email",
              "ai_provider", "openai_model", "anthropic_model"):
        if k in body:
            cfg[k] = body[k]
    for k in ("openai_api_key", "anthropic_api_key"):
        if body.get(k):  # only overwrite if they actually typed one
            cfg[k] = body[k]
    save_config(cfg)
    messages.apply_settings(cfg)
    active_key = cfg.get("anthropic_api_key") if cfg.get("ai_provider") == "anthropic" \
        else cfg.get("openai_api_key")
    return jsonify({
        "ok": True,
        "has_openai_key": bool(cfg.get("openai_api_key")),
        "has_anthropic_key": bool(cfg.get("anthropic_api_key")),
        "ai_ready": bool(active_key),
    })


@app.route("/api/search", methods=["POST"])
def api_search():
    """The Refresh button lands here. Goes out to OpenStreetMap live."""
    body = request.get_json(force=True) or {}
    niche = body.get("niche", "Barber Shop")
    place = (body.get("place") or "").strip()
    mode = body.get("mode", "no_website")
    limit = int(body.get("limit", 60))

    if not place:
        return jsonify({"error": "Type a city and country, e.g. 'Leeds, United Kingdom'."}), 400

    try:
        result = engine.find_leads(niche, place, limit=limit, mode=mode)
    except engine.LeadFinderError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Search failed: {e}"}), 500

    added = save_leads(result["leads"])
    result["new_leads"] = added
    result["duplicates"] = len(result["leads"]) - added
    # exact city/country labels as stored, so the UI can scope the list to
    # precisely what was just searched instead of showing the whole database
    result["filter_city"] = result["leads"][0]["city"] if result["leads"] else ""
    result["filter_country"] = result["leads"][0].get("country", "") if result["leads"] else ""
    result["filter_niche"] = niche
    return jsonify(result)


def _lead_filters(args):
    """Shared WHERE builder so the list and the CSV export always agree."""
    params, where = [], []
    for field in ("niche", "country", "city", "stage"):
        v = args.get(field)
        if v:
            where.append(f"{field}=?")
            params.append(v)
    if args.get("starred"):
        where.append("starred=1")
    search = args.get("q")
    if search:
        where.append("(name LIKE ? OR city LIKE ?)")
        params += [f"%{search}%", f"%{search}%"]
    return (" WHERE " + " AND ".join(where)) if where else "", params


@app.route("/api/leads")
def api_leads():
    clause, params = _lead_filters(request.args)
    q = "SELECT * FROM leads" + clause + " ORDER BY starred DESC, score DESC, name ASC"

    with db() as conn:
        rows = conn.execute(q, params).fetchall()
        # stage counts must reflect the SAME filter the user is looking at,
        # otherwise the stat strip contradicts the list underneath it
        stats = conn.execute(
            "SELECT stage, COUNT(*) c FROM leads" + clause + " GROUP BY stage", params
        ).fetchall()
        star_clause = clause + (" AND starred=1" if clause else " WHERE starred=1")
        starred_total = conn.execute(
            "SELECT COUNT(*) FROM leads" + star_clause, params
        ).fetchone()[0]
        total_all = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        facets = {
            "niches": [r[0] for r in conn.execute("SELECT DISTINCT niche FROM leads ORDER BY 1")],
            "countries": [r[0] for r in conn.execute("SELECT DISTINCT country FROM leads WHERE country<>'' ORDER BY 1")],
            "cities": [r[0] for r in conn.execute("SELECT DISTINCT city FROM leads WHERE city<>'' ORDER BY 1")],
        }
    return jsonify({
        "leads": [row_to_lead(r) for r in rows],
        "stages": {r["stage"]: r["c"] for r in stats},
        "starred_total": starred_total,
        "total_all": total_all,
        "facets": facets,
    })


@app.route("/api/lead/<lead_id>", methods=["PATCH"])
def api_update(lead_id):
    body = request.get_json(force=True) or {}
    fields = {k: v for k, v in body.items() if k in ("stage", "notes", "phone", "email", "starred")}
    if not fields:
        return jsonify({"error": "Nothing to update"}), 400
    sets = ", ".join(f"{k}=?" for k in fields)
    with db() as conn:
        conn.execute(f"UPDATE leads SET {sets} WHERE id=?", list(fields.values()) + [lead_id])
    return jsonify({"ok": True})


@app.route("/api/lead/<lead_id>", methods=["DELETE"])
def api_delete(lead_id):
    with db() as conn:
        conn.execute("DELETE FROM leads WHERE id=?", (lead_id,))
    return jsonify({"ok": True})


@app.route("/api/message", methods=["POST"])
def api_message():
    body = request.get_json(force=True) or {}
    lead_id = body.get("id")
    kind = body.get("kind", "fb")
    use_ai = bool(body.get("ai"))

    with db() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
    if not row:
        return jsonify({"error": "Lead not found"}), 404
    lead = row_to_lead(row)

    if use_ai:
        text, source = messages.ai_rewrite(lead, kind)
    else:
        text, source = messages.build(lead, kind), "template"
    return jsonify({"message": text, "source": source})


@app.route("/api/export.csv")
def api_export():
    # honour the exact same filters the user has applied on screen, so an
    # export of "Estate Agent in Los Angeles" is not the whole database
    clause, params = _lead_filters(request.args)
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM leads" + clause + " ORDER BY starred DESC, score DESC", params
        ).fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Name", "Starred", "Owner/Operator", "Niche", "City", "Country", "Address",
                "Phone", "Email", "Website", "Facebook", "FB link live", "Instagram",
                "IG link live", "WhatsApp", "Why they qualify", "Data verified",
                "Score", "Reachability", "Stage", "Notes", "Found"])
    def _lk(v):
        return {True: "live", False: "broken"}.get(v, "unchecked")
    for r in rows:
        d = dict(r)
        soc = json.loads(d.get("socials") or "{}")
        lk = json.loads(d.get("links_ok") or "{}")
        w.writerow([d["name"], "yes" if d.get("starred") else "", d.get("owner", ""),
                    d["niche"], d["city"], d["country"], d["address"], d["phone"],
                    d["email"], d["website"], soc.get("facebook", ""),
                    _lk(lk.get("facebook")) if soc.get("facebook") else "",
                    soc.get("instagram", ""),
                    _lk(lk.get("instagram")) if soc.get("instagram") else "",
                    soc.get("whatsapp", ""), d["reason"], d.get("verified_date", ""),
                    d["score"], d["reachability"], d["stage"], d["notes"], d["found_at"]])
    return Response(
        buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


if __name__ == "__main__":
    init_db()
    messages.apply_settings(load_config())  # load saved name/portfolio/OpenAI key, if any
    key_status = "ON" if os.environ.get("OPENAI_API_KEY") else "off (templates only — still works)"
    print("\n" + "=" * 62)
    print("  LEAD FINDER — running locally")
    print("=" * 62)
    print(f"  Dashboard : http://127.0.0.1:5000")
    print(f"  Database  : {DB}")
    print(f"  AI rewrite: {key_status}")
    print(f"  Niches    : {len(engine.NICHES)} available")
    print("=" * 62 + "\n")
    # threaded=True is the fix for "the app freezes / won't reload during a
    # search": Flask's dev server is SINGLE-threaded by default, so a 40-second
    # OpenStreetMap search used to block every other request — including simply
    # reloading the page. With threads, searches run in parallel with the UI.
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
