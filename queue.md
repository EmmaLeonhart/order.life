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

1. **Unmerge/dedupe the long Iberian chains — do NOT cut them.** Seven of the eight cycles
   of length >= 20 run through one twelve-edge stretch of the Portuguese de Aguiar family
   ending at Heracles. `Barbara, imperatriz of Rome` / `Bárbara, Princess of Rome` is an
   accented duplicate pair and `Diogo Afonso **Afonso** de Aguiar` is a doubled name — both
   unmerge signatures. The join to Heracles is why the chain exists and must survive.

2. **Fold the Wikidata cross-check into the cycle proposals.** `qa_cycles_proposed.tsv` was
   built before `qa_cycles_vs_wikidata.tsv` and never saw it. 7 of its 25 "unresolved"
   cycles contain an edge Wikidata explicitly contradicts. Most cycle records have working
   Wikidata ids, which is what makes unmerging tractable — use them.

3. **Work the remaining cycles under the repair order above.** Unmerge candidates first.

4. **Regenerate `qa_cycles.tsv` / `qa_cycles_proposed.tsv`.** Found 2026-07-30 while
   verifying the Tros unmerge: only **63 of the 71 recorded chains still exist** in the
   current dump — earlier repairs (`9c0299d8`, "repair 8 mutual pairs") already broke eight
   of them. The proposals file is stale by eight rows and the cycle count is overstated.
   Re-run the detector before anyone counts cycles again.

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
