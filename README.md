<div align="center">

# Ripple Lead Finder

### Find freelance clients before anyone else does.

Discover local businesses **anywhere in the world that have no website**, pull their
contact details, and get a ready-to-send pitch — all from a tool that runs entirely
on your own machine.

<br>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Framework: Flask](https://img.shields.io/badge/framework-Flask-000000.svg)](https://flask.palletsprojects.com/)
[![Data: OpenStreetMap](https://img.shields.io/badge/data-OpenStreetMap-7ebc6f.svg)](https://www.openstreetmap.org/)
[![Runs 100% local](https://img.shields.io/badge/runs-100%25%20local-success.svg)](#privacy)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](#install)

</div>

<!--
  SCREENSHOT PLACEHOLDER — how to replace this with a real image:
  1. Start the app and open http://127.0.0.1:5000
  2. Run a search so the dashboard has leads on screen, then take a screenshot
  3. Save it in the repo as  docs/screenshot.png  (create the docs/ folder)
  4. Delete the blockquote line below and uncomment the image line:
     ![Ripple Lead Finder dashboard](docs/screenshot.png)
-->

> **📸 Screenshot goes here.** _(See the HTML comment above for how to drop in a real image.)_

---

## Contents

- [What it is](#what-it-is)
- [Who it's for](#who-its-for)
- [Why OpenStreetMap, not Google scraping](#why-openstreetmap-not-google-scraping)
- [Features](#features)
- [Data sources](#data-sources)
- [Install](#install)
- [Quick start](#quick-start)
- [Command-line usage](#command-line-usage)
- [Project structure](#project-structure)
- [Privacy](#privacy)
- [Responsible outreach](#responsible-outreach)
- [Troubleshooting](#troubleshooting)
- [Honest limitations](#honest-limitations)
- [Roadmap](#roadmap)
- [License](#license)

---

## What it is

Ripple Lead Finder is a **local web app** (Python + Flask, SQLite) for finding
businesses that need a website. It runs entirely on your own machine — no cloud,
no hosting bill, no account, and **no API key required to start**. Launch it and it
opens in your browser at `http://127.0.0.1:5000`.

Point it at a country and an industry, and it returns real local businesses that
have no website, complete with phone, email, owner name and social handles — plus
four ready-to-send outreach messages for each one.

## Who it's for

Freelancers and small agencies who **sell websites**. The slow part of that work
isn't building sites — it's *finding* the businesses that need one, qualifying them,
and writing a first message that doesn't sound like a bot. Ripple Lead Finder
automates all three.

---

## Why OpenStreetMap, not Google scraping

The obvious idea is "scrape Google for businesses." It doesn't hold up, and it's
worth understanding why before you sink time into it:

- **It's against the rules.** Google's Terms of Service prohibit automated scraping
  of search results.
- **It dies in real use.** In practice Google serves a CAPTCHA after a few dozen
  automated queries and then blocks the IP. A scraper that looks fine in testing
  stops working on day one of actual use.

OpenStreetMap (OSM) solves the same problem properly:

- **Free and legal to reuse** under the Open Database License (ODbL).
- **Global coverage** — the same code works in Leeds, Lisbon, Lagos or Lima.
- **Structured, not scraped.** `website`, `phone`, `email`, `contact:instagram`
  and `opening_hours` are *real fields* in the data. That means **"has no website"
  is an exact filter, not a guess.**

---

## Features

- **108 business categories** — bakeries, barbers, dentists, plumbers, hotels, gyms,
  car repair, landscapers, salons, accountants, and many more.
- **111 countries supported.** India is intentionally excluded (the tool targets
  foreign markets) and this is enforced server-side, regardless of which geocoder
  answers.
- **Instant town lists.** A bundled seed file ships town/city lists for major markets
  that load with **zero network calls**:

  | Country | Towns | Country | Towns |
  |---|---:|---|---:|
  | United States | 331 | Ireland | 63 |
  | United Kingdom | 169 | New Zealand | 61 |
  | Germany | 80 | Netherlands | 60 |
  | France | 80 | Spain | 74 |
  | Italy | 80 | United Arab Emirates | 20 |
  | Canada | 73 | Australia | 63 |

  Any other country is fetched live once, then cached to disk for next time.
- **Three search modes** — businesses with *no website at all* / businesses whose
  existing site is *dead, insecure, parked or non-mobile* / *both*.
- **Permanently-closed shops filtered out.** Anything OSM marks `disused`,
  `abandoned`, `vacant`, with an `end_date`, or `opening_hours=closed` is skipped —
  so you never pitch a shut door. Renamed and heritage businesses that are still
  trading are correctly kept.
- **Owner / operator name** is extracted where the map data has it, so you can open
  a call with a real name.
- **Data-freshness signal.** Each lead shows when its record was last verified or
  edited; recent records rank higher, because recently-touched data is far more
  likely to still be open.
- **Live link verification.** Instagram, Facebook and website links are checked
  during the search and marked ✓ live or ✗ broken. Social platforms sometimes block
  automated checks — those cases are shown as *unverified* rather than falsely
  reported broken.
- **Lead scoring** ranks by how easily you can actually reach a business: phone +
  email scores highest, social-only lowest, with bonuses for a known owner, fresh
  data and verified-live links.
- **Four ready-to-send messages per lead** — a social DM, a cold email, a full
  cold-call script with objection handling, and a follow-up. Price auto-adjusts by
  country (£ for the UK, € for the eurozone, A$ for Australia, C$ for Canada,
  $ elsewhere).
- **Optional AI rewrite.** Bring your own **OpenAI *or* Anthropic** key, pasted into
  the in-app Settings panel — no terminal, no environment variables. Every message
  comes out uniquely worded. If the API call fails, it silently falls back to the
  template, so the message box is never empty.
- **Business Brief, two modes.** *Quick brief* is instant, local, and needs no key.
  *AI brief* uses your key and additionally reads the business's current website for
  richer detail. Both end with a paste-ready prompt for any AI website builder — so
  you can go from lead to built site in one flow.
- **Shortlist + pipeline.** Star leads you intend to message and move them through
  **New → Contacted → Replied → Won / Lost**, with private notes. A floating panel
  tracks shortlisted, reached, replies, deals won and win rate.
- **Filters** — industry, country, stage, has phone, has email, has Instagram, has
  Facebook, verified-live social, owner known, fresh-data-only, shortlist-only.
- **CSV export** of every field, including link-verification status.
- **Everything persists** in a local `leads.db` (SQLite). Re-running the same search
  never wipes your pipeline: existing leads are skipped and only genuinely new ones
  are added.

**Design & UX:** a native system font stack, clean line icons, and a warm,
low-glare palette chosen to be easy on the eyes during long sessions. The server is
multi-threaded, so the interface stays fully responsive while a search runs.

---

## Data sources

All free, all keyless:

| Source | Used for |
|---|---|
| **OpenStreetMap** (Overpass API) | Business data — tried across 3 public mirrors with automatic failover |
| **Nominatim** | Geocoding place names to a search area |
| **Photon** (komoot) | Backup geocoder, used automatically if Nominatim is rate-limited |
| **Bundled town seed file** | Instant, offline town lists for major markets |
| **Built-in live link checker** | Verifying website / social links during a search |

---

## Install

**Requirement:** Python 3.8 or newer. The only dependency is **Flask**, and it
installs itself on first run.

> **Keep the launcher window open while you use the app — closing it stops the
> server.**

### macOS

1. Download the latest release ZIP (or `git clone` this repo).
2. Unzip it somewhere easy to find, e.g. your **Desktop**.
3. Double-click **`start.command`**.
4. **First run only:** macOS blocks apps from unidentified developers. Right-click
   `start.command` → **Open** → **Open** again. You only need to do this once.
5. Flask installs automatically if it's missing, and your browser opens by itself.

### Windows

1. Download the latest release ZIP (or `git clone` this repo).
2. Unzip it somewhere easy to find, e.g. your **Desktop**.
3. Double-click **`start.bat`**.
4. If Python isn't installed, get it from [python.org](https://www.python.org/downloads/)
   and **tick "Add python.exe to PATH"** on the installer's first screen — this is
   the single most common setup mistake.
5. Flask installs automatically if it's missing, and your browser opens by itself.

### Any platform, via terminal

```bash
git clone https://github.com/RippleCheck/Ripple-Lead-Finder.git
cd Ripple-Lead-Finder
pip3 install flask
python3 app.py
```

Then open **http://127.0.0.1:5000**.

---

## Quick start

1. **Pick an industry** (e.g. Barber Shop).
2. **Pick a country** (e.g. United Kingdom).
3. **Pick a town** from the dropdown.
4. Click **Find Businesses**.
5. **Star** the good ones to add them to your shortlist.
6. **Open a lead**, copy the message that fits, and **send it yourself, manually.**

> **Tip:** smaller towns often convert better — there's less competition, and the
> owner usually answers the phone themselves.

---

## Command-line usage

`engine.py` runs standalone if you just want raw results in the terminal:

```bash
python3 engine.py "Bakery" "Porto, Portugal"
python3 engine.py "Dentist" "Warsaw, Poland"
```

---

## Project structure

| File | What it does |
|---|---|
| `app.py` | The local web server + SQLite storage. This is the file you run. |
| `engine.py` | Search, filtering, scoring, and link verification against OpenStreetMap. |
| `messages.py` | Message and business-brief generation, including the optional AI rewrite. |
| `dashboard.html` | The user interface, served automatically at `127.0.0.1:5000`. |
| `cities_seed.json` | Bundled offline town lists for the seeded countries. |
| `start.command` / `start.sh` / `start.bat` | One-double-click launchers for macOS, Linux and Windows. |

---

## Privacy

Everything runs **locally**. The only outbound network calls are to OpenStreetMap
for business data and — *only if you add a key* — to your chosen AI provider. There
is no telemetry, there are no accounts, and no data leaves your machine otherwise.

Your `config.json` (which can hold an API key) and your `leads.db` are **gitignored**
and never committed.

---

## Responsible outreach

Cold outreach done carelessly burns your domain and annoys people. Do it properly:

- **Start slow.** 20–30 emails a day from a fresh domain. Blasting hundreds on day
  one gets a domain permanently flagged as spam.
- **Use a separate sending domain**, never your main email.
- **Every cold email needs** a real sender name, a working reply-to, and a working
  opt-out. The built-in templates already include a "reply STOP" line — **leave it
  in.** US CAN-SPAM requires it and most markets expect it.
- **Honour opt-outs immediately and permanently.**
- **Canada is stricter.** CASL is tougher than US/UK/Australia rules and generally
  requires consent *before* a commercial email, with a narrower B2B exemption. Treat
  Canada separately.

---

## Troubleshooting

<details>
<summary><strong>"All OpenStreetMap mirrors were busy"</strong></summary>

<br>

Public OSM mirrors rate-limit at peak times. Wait a minute and retry — the app
already tries three different mirrors with automatic failover before giving up.

</details>

<details>
<summary><strong>Port 5000 already in use (macOS)</strong></summary>

<br>

On macOS, **AirPlay Receiver** uses port 5000. Turn it off in
**System Settings → General → AirDrop & Handoff**, or change the port at the bottom
of `app.py`.

</details>

<details>
<summary><strong>Zero results</strong></summary>

<br>

That industry may simply be thinly mapped in that town. Try a bigger town, a more
common industry (Cafe, Barber Shop, Restaurant), or switch the mode to **Both**.

</details>

<details>
<summary><strong>Search feels slow</strong></summary>

<br>

The "dead / bad website" mode makes a live HTTP request per business, so ~60 leads
takes roughly 30 seconds. The "no website at all" mode is much faster because it
doesn't need those checks.

</details>

<details>
<summary><strong>Town list missing for my country</strong></summary>

<br>

Seeded countries load instantly. Any other country is fetched live on first use and
then cached to disk, so it's instant every time after that.

</details>

---

## Honest limitations

OSM coverage is thinner than Google's in some regions, and a few businesses have a
website that simply isn't tagged in the map data. Because of that, **every lead has
a one-click "Google them" link** so you can sanity-check before pitching. We'd rather
say this plainly than oversell the coverage.

---

## Roadmap

Planned, but **not built yet**:

- Optional Google Places support for users who bring a paid key.
- Bulk CSV import.
- Email-sending integration.

---

## Data & attribution

The business and place data in this app comes from **OpenStreetMap**. That data is
**© OpenStreetMap contributors** and is published under the
**[Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/)**.

Attribution is a genuine requirement of that licence, not an optional courtesy. If
you publish, redistribute or build on the data this tool returns, you must credit
**© OpenStreetMap contributors** and preserve the ODbL terms — see
[openstreetmap.org/copyright](https://www.openstreetmap.org/copyright).

The MIT licence below covers **this project's own code only**; it does not relicense
the underlying map data.

## License

The code is released under the [MIT License](LICENSE). © 2026 Agrajeet Verma.

Map data © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).

<div align="center">
<br>
<sub>Built by Agrajeet Verma</sub>
</div>
