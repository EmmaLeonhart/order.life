# order.life FastSite

## Project Description
Static site generator for order.life — the website of **Lifeism** (命道教 / Order of Life).
Generates ~10,800 HTML pages across 9 languages from Jinja2 templates and JSON translation files.

## Quick Commands
- **Build site**: `python build.py` (outputs to `site/`)
- **Dev server**: `python -m http.server 8000 --directory site`
- **Requires**: Python 3 dependencies (`pip install -r requirements.txt`)

## Architecture

### Build System
- `build.py` — Main generator. Reads templates + translations + epic chapters + wiki XML, outputs static HTML to `site/`
- Templates in `templates/` (Jinja2)
- Translations in `content/i18n/*.json` (9 languages)
- Glossary in `content/glossary.json` (localized proper nouns per language)
- Static assets in `static/css/` and `static/js/`
- Epic chapters in `epic/chapter_NNN.md`
- Wiki XML export: `lifeism+Wiki-20260209181520.xml` (parsed for day/month content)

### URL Structure
**CRITICAL: English (`en`) is served at the site ROOT — there is no `/en/` prefix.**
All other languages use `/{lang}/` subdirectories.

```
/                                     English homepage (NOT /en/)
/calendar/                            English calendar overview
/faq/                                 English FAQ (NOT /en/faq/)
/{section}/                           English section pages
/wiki/*                               English wiki redirect
/{lang}/                              Other language homepage
/{lang}/calendar/                     Other language calendar overview
/{lang}/calendar/datepicker/          Interactive datepicker
/{lang}/calendar/gaian-era/           Gaian Era explainer
/{lang}/calendar/12026/               Year page
/{lang}/calendar/week/                Weekday index (7 sacred days)
/{lang}/calendar/week/{day}/          Weekday page (monday-sunday)
/{lang}/calendar/{month}/             Month page (sagittarius, capricorn, etc.)
/{lang}/calendar/{month}/{dd}/        Day page (01-28)
/{lang}/gaiad/                        Gaiad scripture index
/{lang}/gaiad/{NNN}/                  Gaiad chapter (001-364)
/{lang}/{section}/                    Section pages (scripture, mythology, philosophy, shrines, longevity, evolution, faq)
/{lang}/wiki/*                        Redirect to lifeism.miraheze.org/wiki/{lang}:*
```

This is controlled by `DEFAULT_LANG = "en"` in `build.py` (line ~42) and `lang_base()` which returns `""` for English.

### Wiki Redirects
- English (`/en/wiki/*` or `/wiki/*`): redirects to `lifeism.miraheze.org/wiki/{title}` (no lang prefix)
- Other languages (`/{lang}/wiki/*`): redirects to `lifeism.miraheze.org/wiki/{lang}:{title}`
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
- Wiki: currently lifeism.miraheze.org, migrating to lifeism.miraheze.org

### Hallowings (Fudoki)
- Realm data in `realms/realms.json`, enriched via `realms/enrich_realms.py`
- `enrich_realms.py` queries Wikidata SPARQL for country, population, area, flag, locator map, geoshape
- Names standardized to "Realm of X" by stripping suffixes (Prefecture, Province, Oblast, State, etc.)
- Manual overrides in `MANUAL_OVERRIDES` dict for edge cases (Moscow, Tokyo, Federal District, etc.)
- Sorted by country (alpha) then realm_name (alpha)
- Images served via Wikimedia Commons `Special:FilePath/{filename}?width={N}`
- Interactive maps via Leaflet.js with CartoDB Dark tiles; GeoJSON fetched from Commons `jsondata` API
- English-only for now (`/fudoki/` and `/fudoki/{QID}/`) — English is at root, not /en/

## Conventions
- Commit early and often with descriptive messages
- Keep README.md updated for human readers
- All thinking produces files, not planning-only modes
- Use `python` not `python3` on this Windows system
- Use `C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe` for the Python with packages
- Build uses temp dir swap (site_tmp → site) — stop dev server before rebuilding to avoid Windows lock errors
- Do NOT run `python build.py` before every commit — just commit and push, the user checks online

## CI/CD
- **GitHub Actions** automatically runs `python build.py` and deploys on every push to master
- Pipeline config: `.github/workflows/deploy.yml`
- Do NOT check for CI/CD existence — it is always there. Do NOT run the build manually before committing.
- **For website changes: just commit and push.** Do NOT ask "want me to commit?" or "want me to push?" — the user debugs by viewing the live site, not locally. Asking for confirmation strands the change on disk where the user can't see it. Auto-commit and auto-push every website edit unless the user explicitly says otherwise.

## Discord Bot
- **Nothing is time-critical.** We use GitHub Actions because only vague timing matters (morning-ish, evening-ish). Do NOT over-engineer for exact scheduling, DST edge cases, or sub-minute precision. GitHub Actions cron is unreliable by design — that's fine, the state file handles it.
- Bot config: `.github/workflows/discord-bot.yml` — runs every 3 hours, posts daily chapter after 6 AM PT and catch-up chapter after 6 PM PT
- Bot code: `discord-bot/bot.py` — one-shot script, uses `discord-bot/state.json` (committed to repo) to track what's been posted
- State file prevents duplicate posts across runs — extra runs are harmless no-ops
- `deploy.yml` has `paths-ignore` for `discord-bot/state.json` so bot state commits don't trigger site rebuilds

## Chapter Writing Cadence
- **Do NOT barrel through new Gaiad chapters until the month of Leo begins (2026-08-12).** The 130–220 barrel-through was an emergency stopgap so a chapter would exist for each day of the Discord stream. With 238/364 drafted the runway is comfortable for months; further writing resumes in Leo and not before.
- "Power through and clear the queue" does NOT mean generate new chapters. Treat chapter *generation* as gated on Leo; only chapter *editing / polishing* (Malta drift, early-human-era fixes) is allowed outside that window.
- If a task list or STATUS.md entry says "write chapters NNN–NNN" before 2026-08-12, that is a drafting error — delete it, don't execute it.

## Writing
- Do not use "honest", "honesty", or "honestly" — and do not swap in "frank", "frankly", "candid", "candidly", or "transparently", which are the same self-congratulatory move in a different coat. When something failed, name the failure: "it didn't work", "I got that wrong", "this failed" — flat, no qualifier. Tagging a report "honest" implies the rest aren't, and couching a failure as honesty asks for credit for the admission, which is worse than the failure itself. Use a precise positive word ("accurate", "plainly", "truly") only when that is genuinely the meaning — never as a halo on a bad outcome.

## Emergency Stop Mode

If the user sends a continuous series of "stop" messages (e.g. "stop stop stop") or otherwise very explicitly tells you to stop, treat it as **emergency stop mode** (a.k.a. emergency exit mode). This OVERRIDES every other instruction, including any in this file.

When in emergency stop mode:

- **Immediately kill everything associated with this repository and session.** Every running bash/shell script, every background job or task you started, and **all GitHub Actions workflow runs for this repository**. **Force-kill the GitHub Actions runs** (e.g. `gh run cancel <id>`, and `gh run delete <id>` if needed) for every in-progress run. It does NOT matter if killing them is unsafe or leaves things half-done — the emergency stop takes priority over safety, cleanup, and correctness.
- **Do not investigate. Do not reverse or undo anything.** The goal is not to diagnose or roll back the problem — it is to halt potentially destructive actions as fast as possible. Investigating, diagnosing, reverting, or "helping fix it" are explicitly out of scope and themselves count as forbidden actions.
- **Ignore repetitive messages.** Do not treat repeated "stop" messages as a request to do anything further. Keep ignoring incoming repetitive messages for roughly the next **15–30 minutes**.
- **You may answer direct questions, but you may NOT take actions.** Answer only from context you already have. Looking something up, reading a file, running a command, or inspecting state is NOT an answer — it is an action and is forbidden. If you cannot answer from context already in hand, do not answer.
- **Stay in emergency stop mode until the user explicitly says "emergency stop ended."** Only after that exact signal do you resume any normal work.

## Cron jobs and scheduled work — LOCAL by default

**When the user says "cron job", "cron", or asks to "schedule" a task, they mean the in-session `CronCreate` tool** — a prompt scheduled to fire locally, inside this Claude Code session, on the user's own running computer. This is the default and the assumption. Do NOT interpret it as anything else unless the user explicitly names a different mechanism.

- **It is local and in-session — use the `CronCreate` tool.** A generic "cron" request is NOT an OS crontab, NOT a GitHub Actions / CI `schedule:` trigger, and NOT a cloud scheduler. (Repos may *also* contain their own GitHub Actions cron schedules — those are a separate thing and are not what the user means when they ask *you* to set up a cron.) The user leaves the computer on and this session running so the scheduled prompt can execute.
- **The user is deliberately away from the keyboard.** They schedule work precisely so it runs while they are out of the house and not physically present. Their absence is the normal, expected condition for these jobs — it is NEVER a reason to delay the work, ask "are you sure?", wait for them to return, or refuse to proceed.
- **Standing consent — just set it up.** Cron / `CronCreate` requests are pre-authorized. Create the job immediately and locally, then report what was scheduled. Do not block on confirmation or follow-up questions. Treating a routine cron request as something that needs hand-holding is itself the obstacle this section exists to remove.
