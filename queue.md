# order.life — Autonomous Work Queue

Worked top-to-bottom by the autonomous work-loop cron (`:00`/`:30`). Each item is
bounded, verifiable, and unblocked. **Delete an item from this file in the same
commit that completes it** (delete-don't-check). Source backlog: `todo.md`.

**Hard rails:** never fake; never weaken/skip a test to pass; never claim
"works"/"verified" without running it; document real blockers, don't paper over
them. **Chapter gate:** do NOT generate new Gaiad chapters before Leo (2026-08-12).

---

## ACTIVE (do in order)

_The genealogy QA work below was previously parked as "BLOCKED / NEEDS EMMA." Emma
unblocked it on 2026-07-30: the blocker was never her availability, it was that nobody
had stated a **policy**. The policy is now **propose, don't apply** — every item here
writes a review file and edits nothing in the dump. That is executable autonomously._

**Propose-only is LIFTED (Emma, 2026-07-30).** Apply fixes directly to
`wikibase/items/*.json`. Do not stop at writing another review document — that was the
old rule and it was followed well past the point where Emma had asked for the actual
change. Still true: where the evidence does not decide a case, say so rather than
guessing, and **verify against the item files after applying** — the derived
`wikibase/analysis/*.tsv` extracts go stale the moment items change.

**An edge lives in TWO places** — the child's `P47`/`P48` *and* the parent's `P20`.
Removing only one direction leaves the edge alive. This bit the Tros unmerge; always
re-verify from the items.

**READ `wikibase/analysis/cycle_policy.md` BEFORE TOUCHING ANY CYCLE.**

**This is not a regular genealogy project.** It is a literary device that links people
across time and space, and it is building a **synoptic mythology** — Greek, Near Eastern,
Egyptian, Trojan, Chinese, Mongol lines integrated into one descent. The cross-tradition
joins are the product, not incidental structure.

**Everything unexpected here that is not an error was imported deliberately by Emma.** The
Emesene route in Muhammad's ancestry, the Genesis 11 patriarchs under Mesopotamian royal
names, the Mongol line descending from the Buddha. Surprising is not evidence of broken.
Do not open general-defect sweeps.

**"Load-bearing" means the ancestors that come through it — depth, upward.** NOT descendant
count. `qa_cycles_load.tsv` scores cycles by descendants lost, which is *width*, which is
the wrong metric and must not be used to rank repairs.

**Repair order, strictly — always prefer the fix that preserves the most connection:**
1. **UNMERGE** an improperly merged record. Both lines survive. This is the default.
2. **DEDUPE** parallel imports. Removes cycles with no edge chosen.
3. **CUT** only if 1 and 2 do not apply, and **never** an edge that is the only link
   between two traditions.
4. **DELETE** only where the loop is genuinely terminal — nothing substantial above it.
   Keep the entry point, drop the rest.

**READ THE ANALYSIS TSVs WITH `quoting=csv.QUOTE_NONE`.** They are written with plain
f-string formatting and never quote anything, but `csv.DictReader` defaults to treating
`"` as a quote character — so a label containing a double quote swallows the rest of the
field and the reader **silently drops rows**. It was dropping **128 of `persons.tsv`'s
107,022**, including `Q153797` "Ghalib born of Fihr", who sits in Muhammad's ancestry.

Every consequence of this was a *measurement* error, not a data error, which is exactly
why it survived: `check_invariants` reported **138 dangling endpoints when the true figure
is 13**, and its own committed baseline listed `Q153797` among the examples — a record
that has always existed. Fixed across all 29 scripts on 2026-08-01 and the baseline
re-taken. **Any figure quoted from these TSVs before that date may be off.**

**SHADOW FILES — always propagate an edit.** 39,527 qids are claimed by more than one
file. `extract_genealogy.py` keeps only the numerically-lowest QID per qid, so editing the
canonical file alone leaves stale shadows that silently revert the fix if that file is ever
vacated. After editing any record, rewrite every file claiming its qid. `shadow_audit.py`
reports disagreements; it must stay at **0**.

**MERGE DIRECTION — after a merge, NO file may still claim the loser's qid.** Vacating a
qid some file still claims lets that file win it and inject its claims; that is what
produced the phantom Cato 2-cycle out of a graph that never contained the edge. Worked
example: `wikibase/analysis/cato_cluster_resolved.md`.
This was first written as "always merge INTO the side that has shadows", which is a proxy
for the real invariant and a bad one: it forbade `Q72434`/`Q72514`, where **both** sides
have shadows, even though repointing makes either direction safe. `merge_cluster.py` now
rewrites every shadow of both sides and then **sweeps all 164k files** asserting nothing
still resolves to a vacated qid. Prefer the lower QID as survivor by convention, not
because the higher one is unsafe.

**A MERGE MUST CARRY THE WHOLE RECORD, not just the genealogy.** The loser's file becomes a
copy of the survivor, so any property only the loser held is gone from the dump. The first
ten merges of 2026-07-31 unioned only `P20/P42/P47/P48/P61` and silently dropped **38
properties** — external ids and, worse, `P56`/`P57` birth and death dates on six people.
They were reported as "strictly additive"; that was true of the graph and not of the
records. Restored by `wiki-scripts/backfill_merged_properties.py`; `merge_cluster.py` now
carries every property the survivor lacks and reports, rather than guesses at, the ones
where both sides differ.

**COUNT TANGLES, NOT CYCLES.** `dump_qa_errors.py` used to iterate `set`s of qid strings,
so Python's per-process hash randomisation changed which cycles its DFS found on every run
— three runs over one unchanged `edges.tsv` gave 45, 50 and 46. It also marked nodes BLACK
on pop, so it only ever found *some* cycles per tangle. **Every "cycles went from X to Y"
number in this file, `devlog.md`, `HANDOFF.md` and `GENEALOGY_QA.md` predating 2026-07-31
is unsound, including the `52 -> 54`.** Fixed 2026-07-31: it now emits one canonical
shortest cycle per strongly connected component, deterministically (five runs byte-identical),
and its totals match `check_invariants.py`'s independent Tarjan. The well-defined quantity is
the **tangle** (an SCC of size > 1) — **35** of them, holding **295** records (2026-07-31,
after the Calavius and Quintus Lepidus dedupes). Verify repairs against
`tangled_components` / `records_in_a_cycle`, never against a cycle count. **These two
numbers go stale on every repair — re-read them from `check_invariants.py`, do not quote
this line.**

**HOW TO VERIFY A REPAIR — one command, not a list of steps.**

```
python wiki-scripts/verify_repair.py --snapshot     # BEFORE: freeze the current edges.tsv
...make the repair...
python wiki-scripts/verify_repair.py                # AFTER: regenerate, then every gate
```

It runs `extract_genealogy.py`, then `compare_tangles.py` (**width** — which SCC partitions
were introduced, removed or reshaped), `compare_depth.py` (**depth** — ancestry lost per
record, the load-bearing one), and `check_invariants.py`, and exits non-zero naming
whichever failed. Merges still go through `wiki-scripts/merge_cluster.py <cluster>`, which
enforces both merge rules above against what actually happened on disk; run
`verify_repair.py` around it.

**`compare_depth` CANNOT TELL SPURIOUS ANCESTRY FROM REAL ANCESTRY.** It measures loss,
and a big loss is *usually* an amputation — but not always. On 2026-08-01 a cut made
`Q88454` fall from **318 levels to 1**, because all 3,525 of her ancestors reached her
through a single edge. Whether that is a catastrophe or a correction depends entirely on
whether the edge was true, which the gate has no way to know:

- if the edge was false, she was inheriting her *husband's* line through a reversed
  parent claim, and losing it is the repair working;
- if the edge was true, the cut just severed a real line.

**So a red `compare_depth` is not automatically "revert", and a green one is not
automatically "correct".** It tells you how much is at stake, not who is right. When it
fires, go and settle the edge on external evidence — and if you cannot, revert, which is
what happened to the two Esthers below.

**A DEDUPE INSIDE A TANGLE WILL TRIP `compare_tangles`, AND THAT IS CORRECT.** It exits
non-zero on *any* change to the SCC partition, and merging a duplicate that sits in a
tangle really does leave that tangle with one fewer member. Read the lists and check the
signature before concluding anything:

- **Expected for a dedupe** — `records newly inside a tangle: 0`, and the tangle reported
  as *introduced* is the *removed* one minus exactly the qids you merged away. The
  `Q72615`/`Q72693` merge showed the Scipio tangle 18 → 17, sole departure `Q72693`.
- **A regression** — anything newly inside a tangle, a tangle whose members you did not
  touch, or a larger largest-tangle.

`compare_depth` has the matching quirk: everything below a shrunken tangle reads as
**exactly −1**, because depth counts a component's size as its contribution. A uniform −1
across many records is arithmetic, not amputation. A real gateway cut looks nothing like
it — see the −273 below. **`verify_repair.py` will not make this call for you.**

**A green `compare_tangles` is not a verified repair.** Against a synthetic `edges.tsv`
missing only the `Q73893 → Q73794` edge — the cut that was applied and reverted on
2026-07-31 — `compare_tangles` reports it clean while `compare_depth` fails with **27,554
records down and a worst loss of 273 levels**. Width said yes, depth said no, depth was
right. That is why the gates run together and why `verify_repair.py` exists: all of these
gates already existed that day, and the ritual for running them lived in prose right here,
which is not a gate. **If `compare_depth` fails, do not lower `--max-loss`** — the edge was
a gateway and the defect is elsewhere in the loop.

**I2 WAS VACUOUS AND IS NOT ANY MORE.** `check_invariants.py` said "self-loops must be
zero, always" and reported 0 unconditionally: its default `--source tsv` reads `edges.tsv`,
and `extract_genealogy.py` drops self-edges before writing it, so the check was
unsatisfiable. Meanwhile 11 records listed themselves as their own parent or child. Fixed
2026-07-31 — the extractor now records what it drops in `qa_self_edges.tsv` and I2 reads
that. All 11 were cut (`cut_edges.py selfloops`, data-driven from that file) and it is
genuinely 0 now. **A gate that cannot fail is worse than no gate**: check any invariant
reporting a perfect score against the source it actually reads.

**WIKIDATA IS THE REFERENCE, NOT GOSPEL.** `qa_cycles_vs_wikidata.tsv` returns
`contradicted` for 16 distinct edges, but in 15 of them the detail reads *"Wikidata records
no link between them"* — an **absence of evidence, not a refutation**, and Wikidata is
incomplete and holds impossible loops of its own. Three of those edges are currently live
and **correct**: `Belus -> Danaus` and `Anchiroe -> Danaus` are exactly the parents
`cycle_policy.md` assigns, and cutting them would sever the cross-tradition join the
genealogy exists to make. They are listed in `PROTECTED` in
`wiki-scripts/propose_tangle_repairs.py` and that tool will never propose cutting them.
Only *"the link the other way round"* — Wikidata recording the same pair with parent and
child swapped — is treated as decisive.

## READ THE CYCLE REVIEW BEFORE PROPOSING ANY REPAIR

**`wikibase/analysis/cycles_review.md`** — all 35 tangles, one section each, every member
listed with its **ancestor count**, descendant count, depth, and whether it reaches
`Q1` Aster. Regenerate with `wiki-scripts/build_cycles_notion.py` after any change to
`wikibase/items/`.

**Notion syncing is central command's job, not this loop's.** Do not push this file to
Notion, do not create or edit Notion pages for it, and do not treat any Notion page as the
source of truth. If a repair needs to be visible outside the repo, that happens through
central command.

- **Every section says `Decision: not made — needs Emma`, and that is the point.** The
  generator states what the data shows and proposes nothing. Repairs were previously
  decided one at a time and justified in commit messages, which left Emma auditing
  decisions after the fact instead of making them. Do not go back to that.
- **`ancestors` is the only column that ranks anything.** Tangle 5 has 29,135 descendants
  and 52 ancestors; tangle 18 has 34 descendants and 6,579 ancestors. Width and depth point
  in opposite directions and depth is the one that matters.
- **Run `wiki-scripts/compare_depth.py` before and after any cut.** It exists because a cut
  on 2026-07-31 passed every other gate while stripping ancestry from 27,569 records.
- **35 tangles is not 71 cycles.** A tangle is a strongly connected component and can hold
  many distinct loops — the 72-record one holds a great many. The "71 cycles" in
  `GENEALOGY_QA.md` and `qa_cycles_proposed.tsv` counted loops, with an enumerator that was
  never stable. Do not present tangle counts under the word "cycles" without saying so.

1. **UNMERGE `Q72786` "Marcus Aemilius Lepidus" — the real defect in the Scipio loop.**
   **NEEDS EMMA: which parentage is the true one.** Investigated 2026-07-31; the diagnosis
   is solid, the choice is not mine.

   `cycle_policy.md` said that if a loop can only be broken by cutting a gateway, the real
   defect is elsewhere — and it is. Not in the Scipio half. `Q72786` carries **three
   separate, individually coherent father+mother couples**:

   | father | mother | both list Q72786 as their child? |
   |---|---|---|
   | `Q73011` M. Aemilius Lepidus (wd Q3622705) | `Q72801` Cornelia | yes — and they are married to each other |
   | `Q73113` M. Aemilius Lepidus | `Q73110` NN wife of M. Aemilius Lepidus | yes — and they are married to each other |
   | `Q73173` M. Aemilius Lepidus, Consul | — | yes |

   A record cannot have three sets of parents. This is the same shape as the worked `Tros`
   example in `cycle_policy.md`, so **UNMERGE is the repair — step 1, the default.** It
   *adds* structure: split, and all three couples keep their child.

   Two further contradictions in the same record, which is why it needs a human:
   - **`Q73173` is the father of `Q73011`.** So `Q72786` is recorded as both `Q73011`'s son
     and `Q73011`'s brother — a collapsed generation, not just a duplicate.
   - **`Q72789` "NN (Wife of Marcus Aemilius Lepidus)" lists `Q72786` as both her spouse
     and her child.**

   **Why this is the loop:** the `Q72801` Cornelia → `Q72786` edge is one of those three
   parent-couples, and it is what drags the Scipiones down into the Aemilii. Split `Q72786`
   correctly and the loop opens **without touching the Scipio half at all** — no gateway
   severed, nothing detached from Aster.

   What is needed from Emma: **which of the three couples is `Q72786`'s real parentage**,
   and what the other two Lepidi should be called once separated. Naming is hers per the
   `Tros` precedent. Do not guess Roman prosopography.

   **A fourth Lepidus now sits on this decision (added 2026-07-31 by the `Q72615`/`Q72693`
   merge).** The merged Quintus Aemilius Lepidus inherits **two fathers**, `Q72786` and
   `Q144279`, both labelled "Marcus Aemilius Lepidus". That conflict was not created by the
   merge — both edges were already in `edges.tsv`, on `Q72693` — it is just now visible on
   one record. **It cannot be settled separately from this item:** `Q144279`'s other child
   is `Q73011`, which is one of the three fathers `Q72786` claims, so merging `Q72786` and
   `Q144279` would close a 2-cycle. Either they are distinct men and one of the two
   father-edges is wrong, or `Q72786` is the corrupt record this item is already about.

   Run `compare_depth.py` before and after regardless. The `Q73893 → Q73794` cut was applied and then **reverted the same day**: it
   was chronologically correct but it was the *sole upward gateway* for the whole Scipio
   line. Measured: `Q73299` Scipio Africanus went from **267 ancestors deep to 4**,
   `Q73794` from **263 to 0**, and the severed chain ran all the way to **`Q1` Aster**.
   `cycle_policy.md` names this case exactly — go find the defect elsewhere in the loop.
   The loop is
   `Q73794 → Q73692 → Q73569 → Q73443 → Q73293 → Q73128 → Q72957 → Q72801 → Q72786 →
   Q72615 → Q72434 → Q73893 → Q73794`.
   The likely culprit is the *downward* half, not the Scipio half: `Q72801` Cornelia
   (wd Q100804879) has **three fathers** — `Q72957`, `Q73425`, `Q73017` — and it is her
   `Q72957` edge that drags the Scipiones back down into the Aemilii. Check whether
   Cornelia is a merge of two women, or whether `Q72957 → Q72801` is simply wrong. Also
   suspect `Q72786`, which had four fathers and three mothers.
   **Do not cut anything here until you have measured ancestral depth before and after.**

2. **THE TWO ESTHERS — genuinely undecidable from the dump. NEEDS A SOURCE OR EMMA.**
   `Q88454` "Esther bat Sahlan ben Abraham" and `Q90982` "Esther bat Yosef ben 'Amram
   haDayyan al-Sijilmasi" are recorded as **each other's mother**. One of the two edges is
   false. Both readings are naming-consistent:

   - **A:** Esther *bat Sahlan* married Yosef → their daughter is "Esther *bat Yosef*"
   - **B:** Esther *bat Yosef* married Sahlan → their daughter is "Esther *bat Sahlan*"

   Under either, **each woman is correctly named for her own father and both recorded
   father-claims hold.** The patronymics confirm the fathers and settle nothing about the
   direction — which is exactly why `fix_mutual_parent_pairs.py` finds spouse-coparent
   evidence on *both* sides and refuses to act. **I cut it under reading A and reverted:**
   the claim that the patronymics decided it was wrong, and the depth gate's reaction
   (`Q88454` 318 → 1) is consistent with *either* reading, so it settles nothing either.
   Do not re-cut this without an external source.

   **Also still open, and neither is a merge:** the `WRONG-PARENT-EDGE` on `Q72834` (two
   fathers who are brothers, `Q72984` wd `Q929498` and `Q148066` wd `Q897091`), and the
   four remaining mutual-parent pairs `fix_mutual_parent_pairs.py` skips —
   `Q119481`/`Q124343` (different sexes and distinct wd ids, so **not** the merge the tool
   suggests), `Q18066`/`Q32705`, `Q29144`/`Q29148`, `Q73530`/`Q73653`.

   **`fix_mutual_parent_pairs.py`'s two reporting defects are FIXED (2026-08-01).**
   Symmetric spouse-coparent evidence no longer claims "two records of one person that
   need a MERGE" — it now says the signal decides nothing, and where the pair is
   demonstrably two people (distinct Wikidata ids, or different recorded sex) it says so
   and says **NOT a merge**. `Q119481`/`Q124343` now reads correctly. It also skips pairs
   with an endpoint absent from `persons.tsv` instead of inferring a family for a record
   that does not exist. It still repairs 0 of 5 — every remaining pair genuinely lacks
   direction evidence, which is the correct answer, not a failure.

3. **Work the remaining cycles under the repair order above.** Start from
   `wikibase/analysis/qa_tangle_repairs.md`, which is generated and ranks all 35 tangles.
   34 are `REVIEW`: no Wikidata evidence decides them, mostly because "contradicted" there
   means *Wikidata records no link*, which is an absence and not a refutation. Unmerge
   candidates first.
   The five remaining cycles of length >= 20 are all Roman, sharing the Q61957/Q62255/
   Q63192/Q63747/Q70152/Q138467 stretch — likely the same repeating-cognomen collision that
   produced the short Roman 2-cycles. Emma: preserve the Roman material; unmerge, do not
   delete.

4. **Fix the one-sided edges.** `wikibase/analysis/edge_symmetry.txt`, rebuilt 2026-08-01:
   **97.1%** of edges are declared on both sides; **3,762** are one-sided. (The older
   96.3% / 4,723 figures were inflated — the scan compared raw qids without canonicalising
   through `redirects.tsv`, and 961 were never a defect.)

   `edge_symmetry_classified.tsv` splits all 3,762 by what their endpoints are:

   - **`ORPHAN` — 0 left.** All 14 cut 2026-08-01, every gate green, **zero records lost
     depth**. `dangling_endpoints` 13 → 4.
   - **`GAP` — 219. DO NOT CUT THESE.** An endpoint has **no item file**, but other records
     record a family around it — parents *and* children. That is a **real person whose file
     is missing**, not a nonexistent one. Four records, and they are not small:
     **`Q74656` has 144 children and 2 parents; `Q75282` has 59 children** and sits between
     the Titans and Melaneus; `Q54196` and `Q78402` are the others.
     **The repair is to CREATE the missing record, not delete its edges** — and that needs
     a name, which is Emma's. *(Learned by cutting all 233 as one batch: `compare_depth`
     failed at −10 levels, Melaneus and Aeneus lost the Titan line entirely, reverted.)*
   - **`PHANTOM` — 1,050. Analysed 2026-08-01, NOT acted on. It has the same shape as
     GAP, and the connectivity test was run BEFORE cutting this time.** 430 distinct shell
     records; **269 of them are connectors** with both parents and children, `Q132255`
     alone having **79 children**. **861 of the 1,050 edges touch a connector and are not
     safe to cut.** The other 189 touch only leaf/root shells.

     **But the leaf shells are not junk either.** Sampled: `Q135293` is **the father of
     Darius I of Persia**; `Q108512` is the father of Al-Qasim ibn an-Nafs az-Zakiyya;
     `Q136745` is a child of Archelaus. They are **unnamed placeholder people** — empty
     items carrying only `P39` — and deleting their edges erases the statement *this person
     had a father*, which is information rather than noise.

     **The decision, and it is genuinely open:**
     - **ADD the missing side** — write the mirror claim into the shell. **This provably
       cannot change `edges.tsv`**, because the graph is built from the UNION and the edge
       is already in it. Purely additive, no data lost, and it removes the silent-failure
       hazard this whole item is about.
     - **REMOVE the present side** — changes the graph and destroys a recorded
       relationship.

     ADD is graph-neutral and REMOVE is not, which argues for ADD. **The counter-argument
     is the one this item already states:** some one-sided edges are deletions that only
     got half done, and adding would cement an edge someone meant to remove. Nothing in an
     empty shell distinguishes the two. **Needs Emma**, or a rule from her about which way
     placeholder people should go.
   - **`BOTH-REAL` — 2,479.** Both endpoints substantive. **The real judgement calls** and
     what the do-not-blanket-add warning is about.

   Decide per record whether the missing side should be added or the present side removed;
   do NOT blanket-add, since some one-sided edges are deletions that only got half done.

5. **NAME THE FOUR MISSING RECORDS — needs Emma.** `Q74656`, `Q75282`, `Q54196`, `Q78402`
   have no item file, yet 219 edges reference them and they hold 200+ recorded
   relationships between them. They are holes in the dump where the surrounding family
   survived. Creating them is one `add_bridge_edges.py`-style operation each; deciding
   *who they are* is not something the dump answers.

---

## AWAITING EMMA — reports written, decisions open

> ### ⛔ NOTION WINS. READ IT BEFORE TRUSTING THIS SECTION.
>
> **Emma, 2026-07-31: "Notion wins pretty much all the time as per central command rules."**
> Where this file and the board disagree, **the board is right and this file is stale.**
>
> The board arrives as two synced files at the repo root — **`notion-open-questions.md`**
> (the order.life board section) and **`notion-work-loop.md`** (the Work Loop page,
> bidirectional). Read both before acting on anything in this section or on any report's
> "needs Emma" verdict.
>
> **Why this warning exists.** Four of the five decisions below sat *answered by Emma on
> the Work Loop page* for a day while this file went on saying "nothing here has been acted
> on", because no route existed from that page to any repo file. The patriarch overlay was
> re-asked repeatedly after she had already answered it. A stale "needs Emma" is not a
> neutral placeholder — it makes the loop interrogate her about settled things and stalls
> the work behind them.
>
> **Never push to Notion from this repo.** Not with the Notion MCP tools, not by extending
> `build_cycles_notion.py`. The hub's `sync_board.py` is the only Notion writer. Generate
> `cycles_review.md`; the hub publishes it. To answer Emma, **write into
> `notion-work-loop.md`** and let the sync carry it up.

**Read the scope note above first.** These reports were written as defect reports before
Emma set the cycles-only scope and said much of what looks wrong is intentional. Treat
their "DATA ERROR" verdicts as *unconfirmed* until she rules on each — R1 was ruled
intentional and that invalidated eight of that report's twelve proposed merges. **Do not
apply anything from these; do not extend them.**

**DECIDED 2026-07-30 — R1: the Emesene route in Muhammad's ancestry is 100% intentional.**
The splice stays. `adnan_merge_proposed.md` is updated; M5–M12 and the "Banu Adnan is
filler" verdict are withdrawn.

1. `planning/lineage_bridges_proposed.md` — **Adam→Genghis: DONE 2026-07-31, both A1 and
   A2** (`wiki-scripts/add_bridge_edges.py adam-genghis`). Emma answered "Both?".
   **`Q37401` Genghis Khan now reaches `Q1` Aster, with 1,272 ancestors where he had
   none.** 403 records gained depth, 0 lost, total **+173,295**; no tangle introduced.

   **Two things Emma should look at, neither of them guessable from the dump:**
   - **The A1 attachment point is a judgement call, and I took the report's.** Khaidu
     `Q53399` is attached under `Q153230` on Rashid al-Din's descent (Bodonchar → Buqa →
     Dutum Menen → Qaidu). The *Secret History* puts him one generation lower, under
     `Q153225`. Both placeholders are unlabelled with no date and no wd id, so **nothing
     in the dump distinguishes them.** Moving one edge down one node is the entire
     correction if she prefers the other reading.
   - **Khaidu now has two fathers**, `Q153230` (Borjigin) and `Q200000` (haplogroup) —
     the direct consequence of "both". Note this **deviates from the dump's own
     precedent**: `Q87862` Youxiong has the haplogroup `Q54433` as its *only* father. If
     the convention is meant to be one-or-the-other, drop whichever edge she prefers.

   **Deliberately NOT done:** retiring the 14 placeholder nodes from `Q153225` down. That
   is a DELETE — repair-order step 4 — and it was never approved. The bridge does not
   depend on it.
   **Still genuinely open:** **Jimmu↔Heo** (strike it, or substitute B1 Prince Junda →
   Yamato no Ototsugu, or drop it) and **Kosala→Heo** (held behind the Kosala dedup, then
   C1). Neither was on the Work Loop page's list.
2. `wikibase/analysis/epic_vs_dump.md` — eight rows in "which side moves".
   **Chapter 181's "bore him ten sons": DECIDED 2026-07-31 — the DATA moves, not the prose.**
   Emma: *"Uhh yeah the ten sons exist"*. The chapter stands; the nine missing sons get
   recorded in the dump. **Do not rewrite the chapter.** Note the naming problem is real and
   unsolved — the report says the data fix "means inventing nine named sons", so before
   creating anything, go and find whether Garakguk-gi actually names them. **If the sources
   name them, record those names; if they do not, that is a second question for Emma, not a
   licence to invent.**
   Row 1 of the eight (the Noah relabel) is **withdrawn** — see item 3.
   The other six rows are still unanswered.
3. ~~`wikibase/analysis/patriarch_overlay.md`~~ — **DECIDED 2026-07-31 by Emma: deliberate
   euhemerism. "the mesopotamian ones is completely intentional euhemerism".** The nine
   records keep their Mesopotamian royal labels; the fix is *none*. **The relabel proposal
   is dead — do not execute it, and do not re-open this.** It should never have been listed
   as open: `CLAUDE.md` has named it a confirmed-deliberate import since 2026-07-30 and
   this queue kept asking anyway. Emma had recorded the decision repeatedly. Details in
   `patriarch_overlay.md`. Still open and unaffected: the position-only rows (`Naram-Ilum`,
   `Shu-Sin`) and the `Kanʿān` generation error, which are structural, not naming.
4. ~~`wikibase/analysis/adnan_merge_proposed.md` — M3~~ — **DONE 2026-07-31.** Emma:
   *"You merge them lol"*. All three Adnan records merged into `Q65555` (cluster `adnan`).
   Every gate green, including `compare_tangles` for the first time this session — the
   Adnan records were not in a tangle, so nothing moved. **Zero records lost depth and 654
   gained**, total ancestral depth **+158,370**: `Q86433`'s 434-ancestor route toward
   Abraham is now reachable by the 8,527 descendants that hang off `Q65555`, which is
   Muhammad's line. This is what "merges only ever add ancestry" looks like when it is
   actually measured.
   **Two open residues, neither hidden:** the survivor now has **four parents**
   (`Q66382`, `Q66385`, `Q66394`, `Q86503`) — `Q66385` "Imaam 'Udd" and `Q66394` "Udd son
   of Umaisi" look like one man, which is the untraced `'Udd`/`Humaisi` tangle the report
   itself flags; and the survivor's **label is still `'Adnaan Bin Imaam 'Udd`** while the
   record now carries wd `Q22338875` whose name is simply *Adnan*. Relabelling is Emma's
   per the `Tros` precedent — flagged, not done.
5. The Kosala dedup — three parallel imports of one king list — gates both C1 above and
   any further Indian-line work. **Still open**; it was not on the Work Loop page's list.

6. ~~Naming the primordial half of `Q74698` Tros~~ — **ANSWERED 2026-07-31 by the dump
   itself, not by Emma.** She asked "What? Explain better", and the better explanation is
   that **there is nothing left to name**: the unmerge was already carried out. `Q74698` is
   labelled **Uranus** (aliases *Uranus / Caelus / Ouranos*), its parents are **Aether and
   Dies** — Hyginus's parentage for Caelus — and its 59 children are the entire Ouranos
   roster (Titans, Cyclopes, Hecatoncheires, Gigantes, Erinyes) with **zero Trojan claims
   left**. The four mythic cycles are gone; none of those records is in a tangle.
   **`Tros → Ops` was never spill** — Ops is Rhea, `Ouranos → Rhea` is correct, and it has
   been moved from `PENDING_UNMERGE` (where it was wrongly marked blocked-on-Emma) into
   `PROTECTED`. Full write-up at the top of `cycle_policy.md`.

---

## DEFERRED — do NOT interleave with the live work-loop

_(none — the Wikibase backfill is DONE; wiki gone, snapshot frozen + committed, 164,536
items in repo. See devlog 2026-07-01. The `fill_missing`/`dump` scripts need a live wiki
and can no longer run; all downstream analysis reads the local dump.)_

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`3 * * * *`),
  auto-flush (`15 * * * *`), status-report (`42 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
  (Schedules corrected 2026-07-30 to match the `autonomous-loop` skill and what is
  actually running; the half-hourly figures this line used to give were never the
  skill's cadence. Crons are session-local — they die with the session, so a fresh
  session always creates them.)
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
