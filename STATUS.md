# order.life — Work Queue

**This file is a queue, not a state snapshot.** When an item is done, delete it. Finished work lives in `git log` and `planning/`.

The work here is **making the Gaiad ship as a daily stream and the order.life site stand on its own** — 364 chapters of real scripture, calendar tooling that subscribers can trust, and a body of content that survives the wiki going dark. The question each queue item answers is: *what does it take to make this thing a real, finished artifact?*

## Chapter runway (load-bearing metric)

Written: **349 / 364**. Remaining gaps: none.

**The Leo gate is LIFTED — Emma, 2026-08-05, a week early. Chapter writing is open.** It had held since roughly 2026-07: the 130–220 barrel-through was an emergency stopgap to keep the daily stream from starving, and once the stream was comfortable for months the gate stopped further barrelling. That was a pacing judgement, and Emma has called it done. What survives is only "don't barrel" — chapters emerge at the writing desk, not from a numbered list made in advance.

## Queued work

- **Fix the early human-era chapters first.** The 130–205 block was power-through quality — real chapters but first-pass. Emma has said to prioritize fixing earlier chapters because they ship through the Discord stream first. Start at 130 and work forward; don't wait on a full editing pass. The register should match the register set by 1–129 (verse, not declarative).

- **Genealogical analysis follow-up.** The Wikibase dump completed 2026-04-16 — 164k items, 4,840 wiki pages, 377 images. Centrality passed (Charlemagne, Bustanai, Jesus, Muhammad all load-bearing). Open: 1,230 children-with->2-parents (Geni merge errors, mostly Iberian royals), 69 cycles that should be zero, fan-out suspects (Danaus 231, Oceanus 155, Dhritarashtra 131, Heracles 113). Lineage gaps: Kosala → Heo Hwang-ok (~15–20 invented kings), Genghis Khan's 7-gen chain disconnected from Adam, Heo Hwang-ok → Jimmu not joined. None of this blocks chapter writing, but the analysis is the handle for per-chapter genealogy callouts.

## Pinned corrections (I keep dropping these)

1. **Do not run `python build.py` before committing.** GitHub Actions handles deploy on push to master. Running it locally wastes time and creates `site_tmp` lock issues on Windows.
2. **English is served at the site root, not `/en/`.** `/faq/`, `/calendar/`, `/` are all English. Other languages use `/{lang}/`. Don't write URL logic that assumes `/en/` exists.
3. **Use `C:\Users\Immanuelle\AppData\Local\Programs\Python\Python313\python.exe`.** The default `python` can resolve to `ambie`'s install, which has no packages. The `Immanuelle` install is the one with everything.
4. **Discord bot timing is not time-critical.** GitHub Actions cron is unreliable by design; the state file in `discord-bot/state.json` handles dedup. Do not over-engineer for exact-time posting, DST edge cases, or sub-minute precision.
5. **Do not propose numbered chapter lists.** Emma has explicitly rejected this ("trying to make a list of the chapters is the absolute worst thing that can be done"). The `planning/gaiad-*.md` docs are *unnumbered* chronologies plus tone guidance; chapters emerge when the writer sits down.
   *Note, 2026-10-12:* `planning/gaiad-253-364/day-themes-draft.md` is a complete day-by-day list for
   Virgo to Ophiuchus, made at Emma's own request that night ("it does kind of have to be complete",
   so it is "citable") and approved by her. It is a theme for each day, not a chapter outline; the
   rule above still stands for everything else.
6. **Three registers braid, not sequence.** Haplogroup/migration (A), mythic antiquity (B), and proper historiography (C) all continue through the block. A does not "close" at the Bronze Age Collapse — Hitler, Napoleon, Perry Y, Japanese D all still belong in register A.
7. **Modern placenames for classical geography.** The Gaiad says Antalya, not Lycia. Grounds ancient events in recognizable geography for modern readers.
8. **No set closing word.** *(Tags: `{{c|}}`, `{{p|}}` and `{{x|}}` are data for later programs (the CI/CD and local tools that build the Gaiad's database of people and places, a Loka database, with each person's GEDCOM data, chapters and quotes); Emma, 2026-10-14: "The tagging was not supposed to be fucking changed whatsoever." Never change existing tags, by script or by hand; a wrong tag is not a problem to fix.)* *(2026-10-14 16:58: the old rule that every chapter ends with "Stand." is withdrawn on Emma's word, "I just want you to remove it from all of them". A Claude agent invented it on 2026-04-18 as a refrain for the haplogroup chapters and another agent made it a rule the same day; she never chose it. See `research/stand-origin.md` in the parent repo. It was removed from all chapters the same day.)*
9. **Barrel-through mode ≠ notes.** Power-through chapters are still real chapters — poetic verse. A later editing pass is expected, which is what licenses the speed, not lower quality bars.
10. **No length guideline (Emma, 2026-10-14).** "There's no upper bound for the lengths of chapters"; "There is no guideline whatsoever about chapter length like that." Chapters "can very regularly get well beyond 150 lines" and "probably should be". The old ~60-150 lines (from 2026-04-18) is withdrawn everywhere.
11. **Rhyme is graded (Emma, 2026-10-14).** "Rhyming is something that you are supposed to be actively grading and monitoring, because rhyming is actually an important part of it." Every review grades each chapter's rhyme.

## Pointers

- Build config, URL structure, calendar spec: `CLAUDE.md`.
- Long-tail roadmap (iCal spec, calendar-lib, Node 24): `todo.md`.
- 130–220 architecture: `planning/gaiad-130-220-structure.md`.
- Tone principle + per-religion founder treatments: `planning/gaiad-tone-and-founders.md`.
- Draft chapters: `Gaiad/epic/chapter_NNN.md`.
- Discord bot: `discord-bot/bot.py` + `state.json`.
- Wiki dump: `wikibase/items/`, `wikibase/pages/`, `wikibase/images/`. Closure context: `memory/wiki_closure_status.md`.
- Chat workflow: `chats/README.md` + `scripts/extract_chat.py`.
