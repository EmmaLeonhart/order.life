# order.life TODO

---

## 👥 Teresa Eriz de Lugo is in the dump three times — dedupe (2026-08-07)

`Q79618` "Tereza Eriz de Lugo", `Q100413` "Teresa Eriz" and `Q110516` "Teresa Eris de
Lugo" (wd `Q110302349`) are one woman, daughter of Ero Fernández, count of Lugo (d. c.
926). `Q79618` and `Q100413` both now hang off `Q100140`; `Q110516` hangs off the other
Ero record, `Q111013` (wd `Q1028988`).

So **Ero Fernández is himself duplicated** as `Q100140` and `Q111013`, which is the
larger half of this. `Q100140` carries the Geni id for the count; `Q111013` carries the
Wikidata id. Merging them is a dedupe, not a cycle repair — it removes no loop, and it
touches a well-populated 10th-century Galician cluster, so do it deliberately rather than
as a side effect of something else.

---

## 🏺 Where do the Servilii attach? — NEEDS EMMA (2026-08-07)

After `apply_servilii_chain.py` opened tangle 5, `Q73170` "Gaius Servilius" is the root of
an eight-record placeholder chain bridging the Republican Servilii (down to P. Servilius
Vatia Isauricus, 120–44 BC) to the Imperial ones (down through Claudia Acilia, AD 185, to
the Anicii and Anicius Auchenius Bassus, 350–408). **The whole component reaches nothing
above it — it does not reach Aster.**

None of the eight carries a Wikidata id, a date or a cognomen, so there is no research
answer to find: they are invented connective tissue. Where the Servilian gens should hang
in the story is a narrative decision.

Options, none of them researchable:
  - attach `Q73170` to an existing Roman line that already reaches Aster;
  - leave the component rootless — honest, but the Anicii and everyone below them then
    reach Aster only through their mothers, if at all;
  - collapse the eight placeholders and join the Republican and Imperial Servilii
    directly, which is repair-order step 4 and loses the generational spacing.

---

## 🧹 Genealogy data hygiene — found 2026-08-07

**1. 8 dangling edge endpoints.** These qids are referenced by `edges.tsv` or
`spouses.tsv` and have **no item file anywhere in the dump**: `Q54196`, `Q74656`,
`Q75282`, `Q78402` and four more surfaced by `repair_persons_tsv.py`. Either the edge is
stale and should go, or the record was lost. Check before deleting either way.

**2. persons.tsv may still be short of the true total.** Records with no parent, no child
and no spouse appear in none of the three extracts, so `repair_persons_tsv.py` cannot see
them. `items_index.txt` (164,544) minus `redirects.tsv` (57,440) suggests ~107,100 real
qids against the repaired 106,029 — so perhaps a thousand isolated records are still
missing. Closing that needs the real regeneration with the temp-file-and-rename guard that
item 0a specifies, which is the CPU-heavy job.

**3. `Q102772` Oliba Cabreta has duplicate fathers AND duplicate mothers** — `Q102765`
"Miro II el Jove, comte de Cerdanya" and `Q111442` "Miró II of Cerdanya" are the same man;
`Q101589` and `Q110870` are both Ava of Cerdanya. A dedupe. Surfaced accidentally by the
divine-father name sweep, which matched Catalan *Jove* as Jupiter.

---

## 🏛 The Lepidus unmerge — what is left after 2026-08-07

`Q72786` is **Mamercus Aemilius Lepidus Livianus, consul 77 BC** (wd `Q721477`) — not a
Marcus. Born a Livius Drusus, adopted into the Aemilii Lepidi, which the cognomen
*Livianus* records. Three things are done: the false Quintus edge is cut
(`apply_lepidus_cut.py`), the biological father is wired in
(`apply_mamercus_biological_father.py` — it is `Q72798`, which carries `P61` = `Q703346`
on the record), and the adoption is written into the record's description.

**1. NEEDS EMMA — is there a kinship-type property, or is a description enough?**
This wikibase has no adoption property. `P47` is just "Father", so `Q72786`'s two correct
fathers are indistinguishable from a two-father defect to anything that scans structurally.
Right now the distinction lives only in the record's English description. The options:

  - leave it in the description (zero schema change, invisible to scripts);
  - add a property, e.g. `P70` "kinship type", used as a **qualifier** on `P47`/`P48`
    with values `biological` / `adoptive` / `divine` — which would also give the
    divine-father class from CLAUDE.md a real home, instead of "ignore them literally"
    being a rule that only lives in prose;
  - keep an explicit allow-list of known-good multi-father records in `wikibase/analysis/`.

The middle option is the one that would actually make `qa_same_role_parents.tsv` mean
something. **It is a schema decision, so it is Emma's.**

**2. RESEARCH — identify couples B and C on `Q72786`.** The record still carries three
father+mother couples. Couple A is settled (adoptive `Q73011` + mother `Q72801` Cornelia,
plus the biological `Q72798` now added). Couples B (`Q73113` / `Q73110`) and C (`Q73173`)
belong to *other men* filed under the same colliding label and need identifying against
the Aemilii Lepidi prosopography — none of the three carries a Wikidata id, which is why
this is a lookup job and not a dump job. Once identified, split them out; **naming the
split records is Emma's**, per the `Tros` precedent.

**3. Consequence of the sign bug, still unaudited.** Only 133 records in the whole dump
carry a negative (BC) date; almost everything pre-Christian is stored positive, and the
dump is therefore *inconsistent* rather than uniformly wrong. Every past repair justified
as "chronologically impossible" — above all the inversion class cut on 2026-08-02, five
tangles and 21 records — needs checking for whether its argument actually compared these
fields numerically. Where it used patronymics, dynasty membership or explicit BC/AD in the
label, it stands. **Do not revert anything on this basis; go and check which arguments
used the fields.** See `wikibase/analysis/lepidus_resolved.md`.

---

## 🗃 Wikibase dump + genealogy — ARCHIVED (2026-07-01)

The source wiki was taken down by Miraheze as off-topic. The dump/backfill is
**complete and frozen**: 164,536 item JSONs + 94 properties committed under
`wikibase/` (the only copy now). The `fill_missing`/`dump` scripts fetch over HTTP
from the wiki, so they can no longer run — but they are no longer needed.

Genealogy analysis + QA runs entirely on the LOCAL dump. Outputs:
- `wikibase/analysis/GENEALOGY_QA.md` — summary (graph shape, centrality, errors).
- `wikibase/analysis/genealogy_qa_report.txt` — full run of
  `wiki-scripts/genealogy_network_analysis.py`.
- `wikibase/analysis/qa_multiparent.tsv` (1,230 children with >2 parents) +
  `qa_cycles.tsv` (~70 impossible cycles) — full error lists from
  `wiki-scripts/dump_qa_errors.py`.

Still open (needs Emma — creative/judgement, not fetch): lineage bridges
Kosala→Heo Hwang-ok, Genghis→Adam, Heo Hwang-ok→Jimmu; and fixing the
enumerated QA errors (which true parents / which cycle-edge to cut). All local now.

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

## ✅ iCal Calendars — Phase 1 (DONE — verified 2026-06-29)

Shipped in `build.py:generate_ical_files()` (~line 1343): Layer 1 daily events
(`_ical_year_daily`), Layer 2 holidays (`_ical_year_holidays`), Layer 3 Lent/
Eastertide season spans (`_ical_year_seasons`), plus a Japanese `current_ja.ics`.
The `m["name"]`→`m["id"]` bug is already fixed (`build.py:1352`). Spec below is
kept for reference only — do NOT re-implement.

### Bug (FIXED)
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

## ✅ Universal Day Description Method — Phase 3 (DONE — `gaian_day_description()` at `build.py:1053`, used by iCal daily events at `build.py:1275`)

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

See `calendar-lib/README.md` for the full roadmap.

- [x] First `dotnet-build.yml` run — **DONE/green.** The workflow has run successfully multiple times (incl. on the 2026-06-29 `setup-dotnet@v5` bump, commit c037669d1); it restores + builds `GaianNodaTimeWrappers.sln` against .NET 8.0.x with no framework mismatch. No decision needed.

**MOOT — the lifeism.miraheze.org wiki is closed (2026-04-16); calendar-bot is disabled (see `calendar-bot.yml` and `STATUS.md`). The two items below are unreachable until/unless a wiki comes back:**
- ~~Import `Module:GaiadDate` onto lifeism.miraheze.org~~ — wiki closed. XML still in `calendar-lib/GaianCalendar-WikiModule-Export.xml` if a wiki is restored.
- ~~Verify the 14 month pages the bot overwrote didn't clobber content~~ — wiki closed; the host returns "Wiki not found", and the bot never ran successfully against a live wiki. Audited 2026-06-29: nothing to verify.
- `calendar-lib/test_overview_preservation.py` was **NOT actually a failing test** (corrected 2026-07-01). It's a manual CLI diagnostic that pytest merely *collected* because of its `test_*.py` name + `test_*` functions; the "2 errors" were `fixture 'username'/'wiki' not found` — a collection artifact, not a wiki problem. **Renamed to `diagnose_overview_preservation.py`** (and its internal functions de-`test_`-prefixed), so pytest no longer collects it → calendar-lib suite is now a clean **2 passed / 0 errors** (`test_page_generation.py`). The diagnostic still can't *connect* (its target wikis, evolutionism/lifeism.miraheze.org, are 404-closed), but that's a can't-run tool, not a red test.

## Notion — central command owns it (2026-07-31)

**Emma's call: central command runs the syncing.** This repo's work loop does not create,
edit or push Notion pages, and does not treat any Notion page as a source of truth.

- **What this repo offers central command:** `wikibase/analysis/cycles_review.md` — all 35
  tangles, one section each, every member with ancestor count, descendant count, depth, and
  whether it reaches `Q1` Aster. Generated by `wiki-scripts/build_cycles_notion.py`, plain
  Markdown, no Notion coupling. Emma wants **bidirectional** editing; this file is a
  generated artefact, so writes coming back from Notion need somewhere real to land —
  probably the `Decision:` line per tangle, which is the only field meant for a human.
- **Two pages were created directly from this repo on 2026-07-31, before that was
  corrected.** Central command owns them now and may keep, replace or delete them:
  the cycle review `3ae96556906781e98643c34a75bd8a86` and a work-loop board
  `3ae96556906781699fbafe5eb90e89c6`.
- **Known defect in the page as built:** it is titled "Ancestry cycles" and says
  "35 cycles" while showing 35 *tangles*. A tangle is a strongly connected component and
  holds many loops; the "71 cycles" in `GENEALOGY_QA.md` counted loops. The two numbers
  are not in conflict but the page makes them look like they are.
