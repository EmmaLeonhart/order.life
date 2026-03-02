# order.life TODO

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
