# Where things stand — 2026-07-31

Run **`sh wiki-scripts/resume.sh`** after rebooting. That is the only command needed.

## Safe to shut down

Everything durable is pushed. The one dirty file, `wikibase/analysis/persons.tsv`, is a
**derived** extract mid-write by a background job — `resume.sh` restores and rebuilds it.
Nothing authored is at risk. The item JSONs under `wikibase/items/` are the source of truth
and are all committed.

## What does NOT survive the reboot

The three work-loop crons (`:03` work-loop, `:15` auto-flush, `:42` status-report) live in
the Claude session, not on disk. They are gone. A new session recreates them — say
"start the work loop".

## Cycle progress today

| | start of day | now |
|---|---|---|
| records inside a cycle | 379 | **305** |
| largest tangled component | 88 | **73** |
| tangled components | 38 | 38 |

Cycle *counts* from `qa_cycles.tsv` are a basis, not a stable set — they move without the
graph changing. Trust `check_invariants.py` (strongly-connected components), not the count.

## Applied to the dump today

- **Ouranos unmerged from Tros of Dardania** (Q74698). The record held both figures; the
  Trojan half was already complete on Q132327. Four mythic cycles gone, no join severed.
- **Four Roman mutual-parent cycles** broken (Torquatus, Fulvius, Valerius, plus a stub).
- **Eight duplicate pairs merged** as redirects, plus 5 orphaned shadow qids repaired.
- **Three long Iberian cycles** broken by cutting `Q81339 → Q82122` (a Portuguese noble
  recorded as father of a Roman empress). **Heracles → de Aguiar survives** — verified.
- **Three further cuts**: Cervantes (Juan was Miguel's grandfather), Iwakura (b.1746 cannot
  parent b.1705), and Crassus Mucianus → Crassus Dives (adoption recorded backwards).
- **52 shadow files propagated** so edits are durable.

## Awaiting your decision

1. **Cato the Elder cluster.** Q148133 and Q73005 both carry `wd Q180081`. Five shadow
   files assert Q73167 "Marcus Porcius Censorius" is Cato's father; the canonical record
   does not. Is Q73167 a third Cato duplicate, his father, or his son Licinianus?
2. **Q74698's label.** Currently `Uranus`, taken from the record's own aliases
   (`['Uranus', 'Caelus', 'Tros', 'Ouranos - - Uranos Caelus']`). Caelus? Ouranos?
3. ~~**The patriarch overlay.**~~ **ANSWERED 2026-07-31 by Emma: deliberate euhemerism.**
   All of Genesis 11 sits under Mesopotamian royal names — `Shu-Ilishu` is Noah,
   `Puzur-Ashur` is Shem — **and that is intentional. Change nothing; the relabel is dead.**
   See `wikibase/analysis/patriarch_overlay.md`. Note this was already covered by
   `CLAUDE.md`'s standing rule that surprising is not evidence of broken; it should not have
   been carried as an open question.
4. **9 dead Wikidata ids** — you chose "find replacements first", which needs live Wikidata
   lookups. Not started.

## Next work, in order (`queue.md` has the detail)

1. Cato cluster — blocked on you
2. Fold `qa_cycles_vs_wikidata.tsv` into the cycle proposals; 7 of 25 "unresolved" cycles
   already have an edge Wikidata contradicts
3. Remaining cycles under the repair order — **unmerge first, never sever a tradition join**
4. The one-sided edges (`edge_symmetry.txt`)

## Two things not to relearn

- **Dates are sign-corrupt for BC figures.** Quintus Mucius Scaevola Pontifex has birth
  `+0140`, death `+0082` — he dies before he is born. `death < birth` detects it. Do not cut
  Roman edges on date evidence; two ~400-year "violations" are almost certainly sign errors.
- **An edit must be propagated to a record's shadow files**, or it silently reverts. The
  pre-commit hook enforces this; install it with `git config core.hooksPath .githooks`.
