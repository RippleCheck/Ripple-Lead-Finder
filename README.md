# Ripple Lead Finder — setup

**[leadfinder.ripplecheck.io](https://leadfinder.ripplecheck.io)** · [Docs](https://leadfinder.ripplecheck.io/docs.html) · [Templates](https://foundry.ripplecheck.io)

A local tool that searches the whole world — India included — for real businesses
with no website, pulls their phone / email / owner name / social handles, and hands
you a ready-to-send message for each one.

Runs entirely on your own machine. No hosting bill, no n8n, no API key required
to get started.

## What's new in v2.1

- **Manual link builder** — a **Manual link** button in the header. Type a
  business name, trade, town and phone for any prospect you found *outside*
  Lead Finder (a walk-in, a referral, someone from Instagram) and get the same
  personalised Foundry website + dashboard links, live as you type. Copy each
  one separately, or both at once.
- **Separate copy buttons** on every lead — one for the website demo link, one
  for the dashboard demo link, so you never paste the wrong one.
- **Port fix** — macOS runs AirPlay Receiver on port 5000, which is why you saw
  "Address already in use" even with every browser closed. The app now finds a
  free port itself and opens the right URL.

## What's new in v2.0

- **258 trades**, from bakeries to cricket academies to solar installers.
- **India supported.** The old block is gone, everywhere — engine, geocoders,
  and the country list.
- **Personalised Foundry links** — every lead gets a website demo *and* an admin
  dashboard demo carrying their own name, town, phone and your agency name in a
  single Base64 `?d=` token, so nothing breaks when it's pasted into WhatsApp.
- **WhatsApp links** — phone numbers are checked against each country's
  numbering plan, and mobiles get a one-click `wa.me` chat link.
- **Google Maps deep links** — verify / pin / Street View for every lead, built
  from its coordinates. No scraping, no Playwright, no 400 MB download.

## Earlier (Ripple)

- **Town dropdown** — pick a country and the town list loads itself (biggest
  towns first, cached after first load). No more needing to know city names.
  There's always a "type a name" option too.
- **Link verification** — Instagram/Facebook/website links are checked live
  during the search: **✓ live** (safe to open and DM), **✗ broken** (dead
  handle), or unmarked (couldn't verify — social sites sometimes block
  checkers; never assumed broken). Verified-live leads score +10 and rank higher.
- **★ Shortlist** — star any lead ("I'm going to message this one"); starred
  leads pin to the top, the outreach panel counts them, and there's a
  "Shortlist only" filter.
- **More filters** — has phone / has email / has Instagram / has Facebook /
  verified-live social / owner known / fresh data only.
- **✨ Business brief button** — one click on any lead generates a full business
  summary that ends with a ready-to-paste prompt for any AI website builder
  (it also reads their current site if they have one). Copy → paste → build
  their site. Works without a key; richer with one.
- Renamed to **Ripple Lead Finder**.

## Earlier improvements

- **Country dropdown** — 111 countries, pick one + type a city.
- **Closed shops filtered out** — anything OpenStreetMap marks as disused,
  abandoned, vacant, ended, or "opening_hours = closed" never reaches your list,
  so you don't pitch a shut door. (Renamed and heritage businesses that are
  still open are correctly kept.)
- **Owner / operator name** — shown on the lead card when the map data has it,
  and the AI rewrite opens the message with their actual name.
- **Freshness signal** — every lead shows when its data was last verified/edited
  in OSM; recently-updated entries rank higher ("Fresh data" chip). This is the
  live-data signal: recently touched = far more likely still open.
- **Second free geocoder (Photon/komoot)** — if Nominatim is busy, the search
  silently falls back, so one rate-limited server never blocks you.
- **108 categories** (later 258).
- **Outreach panel** — floating box in the bottom-right corner: how many leads
  you've reached, replies, deals won, win rate. Updates as you mark stages.
  Click its header to collapse it.
- **AI provider choice** — Settings now takes an OpenAI key *or* an Anthropic
  (Claude) key; pick the provider with one click. Still fully optional.
- **Freeze fix** — the server used to be single-threaded, so a 40-second search
  froze the page (that "stuck / won't reload" problem you saw). It now handles
  requests in parallel: you can browse saved leads while a search runs.
- **Calmer, premium type** — Fraunces for headings, Inter for text, softer
  cream palette that's easier on the eyes.

---

## Start it — no typing required

1. Unzip `leadfinder.zip` somewhere easy to find, e.g. your **Desktop**.
2. Open the `leadfinder` folder.
3. **Mac:** double-click `start.command`.
   First time only, macOS will block it ("unidentified developer") — right-click
   the file → **Open** → click **Open** again. After that it just runs.
   **Windows:** double-click `start.bat`.
4. A window opens, installs Flask automatically if needed, and your browser opens
   to the dashboard on its own.

Leave that window open while you use it — closing it stops the server. Nothing
gets installed system-wide except the one `flask` package.

### If you'd rather use Terminal

The important part: `cd` into the **actual folder**, not just the word `leadfinder` —
if Terminal opens somewhere else (like your home folder), a bare `cd leadfinder`
has nothing to find. Easiest way: type `cd ` (with the trailing space), then
**drag the unzipped `leadfinder` folder from Finder straight into the Terminal
window** — it fills in the correct path for you. Then:

```bash
pip3 install flask || python3 -m pip install flask
python3 app.py
```

(`pip3`/`python3` because on macOS a bare `pip`/`python` sometimes isn't linked.)

Then open **http://127.0.0.1:5000** in your browser.

No account, no key, no signup required to get started. Pick an industry, type a
city, hit **Find Businesses**.

---

## What happens when you click "Find Businesses"

1. Your city gets geocoded to a bounding box (Nominatim, free, no key).
2. Every business of that type inside the box is pulled from OpenStreetMap
   (Overpass API, free, no key).
3. Anything with a `website` tag is filtered out — what's left is your lead list.
4. In "dead / bad website" mode, the ones *with* sites get HTTP-checked in
   parallel and kept only if the site is broken, insecure, parked, non-mobile,
   or clearly abandoned.
5. Each lead is scored on how easily you can actually reach them
   (phone + email = 100, phone only = 55, social only = 15) and sorted best-first.
6. Everything is saved to `leads.db` so it survives a restart.

Re-running the same search never wipes your pipeline — existing leads are skipped,
only genuinely new ones get added.

---

## Instagram, Facebook, WhatsApp

Yes — Instagram is searched, same as Facebook. Whenever OpenStreetMap has a
business's Instagram, Facebook, WhatsApp or Twitter/X handle tagged, it shows up
as a direct link on that lead's card, with its own icon (📸 Instagram,
📘 Facebook, 💬 WhatsApp).

When a handle *isn't* tagged in the map data, the dashboard gives you a one-click
"Find their Instagram" / "Find their Facebook" search link instead of leaving you
stuck — it runs a targeted search for that exact business name + city.

The "Social DM" message tab is written to work for either platform — it doesn't
mention "Facebook" specifically, so the same text works as an Instagram DM too.

---

## Why OpenStreetMap instead of scraping Google

You asked for a bot that opens Google and reads a lakh of results. That approach
breaks quickly and is worth understanding before you spend time on it:

- Google's Terms of Service prohibit automated scraping of search results.
- Practically, Google serves a CAPTCHA after a few dozen automated queries and
  then blocks the IP. A scraper that "works" in testing dies on day one of real use.
- Google search results are unstructured HTML that changes constantly, so the
  parser breaks every few weeks.

OpenStreetMap solves the same problem better:

- Free forever, no key, no billing account, no rate-limit ban.
- Legal to query and reuse (ODbL open licence).
- **Structured** — `website`, `phone`, `email`, `opening_hours`,
  `contact:facebook` are actual fields. "Has no website" becomes a real filter
  instead of a guess.
- Global. Same code works in Leeds, Lisbon, Lagos or Lima.

The one honest tradeoff: OSM coverage is thinner than Google in some regions, and
some businesses in OSM have a website that just isn't tagged. The dashboard gives
you a "Google them" link on every lead so you can sanity-check in one click before
you pitch.

---

## Settings — all in the dashboard now, no terminal needed

Click **⚙ Settings** (top right of the dashboard) to set:

- Your name — goes at the bottom of every message
- Portfolio link — added to cold emails
- Turnaround time you promise
- Your email (optional)
- **OpenAI API key** — paste it here to turn on the **Rewrite with AI** button.
  Templates work fully without it; this just makes every message worded
  differently instead of using the same template each time, which helps
  deliverability and stops you sounding like a bot.

Hit Save. Everything is written to `config.json` next to `app.py` and takes
effect immediately — no restart needed.

If the AI call ever fails for any reason, messages silently fall back to the
template — you'll never get an empty message box.

Prices auto-adjust per country (`PRICE_BY_COUNTRY` in `messages.py` if you want
to hand-edit them) so you're quoting £199 to a UK barber and $250 to a US
bakery — not dollars to everyone.

*(Advanced/optional: you can still set `OPENAI_API_KEY`, `MY_NAME`,
`MY_PORTFOLIO`, `MY_TURNAROUND` as environment variables before starting if you
prefer that to the Settings panel — either way works, Settings just overrides.)*

---

## Also usable from the command line

```bash
python3 engine.py "Bakery" "Porto, Portugal"
python3 engine.py "Dentist" "Warsaw, Poland"
python3 engine.py "Hotel" "Cape Town, South Africa"
```

---

## 258 industries available

Open the **Trade** dropdown in the dashboard to see the full list — it's grouped
into segments (Food & Drink, Health, Home Services, Trades, Auto, Retail,
Professional, Education, Fitness & Sport, Events, Beauty, Hospitality and more),
and the same list feeds the Manual link builder.

To see them from a terminal:

```bash
python3 -c "import categories; print(len(categories.NICHES), 'trades')"
```

Add your own by editing the `NICHES` dict in `categories.py` — any
[OSM tag](https://wiki.openstreetmap.org/wiki/Map_features) works. If the trade
also has a Foundry template, add its slug to `FOUNDRY` in the same file and the
personalised links appear automatically.

---

## Good places to start

Big English-speaking cities have the most OSM coverage and no language barrier:

| City | Try these industries |
|---|---|
| Leeds / Manchester / Glasgow, UK | Barber Shop, Cafe, Car Repair |
| Dublin, Ireland | Cafe, Beauty Salon, Plumber |
| Melbourne / Brisbane, Australia | Cafe, Gym, Pet Grooming |
| Toronto / Calgary, Canada | Restaurant, Car Repair, Dentist |
| Phoenix / Kansas City, USA | Bakery, Landscaper, Home services |

Smaller towns often convert better — less competition, and the owner usually
answers the phone themselves.

---

## Before you send at volume

- **Start slow.** 20–30 emails a day from a fresh domain. Blasting hundreds on
  day one gets the domain flagged as spam, permanently.
- **Use a separate domain** for outreach, never your main email.
- **Every email needs** a real sender name, a real reply-to, and a working
  opt-out. The templates already include a "reply STOP" line — leave it in.
  (US CAN-SPAM requires this; most other markets expect it.)
- **Honour opt-outs immediately.** Mark them Lost and never contact again.
- **Canada is stricter.** CASL generally requires consent *before* a commercial
  email, with a narrower B2B exemption than the US or UK. Start with UK / US /
  Australia and treat Canada separately once you've looked into it.
- **Phone calls** are exempt from most email rules but some countries have
  do-not-call registries for businesses. The call script is designed to fail
  fast and politely — if they say no, mark Lost and move on. Your time is better
  spent on the next lead than on convincing someone who said no.

---

## Files

| File | What it does |
|---|---|
| `app.py` | Local web server + SQLite storage. Run this. |
| `engine.py` | Finds businesses, filters no-website, checks bad sites, scores leads. |
| `messages.py` | Builds the 4 message types; optional AI rewrite. |
| `categories.py` | The 258 trades, their OSM tags, and the Foundry link encoder. |
| `insta.py` | Optional Instagram handle check. |
| `make_link.py` | Command-line personalised link builder (same output as the UI). |
| `dashboard.html` | The UI. Served automatically at `127.0.0.1:5000` (or the next free port). |
| `leads.db` | Created on first run. Your leads and pipeline. Back this up. |

---

## If something breaks

**"All OpenStreetMap mirrors were busy"** — the public mirrors rate-limit at peak
times. Wait a minute and retry; the code already tries three different mirrors.

**"Couldn't find [city]"** — be more specific: `"Leeds, United Kingdom"` rather
than `"Leeds"`.

**0 results** — that industry may be thinly mapped in that city. Try a bigger
city, a more common industry (Cafe, Barber Shop, Restaurant), or switch mode to
"Both".

**Search is slow** — "dead / bad website" mode makes a live HTTP request per
business. 60 leads takes roughly 30 seconds. "No website at all" mode is instant
because it needs no HTTP checks.

## Links

- Website — https://leadfinder.ripplecheck.io
- Documentation — https://leadfinder.ripplecheck.io/docs.html
- Ripple Foundry, the template library the demo links point at — https://foundry.ripplecheck.io
- Issues and questions — https://github.com/RippleCheck/Ripple-Lead-Finder/issues
