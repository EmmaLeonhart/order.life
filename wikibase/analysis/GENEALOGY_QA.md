# Genealogy QA — local dump analysis (2026-07-01)

> **2026-07-30: use Wikidata.** The sections below were written under "fully local,
> nothing is fetched." That rule was about the dead Miraheze wiki, and it got wrongly
> extended to Wikidata, which is live, queryable and holds an ID for 60,085 of these
> records. A great deal of name-based guesswork in this file could have been a lookup.
> Two scripts now do that: `wiki-scripts/check_cycles_against_wikidata.py` (checks cycle
> edges) and `wiki-scripts/audit_wikidata_ids.py` (checks every stored ID). See
> "Wikidata cross-check" at the bottom.

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

## Wikidata cross-check (2026-07-30)

Two read-only scripts, both resumable, neither writes to the dump.

### `check_cycles_against_wikidata.py` → `qa_cycles_vs_wikidata.tsv`

Checks all 514 cycle edges against Wikidata's own P22/P25/P40. **186 confirmed,
33 contradicted outright, 6 inherited, 289 unknown** (one or both endpoints have no
Wikidata ID). By cycle: 27 of 70 are decided by Wikidata alone, with no name heuristics
involved at all.

"Inherited" means Wikidata has the same contradiction. **`Pons Hug d'Entença`
(Q21001415) lists Jussiana (Q14083227) as BOTH his mother and his child on Wikidata
itself**, and the dump copied it faithfully. That cycle is not an import artifact and
no local cleverness fixes it; the repair belongs upstream. It is the only such case in
the cycle set, but it is proof the dump is not always the guilty party.

### `audit_wikidata_ids.py` → `qa_wikidata_ids.tsv`

Walks all 60,037 distinct stored IDs (~4 minutes, 8 workers, cached in
`.wikidata_cache_full.json`).

| verdict | count | share |
|---|---:|---:|
| ok | 53,252 | 88.63% |
| unverifiable | 6,238 | 10.38% |
| not_a_human | 331 | 0.55% |
| name_mismatch | 127 | 0.21% |
| shared_id | 96 | 0.16% |
| sex_conflict | 32 | 0.05% |
| missing | 9 | 0.01% |

`unverifiable` is benign — a placeholder local label (`NN`), a label that is just a QID
string, or the two labels being in different writing systems so no comparison is
possible. Genuinely wrong IDs are about **595 records, ~1%**.

**But the bad ones cluster where it hurts.** `Ops` → Q96761 *Paul Bildt*, a Dutch film
actor. `Tros` → Uranus. `Danaus` → Oceanus. `Saturn` → Cronus. `Xu Fu` → Watatsumi —
and Xu Fu carries the Jimmu descent. Every one is in the Greek/Roman/mythic tier, which
sits under 46 of the 67 ancestry cycles and carries 34,365 descendants. The worst IDs
are attached to the most load-bearing nodes, so a 1% error rate is not a 1% problem.

**Systemic finding: Japanese names were romanised through Chinese pinyin.** 69 of the
127 name mismatches are a Latin local label against a CJK Wikidata label, and the
pattern is consistent — 徳川 is stored as `De Chuan` rather than Tokugawa, 細川 as
`Xi Chuan` rather than Hosokawa, 岩倉 as `Yan Cang` rather than Iwakura, 池田 as
`Chi Tian` rather than Ikeda. The kanji were read as Chinese. In these records the
`wikidata_qid` is **correct** and the local *label* is wrong, which is the opposite of
the other findings here — and it is why name-based matching kept failing on the
Japanese block.

Also spotted: `Q6439` has the local label `kontol`, Indonesian profanity, pointing at
帝臨魁. That is vandalism or junk, not a transliteration.

### Caveats worth keeping

- Wikidata is user-edited too and demonstrably holds impossible loops. "Confirmed"
  means the two copies agree, which is provenance, not truth.
- The audit's `not_a_human` check needs a wide notion of person for this genealogy —
  biblical figures, kami, naiads, Oceanids, disputed humans. The first pass flagged
  1,581 records with a too-narrow class list; the corrected list brings it to 331.
  If that number jumps again, suspect the class list before the data.
- An early threaded run recorded 1,961 IDs as `missing` that were really just batches
  that failed and never got cached. Re-running resolved it to 9. Unfetched is not the
  same as missing.
