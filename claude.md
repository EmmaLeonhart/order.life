# order.life FastSite

## Project Description
Static site generator for order.life — the website of **Lifeism** (命道教 / Order of Life).
Generates ~4,500 HTML pages across 6 languages from Jinja2 templates and JSON translation files.

## Quick Commands
- **Build site**: `python build.py` (outputs to `site/`)
- **Requires**: Python 3 + Jinja2 (`pip install jinja2`)

## Architecture

### Build System
- `build.py` — Main generator. Reads templates + translations + epic chapters, outputs static HTML to `site/`
- Templates in `templates/` (Jinja2)
- Translations in `content/i18n/*.json` (en, ja, zh, es, hi, ar)
- Static assets in `static/css/` and `static/js/`
- Epic chapters in `epic/chapter_NNN.md`

### URL Structure (per language)
```
/{lang}/                          Homepage
/{lang}/calendar/                 Calendar overview
/{lang}/calendar/datepicker       Interactive datepicker
/{lang}/calendar/{month}/         Month page (sagittarius, capricorn, etc.)
/{lang}/calendar/{month}/{dd}/    Day page (01-28)
/{lang}/gaiad/{NNN}/              Gaiad chapter (001-364)
/{lang}/{section}/                Section pages (scripture, mythology, philosophy, shrines, longevity, evolution)
/wiki/*                           Redirect to evolutionism.miraheze.org
```

### Gaian Calendar
- 13 months x 28 days = 364 days + Horus intercalary (7 days, ISO week 53 years only)
- Year = ISO week-year + 10,000 (Gaian Era)
- Month IDs: sagittarius, capricorn, aquarius, pisces, aries, taurus, gemini, cancer, leo, virgo, libra, scorpius, ophiuchus, horus
- Day N of year = Gaiad chapter N

### Languages
| Code | Name | Religion Name | RTL |
|------|------|--------------|-----|
| en | English | Lifeism | No |
| ja | Japanese | 命道教 | No |
| zh | Chinese | 生命教 | No |
| es | Spanish | Vidaísmo | No |
| hi | Hindi | जीवनवाद | No |
| ar | Arabic | حياتية | Yes |

### Key Branding
- Symbol: 命 (life/destiny/command)
- 命 replaces 神 in sacred contexts
- Shrines: 命神宮 (Myōjingū)
- Wiki: currently evolutionism.miraheze.org, migrating to lifeism.miraheze.org

## Conventions
- Commit early and often with descriptive messages
- Keep README.md updated for human readers
- All thinking produces files, not planning-only modes
- Use `python` not `python3` on this Windows system
- Use `C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe` for the Python with packages
