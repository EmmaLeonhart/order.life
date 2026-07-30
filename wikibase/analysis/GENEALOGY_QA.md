# Genealogy QA — local dump analysis (2026-07-01)

Analysis + QA of the **local, committed** Wikibase genealogy dump. Fully local —
reads `wikibase/analysis/{persons,edges,spouses}.tsv` (extracted from the
`wikibase/items/*.json` snapshot). **The source wiki was taken down by Miraheze
as off-topic; the local dump is now the only copy. Nothing is fetched.**

Regenerate: `python wiki-scripts/genealogy_network_analysis.py` (summary →
`genealogy_qa_report.txt`) and `python wiki-scripts/dump_qa_errors.py` (full error
lists → `qa_multiparent.tsv`, `qa_cycles.tsv`).

## Graph shape
- **106,926 persons**, **128,717 parent→child edges**, 24,784 spouse edges.
- Field coverage: label 99.3%, sex 97.1%, wikidata_qid 56.2%, geni_id 32.7%.
- Weakly-connected components: 2,408; **giant component 101,358 (94.67%)**; 2,046 isolates.
  Notable standalone islands: Zhu/Ming clan (1,325), an Emma-Leonhart family cluster
  (500), Khitan/Yelü (141).
- Centrality (graph-walked descendant counts) confirms the load-bearing gateway
  ancestors: **Jesus 28,512**, **Charlemagne 12,539**, Muhammad 3,630, Bustanai 3,250,
  Genghis Khan 349, Confucius 213, Heo Hwang-ok 46. The Greek/primordial tier
  (Erebos/Nyx/Terra ~34,400) sits one level above via the Jesus-through-Rome backbone.

## Data errors found (the "QA")
These are import artifacts from Geni, not Gaiad-authored content.

1. **1,230 children with >2 biological parents** — full list in `qa_multiparent.tsv`
   (`child_qid, child_label, n_parents, parent_qids`). Worst offenders have 8–9 listed
   parents (e.g. Sita Q28324 with 9, Marcus Livius Drusus Q73119 with 8). Concentrated
   in Iberian royalty (León/Pamplona/Castile) — classic Geni merge duplication.
2. **~70 ancestry cycles** (69 via the summary walk, 71 via the full DFS dump —
   traversal-order difference) — full list in `qa_cycles.tsv` (`cycle_len, chain_qids,
   chain_labels`). A cycle means the data asserts someone is their own ancestor
   (impossible). Range from 2-node direct contradictions up to a ~50-node chain
   through Portuguese/Byzantine nobility.
3. **Fan-out conflation suspects** (top by child count): Danaus (231), Oceanus (155),
   Tethys (146), Dhritarashtra (131), Poseidon (127), Heracles (113). One node is
   literally labelled `BAD MERGE` (Q73380, 29,466 descendants) — a known conflation
   sitting on the main backbone.

## Fix status — NOT auto-fixed (deliberate)
The errors are **enumerated and committed**, but **not corrected**, because correcting
them is per-record genealogical judgement, not a mechanical pass:
- Picking which of 3–9 claimed parents is the true biological pair, or which edge in a
  cycle to cut, requires knowing the real lineage. Auto-guessing = fabricating scripture
  genealogy. Hard-rail: don't invent.
- The wiki is gone, so fixes can only be made to the **local dump** (TSV/JSON), not
  upstream. Any fix is a local data edit + re-extract.

Recommended next step when someone wants to act: work `qa_cycles.tsv` first (small,
unambiguous "this is wrong"), then the highest-`n_parents` rows of `qa_multiparent.tsv`.
Both are bounded lists now.

## Cycle cut proposals (2026-07-30) — `qa_cycles_proposed.tsv`

`python wiki-scripts/propose_cycle_cuts.py` reads `qa_cycles.tsv` and writes one row per
cycle naming the single edge it proposes to cut, the evidence, and a confidence. It is
**propose-only**: it modifies neither `wikibase/items/*.json` nor the source extracts, and
where the evidence does not decide a cycle it emits an `unresolved` row rather than
guessing. 46 of the 71 cycles get a proposal (10 high / 5 medium / 31 low confidence);
25 are left for a human. The 39 distinct proposed edges break 47 cycles between them —
one duplicate pair alone (`Barbara, imperatriz of Rome` / `Bárbara, Princess of Rome`)
accounts for the seven long Portuguese/Byzantine chains.

Two false-positive classes the rules deliberately avoid, both of which a naive pass hits:

- **Unsigned BC dates.** Many Roman republican figures are recorded as `+0300` where the
  source meant 300 BC. Read as BC the edge order is often fine, so those rows are demoted
  to `date_ambiguous_era` at low confidence — the fix is probably the *date*, not the edge.
- **Regnal and cognomen distinctions.** `Guerau IV -> Guerau V` and `Scipio Barbatus ->
  Scipio` are how the data distinguishes a father from his son. Those are treated as
  corroboration or as unproven homonyms, never as duplicates to merge.

Nothing here has been applied. Approving a row means an edge deletion (or, for the
duplicate rows, a record merge) in a later, separate pass.

## Multi-parent proposals (2026-07-30) — `qa_multiparent_proposed.tsv`

`python wiki-scripts/propose_multiparent_fixes.py` clusters each child's listed parents
and proposes one representative per cluster when they collapse to a biological pair.
Also propose-only.

**409 of the 1,230 children (33.3%) collapse to ≤2 distinct people** and get a proposed
parent set; the other 821 do not and are emitted `unresolved` with their clusters shown.
They are not rank-and-truncated to two: once a child has three genuinely distinct claimed
parents, deduplication has nothing left to say and the choice is genealogical judgement.
Applying every proposal would remove 436 of the 4,012 listed parent edges.

Records merge only on identical external ID, identical name tokens, ≥90% label
similarity with a matching given name, or a full spelling-variant match of every surname
token. That last rule is what separates `Sancha de Aybar` / `Sancha of Aibar` (one person,
merged) from `Jimena Muñoz` / `Jimena Fernandez de Castro` (two of Alfonso VI's partners,
kept apart) — both pairs share a given name, so a plain similarity threshold gets one of
them wrong whichever way it is set. Regnal numbers, elder/younger markers (`maior`,
`minor`, `Junior`) and conflicting recorded sex all block a merge.

Clustering is single-linkage, so a chain of near-identical labels becomes one cluster.
That is right for duplicate detection but means a large cluster deserves a look before
it is applied.
