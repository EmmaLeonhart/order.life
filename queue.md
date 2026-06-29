# order.life — Autonomous Work Queue

Worked top-to-bottom by the autonomous work-loop cron (`:00`/`:30`). Each item is
bounded, verifiable, and unblocked. **Delete an item from this file in the same
commit that completes it** (delete-don't-check). Source backlog: `todo.md`.

**Hard rails:** never fake; never weaken/skip a test to pass; never claim
"works"/"verified" without running it; document real blockers, don't paper over
them. **Chapter gate:** do NOT generate new Gaiad chapters before Leo (2026-08-12).

---

## ACTIVE (do in order)

### 1. Verify Lifeism month pages weren't clobbered (calendar-lib follow-up)
The first calendar-bot run logged all 14 month pages as `Updated page` (not
`No change`). Read each of the 14 month pages on lifeism.miraheze.org and confirm
the new markup didn't drop pre-existing valuable content.
- **Verify:** read-only diff of current vs. what the bot wrote; report findings.
- If content was clobbered → STOP, document, escalate to Emma (do not auto-revert).

### 2. Kick off Wikibase backfill (long-running, background)
Run `wiki-scripts/wikibase_fill_missing.py` LOCALLY in the background to finish the
~60K-item allpages backfill (items ns 860, properties ns 862), `--commit-every
5000`. ~7h ETA. Then the properties short job (`--type properties`).
- This is a background job, not a blocking step — start it, note the PID/log, let
  it run across ticks; don't busy-wait.
- **After it completes:** genealogy network analysis QA (see todo.md) becomes
  actionable — but the QA *fixes* themselves are in BLOCKED below.

---

## BLOCKED / NEEDS EMMA (do NOT execute autonomously — surface, don't guess)

- **Import `Module:GaiadDate` to lifeism.miraheze.org** — manual `Special:Import`
  of `calendar-lib/GaianCalendar-WikiModule-Export.xml`; needs wiki creds / human.
- **First `dotnet-build.yml` run** — may reveal the `.csproj` targets a non-.NET-8
  framework; bumping it is a decision, not a mechanical fix.
- **Genealogy lineage bridges** (Kosala→Heo Hwang-ok, Genghis→Adam, Heo→Jimmu) —
  these invent connecting kings = creative scripture content; needs Emma's call,
  and is adjacent to the chapter gate.
- **Genealogy QA cleanup** — 69 cycles + 1,230 children with >2 parents (Geni merge
  errors) live on the wiki; fixing them is data surgery needing review.

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`0,30 * * * *`),
  auto-flush (`15,45 * * * *`), status-report (`50 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
