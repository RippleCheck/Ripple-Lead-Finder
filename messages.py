"""
messages.py — turns a lead into something you can actually send.

Templates work with zero API key. If OPENAI_API_KEY is set, the /api/message
endpoint can rewrite them so every message is different (better for deliverability
and it stops you sounding like a bot).
"""

import json
import os
import ssl
import urllib.request

# ── your pitch settings — edit these once, they flow into every message ────────
ME = {
    "name": os.environ.get("MY_NAME", "Agrajeet"),
    "portfolio": os.environ.get("MY_PORTFOLIO", "[your portfolio link]"),
    "turnaround": os.environ.get("MY_TURNAROUND", "5 days"),
    "email": os.environ.get("MY_EMAIL", ""),
}

# price by currency zone so you're not quoting dollars to a UK barber
PRICE_BY_COUNTRY = {
    "United Kingdom": "£199",
    "Ireland": "€230",
    "Germany": "€230",
    "France": "€230",
    "Spain": "€230",
    "Italy": "€230",
    "Netherlands": "€230",
    "Portugal": "€230",
    "Australia": "A$380",
    "New Zealand": "NZ$400",
    "Canada": "C$340",
    "United States": "$250",
}
DEFAULT_PRICE = "$250"


def price_for(lead):
    return PRICE_BY_COUNTRY.get(lead.get("country", ""), DEFAULT_PRICE)


AI = {"provider": "openai"}  # switched from the Settings panel


def apply_settings(cfg):
    """
    Called at server startup and whenever the Settings panel in the dashboard is
    saved. This is what lets you configure name/portfolio/API keys from the
    browser instead of the terminal.
    """
    if not cfg:
        return
    for k in ("name", "portfolio", "turnaround", "email"):
        if cfg.get(k):
            ME[k] = cfg[k]
    if cfg.get("ai_provider"):
        AI["provider"] = cfg["ai_provider"]
    if cfg.get("openai_api_key"):
        os.environ["OPENAI_API_KEY"] = cfg["openai_api_key"]
    if cfg.get("openai_model"):
        os.environ["OPENAI_MODEL"] = cfg["openai_model"]
    if cfg.get("anthropic_api_key"):
        os.environ["ANTHROPIC_API_KEY"] = cfg["anthropic_api_key"]
    if cfg.get("anthropic_model"):
        os.environ["ANTHROPIC_MODEL"] = cfg["anthropic_model"]
    if cfg.get("prices"):
        PRICE_BY_COUNTRY.update(cfg["prices"])


# what a website actually buys them, per niche — keeps the pitch concrete
HOOKS = {
    "Bakery":        ("orders come through DMs and get messy",
                      "a simple order form, photo gallery and pickup times"),
    "Cafe":          ("people googling cafes in your area find your competitors, not you",
                      "your menu, hours and location showing up in Google search"),
    "Restaurant":    ("people check the menu before deciding where to eat, and yours isn't online",
                      "your menu, booking info and photos on one page"),
    "Barber Shop":   ("walk-ins can't check prices or opening hours before turning up",
                      "a price list, opening hours and an online booking button"),
    "Beauty / Nail Salon": ("nearby salons show up on Google and you don't",
                      "a booking page, price list and photo gallery that ranks on Google"),
    "Dentist":       ("patients research a practice online before they'll book",
                      "a professional page with services, team and an appointment form"),
    "Car Repair":    ("people search for a garage on their phone at the roadside",
                      "a mobile page with services, hours and a click-to-call button"),
    "Gardener / Landscaper": ("you're quoting over messages one at a time",
                      "a quote-request form and a before/after gallery that sells the work for you"),
    "Plumber":       ("emergency customers call whoever they find first on Google",
                      "a fast mobile page with a click-to-call button and your service area"),
    "Electrician":   ("customers want to see you're qualified before they let you in the house",
                      "a page with your certifications, service area and a contact form"),
    "Hotel":         ("guests book through sites that take 15-20% commission from you",
                      "a direct booking page so you keep the commission"),
    "Guest House / B&B": ("guests book through platforms that take a big commission",
                      "a direct booking page so more of the payment stays with you"),
    "Gym / Fitness": ("people compare gyms online before visiting one",
                      "a page with classes, pricing and a free-trial signup form"),
    "Florist":       ("most flower orders start with a Google search",
                      "an online order page with your arrangements and delivery area"),
    "Pet Grooming":  ("customers have to DM you to check availability",
                      "an online booking form, service area and before/after gallery"),
}
GENERIC = ("customers can only find you if they're already following you on social media",
           "a simple site with your services, prices and a contact form")


def hook(niche):
    return HOOKS.get(niche, GENERIC)


def facebook_dm(lead):
    pain, win = hook(lead["niche"])
    return f"""Hi! I came across {lead['name']} while looking at {lead['niche'].lower()} businesses in {lead['city']} — looks like a solid operation.

I noticed you don't have a website, which means {pain}. I build simple, clean sites for small businesses at a flat {price_for(lead)}, usually live in about {ME['turnaround']}. For you that would be {win}.

Before you decide anything I'm happy to build a free mockup with your real name and photos, so you can look at it instead of imagining it. Want me to send one over?

— {ME['name']}"""


def cold_email(lead):
    pain, win = hook(lead["niche"])
    sig = f"\n{ME['portfolio']}" if ME["portfolio"] else ""
    return f"""Subject: Quick website idea for {lead['name']}

Hi,

I'm {ME['name']} — I build simple websites for independent local businesses.

I came across {lead['name']} while looking at {lead['niche'].lower()} businesses in {lead['city']}, and noticed you don't have a website yet. That's workable, but it does mean {pain}.

What I'd build: {win}. Flat {price_for(lead)}, no monthly fee, live in around {ME['turnaround']}.

I'd rather show than tell — I'm happy to put together a free mockup using your real business name and photos, no obligation either way. Reply "yes" and I'll have it with you this week.
{sig}
Best,
{ME['name']}

---
Not interested? Reply STOP and I'll remove you from my list straight away."""


def call_script(lead):
    pain, win = hook(lead["niche"])
    n = lead["niche"].lower()
    return f"""COLD CALL SCRIPT — {lead['name']}
Number: {lead.get('phone') or 'not listed — check their social page'}
{lead.get('address') or ''}

OPENER
"Hi, is that {lead['name']}? My name's {ME['name']}, I build websites for small businesses around {lead['city']}. Have you got thirty seconds? I'll be quick, I promise."

WHY YOU'RE CALLING
"I came across you while looking at {n} businesses in the area. I noticed you don't have a website — which means {pain}."

THE OFFER
"What I do is build a simple site — {win} — for a flat {price_for(lead)}. One payment, no monthly fees, done in about {ME['turnaround']}."

THE ASK  (keep it low-commitment, this is the part that works)
"I'm not asking you to decide anything today. What I'd like to do is build you a free mockup with your actual name and photos, send it over, and you tell me yes or no once you've seen it. Would that be alright?"

── OBJECTIONS ──

"I'm too busy right now"
→ "Completely understand, that's exactly why I do the mockup first — it takes zero time from you. What's the best email to send it to?"

"Facebook works fine for us"
→ "It does, for people already following you. The gap is people googling '{n} {lead['city']}' — right now they find your competitors. That's the bit this fixes."

"How much was it again?"
→ "{price_for(lead)} flat. No subscription to me. If you want changes later we can talk, but there's no monthly bill."

"My nephew/friend was going to do one"
→ "Fair enough, and if they do a good job that's great. The offer stays open — if it stalls, give me a shout. Can I send the free mockup anyway so you've got something to compare against?"

"Send me some information"
→ "Will do — what's the best email? You'll have the mockup in a couple of days, not just a brochure."

"We're not interested"
→ "No problem at all, thanks for being straight with me. Have a good day."   [DO NOT PUSH. Mark as Lost and move on.]

CLOSE
"Brilliant, thanks for your time. I'll have that over to you by [day]. Take care."
"""


def follow_up(lead):
    return f"""Hi again — just bringing this back to the top in case it got buried.

Still happy to put together that free website mockup for {lead['name']}, no strings attached. And if it's not something you want right now, that's completely fine — just say so and I won't chase you again.

— {ME['name']}"""


BUILDERS = {
    "fb": facebook_dm,
    "email": cold_email,
    "call": call_script,
    "follow": follow_up,
}


def build(lead, kind="fb"):
    return BUILDERS.get(kind, facebook_dm)(lead)


# ──────────────── optional AI rewrite (OpenAI or Anthropic) ───────────────────

def _build_prompt(lead, kind):
    label = {
        "fb": "a short Facebook/Instagram DM",
        "email": "a cold email (include a Subject: line)",
        "call": "a cold call script with objection handling",
        "follow": "a short, gentle follow-up message",
    }.get(kind, "a short DM")

    facts = {
        "business_name": lead["name"],
        "industry": lead["niche"],
        "city": lead["city"],
        "country": lead.get("country", ""),
        "owner_or_operator": lead.get("owner", "") or "unknown",
        "why_they_qualify": lead.get("reason", "No website"),
        "has_phone": bool(lead.get("phone")),
        "price_to_quote": price_for(lead),
        "my_name": ME["name"],
        "turnaround": ME["turnaround"],
    }
    return (
        f"Write {label} pitching a small-business website build.\n\n"
        f"Facts you may use (do not invent anything beyond these):\n"
        f"{json.dumps(facts, indent=2)}\n\n"
        "Rules:\n"
        "- Warm, direct, human. No hype words like 'revolutionize', 'unlock', 'game-changer'.\n"
        "- Reference something concrete about this specific business or its trade.\n"
        "- If the owner/operator name is known, address them by it.\n"
        "- Lead with a free mockup offer, not a hard sell.\n"
        "- Do not claim to have visited them, met them, or seen their premises.\n"
        "- Do not invent reviews, customer numbers, or awards.\n"
        "- Under 130 words unless it's a call script.\n"
        "- Output only the message text."
    )


def _call_openai(prompt, key):
    body = json.dumps({
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": 0.8,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45, context=ssl.create_default_context()) as r:
        data = json.loads(r.read().decode())
    return data["choices"][0]["message"]["content"].strip()


def _call_anthropic(prompt, key):
    body = json.dumps({
        "model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
        "max_tokens": 800,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45, context=ssl.create_default_context()) as r:
        data = json.loads(r.read().decode())
    return data["content"][0]["text"].strip()


def _brief_template(lead, site_text=""):
    """No-key fallback: a structured brief built from everything we know."""
    soc = lead.get("socials") or {}
    lines = [
        f"BUSINESS BRIEF — {lead['name']}",
        "=" * 46,
        "",
        "WHO THEY ARE",
        f"- Name: {lead['name']}",
        f"- Trade: {lead['niche']}",
        f"- Location: {lead.get('address') or lead['city']}, {lead.get('country','')}",
        f"- Run by: {lead.get('owner') or 'unknown (ask on first call)'}",
        f"- Opening hours: {lead.get('opening_hours') or 'not listed'}",
        "",
        "HOW TO REACH THEM",
        f"- Phone: {lead.get('phone') or 'not listed'}",
        f"- Email: {lead.get('email') or 'not listed'}",
        f"- Facebook: {soc.get('facebook') or 'not found'}",
        f"- Instagram: {soc.get('instagram') or 'not found'}",
        "",
        "ONLINE PRESENCE GAP",
        f"- {lead.get('reason','No website')}",
        "",
        "WEBSITE TO BUILD THEM (paste this into any AI builder)",
        f"Build a modern single-page website for \"{lead['name']}\", a {lead['niche'].lower()}",
        f"in {lead['city']}, {lead.get('country','')}. Sections: hero with the business name",
        "and a one-line promise; services with prices; photo gallery; about the owner;",
        "opening hours; a contact/booking form; footer with phone, address and social links.",
        f"Contact details to include: phone {lead.get('phone') or '[ask owner]'},",
        f"address {lead.get('address') or lead['city']}.",
        "Style: clean, mobile-first, fast, warm and local — not corporate.",
    ]
    if site_text:
        lines += ["", "NOTES FROM THEIR CURRENT SITE (for rebuild reference)", site_text[:1200]]
    return "\n".join(lines)


def build_brief(lead, site_text="", use_ai=False):
    """
    One-click business summary, shaped so it can be pasted straight into an AI
    website builder. Two modes:
      use_ai=False -> instant local template (no key, no network)
      use_ai=True  -> AI-written, enriched with their live website content
    """
    if not use_ai:
        return _brief_template(lead, site_text), "template"

    provider = AI.get("provider", "openai")
    key = os.environ.get("ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY", "")
    if not key:
        return _brief_template(lead, site_text), "no_key"

    facts = {k: lead.get(k, "") for k in
             ("name", "niche", "city", "country", "address", "phone", "email",
              "owner", "opening_hours", "reason", "website")}
    facts["socials"] = lead.get("socials") or {}
    prompt = (
        "Write a detailed business brief for this local business, ending with a "
        "ready-to-paste prompt for an AI website builder.\n\n"
        f"Known facts (do not invent beyond these; mark unknowns as 'unknown'):\n"
        f"{json.dumps(facts, indent=2)}\n\n"
        + (f"Text scraped from their current website:\n{site_text[:3000]}\n\n" if site_text else "")
        + "Structure:\n"
        "1. WHO THEY ARE — 3-4 sentences on the business, its trade and locality.\n"
        "2. HOW TO REACH THEM — every contact channel known.\n"
        "3. ONLINE PRESENCE GAP — why they need a site, concretely.\n"
        "4. LIKELY SERVICES & CUSTOMERS — inferred from the trade, clearly marked as inference.\n"
        "5. WEBSITE BUILD PROMPT — a complete paste-ready prompt for an AI website builder: "
        "sections, copy suggestions using their real details, tone, colour/style direction "
        "fitting the trade.\n"
        "Plain text only, no markdown symbols."
    )
    try:
        caller = _call_anthropic if provider == "anthropic" else _call_openai
        return caller(prompt, key), f"ai:{provider}"
    except Exception as e:
        return _brief_template(lead, site_text), f"fallback: {e}"


def ai_rewrite(lead, kind="fb", api_key=None, model=None):
    """
    Rewrite a message so no two outreach messages are identical, using whichever
    provider is picked in Settings (OpenAI or Anthropic). Falls back to the
    template if anything goes wrong, so the message box is never empty.
    """
    provider = AI.get("provider", "openai")
    if provider == "anthropic":
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        caller = _call_anthropic
    else:
        key = api_key or os.environ.get("OPENAI_API_KEY", "")
        caller = _call_openai
    if not key:
        return build(lead, kind), "no_key"

    try:
        return caller(_build_prompt(lead, kind), key), f"ai:{provider}"
    except Exception as e:
        return build(lead, kind), f"fallback: {e}"
