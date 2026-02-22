# order.life TODO

---

## ✅ Year Page (complete)
Compact year table, 1 row per Gaian month × 28 day columns, JS-driven.
Year/month and year/day sub-pages also implemented.

---

## ✅ iCal Calendars — Phase 1 (complete)

### Goal
Generate static subscribable `.ics` files as part of every CI/CD build.

### Output files (root-level, language-agnostic)
| URL | Description |
|-----|-------------|
| `/calendar/ical/current.ics` | Current GE year ± 2 + adjacent Gregorian year safety buffer |
| `/calendar/ical/gaian-holidays-extended.ics` | Gaian years 12000–12040 (Gregorian 2000–2040) |

Both written to `site/calendar/ical/` (root, not under a lang prefix).

### current.ics year range logic
- Build-time current Gaian year = ISO week-year + 10000
- Include GE years: (current_GE − 2) through (current_GE + 2)
- This safely covers the Gregorian/Gaian boundary regardless of when in the year the build runs

### All-day event format
```
DTSTART;VALUE=DATE:YYYYMMDD
DTEND;VALUE=DATE:YYYYMMDD   ← next calendar day (iCal exclusive end)
SUMMARY:Holiday Name
DESCRIPTION:Gaian date: Month Day\, Year GE
UID:gaian-YYYY-MM-DD-slug@order.life
```
No TZID needed — DATE type events are inherently timezone-free.

### Fixed holidays (computed per year by converting Gaian date → Gregorian)
These are included in both files:

| Gaian date | Event |
|-----------|-------|
| Sagittarius 1 | New Year's Day (Aster Day) |
| Sagittarius 8 | Coming of Age Day |
| Capricorn 7 | Groundhog Day |
| Capricorn 14 | Valentine's Day · Lupercalia |
| Capricorn 21 | Kinen-sai |
| Capricorn 28 | Lantern Festival |
| Aquarius 7 | Hinamatsuri |
| Aquarius 21 | Kōrei-sai · Ides of March · St Patrick's Day |
| Aries 14 | Cinco de Mayo |
| Gemini 14 | Nagoshi no Ōharai |
| Gemini 21 | Tanabata |
| Gemini 28 | Bastille Day |
| Cancer 28 | Qixi |
| Leo 14 | Alolalia |
| Virgo 12 | Mid-Autumn Festival |
| Virgo 14 | Shindensai |
| Libra 1 | Japan Sports Day |
| Ophiuchus 21 | Christmas Day · Dongzhi Festival |
| Horus 1 | Birth of Osiris *(leap years only)* |
| Horus 2 | Birth of Horus *(leap years only)* |
| Horus 3 | Birth of Set *(leap years only)* |
| Horus 4 | Birth of Isis *(leap years only)* |
| Horus 5 | Birth of Nephthys · Sabbath *(leap years only)* |
| Horus 7 | New Year's Eve *(leap years only)* |

### Moveable feasts — Christian season (included because calendar-linked)
Computed per year from Easter (Meeus-Jones-Butcher algorithm):

| Offset from Easter | Event |
|--------------------|-------|
| −46 days | Ash Wednesday (start of Lent) |
| −7 days | Palm Sunday |
| −2 days | Good Friday |
| −1 day | Holy Saturday |
| 0 | Easter Sunday |
| +39 days | Ascension Thursday |
| +49 days | Pentecost |

**NOT included:** Islamic calendar events, Jewish holidays (too divergent from Gaian calendar logic).

### Implementation location
- New function `generate_ical_files(site_dir)` added to `build.py`
- Called once at the end of `build_site()`, writing directly to `site/calendar/ical/`
- Easter computed via Python port of the same Meeus-Jones-Butcher algorithm used in `year-page.js`
- Gaian date → Gregorian date via ISO week arithmetic (same logic as `gregorian_to_gaian()` inverse)

---

## 📋 iCal Calendars — Phase 2 (future)

- `site/calendar/ical/gaian-detailed.ics` — all 364/371 days as labeled events
- Each day: Gaian date, Gaiad chapter number, element, weekday, any festival note
- Add a `/calendar/ical/` index page with subscribe links + instructions for Google/Apple/Outlook

---

## 📋 Programmatic Day Descriptions — Phase 3 (future, major feature)

Used in: `/calendar/year/{Y}/{MM}/{DD}/` pages AND detailed `.ics` descriptions.

### Algorithm inputs per day
- Gaian date (month, day, year GE)
- Gregorian date (for that specific year)
- Gaiad chapter number and theme (from `MONTH_THEMES`)
- Season / element context
- Fixed and moveable holidays on that day
- Cross-calendar notes (e.g. "Lent and Ramadan overlap this year in Aquarius–Pisces")
- Scheduled Lifeism events (from a curated JSON, TBD)

### Output
Short paragraph (2–4 sentences) rendered in the day page description and `.ics` event body.

### Data sources TBD
- Curated `content/day-events.json` keyed by `{month_num}/{day_num}` for recurring events
- Per-year JSON for scheduled events and notable overlaps
- Cross-calendar coincidence detection in build.py (e.g. detect Lent/Ramadan overlap for a given year)
