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
|  | 2026-07-31 | start of 2026-08-01 | now |
|---|---|---|---|
| tangles (SCCs, size > 1) | 36 | 34 | **30** |
| records trapped in one | 299 | 283 | **274** |
| largest tangle | 72 | 71 | 71 |
**Four tangles removed on 2026-08-01 by looking the people up rather than scanning the dump**, all four gates green: Nagano, Entença, Alcimachus, Kayanid. Two were decided by dates, one by a three-generation chain Wikidata states cleanly, one by the Bundahishn. Total ancestral depth moved by −12 across fifteen records, worst −2 — that is the cycle-condensation arithmetic, not amputation.
The 18-record Roman one is still there, pending the right fix.
=== Queue — top 3 ===
1. **Find the real defect in the Scipio loop** — *diagnosed, and it needs you.* It is not in the Scipio half. `Q72786` "Marcus Aemilius Lepidus" carries **three separate father+mother couples**, and one of those fathers is the **son** of another. It is also listed as both spouse and child of the same record. That is a collapsed generation, and which parentage is the real one is Roman prosopography — I am not guessing it.
1. ~~Add a depth gate~~ — **DONE.** `verify_repair.py` runs all four gates as one command. Proved it can fail by running it against the reverted Scipio cut: it catches it at **-273 levels** where the old width-only check called that same cut clean.
1. ~~Merge Q72615 / Q72693~~ — **DONE.** They were both the father of one man, and that man listed both of them as his fathers — the dump saying it about itself.
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
- **NEW 2026-08-01 — the Livius Drusus tangle. One ruling, everything else is done.** `Q73119` carries **two Wikidata ids**: `Q433463` Marcus Livius Drusus the Younger (tribune, 91 BC) and `Q20005554` Marcus Livius Drusus Aemilianus, whose Wikidata description is literally *"father of the general Gaius Livius Drusus"*. It is one record playing two men four generations apart, which is why the loop closes — the tribune comes out as his own great-grandfather's father.
  - **The other half is already in the dump and needs no naming.** `Q148206` is an empty shell that is *already* recorded as a child of Salinator and a father of Gaius, from the other side only. So the unmerge is two removals, the same shape as the Tros one.
  - **What stops me applying it:** the Livii reach Aster **only** through the merged record. After the unmerge, Gaius Livius Drusus goes 921 ancestors → 15 and **exactly 10 records lose their route to `Q1` Aster** (46,703 → 46,693, counted by BFS, not estimated). Everything below is untouched, because it descends through the tribune, who keeps his real 920 through Cornelia.
  - **The question:** those 921 ancestors are the *tribune's*, inherited upward by his own great-grandfather — an artifact of the merge. **May the Livii Drusi lose that route to Aster?** If yes it is two lines and it is done today. If the line has to keep reaching Aster, then the repair is elsewhere: the correct route runs through Lucius Aemilius Paullus, and that branch dead-ends at 9 ancestors here **and dead-ends on Wikidata too** (`Q1306266`, consul 302 BC, no recorded father). Joining the Aemilii Paulli upward would be Gaiad material, which makes it yours.
  - I am not guessing Roman prosopography — that is the standing rule from the Lepidus item and I am holding to it.
- **Genesis 11 patriarchs under Mesopotamian royal names** — corrupt import (relabel all nine) or deliberate euhemerism (change nothing, add a note)? Opposite fixes; everything under the Table of Nations depends on it.
  - Euhemerism lol
  - **RECEIVED and applied.** Nothing relabelled. The relabel proposal is dead in all five places it was still live — it had survived in four spots in `epic_vs_dump.md` alone, including a summary row saying "only the names are wrong". Every DATA ERROR verdict resting on it is withdrawn.
- **Adam → Genghis** — A1 (attach Khaidu to the Borjigin chain already in the dump) or A2 (Haplogroup C2-M217), or both.
  - Both?
  - **RECEIVED: both A1 and A2.** Queued as executable work, not a question.
- **Chapter 181's "bore him ten sons"** — data fix invents nine named sons, prose fix drops a Garakguk-gi detail.
  - Uhh yeah the ten sons exist
  - **RECEIVED: the data moves, the chapter stands.** One thing I will not do silently — the report says the fix "means inventing nine named sons". I will go find whether Garakguk-gi names them. If it does, I record those names. **If it does not, that is a second question for you, not a licence for me to invent nine people.**
- **Which of the three Adnan records survives** (M3).
  - You merge them lol
  - **RECEIVED: merge all three**, not pick a survivor. Queued.
- **Naming the primordial half of Q74698 Tros** — the split is blocked on it, and Tros → Ops can be neither fixed nor cut until it has a name.
  - What? Explain better
  - **ANSWERED — and the answer is that the question is obsolete. Nothing needs naming.** I went and looked at the record instead of at the report. The split was already done. `Q74698` is now labelled **Uranus**, aliases *Uranus / Caelus / Ouranos*, and three things independently confirm that is what it is: its parents are **Aether and Dies**, which is exactly Hyginus's parentage for Caelus; its **59 children are the entire Ouranos roster** — the Titans (Rhea, Saturn, Tethys, Hyperion, Theia, Iapetos, Crius, Coeus, Phoebe), the Cyclopes, the Hecatoncheires, the Gigantes, the Erinyes; and there are **zero Trojan claims left on it** — no Ilus, no Assaracus, no Ganymede, no Dardanus, no Erichthonius, and "Tros" is gone from the aliases.
  - **The four mythic cycles are gone.** Q74698, Iapetos, Danaus, Nilus and Erichthonius are in no tangle at all.
  - **`Tros → Ops` was never spill and must never be cut.** Ops is Rhea. `Ouranos → Rhea` is correct Titan-tier parentage. It had been sitting in the repair tool's `PENDING_UNMERGE` list marked *blocked on Emma naming it* — so a **correct** edge was being held open as an unresolved question against you. Moved to `PROTECTED`; that blocked list is now empty.
  - **So this was never a naming decision.** It was a stale report outliving the fix it described. Sorry for asking you to name something that already had a name.

