"""
engine.py — finds real businesses worldwide that have no website.

Data source: OpenStreetMap (Overpass API + Nominatim geocoder).
Why OSM and not Google scraping:
  - Free, no API key, no billing account.
  - Legal to query and reuse (ODbL licence) — Google's TOS forbids scraping SERPs,
    and Google will CAPTCHA/ban a scraper within minutes anyway.
  - Businesses in OSM carry a `website` tag, so "has no website" is a real
    structured filter instead of something we have to guess at.
  - Global coverage, so this works in any country, not just US/UK.

India is deliberately excluded (see BLOCKED_COUNTRIES) per project scope.
"""

import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "LeadFinder/1.0 (small business website outreach tool)"

# Public Overpass mirrors. We try them in order — if one is busy (they rate-limit
# during peak hours) we fall through to the next instead of failing the request.
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

NOMINATIM = "https://nominatim.openstreetmap.org/search"

# India was excluded in v1. It is now supported — see INDIA_NOTE, which the API
# surfaces so the user knows OSM coverage there is thinner than in the West.
BLOCKED_COUNTRIES = set()

INDIA_NOTE = ("OpenStreetMap coverage in India is thinner than in the US/UK — expect fewer "
              "results per search and more businesses without tagged phone numbers. Metro "
              "areas (Mumbai, Delhi, Bengaluru, Pune, Hyderabad) are mapped far better than "
              "smaller towns. Try 'Both' mode to widen the net.")

# Friendly niche name -> the OSM tags that identify it.
# Each entry is a list of (key, value) pairs; we OR them together.
# Business taxonomy lives in categories.py — 258 trades, each mapped to OSM tags
# and to a matching Ripple Foundry demo template.
from categories import (NICHES, SEGMENTS, FOUNDRY, foundry_demo, foundry_app,  # noqa: E402
                        foundry_links, set_agency, encode_payload, decode_payload, segments)

# Tags that mean a business is permanently closed / gone. Any element carrying
# one of these (or a lifecycle prefix like disused:shop=bakery) is skipped, so
# you never cold-call a shut shop.
CLOSED_MARKERS = (
    "disused", "abandoned", "demolished", "razed", "removed", "closed",
    "was", "old", "historic",
)

# ISO codes for the town lookup — lets the dashboard list real towns per country
# so you never have to know city names yourself.
COUNTRY_ISO = {
    "United Kingdom": "GB", "United States": "US", "Australia": "AU", "Canada": "CA",
    "Ireland": "IE", "New Zealand": "NZ", "Germany": "DE", "France": "FR",
    "Spain": "ES", "Italy": "IT", "Netherlands": "NL", "Belgium": "BE",
    "Portugal": "PT", "Austria": "AT", "Switzerland": "CH", "Sweden": "SE",
    "Norway": "NO", "Denmark": "DK", "Finland": "FI", "Iceland": "IS",
    "Poland": "PL", "Czechia": "CZ", "Slovakia": "SK", "Hungary": "HU",
    "Romania": "RO", "Bulgaria": "BG", "Greece": "GR", "Croatia": "HR",
    "Slovenia": "SI", "Serbia": "RS", "Bosnia and Herzegovina": "BA",
    "North Macedonia": "MK", "Albania": "AL", "Montenegro": "ME", "Estonia": "EE",
    "Latvia": "LV", "Lithuania": "LT", "Ukraine": "UA", "Moldova": "MD",
    "Georgia": "GE", "Armenia": "AM", "Azerbaijan": "AZ", "Turkey": "TR",
    "Cyprus": "CY", "Malta": "MT", "Luxembourg": "LU", "Monaco": "MC",
    "Andorra": "AD", "United Arab Emirates": "AE", "Saudi Arabia": "SA",
    "Qatar": "QA", "Kuwait": "KW", "Bahrain": "BH", "Oman": "OM", "Jordan": "JO",
    "Lebanon": "LB", "Israel": "IL", "Egypt": "EG", "Morocco": "MA",
    "Tunisia": "TN", "Algeria": "DZ", "South Africa": "ZA", "Kenya": "KE",
    "Nigeria": "NG", "Ghana": "GH", "Tanzania": "TZ", "Uganda": "UG",
    "Ethiopia": "ET", "Rwanda": "RW", "Botswana": "BW", "Namibia": "NA",
    "Zambia": "ZM", "Zimbabwe": "ZW", "Mauritius": "MU", "Seychelles": "SC",
    "Japan": "JP", "South Korea": "KR", "Singapore": "SG", "Malaysia": "MY",
    "Thailand": "TH", "Vietnam": "VN", "Philippines": "PH", "Indonesia": "ID",
    "Taiwan": "TW", "Hong Kong": "HK", "Sri Lanka": "LK", "Nepal": "NP",
    "Bangladesh": "BD", "Pakistan": "PK", "Kazakhstan": "KZ", "Uzbekistan": "UZ",
    "Mexico": "MX", "Brazil": "BR", "Argentina": "AR", "Chile": "CL",
    "Colombia": "CO", "Peru": "PE", "Ecuador": "EC", "Uruguay": "UY",
    "Paraguay": "PY", "Bolivia": "BO", "Costa Rica": "CR", "Panama": "PA",
    "Guatemala": "GT", "Dominican Republic": "DO", "Jamaica": "JM",
    "Trinidad and Tobago": "TT", "Bahamas": "BS", "Barbados": "BB",
    "Fiji": "FJ", "Papua New Guinea": "PG", "India": "IN",
}

# ── mobile-number detection ───────────────────────────────────────────────
# A wa.me link only works for a mobile. Landlines produce a dead link and waste
# your time, so we work out which is which from the national numbering plan.
# This is prefix logic on a normalised number — no third-party lookup, no cost.
MOBILE_RULES = {
    "44": lambda n: n.startswith("7"),                        # UK   +44 7xxx
    "1":  lambda n: len(n) == 10,                             # US/CA no landline/mobile split
    "91": lambda n: n[:1] in "6789" and len(n) == 10,         # India +91 6-9
    "61": lambda n: n.startswith("4"),                        # Australia
    "64": lambda n: n.startswith("2"),                        # New Zealand
    "353": lambda n: n.startswith("8"),                       # Ireland
    "49": lambda n: n.startswith("1"),                        # Germany
    "33": lambda n: n[:1] in "67",                            # France
    "34": lambda n: n[:1] in "67",                            # Spain
    "39": lambda n: n.startswith("3"),                        # Italy
    "31": lambda n: n.startswith("6"),                        # Netherlands
    "971": lambda n: n.startswith("5"),                       # UAE
    "27": lambda n: n[:2] in ("60", "61", "62", "63", "64", "65", "66", "67",
                              "68", "71", "72", "73", "74", "76", "78", "79",
                              "81", "82", "83", "84"),        # South Africa
}
CC_BY_ISO = {
    "gb": "44", "us": "1", "ca": "1", "in": "91", "au": "61", "nz": "64",
    "ie": "353", "de": "49", "fr": "33", "es": "34", "it": "39", "nl": "31",
    "ae": "971", "za": "27", "sg": "65", "my": "60", "pk": "92", "bd": "880",
    "lk": "94", "np": "977", "ph": "63", "id": "62", "th": "66", "vn": "84",
}


def maps_links(name, lat, lon, address="", city=""):
    """
    Google Maps verification links built from the coordinates OSM already gives
    us. No API key, no scraping, no rate limit — these are just deep links the
    user clicks, so Google sees an ordinary browser visit.

    Three links, because they answer three different questions:
      verify  — is this business really here, and what does Google know about it?
      pin     — exact OSM coordinate, to spot a mis-tagged location
      street  — Street View at the coordinate: does a shopfront actually exist?
    """
    out = {}
    if lat is None or lon is None:
        # no coordinates: fall back to a plain name search so the button still works
        if name:
            q = urllib.parse.quote_plus(" ".join(x for x in [name, address or city] if x))
            out["maps_verify"] = f"https://www.google.com/maps/search/?api=1&query={q}"
        return out

    ll = f"{float(lat):.6f},{float(lon):.6f}"
    # name searched *at* the coordinate — lands on the business pin when Google
    # has it, and on an empty map when it doesn't (which is itself a signal)
    label = " ".join(x for x in [name, address or city] if x).strip()
    out["maps_verify"] = (
        f"https://www.google.com/maps/search/{urllib.parse.quote(label)}/@{ll},18z"
        if label else f"https://www.google.com/maps/search/?api=1&query={ll}"
    )
    out["maps_pin"] = f"https://www.google.com/maps/search/?api=1&query={ll}"
    out["maps_street"] = (
        f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={ll}"
    )
    return out


def phone_channels(phone, country_code=""):
    """
    Work out how a phone number can actually be used.
    Returns {e164, whatsapp, tel, is_mobile} — whatsapp is a wa.me link with a
    prefilled slot, or "" when the number is a landline or can't be parsed.
    """
    if not phone:
        return {}
    raw = re.sub(r"[^\d+]", "", phone)
    if not raw:
        return {}

    if raw.startswith("+"):
        digits = raw[1:]
    elif raw.startswith("00"):
        digits = raw[2:]
    else:
        # national format — prepend the country's dialling code
        cc = CC_BY_ISO.get((country_code or "").lower(), "")
        digits = cc + raw.lstrip("0") if cc else raw.lstrip("0")

    cc = next((c for c in sorted(MOBILE_RULES, key=len, reverse=True)
               if digits.startswith(c)), "")
    national = digits[len(cc):] if cc else digits
    is_mobile = MOBILE_RULES[cc](national) if cc and national else None

    return {
        "e164": "+" + digits,
        "tel": "tel:+" + digits,
        "is_mobile": is_mobile,
        # unknown is treated as usable — better to offer the link than hide it
        "whatsapp": f"https://wa.me/{digits}" if is_mobile is not False else "",
    }


def _ctx():
    return ssl.create_default_context()


def _http(url, data=None, timeout=90):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return r.read().decode("utf-8", "replace")


class LeadFinderError(Exception):
    pass


# ─────────────────────────── geocoding ────────────────────────────────────────
# Two independent free geocoders. Nominatim is primary; if it's down or
# rate-limited we silently fall back to Photon (komoot) — different servers,
# same OSM data underneath, no key for either.

PHOTON = "https://photon.komoot.io/api/"


def _geocode_nominatim(place):
    qs = urllib.parse.urlencode({
        "q": place, "format": "json", "limit": 1, "addressdetails": 1,
    })
    results = json.loads(_http(f"{NOMINATIM}?{qs}", timeout=30))
    if not results:
        return None
    r = results[0]
    addr = r.get("address", {})
    bb = r.get("boundingbox")
    if not bb or len(bb) != 4:
        return None
    south, north, west, east = (float(x) for x in bb)
    return {
        "display_name": r.get("display_name", place),
        "country": addr.get("country", ""),
        "country_code": (addr.get("country_code") or "").lower(),
        "bbox": (south, west, north, east),
        "lat": float(r["lat"]),
        "lon": float(r["lon"]),
        "geocoder": "nominatim",
    }


def _geocode_photon(place):
    qs = urllib.parse.urlencode({"q": place, "limit": 1})
    data = json.loads(_http(f"{PHOTON}?{qs}", timeout=30))
    feats = data.get("features") or []
    if not feats:
        return None
    f = feats[0]
    props = f.get("properties", {})
    ext = props.get("extent")  # [west, north, east, south]
    if ext and len(ext) == 4:
        west, north, east, south = ext
    else:
        lon, lat = f["geometry"]["coordinates"]
        south, west, north, east = lat - 0.09, lon - 0.14, lat + 0.09, lon + 0.14
    lon, lat = f["geometry"]["coordinates"]
    return {
        "display_name": ", ".join(x for x in [props.get("name"), props.get("state"), props.get("country")] if x),
        "country": props.get("country", ""),
        "country_code": (props.get("countrycode") or "").lower(),
        "bbox": (south, west, north, east),
        "lat": lat,
        "lon": lon,
        "geocoder": "photon",
    }


def geocode(place):
    """Turn 'Leeds, UK' into a bounding box + country. Free, no API key.
    Tries Nominatim first, falls back to Photon so one busy server never
    blocks a search."""
    geo, last_err = None, None
    for fn in (_geocode_nominatim, _geocode_photon):
        try:
            geo = fn(place)
            if geo:
                break
        except Exception as e:
            last_err = e
    if not geo:
        if last_err:
            raise LeadFinderError(f"Both geocoders unreachable right now — try again in a minute. ({last_err})")
        raise LeadFinderError(
            f"Couldn't find '{place}'. Try a more specific form like 'Leeds, United Kingdom'."
        )

    if geo["country_code"] in BLOCKED_COUNTRIES:
        raise LeadFinderError(f"{geo['country']} is not currently supported.")
    return geo


# ─────────────────────────── overpass query ───────────────────────────────────

def _build_query(tag_pairs, bbox, limit):
    south, west, north, east = bbox
    box = f"({south},{west},{north},{east})"
    parts = []
    for key, val in tag_pairs:
        for kind in ("node", "way"):
            parts.append(f'  {kind}["{key}"="{val}"]["name"]{box};')
    body = "\n".join(parts)
    # `meta` includes each element's last-edit timestamp — a live-data freshness
    # signal we use to rank recently-verified businesses higher.
    return f"[out:json][timeout:90];\n(\n{body}\n);\nout center tags meta {limit};"


def _overpass(query):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for mirror in OVERPASS_MIRRORS:
        try:
            return json.loads(_http(mirror, data=data, timeout=150))
        except Exception as e:
            last = e
            time.sleep(1.5)  # mirrors rate-limit; give the next one a beat
    raise LeadFinderError(
        f"All OpenStreetMap mirrors were busy or unreachable. Try again in a minute. ({last})"
    )


# ─────────────────────────── parsing ──────────────────────────────────────────

SOCIAL_KEYS = {
    "facebook": ["contact:facebook", "facebook"],
    "instagram": ["contact:instagram", "instagram"],
    "twitter": ["contact:twitter", "twitter"],
    "whatsapp": ["contact:whatsapp", "whatsapp"],
}


def _first(tags, keys):
    for k in keys:
        v = tags.get(k)
        if v:
            return v.strip()
    return ""


def _social_url(kind, val):
    """OSM stores these inconsistently — sometimes a full URL, sometimes a handle."""
    if not val:
        return ""
    if val.startswith("http"):
        return val
    handle = val.lstrip("@/")
    base = {
        "facebook": "https://www.facebook.com/",
        "instagram": "https://www.instagram.com/",
        "twitter": "https://twitter.com/",
    }.get(kind, "")
    return base + handle if base else val


def _address(tags):
    bits = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
        tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:suburb", ""),
        tags.get("addr:postcode", ""),
    ]
    return " ".join(b for b in bits if b).strip()


CLOSED_NAME_HINTS = (
    "permanently closed", "closed down", "now closed", "ceased trading",
    "out of business", "under new management", "to let", "for lease",
    "coming soon", "opening soon", "site of former", "former ",
)


def _looks_closed(tags):
    """
    True if the OSM tags say this business is gone. Filters out permanently
    closed shops so you never pitch a shut door.

    Five independent signals — a business only has to trip one.
    """
    # 1. lifecycle prefixes: disused:shop=bakery, abandoned:amenity=cafe, was:shop=...
    for key in tags:
        if ":" in key and key.split(":", 1)[0] in CLOSED_MARKERS:
            return True

    # 2. explicit closure flags
    for flag in ("disused", "abandoned", "closed", "demolished", "razed"):
        if tags.get(flag) in ("yes", "true", "1"):
            return True

    # 3. vacant units and anything with an end date
    if tags.get("shop") in ("vacant", "empty") or tags.get("office") == "vacant":
        return True
    if tags.get("end_date") or tags.get("demolished:building"):
        return True
    if tags.get("building") in ("ruins", "ruin", "collapsed"):
        return True
    if tags.get("abandoned") or tags.get("ruins") == "yes":
        return True

    # 4. opening hours that say it never opens
    oh = (tags.get("opening_hours") or "").strip().lower()
    if oh in ("closed", "off", "no", "none"):
        return True

    # 5. the name itself announces it — surprisingly common in OSM
    name = (tags.get("name") or "").lower()
    if any(h in name for h in CLOSED_NAME_HINTS):
        return True

    # 6. under construction / not open yet — real, but not yet a customer
    if tags.get("construction") or tags.get("proposed") or tags.get("planned"):
        return True
    if tags.get("building") == "construction":
        return True

    return False


def _activity_signals(tags, edited):
    """
    Positive evidence the business is actually trading. Used both to rank and,
    in strict mode, to exclude listings that show no sign of life at all.
    Returns (count, list_of_reasons).
    """
    hits = []
    if tags.get("opening_hours") and tags["opening_hours"].strip().lower() not in ("closed", "off"):
        hits.append("opening hours listed")
    if tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile"):
        hits.append("phone listed")
    if any(k.startswith("contact:") for k in tags):
        hits.append("contact details tagged")
    if tags.get("check_date") or tags.get("survey:date"):
        hits.append("surveyed on the ground")
    if tags.get("addr:housenumber") and tags.get("addr:street"):
        hits.append("full street address")
    if tags.get("wheelchair") or tags.get("payment:cash") or tags.get("cuisine") \
            or tags.get("outdoor_seating") or tags.get("takeaway") or tags.get("delivery"):
        hits.append("operational detail tagged")
    if edited and edited >= "2023-01":
        hits.append("recently edited in OSM")
    return len(hits), hits


def parse_elements(elements, niche, place_label, country, country_code="", min_activity=0):
    out = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name:
            continue
        if _looks_closed(tags):
            continue

        website = _first(tags, ["website", "contact:website", "url", "contact:url"])
        phone = _first(tags, ["phone", "contact:phone", "contact:mobile", "mobile"])
        email = _first(tags, ["email", "contact:email"])
        # who actually runs the place, when the map data has it — useful for
        # opening a call with a real name instead of "hi, is this the owner?"
        owner = _first(tags, ["operator", "owner", "contact:person", "name:etymology"])

        socials = {}
        for kind, keys in SOCIAL_KEYS.items():
            v = _first(tags, keys)
            if v:
                socials[kind] = _social_url(kind, v)

        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")

        # freshness: prefer an explicit survey date, else the element's last edit
        last_seen = tags.get("check_date") or tags.get("survey:date") or ""
        edited = (el.get("timestamp") or "")[:10]

        # proof-of-life scoring — in strict mode, listings with no evidence of
        # trading at all are dropped rather than shown as leads
        act_count, act_reasons = _activity_signals(tags, edited)
        if min_activity and act_count < min_activity:
            continue

        ch = phone_channels(phone, country_code)
        if not ch.get("whatsapp"):
            # OSM sometimes carries a separate WhatsApp-only number
            wa = _first(tags, ["contact:whatsapp", "whatsapp"])
            if wa:
                wch = phone_channels(wa, country_code)
                if wch.get("whatsapp"):
                    ch = {**ch, "whatsapp": wch["whatsapp"], "e164": ch.get("e164") or wch["e164"]}

        out.append({
            "id": f"{el.get('type','n')}{el.get('id')}",
            "name": name,
            "niche": niche,
            "city": place_label,
            "country": country,
            "address": _address(tags),
            "phone": phone,
            "email": email,
            "owner": owner,
            "website": website,
            "socials": socials,
            "opening_hours": tags.get("opening_hours", ""),
            "verified_date": last_seen or edited,
            "lat": lat,
            "lon": lon,
            "osm_url": f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}",
            # new in v1.2
            "whatsapp": ch.get("whatsapp", ""),
            "phone_e164": ch.get("e164", ""),
            "is_mobile": ch.get("is_mobile"),
            "activity": act_count,
            "activity_reasons": act_reasons,
            # personalised Foundry previews — this business's own name, city,
            # phone and current site already inside the demo, ready to paste
            # straight into a DM
            **foundry_links(niche, business=name, city=place_label, phone=phone),
            "segment": SEGMENTS.get(niche, ""),
            # Google Maps verification, straight from the OSM coordinates
            **maps_links(name, lat, lon, _address(tags), place_label),
        })
    return out


# ─────────────────────────── town lookup per country ──────────────────────────

def list_cities(country, limit=400):
    """
    Every city + town OSM knows in a country, biggest first (by population tag
    where available). Feeds the dashboard's town dropdown so you can just pick
    instead of having to know place names.
    """
    iso = COUNTRY_ISO.get(country)
    if not iso:
        raise LeadFinderError(f"No ISO code on file for '{country}'.")
    q = (
        f'[out:json][timeout:60];'
        f'area["ISO3166-1"="{iso}"]["admin_level"="2"]->.c;'
        f'(node["place"="city"](area.c);node["place"="town"](area.c););'
        f'out tags {limit * 4};'
    )
    result = _overpass(q)
    seen, out = set(), []
    for el in result.get("elements", []):
        t = el.get("tags", {})
        # prefer the English name so the dropdown stays readable everywhere
        name = (t.get("name:en") or t.get("name") or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        try:
            pop = int(re.sub(r"\D", "", t.get("population", "") or "0") or 0)
        except ValueError:
            pop = 0
        out.append((pop, name))
    out.sort(key=lambda x: (-x[0], x[1]))
    return [n for _, n in out[:limit]]


# ─────────────────────────── social link verification ─────────────────────────

def verify_link(url, timeout=6):
    """
    Tri-state link check so you don't waste time on dead handles:
      True  -> link responds (safe to open and DM)
      False -> hard 4xx/5xx (dead handle / removed page)
      None  -> couldn't tell (site blocked the check) — treat as unverified, not broken
    """
    if not url:
        return None
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept-Language": "en",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return 200 <= r.status < 400
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429, 999):
            return None   # bot-blocked, not proof it's dead
        return False      # 404/410/5xx -> genuinely broken
    except Exception:
        return None


def verify_lead_links(leads, max_leads=40, budget=12.0):
    """
    Check social links + websites in parallel. Adds `links_ok`.
    Hard time budget: link checking is a nice-to-have, so it must never be the
    reason a search appears to hang. Anything not finished in `budget` seconds
    is simply left unverified.
    """
    jobs = []
    for l in leads[:max_leads]:
        for kind, url in (l.get("socials") or {}).items():
            if kind in ("facebook", "instagram"):
                jobs.append((l, kind, url))
        if l.get("website"):
            jobs.append((l, "website", l["website"]))
    if not jobs:
        return leads
    deadline = time.time() + budget

    def run(j):
        if time.time() > deadline:
            return None          # out of budget -> "unverified", never "broken"
        return verify_link(j[2], timeout=4)

    with ThreadPoolExecutor(max_workers=24) as pool:
        results = list(pool.map(run, jobs))
    for (l, kind, _), ok in zip(jobs, results):
        l.setdefault("links_ok", {})[kind] = ok
    for l in leads:
        lk = l.get("links_ok", {})
        if any(v is True for v in lk.values()):
            l["score"] = l.get("score", 0) + 10   # verified-live channel = better lead
    return leads


# ─────────────────────────── website health check ─────────────────────────────

def check_website(url, timeout=8):
    """
    Decide whether an existing site is bad enough to pitch a rebuild.
    Returns (is_bad, reason).
    """
    if not url:
        return True, "No website at all"
    if not url.startswith("http"):
        url = "http://" + url

    problems = []
    if url.startswith("http://"):
        problems.append("no HTTPS (browsers show 'Not secure')")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            html = r.read(200_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return True, f"Website returns HTTP {e.code} (broken link)"
    except Exception:
        return True, "Website did not load (dead, expired, or timing out)"

    low = html.lower()
    if "viewport" not in low:
        problems.append("not mobile-friendly (no viewport tag)")
    if len(html) < 1500:
        problems.append("near-empty page")
    for parked in ("domain is for sale", "buy this domain", "parked domain",
                   "under construction", "coming soon", "godaddy.com/domains"):
        if parked in low:
            problems.append("parked / placeholder page, not a real site")
            break
    years = re.findall(r"(?:©|&copy;|copyright)\s*(\d{4})", low)
    if years:
        try:
            newest = max(int(y) for y in years)
            if newest <= 2019:
                problems.append(f"copyright still says {newest} — looks abandoned")
        except ValueError:
            pass

    if problems:
        return True, "; ".join(problems)
    return False, "Site looks fine — skip this one"


# ─────────────────────────── scoring ──────────────────────────────────────────

def score(lead):
    """Higher = easier to actually reach and close. Drives the default sort order."""
    s = 0
    if lead.get("phone"):
        s += 40          # you can cold call today
    if lead.get("email"):
        s += 30          # you can cold email today
    if lead.get("socials"):
        s += 15          # at least you can DM them
    if lead.get("address"):
        s += 5           # real premises, not a ghost listing
    if lead.get("opening_hours"):
        s += 10          # actively maintained listing = business is alive
    if lead.get("owner"):
        s += 5           # you know who to ask for by name
    if lead.get("whatsapp"):
        s += 20          # reachable on WhatsApp — by far the highest reply rate
    # proof the business is actually trading, capped so it can't dominate
    s += min(lead.get("activity", 0), 5) * 4
    # freshness: data touched in the last ~2 years is far more likely to be a
    # live, still-open business
    vd = lead.get("verified_date", "")
    if vd >= "2024-07":
        s += 10
    elif vd >= "2022-07":
        s += 5
    return s


def reachability(lead):
    if lead.get("whatsapp") and lead.get("email"):
        return "WhatsApp + Email"
    if lead.get("whatsapp"):
        return "WhatsApp"
    if lead.get("phone") and lead.get("email"):
        return "Phone + Email"
    if lead.get("phone"):
        return "Phone only"
    if lead.get("email"):
        return "Email only"
    if lead.get("socials"):
        return "Social only"
    return "Hard to reach"


# ─────────────────────────── main entry point ─────────────────────────────────

def find_leads(niche, place, limit=60, mode="no_website", check_sites=True, strict=True):
    """
    mode:
      'no_website'  -> only businesses with no website tag at all
      'bad_website' -> only businesses whose site is dead/insecure/unresponsive
      'all'         -> everything, annotated
    """
    if niche not in NICHES:
        raise LeadFinderError(f"Unknown niche '{niche}'. Options: {', '.join(sorted(NICHES))}")

    geo = geocode(place)
    query = _build_query(NICHES[niche], geo["bbox"], limit * 4)
    result = _overpass(query)

    # strict mode requires at least two independent signs the business is
    # trading. Thinly-mapped regions (India, much of Africa/SE Asia) would
    # return almost nothing under that rule, so it relaxes there.
    thin = geo["country_code"] in ("in", "pk", "bd", "lk", "np", "ng", "ke",
                                   "id", "ph", "vn", "th", "eg", "za")
    min_activity = (1 if thin else 2) if strict else 0

    leads = parse_elements(
        result.get("elements", []), niche,
        geo["display_name"].split(",")[0], geo["country"],
        country_code=geo["country_code"], min_activity=min_activity,
    )

    # de-duplicate: OSM often has the same shop as both a node and a building way
    seen, unique = set(), []
    for l in leads:
        key = (l["name"].lower(), l.get("address", "").lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(l)

    no_site = [l for l in unique if not l["website"]]
    with_site = [l for l in unique if l["website"]]

    for l in no_site:
        l["qualified"] = True
        l["reason"] = "No website at all — only findable if you already know they exist"

    if mode == "no_website":
        chosen = no_site
    else:
        if check_sites and with_site:
            # Network-bound, so run it wide and under a hard time budget. A few
            # slow-loading sites must not stall the whole search.
            with_site = with_site[:limit * 2]
            deadline = time.time() + 25.0

            def _chk(l):
                if time.time() > deadline:
                    return (False, "Has a website (not health-checked — time budget reached)")
                return check_website(l["website"], timeout=5)

            with ThreadPoolExecutor(max_workers=24) as pool:
                checks = list(pool.map(_chk, with_site))
            for l, (bad, reason) in zip(with_site, checks):
                l["qualified"] = bad
                l["reason"] = reason
        else:
            for l in with_site:
                l["qualified"] = False
                l["reason"] = "Has a website (not health-checked)"

        if mode == "bad_website":
            chosen = [l for l in with_site if l["qualified"]]
        else:
            chosen = no_site + with_site

    for l in chosen:
        l["score"] = score(l)
        l["reachability"] = reachability(l)
        l["place_query"] = place
        l["mode"] = mode

    chosen.sort(key=lambda l: l["score"], reverse=True)
    final = chosen[:limit]

    # verify social links + websites are actually live, then re-rank with the bonus
    verify_lead_links(final)
    final.sort(key=lambda l: l["score"], reverse=True)

    return {
        "place": geo["display_name"],
        "country": geo["country"],
        "niche": niche,
        "scanned": len(unique),
        "found": len(chosen),
        "leads": final,
        "whatsapp_count": sum(1 for l in final if l.get("whatsapp")),
        "foundry_demo": foundry_demo(niche) or "",
        "note": INDIA_NOTE if geo["country_code"] == "in" else "",
    }


if __name__ == "__main__":
    import sys
    n = sys.argv[1] if len(sys.argv) > 1 else "Barber Shop"
    p = sys.argv[2] if len(sys.argv) > 2 else "Leeds, United Kingdom"
    res = find_leads(n, p, limit=25)
    print(f"\n{res['niche']} in {res['place']} — scanned {res['scanned']}, qualified {res['found']}\n")
    for l in res["leads"]:
        print(f"[{l['score']:>3}] {l['name']}")
        print(f"      {l['address'] or 'no address'} | {l['phone'] or 'no phone'} | {l['email'] or 'no email'}")
        print(f"      {l['reason']}")
