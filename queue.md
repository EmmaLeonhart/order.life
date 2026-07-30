# order.life — Autonomous Work Queue

Worked top-to-bottom by the autonomous work-loop cron (`:00`/`:30`). Each item is
bounded, verifiable, and unblocked. **Delete an item from this file in the same
commit that completes it** (delete-don't-check). Source backlog: `todo.md`.

**Hard rails:** never fake; never weaken/skip a test to pass; never claim
"works"/"verified" without running it; document real blockers, don't paper over
them. **Chapter gate:** do NOT generate new Gaiad chapters before Leo (2026-08-12).

---

## ACTIVE (do in order)

_The genealogy QA work below was previously parked as "BLOCKED / NEEDS EMMA." Emma
unblocked it on 2026-07-30: the blocker was never her availability, it was that nobody
had stated a **policy**. The policy is now **propose, don't apply** — every item here
writes a review file and edits nothing in the dump. That is executable autonomously._

**Standing rule for all these items:** do NOT modify `wikibase/items/*.json` or the
`wikibase/analysis/*.tsv` source extracts. Each item's output is a NEW review file that
records, per record, the proposed change AND the evidence for it. Emma approves, and a
later item applies the approved set. Where the evidence does not decide the case, say
so in the row rather than picking — an unresolved row is a correct outcome, a guessed
one is not.

_(empty — every proposed-review item is done. All five reports are written and
awaiting Emma's decisions; see `## AWAITING EMMA` below. Refill from `todo.md`.)_

---

## AWAITING EMMA — reports written, decisions open

Not blocked work — finished work. Each is a review file with the evidence; the decision
is the deliverable Emma owes back, and the apply pass is a later item.

1. `planning/lineage_bridges_proposed.md` — **Adam→Genghis**: take A1 (attach Khaidu to
   the Borjigin chain already in the dump) or A2 (Haplogroup C2-M217), or both.
   **Jimmu↔Heo**: strike it — it cannot be drafted without inventing scripture — and
   substitute B1 (Prince Junda → Yamato no Ototsugu), or drop it. **Kosala→Heo**: held
   behind the Kosala dedup, then C1.
2. `wikibase/analysis/epic_vs_dump.md` — eight rows in "which side moves". The one that
   needs Emma most: chapter 181's "bore him ten sons", where the data fix means inventing
   nine named sons and the prose fix means dropping a Garakguk-gi detail.
3. `wikibase/analysis/patriarch_overlay.md` — **the biggest open question in the dump.**
   Is the Genesis 11 line under Mesopotamian royal names a corrupt import (relabel all
   nine) or deliberate euhemerism (change nothing, add a note)? The two fixes are
   opposites. Everything under the Table of Nations depends on it.
4. `wikibase/analysis/adnan_merge_proposed.md` — decide **R1** (cut the Emesene splice at
   `Fihr born of Iamblichus`) *before* **M3** (which of the three Adnan records survives).
   The order matters; M3 is not decidable on its own.
5. The Kosala dedup — three parallel imports of one king list — gates both C1 above and
   any further Indian-line work.

---

## DEFERRED — do NOT interleave with the live work-loop

_(none — the Wikibase backfill is DONE; wiki gone, snapshot frozen + committed, 164,536
items in repo. See devlog 2026-07-01. The `fill_missing`/`dump` scripts need a live wiki
and can no longer run; all downstream analysis reads the local dump.)_

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`3 * * * *`),
  auto-flush (`15 * * * *`), status-report (`42 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
  (Schedules corrected 2026-07-30 to match the `autonomous-loop` skill and what is
  actually running; the half-hourly figures this line used to give were never the
  skill's cadence. Crons are session-local — they die with the session, so a fresh
  session always creates them.)
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
