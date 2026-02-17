# order.life

Static website for **Lifeism** (命道教 / Order of Life) — a religion of universal flourishing, negative theology polytheism, and the moral horizon of immortality.

**Live domains**: order.life (primary), evolution.faith (redirects to order.life/evolution)

## What This Is

A multilingual static website generator that produces the order.life website in 9 languages:
- **en** English — Lifeism
- **ja** Japanese — 命道教 (Inochi-no-Michikyō)
- **zh** Chinese — 生命教 (Shēngmìngjiào)
- **es** Spanish — Vidaísmo
- **hi** Hindi — जीवनवाद (Jīvanavād)
- **ar** Arabic — حياتية (Hayātiyya)
- **fr** French — Viéisme
- **ru** Russian — Жизнеизм (Zhizneizm)
- **uk** Ukrainian — Життєїзм (Zhyttyeïzm)

Language subdomains follow Wikipedia conventions: en.order.life, ja.order.life, etc.

## Site Structure

| Path | Content |
|------|---------|
| `/` | Language selector with live Gaian date |
| `/{lang}/` | Homepage with today's date, core commitments |
| `/{lang}/calendar/` | Gaian Calendar overview (13 months) |
| `/{lang}/calendar/datepicker/` | Interactive date picker |
| `/{lang}/calendar/gaian-era/` | Gaian Era explainer |
| `/{lang}/calendar/week/` | Weekday index (7 sacred days) |
| `/{lang}/calendar/week/{day}/` | Weekday page (monday-sunday) |
| `/{lang}/calendar/{month}/` | Month page with day grid |
| `/{lang}/calendar/{month}/{dd}/` | Day page with wiki content + Gaiad link |
| `/{lang}/gaiad/` | Scripture index (364 chapters) |
| `/{lang}/gaiad/{NNN}/` | Individual Gaiad chapter |
| `/{lang}/scripture/` | Scripture overview |
| `/{lang}/mythology/` | Mythology of Aster & Andromeda |
| `/{lang}/philosophy/` | Negative theology polytheism |
| `/{lang}/shrines/` | 命神宮 Myōjingū shrines |
| `/{lang}/longevity/` | Universal immortality & transhumanism |
| `/{lang}/evolution/` | Evolution as sacred narrative |
| `/{lang}/fudoki/` | Hallowings of the Realms — first-level divisions database |
| `/{lang}/wiki/*` | Redirects to lifeism.miraheze.org/wiki/{lang}:* |
| `/wiki/*` | Redirects to lifeism.miraheze.org/wiki/* (English) |

## The Gaian Calendar

- 13 months of 28 days each (364 days) + Horus intercalary week (7 days in years with ISO week 53)
- Year = ISO week-year + 10,000 (Gaian Era)
- Current year: **12026 GE** (Gregorian 2026)
- Months: Sagittarius, Capricorn, Aquarius, Pisces, Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpius, Ophiuchus, (Horus)
- Each day 1-364 corresponds to a Gaiad chapter

## The Gaiad

A 364-chapter creation epic in iambic pentameter (ABAB rhyme scheme) telling the cosmic love story of Aster and Andromeda — from the Big Bang through evolution, human history, and cosmic reunion. One chapter per day of the Gaian year.

Currently 63 chapters complete (Chapters 1-63: Cosmogony through Early Carboniferous).

## Hallowings of the Realms (Fudoki)

Database of first-level administrative divisions worldwide, sourced from Wikidata. Merged from the [Hallowings-of-the-Realms](https://github.com/Immanuelle/Hallowings-of-the-Realms) project.

## Building

Requires Python 3 with Jinja2:

```bash
pip install jinja2
python build.py
```

Outputs static HTML to `site/` directory. ~10,800 pages across all languages.

## Tech Stack

- **Python + Jinja2**: Static site generation
- **Vanilla HTML/CSS/JS**: No framework dependencies
- **Dark cosmic theme**: Matching the Gaian Calendar aesthetic

## Key Files

- `build.py` — Site generator
- `templates/` — Jinja2 HTML templates
- `content/i18n/` — Translation JSON files (en, ja, zh, es, hi, ar, fr, ru, uk)
- `static/` — CSS and JS assets
- `epic/` — Gaiad epic chapters and reference materials
- `planning/` — Architecture and doctrine documentation
- `site/` — Generated output (gitignored)

## Connected Services

- **Wiki**: lifeism.miraheze.org (migrating to lifeism.miraheze.org)
- `/wiki/*` redirects to lifeism.miraheze.org (English, no lang prefix)
- `/{lang}/wiki/*` redirects with interwiki prefix (e.g. `ja:Title`, `hi:Title`)
