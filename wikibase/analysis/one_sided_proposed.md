# One-sided BOTH-REAL edges against Wikidata (queue item 16), 2026-10-10

`edge_symmetry.py` rebuilt on 2026-10-10: 2,670 one-sided edges, of which **2,451 BOTH-REAL** (both
endpoints are real records). `wiki-scripts/propose_one_sided.py` checked each against Wikidata where
both endpoints carry a Wikidata id (child's P22/P25, parent's P40). Rows: `one_sided_proposed.tsv`.

| verdict | edges | what was done |
|---|---:|---|
| **CONFIRMED** | **330** | Wikidata records the pair. **Missing side added** by `apply_one_sided_confirmed.py` (467 claims in 381 files, shadows included). Graph-neutral. |
| CONTRADICTED | 172 | Wikidata gives the child a different parent in that role. **Nothing changed.** |
| SILENT | 7 | both have Wikidata ids; Wikidata records neither the pair nor a rival |
| NO_WD | 1,942 | one or both endpoints lack a Wikidata id |

**The CONTRADICTED rows are not a cut list.** Spot-checked, they are at least three different things:

- **A wrong Wikidata id on the dump's record**, not a wrong edge: `Q123443` "Sancha", mother of
  Sancho II, García II and Alfonso VI, carries wd `Q111457114` (a different Sancha), while Wikidata
  gives their mother as `Q1847459` Sancha of León.
- **Deliberate myth variants**: `Q131430` Dies as mother of Uranus and Terra (Hyginus's version).
- **Rulings already made**: `Q74991` Abas keeps Ixion, not Poseidon (the divine-father ruling,
  2026-08-07). `Q73380` is labelled "BAD MERGE".

Each needs a look of its own, with the narrative-spine and cycle-policy rules.
