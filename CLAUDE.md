# order.life FastSite

## Project Description
Static site generator for order.life — the website of **Lifeism** (命道教 / Order of Life).
Generates ~10,800 HTML pages across 9 languages from Jinja2 templates and JSON translation files.

## Quick Commands
- **Build site**: `python build.py` (outputs to `site/`)
- **Dev server**: `python -m http.server 8000 --directory site`
- **Requires**: Python 3 + Jinja2 (`pip install jinja2`)

## Architecture

### Build System
- `build.py` — Main generator. Reads templates + translations + epic chapters + wiki XML, outputs static HTML to `site/`
- Templates in `templates/` (Jinja2)
- Translations in `content/i18n/*.json` (9 languages)
- Glossary in `content/glossary.json` (localized proper nouns per language)
- Static assets in `static/css/` and `static/js/`
- Epic chapters in `epic/chapter_NNN.md`
- Wiki XML export: `Evolutionism+Wiki-20260209181520.xml` (parsed for day/month content)

### URL Structure (per language)
```
/{lang}/                              Homepage
/{lang}/calendar/                     Calendar overview
/{lang}/calendar/datepicker/          Interactive datepicker
/{lang}/calendar/gaian-era/           Gaian Era explainer
/{lang}/calendar/12026/               Year page
/{lang}/calendar/week/                Weekday index (7 sacred days)
/{lang}/calendar/week/{day}/          Weekday page (monday-sunday)
/{lang}/calendar/{month}/             Month page (sagittarius, capricorn, etc.)
/{lang}/calendar/{month}/{dd}/        Day page (01-28)
/{lang}/gaiad/                        Gaiad scripture index
/{lang}/gaiad/{NNN}/                  Gaiad chapter (001-364)
/{lang}/{section}/                    Section pages (scripture, mythology, philosophy, shrines, longevity, evolution)
/{lang}/wiki/*                        Redirect to evolutionism.miraheze.org/wiki/{lang}:*
/wiki/*                               Redirect to evolutionism.miraheze.org/wiki/*
```

### Wiki Redirects
- English (`/en/wiki/*` or `/wiki/*`): redirects to `evolutionism.miraheze.org/wiki/{title}` (no lang prefix)
- Other languages (`/{lang}/wiki/*`): redirects to `evolutionism.miraheze.org/wiki/{lang}:{title}`
- Both static per-page redirects (from XML export) and JS fallback for unknown pages

### Gaian Calendar
- 13 months x 28 days = 364 days + Horus intercalary (7 days, ISO week 53 years only)
- Year = ISO week-year + 10,000 (Gaian Era)
- Month IDs: sagittarius, capricorn, aquarius, pisces, aries, taurus, gemini, cancer, leo, virgo, libra, scorpius, ophiuchus, horus
- Day N of year = Gaiad chapter N
- Wiki uses "Scorpio" not "Scorpius" for month 12 — build.py handles mapping
- Every date permanently falls on the same weekday (perpetual calendar)
- Friday, Saturday, Sunday are the three Sabbaths

### Languages
| Code | Name | Religion Name | RTL |
|------|------|--------------|-----|
| en | English | Lifeism | No |
| ja | Japanese | 命道教 (Inochi-no-Michikyō) | No |
| zh | Chinese | 生命教 (Shēngmìngjiào) | No |
| es | Spanish | Vidaísmo | No |
| hi | Hindi | जीवनवाद (Jīvanavād) | No |
| ar | Arabic | حياتية (Hayātiyya) | Yes |
| fr | French | Viéisme | No |
| ru | Russian | Жизнеизм (Zhizneizm) | No |
| uk | Ukrainian | Життєїзм (Zhyttyeïzm) | No |

### Key Branding
- Symbol: 命 (life/destiny/command)
- 命 replaces 神 in sacred contexts
- Shrines: 命神宮 (Myōjingū)
- Wiki: currently evolutionism.miraheze.org, migrating to lifeism.miraheze.org

### Hallowings (Fudoki)
- Realm data in `realms/realms.json`, enriched via `realms/enrich_realms.py`
- `enrich_realms.py` queries Wikidata SPARQL for country, population, area, flag, locator map, geoshape
- Names standardized to "Realm of X" by stripping suffixes (Prefecture, Province, Oblast, State, etc.)
- Manual overrides in `MANUAL_OVERRIDES` dict for edge cases (Moscow, Tokyo, Federal District, etc.)
- Sorted by country (alpha) then realm_name (alpha)
- Images served via Wikimedia Commons `Special:FilePath/{filename}?width={N}`
- Interactive maps via Leaflet.js with CartoDB Dark tiles; GeoJSON fetched from Commons `jsondata` API
- English-only for now (`/en/fudoki/` and `/en/fudoki/{QID}/`)

## Conventions
- Commit early and often with descriptive messages
- Keep README.md updated for human readers
- All thinking produces files, not planning-only modes
- Use `python` not `python3` on this Windows system
- Use `C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe` for the Python with packages
- Build uses temp dir swap (site_tmp → site) — stop dev server before rebuilding to avoid Windows lock errors
- Do NOT run `python build.py` before every commit — just commit and push, the user checks online
