# order.life — Work Queue

**This file is a queue, not a state snapshot.** When an item is done, delete it. Finished work lives in `git log` and `planning/`.

The work here is **making the Gaiad ship as a daily stream and the order.life site stand on its own** — 364 chapters of real scripture, calendar tooling that subscribers can trust, and a body of content that survives the wiki going dark. The question each queue item answers is: *what does it take to make this thing a real, finished artifact?*

## Chapter runway (load-bearing metric)

Written: **238 / 364**. Remaining gaps: **253–328** (76), **330–364** (35).

**Do not write more chapters until the month of Leo begins (2026-08-12).** The 130–220 barrel-through was an emergency stopgap to keep the daily stream from starving. The stream is now comfortable for months. Further chapter writing resumes when Leo starts; until then, any chapter work should be editing / polishing existing drafts, not generating new ones.

## Queued work

1. **Fix the Malta chapter and the late-Capricorn drift.** Emma flagged that the Malta chapter and the late-Capricorn stretch drifted from the earlier poetic form into a declarative / expository mode — probably because the source material was more fleshed-out, which "poisoned" the register. The fix is not a rewrite; it is a tone correction in place: compress, re-shape into the ABAB-ish verse form, keep the facts, cut the reporter voice. Earlier chapters ship first, so this has priority over further writing.

2. **Fix the early human-era chapters first.** The 130–205 block was power-through quality — real chapters but first-pass. Emma has said to prioritize fixing earlier chapters because they ship through the Discord stream first. Start at 130 and work forward; don't wait on a full editing pass. The register should match the register set by 1–129 (verse, not declarative).

3. **Unlink the wiki from the site.** `lifeism.miraheze.org` is closing (see `memory/wiki_closure_status.md`). The site still has wiki redirects — English `/wiki/*` and `/{lang}/wiki/*` both point to the Miraheze instance. Those links will rot. Strip them, redirect to an in-repo page, or point at whatever replacement surface the content ends up on. Do not leave broken links in the shipped site.

4. **iCal bug fix + Phase 1 spec.** `generate_ical_files()` in `build.py` uses `m["name"]` but `MONTHS` uses `m["id"]` — currently broken. Fix: `{m["num"]: m["id"].capitalize() for m in MONTHS}`. After that, the revised `current.ics` format has three layers (daily Gaian-date events, holiday events, season-span events); `gaian-holidays-extended.ics` stays holidays-only. Full spec in the detached notes below in `todo.md` §iCal.

5. **Genealogical analysis follow-up.** The Wikibase dump completed 2026-04-16 — 164k items, 4,840 wiki pages, 377 images. Centrality passed (Charlemagne, Bustanai, Jesus, Muhammad all load-bearing). Open: 1,230 children-with->2-parents (Geni merge errors, mostly Iberian royals), 69 cycles that should be zero, fan-out suspects (Danaus 231, Oceanus 155, Dhritarashtra 131, Heracles 113). Lineage gaps: Kosala → Heo Hwang-ok (~15–20 invented kings), Genghis Khan's 7-gen chain disconnected from Adam, Heo Hwang-ok → Jimmu not joined. None of this blocks chapter writing, but the analysis is the handle for per-chapter genealogy callouts.

6. **GitHub Actions Node 20 deprecation.** Runners force Node 24 by default on 2026-06-02; Node 20 removed entirely 2026-09-16. Bump action tags in `.github/workflows/*.yml` when they officially support Node 24, or set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` as interim. Not urgent but has a hard deadline.

## Pinned corrections (I keep dropping these)

1. **Do not run `python build.py` before committing.** GitHub Actions handles deploy on push to master. Running it locally wastes time and creates `site_tmp` lock issues on Windows.
2. **English is served at the site root, not `/en/`.** `/faq/`, `/calendar/`, `/` are all English. Other languages use `/{lang}/`. Don't write URL logic that assumes `/en/` exists.
3. **Use `C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe`.** The default `python` can resolve to `ambie`'s install, which has no packages. The `Immanuelle` install is the one with everything.
4. **Discord bot timing is not time-critical.** GitHub Actions cron is unreliable by design; the state file in `discord-bot/state.json` handles dedup. Do not over-engineer for exact-time posting, DST edge cases, or sub-minute precision.
5. **Do not propose numbered chapter lists.** Emma has explicitly rejected this ("trying to make a list of the chapters is the absolute worst thing that can be done"). The `planning/gaiad-*.md` docs are *unnumbered* chronologies plus tone guidance; chapters emerge when the writer sits down.
6. **Three registers braid, not sequence.** Haplogroup/migration (A), mythic antiquity (B), and proper historiography (C) all continue through the block. A does not "close" at the Bronze Age Collapse — Hitler, Napoleon, Perry Y, Japanese D all still belong in register A.
7. **Modern placenames for classical geography.** The Gaiad says Antalya, not Lycia. Grounds ancient events in recognizable geography for modern readers.
8. **Every chapter ends with "Stand."** Single word, period, nothing after. Every chapter uses `{{c|Name}}` for characters and `{{p|Place}}` for places.
9. **Barrel-through mode ≠ notes.** Power-through chapters are still real chapters — poetic verse, ~60–150 lines, proper templating, Stand. Ending. A later editing pass is expected, which is what licenses the speed, not lower quality bars.

## Pointers

- Build config, URL structure, calendar spec: `CLAUDE.md`.
- Long-tail roadmap (iCal spec, calendar-lib, Node 24): `todo.md`.
- 130–220 architecture: `planning/gaiad-130-220-structure.md`.
- Tone principle + per-religion founder treatments: `planning/gaiad-tone-and-founders.md`.
- Draft chapters: `Gaiad/epic/chapter_NNN.md`.
- Discord bot: `discord-bot/bot.py` + `state.json`.
- Wiki dump: `wikibase/items/`, `wikibase/pages/`, `wikibase/images/`. Closure context: `memory/wiki_closure_status.md`.
- Chat workflow: `chats/README.md` + `scripts/extract_chat.py`.
