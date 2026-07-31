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

**Propose-only is LIFTED (Emma, 2026-07-30).** Apply fixes directly to
`wikibase/items/*.json`. Do not stop at writing another review document — that was the
old rule and it was followed well past the point where Emma had asked for the actual
change. Still true: where the evidence does not decide a case, say so rather than
guessing, and **verify against the item files after applying** — the derived
`wikibase/analysis/*.tsv` extracts go stale the moment items change.

**An edge lives in TWO places** — the child's `P47`/`P48` *and* the parent's `P20`.
Removing only one direction leaves the edge alive. This bit the Tros unmerge; always
re-verify from the items.

**READ `wikibase/analysis/cycle_policy.md` BEFORE TOUCHING ANY CYCLE.**

**This is not a regular genealogy project.** It is a literary device that links people
across time and space, and it is building a **synoptic mythology** — Greek, Near Eastern,
Egyptian, Trojan, Chinese, Mongol lines integrated into one descent. The cross-tradition
joins are the product, not incidental structure.

**Everything unexpected here that is not an error was imported deliberately by Emma.** The
Emesene route in Muhammad's ancestry, the Genesis 11 patriarchs under Mesopotamian royal
names, the Mongol line descending from the Buddha. Surprising is not evidence of broken.
Do not open general-defect sweeps.

**"Load-bearing" means the ancestors that come through it — depth, upward.** NOT descendant
count. `qa_cycles_load.tsv` scores cycles by descendants lost, which is *width*, which is
the wrong metric and must not be used to rank repairs.

**Repair order, strictly — always prefer the fix that preserves the most connection:**
1. **UNMERGE** an improperly merged record. Both lines survive. This is the default.
2. **DEDUPE** parallel imports. Removes cycles with no edge chosen.
3. **CUT** only if 1 and 2 do not apply, and **never** an edge that is the only link
   between two traditions.
4. **DELETE** only where the loop is genuinely terminal — nothing substantial above it.
   Keep the entry point, drop the rest.

1. **Resolve the Cato the Elder three-record cluster.** Q148133 and Q73005 both carry
   `wd Q180081` (Cato the Elder) and Q73167 is `Marcus Porcius Censorius` — Censorius is
   Cato's own cognomen. Merging Q73005 into Q148133 created the 2-cycle
   `Q148133 <-> Q73167`, because Q73005 had Q73167 as a CHILD while Q73167 had Q148133 as
   a child. The merge is reverted and guarded (`DO_NOT_MERGE` in `apply_dup_merge.py`).
   If the three are one man, merge all three; if Q73167 is Cato's father or his son
   Licinianus, one of the two edges is simply wrong. Decide which, then apply.

2. **Reproduce the Cato 2-cycle before trusting any merge precondition.** Merging Q73005
   into Q148133 produced `Q148133 <-> Q73167`. The devlog previously stated the mechanism
   was "Q73005 had Q73167 as a child while Q73167 had Q148133 as a child" — **that is
   wrong**: in the current extract Q73167 has NO children and Q148133 has NO parents. An
   ancestor/descendant precondition built on that story returned False for the very case it
   was written for, so it was removed rather than shipped as false confidence. Reproduce the
   merge on a scratch copy, regenerate, and find the actual edge that closes the loop —
   likely something about how `save(b, load(a))` interacts with redirect canonicalisation.
   Only then write the precondition. Until then, `check_invariants.py` is the gate.

3. **Unmerge/dedupe the long Iberian chains — do NOT cut them.** Seven of the eight cycles
   of length >= 20 run through one twelve-edge stretch of the Portuguese de Aguiar family
   ending at Heracles. `Barbara, imperatriz of Rome` / `Bárbara, Princess of Rome` is an
   accented duplicate pair and `Diogo Afonso **Afonso** de Aguiar` is a doubled name — both
   unmerge signatures. The join to Heracles is why the chain exists and must survive.

4. **Fold the Wikidata cross-check into the cycle proposals.** `qa_cycles_proposed.tsv` was
   built before `qa_cycles_vs_wikidata.tsv` and never saw it. 7 of its 25 "unresolved"
   cycles contain an edge Wikidata explicitly contradicts. Most cycle records have working
   Wikidata ids, which is what makes unmerging tractable — use them.

5. **Work the remaining cycles under the repair order above.** Unmerge candidates first.

6. **Fix the one-sided edges.** `wikibase/analysis/edge_symmetry.txt`: 96.3% of
   edges are declared on both sides (parent `P20` and child `P47`/`P48`), but 2,325 are
   parent-side only and 2,398 child-side only. `edges.tsv` is built from the union, so a
   half-declared edge still reads as real and any one-sided repair silently fails — this is
   what made the Tros fix look done when two cycles were still closed. Concentrated in the
   fan-out records: Oceanus Q90309 has 142, Danaus Q74973 has 82, Q66360 has 46. Decide per
   record whether the missing side should be added or the present side removed; do NOT
   blanket-add, since some one-sided edges are probably deletions that only got half done.

---

## AWAITING EMMA — reports written, decisions open

**Read the scope note above first.** These reports were written as defect reports before
Emma set the cycles-only scope and said much of what looks wrong is intentional. Treat
their "DATA ERROR" verdicts as *unconfirmed* until she rules on each — R1 was ruled
intentional and that invalidated eight of that report's twelve proposed merges. **Do not
apply anything from these; do not extend them.**

**DECIDED 2026-07-30 — R1: the Emesene route in Muhammad's ancestry is 100% intentional.**
The splice stays. `adnan_merge_proposed.md` is updated; M5–M12 and the "Banu Adnan is
filler" verdict are withdrawn.

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
