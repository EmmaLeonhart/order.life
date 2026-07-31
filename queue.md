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

**SHADOW FILES — always propagate an edit.** 39,527 qids are claimed by more than one
file. `extract_genealogy.py` keeps only the numerically-lowest QID per qid, so editing the
canonical file alone leaves stale shadows that silently revert the fix if that file is ever
vacated. After editing any record, rewrite every file claiming its qid. `shadow_audit.py`
reports disagreements; it must stay at **0**.

**MERGE DIRECTION — after a merge, NO file may still claim the loser's qid.** Vacating a
qid some file still claims lets that file win it and inject its claims; that is what
produced the phantom Cato 2-cycle out of a graph that never contained the edge. Worked
example: `wikibase/analysis/cato_cluster_resolved.md`.
This was first written as "always merge INTO the side that has shadows", which is a proxy
for the real invariant and a bad one: it forbade `Q72434`/`Q72514`, where **both** sides
have shadows, even though repointing makes either direction safe. `merge_cluster.py` now
rewrites every shadow of both sides and then **sweeps all 164k files** asserting nothing
still resolves to a vacated qid. Prefer the lower QID as survivor by convention, not
because the higher one is unsafe.

**A MERGE MUST CARRY THE WHOLE RECORD, not just the genealogy.** The loser's file becomes a
copy of the survivor, so any property only the loser held is gone from the dump. The first
ten merges of 2026-07-31 unioned only `P20/P42/P47/P48/P61` and silently dropped **38
properties** — external ids and, worse, `P56`/`P57` birth and death dates on six people.
They were reported as "strictly additive"; that was true of the graph and not of the
records. Restored by `wiki-scripts/backfill_merged_properties.py`; `merge_cluster.py` now
carries every property the survivor lacks and reports, rather than guesses at, the ones
where both sides differ.

**COUNT TANGLES, NOT CYCLES.** `dump_qa_errors.py` used to iterate `set`s of qid strings,
so Python's per-process hash randomisation changed which cycles its DFS found on every run
— three runs over one unchanged `edges.tsv` gave 45, 50 and 46. It also marked nodes BLACK
on pop, so it only ever found *some* cycles per tangle. **Every "cycles went from X to Y"
number in this file, `devlog.md`, `HANDOFF.md` and `GENEALOGY_QA.md` predating 2026-07-31
is unsound, including the `52 -> 54`.** Fixed 2026-07-31: it now emits one canonical
shortest cycle per strongly connected component, deterministically (five runs byte-identical),
and its totals match `check_invariants.py`'s independent Tarjan. The well-defined quantity is
the **tangle** (an SCC of size > 1) — **34** of them, holding **278** records. Verify repairs against
`tangled_components` / `records_in_a_cycle`, never against a cycle count.

**HOW TO VERIFY A REPAIR.** Snapshot `edges.tsv` first, make the change, regenerate, then
`python wiki-scripts/compare_tangles.py <snapshot>`. It compares SCC *partitions* — what was
introduced, removed, or reshaped, and which records entered or left a tangle — so a repair
that keeps the counts equal while moving records between tangles still shows up. Exits
non-zero if anything was introduced. Merges go through `wiki-scripts/merge_cluster.py
<cluster>`, which enforces both merge rules above and verifies them against what actually
happened on disk, not against the inputs.

**I2 WAS VACUOUS AND IS NOT ANY MORE.** `check_invariants.py` said "self-loops must be
zero, always" and reported 0 unconditionally: its default `--source tsv` reads `edges.tsv`,
and `extract_genealogy.py` drops self-edges before writing it, so the check was
unsatisfiable. Meanwhile 11 records listed themselves as their own parent or child. Fixed
2026-07-31 — the extractor now records what it drops in `qa_self_edges.tsv` and I2 reads
that. All 11 were cut (`cut_edges.py selfloops`, data-driven from that file) and it is
genuinely 0 now. **A gate that cannot fail is worse than no gate**: check any invariant
reporting a perfect score against the source it actually reads.

**WIKIDATA IS THE REFERENCE, NOT GOSPEL.** `qa_cycles_vs_wikidata.tsv` returns
`contradicted` for 16 distinct edges, but in 15 of them the detail reads *"Wikidata records
no link between them"* — an **absence of evidence, not a refutation**, and Wikidata is
incomplete and holds impossible loops of its own. Three of those edges are currently live
and **correct**: `Belus -> Danaus` and `Anchiroe -> Danaus` are exactly the parents
`cycle_policy.md` assigns, and cutting them would sever the cross-tradition join the
genealogy exists to make. They are listed in `PROTECTED` in
`wiki-scripts/propose_tangle_repairs.py` and that tool will never propose cutting them.
Only *"the link the other way round"* — Wikidata recording the same pair with parent and
child swapped — is treated as decisive.

1. **Find the real defect in the Scipio loop — WITHOUT detaching the Scipiones from
   Aster.** The `Q73893 → Q73794` cut was applied and then **reverted the same day**: it
   was chronologically correct but it was the *sole upward gateway* for the whole Scipio
   line. Measured: `Q73299` Scipio Africanus went from **267 ancestors deep to 4**,
   `Q73794` from **263 to 0**, and the severed chain ran all the way to **`Q1` Aster**.
   `cycle_policy.md` names this case exactly — go find the defect elsewhere in the loop.
   The loop is
   `Q73794 → Q73692 → Q73569 → Q73443 → Q73293 → Q73128 → Q72957 → Q72801 → Q72786 →
   Q72615 → Q72434 → Q73893 → Q73794`.
   The likely culprit is the *downward* half, not the Scipio half: `Q72801` Cornelia
   (wd Q100804879) has **three fathers** — `Q72957`, `Q73425`, `Q73017` — and it is her
   `Q72957` edge that drags the Scipiones back down into the Aemilii. Check whether
   Cornelia is a merge of two women, or whether `Q72957 → Q72801` is simply wrong. Also
   suspect `Q72786`, which had four fathers and three mothers.
   **Do not cut anything here until you have measured ancestral depth before and after.**

2. **`compare_tangles.py` measures width, not depth — add a depth check.** It reported
   "18 records freed, 0 tangles introduced" for a repair that amputated 263 generations
   from a major line, because nothing in the gate set measures ancestry upward.
   `qa_cycles_load.tsv` has the same flaw and the rails already say so. Add a tool that,
   given a before/after `edges.tsv` pair, reports **which records lost ancestral depth and
   how much**, and wire it into the verification ritual next to `compare_tangles.py`. Any
   record dropping more than a few levels should fail loudly. This is the gate that would
   have caught the Scipio cut before it was committed.

3. **Merge `Q72615` / `Q72693`, both "Quintus Aemilius Lepidus".** Both are children of
   `Q72786` and both are recorded as fathers of the merged `Q72434` — one man cannot have
   two fathers who are the same person. `Q72693` carries `wd Q11944252`; `Q72615` carries
   none, which is a gap and not a conflict. **`propose_tangle_repairs.py` will not surface
   this**, because its DEDUPE detector keys on a *shared* Wikidata id and here only one
   side has one. Worth teaching it the identical-label-plus-shared-parent signal too.
   Note `Q72693` itself has two fathers (`Q72786`, `Q144279` wd Q3625112) — settle that
   before or during, don't union it blind.

2. **Work the remaining cycles under the repair order above.** Start from
   `wikibase/analysis/qa_tangle_repairs.md`, which is generated and ranks all 35 tangles.
   34 are `REVIEW`: no Wikidata evidence decides them, mostly because "contradicted" there
   means *Wikidata records no link*, which is an absence and not a refutation. Unmerge
   candidates first.
   The five remaining cycles of length >= 20 are all Roman, sharing the Q61957/Q62255/
   Q63192/Q63747/Q70152/Q138467 stretch — likely the same repeating-cognomen collision that
   produced the short Roman 2-cycles. Emma: preserve the Roman material; unmerge, do not
   delete.

3. **Fix the one-sided edges.** `wikibase/analysis/edge_symmetry.txt`: 96.3% of
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
