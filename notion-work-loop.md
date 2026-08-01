> Live board for the autonomous work loop on order.life. Replaces the wall-of-text status reports in chat. Updated by the loop each tick.
=== ⚠️ Needs your eye first ===
**A load-bearing gateway was cut and then reverted, same day.**
I cut Q73893 → Q73794 because it is chronologically impossible — Scipio Asiaticus Aemilianus (cos. 83 BC) recorded as ancestor of Scipio Barbatus (cos. **298 BC**). It broke an 18-record Roman tangle and every gate went green.
It was also the **sole upward gateway for the entire Scipio line**:
| record | ancestors deep before | after |
|---|---|---|
| Q73794 Gnaeus Cornelius Scipio | 263 | 0 |
| Q73692 Scipio Barbatus | 264 | 1 |
| Q73299 Scipio Africanus | 267 | 4 |
| Q72957 Nasica Serapio | 269 | 12 |
The severed chain ran all the way to **Q1 Aster**. Reverted. cycle_policy.md names this case exactly: the real defect is elsewhere in the loop.
**The methodological hole:** I verified with compare_tangles.py, which measures **width** — how many records sit in a tangle. Load-bearing here means **depth, upward**, and nothing in the gate set measures it. A repair can pass every check and still amputate 263 generations. Building that gate is now queue item 2.
=== Where the cycles actually stand ===
No, they are not all gone.
|  | start of session | now |
|---|---|---|
| tangles (SCCs, size > 1) | 36 | 35 |
| records trapped in one | 299 | 296 |
| largest tangle | 72 | 72 |
One tangle genuinely resolved (a mutual-parenthood pair Wikidata settled). The 18-record Roman one is back, pending the right fix.
=== Queue — top 3 ===
1. **Find the real defect in the Scipio loop**, without detaching the Scipiones from Aster. Prime suspect is the *downward* half: Q72801 Cornelia has **three fathers**, and her Q72957 edge is what drags the Scipiones back into the Aemilii.
1. **Add a depth gate.** Report which records lose ancestral depth on any repair, and fail loudly past a few levels.
1. Merge Q72615 / Q72693, both "Quintus Aemilius Lepidus", both fathers of the same man.
=== Done this session, and holding ===
- **11 duplicate records absorbed** across three parallel-import clusters — Porcii Catones (7 pairs), Porcia/Atilia/Atilius (3), Aemilii Lepidi (1). All decided by shared Wikidata ids or by a record that already listed both duplicates as spouses. Merges only ever *add* ancestry.
- **Q73167 relabelled** "Marcus Porcius Censorius" → "Marcus Porcius Cato Licinianus". His mother is Licinia, Cato's wife, so he is Cato's son — the old label was the father's cognomen and is what made him look like a third Cato. Old name kept as an alias.
- **11 records that were their own parent** — cleared. Includes Terra, Erebos and Nyx. Zero risk: a self-edge links a node to itself, so it can never be a cross-tradition join, and the graph provably could not change. It didn't.
=== Three things I got wrong ===
1. **The Scipio cut above.** Locally correct, globally destructive, and I did not measure the cost.
1. **"Strictly additive" was false.** The merge tools carried only the five genealogical properties, so **38 properties were dropped** — external ids and **birth/death dates on six people**. Restored from git.
1. **The cycle counter was non-deterministic.** Three runs over one unchanged file gave 45, 50, 46. Rewritten around strongly connected components. **Every "cycles went X → Y" figure in devlog.md, queue.md, HANDOFF.md and GENEALOGY_QA.md predating 2026-07-31 is unsound**, including the 52 → 54.
=== Waiting on you ===
None of these block the loop — it works around them.
- **Genesis 11 patriarchs under Mesopotamian royal names** — corrupt import (relabel all nine) or deliberate euhemerism (change nothing, add a note)? Opposite fixes; everything under the Table of Nations depends on it.
  - Euhemerism lol
- **Adam → Genghis** — A1 (attach Khaidu to the Borjigin chain already in the dump) or A2 (Haplogroup C2-M217), or both.
  - Both?
- **Chapter 181's "bore him ten sons"** — data fix invents nine named sons, prose fix drops a Garakguk-gi detail.
  - Uhh yeah the ten sons exist
- **Which of the three Adnan records survives** (M3).
  - You merge them lol
- **Naming the primordial half of Q74698 Tros** — the split is blocked on it, and Tros → Ops can be neither fixed nor cut until it has a name.
  - What? Explain better

- Notion-side test edit — verifying an edit made IN Notion reaches the repo. Removed immediately after.