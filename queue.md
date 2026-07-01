# order.life — Autonomous Work Queue

Worked top-to-bottom by the autonomous work-loop cron (`:00`/`:30`). Each item is
bounded, verifiable, and unblocked. **Delete an item from this file in the same
commit that completes it** (delete-don't-check). Source backlog: `todo.md`.

**Hard rails:** never fake; never weaken/skip a test to pass; never claim
"works"/"verified" without running it; document real blockers, don't paper over
them. **Chapter gate:** do NOT generate new Gaiad chapters before Leo (2026-08-12).

---

## ACTIVE (do in order)

_All currently-actionable quick items are done. The wiki is permanently gone (Miraheze
took it down as off-topic, 2026-07-01) — the Wikibase backfill is complete/frozen and
the site has been de-linked from the wiki entirely (see devlog 2026-07-01). Remaining
work is BLOCKED-on-Emma or GATED until Leo._

---

## DEFERRED — do NOT interleave with the live work-loop

_(none — the Wikibase backfill is DONE; wiki gone, snapshot frozen + committed, 164,536
items in repo. See devlog 2026-07-01. The `fill_missing`/`dump` scripts need a live wiki
and can no longer run; all downstream analysis reads the local dump.)_

## BLOCKED / NEEDS EMMA (do NOT execute autonomously — surface, don't guess)

- **Genealogy lineage bridges** (Kosala→Heo Hwang-ok, Genghis→Adam, Heo→Jimmu) —
  these invent connecting kings = creative scripture content; needs Emma's call,
  and is adjacent to the chapter gate. (Source is now the LOCAL dump, not the wiki.)
- **Genealogy QA — analysis DONE, fixing needs review.** Ran 2026-07-01 on the local
  dump: full error lists enumerated in `wikibase/analysis/qa_multiparent.tsv` (1,230
  children with >2 parents) + `qa_cycles.tsv` (~70 impossible ancestor cycles), summary
  in `wikibase/analysis/GENEALOGY_QA.md`. NOT auto-fixed: picking the true parents /
  which cycle-edge to cut is per-record genealogical judgement (auto-guessing =
  fabricating scripture). Fixes are local-dump edits (wiki is gone). Surface for Emma.

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`0,30 * * * *`),
  auto-flush (`15,45 * * * *`), status-report (`50 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
