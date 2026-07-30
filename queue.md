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

1. **Trace the `Banu Adnan` chain and the `'Udd`/`Humaisi` tangle.** Found 2026-07-30
   (`wikibase/analysis/adnan_merge_proposed.md`, "Not covered"). Two loose ends the merge
   proposal read but did not trace. (a) The `Banu Adnan` chain, Q86403–Q86431, twelve
   records from `Ithobaal` down to `Imran`, sits between the Emesene priest-kings and
   `Adnan Banu Ismail` — and **`Ithobaal` is a Tyrian royal name, not an Arab one**, which
   looks like the same splice defect as the Emesene one, a second time. (b) The ancestry
   above `'Adnaan Bin Imaam 'Udd` (Q65555), which runs into `'Udd`/`Humaisi`/`N.N.`
   placeholders and terminates without reaching anything. Walk both, and extend
   `adnan_merge_proposed.md` with a section per chain: what each record is, where the
   names come from, and whether the chain is a genuine tradition, a splice, or filler.
   Propose only. If (a) turns out to be a Tyrian splice, say what it would attach to
   rather than proposing the cut — the cut is Emma's, and it is entangled with R1.

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
