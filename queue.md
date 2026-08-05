# order.life — Autonomous Work Queue

> ## ⛔ READ FIRST — Emma, 2026-08-01. THE TASK IS REMOVING THE LOOPS. NOTHING ELSE.
>
> **"There are 34 loop clusters. I don't give a shit about deduplication. I only care
> about removing the loops. I don't believe they should be done with scripts because
> they're easy to do. Basically every single ancestral loop takes maybe removing two lines.
> This isn't an algorithmic task."**
>
> **What went wrong in the 2026-08-01 session, so it is not repeated:**
>
> 1. **Not one of that session's last ten merges was in a tangle.** Maratton, Isabel de
>    Polanco, Anna Xylaloe, Julia Maesa, the four Chinese royal pairs — all outside every
>    cycle. A scan produced 1,712 "same-role" defects and I worked the list instead of the
>    loops. Deduplication is not the job.
> 2. **I built tools instead of making decisions.** `verify_repair.py`,
>    `cheapest_cycle_break.py`, `same_role_parents.py`, the edge classifier, the I4
>    pre-check, a CSV fix across 29 scripts — against roughly twenty pairs actually merged.
> 3. **Every check rescans 164,000 files.** `verify_repair` grew from ~10 to ~35 minutes and
>    was run about fifteen times. That is most of the wall clock, spent on four-pair
>    batches. **Do not run a full-dump scan to justify a two-line edit.**
> 4. **I never once looked a person up on Wikidata.** The two Esthers, the 'Udd/Adnan
>    parentage and Elagabalus-vs-Malchus were all filed "UNSAFE-TO-GUESS" on the grounds
>    that *the dump* cannot decide them — when birth and death dates on Wikidata would
>    settle several in minutes. **Look up the dates. That is what decides a loop.**
>
> **How to actually do this:** take one tangle from `wikibase/analysis/cycles_review.md`,
> look its records up on Wikidata for dates, find the one edge that is chronologically
> impossible, remove it from both sides (`P47`/`P48` on the child, `P20` on the parent),
> move to the next. One tangle, one decision. `compare_depth.py` before cutting is still
> worth it — a cut that costs hundreds of generations is a gateway and the defect is
> elsewhere — but it does not need the full ritual for every edit.
>
> **State at handoff:** 34 tangles, 283 records trapped, down from 36/299. The one
> substantial win was the Adam→Genghis bridge: Genghis Khan went from 0 ancestors to 1,272
> and now reaches Aster.
>
> **State at end of 2026-08-02, re-read from `check_invariants.py` after regenerating
> `edges.tsv`: 8 tangles, 80 records trapped, largest tangle 15.** Every one of the 8 has a
> section in `cycles_review.md` and a numbered item below; **none of the 8 is a two-line
> edit waiting to be made.** They are the residue — each needs either a ruling from Emma or
> an external stemma. See the roster under ACTIVE.
>
> **2026-08-05 — FOUR OF THOSE RULINGS NOW EXIST. Emma was simply asked, in one round,
> and answered all four.** Items 1, 2, 3 and 16 are no longer open questions:
>
> | item | ruling |
> |---|---|
> | 3 — Daksha rebirth | **SPLIT into two records** (both copies) — dissolves tangles 2 and 4, **28 records** |
> | 2 — Roman Republic | **Attach `Q73308` to all three** of Aeneas, Iulus, Romulus — **103 records** regain Aster |
> | 16 — phantom one-sided edges | **ADD the missing side, always** — **1,050 edges**, provably graph-neutral |
> | 1 — the Lepidus unmerge | **Emma is researching it herself.** Hands off; do not ask again |
>
> **The lesson, and it is the one that matters for how this file is worked:** these had
> been sitting as "BLOCKED / NEEDS EMMA" for days. Nobody had asked her. Every one of the
> four took a single question. **When an item genuinely needs a ruling, ask her with
> `AskUserQuestion` — do not park it in this file and move on.** Parking it is what
> produced a queue that reads as fully blocked while holding well over a thousand records
> of ordinary executable work.


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

### THE 8 REMAINING TANGLES, AND WHICH ITEM EACH IS (2026-08-02, 80 records)

Re-read from `cycles_review.md` after regenerating `edges.tsv`. **Every one is already
diagnosed and written up below.** None is waiting on analysis; each is waiting on either a
ruling from Emma or a source that is not Wikidata.

| # | tangle | records | item | what it waits on |
|---:|---|---:|---:|---|
| 1 | Marcus Aemilius Lepidus | 15 | 1 | **Emma is researching it herself** (2026-08-05) — hands off |
| 2 | Prachetas (10 sons) | 14 | 3 | **NOTHING — RULED 2026-08-05: split Daksha. Go do it.** |
| 3 | D. Ausindo Ximeno | 14 | 10 | a *Livro de Linhagens* stemma |
| 4 | Aditi Kashyapa | 14 | 3 | **NOTHING — same ruling, the second copy. Go do it.** |
| 5 | Gaius Servilius | 8 | 11 | a Servilian stemma, or Emma's step-4 collapse |
| 6 | Joan ferch Ieuan ap Rhys | 7 | 9 | Bartrum's *Welsh Genealogies* |
| 7 | Sekhemre Sankhtawy Neferhotep III | 6 | 8 | Turin King List / Ryholt |
| 8 | Esther bat Sahlan ben Abraham | 2 | 12 | a source; cut once and reverted |

**Tangles 2 and 4 are the Daksha rebirth, and on 2026-08-05 Emma ruled: SPLIT.** She did
not accept them as doctrine — see item 3 for the ruling and the exact procedure. They are
**28 records of ordinary executable work**, not a philosophical question, and they are the
single largest unblocked win on this table.

**THIS TABLE'S "WAITING ON A RULING" FRAMING IS OUT OF DATE AS OF 2026-08-05.** Four
rulings were obtained from Emma directly, in one round, by asking her (items 1, 2, 3, 16).
Tangles 2 and 4 are ruled and executable; item 2's Roman reattachment is ruled and
executable; item 16's phantom class is ruled and executable; tangle 1 is Emma's own
research and is hands-off. What is genuinely still waiting is only what needs an
**external stemma** — tangles 3, 5, 6, 7 (items 10, 11, 9, 8) — and tangle 8 (item 12).
**Do not report this repo as blocked, and when something really does need Emma, ask her
with AskUserQuestion instead of parking it here.**

**The inversion class is DONE** — Emma ruled on it 2026-08-02 and it took five tangles and
21 records off this table in one pass. See the devlog entry; the cut set is
`cut_edges.py inversion-class`.

1. **UNMERGE `Q72786` "Marcus Aemilius Lepidus" — the real defect in the Scipio loop.**

   > **EMMA HAS TAKEN THIS ONE (2026-08-05, asked directly).** Her words: *"I do the
   > research. I'm pretty sure there's something easy to find that we just haven't seen
   > yet."* So this is **BLOCKED-ON-USER-ACTION, owner Emma**, not a ruling waiting to be
   > prompted for. **Do not ask her about it again, do not guess the prosopography, and do
   > not work around it by cutting the Scipio half.** Leave tangle 1 (15 records) standing
   > until she brings back the source. The diagnosis below is what she is researching
   > against — keep it accurate, add to it if you find dates, but make no edit to
   > `Q72786` or any of the three couples.

   Investigated 2026-07-31; the diagnosis is solid, the choice is not mine.

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

2. **⭐ THE ROMAN REPUBLIC IS FLOATING — 103 records, and the reattachment is RULED.**

   > **RULED BY EMMA 2026-08-05, asked directly.** Her words: *"I am pretty sure we can
   > just connect it with all of them. I don't understand why this is a decision."*
   >
   > **So it is not a decision any more, and it must not be re-raised as one.** Attach
   > `Q73308` to **all three** of `Q90257` Aeneas, `Q74644` Iulus and `Q74518` Romulus.
   >
   > **The one fact that made it look like a decision, recorded so nobody re-litigates
   > it:** Aeneas is an ancestor of both Iulus and Romulus, but **Iulus and Romulus are
   > not in each other's ancestry** — they are collateral, not a chain. (Measured
   > 2026-08-05 from `edges.tsv`: Romulus has 781 ancestors including `Q90257`, Iulus has
   > 827 including `Q90257`, neither contains the other; all three reach `Q1` Aster.) So
   > "all of them" cannot be satisfied by one edge to the lowest of the three; it means
   > `Q73308` carries **three parent edges**. That was Emma's instruction, taken literally,
   > and it is coherent with CLAUDE.md rule 1 — integrating several ancestries into one
   > descent is the product here, not a defect.
   >
   > **THEREFORE: `Q73308`'s parents are PROTECTED.** Add all three to `PROTECTED` in
   > `wiki-scripts/propose_tangle_repairs.py` and exempt `Q73308` from
   > `qa_same_role_parents.tsv` (item 13) — a multi-father record is exactly what that
   > sweep is built to flag, and this one is deliberate. **Any future session that
   > "repairs" `Q73308` down to a single father is reverting an Emma ruling.**
   >
   > **How to apply it** — remember an edge lives in TWO places: write `P47` on `Q73308`
   > for each of the three, AND `P20` on each of `Q90257`, `Q74644`, `Q74518` naming
   > `Q73308`. Propagate to every shadow file claiming any of those four qids
   > (`shadow_audit.py` must stay at 0). Run `verify_repair.py --snapshot` before and
   > `verify_repair.py` after; the expected result is **103 records regaining their route
   > to `Q1` Aster and no new tangle**. If a tangle appears, one of the three edges closes
   > a loop — report which, do not silently drop it.
   >
   > If Emma later prefers a single father, it is one edit: keep `Q74644` Iulus, drop the
   > other two.

   **The cut is DONE (2026-08-02, `cut_edges.py licinius-varus-collision`).** What is left
   is only the reattachment.

   Found 2026-08-02 while working the 71-record tangle — a third of everything then
   trapped.

   `Q73308` is labelled **"Licinius Varus"**, alias `Licinius /Varus/` — GEDCOM surname
   slashes, **no Wikidata id**. The dump records it as a child of `Q136506` **Flavia Julia
   Constantia** (wd `Q238023`, d. 330, Constantine's sister) and `Q73455` **Licinius** (wd
   `Q184549`, the emperor). Beneath it hangs the entire Republican Roman block:

       Q73308 Licinius Varus -> Q73140 Gaius Licinius Varus -> Q72966 Licinia Varus
         -> Q72807 Publius Mucius Scaevola (b. 300 BC) -> ... -> the Mucii Scaevolae,
            the Licinii Crassi, Pompey the Great, Sextus Pompey, Asinius Pollio

   **Six centuries in one edge**, and it is what closes the 71-record tangle: the Republic
   descends from the imperial house, which descends from the Republic.

   **Wikidata settles the parentage outright: `Q238023` Constantia has exactly ONE child,
   `Q166731` Licinius II — and the dump already holds him correctly as `Q136818`** (b. 315,
   d. 326), with the same father and mother. So `Q73308` as a *second* son of that couple is
   a name collision on *Licinius*, and nothing is lost by removing it: her real son is
   already there.

   **What it cost, measured after applying:**

   | | |
   |---|---:|
   | tangles | 14 → **13** |
   | records in a tangle | 173 → **102** |
   | largest tangle | 71 → **15** |
   | **records that lost their route to `Q1` Aster** | **103** |

   Those 103 are **the Roman Republic** — `Q138505` Gnaeus Pompeius Magnus, `Q138506`
   Sextus Pompey, `Q139671` Gaius Asinius Pollio, the Scaevolae, the Licinii. Their *only*
   route to Aster today runs through this false edge, i.e. **the Republic currently reaches
   Aster by descending from its own remote descendants.**

   **DO NOT GO LOOKING FOR HIS ANCESTRY. THERE ISN'T ANY. Emma, 2026-08-02.**
   `Q73308` carries a Geni id, `P62` = `6000000030478073233`, and **no Wikidata id**. That
   Geni id is bait: **he has no ancestry on Geni — none.** Do not fetch Geni for this
   record, do not open the profile, do not treat the id as a lead. The record's only
   recorded parents were ever the Constantia/Licinius pair that was cut on 2026-08-02 as a
   name collision, and there is no source anywhere that supplies him with different ones.

   The structural reading agrees: `Q73308` and his son `Q73140` are the **only two** of the
   103 floating records from the `6000000030478` Geni block — the same import that produced
   `Q73455` the emperor Licinius. The other 101 come from dozens of unrelated imports. The
   pair is a two-record seam stitching the late-imperial import onto the Republican one,
   and the collision happened at that seam.

   **So this is not a research task and cannot become one.** There is nothing to look up.
   Where the Roman Republic attaches is Gaiad material and Emma's alone.

   **THE OPEN QUESTION, and it is the whole of what remains here: where does the Roman
   Republic attach?** The 103 sit outside Aster right now. **They hang from exactly one
   record — `Q73308` itself — so this is one edge, not 103 decisions:** give `Q73308` a
   father and the entire block follows.

   The dump already carries the right Roman route, unused by these records: `Q90257` Aeneas
   the Dardanian reaches Aster with 29,153 descendants, `Q74644` Iulus gens Julia 28,812,
   `Q74518` Romulus 28,671 — and **none of the 103 are among their descendants**. Rome here
   is two populations: 28,812 attached through Troy properly, and 103 that were attached
   through the collision.

   So the choice is which Trojan/Julian record carries the join, and whether `Q73308` keeps
   its "Licinius Varus" label once it is no longer Constantia's son. That is Gaiad material
   and naming, which is Emma's per the `Tros` precedent. **Do not guess it.**

3. **⭐ THE PURANIC REBIRTH OF DAKSHA — RULED: SPLIT INTO TWO RECORDS.**

   > **RULED BY EMMA 2026-08-05, asked directly: "Split Daksha into two records."**
   >
   > This **overrides the recommendation written in this item below**, which said "do not
   > split Daksha — the tradition's whole point is that the two are one person," and which
   > offered a non-descent property as the only option that removed the loops without
   > denying the doctrine. Emma was shown that option, and shown that splitting
   > contradicts the tradition, and chose the split anyway. **That is her call as author
   > and it is now the instruction.** Do not re-open it, do not propose the
   > alias/non-genealogical-property version again, and do not treat the text below as
   > still live where it conflicts.
   >
   > **What to do.** `Q153390` "DAKSHA (reborn as DAKSHA) Prachetas" carries two fathers:
   > `Q49634` (first birth) and `Q1955` the Prachetas (rebirth). Split it into:
   > - **Daksha I** — keeps `Q49634` as father, keeps the children of the first life
   >   (above all `Aditi`), and keeps the qid `Q153390`.
   > - **Daksha II** — a NEW qid, father `Q1955` the Prachetas, carrying whatever the
   >   second life is recorded as doing. Label it so the relationship is legible
   >   (e.g. "Daksha, son of the Prachetas") — **final naming is Emma's** per the `Tros`
   >   precedent, so flag the placeholder rather than treating it as settled.
   >
   > **Do it in BOTH copies.** This genealogy is imported twice — the `Q153xxx`/`Q19xx`
   > block and the `Q160xxx` block are the same figures, and only splitting one copy
   > leaves the other tangle standing. Find the `Q160xxx` counterpart of `Q153390` first
   > and split it the same way in the same pass.
   >
   > **Expected result: tangles 2 and 4 both dissolve — 28 records, ~13% of everything
   > still trapped.** `compare_tangles` should show both SCCs removed with **0 records
   > newly inside a tangle**; `compare_depth` should show no amputation, because the split
   > is additive — every edge that existed still exists, on one of the two records. **If
   > `compare_depth` shows real loss, the split dropped children on the floor** — that is
   > a bug in the split, not a judgement call. Snapshot with `verify_repair.py --snapshot`
   > first, propagate to every shadow file, keep `shadow_audit.py` at 0.
   >
   > The dedupe of the two copies is a SEPARATE, still-open task and does not remove
   > either loop — do the split first, dedupe after, never both in one commit.

   Found 2026-08-02. Tangles 3 and 5 — **28 records, 13% of everything still trapped** —
   are the same Puranic genealogy imported twice, and in both copies **every single edge is
   canonical**:

       Daksha → Aditi        (Aditi is Daksha's daughter)
       Aditi + Kashyapa → Surya/Vivasvan
       Surya + Sanjna (daughter of Tvastar) → Yama
       Yama/Mrityu → Sunita   (Sunitha, daughter of Death)
       Sunita + Anga → Vena → Prithu
       Prithu + Archis → Vijitashva → Havirdhana → Prachinabarhi → the Prachetas
       Prachetas → Daksha     ← the ring closes here, and the tradition says so

   **The dump states it outright.** `Q153390` is labelled **"DAKSHA (reborn as DAKSHA)
   Prachetas"**, and it carries **two fathers** — `Q49634` for the first birth and `Q1955`
   the Prachetas for the second. The Puranas have Daksha, son of Brahma and father of
   Aditi, die and be reborn as the son of the Prachetas, who are his own descendants
   through Aditi. The loop *is* the doctrine.

   **This is CLAUDE.md rule 1 exactly: surprising is not evidence of broken.** Do not cut
   either ring, and do not split Daksha — the tradition's whole point is that the two are
   one person.

   **What is actually open, and it is a modelling question rather than a data one:**
   - **accept them** — mark both tangles permanent so no future session re-investigates
     them, as happened repeatedly with the patriarch overlay; or
   - **represent the rebirth as something other than descent** — keep Daksha's first
     parentage (`Q49634`) as his `P47` and record the Prachetas rebirth as an alias, a
     note, or a non-genealogical property. That removes both loops without denying
     anything the tradition says; or
   - **split Daksha into two records**, which does contradict the tradition.

   Only Emma can pick. The second option is the only one that both removes the loops and
   keeps the doctrine, and it needs a property that is not `P47`/`P20`.

   **Also: the two copies duplicate each other** — the `Q153xxx`/`Q19xx` block and the
   `Q160xxx` block are the same figures. That is a dedupe, and merging them would not
   remove either loop.

4. **ONE CUT TO SANITY-CHECK IF YOU DISAGREE — Brahma and the eleven Rudras
   (2026-08-02, applied).** Tangle 15 was cut on the reading that `Q160946` "11 Rudras" is
   the **Kashyapa-and-Surabhi** set of the Vishnu Purana — its mother in the dump is
   `Q160966` **Surbhi** — and therefore Brahma's descendant, not his parent. Brahma keeps
   `Q160947` **Gobardhan Vishnu**, his canonical birth.

   **The reading I rejected, in case it was yours:** in Shaiva cosmology Shiva *does*
   generate Brahma, and a Shaiva/Vaishnava synthesis is exactly the kind of cross-tradition
   join this project exists to make. I ruled it out because the record is the *eleven*
   Rudras with a named father and mother, not Rudra-Shiva the creator. **If the intent was
   the Shaiva reading, this cut is wrong and is one revert** — `cut_edges.py`, cut set
   `brahma-rudras`.

6. **TWO RESIDUES FROM THE DEIMACHUS UNMERGE — small, precise, and not hidden.**
   The unmerge landed on 2026-08-01 and dissolved tangle 15, but the existing tools cannot
   write two of the claims it implies:

   - **`Q200002` has its father `Q131902` Neleus but not its mother `Q133062` Chloris.**
     `add_bridge_edges.py` writes `P47` only. The claim is true and attested (wd
     `Q1183222`'s mother is wd `Q28122362` = Chloris) and is simply unrecorded.
   - **`Q75123` still carries BOTH Wikidata ids**, `Q1183226` *and* `Q1183222`, and
     `Q200002` carries none. No tool here writes `P61`. **This is a re-merge hazard** —
     the duplicated id is exactly the signal that found the defect, so leaving it invites a
     later session to re-merge them.

   Neither is worth a new script on its own; both should go in the next time anything
   touches `P48`/`P61`.

7. **DUPLICATES SURFACED BY LOOP WORK — real, deliberately not merged.** Every one was
   found while cutting a loop, and in each case the merge would NOT have broken the loop,
   which is why they are here and not done. Scope this session is loops.

   - **The Pinarii, tangle 19 (2026-08-01).** Wikidata has a two-generation family:
     `Q93953755` Pinarius, Caesar's brother-in-law, and his son `Q382127`, which carries
     **both** labels *Lucius Pinarius* and *Lucius Pinarius Scarpus*. The dump spreads that
     one son over three records — `Q78264` (holding the wd id), `Q78108` and `Q77955`
     (same label, no wd id) — and gives him **two wives who are the same woman**:
     `Q137708` "Julia Major" and `Q78267` "Julia Caesaris Major" have identical parents
     `Q73029`/`Q73026`, so Lucius Pinarius is married to a second copy of his own mother.
   - **Arsenda de Cabrera, twice (2026-08-02).** `Q118293` "Arsenda de Cabrera" carries
     wd `Q21126905`, her real parents `Q123444`/`Q123448`, her husband Ermengol VI and her
     son Ermengol VII. `Q104371` "Arsende de Cabrera" carries **no wd id** and the *same*
     husband and son. The loop it sat in was cut instead, because merging would not have
     broken it — the survivor keeps the false father-claim either way.
   - **Zebudah, twice (2026-08-02).** `Q4626` and `Q60222` share the label, the Wikidata
     id `Q30527376`, both fathers, and both sons. Surfaced by the Pedaiah unmerge; both sit
     on the same side of that split, so it did not need deciding.
   - **You Xiong, twice (2026-08-02).** `Q51954` "You Xiong" and `Q87862` " (You Xiong)
     Youxiong" both have father `Q54433` and exactly one child, `Q6421` Shaodian, and
     `Q51954`'s aliases include the other's label verbatim. Surfaced by the Shaodian cut;
     merging would not have broken that ring. **Note `Q54433` is the haplogroup bridge
     node**, so this pair sits on a cross-tradition join — check `cycle_policy.md` before
     touching it.
   - **The Shila pair.** `Q86617` and `Q91224` are both "Shila Ish Kfar Temarta" and both
     recorded as the father of `Q86607` Acha. `Q86589` / `Q91134` is the same story one
     generation down, both "Abba 'Abbahu' bar Acha bar Sallah al-Kafri", both children of
     Acha.

8. **THE THEBAN RING — needs an Egyptological source, not another pass over the dump.**
   Tangle 11, the Second Intermediate Period kings. **None of the seven records carries a
   Wikidata id**, so the method the banner prescribes — look the dates up — does not reach
   them directly; they had to be matched by name first.

   One edge is settled and was cut on 2026-08-01 (`cut_edges.py theban-senebhenaf`):
   Wikidata has the vizier Senebhenaf's child as `Q536310` **Queen Mentuhotep**, whose
   spouse is `Q889883` Djehuti. So the dump's `Q85514` → `Q85498` recorded Djehuti's
   father-in-law as his father. Cut, 0 records lost Aster, tangle 7 → 6 records.

   **THAT CUT DID NOT ACTUALLY LAND UNTIL 2026-08-02, and the tool said it had.** `Q85514`
   listed **both** `Q85498` and `Q85518` as children, and `Q85518` is a silent redirect to
   `Q85498` — the same man under a duplicate qid. Removing the literal `Q85498` left
   `Q85518` behind, `extract_genealogy.py` canonicalized it straight back to
   `Q85514 → Q85498`, and `cut_edges.py`'s own verify pass — which compared cited qids
   literally — reported "edges gone from both sides". The tangle stayed at 7 for a day.
   **`cut_edges.py` now compares through `redirects.tsv`** (`canon`/`cvals`) on plan, apply
   and verify, and additionally checks every alias file of both endpoints. Re-run under the
   fixed tool: tangle **7 → 6**, records in a tangle 102 → 101, 0 records lost Aster, depth
   **+6**. A sweep of all 29 declared cuts across the 21 cut sets found this was the **only**
   one still live.

   **The surviving ring, and it is not guessable** (six records, re-read from
   `cycles_review.md` after the cut actually landed — `Q85478` Neferhotep III is in the
   ring, not below it):

       Q85478 Neferhotep III → Q85578 Mentuhotep VI → Q85554 Sebekemsaf → Q85528 Yauyebi
       → Q85514 Senebhenaf → Q85500 Mentuhotep → Q85478

   `Q85514` → `Q85500` is the attested edge and must not be cut. The false one is among the
   other three, and **Wikidata cannot settle it**: it records no parents for Sobekemsaf I
   (`Q563693`), has **no entry at all for "Yauyebi"**, and dates Senebhenaf to −1500 while
   dating his own daughter to −1650, so its chronology here is placeholder round numbers
   and decides nothing. This needs the Turin King List and Ryholt's reconstruction of the
   16th Dynasty.

   The one edge that would dissolve the ring on its own is `Q85578` → `Q85554`, and it is
   expensive — **3 records lose their route to Aster and 31,790 lose ancestry**. Do not
   take it as the cheap way out.

9. **THE JOAN / LLYWELYN DDÛ RING — the Esther shape, in Welsh. NEEDS A PEDIGREE SOURCE.**
   Tangle 10, seven records, investigated 2026-08-02 and **not** acted on.

   Six of the seven edges are confirmed by the patronymics, which in Welsh *are* the
   pedigree: `Q139043` "Ieuan **ap Rhys**", `Q140643` "Rhys **ap Llowdden** y Gath",
   `Q140681` "Lleucu **ferch Gruffudd**", `Q139067` "Gruffudd Foethus **ap Llywelyn**",
   `Q140234` "Llywelyn Foethus **ap Llywelyn Ddû ab Owain**", `Q138061` "Joan **ferch
   Ieuan ap Rhys ap Llowdden**". Every recorded father is corroborated by a name, and each
   is present in the dump under that name — `Q137927` really is "Owain", `Q142996` really
   is "Llowdden y Gath".

   **That leaves exactly two maternal claims, and precisely one of them must be false:**

   - `Q138061` Joan → `Q138810` Llywelyn Ddû ab Owain
   - `Q140681` Lleucu → `Q140643` Rhys ap Llowdden y Gath

   Both are spouse-consistent — Joan's husband is Owain, Llywelyn Ddû's father; Lleucu's
   husband is Llowdden, Rhys's father. **And Wikidata carries the identical ring**, both
   claims mirrored on both sides, so it arbitrates nothing. This is the two-Esthers shape:
   two readings, each internally coherent, nothing available to separate them.

   Needs a Welsh pedigree source — Bartrum's *Welsh Genealogies AD 300–1400* is the
   obvious one — not another pass over the dump. **Do not guess it**, and do not take the
   cheap cut: `Q138061` → `Q138810` is free and dissolves the tangle, which says nothing
   about whether it is the true edge.

10. **THE PORTUGUESE RING — four contradicted edges, not one. NEEDS A LINHAGENS SOURCE.**
   Tangle 4, fourteen records, investigated 2026-08-02 and **not** acted on.

   Portuguese patronymics work like the Welsh ones — *Ausendes* = son of Ausindo, *Soares*
   = son of Soeiro, *Ximenes* = son of Ximeno — and four of the ring's edges are
   **positively contradicted** by them, i.e. the child's own name gives a different
   father-name than the recorded parent:

   | recorded parent | child | the child's name says |
   |---|---|---|
   | `Q113625` D. Teodoredo **Ausendes** | `Q79388` D. Ausindo **Ximeno** | son of a Ximeno |
   | `Q79415` D. Soeiro **Ausendes** | `Q79435` D. Arnaldo **Ximenes** | son of a Ximeno |
   | `Q79480` Fernão de Tangil | `Q79537` Estêvão **Soares** | son of a Soeiro |
   | `Q79537` Estêvão Soares | `Q79618` Tereza **Eriz** de Lugo | daughter of an Ero |

   Four other edges are *confirmed* by the same test — Soeiro Guedes → Ausindo **Soares** →
   Teodoredo **Ausendes**, Ausindo Ximeno → Soeiro **Ausendes**, Arnaldo → Sancho
   **Arnolfo** — plus two external father-links, Ufo Ufes → Ufa **Ufes** and Arnaldo → Godo
   **Arnaldes**.

   **So this is not one bad join in one family. It is several fragments — Ximenes, Tangil,
   Baião, Lugo — concatenated into a chain**, and cutting any single edge opens the ring
   while leaving three false parentages standing.

   **Why I am not picking one.** The best candidate is `Q113625` → `Q79388`, which joins
   the end of the best-attested fragment to the start of another. But `Q113625` is a
   **claimless connector** — no `P47`, `P48` or `P20` in the canonical file *or* its shadow
   `Q101962`, only a birth of 1078 — so both its ring edges are one-sided, declared solely
   from its neighbours. That is the PHANTOM shape item 15 warns is not automatically safe
   to cut. And Portuguese naming is looser than Welsh: toponymics (*de Baião*, *Tangil*,
   *de Lugo*) break the patronymic rule often enough that "contradicted" carries less
   weight here than it did for Morfudd or Gwent.

   Needs the *Livro de Linhagens do Conde D. Pedro*, or Braamcamp Freire's *Brasões da Sala
   de Sintra* — a real Portuguese stemma, not another pass over the dump.

11. **THE EIGHT SERVILII — an eight-record ring with no evidence in it at all.**
   Tangle 8, investigated 2026-08-02 and **not** acted on.

   Eight records, each with exactly one father and one in-ring child, forming a closed
   8-cycle: `Q73170` → `Q73985` → `Q73910` → `Q73812` → `Q73710` → `Q73599` → `Q73479` →
   `Q73332` → `Q73170`. **Not one carries a Wikidata id, a date, or a cognomen** — they are
   "Gaius Servilius" ×3, "Quintus Servilius" ×2, "Publius Servilius", "Gnaeus Servilius",
   and one bare "Servilius". The component has **7 ancestors — the other seven members —
   and does not reach Aster**, so nothing enters it from above. It exists only to link two
   real Servilian groups, and its ends have been joined.

   **What the two branch points do tell us.** Only two members have children outside the
   ring, and their descendants are datable:
   - `Q73170` → `Q73008` Marcus Servilius, whose line reaches **Publius Servilius Vatia
     Isauricus, 120–44 BC** (wd `Q392647`) — Republican.
   - `Q73910` → `Q78378` Gaius Servilius, whose line reaches **Claudia Acilia (185–215 AD)
     and the Anicii, down to Anicius Auchenius Bassus (350–408)** — late Imperial.

   In the ring `Q73170` sits two generations above `Q73910`, which puts the Republican
   branch above the Imperial one — chronologically right. **So the cut cannot fall on
   `Q73170` → `Q73985` or `Q73985` → `Q73910`**, which would invert that. That rules out
   two of the eight edges and leaves six, and **nothing available distinguishes those
   six.**

   Do not pick one by cost — all eight are free and all eight dissolve the ring. This needs
   a Servilian stemma (Münzer, *Römische Adelsparteien*, or the RE) or Emma's decision to
   collapse the placeholder chain entirely under repair-order step 4, which is the one case
   in the queue where "nothing substantial above it" is literally true.

12. **THE TWO ESTHERS — genuinely undecidable from the dump. NEEDS A SOURCE OR EMMA.**
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

   **Three of the four mutual-parent pairs are now CUT and their tangles are gone
   (2026-08-01).** `Q18066`/`Q32705` and `Q119481`/`Q124343` via `cut_edges.py
   nagano-entenca`; `Q29144`/`Q29148` via `agathocles-kayanid` plus the
   `add_bridge_edges.py kayanid-pisan` reattachment, which is not optional — the cut alone
   took Kay Pisan from 341 ancestors to 0. All three were decided by reading the people
   rather than the dump; see the devlog entries and the cut sets' comments. Two of the
   three false edges are on Wikidata as well, and in both cases Wikidata contradicts
   itself, which is where they came from.

   **`Q73530`/`Q73653` is DONE (2026-08-02, `cut_edges.py fulvii-mutual-parents`).** Both
   directions cut, not one: the Fulvii stemma is already complete in the dump — `Q99418`
   L. Fulvius I → `Q73958` L. Fulvius II → `Q73872` L. Fulvius Curvus → both `Q73530`
   Marcus Flaccus and `Q99414` Marcus Curvus, and `Q99414` → `Q73653` Cassus Curvus — so
   Flaccus and Marcus Curvus are brothers and Cassus Curvus is Flaccus's nephew. Neither of
   the pair is the other's father either way.

   **Also still open, and not a merge:** the `WRONG-PARENT-EDGE` on `Q72834` (two fathers
   who are brothers, `Q72984` wd `Q929498` and `Q148066` wd `Q897091`).

   **`Q72834`'s two fathers are NOT a dump defect — Wikidata carries the same pair.**
   Checked 2026-08-01: `Q703354` lists father = [`Q897091` Marcus, `Q929498` Quintus] and
   both of those are sons of `Q359810` L. Caecilius Metellus cos. 251. So the dump
   faithfully imported a contradiction that exists upstream, and one of the two is wrong
   there as well. It is **not** part of the tangle-7 loop, which was cut separately, so it
   is a standalone multi-parent defect and needs a source rather than a graph argument.

   **NEW, and it is an UNMERGE for Emma — the Kayanid conflation.** The Bundahishn gives
   two lists that share names, XXXI.25's four brothers (Kay Arsh, **Kay Vyarsh**, Kay
   Pisan, **Kay Kaus**) and XXXI.28's descent (Lohrasp ← **Auzav** ← **Manush** ← Kay
   Pisin ← Kay Apiveh ← Kay Kobad). The import merged one name from each list into one
   record, twice: `Q29144` is "kay uyarsh" aliased "kay manush", and `Q29140` is "kay
   kaus" aliased "kay auzav". The loop that came out of the first was cut; the conflations
   themselves stand. Splitting either needs a new record and a name, which is Emma's per
   the `Tros` precedent. `Q29144`'s three fathers (`Q29148`, `Q29152`, and the empty shell
   `Q52717`) are the same defect wearing a different hat.

   **`fix_mutual_parent_pairs.py`'s two reporting defects are FIXED (2026-08-01).**
   Symmetric spouse-coparent evidence no longer claims "two records of one person that
   need a MERGE" — it now says the signal decides nothing, and where the pair is
   demonstrably two people (distinct Wikidata ids, or different recorded sex) it says so
   and says **NOT a merge**. `Q119481`/`Q124343` now reads correctly. It also skips pairs
   with an endpoint absent from `persons.tsv` instead of inferring a family for a record
   that does not exist. It still repairs 0 of 5 — every remaining pair genuinely lacks
   direction evidence, which is the correct answer, not a failure.

13. **Work `qa_same_role_parents.tsv` — 1,712 same-role parent collisions, graph-wide.**
   Generated 2026-08-01 by `wiki-scripts/same_role_parents.py`. One child has one father
   and one mother, so **every row is a defect**: either the pair is one person recorded
   twice, or one of the two edges is false.

   **This is the class the tangle-scoped detector could not see.** `propose_tangle_repairs.py`
   examines the 283 records inside tangles and found **6**. There are **1,712 pairs over
   1,330 children** — it was seeing 0.35%.

   | verdict | n | meaning |
   |---|---|---|
   | `DEDUPE` | 1,154 | nothing distinguishes the pair; **630 have corroboration** (shared parent or shared spouse) |
   | `ABSENT` | 408 | one side has no file or is an empty shell — belongs with item 4 |
   | `COLLAPSE` | 120 | one is an ancestor of the other. **NOT duplicates**; merging fuses two generations |
   | `DISTINCT` | 30 | different Wikidata ids or different recorded sex. Two people, so one edge is false — a CUT, not a merge |

   **Verified against every case checked by hand:** `Q72834` comes out `DISTINCT` (the two
   Caecilii Metelli brothers), and Adnan `Q65555`'s three fathers all appear, with
   `Q66385`/`Q66394` carrying the shared wife `Q66382` as corroboration.

   **THE MULTI-PARENT CHECK IS NOW IN THE TOOL** (2026-08-01). `merge_cluster.py`'s dry run
   unions each pair's parents and warns on any survivor crossing **three**; `--write`
   aborts rather than applying a cluster that would fail I4. It over-warns by design — it
   does not model the offsetting decreases a merge causes — so a warning means *look*, not
   *impossible*. `--force-i4` exists for a deliberate, explained increase. Batch 2 was applied seven-strong,
   failed I4 at 1207 → 1210, and had to be reverted to three. The merges were *correct* —
   they surfaced a father-conflict previously hidden by being split across two copies of a
   duplicated subtree — but a real conflict revealed is still a gate failure.

   **The Severan subtree is BLOCKED on its husbands.** `Q4680`/`Q166165` Julia Maesa is
   merged; `Q4681`/`Q166205` Mamaea, `Q4682`/`Q166216` Zenobius, `Q151866`/`Q166249` and
   `Q151865`/`Q166250` are not, because each survivor would inherit two fathers.
   `Q151898`/`Q166247` "Marcus Julius Gessius Ma…" share a label and are probably a pair —
   merging them first would unblock two of the four. `Q4682`'s fathers are **Elagabalus**
   and **Malchus II of Palmyra**, plainly different men: one edge is false and the dump
   does not say which. **Needs Emma or a source.**

   **Batch 1 applied 2026-08-01** (`same-role-batch-1`: Maratton, Isabel de Polanco, Anna
   Xylaloe) — every gate green, zero depth change. **1,707 pairs / 1,149 DEDUPE remain.**
   **Do not take the Kosala (`Q2627`/`Q29967`) or Quraysh (`Q64471`/`Q94808`,
   `Q65861`/`Q94403`) pairs** — those are held for Emma. `Q1683`/`Q48279` "Gayatri
   Rajapatni" is a three-level cascade (Gayatri, Kertanegara under his regnal title
   `Q48307`, Wisnuwardana `Q1699`/`Q48347`) and needs its own cluster, not a bottom-level
   merge.

   **DEDUPE is a candidate, not a verdict.** Every merge this session that looked obvious
   from a signal needed the hand-check anyway. Work them in batches with `merge_cluster.py`
   and the full `verify_repair.py` ritual, highest-corroboration first.

   **Note the dump is not only people.** Rows like `Q39502` "Euteleostei" / `Q153134`
   "1 Euteleostei" are in the **evolutionary taxonomy**, not the human genealogy. The
   duplicate there is real, but the naming conventions and what counts as evidence are
   different — do not apply prosopography reasoning to a clade.

14. **THE 'UDD / ADNAN PARENTAGE — NEEDS EMMA.** `Q65555` Adnan has **three fathers**:
   `Q66385` "Imaam 'Udd \ Add Ben Add Ben ?'Udadh", `Q66394` "Udd son of Umaisi", and
   `Q86503` "Nabhan Banu Ismail" (the last acquired in the M3 merge). At most one is right.

   `Q66385` and `Q66394` are both married to **the same woman** `Q66382`, who lists both as
   her husbands — the dump stating the duplication about itself. Neither carries a Wikidata
   id and neither is an ancestor of the other, so nothing structural separates them.

   **But their fathers differ in exactly the way variant traditions differ:** `Q66385`'s
   father is `'Udadh`, `Q66394`'s is `Umaisi`/`Humaisi`. The Arab sources give variant
   chains for Adnan's ancestry, and *'Udd* and *'Udad* are variants of one name. **This may
   be two source-traditions deliberately kept, not a duplicate** — and R1 already
   established that Muhammad's ancestry here is intentional. Merging them would collapse
   the variant. **Do not merge without Emma.**

   Related and also unresolved: `Q66385`'s own two fathers `Q67549` and `Q67552` are both
   children of `Q67561` — and `Q67552` is flagged `COLLAPSE` against `Q67561`, so those two
   must not be merged either.

15. **Work the remaining cycles under the repair order above.** Start from
   `wikibase/analysis/qa_tangle_repairs.md`, which is generated and ranks all 35 tangles.
   34 are `REVIEW`: no Wikidata evidence decides them, mostly because "contradicted" there
   means *Wikidata records no link*, which is an absence and not a refutation. Unmerge
   candidates first.
   The five remaining cycles of length >= 20 are all Roman, sharing the Q61957/Q62255/
   Q63192/Q63747/Q70152/Q138467 stretch — likely the same repeating-cognomen collision that
   produced the short Roman 2-cycles. Emma: preserve the Roman material; unmerge, do not
   delete.

16. **Fix the one-sided edges. THE PHANTOM RULE IS NOW SET.**

   > **RULED BY EMMA 2026-08-05, asked directly: "ADD the missing side, always."**
   >
   > This settles the `PHANTOM` class — **1,050 edges, 430 shell records** — and it is a
   > *rule about placeholder people*, not a one-off: when an edge is declared on only one
   > side and the other endpoint is an empty shell, **write the mirror claim into the
   > shell**. Never remove the present side.
   >
   > **Why this is safe to run in bulk, unlike everything else in this file:** ADD is
   > **provably graph-neutral**. `edges.tsv` is built from the UNION of both directions, so
   > the edge is already in the graph and writing the mirror cannot change it. Expect
   > `compare_tangles` and `compare_depth` to come back **completely clean** — and if
   > either moves, the script wrote something other than the mirror of an existing edge.
   > **That is the gate: any movement at all is a bug, not a finding.**
   >
   > It also removes the silent-revert hazard this item exists for: a one-sided edge is
   > one vacated file away from disappearing.
   >
   > **Scope of the ruling: `PHANTOM` only.** `GAP` (219) still needs its four missing
   > records CREATED and named — that is item 17 and still Emma's. `BOTH-REAL` (2,479) is
   > still per-record judgement and the do-not-blanket-add warning below still applies to
   > it in full. Do not let "ADD always" leak out of the phantom class.
   >
   > Emma was shown the counter-argument — that some one-sided edges are half-finished
   > deletions and adding would cement an edge someone meant to remove — and ruled ADD
   > anyway. Nothing in an empty shell distinguishes the two cases, so **do not try to
   > second-guess it per record**; that is precisely the analysis paralysis the ruling ends.
   >
   > Propagate every write to all shadow files claiming those qids; `shadow_audit.py` must
   > finish at 0. Commit in batches with the count in the message, not as one 1,050-edge
   > commit.

   `wikibase/analysis/edge_symmetry.txt`, rebuilt 2026-08-01:
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

17. **NAME THE FOUR MISSING RECORDS — needs Emma.** `Q74656`, `Q75282`, `Q54196`, `Q78402`
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
