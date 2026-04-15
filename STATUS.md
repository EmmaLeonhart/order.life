# order.life — Current State

**Read this at the start of every session.** Truth table, not docs.
Lean — tracks what's left to do. Finished work lives in `git log` and
`planning/`.

## What this is

Static site generator + chapter pipeline for Lifeism (the order.life
website and the Gaiad scripture, 364 daily chapters). The Discord bot
posts one Gaiad chapter per day. Missing chapters = starved stream, so
chapter-count runway is the load-bearing metric. See `CLAUDE.md` for
build / calendar / language details.

## Chapter status (of 364)

Written (162):
- 1–129 contiguous (pre-human cosmogony, ends at "The Dawn of Humanity")
- 221–252 (32 chapters, 1453 CE → ~1720s, the first-drafted human block)
- 329 (one-off, Emperor Showa)

Missing (202):
- **130–220** (91 chapters) — the pre-1453 human arc. The active work.
- 253–328 (76 chapters) — indigenous-clash / modern period block.
- 330–364 (35 chapters) — tail, Ophiuchus + Horus.

Daily stream runway: ~3 weeks before ch 130 is due. Catch-up bot runs
longer regardless. Do not over-engineer — GitHub Actions cron is fine.

## Active work — chapters 130–220

The 91-chapter pre-modern human arc. Structural frame lives in
`planning/gaiad-130-220-structure.md` and `planning/gaiad-tone-and-founders.md`.
Do not re-generate chapter lists — the user has explicitly rejected
numbered chapter proposals ("trying to make a list of the chapters is
the absolute worst thing that can be done"). The planning docs are an
*unnumbered* chronology + tone + tiering; chapters emerge when the user
sits down to write them.

Three registers braid throughout the block, not sequentially:
- **A** haplogroup / migration (never closes — Hitler, Napoleon,
  Perry Y, Japanese D still belong here)
- **B** mythic antiquity (Irihor → Iliad → Ramayana coexist as
  same-texture sources)
- **C** proper historiography (post-BAC → 1453)

Pivot: Moses-synthesizes-the-alphabet at the Bronze Age Collapse.
Writing mode shifts within the narrative at that chapter.

Late-mythic-cycle tiering (which cultures get a clean mythic-to-
historical bridge):
1. Aztec (strongest — captured at moment of conquest)
2. Scandinavia, Japan (benchmark — Eddas, Kojiki/Nihon Shoki)
3. Rome, China (strong, China smoothed by Confucian rationalization)
4. Greece (thinner)
   + Mongolia, Arabia, Ethiopia confirmed strong
   + Lithuania counterfactual: the book never written (chapter idea)

West Eurasian super-network (not "Abrahamic"): Rome + Greece/Sparta +
Egypt + Mesopotamia + biblical + Muhammad-via-Rome + Jesus-via-Rome,
stretching NA → Europe → parts of India. Gateway ancestors:
Charlemagne, Bustanai (Exilarch × Sasanian princess Dara, ~610–670 CE,
Jewish/Persian/Islamic triple bridge), Jesus-via-Rome, Muhammad-via-Rome.

Asia is deliberately looser — polytheistic traditions handled on own
terms, surname/clan framing rather than royal-dynasty. One named
Asian-to-Asian bridge: Princess Heo Hwang-ok (Ayodhya → Korea → Japan,
~48 CE).

Required scale-correction inclusions: Indus Valley, Cucuteni-Trypillia,
Indo-European / Yamnaya expansion. Indigenous groups framed
descriptively, not morally.

## Wiki-sync bot (active)

`wiki-scripts/wikibase_dump.py` + `.github/workflows/wikibase-dump.yml`
walk numeric ID ranges on `wiki.order.life` and save each entity as
JSON under `wikibase/items/` and `wikibase/properties/`.

The GitHub Action dispatch was hitting 503s. The script works when run
locally (properties P1..P100 test: created=39 missing=61, no errors),
so the plan is: run locally against bigger ranges, commit the data to
master, then run network analysis on the genealogy graph once it's
populated.

Action items on the data once it lands:
- Empirical centrality: do Charlemagne / Bustanai actually pass the
  gateway-ancestor centrality test, or are other nodes doing the work?
- Weakly-connected components: how scattered is Asia, really?
- QA pass: cycles, impossible dates, excessive fan-out (conflation).

## Workflow reminders

- `python build.py` → `site/`. Dev server: `python -m http.server 8000 --directory site`.
- English is served at the site **root**, not `/en/`.
- Discord bot uses `discord-bot/state.json` to dedupe; extra runs are harmless.
- Use `C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe`
  (the `ambie` Python has no packages).
- **Do not run `python build.py` before every commit** — GitHub Actions
  handles deploy on push to master.

## Chat workflow

Claude Code / Claude.ai chat HTML exports land in `chats/`. Run
`python scripts/extract_chat.py` to produce a `.md` sibling. Chats are
triage inputs — once content is implemented or captured in
`STATUS.md` / planning, the chat can be deleted. See `chats/README.md`.

## Pointers

- Build config + URL structure: `CLAUDE.md`.
- Long-term agenda: `todo.md`.
- 130–220 architecture: `planning/gaiad-130-220-structure.md`.
- Tone principle + per-religion founder treatments:
  `planning/gaiad-tone-and-founders.md`.
- Draft chapters: `Gaiad/epic/chapter_NNN.md`.
- Discord bot: `discord-bot/bot.py` + `state.json`.
