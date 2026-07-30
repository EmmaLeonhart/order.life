# Q74698 "Tros" — the unmerge, and it needs no new records

**2026-07-30, work-loop. Propose only — nothing applied.** No `wikibase/items/*.json` and no
`wikibase/analysis/*.tsv` was modified. Follows `wikibase/analysis/cycle_policy.md`.

## The finding: the correct record already exists

There are two records labelled exactly `Tros`, and **Q132327 is already correct and clean**:

| | **Q132327** `Tros` (wd Q599482) | **Q74698** `Tros` (wd Q79999) |
|---|---|---|
| parents | Erichthonius of Dardania, Astyoche | **the same two**, *plus* Aether, Dies, Terra, Erebos, Nyx |
| spouses | Callirhoe, Acallaris | **the same two**, plus Terra, Nyx, and two blanks |
| children | Assaracus, Ganymede, Cleomestra, Ilus, Cleopatra | **the same five**, plus 65 more |

So this is not a merged record that has to be split into two new ones. **The Trojan Tros's
edges have been duplicated onto Q74698**, which is otherwise a completely different figure.
Every duplicated edge is already held, correctly, by Q132327.

## What Q74698 actually is

Strip the seven duplicated Trojan edges and what remains is unambiguous. Its 65 remaining
children, essentially all with **Terra** (Gaia) as the other parent:

- **Titans** — Ops, Saturn, Tethys, Themis, Iapetos, Hyperion, Theia, Coeus, Phoebe,
  Oceanus, Cronos, Crius, Rhea
- **Cyclopes** — Brontes, Steropes, Arges
- **Hekatoncheires** — Briareus, Cottus, Gyges
- **Gigantes** — Alcyoneus, Enceladus, Eurytos, Porphyrion, Pallas, Polybotes, Mimas,
  Clytius, Ephialtes, Gration, Hippolytos, Peloreus, Damysos, Anax, Otus, Abseus …
- **Erinyes** — Alecto, Megaera, Tisiphone

That is the canonical offspring of **Ouranos and Gaia**, complete. And its remaining parent
set — **Aether, Dies (Hemera), Terra** — is exactly Hyginus's genealogy for Caelus in the
*Fabulae* preface.

**Q74698 is Ouranos / Caelus, carrying the wrong label.** That conclusion comes from the
child list, not from the name — it is the strongest identification in this whole analysis.

**What to call it is Emma's, not mine.** Ouranos, Caelus, or whatever the Gaiad uses for the
sky-father. I am not picking a name for a record in a scripture project.

## Proposed change: remove 8 edges, create nothing

**Seven duplicated Trojan edges on Q74698** — each verified as already held by Q132327:

| Edge to remove | Already on Q132327? |
|---|---|
| parent `Erichthonius of Dardania` (Q132328) → Q74698 | yes |
| parent `Astyoche` (Q131114) → Q74698 | yes |
| Q74698 → child `Assaracus` (Q132329) | yes |
| Q74698 → child `Ganymede` (Q132330) | yes |
| Q74698 → child `Cleomestra` (Q132331) | yes |
| Q74698 → child `Ilus` (Q133643) | yes |
| Q74698 → child `Cleopatra` (Q133644) | yes |

**One spurious edge on Danaus:**

| Edge to remove | Why |
|---|---|
| parent `Danaus` (Q74973) → `Nilus` (Q130061) | Nilus's parents are **Oceanus and Tethys**, both already recorded. Nilus is Danaus's *ancestor* — Nilus → Anchiroe → Danaus — so this edge has him as his own great-grandchild's child |

Also relabel Q74698 (see above). **No records created. No records deleted. No
cross-tradition join touched.**

## Verified, by simulation

Rebuilt the parent map without those 8 edges and re-tested all 71 recorded cycle chains:

```
known cycle chains intact BEFORE : 63/71
known cycle chains intact AFTER  : 59/71
broken by this change            : 4
   len=6  Q74698 Tros
   len=7  Q74698 Tros
   len=5  Q90576 Belus
   len=3  Q74973 Danaus
```

**All four mythic cycles gone.** And the joins survive, checked explicitly:

- `Nilus` keeps **Oceanus + Tethys**
- `Danaus` keeps **Belus + Anchiroe** — the Greek/Egyptian join Emma flagged as the thing
  that must not be cut
- `Atlas → Electra → Dardanus` untouched
- all five Trojan children keep `Tros` Q132327
- Libya, Memphis, Epaphus untouched

Reproduce: the simulation is the snippet in this commit's message; the underlying graph
loader is `wiki-scripts/graph_probe.py`.

## Two things noticed, not acted on

1. **63 of 71, not 71 of 71.** Eight of the recorded cycle chains no longer exist in the
   current dump — earlier repairs (commit `9c0299d8`, "repair 8 mutual pairs") already broke
   them. `qa_cycles_proposed.tsv` is stale by eight rows and should be regenerated before
   anyone counts cycles again.
2. **`Oceanus` (Q90309) carries `wikidata_qid` Q161419, which is Danaus's identifier** —
   `Danaus` (Q74973) carries the same one. A duplicate-ID collision in the middle of this
   same neighbourhood. Belongs to the ID-repair worklist, not to this item.

## Residue this does not fix

`Danaus` (Q74973) keeps `Tros`(Q74698 → Ouranos) and `Terra` as parents alongside Belus and
Anchiroe. Those two look like spill from the same duplication, and Danaus's parents in every
account are Belus and Anchiroe. **They cause no cycle, so I am not proposing their removal
here** — flagging them for the fan-out worklist instead. Danaus has 231 recorded children
and is already a known fan-out suspect.
