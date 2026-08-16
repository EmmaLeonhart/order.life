# The Licinii Vari: `Q73308` does not need a father. There are two Licinias.

Research for `queue.md` item 2, done 2026-08-15 against Wikidata. The item asks *"who was
`Q73308`'s father?"* on the reasoning that one edge would return 103 Republican Roman
records to the synoptic descent. **The premise is wrong in a way that matters**, and the
research says so rather than supplying the missing name.

## What the dump records

    Q73308  "Licinius  Varus"          no wd, geni 6000000030478073233
      -> Q73140  "Gaius Lincinius  Varus"   no wd, geni 6000000030478360865
           -> Q72966  "Lincinia  Varus"     no wd, geni 6000000002188289192
                spouse Q72963 Q. Mucius Scaevola (pr. 215, wd Q939045)
                child  Q72807 P. Mucius Scaevola (cos. 175, wd Q2066659)
                   -> the Mucii Scaevolae, Licinii Crassi, Pompey, Asinius Pollio ...

Every one of those three Licinii carries a Geni id, GEDCOM surname slashes, the
misspelling *Lincinius*, and **no Wikidata id**.

## What the sources record

| | |
|---|---|
| `Q1338451` Gaius Licinius Varus, **cos. 236 BC** | child: `Q26110551` P. Licinius Varus (pr. 208). **NO FATHER.** |
| `Q2066659` P. Mucius Scaevola, **cos. 175 BC** | father `Q939045`/`Q6095299` Q. Mucius Scaevola. **NO MOTHER.** spouse **`Q12284962` Licinia** |
| `Q12284962` Licinia | *"wife of Publius Mucius Scaevola"*; children `Q261441` (cos. 133) and `Q715499` Mucianus |
| `Q715499` P. Licinius Crassus Dives Mucianus | father `Q2066659` **and** `Q746582` P. Licinius Crassus; mother `Q12284962` Licinia |

Two things follow immediately.

**The cos. 175 has no recorded mother.** The Licinia in his life is his **wife**, and she is
why his younger son was adopted into the Licinii Crassi and became *Mucianus* — the
adoption runs through his mother's kin. That is CLAUDE.md case 2, adoptive + biological,
and Wikidata records both fathers on `Q715499` exactly as the rule expects.

**Gaius Licinius Varus, consul 236 BC, has no attested father.** The line stops there. So
`Q73308` — the dump's generation *above* him — corresponds to no one in the sources at all.
**There is no name to find. This is not a research gap; it is where the evidence ends.**

## The actual defect: the dump holds TWO Licinias, one generation apart

| | `Q72810` — correct | `Q72966` — the problem |
|---|---|---|
| label | Licinia | "Lincinia  Varus" |
| wikidata | **`Q12284962`** | none |
| geni | 6000000002188289**159** | 6000000002188289**192** |
| aliases | "Licinia, wife of Scaevola" | "Lincinia /Varus/" |
| spouse | `Q72807` cos. 175 | `Q72963` pr. 215 |
| children | `Q72633` cos. 133, `Q141474` Mucianus | `Q72807` cos. 175 |
| father | `Q72972` | `Q73140` |

**Both are the same woman.** The Geni ids are eighteen apart in one import block. One copy
is attached correctly — wife of the cos. 175, mother of the cos. 133 and of Mucianus,
matching Wikidata claim for claim. The other is attached **one generation too high**, as
the cos. 175's mother, a relationship no source records.

And the fathers confirm it. `Q72972`, father of the correct Licinia, carries the aliases
**"Gaius Licinius Varus /Licinius-Crassus/"** and **"Publius Licinius Varus Licinius
Crassus Dives"**, and `Q72969` his wife is labelled **"NN (Wife of Gaius Licinius
Varus)"**. So the Licinii Vari are *already* joined to this family through the `Q72972`
copy. The `Q73140` copy is the duplicate.

## Why this cannot simply be deduped, and what is genuinely open

`Q72966`'s **only** child is `Q72807`. Her only function in the graph is to be the cos.
175's mother. Delete that false edge and the 103 Republican records above her — the whole
`Q73308` → `Q73140` → `Q72966` stem — **detach completely**, because nothing else connects
them.

So the position is exactly the one `narrative_spine.md` names:

> *A severed line is honest and one edge from correct. A line attached through the wrong
> story is already wrong while measuring as fine.*

**Today the Licinii Vari are the second kind.** They reach `Q1` Aster, and they reach it by
a mother-son link that no source records, invented by a GEDCOM import to bridge two blocks.

`Q72972` is **not** a safe reattachment point as it stands: its Wikidata id is `Q29518656`
P. Licinius Crassus Dives, who is **Mucianus's son** — two generations *below* the cos.
175 — while the record simultaneously stands as father of the cos. 175's wife. That record
is itself a conflation of at least two men and must be untangled before anything is hung
from it.

## What is left to decide, and by whom

**Research is done and it does not settle the attachment.** The sources give the Licinii
Vari no ancestor above the consul of 236 BC, so no edge can be sourced. Three options, and
choosing among them is narrative intent, which is Emma's:

1. **Accept the severed line.** Cut the false `Q72966` → `Q72807` edge; the 103 become
   rootless. Honest, one edge from correct, and consistent with the spine.
2. **Dedupe `Q72966` into `Q72810`** and re-hang the Vari stem from `Q72972` — but only
   after `Q72972`'s own conflation is resolved, since as recorded it is chronologically
   impossible.
3. **Invent a bridge** above `Q73308` to carry the Republic into the descent deliberately,
   which is a Gaiad decision and needs Emma's explicit approval per CLAUDE.md.

**Do not apply any of these on the strength of this document alone.** What is established
here is the diagnosis: the cos. 175 had no Licinia for a mother, the dump has her twice,
and the Republican block currently hangs from the copy that is wrong.
