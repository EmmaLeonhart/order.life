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
> **STATE AS OF 2026-08-15: ZERO TANGLES. The loop-removal task this banner describes is
> DONE.** `check_invariants.py` on a freshly regenerated extract: `tangled_components 0`,
> `records_in_a_cycle 0`, `self_loops 0`. It ran from 34 tangles / 283 records trapped at
> the 2026-08-01 handoff to nothing.
>
> **Keep reading the banner anyway** — every warning in it is about *method*, and the
> method is why the last one took eight days to actually land. The 2026-08-07 Lepidus cut
> reported "Verified" and removed nothing; see item 1. Point 4 below ("I never once looked
> a person up on Wikidata") is the one that closed most of these.
>
> *Superseded, kept for the shape of the climb: at end of 2026-08-02 this read 8 tangles,
> 80 records trapped, largest 15 — with a note that none of the 8 was "a two-line edit
> waiting to be made" and each needed a ruling from Emma or an external stemma. Seven were
> closed on 2026-08-07 by going and finding the stemma, and the eighth by fixing a script
> that was comparing the wrong string. **None of them needed a ruling from Emma.***
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
them. **The chapter gate is GONE** — lifted by Emma 2026-08-05; chapter generation is
open. Still don't barrel: chapters emerge at the writing desk, not from a numbered list.

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
record, the load-bearing one), `check_invariants.py`, and then the two *standing-claim*
gates, `verify_cuts_landed.py` and `verify_applies_landed.py`. It exits non-zero naming
whichever failed.

**Gates 5 and 6 are not before/after comparisons, and that is the whole reason they
exist.** Every delta gate reads a repair that never landed as a **no-op rather than a
failure** — so a script that silently did nothing sails through all four. That is how
`theban-senebhenaf` sat applied-and-alive for a day, and how the 2026-08-07 Lepidus cut sat
that way for eight while its own verify block agreed it was done. The standing-claim gates
ask a different question: is the graph what the repo says it is? **When you add or change an
`apply_*.py` repair, add its edges to `EXPECTED` in `verify_applies_landed.py` in the same
commit** — an entry that drifts from its script passes while measuring the wrong thing,
which is worse than no entry. Merges still go through `wiki-scripts/merge_cluster.py <cluster>`, which
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

### CLOSED REPAIRS LIVE IN `wikibase/analysis/closed_repairs.md` — read it before
re-opening anything

Items 2, 3, 9, 10, 11 and 12 were finished and are **deleted from this file**, per
delete-don't-check. Their reasoning is not lost: `closed_repairs.md` carries the Licinii
Vari closure and its withdrawn finding, the four rings settled by external evidence on
2026-08-07 (Joan/Lleucu, the Portuguese ring, the eight Servilii, the two Esthers), and
above all **the ⚠ Daksha trap** — the split that was applied and reverted the same day and
must not be re-proposed.

Two rules from that file worth carrying here:

- **Opening a loop is not evidence of having found its defect.** If the only way to open it
  is to move something that belongs where it is, the defect is elsewhere.
- **Undecidable from the dump is not undecidable.** All four of the 2026-08-07 rings had
  been filed as needing a ruling; each fell to one lookup or one date.

### THE TANGLE TABLE — ALL EIGHT ARE NOW CLOSED (last one 2026-08-15, 0 records trapped)

**`tangled_components` is 0. There is no ancestry cycle left in this dump.** Measured by
`check_invariants.py` on a freshly regenerated extract, 2026-08-15, and cross-checked by
`compare_tangles.py` reporting 1 → 0 with **0 records newly inside a tangle**.

**This does not mean the genealogy is correct — it means it is acyclic.** The open work is
now about lines attached through the *wrong story* rather than lines that loop, and
`narrative_spine.md` is explicit that the second kind is worse: a severed line is one
honest edge from correct, a wrongly-attached one is already wrong while measuring fine.
Item 2 (`Q73308`) is exactly that kind and is unaffected by any of this.

The table below is kept as the record of how each was closed. Re-read the live numbers
from `check_invariants.py`, never from this file.

| # | tangle | records | item | what it waits on |
|---:|---|---:|---:|---|
| 1 | Mamercus Aemilius Lepidus Livianus | 15 | 1 | **RING ACTUALLY CUT 2026-08-15.** The 2026-08-07 cut reported success and removed nothing — see below. Couples B and C are in `todo.md` |
| 2 | Prachetas (10 sons) | 14 | 3 | **DONE 2026-08-07 — Sunitha's father, `apply_sunita_mrityu.py`. Not the Daksha split.** |
| 3 | D. Ausindo Ximeno | 14 | 10 | **DONE 2026-08-07 - Tereza Eriz belongs to Ero of Lugo, `apply_tereza_eriz.py`** |
| 4 | Aditi Kashyapa | 14 | 3 | **DONE 2026-08-07 — same repair, second copy** |
| 5 | Gaius Servilius | 8 | 11 | **DONE 2026-08-07 - dated by the two exits, `apply_servilii_chain.py`** |
| 6 | Joan ferch Ieuan ap Rhys | 7 | 9 | **DONE 2026-08-07 — Rhys Gryg d. 1234 dates it, `apply_lleucu_generation.py`** |
| 7 | Sekhemre Sankhtawy Neferhotep III | 6 | 8 | **DONE 2026-08-07 — Queen Mentuhotep is a wife, `apply_mentuhotep_queen.py`** |
| 8 | Esther bat Sahlan ben Abraham | 2 | 12 | **DONE 2026-08-07 — the 1037 ketubba, `apply_esther_generation.py`** |

**Tangles 1, 2 and 4 were applied on 2026-08-07** — Emma: *"Apply them lol."* Three of the
eight are off the table; the remaining five all want an external stemma, which is research
to go and do, not a question for Emma.

**⚠ THE DAKSHA SPLIT WAS APPLIED AND THEN REVERTED THE SAME DAY. Read this before ever
re-proposing it.** Splitting Daksha did open both rings, and it was the wrong repair:

- **The sixty daughters belong to the SECOND Daksha, not the first.** Aditi, Diti, Danu
  and Kadru married to Kashyapa, the 27 nakshatras married to Chandra, the 10 married to
  Dharmadeva — that whole set is canonically the issue of **Prachetasa Daksha by Asikni**.
  The first Daksha, Brahma's son, married *Prasuti* and fathered *Sati*. The dump's 63
  children are unmistakably the second set. The split moved them onto a first-birth Daksha
  to open the ring, which is backwards, and only opened it *because* it was backwards.
- **The real defect was one edge away.** `Q153444` "SUNITA Anga" had `Q2035` Yama as her
  father. Sunitha, wife of Anga and mother of Vena, is the daughter of **Mrityu** — Death
  personified, a separate figure from Yama Dharmaraja, carried separately on Wikidata as
  `Q12735987`. Two death-figures conflated into one, the same shape as the Lepidus record.
  Structurally it was the only edge joining the solar line to the Prithu line, and the
  Prithu line descends from Svayambhuva Manu through Dhruva, not from Vaivasvata.
- **`apply_sunita_mrityu.py` is the repair that stands.** Mrityu created in both copies,
  Sunitha's parentage moved onto him, Shyamala (Yama's own wife) dropped as her mother
  since she came with the same conflation. Both rings open; Daksha keeps his Prachetas
  parentage and all sixty daughters; `Q153390` now reaches 142 real ancestors and
  `Q160489` reaches 45, where before each reached only itself.

**The general lesson, and it is `cycle_policy.md`'s own:** the split was reachable from the
ring alone, and wrong. Opening a loop is not evidence of having found its defect. If the
only way to open it is to move something that belongs where it is, the defect is elsewhere.

**One narrower trap worth keeping.** Item 3 said `Q153390` carries two fathers, `Q49634`
(first birth) and `Q1955` (rebirth). **`Q49634.json` is a shadow file whose own `id` is
`Q1955`** — byte-identical, and `redirects.tsv` maps one to the other. The "two fathers"
were one man referenced twice, once directly and once through a redirect qid. **Check
whether a second father is a redirect before reading it as a second parentage.**

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

## GAIAD AND THE GAIAN CALENDAR (added 2026-10-12, from Emma's psilocybin-session chat of 2026-10-11/12)

Her request: queue items "for reworking the Gaian calendar and the Gaiad to make this work better",
"based off of all of the stuff that we've been talking about". The chat is in the
`psilocybin-session-management` repo (`sessions/2026-10-11_d11e58a5.md`,
`research/session-2026-10-11.md`). What she said that these items rest on:

- The calendar is the part of the Gaiad she is proudest of: "I managed to establish it into a
  calendar system so that it's something that can actually be used liturgically rather than ...
  some long book nobody reads." "The calendar is actually doing more work than I may initially think
  of it as being."
- The modern sections: "we probably should have enough content and ideas that we can ... make the
  modern sections. They're not going to be set in stone."
- Ophiuchus is the 21st century and is rewritten often for a while: "Am I going to say it's going
  to be rewritten every year? Every year? No. But I imagine it's going to be such for a while ...
  we're about a quarter of the way through it."
- What she likes: "It feels like an ancient tradition. That couldn't have been made in the modern
  day, except it was made in this year."
- The day-by-day draft must be complete: "just this thing being out there as a thing ... makes it
  so that it's, in a sense, citable ... But it does kind of have to be complete."

Items, in order:

7. **The modern chapters, one item each, in order (Emma, 2026-10-12 15:55: "each chapter is individually
   there in order so that they just get made ... reliably, not half-assed").** Themes are from the
   approved `planning/gaiad-253-364/day-themes-draft.md`. Each one is written, not drafted (Emma,
   15:56: "it's not supposed to be drafted. You're supposed to literally write each one of them in
   order"): a finished chapter, in order, before the next. For every chapter: read
   `planning/gaiad-tone-and-founders.md`, the thematic spine and any brief in `planning/gaiad-253-364/`
   first; real verse, ~60-150 lines, `{{c|}}`/`{{p|}}` templating, modern placenames, ends "Stand.";
   check the facts before committing; update the runway in `STATUS.md`; one chapter per commit; delete
   its line here when done. Ch 253-263 are done.
   - **Ch 264 (Virgo 12):** 1582 to 1610: Matteo Ricci in China, Confucian and Christian accommodation. Holiday: Mid-Autumn Festival; Days of Awe.
   - **Ch 265 (Virgo 13):** 1590 and 1597: Hideyoshi unifies Japan; the Twenty-Six Martyrs. Holiday: Days of Awe.
   - **Ch 266 (Virgo 14):** 1600: Sekigahara, the Tokugawa order. Holiday: Shindensai; Days of Awe.
   - **Ch 267 (Virgo 15):** 1602: the VOC, a company with the powers of a state. Holiday: Days of Awe.
   - **Ch 268 (Virgo 16):** 1568 to 1652, working years from c. 1600: Johannes Bureus, runes, Kabbalah, Gothicism, *Om Bura namn och ätt*. Holiday: Days of Awe.
   - **Ch 269 (Virgo 17):** 1609 to 1610: Galileo's telescope, the sky opens. Holiday: Days of Awe.
   - **Ch 270 (Virgo 18):** 1611 to 1632: Gustavus Adolphus; Gothicism as Sweden's state myth. Holiday: Days of Awe.
   - **Ch 271 (Virgo 19):** 1613 and 1666: Russia, the Romanovs and the Old Believer schism (open: "unsure how much"). Holiday: Days of Awe.
   - **Ch 272 (Virgo 20):** 1618 to 1648: the Thirty Years' War and Westphalia. Holiday: Yom Kippur.
   - **Ch 273 (Virgo 21):** 1630s to 1660s: sakoku and the temple registration system, every household registered through a temple.
   - **Ch 274 (Virgo 22):** 1637 to 1638: Shimabara and the Hidden Christians, a faith kept in secret for 250 years.
   - **Ch 275 (Virgo 23):** 1644: the Ming fall and the Qing take over.
   - **Ch 276 (Virgo 24):** 1658 to 1707: Aurangzeb, the Mughal synthesis closes.
   - **Ch 277 (Virgo 25):** 1660: the Royal Society.
   - **Ch 278 (Virgo 26):** 1665 to 1666: Sabbatai Zevi, a messiah and a mass movement. Holiday: Sukkot.
   - **Ch 279 (Virgo 27):** 1687: Newton's *Principia*.
   - **Ch 280 (Virgo 28):** 1679 to 1703: Leibniz, binary, the I Ching, a universal language (the bridge to Libra).
   - **Ch 281 (Libra 1):** 1704 and 1742: the Chinese Rites controversy, Rome refuses the synthesis. Holiday: Harvest Day.
   - **Ch 282 (Libra 2):** 1735: Linnaeus, a Swede puts all life into one system.
   - **Ch 283 (Libra 3):** c. 1740: the Baal Shem Tov and Hasidism.
   - **Ch 284 (Libra 4):** 1744: Wahhabism, purification as a split.
   - **Ch 285 (Libra 5):** 1745 to 1772: Swedenborg, a Swedish visionary's new church.
   - **Ch 286 (Libra 6):** 1751: the *Encyclopédie*, all knowledge in one structure.
   - **Ch 287 (Libra 7):** 1760: Ossian, a tradition made to look ancient.
   - **Ch 288 (Libra 8):** 1768 to 1779: Cook in the Pacific.
   - **Ch 289 (Libra 9):** 1769 and 1776: Watt's engine, the machine age.
   - **Ch 290 (Libra 10):** 1773 to 1782: the *Siku Quanshu*, the largest compilation ever made, and a censorship.
   - **Ch 291 (Libra 11):** 1786: William Jones, languages turn out to have a family tree.
   - **Ch 292 (Libra 12):** 1793: the French Republican calendar, a revolution remakes time.
   - **Ch 293 (Libra 13):** 1794: the Cult of the Supreme Being, a state invents a god.
   - **Ch 294 (Libra 14):** 1798: Motoori Norinaga completes the *Kojiki-den*, ancient Shinto recovered.
   - **Ch 295 (Libra 15):** 1804 and 1806: Napoleon; the Holy Roman Empire ends.
   - **Ch 296 (Libra 16):** 1812 and 1835: the Grimms and the *Kalevala*, a national epic compiled.
   - **Ch 297 (Libra 17):** 1822: the Rosetta Stone deciphered, the dead speak again.
   - **Ch 298 (Libra 18):** 1822 to 1843: Babbage and Lovelace, the record gets a machine.
   - **Ch 299 (Libra 19):** 1844 and 1863: the Báb, then Baháʼu'lláh, a religion of unification.
   - **Ch 300 (Libra 20):** 1850 to 1864: Taiping, Christ's younger brother.
   - **Ch 301 (Libra 21):** 1853: Perry, Japan opens. Holiday: Halloween, Eve of Ancestors.
   - **Ch 302 (Libra 22):** 1859: Darwin, the Gaiad's own foundation.
   - **Ch 303 (Libra 23):** 1866 and 1869: Mendel and Galton, inheritance and who gets to survive.
   - **Ch 304 (Libra 24):** 1868: Meiji; the Department of Divinities restored, kami and buddhas forced apart.
   - **Ch 305 (Libra 25):** 1875: Theosophy, East and West in one system.
   - **Ch 306 (Libra 26):** 1887: Nietzsche's *Genealogy of Morals*, who gets to define good.
   - **Ch 307 (Libra 27):** 1890: Hollerith, the census becomes a machine.
   - **Ch 308 (Libra 28):** 1893: the Parliament of the World's Religions; Vivekananda. Holiday: Samhain.
   - **Ch 309 (Scorpius 1):** 1905: Einstein.
   - **Ch 310 (Scorpius 2):** 1911 to 1912: the Qing fall, the imperial cult of Heaven ends.
   - **Ch 311 (Scorpius 3):** 1914 to 1918: the First World War.
   - **Ch 312 (Scorpius 4):** 1917: Russia, Marxism takes a state.
   - **Ch 313 (Scorpius 5):** 1924: the caliphate abolished.
   - **Ch 314 (Scorpius 6):** 1936: Turing, what can be computed.
   - **Ch 315 (Scorpius 7):** 1941 to 1945: the Holocaust, who survives, and the names kept (Yad Vashem, 1953).
   - **Ch 316 (Scorpius 8):** 1945: Hiroshima and Nagasaki.
   - **Ch 317 (Scorpius 9):** 1945 and 1947: ENIAC and the transistor.
   - **Ch 318 (Scorpius 10):** 1945 to 1946: the Shinto Directive, the Humanity Declaration, the founding of Jinja Honchō.
   - **Ch 319 (Scorpius 11):** 1945 and 1948: the UN and the Universal Declaration of Human Rights.
   - **Ch 320 (Scorpius 12):** 1947 and 1948: Partition, and Israel, splits.
   - **Ch 321 (Scorpius 13):** 1953: DNA.
   - **Ch 322 (Scorpius 14):** 1957: Sputnik. Holiday: Shichi-go-san.
   - **Ch 323 (Scorpius 15):** 1962 to 1965: Vatican II, the rite in the people's language.
   - **Ch 324 (Scorpius 16):** 1965: the Granite Mountain Records Vault, the Mormons microfilm the world's ancestors.
   - **Ch 325 (Scorpius 17):** 1966 to 1976: the Cultural Revolution, tradition destroyed.
   - **Ch 326 (Scorpius 18):** 1969: the Moon landing and ARPANET. Holiday: US Thanksgiving.
   - **Ch 327 (Scorpius 19):** 1973: revived paganisms, Ásatrú recognised in Iceland.
   - **Ch 328 (Scorpius 20):** 1978 and 1979: Deng opens China; the Iranian Revolution.
   - **Ch 329 (Scorpius 21), revise:** weave Heisei's 1990 Daijōsai into "The Covenant of Peace" (decided 2026-10-12; see the draft's Scorpius note). Holiday: Niiname-sai.
   - **Ch 330 (Scorpius 22):** 1990: the Human Genome Project begins.
   - **Ch 331 (Scorpius 23):** 1991: the Soviet collapse.
   - **Ch 332 (Scorpius 24):** 1991: the Web goes public.
   - **Ch 333 (Scorpius 25):** 1995: Aum Shinrikyo, the shadow side of new religions. Holiday: US Thanksgiving.
   - **Ch 334 (Scorpius 26):** 1996: Dolly the sheep, copying life.
   - **Ch 335 (Scorpius 27):** 1997: Deep Blue.
   - **Ch 336 (Scorpius 28):** 2000: Y2K, the century ends worried about its own clocks.
   - **Ch 337 (Ophiuchus 1):** 2001: Wikipedia, everyone writes the record.
   - **Ch 338 (Ophiuchus 2):** 2001: 9/11 and its wars, religion back at the centre of politics.
   - **Ch 339 (Ophiuchus 3):** 2003: the Genome completed, the code of descent read.
   - **Ch 340 (Ophiuchus 4):** 2004: Facebook, kinship becomes a network.
   - **Ch 341 (Ophiuchus 5):** 2004: Google Books, the paper record becomes searchable.
   - **Ch 342 (Ophiuchus 6):** 2007: the iPhone, the machine in every hand.
   - **Ch 343 (Ophiuchus 7):** 2006 to 2007: indexed genealogy and consumer DNA (FamilySearch indexing, 23andMe), everyone traces descent.
   - **Ch 344 (Ophiuchus 8):** 2008 to 2009: the crash and Bitcoin, trust moves from institutions to protocol.
   - **Ch 345 (Ophiuchus 9):** 2009 to 2015: climate, from Copenhagen to Paris, who survives.
   - **Ch 346 (Ophiuchus 10):** 2010 to 2011: the Arab Spring, networks against states; Fukushima.
   - **Ch 347 (Ophiuchus 11):** 2012: AlexNet, machines learn to see.
   - **Ch 348 (Ophiuchus 12):** 2012: Wikidata, the register becomes a machine-readable ontology.
   - **Ch 349 (Ophiuchus 13):** 2013: Snowden, the register watches back.
   - **Ch 350 (Ophiuchus 14):** 2014: the Islamic State, reactionary invented tradition.
   - **Ch 351 (Ophiuchus 15):** 2016: AlphaGo, the oldest game falls.
   - **Ch 352 (Ophiuchus 16):** 2016: the populist turn, invented tradition in politics.
   - **Ch 353 (Ophiuchus 17):** 2017: the Transformer, attention.
   - **Ch 354 (Ophiuchus 18):** 2019: Reiwa's Daijōsai, the oldest rite continued.
   - **Ch 355 (Ophiuchus 19):** 2020: COVID; alongside it, Emma's 2020: the Gaiad's weekly verses through much of the year, to about chapter 60.
   - **Ch 356 (Ophiuchus 20):** 2021: the vaccines, and the Taliban back in Kabul; alongside it, Emma's 2021: "a pretty significant year for me where I ran around Europe and did lots of stuff" (her words, 2026-10-12; the Gaiad itself had a gap that year).
   - **Ch 357 (Ophiuchus 21):** 2022: Russia's full invasion of Ukraine (after Crimea, 2014), war in Europe again (Emma: "the biggest missing part here"); ChatGPT, the writing machine; alongside it, Emma's 2022: Sudowrite, her first writing with AI. Holiday: Christmas, Dongzhi.
   - **Ch 358 (Ophiuchus 22):** 2023: Shinto overseas, traditions carried past their borders; alongside it, Emma's 2023: "a lot of this Shinto stuff fall into my hands".
   - **Ch 359 (Ophiuchus 23):** 2024: the fork, the machine in few hands or everyone's; alongside it, Emma's 2024: "trying to reclaim a sacred geography, trying to reclaim other things .. being able to do so, but having it yanked away from me, too".
   - **Ch 360 (Ophiuchus 24):** 2025: agents, machines that act, and a scripture written with them; alongside it, Emma's 2025: "a very, very, very miserable year".
   - **Ch 361 (Ophiuchus 25):** 2026: Emma and her ancestry, with the Virgo coincidence; "an extremely well-documented year of my life".
   - **Ch 362 (Ophiuchus 26):** 2026 and the time skip (hard anchor, ch 362).
   - **Ch 363 (Ophiuchus 27):** The cryonic revival (hard anchor, ch 363).
   - **Ch 364 (Ophiuchus 28):** Milkomeda (hard anchor, ch 364).
8. **Ancestor lines: full dates in both calendars (Emma, 2026-10-12 15:09).** On her phone the iCal
   line reads "Died: Welf I von Altdorf Graf in Schwaben (0825)": the Gregorian year alone,
   zero-padded, on a Gaian day. She wants the date as the source gives it (Gregorian, or the native
   calendar's date) and the Gaian date. Work: keep the source's date text in
   `content/ancestor_days.json` (`scripts/build_ancestor_days.py`), compute the Gaian date with year
   (year + 10000, from the ISO week as now), and show both in `_ancestor_lines` in `build.py` and in
   `templates/sections/ancestor-day.html`, e.g. "(14 March 825; Virgo 26, 10825 GE)"; for a date
   placed by her rules, show what the source said ("abt 825"). No zero padding.

9. **After every chapter is written: a systematic review of the whole Gaiad, in chronological order
   (Emma, 2026-10-12 15:56).** Her words: "a systematic review of all of the chapters in chronological
   order ... to review the degree that they satisfy all of the criteria that order.life is supposed
   to have." Ch 1 to 364 in order, one chapter at a time, each checked against every criterion: the
   pinned corrections in `STATUS.md` (verse register, three braided registers, modern placenames,
   `{{c|}}`/`{{p|}}` templating, ends "Stand."), `CLAUDE.md` (the synoptic genealogy told by its
   story; linear time; one person, one set of parents; cross-tradition joins kept), the tone and
   founder guidance in `planning/gaiad-tone-and-founders.md`, the thematic spine for 253-364, the
   chapter's day and holiday in the calendar, and its facts. Record each chapter's result, fix what
   fails, one commit per chapter. Starts only when ch 364 exists.

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
   **Research note, 2026-10-11 (checked the same day against Korean Wikipedia citing the *Samguk yusa*):** the
   *Garakguk-gi* (in *Samguk yusa*) names only the eldest son, Geodeung, who succeeded Suro; two
   sons took their mother's surname Heo; the seven who became monks are named in later Chilbulsa
   legend, not in the *Garakguk-gi*. If that holds, the nine sons are unnamed in the source, and
   naming them is the second question for Emma, not to be invented.
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

## GATED

_(none — **the Leo gate was lifted by Emma on 2026-08-05**, a week early. New Gaiad
chapter generation (253–328, 330–364) is open. Do not re-add it here.)_

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
