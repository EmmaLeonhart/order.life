# How much of the genealogy is decided by filename order?

**2026-07-30. Read-only audit, produced by `wiki-scripts/shadow_audit.py`.**

`extract_genealogy.py` keeps only the first file it sees per qid, and sorts files
NUMERICALLY by QID, so the winner is the **lowest QID number**. Shadow files carry
genealogical claims the winner does not. Each disagreement is an edge that exists,
or fails to exist, because of a filename.

## Scale

- items read: **164,456**
- distinct qids: **107,028**
- qids claimed by more than one file: **39,522**
- of those, qids where the files DISAGREE on parents/children: **0**
- edges suppressed because the winning file lacks them: **0**
- edges present ONLY because the winner happens to have them: **0**

The suppressed edges are the dangerous ones for merges: vacating a qid lets a
shadow win and injects them, which is exactly how the Cato 2-cycle appeared.

## Worst offenders (most suppressed claims)

| qid | winning file | suppressed claims |
|---|---|---|

## What this means

The graph as it stands is not the union of what the dump asserts -- it is one
arbitrary selection from it. Re-sorting the item directory, or renaming a file,
would silently change the genealogy. Because the sort is numeric, the winner is
simply whichever import happened to land on the smaller QID, which carries no
meaning at all.

**Not resolved here, deliberately.** Deciding whether the winner or a shadow is
right is a per-record judgement, and this dump is a synoptic mythology where
surprising content is usually intentional. Options, for Emma:

1. **Union everything** -- take every claim any file makes. Maximises connection,
   which suits a genealogy built to link traditions, but will add cycles and
   multi-parent records.
2. **Keep winner-takes-all** -- accept the status quo, but make it explicit rather
   than accidental by collapsing shadows into their target.
3. **Union only where it adds no cycle** -- run `check_invariants.py` per batch and
   keep the claims that do not regress it.

Option 1 is the one most in keeping with what the genealogy is for; option 3 is the
one that will not make the cycle backlog worse. They can be combined by unioning
first and treating the resulting cycles as ordinary repair work.
