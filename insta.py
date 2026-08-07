"""
insta.py — optional Instagram activity check.

WHAT THIS DOES
Given a public Instagram handle, reports when the account last posted, so you
can skip dead accounts instead of spending a DM on them.

READ THIS BEFORE TURNING IT ON
This feature is OFF by default and should stay off unless you understand the
trade-off:

  * Instagram's Terms of Service prohibit automated access. Using this is your
    decision, on your machine, against public data — but it is against their
    terms.
  * Instagram aggressively rate-limits anonymous requests. In practice you get
    a handful of lookups before 401/429 responses start, and repeated attempts
    can get your IP temporarily blocked from instagram.com in a normal browser
    too.
  * Because of that, this is deliberately capped hard (default 12 lookups per
    search, 3s apart) and every failure is treated as "unknown", never as
    "inactive". A blocked check must never mark a good lead as dead.

If `instaloader` is not installed, the feature simply reports "unknown" for
everything and the app carries on. Nothing breaks.

    pip install instaloader     # optional, only if you want this
"""

import re
import time
from datetime import datetime, timedelta, timezone

ACTIVE_DAYS = 30          # posted within this window -> "Active"
QUIET_DAYS = 180          # nothing in this window -> "Dormant"


def _handle(url_or_handle):
    """Pull the bare username out of a profile URL or an @handle."""
    if not url_or_handle:
        return ""
    s = url_or_handle.strip()
    m = re.search(r"instagram\.com/([A-Za-z0-9._]+)", s)
    if m:
        return m.group(1)
    return s.lstrip("@/").split("/")[0]


def available():
    """True if instaloader is installed."""
    try:
        import instaloader  # noqa: F401
        return True
    except ImportError:
        return False


def check_profile(url_or_handle, timeout_posts=3):
    """
    Returns a dict describing the account's activity:

        {status, last_post, days_since, posts, followers, handle, note}

    status is one of:
        active   - posted within ACTIVE_DAYS
        quiet    - posted between ACTIVE_DAYS and QUIET_DAYS ago
        dormant  - nothing in QUIET_DAYS
        empty    - profile exists but has no posts
        private  - exists but not public, so we can't tell
        missing  - handle does not exist
        unknown  - we were blocked, rate-limited or the library is absent

    'unknown' is deliberately distinct from 'dormant'. Being blocked is not
    evidence that a business is inactive, and treating it as such would quietly
    discard good leads.
    """
    out = {"handle": _handle(url_or_handle), "status": "unknown",
           "last_post": "", "days_since": None, "posts": None,
           "followers": None, "note": ""}
    if not out["handle"]:
        return out

    try:
        import instaloader
    except ImportError:
        out["note"] = "instaloader not installed (pip install instaloader)"
        return out

    try:
        L = instaloader.Instaloader(
            quiet=True, download_pictures=False, download_videos=False,
            download_comments=False, save_metadata=False,
            request_timeout=12.0,
        )
        p = instaloader.Profile.from_username(L.context, out["handle"])
        out["followers"] = p.followers
        out["posts"] = p.mediacount

        if p.is_private:
            out["status"] = "private"
            out["note"] = "private account — can't see post dates"
            return out
        if not p.mediacount:
            out["status"] = "empty"
            out["note"] = "profile exists but has never posted"
            return out

        newest = None
        for i, post in enumerate(p.get_posts()):
            if newest is None or post.date_utc > newest:
                newest = post.date_utc
            if i + 1 >= timeout_posts:
                break
        if newest is None:
            return out

        if newest.tzinfo is None:
            newest = newest.replace(tzinfo=timezone.utc)
        days = (datetime.now(timezone.utc) - newest).days
        out["last_post"] = newest.date().isoformat()
        out["days_since"] = days
        if days <= ACTIVE_DAYS:
            out["status"] = "active"
        elif days <= QUIET_DAYS:
            out["status"] = "quiet"
        else:
            out["status"] = "dormant"
        return out

    except Exception as e:
        name = type(e).__name__
        if "ProfileNotExists" in name:
            out["status"] = "missing"
            out["note"] = "handle does not exist"
        elif "Private" in name:
            out["status"] = "private"
        else:
            # rate limit, connection error, login wall — all "unknown"
            out["status"] = "unknown"
            out["note"] = f"could not check ({name}) — treated as unknown, not inactive"
        return out


def check_many(leads, max_checks=12, delay=3.0):
    """
    Check up to `max_checks` leads, pausing `delay` seconds between each.

    The cap and the delay are the whole point: without them Instagram starts
    refusing requests within seconds and you learn nothing about anyone.
    Leads beyond the cap keep status "unknown".
    """
    if not available():
        return {"checked": 0, "available": False}

    done = 0
    for l in leads:
        if done >= max_checks:
            break
        url = (l.get("socials") or {}).get("instagram")
        if not url:
            continue
        info = check_profile(url)
        l["insta"] = info
        done += 1
        if info["status"] == "unknown" and "could not check" in info.get("note", ""):
            break          # we're being blocked — stop rather than dig in deeper
        time.sleep(delay)
    return {"checked": done, "available": True}
