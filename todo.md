# order.life TODO

---

## 📥 Wikibase dump: import items + properties from wiki.order.life

`wiki.order.life` is a **Wikibase** instance (items Q1.., properties P1..),
not a plain MediaWiki wiki. Human-era genealogy (Charlemagne/Pani lines,
Persian-royal-family bridge connecting Jewish/Muslim lines, gateway ancestors
back to prehistoric haplogroup founders) lives on it as Wikibase entities,
none of which have been imported into the repo yet. The existing JSONs in
`Gaiad/genealogy/` are pre-human stubs only and do not overlap with this.

### Why this matters
Needed to support the 130–220 chapter block (beginning of humanity →
beginning of modern age). The genealogical spine is load-bearing for the
pre-BAC mythic-mosaic register and for the post-BAC genealogical-bridge
material. Also enables real network analysis on the built genealogies
(see `planning/gaiad-130-220-structure.md` §13).

### Implementation (READY — merge the open PR after the first run)
- **Script:** `wiki-scripts/wikibase_dump.py` — fetches entities from
  `Special:EntityData/{id}.json` with `wbgetentities` API fallback.
- **Workflow:** `.github/workflows/wikibase-dump.yml` — manual dispatch with
  numeric range inputs; commits to a throwaway branch and opens a PR per run.
- **Output layout:** `wikibase/items/Q{N}.json`, `wikibase/properties/P{N}.json`.
  Kept separate from `Gaiad/genealogy/` because (per Emma) the Wikibase data
  is complex and should be isolated.

### How to run
Trigger the `wikibase-dump` workflow from the Actions tab with the numeric
range of items/properties to pull. Default is Q1..Q100 and P1..P100. A PR
is created automatically on success.

### Open after first run
- Confirm the endpoint / schema matches what the script expects — it's
  untested against the live wiki from Emma's side; script has a fallback
  URL but the real structure of the entities is unknown.
- Schema parity with pre-human `Gaiad/genealogy/*.json` — the Wikibase
  dump is raw; a later pass will translate selected items into the
  existing JSON shape if useful.
- Network analysis on the graph once properties + items are imported.

---

## 🚨 Discord Bot Cron Reliability — FIXED (2026-03-14)

Rewrote the Discord bot to use a state-file approach instead of relying on exact cron timing.

### What changed
- **Runs every 3 hours** (`0 */3 * * *`) instead of at exact times — state file prevents duplicates
- **Two time windows**: daily chapter posts after 6 AM PT, catch-up after 6 PM PT
- **Committed state file** (`discord-bot/state.json`) instead of GitHub Actions cache
- **Always uses Pacific time** via `zoneinfo` — no more UTC offset hacks or DST confusion
- **No more RSS dependency** — daily chapter computed directly from Gaian calendar date
- **deploy.yml ignores** state.json changes to avoid unnecessary rebuilds

### Monitor for
- Verify both daily and catch-up posts are landing reliably over the next few days
- If GitHub Actions skips all 8 daily runs (extremely unlikely), the post will go out next day

---

## ⚠️ iCal Calendars — Phase 1 (bug fix + spec revision needed)

### Bug
`generate_ical_files()` in build.py uses `m["name"]` but MONTHS uses `m["id"]`.
Fix: `{m["num"]: m["id"].capitalize() for m in MONTHS}`.

### Revised current.ics format
`current.ics` should have THREE layers of events per year:

**Layer 1 — Daily Gaian date events (one per day, 364 or 371 per year)**
- `SUMMARY`: `♐ Sagittarius 1, 12026 GE` (symbol + month name + day + year)
- `DESCRIPTION`: output of `gaian_day_description()` (see Phase 3)
  - Placeholder until Phase 3: Gaiad Chapter N · Element · Month theme snippet
- `UID`: `gaian-YYYY-MM-DD-daily@order.life`

**Layer 2 — Holiday events (separate all-day events, same as extended.ics)**
- Makes holidays obvious at a glance in any calendar app
- Same holiday list as before (fixed + Horus + Easter-season individual days)

**Layer 3 — Season span events (multi-day background events)**
- Lent: `DTSTART = Ash Wednesday`, `DTEND = Easter + 1` — `SUMMARY: Season of Lent`
- Eastertide: `DTSTART = Easter`, `DTEND = Pentecost + 1` — `SUMMARY: Eastertide`
- These show as background bands in calendar apps

**`gaian-holidays-extended.ics` stays as Layer 2 only (holidays, no daily events).**

### Output files
| URL | Format |
|-----|--------|
| `/calendar/ical/current.ics` | Layers 1 + 2 + 3, current GE ±2 |
| `/calendar/ical/gaian-holidays-extended.ics` | Layer 2 only, GE 12000–12040 |

Both at `site/calendar/ical/` (root, language-agnostic).

### current.ics year range
- Include GE years: `(current_GE − 2)` through `(current_GE + 2)`
- Rebuilds on every CI/CD push → always current

### All-day event format
```
DTSTART;VALUE=DATE:YYYYMMDD
DTEND;VALUE=DATE:YYYYMMDD   ← exclusive (next day for single-day, span-end+1 for spans)
SUMMARY:...
DESCRIPTION:...
UID:...@order.life
```
No TZID — DATE type events are timezone-free.

### Fixed holidays (both files)
| Gaian date | Event |
|-----------|-------|
| Sagittarius 1 | New Year's Day (Aster Day) |
| Sagittarius 8 | Coming of Age Day |
| Capricorn 7 | Groundhog Day |
| Capricorn 14 | Valentine's Day · Lupercalia |
| Capricorn 21 | Kinen-sai |
| Capricorn 28 | Lantern Festival |
| Aquarius 7 | Hinamatsuri |
| Aquarius 21 | Korei-sai · Ides of March · St Patrick's Day |
| Aries 14 | Cinco de Mayo |
| Gemini 14 | Nagoshi no Oharai |
| Gemini 21 | Tanabata |
| Gemini 28 | Bastille Day |
| Cancer 28 | Qixi |
| Leo 14 | Alolalia |
| Virgo 12 | Mid-Autumn Festival |
| Virgo 14 | Shindensai |
| Libra 1 | Japan Sports Day |
| Ophiuchus 21 | Christmas Day · Dongzhi Festival |
| Horus 1–5, 7 | Egyptian birth days (leap years only) |

### Christian season (moveable, both files as individual events + current.ics also as spans)
Ash Wednesday, Palm Sunday, Good Friday, Holy Saturday, Easter, Ascension, Pentecost.
NOT included: Islamic or Jewish calendar events.

---

## 📋 iCal Calendars — Phase 2 (future)
- Add `/calendar/ical/` index page with subscribe links + instructions for Google/Apple/Outlook

---

## ⏳ Universal Day Description Method — Phase 3 (implement after iCal fix)

### Purpose
Single function that generates a plain-text description for any Gaian calendar day.
Used identically by:
- Day pages: `/calendar/year/{Y}/{MM}/{DD}/` (rendered in the `section-content` div)
- iCal: `DESCRIPTION` field of daily events in `current.ics`
- Future: any other surface that needs day-level narrative

### Signature
```python
def gaian_day_description(gaian_year, month_num, day_num, chapters=None) -> str
```

### GaianCalendar Python library (future integration)
A dedicated `GaianCalendar` Python library is in development but not yet complete.
Once available, replace the inline weekday computation `(day_num - 1) % 7` and
`_gaian_day_to_greg()` helper with library calls. Marked with `# TODO: GaianCalendar`
in build.py.

### Output format (2–4 sentences)
1. Gregorian date in that year + Gaian date
2. Gaiad chapter N of 364 (or intercalary note for Horus) + month theme excerpt
3. Any holidays on this day (fixed or computed moveable)
4. Optional: cross-calendar coincidence note if notable (e.g. "Lent and Ramadan overlap
   in Aquarius–Pisces this year")

### Inputs consumed
- `gaian_year`, `month_num`, `day_num` → Gregorian date via `_gaian_day_to_greg()`
- `MONTH_THEMES[month_id]` → (theme_title, theme_desc)
- `_ICAL_FIXED` + Horus list + `_ICAL_CHRISTIAN_OFFSETS` → holidays on this day
- Build-time precomputed data: Easter, Ramadan start for cross-calendar notes

### Data extension points (future)
- `content/day-events.json` keyed by `MM/DD` for recurring culturally-noted events
- Per-year scheduled Lifeism events JSON
- Historical events database (optional, curated)

---

## 🛠 GitHub Actions — Node.js 20 deprecation

GitHub is deprecating Node.js 20 actions. Every workflow in `.github/workflows/` that uses `actions/checkout@v4` or `actions/setup-python@v5` currently runs on Node 20, which affects: `calendar-bot.yml`, `dotnet-build.yml`, `wiki-bot.yml`, `discord-bot.yml`, `deploy.yml`.

**Timeline:**
- **June 2, 2026** — runners will force Node.js 24 by default
- **September 16, 2026** — Node.js 20 removed from runners entirely

**Fix:** bump to newer action tags once they officially support Node 24, or set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` as an interim opt-in. Not urgent — still has months.

Reference: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/

---

## 🗓 calendar-lib follow-ups

See `calendar-lib/README.md` for the full roadmap. Most pressing after the first successful bot run:

- [ ] Import `Module:GaiadDate` onto lifeism.miraheze.org (manual — the XML is in `calendar-lib/GaianCalendar-WikiModule-Export.xml`, paste into `Module:GaiadDate` via Special:Import or copy-paste the Lua source)
- [ ] First `dotnet-build.yml` run — may reveal the `.csproj` targets a framework other than .NET 8; bump if so
- [ ] Verify the 14 month pages the bot just overwrote on Lifeism didn't clobber valuable content (first run logged all 14 as `Updated page`, not `No change` — worth a visual check that the new markup isn't missing anything)
