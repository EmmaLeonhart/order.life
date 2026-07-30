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

**Standing rule for all four items:** do NOT modify `wikibase/items/*.json` or the
`wikibase/analysis/*.tsv` source extracts. Each item's output is a NEW review file that
records, per record, the proposed change AND the evidence for it. Emma approves, and a
later item applies the approved set. Where the evidence does not decide the case, say
so in the row rather than picking — an unresolved row is a correct outcome, a guessed
one is not.

1. **Propose fixes for the ~70 ancestry cycles.** Input `wikibase/analysis/qa_cycles.tsv`.
   For each cycle, name the ONE edge to cut and why — birth-date contradiction, a
   duplicate-QID pair (the 2-node cycles like `Guerau V de Cabrera → Ponc II Giraldo →
   Guerau V` are merge artifacts, not lineage puzzles), or weakest sourcing. Output
   `wikibase/analysis/qa_cycles_proposed.tsv` with columns
   `cycle_len, chain_qids, cut_parent, cut_child, reason, confidence`. Start here: the
   set is small and every row is unambiguously wrong today.

2. **Propose fixes for the 1,230 children with >2 parents.** Input
   `wikibase/analysis/qa_multiparent.tsv`. The cause named in `GENEALOGY_QA.md` is Geni
   merge duplication, so the method is: cluster the parent QIDs by label similarity and
   treat near-identical labels as one person. If a record collapses to ≤2 distinct
   people, propose keeping one representative per cluster. If it does not collapse,
   emit the row as unresolved with the clusters shown — do NOT rank-and-truncate to two.
   Output `wikibase/analysis/qa_multiparent_proposed.tsv` with columns
   `child_qid, child_label, n_parents, clusters, proposed_parents, unresolved, reason`.
   Report the collapse rate in `devlog.md`.

3. **Characterize Q73380 `BAD MERGE` — describe it, do not fix it yet.** It carries
   29,466 descendants on the main backbone, so it gets understood before it gets
   touched. Known as of 2026-07-30: its 4 parents split into two unrelated families
   (Gorgophone + Oebalus, Spartan myth; Antiochus III the Great + Laodice III,
   Seleucid), and its 20 children split the same way (Penelope, Thoas, Alyzeus,
   Leucadius, Aletes vs Antiochus V, Alexandros Balas), with co-parents agreeing
   (Periboea/Asterodeia/Polycaste vs Laodice IV). Working hypothesis: Icarius of Sparta
   merged with a Seleucid king. Write `wikibase/analysis/Q73380_context.md` — the full
   parent/child/co-parent split, which descendants route through which side, whether
   anything downstream depends on the two sides being joined, and a proposed two-node
   split. Emma decides whether to execute it.

4. **Draft the three lineage bridges as proposals only.** Verified 2026-07-30 against
   the local dump: none of them exist. Genghis Khan (Q37401) has no descent path from
   Adam (Q152973); Jimmu (Q6432) has no path to or from Heo Hwang-ok (Q51928) — his
   line runs back through Ugayafukiaezu → Toyotama-hime → Xu Fu into the Xú clan; and
   none of the 44 Kosala kings connect to Heo. **Heo Hwang-ok has zero parents recorded
   and one child**, so the Kosala bridge is a single missing parent edge. Draft
   candidate bridges into `planning/lineage_bridges_proposed.md` — the attachment point,
   the connecting figures, and the legendary basis for each. Write NOTHING into the dump
   or the Gaiad. This is proposal-drafting, not chapter generation, so the Leo gate does
   not cover it; if a bridge cannot be drafted without writing new scripture prose, stop
   and say so.

5. **Reconcile shipped Gaiad genealogy claims against the dump.** Found 2026-07-30.
   The Heo Hwang-ok chapter (`gaiad_full.md` ~line 39614) is written and live, and it
   asserts what the data does not contain: princess of **Ayodhya** (the capital of
   Kosala — i.e. the missing Kosala bridge, stated as fact in verse), "bore him ten
   sons" (dump: one child, Geodeung of Geumgwan Gaya), Kimhae Heo + Kimhae Kim both
   descending from her, "millions of modern Koreans" (dump: 46 descendants). This
   happened because STATUS.md item 7 recorded the three lineage gaps and declared
   "None of this blocks chapter writing" — the prose then shipped making claims the
   graph was supposed to back. Sweep the epic for every genealogical assertion of this
   kind and check each against `wikibase/analysis/`. Output
   `wikibase/analysis/epic_vs_dump.md`: the claim, the chapter location, what the dump
   holds, and whether the gap is a data gap (fix the dump) or a prose error (fix the
   chapter). Propose only — do NOT edit chapter text or the dump. Chapter *editing* is
   allowed outside the Leo gate, but this item stops at the report so Emma decides
   which side moves.

---

## DEFERRED — do NOT interleave with the live work-loop

_(none — the Wikibase backfill is DONE; wiki gone, snapshot frozen + committed, 164,536
items in repo. See devlog 2026-07-01. The `fill_missing`/`dump` scripts need a live wiki
and can no longer run; all downstream analysis reads the local dump.)_

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`0,30 * * * *`),
  auto-flush (`15,45 * * * *`), status-report (`50 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
