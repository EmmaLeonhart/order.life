# The Cato the Elder cluster — resolved

**2026-07-31. Applied, not proposed. Closes queue.md item 1.**

## The question

`queue.md` asked whether `Q148133`, `Q73005` and `Q73167` are one man:

> Q148133 and Q73005 both carry `wd Q180081` (Cato the Elder) and Q73167 is
> `Marcus Porcius Censorius` — Censorius is Cato's own cognomen. […] If the three are one
> man, merge all three; if Q73167 is Cato's father or his son Licinianus, one of the two
> edges is simply wrong. Decide which, then apply.

## The answer, from the dump itself

```
Q73167  "Marcus Porcius  Censorius"    P47 father = Q73005 Cato the Elder
                                       P48 mother = Q73329 Licinia
Q73005  "Cato the Elder"               P42 spouse = Q73329 Licinia
```

**Q73167's mother is Cato's own wife.** A man cannot have his son's wife for a mother, so
Q73167 is neither a third copy of Cato nor Cato's father. He is Cato's son by Licinia —
which is exactly **Marcus Porcius Cato Licinianus**, whose cognomen means "Licinia's son".

The label was the trap. `P5` reads `Marcus Porcius /Censorius/`: the source carried the
*father's* cognomen in the surname slot, so the record came in named after Cato instead of
after himself. Reading the label rather than the parent claims is what made this look like
a third Cato for as long as it did.

The record now carries `wd Q1275684` (Cato Licinianus) from the merge, so it has been
relabelled to **Marcus Porcius Cato Licinianus**, with `Marcus Porcius Censorius` kept as
an English alias. Nothing is lost and the record no longer contradicts its own Wikidata id.

## The defect underneath

The queue's premise — three records, one man — was wrong in a useful way. There is no third
Cato. There is a **parallel import of the entire Porcii Catones family**, one branch under
`Q7xxxx` and an independent one under `Q14xxxx`/`Q15xxxx`:

| survivor | loser | person | evidence |
|---|---|---|---|
| Q73005 | Q148133 | Cato the Elder | shared `wd Q180081` |
| Q73002 | Q148134 | Salonia | shared `wd Q435959` |
| Q73329 | Q151388 | Licinia | position |
| Q72855 | Q144170 | Cato Salonianus | shared `wd Q1181865` |
| Q73167 | Q148135 | Cato Licinianus | position |
| Q72684 | Q141517 | Marcus Porcius Cato | shared `wd Q1372970` |
| Q72496 | Q141438 | Cato the Younger | shared `wd Q193506` |

Five of the seven are decided by a Wikidata id that **both** sides carry — the same evidence
standard `qa_wikidata_ids.tsv` already uses for its `shared_id` verdict. The remaining two
carry an id on one side only; that is a gap, not a conflict, and both are forced by the
other five: both Licinia records are wife-of-Cato and mother-of-the-Licinianus-record, and
both Licinianus records are son-of-Cato-and-Licinia. Leaving them apart would have handed
the merged Cato two duplicate wives and two duplicate sons.

This is **repair-order step 2, DEDUPE** (`cycle_policy.md`). No edge was cut, no
cross-tradition join was touched, and both descents survive: the union is strictly larger
than either branch. Every one of the seven merges *gained* claims and none lost any.

## Why the survivor is always the low side

Every `Q7xxxx` record in this cluster has shadow files; no `Q14xxxx`/`Q15xxxx` record has
any:

```
Q73005  shadows Q87608 Q99390 Q111052 Q185613 Q185617      Q148133  none
Q73167  shadows Q73476 Q87716 Q87923 Q185614 Q185616      Q148135  none
Q72855  shadows Q87508 Q185636                             Q144170  none
Q72684  shadows Q87393 Q185192                             Q141517  none
Q72496  shadows Q87267 Q185194                             Q141438  none
Q73002  shadows Q87606 Q185638                             Q148134  none
Q73329  shadows Q87824 Q185637                             Q151388  none
```

Merging the other way — Q73005 into Q148133, which is what was tried before and reverted —
**vacates a shadowed qid**. `extract_genealogy.py` keeps the numerically-lowest file per
qid, so a shadow immediately wins the vacancy and injects its own claims, and that is how
the phantom `Q148133 <-> Q73167` 2-cycle appeared out of a graph that did not contain the
edge beforehand. Merging into the low side vacates only `Q14xxxx`/`Q15xxxx` qids, which
nothing can re-claim. All 27 files — losers and every shadow of both sides — were rewritten
to the survivor's content in the same pass.

## Left standing on purpose

Below Cato the Younger the two branches stop corresponding one-to-one. The `Q7xxxx` branch
gives him one child, `Q78063` "Porcia Catonis" (no Wikidata id); the `Q14xxxx` branch gives
him five, including three separate Porcia records (`Q141439`, `Q141441`, `Q144042`). Q78063
is probably one of those three, but **the dump does not say which and no shared id decides
it**. Guessing would invent a person, so the merged Cato the Younger keeps all six children
and the Porcia duplication stands. It is now its own queue item, not a silent residue.

## The cycle counter was broken, and that had to be fixed first

The first attempt to verify this merge compared `qa_cycles.tsv` before and after and got
**47 cycles both times**. That number was worthless, and so was the comparison.

Running the unchanged `dump_qa_errors.py` three times over one unchanged `edges.tsv`
returned **45, 50 and 46**. Two defects, both in the cycle section:

1. It iterated `set`s of qid strings. Python randomises string hashing per process, so
   traversal order — and therefore which cycles the DFS happened to find — changed on
   every invocation.
2. It marked nodes `BLACK` on pop and never revisited them, so it found *some* cycles per
   tangle, never all. It was never counting cycles in the first place: a single tangle of
   n nodes can contain exponentially many.

**Every "cycles went from X to Y" claim in `devlog.md` and `queue.md` that came from this
script is unsound**, including the `52 -> 54` regression that `check_invariants.py` was
written to catch. (`check_invariants.py` itself was always fine — it uses Tarjan, and the
SCC partition is unique regardless of traversal order, which is why its numbers were the
stable ones all along.)

`dump_qa_errors.py` now computes strongly connected components over sorted adjacency and
emits **one canonical shortest cycle per tangle**, plus `tangle_size` and `tangle_qids`
columns. Five consecutive runs now produce a byte-identical file, and its totals —
36 tangles, 299 records — match `check_invariants.py`'s independent Tarjan exactly. Row
count is now a real quantity: the number of tangles.

The right invariant is the tangle, not the cycle. **Compare tangles, never cycle counts.**

## Verification

The pre-merge graph was reconstructed exactly rather than re-extracted: every file outside
the 27 the merge touched is byte-identical, so the untouched edges come from the current
`edges.tsv` and the rest are re-derived from the `HEAD` versions of the merged records and
of every neighbour of a survivor, canonicalised through the pre-merge redirect map. The
reconstruction lands on **128,689 canonical parent edges — exactly the figure the
independent full extract reported before the merge**, which is what makes it trustworthy.

| | before | after |
|---|---|---|
| tangles (SCCs, size > 1) | 36 | **36** |
| records inside a tangle | 299 | **299** |
| largest tangle | 72 | **72** |
| tangles introduced by the merge | — | **0** |
| tangles removed by the merge | — | **0** |
| tangles containing any merged qid | 0 | **0** |
| canonical persons | 107,046 | 107,039 (−7, exactly the merges) |
| canonical parent edges | 128,689 | 128,682 (−7, duplicates collapsed) |
| loser qids surviving as graph nodes | — | **none** |

The two SCC partitions are not merely equal in count — they are the **same sets**. The
merge is structurally neutral on tangles and strictly additive on claims, which is what a
correct dedupe should be.

`check_invariants.py`: **PASS**, no invariant regressed; the baseline has been ratcheted
from 38 / 379 / 88 down to 36 / 299 / 72 so the standing gain cannot silently erode.
`check_staged_shadows.py` on all 14 qids: **all consistent**.
`shadow_audit.py` over all 164,536 files: **0 qids where the files disagree**.
