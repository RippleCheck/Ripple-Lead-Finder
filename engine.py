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

BLOCKED_COUNTRIES = {"in", "ind", "india"}

# Friendly niche name -> the OSM tags that identify it.
# Each entry is a list of (key, value) pairs; we OR them together.
NICHES = {
    "Bakery":            [("shop", "bakery"), ("shop", "pastry")],
    "Cafe":              [("amenity", "cafe")],
    "Restaurant":        [("amenity", "restaurant")],
    "Fast Food":         [("amenity", "fast_food")],
    "Bar / Pub":         [("amenity", "bar"), ("amenity", "pub")],
    "Barber Shop":       [("shop", "hairdresser")],
    "Beauty / Nail Salon": [("shop", "beauty"), ("shop", "nails")],
    "Tattoo Studio":     [("shop", "tattoo")],
    "Dentist":           [("amenity", "dentist"), ("healthcare", "dentist")],
    "Doctor / Clinic":   [("amenity", "doctors"), ("healthcare", "doctor")],
    "Veterinary":        [("amenity", "veterinary")],
    "Pharmacy":          [("amenity", "pharmacy")],
    "Physiotherapy":     [("healthcare", "physiotherapist")],
    "Gym / Fitness":     [("leisure", "fitness_centre")],
    "Car Repair":        [("shop", "car_repair")],
    "Car Dealer":        [("shop", "car")],
    "Tyre Shop":         [("shop", "tyres")],
    "Grocery / Convenience": [("shop", "convenience"), ("shop", "grocery")],
    "Supermarket":       [("shop", "supermarket")],
    "Butcher":           [("shop", "butcher")],
    "Greengrocer":       [("shop", "greengrocer")],
    "Florist":           [("shop", "florist")],
    "Jeweller":          [("shop", "jewelry")],
    "Optician":          [("shop", "optician")],
    "Bicycle Shop":      [("shop", "bicycle")],
    "Furniture Store":   [("shop", "furniture")],
    "Hardware Store":    [("shop", "hardware"), ("shop", "doityourself")],
    "Pet Shop":          [("shop", "pet")],
    "Pet Grooming":      [("shop", "pet_grooming")],
    "Laundry / Dry Clean": [("shop", "laundry"), ("shop", "dry_cleaning")],
    "Bookshop":          [("shop", "books")],
    "Clothing Store":    [("shop", "clothes")],
    "Shoe Shop":         [("shop", "shoes")],
    "Plumber":           [("craft", "plumber")],
    "Electrician":       [("craft", "electrician")],
    "Carpenter":         [("craft", "carpenter")],
    "Painter / Decorator": [("craft", "painter")],
    "Gardener / Landscaper": [("craft", "gardener")],
    "Photographer":      [("craft", "photographer")],
    "Builder":           [("craft", "builder")],
    "Roofer":            [("craft", "roofer")],
    "Hotel":             [("tourism", "hotel")],
    "Guest House / B&B": [("tourism", "guest_house"), ("tourism", "bed_and_breakfast")],
    "Travel Agency":     [("shop", "travel_agency")],
    "Estate Agent":      [("office", "estate_agent")],
    "Accountant":        [("office", "accountant")],
    "Lawyer":            [("office", "lawyer")],
    "Insurance Office":  [("office", "insurance")],
    "Driving School":    [("amenity", "driving_school")],
    "Childcare / Nursery": [("amenity", "childcare"), ("amenity", "kindergarten")],
    "Funeral Director":  [("shop", "funeral_directors")],
    "Ice Cream Shop":    [("amenity", "ice_cream"), ("shop", "ice_cream")],
    "Deli / Fine Food":  [("shop", "deli")],
    "Confectionery / Sweets": [("shop", "confectionery"), ("shop", "chocolate")],
    "Wine / Liquor Shop": [("shop", "wine"), ("shop", "alcohol")],
    "Tea / Coffee Shop": [("shop", "tea"), ("shop", "coffee")],
    "Massage / Spa":     [("shop", "massage"), ("leisure", "spa")],
    "Chiropractor":      [("healthcare", "chiropractor")],
    "Locksmith":         [("craft", "locksmith"), ("shop", "locksmith")],
    "Shoe Repair / Cobbler": [("craft", "shoemaker"), ("shop", "shoe_repair")],
    "Tailor / Alterations": [("craft", "tailor"), ("shop", "tailor")],
    "Dressmaker":        [("craft", "dressmaker")],
    "Watch / Clock Repair": [("craft", "watchmaker"), ("shop", "watches")],
    "Computer / Phone Repair": [("shop", "computer_repair"), ("shop", "mobile_phone_repair"), ("shop", "computer")],
    "Car Wash":          [("amenity", "car_wash")],
    "Taxi Company":      [("office", "taxi"), ("amenity", "taxi")],
    "Moving Company":    [("office", "moving_company")],
    "Cleaning Service":  [("craft", "cleaning"), ("shop", "cleaning")],
    "HVAC / Heating":    [("craft", "hvac"), ("craft", "heating_engineer")],
    "Glazier / Windows": [("craft", "glaziery"), ("craft", "window_construction")],
    "Metalworker / Welder": [("craft", "metal_construction"), ("craft", "blacksmith")],
    "Upholsterer":       [("craft", "upholsterer")],
    "Stonemason":        [("craft", "stonemason")],
    "Music School":      [("amenity", "music_school")],
    "Tutoring / Education": [("office", "tutoring"), ("amenity", "prep_school")],
    "Language School":   [("amenity", "language_school")],
    "Dance School":      [("leisure", "dance"), ("amenity", "dancing_school")],
    "Gift Shop":         [("shop", "gift")],
    "Toy Shop":          [("shop", "toys")],
    "Stationery Shop":   [("shop", "stationery")],
    "Sports Shop":       [("shop", "sports")],
    "Garden Centre":     [("shop", "garden_centre")],
    "Art Gallery / Studio": [("shop", "art"), ("tourism", "gallery")],
    "Picture Framer":    [("craft", "frame_maker"), ("shop", "frame")],
    "Antique Shop":      [("shop", "antiques")],
    "Second-hand / Charity Shop": [("shop", "second_hand"), ("shop", "charity")],
    "Fishmonger":        [("shop", "seafood")],
    "Health Food Shop":  [("shop", "health_food")],
    "Farm Shop":         [("shop", "farm")],
    "Catering":          [("craft", "caterer")],
    "Nightclub / Venue": [("amenity", "nightclub"), ("amenity", "events_venue")],
    "Camping / Caravan Site": [("tourism", "camp_site"), ("tourism", "caravan_site")],
    "Hostel":            [("tourism", "hostel")],
    "Architect":         [("office", "architect")],
    "Surveyor":          [("office", "surveyor")],
    "IT / Software Office": [("office", "it")],
    "Marketing / Advertising Office": [("office", "advertising_agency")],
    "Employment Agency": [("office", "employment_agency")],
    "Chimney Sweep":     [("craft", "chimney_sweeper")],
    "Scaffolder":        [("craft", "scaffolder")],
    "Tiler":             [("craft", "tiler")],
    "Plasterer":         [("craft", "plasterer")],
    "Flooring / Parquet": [("craft", "floorer"), ("craft", "parquet_layer")],
    "Joiner / Cabinet Maker": [("craft", "joiner"), ("craft", "cabinet_maker")],
    "Sailmaker / Boatbuilder": [("craft", "boatbuilder"), ("craft", "sailmaker")],
    "Laundry Self-Service": [("shop", "laundry_self_service")],
    "Vacation Rental":   [("tourism", "chalet"), ("tourism", "apartment")],
    "Butchery / Charcuterie": [("shop", "charcuterie")],
}

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
    "Fiji": "FJ", "Papua New Guinea": "PG",
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

    if geo["country_code"] in BLOCKED_COUNTRIES or geo["country"].strip().lower() == "india":
        raise LeadFinderError(
            "This tool is scoped to markets outside India. Pick a city in another country."
        )
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


def _looks_closed(tags):
    """
    True if the OSM tags say this business is gone. Filters out permanently
    closed shops so you never pitch a shut door.
    """
    # lifecycle prefixes: disused:shop=bakery, abandoned:amenity=cafe, was:shop=...
    for key in tags:
        if ":" in key and key.split(":", 1)[0] in CLOSED_MARKERS:
            return True
    # explicit closure flags
    for flag in ("disused", "abandoned", "closed"):
        if tags.get(flag) in ("yes", "true", "1"):
            return True
    if tags.get("shop") == "vacant" or tags.get("end_date"):
        return True
    if (tags.get("opening_hours") or "").strip().lower() in ("closed", "off"):
        return True
    return False


def parse_elements(elements, niche, place_label, country):
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
    # freshness: data touched in the last ~2 years is far more likely to be a
    # live, still-open business
    vd = lead.get("verified_date", "")
    if vd >= "2024-07":
        s += 10
    elif vd >= "2022-07":
        s += 5
    return s


def reachability(lead):
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

def find_leads(niche, place, limit=60, mode="no_website", check_sites=True):
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

    leads = parse_elements(
        result.get("elements", []), niche,
        geo["display_name"].split(",")[0], geo["country"],
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
