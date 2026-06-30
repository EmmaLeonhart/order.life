# order.life — Autonomous Work Queue

Worked top-to-bottom by the autonomous work-loop cron (`:00`/`:30`). Each item is
bounded, verifiable, and unblocked. **Delete an item from this file in the same
commit that completes it** (delete-don't-check). Source backlog: `todo.md`.

**Hard rails:** never fake; never weaken/skip a test to pass; never claim
"works"/"verified" without running it; document real blockers, don't paper over
them. **Chapter gate:** do NOT generate new Gaiad chapters before Leo (2026-08-12).

---

## ACTIVE (do in order)

_All currently-actionable quick items are done (iCal Phase 2, Node 24 bump). The
calendar-bot month-page verification turned out moot — the wiki is closed (below).
Remaining work is DEFERRED, BLOCKED-on-Emma, or GATED until Leo._

---

## DEFERRED — do NOT interleave with the live work-loop

- **Wikibase backfill** (`wiki-scripts/wikibase_fill_missing.py`, ~60K items, ~7h)
  — read-only against the wiki (safe), but with `--commit-every` it runs `git add
  … && git push origin master` *directly, without pull-rebase*. Running it for 7h
  alongside the three work-loop crons causes git index-lock contention and push
  races. Its only downstream consumer (genealogy for ch 130–220) is gated until
  Leo (2026-08-12) anyway. **Run as a dedicated job with the crons paused**, or with
  `--commit-every 0` and let auto-flush handle commits. Not urgent.

## BLOCKED / NEEDS EMMA (do NOT execute autonomously — surface, don't guess)

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
