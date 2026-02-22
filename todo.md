# Year Page TODO

## Goal
Compact year calendar table, one row per Gaian month (not one row per day).
Modelled on https://wiki.order.life/wiki/Template:Gaian_calendar

## Table layout
- **Rows**: one per Gaian month (13 rows normally, 14 rows in a 53-week/Horus year)
- **Columns**: month name/symbol | Mon | Tue | Wed | Thu | Fri | Sat | Sun | Mon | ... (weekday header repeats 4 times across = 28 day columns total)
- **Each cell**: just the day number (1–28), no extra text
- **Hover tooltip** (`title` attr): shows Gregorian date for that cell (e.g. "Mon 29 Dec 2025")
- **Cell link**: clicking the number goes to the Gaian day page (`/calendar/sagittarius/01/`)
- **Horus row** (only in 53-week years): 7 filled cells, remaining 21 cells grayed/empty

## Styling
- Sabbath columns (Fri/Sat/Sun = every 5th/6th/7th col in each week group): subtle gold tint
- Easter cell: highlighted distinctly (amber/orange)
- Horus trailing empty cells: dark/grayed background
- Table scrollable horizontally on small screens (overflow-x: auto)

## Prose intro (above the table)
Full sentence giving:
- Gregorian start date of the Gaian year (e.g. "Monday 29 December 2025")
- Gregorian end date (e.g. "Sunday 3 January 2027")
- Whether it's a 53-week year (includes Horus) or 52-week year
- Easter date in both Gregorian and Gaian (e.g. "Easter: Sun 5 Apr 2026 = Pisces 14")

## Wiki link
Dynamic link to `https://wiki.order.life/wiki/{GAIAN_YEAR}_GE`

## Implementation notes
- Everything JS-driven (year-page.js); page shell is static HTML with `<div id="year-calendar">`
- GAIAN_YEAR constant injected by Jinja2: `<script>const GAIAN_YEAR = {{ display_year }};</script>`
- Years 12020–12040 are pre-generated at `/calendar/year/{year}/`
- Old `/calendar/{year}/` URLs redirect to new canonical path

## Current status (as of Feb 2026)
- URL structure: DONE (`/calendar/year/12026/` etc.)
- Build loop: DONE (21 years generated)
- Redirect: DONE
- JS file: EXISTS but currently renders WRONG layout (1 row per day, not 1 row per month)
  → Need to rewrite `buildYearCalendar()` in `static/js/year-page.js`
- year.html template: mostly correct shell, may need tweaks
