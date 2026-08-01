# Cycle repair policy — what the genealogy is for

**2026-07-30. Written after Emma corrected the framing twice. Supersedes the repair
recommendations in `cycle_origins.md`.**

## What I had wrong

I was treating this genealogy as a database with defects, and scoring cycles by how cheap
they were to cut. Two things follow from that framing and both are wrong here.

**1. I proposed cutting the mythic tier, and put it last as a tidy-up.** Belus → Danaus,
Atlas → Electra, Danaus → Nilus. Those joins are the *product*. The genealogy is a literary
device for linking people across time and space, and it is building a **synoptic
mythology** — Greek, Near Eastern, Egyptian, Trojan lines integrated into one descent.
Severing Danaus from Belus to clear a loop destroys precisely what the structure exists to
do. It was the worst available option and I ranked it as routine.

**2. I used "load-bearing" to mean descendant count.** That is *width*. The priority is
**depth** — ancestry running back, not fanning out. `qa_cycles_load.tsv` scores every cycle
by "cheapest_cut_loses = descendants lost", and I carried that framing forward without
questioning it. A cycle can lose zero descendants and still be catastrophic to cut, because
what it loses is a *link between traditions*.

**3. And the base assumption was wrong.** Almost everything unexpected in this dump was put
there deliberately, by import. The Emesene route in Muhammad's ancestry, the Genesis 11
patriarchs under Mesopotamian royal names, the Mongol chain descending from the Buddha —
these are authored. "Surprising" is not evidence of "broken."

## The policy

**Repair order, strictly. Prefer the fix that preserves the most connection.**

1. **UNMERGE first.** An improper merge is the most common real cause, and unmerging *adds*
   structure — both lines survive, both sets of edges survive, the cycle disappears. Most
   of these records have working Wikidata ids, so the two people can be told apart by
   lookup. This is the default, not the fallback.
2. **DEDUPE parallel imports second.** Where the same material was imported twice, merging
   the copies removes cycles without anyone choosing an edge to cut.
3. **CUT only when 1 and 2 do not apply**, and never an edge that is the only link between
   two traditions.
4. **DELETE only where the loop is genuinely terminal** — nothing substantial above it,
   nothing lookupable in it. Keep the entry point into the loop, drop the rest. This is the
   narrow case Emma described, not the general one.

**Never sever a cross-tradition join to break a cycle.** If a cycle can only be broken by
cutting such a join, that is a signal the real defect is elsewhere in the loop — go find it.

## Worked case: the mythic cycles are one merge, not four tradition conflicts

> **DONE, and the naming question it ends on is answered by the dump itself (2026-07-31).**
> Emma asked for a better explanation of "naming the primordial half of Q74698 Tros". The
> honest answer is that **there is nothing left to name.** The split below was carried out,
> and the primordial half is `Q74698` itself, which is now labelled **Uranus**, aliases
> *Uranus / Caelus / Ouranos*. Three independent checks agree:
>
> - **Parents: Aether and Dies.** That is exactly Hyginus's parentage for Caelus. (It also
>   still carries Terra, Erebos and Nyx, which is the residue worth a look — but not a
>   naming question.)
> - **Children: 59, and the roster is Ouranos's, entire.** The Titans (Ops/Rhea, Saturn,
>   Tethys, Hyperion, Theia, Iapetos, Crius, Coeus, Phoebe), the Cyclopes (Brontes,
>   Steropes, Arges), the Hecatoncheires (Gyges, Cottus, Briareus), the Gigantes, the
>   Erinyes.
> - **Zero Trojan claims remain.** No Ilus, no Assaracus, no Ganymede, no Dardanus, no
>   Erichthonius, and "Tros" is gone from the aliases.
>
> **The four cycles below are gone.** `Q74698`, `Q75225` Iapetos, `Q74973` Danaus,
> `Q130061` Nilus and `Q132328` Erichthonius are in no tangle at all.
>
> **`Tros -> Ops` was never spill and must not be cut.** Ops is Rhea; `Ouranos -> Rhea` is
> correct Titan-tier parentage. It sat in `propose_tangle_repairs.py`'s `PENDING_UNMERGE`
> as blocked-on-Emma, which marked a *correct* edge as unresolved; it has been moved to
> `PROTECTED` and `PENDING_UNMERGE` is now empty.
>
> Everything below this line is the original 2026-07-30 diagnosis, kept as the record.


Four cycles run through `Tros` (Q74698, wd Q79999). The record carries **two incompatible
parent sets simultaneously**:

| | parents |
|---|---|
| primordial tier | Aether, Dies, Terra, Erebos, Nyx |
| Trojan tier | Erichthonius of Dardania (Q132328), Astyoche (Q131114) |

and **70 children** spanning both tiers, including **Iapetos** (Q75225), **Ops** (Q74677)
and **Danaus** (Q74973) — all of them generations *above* Dardanus.

That is Tros king of Dardania merged with a primordial-tier progenitor. The loop follows
directly:

```
Tros -> Iapetos -> Atlas -> Electra -> Dardanus -> Erichthonius of Dardania -> Tros
```

Tros is his own great-great-great-grandfather. The contamination then propagates:

- `Danaus` (Q74973) has parents Anchiroe, **Tros**, Terra, Belus. His parents are Belus and
  Anchiroe; the Tros and Terra edges are merge spill.
- `Nilus` (Q130061) has parents Tethys, **Danaus**, Oceanus. Nilus is Oceanus and Tethys's
  son, and he is Danaus's *ancestor* (Nilus -> Anchiroe -> Danaus), not his child.

**Proposed: split Q74698 into two records.**

- **Tros of Dardania** — parents Erichthonius + Astyoche; keeps the Trojan descent.
- **the primordial figure** — parents Aether, Dies, Terra, Erebos, Nyx; keeps Iapetos, Ops
  and the Titan descent. *What this figure should be called is Emma's, not mine — the dump
  does not say, and guessing a name here would be inventing.*

Then drop the two spill edges: `Tros -> Danaus` and `Danaus -> Nilus`.

**What this preserves:** Belus -> Danaus, Atlas -> Electra -> Dardanus, Iapetos -> Atlas,
Libya, Memphis, Epaphus, Nilus, Oceanus/Tethys — every cross-tradition join stays. Four
cycles gone, nothing severed.

**Confidence: high on the diagnosis** (a record cannot have both the primordials and
Erichthonius as parents), **needs Emma on the naming** of the primordial half.

## The long Iberian chains

Emma: "the very long chains are things I'm afraid of cutting." Agreed, and they should not
be cut. Seven of the eight cycles of length >= 20 run through one twelve-edge stretch of the
Portuguese **de Aguiar** family that ends by joining it to Heracles via
`Barbara, imperatriz of Rome` / `Bárbara, Princess of Rome` — an accented duplicate pair,
and `Diogo Afonso **Afonso** de Aguiar`, a doubled name. Those are unmerge/dedupe
signatures, not cut candidates. **Same treatment: split or merge the duplicates, keep the
join to Heracles.** That join is the whole reason the chain exists.

## How to verify a repair — one command

```
python wiki-scripts/verify_repair.py --snapshot     # BEFORE: freeze the current edges.tsv
...make the repair...
python wiki-scripts/verify_repair.py                # AFTER: regenerate, then every gate
```

It runs `extract_genealogy.py`, then `compare_tangles.py` (width), `compare_depth.py`
(depth), and `check_invariants.py`, and exits non-zero naming whichever failed. Shadow
consistency is *not* in it: `.githooks/pre-commit` checks exactly the records you staged,
which is better targeted than anything an `edges.tsv` pair could see. Install it once per
checkout with `git config core.hooksPath .githooks`.

**Why it is one command and not a list of steps.** Every one of those gates already
existed on 2026-07-31 when the `Q73893 -> Q73794` cut went in, passed review, and was
reverted the same day for stripping 263 generations off the Scipio line.
`compare_depth.py` had been written *specifically* to catch that and was never wired to
anything — the ritual lived in prose in `queue.md`, so running all of it in the right order
depended on remembering it mid-repair. A gate nobody runs is not a gate.

**The two gates disagree, and that is the point.** Re-run against a synthetic `edges.tsv`
with that one edge removed and `compare_tangles` reports the repair *clean* while
`compare_depth` fails with 27,554 records down and a worst loss of 273 levels. Width said
yes; depth said no; depth was right. Never read a green `compare_tangles` as a verified
repair.

**If `compare_depth` fails, do not lower `--max-loss`.** The failure means the edge was a
gateway, and `cycle_policy.md`'s rule applies: the real defect is elsewhere in the loop. Go
find it.
