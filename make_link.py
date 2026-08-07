#!/usr/bin/env python3
"""
make_link.py — build a personalised Ripple Foundry link for one business.

    python3 make_link.py "Cric8InNet" cricket-academy \
            --city Delhi --phone "+91-9999-30-5050" --kind both

By default this prints the long, self-contained link:

    https://foundry.ripplecheck.io/demo/cricket-academy/?d=Q3JpYzhJbk5ldHwr...

Add --short to shorten it through d.php on Foundry (needs SHORTENER_SECRET):

    https://foundry.ripplecheck.io/d/x7f2k

The short form hides the payload and records opens. The long form needs no
server-side anything and can never break. Both resolve to the same page.
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from categories import (CATALOGUE, FOUNDRY, FOUNDRY_BASE,  # noqa: E402
                        encode_payload, decode_payload)

SHORTENER_URL = os.environ.get("SHORTENER_URL", f"{FOUNDRY_BASE}/d.php")
SHORTENER_SECRET = os.environ.get("SHORTENER_SECRET", "")


def resolve_slug(value):
    """Accept either a Foundry slug ('cricket-academy') or a trade name."""
    v = (value or "").strip()
    if v in FOUNDRY.values():
        return v
    if v in FOUNDRY:
        return FOUNDRY[v]
    low = v.lower().replace("_", "-").replace(" ", "-")
    if low in FOUNDRY.values():
        return low
    # last try: fuzzy match on the display name
    for name, slug in FOUNDRY.items():
        if name.lower() == v.lower():
            return slug
    return None


def long_links(business, slug, city="", phone="", agency="", kind="both"):
    token = encode_payload(business=business, phone=phone, city=city,
                           trade=slug, agency=agency)
    out = {"token": token, "slug": slug}
    if kind in ("demo", "both"):
        out["demo"] = f"{FOUNDRY_BASE}/demo/{slug}/?d={token}"
    if kind in ("app", "both"):
        out["app"] = f"{FOUNDRY_BASE}/app/{slug}/?d={token}"
    return out


def shorten(target, label=""):
    """
    Ask d.php on Foundry for a short code. Returns the short URL, or None with
    a reason printed — never raises, so a shortener outage just means you get
    the long link instead of nothing.
    """
    if not SHORTENER_SECRET:
        return None, ("no SHORTENER_SECRET set — export it to match the SECRET "
                      "constant inside d.php")
    body = urllib.parse.urlencode({
        "secret": SHORTENER_SECRET, "url": target, "label": label,
    }).encode()
    req = urllib.request.Request(SHORTENER_URL, data=body,
                                 headers={"User-Agent": "RippleLeadFinder/1.9"})
    try:
        with urllib.request.urlopen(req, timeout=15,
                                    context=ssl.create_default_context()) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return None, f"shortener returned HTTP {e.code}"
    except Exception as e:
        return None, f"could not reach the shortener ({e})"
    if not data.get("ok"):
        return None, data.get("error", "shortener refused the request")
    return data.get("short"), None


def main():
    p = argparse.ArgumentParser(
        description="Build a personalised Ripple Foundry link.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    p.add_argument("business", help='Business name, e.g. "Cric8InNet"')
    p.add_argument("trade", help="Foundry slug or trade name, e.g. cricket-academy")
    p.add_argument("--city", default="")
    p.add_argument("--phone", default="")
    p.add_argument("--agency", default=os.environ.get("AGENCY_NAME", ""),
                   help="Your agency name, shown on the demo")
    p.add_argument("--kind", choices=["demo", "app", "both"], default="both")
    p.add_argument("--short", action="store_true",
                   help="Shorten via d.php (needs SHORTENER_SECRET)")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    p.add_argument("--enc", action="store_true",
                   help=argparse.SUPPRESS)  # accepted for compatibility; always on
    args = p.parse_args()

    slug = resolve_slug(args.trade)
    if not slug:
        print(f"Unknown trade '{args.trade}'.", file=sys.stderr)
        near = [s for s in sorted(set(FOUNDRY.values()))
                if args.trade.lower()[:4] in s][:8]
        if near:
            print("Did you mean: " + ", ".join(near), file=sys.stderr)
        print(f"({len(set(FOUNDRY.values()))} slugs available — see categories.py)",
              file=sys.stderr)
        return 2

    links = long_links(args.business, slug, args.city, args.phone,
                       args.agency, args.kind)

    warnings = []
    if args.short:
        for key in ("demo", "app"):
            if key not in links:
                continue
            short, err = shorten(links[key], label=f"{args.business} ({key})")
            if short:
                links[key + "_long"] = links[key]
                links[key] = short
            elif err and err not in warnings:
                warnings.append(err)

    if args.json:
        print(json.dumps(links, indent=2, ensure_ascii=False))
        return 0

    print()
    print(f"  {args.business}  ·  {slug}" + (f"  ·  {args.city}" if args.city else ""))
    print("  " + "-" * 62)
    if "demo" in links:
        print(f"  WEBSITE    {links['demo']}")
    if "app" in links:
        print(f"  DASHBOARD  {links['app']}")
    print()
    print(f"  payload    {decode_payload(links['token'])}")
    for w in warnings:
        print(f"\n  note: {w}\n         falling back to the long link, which always works.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
