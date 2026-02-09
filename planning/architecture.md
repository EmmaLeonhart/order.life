# order.life Site Architecture

## Domain Structure
- **Primary domain**: order.life
- **Redirect**: evolution.faith -> order.life/evolution
- **Language subdomains** (Wikipedia-style): en.order.life, ja.order.life, zh.order.life, es.order.life, hi.order.life, ar.order.life
- **Wiki redirect**: any /wiki/* path -> lifeism.miraheze.org/wiki/*

## Tech Stack
- **Static site generator**: Python build script with Jinja2 templates
- **Output**: Static HTML/CSS/JS in `site/` directory, one subdirectory per language
- **Styling**: Dark cosmic theme matching gaian-date-picker aesthetic
- **Calendar logic**: Client-side JS (ported from gaian-date-picker.html)
- **No framework dependencies**: Pure HTML/CSS/JS output

## Site Map (per language)
```
/{lang}/                          Homepage with live Gaian date
/{lang}/calendar/                 Calendar overview & explanation
/{lang}/calendar/datepicker       Interactive Gaian datepicker
/{lang}/calendar/{month}          Month page (sagittarius, capricorn, etc.)
/{lang}/calendar/{month}/{dd}     Day page (01-28, or 01-07 for horus)
/{lang}/calendar/{year}           Year page (e.g. 12026)
/{lang}/calendar/gaian-era        Gaian Era explanation
/{lang}/gaiad/{NNN}               Scripture chapter (001-364)
/{lang}/scripture/                Scripture overview
/{lang}/mythology/                Mythology section
/{lang}/philosophy/               Philosophy section
/{lang}/shrines/                  Shrines section (命神宮 Myojingu)
/{lang}/longevity/                Longevity/transhumanism section
/{lang}/evolution/                Evolution story section
```

## Gaian Calendar Logic
- 13 months x 28 days = 364 days
- Month 14 "Horus" = 7 intercalary days (only in years with ISO week 53)
- Year = ISO week-year + 10,000
- Months named after zodiac: Sagittarius(1) through Ophiuchus(13), Horus(14)
- Each day 1-364 corresponds to Gaiad chapter of same number
- Days always start on Monday (ISO week alignment)

## Languages
| Code | Language | Religion Name | Script Direction |
|------|----------|--------------|-----------------|
| en   | English  | Lifeism      | LTR |
| ja   | Japanese | 命道教 (Inochi-no-Michikyō) | LTR |
| zh   | Chinese  | 生命教 (Shēngmìngjiào) | LTR |
| es   | Spanish  | Vidaísmo     | LTR |
| hi   | Hindi    | जीवनवाद (Jīvanavād) | LTR |
| ar   | Arabic   | حياتية (Hayātiyya) | RTL |

## Key Branding
- Symbol: 命 (mei/myō/inochi - "life/destiny/command")
- 命 replaces 神 in sacred contexts
- Shrines: 命神宮 (Myōjingū)
- Extension of Shinto shrine tradition
