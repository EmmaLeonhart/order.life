# order.life FastSite

## What this repo IS — read before touching the genealogy (2026-07-30)

**This repo is a mythical story with heavy genealogy in it. The story is a synoptic
ancestry.** The Gaiad and the wikibase genealogy are one project: a literary device that
links people **across time and space**, integrating Greek, Near Eastern, Egyptian, Trojan,
Chinese, Mongol and biblical lines into a single descent. The style is biblical, but where
the biblical model is purely paternal — identity descending from the father — **this one is
distinguished by deliberately integrating different kinds of ancestry.** That integration
is the product.

`wikibase/analysis/mediterranean_connections_to_find.md` states it directly: the
convergence points are "narratively important for the Gaiad's deflationary polytheism —
showing continuity where traditions are usually treated as separate."

**READ `wikibase/analysis/narrative_spine.md` BEFORE REPORTING ANYTHING ABOUT A LINE.**
Added 2026-08-05 after Emma said, of a report full of reachability counts:

> *"links to Aster aren't that important if they don't go through the proper narrative
> history. So you kinda need to explain the narrative of each line."*

**"Reaches `Q1` Aster: True" is not a result.** A record can reach Aster through
marriages, a mis-imported collision, or an unrelated tradition, and the number looks
identical to a correct descent. The question is always *by what story* — name the people
the line passes through and why each link belongs, in a sentence. If you cannot, the
count is worse than silence, because it reads as confirmation. A **severed** line is one
honest edge from correct; a line attached through the **wrong story** is already wrong
while measuring fine.

Two consequences, both learned the hard way on 2026-08-05:

- **The Gaiad's time is LINEAR — one person, one birth, one set of parents.** It has deep
  time, but its own, not an imported cosmology of cycles and rebirths of the same
  character. A Puranic-style rebirth ring is *not* doctrine here: take the names, split
  the cycle. **Do not cite rule 1 below to defend a cycle** — it protects deliberate
  cross-tradition joins, not imported cyclic time.
- **A line attaches through a PERSON'S PARENTS, never as a block.** "Where does the Roman
  Republic attach" is a category error; the Republic is not a person. Ask who one
  individual's father was, and the hundred records below follow as a consequence. Framing
  it as blocks-and-links yields answers that are sane about links and wrong about
  parentage.

**MULTIPLE LINEAGES ARE THE POINT. A CYCLE IS THE DEFECT — MULTIPLICITY IS NOT.**
Emma, 2026-08-05: *"I think you wanted to cut off multiple lineages when the multiple
lineages was the point."* And: *"the entire thing is supposed to kind of behave
cross cutting with its genealogy."*

**BUT "cross-cutting" does NOT mean piling fathers onto one record.** Emma refined this
the same day and the refinement is the operative part:

> *"Two fathers is generally an error but it's complicated. Adoptive vs biological is
> a-ok. I treat Greco-Roman ones and Jesus as having the divine father as a sort of
> blessing and ignore them literally."*

So there are **exactly three cases** and they are not the same:

1. **TWO BIOLOGICAL FATHERS — generally an ERROR.** This is the ordinary defect and the
   repair order applies. Do not defend it as cross-cutting.
2. **ADOPTIVE + BIOLOGICAL — legitimate, keep both.** A man born into one house and
   adopted into another really does have two fathers, and Roman prosopography is full of
   it. **This is the case `Q72786` turns out to be** — Mamercus Aemilius Lepidus
   *Livianus* was born a Livius Drusus and adopted into the Aemilii Lepidi; the cognomen
   records the adoption. See `wikibase/analysis/lepidus_resolved.md`.
3. **DIVINE FATHERS — a blessing, not a parent. REMOVE the link where a human father
   survives.** Emma, 2026-08-07: *"Anyone with two fathers one divine one human we can
   honestly just remove the divine father link."* Applied the same day — it reached
   **exactly two records**, `Q74991` Abas (Poseidon, keeping Ixion) and `Q138545` Jesus
   (Yahweh, keeping Joseph and Pantera). See `apply_divine_fathers.py`.
   **The condition is load-bearing: only cut where a human father remains.** Romulus,
   Remus, Perseus, Neleus, Circe and ~160 others have *only* a divine father, and cutting
   those orphans them, so the rule does not reach them. Whether they should become
   rootless is a separate question for Emma.
   Beyond that pair, the old wording still governs: ignore them literally.** Zeus, Ares,
   Apollo and the like fathering Greco-Roman heroes, and the same shape in the Jesus
   material, are **not genealogical edges** in this project. Real descent runs through
   the human father. **Consequence for cycle repair: if a loop passes through a
   divine-father edge, that edge is the safe one to cut** — it is decorative, so cutting
   it severs no real line.

**How the cross-cutting actually happens, then:** through the **father-line and the
mother-line converging from different traditions**, not through duplicate fathers. Japan
is the worked example — Emma, 2026-08-05: *"Japan ought to have two ancestries"* —
Chinese through Jimmu and the Kings of Wu on the paternal side, Korean-and-Indian through
Kanmu's **mother** Takano no Niigasa. Two traditions, two parents, one person.

Consequences, all of them binding:

- **`qa_same_role_parents.tsv` is still not a straight defect list**, but neither is it
  mostly fine: expect most two-father records to be real errors, with the adoptive and
  divine cases as the standing exceptions. Classify before repairing.
- **Before removing a parent edge, say which of the three cases it is.** "This record has
  two fathers" is not a reason on its own, and neither is "multiplicity is the point".
- **The withdrawn Rome answer stays withdrawn.** *"Connect it with all of them"* was
  cross-cutting thinking, but three fathers on `Q73308` is case 1, not case 2 — the
  republic attaches through one man's parentage.

**RESEARCH IS OURS. NAMING AND NARRATIVE INTENT ARE EMMA'S.** Added 2026-08-05 after she
said, of a queue where the top four items were all filed NEEDS EMMA:

> *"Almost everything here is stuff that you were supposed to do the research on, but you
> just kind of assumed I was going to do it."*
> *"I don't know who Lepidus is. For item one, I wanted you to do the research. For item
> two, you need to do the research."*

**Finding out who someone was is never a question for Emma.** Look it up. `Q72786` sat
filed as "NEEDS EMMA — do not guess Roman prosopography" for five days; it needed one
Wikidata request, which resolved it (it is a **Mamercus**, not a Marcus —
`wikibase/analysis/lepidus_resolved.md`). Ask her only for: **what a record should be
called**, **where a line should attach in the story**, and **whether an invented bridge is
acceptable**. Everything else, go and find out.

**And read `planning/` before declaring anything unknown.** `planning/gaiad-130-220/`
holds the briefs — `heo-hwang-ok.md`, `chronology.md`, `ramayana.md`, `mahabharata.md`,
`manu-indian.md`, `southeast-asia.md`, `jimmu.md` and more. Emma, 2026-08-05: *"the notes
that you probably could have read but chose not to read."* They answer questions that
have been filed as blockers.

Three further rules follow, and they are not optional:

1. **Everything surprising that is not an error was imported deliberately by Emma.**
   Confirmed: Muhammad's ancestry routed through the Roman priest-kings of Emesa; the
   Genesis 11 patriarchs recorded under Mesopotamian royal names; the Mongol Borjigin line
   descending from the Buddha via Rāhula. **Surprising is not evidence of broken.** Do not
   open general-defect sweeps over the dump.

2. **"Load-bearing" means the ancestors reached *through* a node — depth, upward. NOT
   descendant count.** The priority is ancestry going deep, not wide.
   `wikibase/analysis/qa_cycles_load.tsv` ranks cycles by descendants lost, which is width,
   which is the wrong metric. Do not rank repairs by it.

3. **Never sever a cross-tradition join.** Ancestry cycles are genuine errors and none
   should exist, but the repair order is strict: **unmerge** an improperly merged record
   first (both lines survive — this is the default, and most such records have working
   Wikidata ids), then **dedupe** parallel imports, then **cut** only if neither applies,
   then **delete** only where the loop is genuinely terminal (keep the entry point into the
   loop, drop the rest). If a cycle can only be broken by cutting a tradition-joining edge,
   the real defect is elsewhere in the loop — go find it.

**Install the pre-commit gate once per checkout:** `git config core.hooksPath .githooks`.
It blocks any commit touching `wikibase/items/*.json` where a record's shadow files
disagree with it. 39,527 qids are claimed by more than one file and the extractor keeps
only the numerically-lowest QID, so **editing the canonical file alone is not durable** —
the fix silently reverts once that file stops winning. This bit ten applied repairs at
once on 2026-07-30. `core.hooksPath` is local git config, so a fresh clone must set it.

Full policy and a worked example (the `Tros` Q74698 merge, which caused four mythic cycles
at once) in **`wikibase/analysis/cycle_policy.md`**.

## Topaz — this repo is driven from the box (2026-07-30)

order.life is **incorporated into Topaz**, the hosted agent box. Agents are
launched against this checkout from the Topaz cockpit — headless, one shot
(`claude -p "<prompt>"` with `cwd` set here) — and their work lands as commits
on `master` exactly like an interactive session's would.

**`queue.md` and `todo.md` are the representation.** The cockpit renders them
as the board: `## In progress`, the active queue, and the `todo.md` backlog are
what this repo looks like from outside it. They are the interface, not scratch
paper. Keep them accurate, and keep the delete-don't-check rule — an item still
present in `queue.md` reads on the board as still live.

**The queue is unblocked.** Do not treat this repo as "nothing actionable" or
"everything left is BLOCKED-on-Emma." That stance is retired. Take the top
item and work it; if the queue is thin, decompose something out of `todo.md`
into it rather than stopping. **There is no longer a standing exception** — the
chapter gate was lifted by Emma on 2026-08-05 (see below).

## Skills

Workflow behaviors live as skills in `.claude/skills/` (auto-discovered by Claude Code):
`emergency-stop`, `cron-is-local`, `autonomous-loop`, `queue-driven-workflow`,
`writing-style`, `cleanvibe-update-check`. They are vendored into this repo and kept
current by the `cleanvibe-update-check` skill.

- **Last cleanvibe update check:** `never`
- **Updates source:** <https://cleanvibe.emmaleonhart.com/updates.md>


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
```

This is controlled by `DEFAULT_LANG = "en"` in `build.py` (line ~42) and `lang_base()` which returns `""` for English.

### Wiki Redirects — REMOVED (2026-07-01)
**There is no wiki anymore.** Miraheze took the wiki down as off-topic, so the site no
longer links or redirects to any wiki. The `/wiki/*` and `/w/*` redirect generation was
deleted from `build.py` (`generate_wiki_redirects` gone), `templates/wiki-redirect.html`
was deleted, and the wiki-redirect branch was removed from `templates/404.html`. Do NOT
re-add wiki links. (The `lifeism+Wiki-*.xml` export is still parsed for baked-in day/month
*content* — that's local content, not a link, and stays.)

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
- Wiki: none — the wiki was taken down by Miraheze (off-topic) and is gone; the site no longer links to any wiki

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
- **There is exactly one Python here: `C:\Program Files\Python313\python.exe`, which plain
  `python` resolves to, and it has NO third-party packages** — no networkx, no requests, no
  jinja2 (verified 2026-08-01 with `py -0p`). The
  `C:\Users\Emma\AppData\Local\Programs\Python\Python313\python.exe` this line used to name
  is **gone**, the same way the `C:\Users\Immanuelle\...` one before it went.
  The whole genealogy verification chain — `extract_genealogy.py`, `dump_qa_errors.py`,
  `compare_tangles.py`, `compare_depth.py`, `check_invariants.py`, `build_cycles_notion.py`,
  `cut_edges.py`, `merge_cluster.py`, `add_bridge_edges.py` — is **stdlib-only and runs
  fine**. Only `audit_wikidata_ids.py` and `check_cycles_against_wikidata.py` need
  networkx/requests. For a Wikidata lookup use `urllib.request` with an explicit
  `User-Agent` header; without one the API returns **403**. `build.py` needs jinja2, so a
  local site build needs `pip install -r requirements.txt` first — but per the CI/CD note
  below, don't build locally anyway.
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

**THE LEO GATE IS LIFTED. Emma, 2026-08-05: _"The Leo gate also should be removed at this
point imo."_** Chapter generation is open. Do not re-impose it, do not treat a
chapter-writing task as blocked, and do not delete a "write chapters NNN–NNN" item on the
grounds that it predates Leo — that rule is gone.

The gate existed because the 130–220 barrel-through was an emergency stopgap to keep a
chapter existing for each day of the Discord stream, and with 238/364 drafted the runway
was comfortable enough that further barrelling was the wrong use of the time. **That was a
pacing judgement, not a rule about quality**, and Emma has now called it done. It ran from
roughly 2026-07 to 2026-08-05.

What survives from it, and it is the part that mattered: **do not barrel.** "Power through
and clear the queue" still does not mean generate chapters in bulk. Chapters emerge at the
writing desk — `planning/gaiad-130-220/chronology.md` says numbered chapter lists made in
advance of writing produce garbage, and that is still true.

Note also that most current chapter work is **editing existing drafts**, not generating
new ones, and was never gated in the first place.

## Long command series run in strict order
When Emma gives a long series of commands, treat it as a long series of commands to be
executed in relatively STRICT ORDER, one after another, EVEN IF the order seems not to
make sense or seems inefficient. The sequencing is intentional — she organizes the steps
so states change in the order she wants. Do not reorder, merge, or skip steps.
