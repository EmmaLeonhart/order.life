# order.life — Devlog

Dated log of autonomous work-loop progress. Newest first.

## 2026-08-01

- **The best duplicate signal I have was looking at 0.35% of the graph. Now it looks at
  all of it: 1,712 same-role parent collisions over 1,330 children.**

  `propose_tangle_repairs.py` only examines records inside tangles — 283 of 102,000 — and
  found six same-role collisions. Chasing the `'Udd`/`Humaisi` residue from the Adnan merge
  turned up a seventh that it structurally could not see: **Adnan `Q65555` has two fathers,
  `Q66385` and `Q66394`, both married to the same woman `Q66382`** — and Adnan is in no
  tangle at all.

  `wiki-scripts/same_role_parents.py` runs it graph-wide in 32 seconds. One child has one
  father and one mother, so every row is a defect: **1,154 `DEDUPE`** (630 corroborated by
  a shared parent or spouse), **408 `ABSENT`**, **120 `COLLAPSE`**, **30 `DISTINCT`**.

  The verdict order encodes what this session cost to learn. `COLLAPSE` is checked first
  and only on a **strictly one-way** ancestry relation, because mutual reachability is
  meaningless inside a tangle. `DISTINCT` catches the two Caecilii Metelli brothers that a
  naive same-role rule would have merged. `ABSENT` is the GAP/PHANTOM lesson. `DEDUPE` is
  what is left, and it is labelled a candidate rather than a verdict.

  **Checked against every case I had already done by hand**, and it reproduces all of them:
  `Q72834` comes out `DISTINCT`, Adnan's three father-pairs all appear with the shared wife
  as corroboration on the right one.

  **Two things worth knowing about the 1,154.** They are not all people — `Q39502`
  "Euteleostei" / `Q153134` "1 Euteleostei" are clades in the evolutionary tree, where the
  naming conventions and the evidence are different. And the `'Udd` pair, which prompted
  all this, is the one I will *not* act on: their fathers differ as `'Udadh` versus
  `Umaisi`, which is exactly how variant Arab source-chains for Adnan differ, and R1
  already established this ancestry as deliberate. Merging would collapse a variant.
  Written into the queue as needing Emma.

  Also fixed: the writer hit the mirror image of this morning's reader bug — `csv` with
  `QUOTE_NONE` refuses a field containing a double quote unless an escapechar is set, and
  setting one produces a file the `QUOTE_NONE` readers cannot parse back. Written with
  plain formatting, like every other TSV in `wikibase/analysis`.

- **Ran the connectivity test on the PHANTOM bucket BEFORE cutting anything, and it has
  the same shape as GAP at four times the scale.**

  1,050 one-sided edges over **430 shell records**. **269 of those shells are connectors**
  — both parents and children recorded by others — so **861 of the 1,050 edges would sever
  a chain if cut**. `Q132255` alone has 79 children. Last tick I learned this by cutting
  233 edges and watching the depth gate fail; this tick the same question was asked first.

  **The remaining 189 are still not obviously cuttable, and sampling is why.** The leaf
  shells are empty items carrying only `P39`, but of the eight I looked at, `Q135293` is
  **the father of Darius I of Persia**, `Q108512` is the father of Al-Qasim ibn an-Nafs
  az-Zakiyya, and `Q136745` is a child of Archelaus. They are unnamed placeholder people.
  Deleting their edges would erase *this person had a father*, which is a real statement.

  **The genuinely useful observation: ADD and REMOVE are not symmetric options here.**
  Adding the missing side **provably cannot change `edges.tsv`**, because the graph is
  built from the union and the edge is already in it — the same argument that made the
  self-loop cleanup safe. Removing changes the graph and destroys a relationship. So ADD is
  graph-neutral and REMOVE is not.

  That is not enough to act on. This item's own warning is that some one-sided edges are
  half-finished deletions, and adding would cement an edge someone meant to remove —
  nothing in an empty shell tells the two apart. **Written up and left for Emma rather than
  guessed at**, which is the whole of this tick's output on it.

- **`shadow_audit` refreshed and verified by mtime — 0 disagreements**, and byte-identical
  to the committed copy, so the 30 item files changed by the ORPHAN cuts moved no shadow.

- **Cut 233 "dangling" edges, and 219 of them were holes in the dump rather than
  nonexistent people. Reverted, split the category, cut the 14 that were real.**

  I had queued the 233 as "removable with no judgement" for three ticks. They are not.
  `compare_depth` failed at **−10 levels** across 126 records, and tracing it found the
  reason: `Q75282` has **no item file at all**, but 15 ancestors and 59 children — all
  recorded by *other* records. It sits between the Titan tier and Melaneus. Cutting its
  edges severed Melaneus and Aeneus from the Titan line completely.

  **A missing endpoint is two different things and I had one word for both:**

  - **`GAP`** — no file, but referenced from *both* directions. A real person whose item
    file is absent, with the family recorded around the hole. **Cutting severs a real
    chain.** 219 edges over 4 records, and they are substantial: `Q74656` has **144
    children**, `Q75282` 59.
  - **`ORPHAN`** — no file, edges one way only. Nothing connects through it, so nothing can
    be severed. 14 edges.

  Reverted the 233, taught `edge_symmetry.py` the split, restricted `cut_edges.py`'s
  data-driven set to `ORPHAN` only, and re-ran: the tool's split matched an independent
  hand-count exactly, 219 / 14. Cut the 14. **Every gate green, zero records lost depth** —
  which is what an orphan reference should cost. `dangling_endpoints` 13 → 4, and the 4
  that remain are exactly the GAP records that must stay.

  **The safety argument I had been making was for the wrong reason.** "A record that does
  not exist cannot be anyone's parent" sounds airtight and is true of `ORPHAN`. What makes
  it safe is not that the record is absent but that **nothing is connected through it** —
  and I never checked that until the gate made me. The condition is now the load-bearing
  half of the comment in `cut_edges.py`.

  New queue item: the four missing records need names before they can be created, and
  creating them is the actual repair for those 219 edges.

- **`csv.DictReader` has been silently dropping 128 records from `persons.tsv`, and a
  standing invariant has been reporting 138 dangling endpoints when the truth is 13.**

  The analysis TSVs are written with plain f-strings and never quote anything. `DictReader`
  defaults to treating `"` as a quote character, so a label containing a double quote
  swallows the rest of the field and the row vanishes. 128 of 107,022 gone, in **every one
  of the 29 scripts that read these files**.

  Everything it caused was a measurement error rather than a data error, which is why it
  lasted: nothing broke, numbers were just wrong. `check_invariants`'s I3 reported **138**
  dangling endpoints against a true **13** — and its own committed baseline listed
  `Q153797` "Ghalib born of Fihr" among the dangling examples. He is a fully populated
  record in Muhammad's ancestry and has always existed.

  Fixed everywhere (`quoting=csv.QUOTE_NONE`), verified against a plain-split read of the
  file — 107,022 both ways, identical sets — and the invariant baseline re-taken at the now
  correct 34 / 283 / 71 / 0 / **13** / 1,209.

  **How it surfaced, which is the part worth keeping.** Last tick I flagged an
  inconsistency in my own status report: `check_invariants` said 138 dangling endpoints
  while my new classifier found 233 dangling *edges*, and I noted those measure different
  things but that I had not confirmed they reconcile. Reconciling them was the whole find.
  The 233 edges involve only 13 unique missing endpoints; the other 125 the invariant was
  counting turned out to be real people its reader could not see.

  **The 233 `DANGLING` removals I meant to do this tick did not happen.** Correcting a gate
  that reports a tenfold-wrong number outranks acting on the number. They are still next.

- **The one-sided-edge count has been wrong since 2026-07-30. 961 of the 4,723 were never
  one-sided.**

  Item 4's headline figures — 96.3% symmetric, 2,325 parent-side-only, 2,398
  child-side-only — came from `edge_symmetry.py` comparing **raw qids**. 39,521 qids in
  this dump are claimed by more than one file, so a parent can name a child by a qid that
  redirects elsewhere while the child declares the canonical one. Compare those raw and the
  same edge appears on only one side. `extract_genealogy.py` canonicalises for exactly this
  reason; this scan never did.

  Corrected: **97.1% symmetric, 1,816 parent-side-only, 1,946 child-side-only, 3,762
  total.**

  **I found it by spot-checking my own new classifier rather than shipping it.** I had
  extended the scan to bucket one-sided edges by what their endpoints are, and it reported
  **897 DANGLING** — edges pointing at records that do not exist. Checking eight of them,
  every single one had a file on disk. `Q107385` is "Fatima bint Amr al-Makhzumi";
  `Q107411` is "Khuwaylid bin Asad". They are ordinary shadow files whose internal id
  differs from their filename. The qid is vacated; the person is not missing. After
  canonicalising, DANGLING is **233**.

  The classification now splits item 4 into work rather than a pile: **233 DANGLING**
  (removable with no judgement), **1,050 PHANTOM** (endpoint is an empty shell), **2,479
  BOTH-REAL** (the actual judgement calls). Per-edge detail in
  `edge_symmetry_classified.tsv`.

  Worth naming: the classifier's first output looked entirely plausible — 897 dangling
  edges is a believable number, and nothing about it invited suspicion. It only fell over
  because the DANGLING bucket makes a *checkable* claim ("this record does not exist"), and
  checking it took one command. A bucket that had merely said "suspicious" would have
  shipped.

- **Fixed the two reporting defects in `fix_mutual_parent_pairs.py`, the one script that
  edits the dump on its own judgement.**

  It repaired 0 of 6 pairs, so it was not doing damage — but it was giving two wrong
  answers, and it is the tool most able to act on them.

  **"Both sides have spouse co-parent evidence, so these are two records of one person and
  need a MERGE."** That is an unjustified leap, and it was in the docstring as a rule.
  A family record reading consistently in both directions is equally what two genuinely
  different people with one reversed edge look like. `Q119481` "Pons Hug d'Entença" and
  `Q124343` "Jussiana d'Entença" have symmetric evidence and are plainly two people —
  different recorded sex, distinct Wikidata items `Q21001415` and `Q14083227`. Acting on
  that recommendation would have fused a man and a woman. It now reports the signal as
  deciding nothing, and names the distinguishing evidence when the pair is two people.

  **It inferred a family for a record that does not exist.** `Q78402` had no item file, no
  shadow and no `persons.tsv` row, and the script reported spouse-coparent evidence for it
  and recommended a merge. Now skipped as a dangling endpoint.

  **The dangling guard is unreachable on live data**, because the edges it protects against
  were removed yesterday — so it is regression-prevention, not an active fix, and an
  unexercised branch is exactly what keeps going wrong this session. Tested against the
  `edges.tsv` as it stood *before* that commit, read out of git: it fires on
  `Q78402 <-> Q78719` and on none of the four real pairs.

  Five pairs remain and the script repairs none of them. That is the right answer: every
  one genuinely lacks direction evidence.

- **`shadow_audit` refreshed and verified by mtime rather than by task status — 0
  disagreements** across 164,456 items, 39,521 qids claimed by more than one file. Checking
  the file's timestamp is the only reason I know it ran; three earlier reports said it had
  when it had not.

- **Removed two claims pointing at a record that does not exist. One whole tangle gone:
  35 -> 34. And I retracted a cut mid-tick after my justification for it collapsed.**

  Cleopatra III (`Q78719`) listed `Q78402` as **both her mother and her child**. `Q78402`
  has no file, no shadow claiming the qid, and no `persons.tsv` row — one of the 138
  dangling endpoints. A record that does not exist cannot be anyone's mother, so both
  claims went, with no judgement call. **Every gate green**, tangles **35 -> 34**, records
  in a tangle 285 -> 283, `records_in_a_cycle` improved and `children_over_2_parents` held.

  **THE PART THAT MATTERS IS THE ONE I TOOK BACK.** I also cut `Q90982 -> Q88454`, the two
  Esthers, claiming their patronymics fixed the direction. They do not. Both readings are
  naming-consistent — *bat Sahlan* married Yosef giving a daughter *bat Yosef*, or *bat
  Yosef* married Sahlan giving a daughter *bat Sahlan* — and under either, each woman is
  correctly named for her own father. The patronymics confirm both fathers and say nothing
  about who descends from whom. That is precisely why the tool reports evidence on both
  sides and refuses to act.

  The depth gate then failed on it: `Q88454` fell from **318 levels to 1**, all 3,525 of
  her ancestors having reached her through that one edge. I could have argued that as proof
  — under reading A she was inheriting her *husband's* line and losing it is correct — but
  it is equally consistent with reading B, where it is a real amputation. **The gate cannot
  distinguish spurious ancestry from real ancestry, and neither could I.** Reverted the
  Esther cut, kept the Cleopatra one, re-ran: green.

  Written into `queue.md`'s rails, because I had been reading `compare_depth` as a verdict:
  **a red gate is not automatically "revert" and a green one is not automatically
  "correct"** — it tells you how much is at stake, not who is right.

  **Three crashes in `cut_edges.py`, all the same missing guard**, and the second landed
  *after* the first edge was already on disk. I fixed the plan phase, then the apply phase,
  then the verify phase. The right fix was at the root: `vals()` now returns `[]` for a
  missing record, because a qid with no file trivially lists nothing. One guard at the
  root beat three at the edges, and I only got there by getting it wrong twice.

- **Merged six empty shells out of the tangles. 291 records in a cycle -> 285.**

  The `PHANTOM-PARENT` hits from yesterday's signal. Each loser is a shell: no label, no
  description, and exactly one claim type (`P39`, same two values and byte-identical hashes
  across all six). They exist in `edges.tsv` only because other records name them in `P20`
  -- the one-sided-edge defect -- and each sits in a tangle recorded in the *same* parental
  role as a real person for the same child.

  **My first verification test was wrong and would have blocked half the work.** I checked
  "are the parents identical", and three of six failed. The right test is **subset**: is the
  shell's edge set wholly contained in the real record's? All six pass that, so merging adds
  no edge and only removes a duplicate node. The extra parents the real records carried
  turned out to be *other shells* -- one import made shells, a second made real records, and
  the real ones picked up shell-parents on the way.

  `Q52709` was the one with positive identification rather than mere structure: no label,
  but its aliases include "kay uyarsh Raja Iran", which is exactly `Q29144`'s label.

  Gates: **records in a tangle 291 -> 285**, the six departures being exactly the six
  merged-away shells, 0 newly tangled, tangle count and largest unchanged;
  `children_over_2_parents` **1215 -> 1209**; `compare_depth` PASS, worst loss 3 -- the
  tangle-shrink arithmetic, not amputation.

  **Corrected the classifier to agree with what I actually did.** It called `Q52709` a
  phantom while I merged it as a duplicate on the strength of its aliases. Aliases are
  identifying content, so `substance()` now counts them. Leaving the two disagreeing would
  have meant shipping a rule I knew mislabelled a case I had just acted on.

  **Not fixed, and not caused by this:** `Q29144` and `Q29148` are recorded as each other's
  parent -- a real mutual-parenthood 2-cycle among the Persian records, independent of the
  shells. `fix_mutual_parent_pairs.py` exists for that shape.

- **Built the same-role parent signal. My first version of the rule was wrong, and
  hand-checking its six hits is the only reason it did not ship.**

  Queue item 2. The rule: two records in the SAME parental role for one child -- both
  `P47`, or both `P48` -- that also share their own parents. It uses no label at all, which
  is the point: this dump's labels are the least reliable thing in it, and the Domitia
  Lucilla duplicate was invisible to all three label-and-id signals.

  It found six collisions. **I checked each against the item files instead of trusting the
  verdict, and all six were wrong as DEDUPEs:**

  - **Four paired a real person against a PHANTOM** -- `Q99368`, `Q99386`, `Q60222`,
    `Q52709`, `Q73284`: records with no label and no genealogical claim of their own,
    present in `edges.tsv` only because something names them in `P20`. Not duplicates of a
    person. One-sided edges, which is item 4's defect.
  - **One paired a real person against `Q78402`, which has no file at all** -- one of the
    138 dangling endpoints.
  - **One paired two DIFFERENT MEN.** `Q72984` *Quintus* Caecilius Metellus (wd `Q929498`)
    and `Q148066` *Marcus* Caecilius Metellus (wd `Q897091`) are **brothers**, both sons of
    `Q73146`, and both recorded as the father of `Q72834`. Distinct praenomina, distinct
    Wikidata items. **Merging them would have been a fabrication.**

  I had written the trap into the queue item myself and got it half right: I guarded
  against a brother-*sister* couple, which the same-role test excludes, and missed that two
  *brothers* both listed as father produce the identical pattern. Same-role is necessary
  and **not sufficient.**

  So the verdict now splits three ways on whether the pair is distinguishable at all --
  `PHANTOM-PARENT`, `WRONG-PARENT-EDGE`, or `DEDUPE` -- and after the split **zero of the
  six are merges.** Calibration check that matters: `Q64582`, the Domitia Lucilla survivor
  this signal was built from, still classifies `real`, so the rule keeps its own founding
  case. Ten cases tested against the live dump.

  **The signal is still worth having.** It surfaced six genuine defects no other detector
  sees, and gave item 4 -- the 4,723 one-sided edges, previously an undifferentiated pile
  -- a concrete entry point of six records inside tangles.

- **The biggest tangle in the dump finally moved: 72 -> 71. The repair was a dedupe, and
  three wrong guesses came first.**

  Queue item 2 said the `Julia Livia` pair was the thing to fix and that "the cycle runs
  through the Rubellius chain". **Both claims were wrong.** `Q139688` is not in a cycle at
  all, and the canonical 21-record cycle does not touch the Rubellii.

  What the cycle actually contains is one chronologically impossible step: `Q73140` "Gaius
  Lincinius Varus" -- a descendant of `Q136506` Flavia Julia Constantia, d. 330 AD -- is
  recorded as the father of `Q73770` "Publius Licinius Crassus", a Republican. A ~450-year
  backwards jump on the shared nomen *Licinius*, exactly the repeating-cognomen collision
  `queue.md` predicts for the long Roman tangles.

  **So I tried to cut it, and the depth gate refused: 358 levels lost across 19,700
  records.** Then the two edges upstream, which cost 1.5M and 1.56M total depth. All three
  were gateways. `cycle_policy.md` says that when a loop can only be broken by cutting a
  gateway the defect is elsewhere -- and I had now confirmed that by guessing three times.

  **Guessing which edge to test is the wrong loop, so I built
  `wiki-scripts/cheapest_cycle_break.py`**: it costs *every* edge of a cycle by the ancestry
  a cut would destroy, and ranks them. Three edges came out at **zero**. Zero cost means a
  parallel path exists, and a parallel path means a duplicate.

  It was `Q64582` "Domitia Lucilla Minor" and `Q139826` "Calvisia Domitia Lucilla" -- **both
  recorded as the mother of `Q63780` Marcus Aurelius**, with the same father and the same
  mother by identity. Merged. `children_over_2_parents` 1217 -> 1215, records in a tangle
  292 -> 291, **largest tangle 72 -> 71**, `compare_depth` PASS with worst loss 1, which is
  the documented arithmetic of a tangle losing one member rather than any amputation.

  **All three of my duplicate detectors were blind to it**, and that is the useful part.
  The Wikidata-id signal needs both sides to carry an id and only one does; both label
  signals need the labels to match, and "Domitia Lucilla Minor" does not normalise to
  "Calvisia Domitia Lucilla". The evidence that actually decided it uses **no label at
  all**: two records in the SAME parental role for one child, sharing their own parents.
  One child cannot have two mothers. Written up as the next queue item, with the trap
  attached -- sharing parents *and* a child is not enough by itself, because a
  brother-sister couple produces exactly that and this genealogy has them. The same-role
  part is what makes it a duplicate.

  **A cheap edge is where a cut is affordable, not where it is correct.** The tool says so
  in its own output, because ranking by damage would otherwise read as ranking by
  correctness -- and the repair order still puts UNMERGE and DEDUPE ahead of CUT. Here the
  cheap edge and the wrong edge coincided, which is what made it safe.

## 2026-07-31

- **Genghis Khan reaches Aster. Bridge A applied, both halves, on Emma's "Both?".**

  `planning/lineage_bridges_proposed.md` Bridge A, via a new `wiki-scripts/add_bridge_edges.py`.
  `Q37401` Genghis Khan had **zero** ancestors; he now has **1,272 and reaches `Q1` Aster**.
  403 records gained depth, **0 lost**, total ancestral depth **+173,295**. No tangle
  introduced, no invariant regressed.

  - **A2** creates `Q200000` "C2 (M217)" under `Q1164` Haplogroup C and attaches Khaidu
    beneath it -- mirroring `Q54433` "Sinitic O2a2b1a2 (F114)", which already sits between
    the Yellow Emperor's line and Adam. C2-M217 is a real clade in a real position, so this
    invents no person.
  - **A1** attaches Khaidu `Q53399` under `Q153230` on the Borjigin chain.

  **The A1 attachment point is a judgement call and it is flagged as one, in the script,
  the queue and here.** Rashid al-Din gives Bodonchar → Buqa → Dutum Menen → Qaidu, which
  puts Khaidu under `Q153230`. The *Secret History* puts him one generation lower, under
  `Q153225`. Both placeholders are unlabelled, undated, and carry no `wikidata_qid`, so
  **nothing in the dump distinguishes them.** I took the report's recommendation and made
  the alternative a one-edge move rather than pretending the evidence decided it.

  **A consequence I will not bury: Khaidu now has two fathers**, the Borjigin node and the
  haplogroup node. That is what "both" means structurally, and the report anticipated it
  ("A1 and A2 are not exclusive"). But it **deviates from the dump's own precedent** --
  `Q87862` Youxiong has its haplogroup as its *only* father, so the established device is
  one-or-the-other. Flagged for Emma; either edge drops cleanly.

  **Deliberately not done:** retiring the 14 placeholder nodes below `Q153225`. The report
  recommends it, but it is a DELETE -- repair-order step 4 -- and was never approved. The
  bridge does not depend on it.

  **Why a script rather than a hand edit.** An edge lives in two places, the child's `P47`
  and the parent's `P20`, and `edges.tsv` is built from the union -- so a half-declared
  edge reads as real while a one-sided repair silently fails. That is what made the Tros
  fix look done while two cycles were still closed. `add_bridge_edges.py` writes both
  directions, propagates to shadows, and then **verifies from the files rather than from
  its own plan.**

- **Merged all three Adnan records, on Emma's decision. First fully-green verify of the
  session, and the first repair that measurably ADDED ancestry.**

  M3 from `adnan_merge_proposed.md`. Emma: *"You merge them lol"* -- she answered the
  question by refusing its premise. The report asked *which* Adnan survives and could not
  choose, because each was right by a different measure: `Q111364` had the only Wikidata
  id, `Q86433` had the 434-ancestor route toward Abraham, `Q65555` was the one Muhammad's
  line actually reaches. Merging keeps all three. Survivor `Q65555` by the lower-QID
  convention.

  **Checked the cycle risk before applying rather than reasoning from the prose.** `Q86433`
  routes *upward* into the Emesene material while `Q65555` runs *downward* to Muhammad,
  which is exactly the shape that closes a loop. No ancestor set of any of the three
  intersects another's descendant set, so it could not.

  **Gates, all green including `compare_tangles` -- the first time this session:**
  0 tangles introduced, removed or reshaped; 0 records changed tangle. **0 records lost
  depth, 654 gained, total ancestral depth +158,370.** `Q86433`'s route toward Abraham is
  now reachable by the 8,527 descendants below `Q65555`. Every prior repair this session
  was a dedupe that shrank a tangle; this is the first one where the rails' claim that
  "merges only ever add ancestry" was actually measurable, and it measured.

  **Two errors in the report, found by reading the graph instead of trusting it.** It says
  `Q65555` "reaches nothing upward" -- it has three parents and 10 ancestors. And the
  report's conditional recommendation was already spent: it said to decide R1 first, R1 was
  decided on 2026-07-30, and it then said that if the splice is kept the merge set "is not
  worth applying at all". Emma's instruction overrides that, and the +158,370 says the
  merge was worth applying.

  **Two residues left standing and flagged, not buried:** the survivor now has **four
  parents**, because `Q66385` "Imaam 'Udd" and `Q66394` "Udd son of Umaisi" look like one
  man -- the `'Udd`/`Humaisi` tangle the report lists as untraced, and still untraced. And
  the survivor's label is `'Adnaan Bin Imaam 'Udd` while it now carries wd `Q22338875`,
  whose name is simply *Adnan*. Relabelling is Emma's per the `Tros` precedent.

- **The pre-commit gate blocked this merge and was right. Two bugs in `merge_cluster.py`,
  both invisible to the tool's own verification.**

  The first attempt was refused by `.githooks/pre-commit`: `Q65555`'s shadow files
  disagreed with it. The tool had just reported *"all files agree with their survivor"*.
  The gate was correct and the tool was wrong.

  **Bug 1 -- the shadow set is computed once, before any merge.** Merge 1 rewrites the
  loser and its shadows as copies of the survivor, which makes every one of those files a
  **new claimant** of the survivor's qid. Merge 2 then updates the survivor and the shadows
  known at the start, leaving the new claimants frozen at merge-1 state. Measured:
  `Q86433.json` and `Q98118.json` held **10** children while the other four held **12**.

  **This shape had never occurred before.** `porcia` (3 merges) and `prachetas` (2) each
  merged into *different* survivors. `adnan` is the first cluster with **two merges into
  one survivor**, which is the only way to produce it.

  **Bug 2 -- the verification could not have caught it.** It asked only whether each file's
  internal `id` equalled the survivor's. A stale copy still says `id=Q65555`, so it passed.
  And it swept the same pre-merge shadow set, so it never looked at the two files that went
  stale. A check that reads the wrong set *and* the wrong field will report success
  forever. Now it compares the whole record across the union of pre-merge shadows and
  everything rewritten during the run.

  Fixed both, then **reverted the merge and re-ran it from the pre-merge state** rather
  than patching the two files by hand -- the point was to prove the fix works, not to make
  the symptom go away. It reported `reconciled 2 file(s) left stale by an earlier merge
  into Q65555: Q86433, Q98118`, exactly the two the gate had named, and all six claimant
  files are now byte-identical. The graph numbers came out identical to the first run
  (+158,370 depth, 654 gained, 0 lost), which is the expected result: the reconciliation
  changed durability, not ancestry.

  **The rails already said editing the canonical file alone is not durable.** This was the
  same failure one level up -- writing every shadow, but computing which files *are*
  shadows before the merges that create more of them.

- **Built the parallel-import signal, and it immediately refused the merge I had queued.**

  Queue item 2 asked for a third duplicate signal: *same label + same parents + a
  same-labelled spouse or child under a different qid* -- the parallel-subtree shape, where
  nothing below a pair is shared by identity because the whole branch was imported twice.
  Both existing signals require a shared *record*, so neither can see it.

  Built it with a guard, and the guard is the part that mattered. **A parallel subtree has
  to be merged as a cascade**, twins included, or the survivor inherits duplicate relatives.
  So every twin pair is checked first, and a **strictly one-way ancestry relation** between
  any of them means the "duplicate" is really an ancestor of its twin.

  **`Julia Livia` fails that check, and my queue entry for it was wrong.** I had written
  that the spouse and child pairs "have to be merged with it". They must not be:
  `Q139688` "Gaius Rubellius Blandus" is the **great-grandfather** of `Q70718` of the same
  name via `Q72338` -> `Q71628`, and `Q70152` "Rubellia Bassa" is an ancestor of `Q139691`
  of the same name. That is a real repeating-cognomen line -- the signature `queue.md` warns
  is behind the long Roman tangles -- and the cascade would have collapsed three generations
  of Rubellii. New `GENERATION-COLLAPSE` verdict, ranked second so it is read before the
  DEDUPE-CANDIDATE sitting under the same evidence.

  **The guard's subtlety, which took a wrong first draft to see: inside a tangle every pair
  is mutually reachable**, so a naive "is one an ancestor of the other?" test fires on
  everything and means nothing -- it would have blocked every dedupe this tool exists to
  find. Only a strictly one-way relation is informative; `mutual` is documented as the
  uninformative case.

  **Three test expectations were wrong before the code was.** I asserted the Julia Livia
  direction backwards; assumed Aster `Q1` would be unrelated to a random record when it is
  the ancestor of nearly everything; and assumed Aditi and Diti, both children of Daksha,
  were unrelated siblings -- Aditi reaches Diti through Surya -> Yama -> ... -> Prachetas ->
  Daksha, which is precisely the cycle that makes them a tangle. Each time I traced the
  actual path rather than adjusting the code to match the guess. The `none` case is now
  found by search instead of by assumption, and reports which pair it used.

- **`shadow_audit` refreshed after the three merges -- 0 disagreements dump-wide**, closing
  the caveat the last status report carried.

- **Applied the two dedupes the new detector found. First repairs in this repo found by a
  tool rather than by hand.**

  `prachetas` (2 merges) and `metellus` (1). Both were surfaced by the label-plus-
  corroboration signal added earlier today, and **neither could ever have been found by the
  old shared-Wikidata-id detector** — no side of the Prachetas cascade carries an id at all.

  **`prachetas` is a two-level cascade and had to be merged as one.** `Q1968`/`Q49707`
  "Prachinbarhi" share **both parents by identity**, not merely by label — `Q1978`
  Havirdhana and `Q49767` Havirdhani. Their sons `Q1955`/`Q49634` "Prachetas (10 sons)" are
  both fathers of `Q153390` Daksha, which lists both of them. Merging only the lower pair
  would have left the survivor with two duplicate fathers, which is the trap the Porcii
  Catones cluster documented.

  **`metellus`**: `Q72984`/`Q144060`, same label, same father `Q73146` by identity, both
  recorded as father of `Q72858`.

  **Gates.** `compare_depth` **PASS**, worst loss 2 — the arithmetic artefact of a tangle
  shrinking by two members, not amputation. `check_invariants` **PASS and improved**:
  `children_over_2_parents` 1218 → 1217, Daksha going from two fathers to one.
  `compare_tangles` exits 1, and its lists are the documented dedupe signature — **records
  newly inside a tangle: 0**, the three that left are exactly the three merged-away qids
  (`Q49634`, `Q49707`, `Q144060`), the introduced tangles are the removed ones minus exactly
  those qids (16→14, 14→13), largest tangle unchanged at 72. Committed on that reading, as
  before.

- **Fixed the merge tool's dry run, which was under-reporting what it would do.**

  The preview printed only the five genealogical properties. The apply path has carried
  everything else since the 38-dropped-properties fix, so a reader checking the plan could
  not see that birth and death dates and external ids were about to move. That gap between
  what the preview showed and what the tool did is the same shape as the "strictly additive"
  claim that was true of the graph and false of the records.

  Caught it by noticing the `metellus` dry run reported only `P61` while `Q144060` visibly
  held `P56`, `P57` and three external ids the survivor lacked — i.e. by checking a claim I
  had written into the cluster comment before trusting it. The preview now lists both the
  properties carried from the loser alone and the ones where both sides differ. `Q72984` did
  gain `P1185, P1819, P4159, P56, P57`.

  **35 tangles / 292 records** across all four sources.

- **Taught `propose_tangle_repairs.py` the duplicate signal it was blind to. Three tangles
  came out of a set where all 35 read REVIEW.**

  Queue item 2. The DEDUPE detector keyed on a **shared Wikidata id**, which needs *both*
  sides to carry one. It missed `Q72615`/`Q72693` (one side had an id) and `Q73425`/`Q73017`
  (neither did) — both real duplicates, both merged by hand today.

  A shared label alone is far too weak to substitute: this dump is full of Romans with
  repeating cognomina and `queue.md` warns the long Roman tangles are exactly that. So each
  new signal requires the label match **plus positional corroboration from the graph**:

  - **SHARED-CHILD** — both records are parents of the *same* record. Strong, and treated as
    decisive: one man has one father, so a child naming two identically-labelled fathers is
    the dump stating the duplication about itself. This is what decided `Q72615`/`Q72693`.
  - **SHARED-PARENT** — identically-named siblings. Ranked `DEDUPE-CANDIDATE`, explicitly
    *suspicious, not settled*, because two brothers really can share a praenomen.

  Labels are normalised for case and whitespace **and for a word repeated adjacent to
  itself** — "Pacuvius Calavius Calavius", "Diogo Afonso Afonso de Aguiar". Without that
  collapse the Calavius pair does not match at all.

  **Found, and each checked by hand against the item files rather than trusted:**
  `Q1955`/`Q49634` "Prachetas (10 sons)", both fathers of Daksha, with their own fathers
  being two records both labelled "Prachinbarhi" — a cascade, not a pair;
  `Q72984`/`Q144060` "Quintus Caecilius Metellus", same father, both fathers of `Q72858`.
  **Nothing was applied** — item 2 was to teach the tool, and applying is item 3.

  **Proved it would have caught the two it historically missed.** Both pairs are already
  merged so they cannot be found live; what is testable is the normalisation that failed.
  Ten cases, including three negatives that must NOT match — a cognomen extension
  ("Scipio Nasica" vs "Scipio Nasica Serapio") is a different man, not a duplicate. All pass.

  **Named a class it still cannot see.** `Q77386`/`Q138467` "Julia Livia" ranked only
  CANDIDATE, yet has identical parents, a husband *Gaius Rubellius Blandus* on both and a
  daughter *Rubellia Bassa* on both — each under **two different QIDs**. Nothing is shared by
  identity because the entire subtree was imported twice, and both signals require a shared
  *record*. Written into the queue rather than built blind.

- **Notion wins. Four of Emma's five open decisions had been answered for a day and no repo
  file knew.**

  Emma: *"Notion wins pretty much all the time as per central command rules."* Recorded as a
  standing rule at the head of `queue.md`'s AWAITING EMMA section: the board arrives as
  `notion-open-questions.md` and `notion-work-loop.md` at the repo root, and where this repo
  and the board disagree, **the board is right and the repo is stale.**

  Her answers were sitting as sub-bullets on the Work Loop page, which nothing read.
  Recorded and converted from questions into work: **Adam→Genghis — do both A1 and A2**;
  **chapter 181's ten sons — the data moves, the chapter stands**; **M3 — merge all three
  Adnan records, do not pick a survivor**; patriarch overlay — euhemerism, already applied
  earlier today. Kosala and Jimmu↔Heo remain genuinely open.

  On the ten sons I flagged rather than absorbed the hard part: the report says the data fix
  "means inventing nine named sons". Recording nine invented people is not what "the ten
  sons exist" licenses. Go and find whether Garakguk-gi names them; if it does not, that is
  a second question for Emma.

- **The Tros naming question was obsolete, and it was holding a correct edge hostage.**

  Emma answered "What? Explain better", so I read the record instead of the report. There is
  nothing left to name — the unmerge was already done. `Q74698` is labelled **Uranus**
  (aliases *Uranus / Caelus / Ouranos*), its parents are **Aether and Dies**, which is
  Hyginus's parentage for Caelus, and its **59 children are the entire Ouranos roster** —
  Titans, Cyclopes, Hecatoncheires, Gigantes, Erinyes — with **zero Trojan claims left**.
  The four mythic cycles `cycle_policy.md` describes are gone; none of those records is in a
  tangle.

  Worse than merely stale: **`Tros → Ops` sat in `propose_tangle_repairs.py`'s
  `PENDING_UNMERGE` as blocked-on-Emma, and it is a correct edge.** Ops is Rhea;
  `Ouranos → Rhea` is right. A tool was holding a correct edge open as a question against
  her. Moved to `PROTECTED`; `PENDING_UNMERGE` is now empty.

- **Fixed the table-escaping bug the hub reported back, and the fix's own trap.**

  `build_cycles_notion.py` did not escape `|` in cell text, so `Q137449`
  ("Lleuki|Nest ferch Gwerstan ap Gwaithfoed") emitted **ten fields against a nine-column
  header**. The hub had built a recovery for it; a recovery downstream of a generator that
  emits broken rows is a repair, not a fix.

  The obvious patch would have reintroduced the bug: names are truncated to 46 chars, and
  escaping *before* truncating lets a cut land between a backslash and what it escapes,
  leaving a trailing backslash that escapes the cell delimiter itself. Truncate first, then
  escape backslash before pipe. Tested both boundary cases explicitly — all six cases emit
  exactly ten delimiters and no trailing backslash — and confirmed against the three real
  records.

- **`qa_cycles.tsv` was stale and `cycles_review.md` was publishing the stale number.**
  It said 296 records in a tangle where `check_invariants` said 295, because
  `dump_qa_errors.py` had not been re-run after the merge. Regenerated the chain; all four
  sources now agree at **35 tangles / 295 records**. The rails line in `queue.md` still
  quoted **34 / 278** and now carries the current figures plus a warning not to quote it.

- **Emma decided the patriarch overlay: deliberate euhemerism. The relabel is dead.**

  > "the mesopotamian ones is completely intentional euhemerism I edited the notion
  > document several times to say it was"

  The Genesis 11 line under Mesopotamian royal names — `Shu-Ilishu` as Noah, `Puzur-Ashur`
  as Shem, nine records in one continuous chain — is intentional. **Fix: none.** The
  records keep their labels.

  This was the single largest open question in the dump and it should never have been open.
  `CLAUDE.md` has listed it as a confirmed-deliberate import since 2026-07-30, under the
  standing rule that *everything surprising that is not an error was imported deliberately
  by Emma; surprising is not evidence of broken.* The rule was written down and then not
  applied to the case it names. Emma had recorded the decision repeatedly and it kept
  coming back as a question.

  Withdrawn everywhere it was still live, because a stale recommendation is one work-loop
  tick away from being executed:
  - `patriarch_overlay.md` — decision recorded at the top; the three readings kept below as
    the record of how it was decided.
  - `epic_vs_dump.md` **Finding 1** — supersession notice; the "relabel Q70439 to Noah,
    Q70454 to Eber" recommendation marked dead in all four places it appeared, including
    the summary table row and the second banner that still called it "still right".
  - `HANDOFF.md` open question 3, `queue.md` AWAITING EMMA item 3.

  **Every "DATA ERROR" verdict resting on Finding 1 is withdrawn.** Where a chapter says
  "descendant of Noah" and the dump says `Shu-Ilishu`, the dump is right and they are the
  same figure by intent — the prose and the data agree on the person and disagree on the
  name, which is the euhemerism working rather than a defect.

  **Deliberately kept live**, because they survive the decision and are about parentage and
  position rather than naming: `Q70439`'s spurious third parent `Ilushu` (a real
  multi-parent error, now explicitly decoupled from the dead relabel it was to have landed
  with); the position-only rows `Naram-Ilum` and `Shu-Sin`; and `Kanʿān` recorded as Noah's
  son rather than grandson.

- **`shadow_audit` refreshed — 0 disagreements dump-wide**, current as of both of today's
  merges. The status report flagged the previous figure as stale rather than quoting it.

- **Merged `Q72615`/`Q72693` "Quintus Aemilius Lepidus"; my own depth gate cried wolf and I
  fixed the gate, not the threshold.**

  Queue item 2. The evidence was stronger than the item suggested, because the `lepidi`
  merge had since landed: `Q72514` canonicalises to `Q72434`, so both Quinti are the father
  of **one** man — and `Q72434` lists **both of them as its fathers**. That is the dump
  stating the duplication about itself, the signature that decided the Porcia pair. Same
  label, same father `Q72786`, same offices, same sex, same arms filename. Survivor
  `Q72615` by lower QID; it also holds the mother and spouse. `Q72434` drops from two
  fathers to one.

  Checked before applying that the new `Q144279 -> Q72615` edge closes no loop: `Q144279`
  is not a descendant of `Q72615`, whose only child is `Q72434`.

  **The merge process was killed mid-run**, so the tool's own 164k sweep never reported. I
  re-ran the assertion independently rather than assuming: all five files (survivor, loser,
  three shadows) agree, and **nothing resolves to the vacated `Q72693`**.

  **Then `verify_repair.py` said DO NOT COMMIT, and it was half wrong.** Both graph gates
  went red. The numbers reconciled exactly, which is what made it diagnosable:
  total depth `-27,815` = `Q72693`'s own 259 + 27,556 records at exactly `-1`.

  - The `-1`s are arithmetic. The Scipio tangle went 18 members to 17, and depth counts a
    component's size as its contribution, so everything below it reads one level shallower.
    One duplicate left a cycle; no ancestry was severed.
  - `Q72693` at `-259` was a **bug in compare_depth.py** — a record that is absent
    afterwards did not lose ancestry, it stopped existing, which is precisely what a merge
    does to the loser. It was already reported on its own `absent afterwards` line and
    counted as a loss as well.

  Fixed the false positive. **Changing a gate that just failed is the exact shape of
  weakening a test to make it pass, so it does not get taken on trust:** re-ran it against
  the synthetic `edges.tsv` missing only `Q73893 -> Q73794`, and it **still fails at -273
  levels**. The threshold was not touched. Deletions still surface on the `absent` line.

  `compare_tangles` still exits 1 and I left it alone — a dedupe inside a tangle genuinely
  changes the partition. Its lists show the correct signature: `records newly inside a
  tangle: 0`, sole departure `Q72693`, largest tangle unchanged at 72. That read is a human
  one, so `verify_repair.py` now prints the dedupe-vs-regression signatures instead of
  ruling on it, and `queue.md` carries the same. **Committed against a non-green
  compare_tangles, deliberately and on that reading.**

  Residue not guessed at: the survivor inherits **two fathers**, `Q72786` and `Q144279`,
  both "Marcus Aemilius Lepidus". Pre-existing on `Q72693`, both edges already in the
  graph. It cannot be settled apart from queue item 1 — `Q144279`'s other child `Q73011` is
  one of the three fathers `Q72786` claims, so merging those two would close a 2-cycle.
  Folded into item 1 as a fourth Lepidus rather than resolved.

- **`verify_repair.py` — the repair ritual is one command now, and it can fail.**

  Session was killed mid-repair by a Windows crash; picked up from the transcript. Two
  things were outstanding: the Calavius dedupe sitting uncommitted, and queue item 2.

  **Committed the Calavius dedupe** (`Q73425` -> `Q73017`). Verified before committing, not
  after: the merge's own 164k-file sweep found nothing still resolving to the vacated qid,
  `check_invariants` held at 35 tangles / 296 records, and `compare_depth` showed zero
  ancestry lost. `Q72801` Cornelia is down from three fathers to two.

  **Then closed queue item 2, which asked for a depth gate wired into the verification
  ritual.** The tool half already existed — `compare_depth.py` was written the same day the
  Scipio cut was reverted. It was wired to nothing. The ritual lived as prose in `queue.md`
  telling whoever was mid-repair to remember four scripts in the right order, which is how
  the Scipio cut passed review in the first place: every gate it needed already existed.

  So `wiki-scripts/verify_repair.py` runs `extract_genealogy` -> `compare_tangles` ->
  `compare_depth` -> `check_invariants` and exits non-zero naming the failure.
  `--snapshot` handles the before-state. Shadow consistency stays with the pre-commit hook,
  which checks the records actually staged and is better targeted than an `edges.tsv` pair.

  **Proved it fails, rather than asserting it passes.** The rails already say a gate that
  cannot fail is worse than none, so it got a two-file mode and was run against a synthetic
  `edges.tsv` missing only `Q73893 -> Q73794` — the reverted cut. `compare_tangles`
  reported it **clean**; `compare_depth` failed with **27,554 records down, worst loss 273
  levels**. Width said yes, depth said no. That disagreement is now in `cycle_policy.md`
  and `queue.md` as the reason not to read a green `compare_tangles` as a verified repair.

  Not done and not attempted: queue item 1, the `Q72786` unmerge. Three coherent
  father+mother couples on one record, one father being the son of another. Which parentage
  is real is Roman prosopography and Emma's call — NEEDS-DECISION, not guesswork.

- **REVERTED the Scipio cut. It severed a load-bearing gateway and I did not check.**

  Emma asked one question — "no risk of load bearing ancestor gateways being lost?" — and
  the answer was no, there was a large one. The cut below is chronologically correct and
  was still the wrong move.

  `Q73893 → Q73794` was the **sole upward gateway for the entire Scipio line**. Measured
  after the fact:

  | record | ancestors deep before | after |
  |---|---|---|
  | `Q73794` Gnaeus Cornelius Scipio | 263 | 0 |
  | `Q73692` Scipio Barbatus | 264 | 1 |
  | `Q73299` Scipio Africanus | 267 | 4 |
  | `Q72957` Nasica Serapio | 269 | 12 |

  and the 263-link chain ran all the way to **`Q1` Aster**. The cut made Scipio Africanus,
  Barbatus, the Nasicae and Cornelia a rootless island. `cycle_policy.md` describes this
  exact situation and says what to do: "If a cycle can only be broken by cutting such a
  join, that is a signal the real defect is elsewhere in the loop — go find it." I broke
  the cycle instead of finding the defect.

  **The methodological hole, which is the part worth keeping.** I verified with
  `compare_tangles.py`, and it reported 18 records freed, 0 tangles introduced, 0 reshaped
  — a clean win by every gate in the repo. But `compare_tangles.py` measures **width**:
  how many records sit inside a tangle. Load-bearing here means **depth, upward**, and
  *nothing I ran measured that*. This is the same error the rails already call out about
  `qa_cycles_load.tsv` ranking by descendants lost, and I reproduced it in a new tool
  while quoting the rule against it. A repair can be green on every existing check and
  still amputate 263 generations.

  Reverted by restoring the three records and all 14 claiming files from `5fce715a9`.
  Tangles back to 35, records in a tangle 296. `invariants.json` reset to match — the
  I1 "cycles must not increase" failure this produced is deliberate, not a regression.
  The cut set is kept in `cut_edges.py`, disabled and annotated, as the record.

  Queued: find the actual defect in the loop (prime suspect is the downward half —
  `Q72801` Cornelia has three fathers), and **build the depth gate that would have caught
  this before it was committed**.

- **The 18-record Roman tangle is gone — two edges, and Scipio Africanus, Barbatus, the
  Nasicae and the Aemilii Lepidi all come free. Tangles 35 → 34, records in a tangle
  296 → 278.**

  The loop ran `Q72434 → Q73893 → Q73794 → Q73692 → … → Q72801 → Q72786 → Q72615 →
  Q72434`. `Q73893` is Lucius Cornelius Scipio Asiaticus Aemilianus (wd Q7234050), consul
  83 BC — correctly a child of the Lepidus record, since he was an Aemilius by birth. But
  he was recorded as father of `Q73794` Gnaeus Cornelius Scipio, whose son is Scipio
  Barbatus, consul **298 BC**.

  **The unsigned-BC warning in the queue item was the whole game.** The dump stores these
  dates unsigned: Q73893 as 200/77, Barbatus as 400/300. Read naively as AD, 200 then 400
  looks like a perfectly ordinary grandfather → grandson, which is presumably how the edge
  survived. Read as the BC magnitudes they are — and they must be, since `Q72957` and
  `Q72434` in the same chain are stored *signed negative*, and Q73443's +0211 is exactly
  Scipio Calvus's death in 211 BC — the descent below Q73794 runs cleanly forward
  (400→306→256→230→205→182 BC) while Q73893 sits at 200/77. His grandson is born some 140
  to 200 years before him. The repeating-cognomen collision the queue predicted: the
  ancient Scipiones hung under a 1st-century Scipio because both are "Cornelius Scipio".

  UNMERGE and DEDUPE were both ruled out before cutting — Q73893 carries one identity, not
  two (Lepidi parents, 1st-century Wikidata id, and its other child `Q72248` Scipio
  Salvito is Caesar's associate at Thapsus in 46 BC), and Q73794's wd duplicates nothing.
  Both sides Roman, so no tradition join at risk.

  **Cut both parents, not just the one that closed the loop.** `Q99342` Aemilia Paula is
  Q73893's wife and Q73794's recorded mother, and she is not in the tangle — so cutting
  only the father edge would have broken the cycle while leaving an equally impossible
  claim standing purely because no loop happened to run through it. New
  `wiki-scripts/cut_edges.py` removes an edge from both sides and every claiming file.

  `compare_tangles.py`: 2 edges, 1 tangle removed, **0 introduced, 0 reshaped, 0 records
  newly inside**, 18 freed.

- **`check_invariants.py`'s I2 could never fail, and 11 records were exploiting that.**

  It says "no record is its own parent — self-loops must be zero, always" and reported 0
  every time. Its default `--source tsv` reads `edges.tsv`, and `extract_genealogy.py`
  drops self-edges before writing it, so `q in par[q]` was unsatisfiable by construction.
  A gate that cannot fail is worse than no gate, because it reads as evidence.

  The extractor now writes what it drops to `qa_self_edges.tsv` and I2 reads that. Turned
  on, it immediately failed with **11 records listing themselves as their own parent or
  child** — `Q72786` Marcus Aemilius Lepidus (11 shadow files), two Aurelii Cottae, Appius
  Claudius Crassus, Alba Silvius, and the primordials Terra, Erebos and Nyx.

  All 11 cut, data-driven from that file rather than a hand-kept list. This carries no risk
  of the kind the repair order guards against: a self-edge links a node to itself, so it can
  never be the only link between two traditions, and since the extractor already excluded
  them the graph could not change. It didn't — 34 tangles / 278 records / largest 72,
  identical before and after. The item files now agree with the graph that was always
  computed from them, and I2 reports 0 **honestly**.

- **My ten merges today silently dropped 38 properties. Restored, and the tool fixed so it
  cannot happen again.**

  I reported those merges as "strictly additive". That was true of the **genealogy** and
  not of the **records**, and I did not make the distinction. `merge_cluster.py` and
  `apply_cato_cluster_merge.py` unioned only `P20/P42/P47/P48/P61` and then rewrote the
  loser's file as a copy of the survivor — so any property only the loser held vanished
  from the dump. Caught while dry-running the Lepidi merge and noticing the survivor
  "gained nothing" even though the loser carried birth and death dates.

  What was lost: external identifiers (`P1185` Rodovid, `P1819` Geni, `P4159`, `P6821`
  Alvin, `P9495`, `P64`) and — the ones that matter — **`P56`/`P57` birth and death dates
  on six people**, including Cato Salonianus, Cato Licinianus, Atilia and Porcia Catonis.
  `edges.tsv` reads only the genealogical properties so the graph was never affected, but
  `persons.tsv` carries dates, so six people quietly lost theirs.

  All 38 restored from the pre-merge commit by the new
  `wiki-scripts/backfill_merged_properties.py`, propagated to every claiming file. Three
  properties where both sides differed (`P94` arms filenames) were left alone and reported
  rather than guessed at. `merge_cluster.py` now carries over every property the survivor
  lacks, and reports conflicts instead of resolving them.

- **Aemilii Lepidi deduped; the guard I wrote this morning was wrong and is now
  outcome-based.**

  `Q72434` and `Q72514` both carry `wd Q435329` (Marcus Aemilius Lepidus, cos. 78 BC),
  share the spouse Q72517 Appuleia and four children. **Both sides have shadow files**, so
  the input-side guard — "the loser must have no shadows" — forbade the merge in either
  direction. That guard was a proxy for the real invariant and a redundant one: the tool
  already repoints every shadow of the loser in the same pass. Replaced with the
  outcome-side assertion, which is strictly stronger — after the merge it **sweeps all
  164,536 item files** and asserts that nothing still resolves to a vacated qid. Not
  deleted, replaced.

  Confirmation the merge was right: `children_over_2_parents` fell **1223 → 1218**. Five
  children had literally the same man listed twice as a parent.
  `compare_tangles.py`: the 19-record Roman tangle became 18, losing exactly `Q72514`,
  with **0 records newly inside a tangle**. Tangles 35, records in a tangle 297 → 296.

- **Two defects found in the same tangle, both queued rather than rushed.**

  `Q73893 → Q73794` is what actually closes that 18-record loop, and it is ~270 years
  backwards: Lucius Cornelius Scipio Asiaticus Aemilianus (cos. 83 BC) is recorded as the
  father of the Gnaeus Cornelius Scipio who fathered Scipio Barbatus (cos. **298 BC**).
  The repeating-cognomen collision the queue predicted. Queued with the chronology to
  verify from the item files first, since this dump stores many BC dates unsigned.

  And **`Q72786` is its own father and its own child** — with 11 shadow files.
  `check_invariants.py` reports `self_loops: 0` and always will: its default `--source tsv`
  reads `edges.tsv`, and `extract_genealogy.py` drops self-edges at extraction. **I2 is
  vacuous on the default source and cannot fail.** Queued to fix the gate before the data.

- **The 81 unread files are explained.** `shadow_audit.py` reads 164,455 of 164,536, a gap
  I have been carrying as unexplained for three status reports. Scanned every file: **0 are
  unparseable — exactly 81 contain the literal JSON `null`.** Empty placeholders, skipped by
  design by both the extractor and the audit via `isinstance(data, dict)`. Nothing to
  repair, and nobody needs to investigate it again.

- **Wikidata cross-check folded into the cycle proposals — and the fold immediately paid
  for itself: one tangle gone, 36 → 35.**

  The queue asked to fold `qa_cycles_vs_wikidata.tsv` into `qa_cycles_proposed.tsv`. That
  join could not be done as stated, because `qa_cycles_proposed.tsv` is keyed to the old
  **non-deterministic** cycle enumeration — "cycle 7 of 25" is not a stable referent when
  consecutive runs disagreed on how many cycles existed. So the fold rebuilds against the
  one well-defined object, the strongly connected component: new
  `wiki-scripts/propose_tangle_repairs.py` → `qa_tangle_repairs.tsv` / `.md`, one row per
  edge inside a tangle with the Wikidata verdict attached and a repair proposed under the
  `cycle_policy.md` order.

  **The fold's main job turned out to be restraint.** Of 16 distinct `contradicted` edges,
  15 say only *"Wikidata records no link between them"* — an absence of evidence, not a
  refutation. Three of those are live and **correct**: `Belus -> Danaus` and
  `Anchiroe -> Danaus` are precisely the parents `cycle_policy.md` assigns. A naive fold
  that cut on the cross-check would have severed exactly the cross-tradition joins the
  genealogy exists to make. Those edges are now in a `PROTECTED` list the tool refuses to
  propose cutting, sourced from the policy doc rather than inferred.

  Only one verdict is decisive — *"the link the other way round"*, where Wikidata records
  the same pair with parent and child swapped. Exactly one edge qualified, so the evidence
  went where it could actually be used: **`fix_mutual_parent_pairs.py` gained an S4
  `wikidata` signal**, alongside its existing spouse-coparent / dates / patronymic ones.
  It fired once, on `Q139601 -> Q70988`, and it was the *only* signal that could decide
  that pair — no usable dates, no patronymic, no co-parent. Wikidata records Lucius
  Scribonius Libo Drusus as the parent of Marcus Livius Drusus Libo; the dump also asserted
  the reverse, giving Q70988 a second father he does not need (he already has Q72272).
  Dropped the two claims encoding the false direction.

  **That script had the shadow bug.** It wrote only `ITEMS/<qid>.json` — the exact failure
  CLAUDE.md records as having reverted ten applied repairs at once on 2026-07-30. It now
  rewrites every file claiming an edited qid and verifies afterwards that they agree. This
  was not hypothetical: **Q70988 has four shadow files**, so the old code would have left
  the repair to be silently undone the moment `Q70988.json` stopped being the lowest
  claimant.

  Verified: edges −1, `compare_tangles.py` reports **1 tangle removed, 0 introduced, 0
  reshaped, 2 records freed** and nothing else moved. Tangles **36 → 35**, records in a
  tangle **299 → 297**, `children_over_2_parents` **1224 → 1223**. `check_invariants` PASS
  with two invariants improved; baseline ratcheted to 35 / 297 / 72. Shadow propagation
  self-check passed on all six files.

  Next up and now ranked at the top of the queue: `Q72434` / `Q72514` both carry
  `wd Q435329` inside a 19-record Roman tangle. It is blocked by a guard I wrote too
  strictly this morning — `merge_cluster.py` refuses a pair whose loser has shadows, but
  the tool already repoints those shadows in the same pass, so the refusal forbids safe
  merges. The fix is to replace it with the outcome-side assertion that no file still
  claims the loser's qid, not to delete it.

- **The Porcia residue is closed: Q78063 and Q144042 are one woman, and two records above
  her had to merge with them.**

  Yesterday's Porcii Catones dedupe deliberately left this standing — Cato the Younger came
  out of it with six children because both import branches contributed daughters. The dump
  settles the identification without any guessing: **Q78066 "Marcus Calpurnius Bibulus"
  (wd Q316775) is a single record listing BOTH Porcias as wives**, and both are mothers of
  a son of his. On top of that, Q144042 carries wd Q255448, whose own Wikidata name is
  "Porcia Catonis" — letter for letter the label on Q78063.

  That forced the two records above her, or the survivor would have inherited two duplicate
  mothers and Cato the Younger two duplicate wives: **Q72493 / Q144102 "Atilia"** (both his
  wives, both mothers of the Porcia pair; Q144102 carries wd Q2334126) and **Q72681 "Gaius
  Atilius" / Q144174 "Atilius Serranus"** (both the father of that Atilia; Q144174 carries
  wd Q12275873, whose Wikidata name is "G. Atilius Serranus" — the man Q72681 is named for).
  Three pairs, each forced by the one below it.

  **The queue item had the merge direction backwards** — it said "dedupe Q78063 into
  Q144042". Q78063 has shadow files and Q144042 has none, so merging that way would have
  vacated a shadowed qid, which is the exact mechanism that manufactured the phantom Cato
  2-cycle. Survivor is the low side in all three pairs. That rule is now enforced in code
  rather than remembered: `merge_cluster.py` refuses any pair whose loser has shadows.

  **Left unmerged on purpose:** Q141439 (wd Q18280006) and Q141441 (wd Q94959905) are also
  Porcia daughters of Cato the Younger, but by Marcia — a different wife — and they carry
  two distinct Wikidata items. Likewise Q77899 (wd Q3655959) and Q141508 (wd Q104224002),
  both sons of Bibulus who now land on the merged Porcia, are plausibly one man but carry
  different ids. Merging either pair would be a guess.

  Two new tools, because the lessons kept living in prose: `wiki-scripts/merge_cluster.py`
  (generalised cluster dedupe, enforcing the merge-direction rule) and
  `wiki-scripts/compare_tangles.py` (compares SCC *partitions* between two `edges.tsv`
  snapshots — introduced, removed, reshaped, and records entering or leaving a tangle).

  **The dry run earned its keep.** It showed the merge would import references to Q141438
  — a qid the *previous* merge had already retired into Q72496 — which would have given the
  merged Porcia two fathers that are the same man. The graph would have canonicalised them
  into one edge and hidden it. Fixed by folding the global redirect map into the tool's
  canonicalisation before any union.

  Verified: edges 128,682 → 128,679 and persons 107,039 → 107,036, exactly the three merges;
  `compare_tangles.py` reports **0 tangles introduced, 0 removed, 0 reshaped, 0 records
  entering or leaving** — 36 tangles / 299 records / largest 72, unchanged. `check_invariants`
  PASS, shadow gate consistent on all six qids, merged records confirmed to have exactly one
  father and one mother each.

- **The cycle counter has been wrong the whole time. Every "cycles X → Y" number in this
  log predating today is unsound.**

  Found while verifying the Cato merge below. Three consecutive runs of
  `dump_qa_errors.py` over one *unchanged* `edges.tsv` returned **45, 50 and 46 cycles**.
  Two defects in its cycle section: it iterated `set`s of qid strings, and Python
  randomises string hashing per process, so the DFS traversal order — and therefore which
  cycles it found — changed on every invocation; and it marked nodes `BLACK` on pop and
  never revisited them, so it only ever found *some* cycles per tangle. It was never
  counting cycles at all: one tangle of n nodes can hold exponentially many.

  That invalidates the `52 -> 54` regression `check_invariants.py` was written to catch,
  and every before/after cycle figure in `devlog.md`, `queue.md`, `HANDOFF.md` and
  `GENEALOGY_QA.md` from before today. `check_invariants.py` itself was always sound — it
  uses Tarjan, and an SCC partition is unique regardless of traversal order, which is why
  its numbers were the stable ones.

  Fixed: `dump_qa_errors.py` now computes SCCs over sorted adjacency and emits **one
  canonical shortest cycle per tangle**, with new `tangle_size` / `tangle_qids` columns
  (existing readers use `DictReader`, so they are unaffected). Five consecutive runs now
  produce a byte-identical file, and its totals — **36 tangles, 299 records** — match
  `check_invariants.py`'s independent Tarjan exactly. The well-defined quantity is the
  tangle, not the cycle; repairs should be verified against `tangled_components`.

- **Cato the Elder resolved: not three records of one man, but a parallel import of the
  whole Porcii Catones family. Seven pairs deduped, zero tangles moved.**

  `queue.md` asked whether Q148133, Q73005 and Q73167 are one man, or whether Q73167
  ("Marcus Porcius Censorius") is Cato's father or his son Licinianus. The dump answers it
  outright: **Q73167's mother is Q73329 Licinia, who is Cato's own wife.** A man cannot
  have his son's wife for a mother, so Q73167 is Cato's son by Licinia — Marcus Porcius
  Cato Licinianus, whose cognomen means "Licinia's son". The label was the trap: `P5` reads
  `Marcus Porcius /Censorius/`, the source having carried the *father's* cognomen in the
  surname slot. There is no third Cato and there never was.

  The real defect was one branch under `Q7xxxx` and an independent import of the same
  family under `Q14xxxx`/`Q15xxxx` — seven duplicate pairs, five of them confirmed by a
  Wikidata id **both** sides carry (Q180081, Q435959, Q1181865, Q1372970, Q193506); the
  other two forced by those five. Repair-order step 2, DEDUPE: nothing cut, no
  cross-tradition join touched, every merge strictly additive.

  Survivor is always the low side, and that is the whole lesson of the earlier reverted
  attempt: every `Q7xxxx` record here has shadow files and no `Q14xxxx` record has any, so
  merging the other way **vacates a shadowed qid**, a shadow immediately wins it, and its
  claims get injected — which is how the phantom `Q148133 <-> Q73167` 2-cycle appeared out
  of a graph that never contained the edge. Every file claiming any of the 14 qids — 34 in
  all, survivors, losers and every shadow of both sides — was rewritten in the same pass;
  28 of them actually differed and are in the commit, the other 6 already held identical
  content.

  Verified by reconstructing the pre-merge graph exactly (untouched edges from the current
  extract, the rest re-derived from the `HEAD` versions of the merged records and their
  neighbours through the pre-merge redirect map). The reconstruction lands on **128,689
  canonical parent edges — exactly what the independent full extract reported beforehand**.
  Tangles **36 → 36**, in-tangle records **299 → 299**, largest **72 → 72**, and the two SCC
  partitions are the *same sets*, not merely the same size: **0 tangles introduced, 0
  removed**, none containing a merged qid. Persons 107,046 → 107,039 and edges 128,689 →
  128,682, i.e. exactly the seven merges. `shadow_audit.py`: 0 disagreements.
  `check_invariants.py`: PASS, baseline ratcheted 38/379/88 → 36/299/72.

  Q73167 relabelled to **Marcus Porcius Cato Licinianus** (it now carries wd Q1275684, so
  the "Censorius" label contradicted its own id); the old label is kept as an English alias.
  Left standing on purpose: Q78063 "Porcia Catonis" versus the three Porcia records the
  other branch gives Cato the Younger. Q78063 is probably Q144042 — the Bibulus descent
  lines up — but no id decides it, so it is a new queue item rather than a guess.
  Full writeup: `wikibase/analysis/cato_cluster_resolved.md`.

- **The three long Iberian cycles are gone. 74 records freed; the Heracles join survives.**

  The queue item said "unmerge/dedupe — do NOT cut", on my own earlier reading that
  `Barbara`/`Bárbara` and `Proba`/`Proba Rogas` were accented duplicate pairs. **That
  reading was wrong.** Their actual claims:

      Q99597 Bárbara: father=Q99607 (which is Q82122's spouse), mother=Q82122
      Q99558 Proba Rogas: father=Q99575 (Q99573's spouse), mother=Q99573

  Every one is a mother-and-daughter pair with the father correctly recorded as the
  mother's spouse — daughters named after mothers, which is ordinary. Merging them would
  have collapsed real generations out of the line. Another instance of reading a similar
  name as a defect, in a repo where that assumption has been wrong every time.

  With unmerge and dedupe genuinely inapplicable, the repair order licenses a cut. The edge
  is `Q81339 Antonio Ambrosio de Aguiar Coutinho -> Q82122 Barbara, imperatriz of Rome`:
  it appears in all three long cycles, and it is the only edge running against the chain's
  direction — everything else descends **from** Heracles **to** the de Aguiar family, while
  this one makes a Portuguese noble the father of a Roman empress.

  Checked before applying, not after: with the edge removed, Heracles Q99544 is still an
  ancestor of de Aguiar Q79582. Confirmed again on the regenerated extract. The
  cross-tradition join — the reason the chain exists at all — is untouched, and Q81339
  keeps its other eight children.

  Removed from both P20 and P47, propagated to 2 shadows. Result: records in a cycle
  **379 -> 305**, largest component **88 -> 73**, zero cycles still touching the
  Iberian/Heracles stretch, invariants PASS. All five remaining cycles of length >= 20 are
  Roman.


## 2026-07-30

- **Wired the gates to a pre-commit hook, and tested that it actually blocks.**
  `.githooks/pre-commit` + `wiki-scripts/check_staged_shadows.py`. Install with
  `git config core.hooksPath .githooks`.

  The gates I built today only ran when I remembered to run them, and today that assumption
  failed three times. The specific damage: ten applied repairs sat silently revertible for
  hours because their shadow files were never updated. This hook fires on any staged
  `wikibase/items/*.json` and blocks the commit if a record's shadows disagree with it.

  It checks only the qids actually touched, so it is sub-second — the full gates need a
  10-minute extract regeneration (`check_invariants.py`) or a 164k-file scan
  (`shadow_audit.py`), and the hook prints a reminder rather than running them.

  **Verified in both directions rather than asserted.** Dropped one child from Q74698,
  staged it, and the commit was refused with exit 1 naming Q88740 and Q129977. Reverted,
  re-staged, and it passed with exit 0. The first version dumped two 59-element lists to
  show a one-element difference, so it now reports just the difference:
  `Q74698 child: Q88740.json has ['Q132029'] (the other does not)`.

  `core.hooksPath` is local git config and cannot install itself, so CLAUDE.md now carries
  the one-line install command.


- **Shadow audit: I overstated the problem by three orders of magnitude, then found it was
  aimed at my own repairs.**

  Last tick I said the graph "already reflects arbitrary filename-order winners across
  39,533 qids". Measured: 39,527 qids do have multiple files, but **only 21 of them
  disagree** on parents or children, covering **31 edges**. The other 39,506 are identical
  copies. Zero edges existed only by filename luck.

  Two things the audit caught that I had wrong. First, I wrote it assuming the extractor
  keeps the lexicographically-first filename; it sorts **numerically by QID**
  (`key=lambda p: int(p.stem[1:])`), so the winner is the lowest QID number. String `min()`
  named the wrong winner for any record whose shadows differ in digit count. Discarded that
  run. It also pins the Cato mechanism exactly: Q73005 is numerically lowest and won, and
  once vacated the next-lowest is **Q87608**, which carries `P47=['Q73167']`.

  Second, and worse: **ten of the 21 were records I edited today.** Q74698's shadows still
  held the Trojan children and Erichthonius-as-father — precisely the claims the unmerge
  removed. My repairs were durable only while the edited file kept winning. And two pairs I
  reported as "already one-directional, left alone" — Marullinus Q69886/Q70388 and Granius
  Q78384/Q78507 — are one-directional *only* because the lower QID won; their shadows
  assert the reverse edge. I drew that conclusion from the extract instead of the files.

  Propagated each winner to its 52 shadows. Zero edges changed, because the winner already
  determined the graph. Verified: invariants identical to baseline (38 tangled components,
  379 records, largest 88, 0 self-loops, 1,224 multi-parent), and shadow disagreements
  **21 -> 0**, suppressed edges **31 -> 0**.

  Standing rule added to queue.md: after editing any record, rewrite every file claiming its
  qid, and keep `shadow_audit.py` at zero.


- **Reproduced the Cato cycle. The cause is shadow files, and it is systemic.**

  I had twice asserted a mechanism for this cycle and been wrong twice, so this time I
  re-applied the merge, regenerated, and read the edges.

  **39,533 qids in this dump are claimed by more than one file — 57,410 shadow files.**
  `extract_genealogy.py` keeps only the first file it sees per qid (`if qid in seen_ids:
  continue`) and silently drops the rest, so which claims survive depends on filename
  order. Shadows routinely carry claims the canonical file does not have.

  Canonical `Q73005.json` had `P47=[]`. Five shadows — Q87608, Q99390, Q111052, Q185613,
  Q185617 — all carry `P47=['Q73167']`. While Q73005.json was canonical it won the contest
  and those were suppressed. Merging rewrote it to `id=Q148133`, which **removed it from
  the contest for qid Q73005**; a shadow won instead, injected `Q73167 -> Q73005`, and
  canonicalisation rewrote that onto Q148133. The loop closed. No ancestor/descendant
  precondition could have caught it — the edge did not exist beforehand, which is exactly
  why my earlier check returned False on its own test case.

  **The fix is structural:** when redirecting B into A, repoint B's shadows too, so no qid
  is left vacant. Wired into `apply_dup_merge.py`; claims held only by shadows are reported,
  never silently absorbed. 31 of the 35 duplicate pairs have a shadow on one side.

  **And there was live damage from the earlier commit.** 5 of the 8 merges in `31d1c8c6a`
  left vacated qids with shadows still claiming them — Q120943, Q121094, Q116586, Q122928,
  Q90525. Q122928 was injecting `P47=['Q111221']`. All five repointed.

  Verified: invariants identical to baseline — 38 tangled components, 379 records, largest
  88, 0 self-loops. Worth noting the cycle *basis* moved 49 -> 53 across the same change
  while the SCC count did not move at all. That is the metric doing its job; the basis
  count is noise and I spent much of today quoting it.

  Queued the obvious follow-on: this is not merge-specific. The graph as it stands already
  reflects arbitrary filename-order winners across 39,533 qids.


- **Built the standing invariant gate. Tried to build a merge precondition, failed to
  validate it, and threw it away.**

  `wiki-scripts/check_invariants.py` — the thing that was actually missing all session.
  Every check until now was bespoke and written after the fact, which is how a merge
  silently added cycles. This one measures strongly-connected components rather than a
  cycle basis, which matters: an SCC is canonical, whereas the cycle basis the detector
  reports is not stable across runs and is exactly what made my earlier comparisons
  meaningless. Current state, now baselined in `wikibase/analysis/invariants.json`:
  **38 tangled components, 379 records inside one, largest 88, zero self-loops,
  138 dangling endpoints, 1,224 multi-parent children.** Verified both directions — it
  passes on the current tree and exits 1 on a simulated regression.

  **The correction that matters.** I attributed the Cato cycle to a specific mechanism:
  "Q73005 had Q73167 as a child while Q73167 had Q148133 as a child." That is not true.
  Q73167 has no children at all and Q148133 has no parents. I asserted a causal story from
  a correlation — the new cycle contained a merge survivor — without checking the edges.
  The precondition I then wrote on that story returned False for the exact case it existed
  to catch. An unvalidated safety check is worse than none, so it is removed, and
  `apply_dup_merge.py` now carries a warning saying plainly that it has no such check and
  that the mechanism is not understood.

  What actually closes that loop is still unknown, and finding it is queued. My present
  guess is something in how `save(b, load(a))` interacts with redirect canonicalisation in
  the extractor, but that is a guess and it is labelled as one.


- **A merge I applied created a cycle. Caught it, reverted it, and the precondition that
  would have prevented it is now queued.** 52 -> 49 cycles after the correction.

  Merging 9 duplicate pairs took the count to 54, not down. Comparing chain strings said 31
  new and 29 resolved, which was noise — the detector re-roots each cycle at a different
  head. Comparing canonically by edge set: 10 resolved, 12 new, and exactly **one**
  attributable to me: `Q148133 <-> Q73167`. Neither Q73005 nor Q73167 had been in any cycle
  before. Q73005 had Q73167 as a child; Q73167 had Q148133 as a child; merging Q73005 into
  Q148133 joined two individually-valid edges into a loop.

  The contradiction is diagnostic. Both records carry `wd Q180081` (Cato the Elder), so if
  they are the same man, Q73167 cannot be both his parent and his child — one edge is
  wrong. Which one depends on whether `Marcus Porcius Censorius` is a third Cato duplicate,
  his father, or his son Licinianus. **That is a judgement call and I did not make it.**
  Reverted only the Cato merge, kept the other eight, and added a `DO_NOT_MERGE` guard
  carrying the full reasoning so a future run cannot silently repeat it.

  **The real defect was in my script, not in the data.** It checked that parent sets do not
  conflict, which is not sufficient: a merge is safe only if no third record ends up both
  above and below the survivor. Queued as an explicit induced-cycle precondition, which
  also unblocks the 27 deferred pairs by making them safe to attempt.

  Re-verified after the revert: 49 cycles, 10 resolved, 7 differing — and **zero** of those
  touch any merge survivor or duplicate. Worth recording that the detector reports a cycle
  *basis* rather than a stable set, so individual cycles are not comparable across runs even
  though counts are.

- **Two extract runs died mid-write** and left `persons.tsv` truncated at 70,763 of 107,055
  lines. Auto-flush caught it both times by checking the line count rather than committing
  whatever showed as modified. Restored from git — safe because the extracts are derived and
  the item JSONs are the source of truth — and re-ran to completion.


- **71 cycles -> 52, and the count is now honest.** Regenerated the derived extracts with
  `extract_genealogy.py` and re-ran `dump_qa_errors.py`. Everything downstream had been
  reading `wikibase/analysis/*.tsv` files that went stale the moment I started editing
  items — and `qa_cycles_proposed.tsv` was *already* stale by eight rows before that,
  because `9c0299d8` repaired eight mutual pairs and nobody re-ran the detector. So the
  "71 cycles" figure I have been quoting all session was wrong from the start.

  Current: **52 cycles**, 1,224 multi-parent children (was 1,230). All seven records I
  repaired today — Ouranos/Tros, Danaus, Belus, Nilus, Titus Manlius Torquatus, Lucius
  Fulvius Curvus, Marcus Valerius — are out of every remaining cycle, checked against the
  regenerated file rather than assumed. The extract diff is exactly 13 removed edges, which
  matches what was applied.

  Remaining shape: 10 two-cycles, 8 threes, 9 fours, and a tail running to one 46. The long
  Iberian chains are still there and are next, by unmerge and dedupe rather than cutting.

- **Also fixed the work-loop cron**, which was still instructing every tick to "PROPOSE,
  DON'T APPLY" — the rule Emma revoked. Left alone it would have quietly restored the
  behaviour she had to ask me twice to stop. The new prompt carries the apply-directly
  policy, the synoptic-ancestry framing, the repair order, and the two-places-per-edge
  warning.


- **The Tros unmerge needs no unmerge — the correct record was already there.**
  `wikibase/analysis/tros_unmerge_proposed.md`, propose-only. I had diagnosed Q74698 as
  Tros-of-Dardania merged with a primordial figure and proposed splitting it into two new
  records. Looking properly: there are two records labelled `Tros`, and **Q132327 (wd
  Q599482) is already correct and clean** — right parents (Erichthonius of Dardania,
  Astyoche), right spouses (Callirhoe, Acallaris), exactly the five Trojan children. The
  Trojan Tros's edges have simply been *duplicated onto* Q74698, which is a different figure
  entirely. Every duplicated edge is already held correctly by Q132327, so the fix creates
  nothing and deletes no record.

  **Q74698 is Ouranos.** Strip the seven duplicated edges and its 65 remaining children, all
  by Terra, are the complete canonical offspring of Ouranos and Gaia — the Titans, the
  Cyclopes, the Hekatoncheires, the Gigantes, the Erinyes — and its remaining parents,
  Aether + Dies + Terra, are Hyginus's genealogy for Caelus. The identification comes from
  the child list, not the label. What the record should be *called* is Emma's call, not
  mine; I am not naming a figure in a scripture project.

  Eight edge removals in total, the eighth being `Danaus → Nilus` (Nilus's parents are
  Oceanus and Tethys, both already recorded, and Nilus is Danaus's ancestor via Anchiroe).
  **Verified by simulation rather than asserted**: rebuilt the parent map without those
  edges and re-tested all 71 recorded chains. All four mythic cycles break. Nilus keeps
  Oceanus and Tethys; Danaus keeps Belus and Anchiroe — the Greek/Egyptian join that must
  not be cut; Atlas → Electra → Dardanus untouched.

  Two things the verification turned up. **Only 63 of the 71 recorded chains still exist** —
  earlier repairs already broke eight, so the proposals file is stale and the cycle count is
  overstated. Queued a regeneration. And **`Oceanus` (Q90309) carries Danaus's Wikidata id**
  (Q161419), which `Danaus` also carries — an ID collision in the same neighbourhood, left
  for the ID-repair worklist.


- **Emma: "Muhammad's genealogy there is 100% intentional." And: cycles only.** Two
  corrections to how I was working, and the second is the bigger one.

  R1 is answered — the Emesene route stays. I had the counter-evidence and walked past it.
  The record's own label is `Fihr born of Iamblichus`, which is not what a name-collision
  merge produces, it is what somebody writes when they mean it; and I wrote in the report
  that connecting Quraysh to the Sampsigeramids "is a real genealogical speculation" and
  then filed it as a defect anyway. By the report's own logic that also withdraws M5–M12
  (merging the `Banu Ismail` chain into Muhammad's line would pull the authored route
  apart) and the verdict that the `Banu Adnan` chain is filler. Withdrawn in place, with
  what survives listed separately.

  **The scope correction matters more.** Emma is looking for cyclical errors only, and a
  large number of unexpected things in this dump are intentional. I spent this session
  running general-defect sweeps and reporting everything surprising as broken — the
  patriarch overlay, the Emesene splice, the Banu Adnan chain. At least one of those is
  authored and I now think the patriarch overlay is too, for the reason I already gave in
  that report and then under-weighted: nobody renaming Noah by accident also gives the
  renamed record Naamah and Emzara as wives. **Unexpected is not evidence of wrong here.**
  The standard is impossibility, and a person being their own ancestor is the one thing
  that always qualifies. Queue rescoped to the 25 unresolved cycles; the five existing
  reports marked do-not-apply and do-not-extend pending her rulings.

  Also confirmed for the record: **nothing was removed.** All five cycles artifacts
  (`cycles.html`, `qa_cycles.tsv`, `qa_cycles_load.tsv`, `qa_cycles_proposed.tsv`,
  `qa_cycles_vs_wikidata.tsv`) are untouched this session — `git diff 54dca9a00..HEAD`
  shows eight files, none of them a cycles file. The only queue.md deletions were the two
  items I completed and the wrong cron schedules on T1.


- **Cleared the queue. Two chains traced, one suspicion of mine retracted.** Addendum on
  `adnan_merge_proposed.md`. (a) The `Banu Adnan` chain is fifteen records of ordinary Arab
  given names in no recognised king list, running *downward* from Adnan toward Emesa — a
  bridge somebody built to reach `Sampsiceramus I`, not a transmitted genealogy. It lives
  or dies with R1 and should not be decided separately. **I had flagged `Ithobaal` there as
  a Tyrian name and suspected a second splice. There isn't one** — three unrelated records
  share that name and none of them is Ithobaal I of Tyre. One real defect found: `Malichus`
  fathers both Sampsiceramus I and **`Creator BRAHMA`**, which is a spurious edge.
  (b) The `'Udd`/`Humaisi` tangle is the opposite case — `'Udd` genuinely is Adnan's father
  in the standard Adnanite genealogy, so the content is orthodox and the transmission is
  what broke: the same two names appear as several records apiece, two rows carry three
  parents, and Q67552's *label* is somebody's working note, "Humaisi' direct to Addi \ Udd
  desc Malchut ben Abraham", saved into the name field.

  The active queue is now empty. Five reports are written and every open item is a decision
  Emma owes back, not work that is blocked — moved them into an `AWAITING EMMA` section on
  the board rather than leaving them to read as live queue items.

- **The whole of Genesis 11 is in the dump under Mesopotamian royal names.**
  `wikibase/analysis/patriarch_overlay.md`. I had reported this as two mislabelled records.
  It is nine, and they form one continuous chain from Lamech to Nahor: `Shu-Ilishu` is
  Noah, `Puzur-Ashur` is Shem, `Ishme-Dagan` is Arpachshad, `Naram-Ilum` is Shelah,
  `Ilum-bani` is Eber, `Iddin-Sin` is Peleg, `Shu-Sin` is Reu, `Ur-Ninurta` is Serug. The
  identifications are forced by the children, not by the names: Puzur-Ashur fathers Elam,
  Ashur, Lud and Aram — four of Shem's five sons in Genesis 10:22 — and Ilum-bani fathers
  Joktan and Iddin-Sin, which is Eber's pair. **Only the patriarchs in the direct line were
  renamed. Every branch child kept its biblical name.**

  Two attachment points. Noah has *two fathers* — Lamech, and `Ilushu`, who heads the
  Sargonic dynasty of Akkad running up to Rimush and Sargon's wife Tashlultum. And the
  complete First Dynasty of Babylon, Sumuabum through Hammurabi to Samsuditana in correct
  order, hangs off Serug as a side branch.

  **I don't think this is corruption, and I'm not acting as if it were.** A careless merge
  that renamed Noah to Shu-Ilishu would have no reason to also give Shu-Ilishu *Naamah and
  Emzara* as wives — the two traditional names for Noah's wife. Nor to include `Gionitus`,
  Noah's apocryphal fourth son from Pseudo-Methodius, or the Septuagint's extra generation
  Cainan. That looks like deliberate euhemerism: someone identifying each patriarch with a
  specific historical Mesopotamian ruler. If that reading is right the fix is a note, not a
  relabel. The evidence does not settle it and the two fixes are opposites, so it goes to
  Emma undecided. Superseding notice added to the earlier report so nobody acts on its
  narrower recommendation.

- **Muhammad's ancestry leaves the Arab genealogy for twelve generations and passes
  through the Roman client kings of Emesa.** Went in expecting a duplicate-record merge
  (`wikibase/analysis/adnan_merge_proposed.md`); the duplicates are real but they are
  downstream of a splice. Walking Muhammad (Q65705) up his agnatic line gives the
  traditional Quraysh sequence for eleven generations and then `Fihr born of Iamblichus`
  (Q153798) — the label says it outright. In every Arab genealogy Fihr's father is Ghalib.
  Here it is a Hellenistic priest-king, and the line spends twelve generations among the
  Sampsigeramids of Emesa before rejoining an Arab chain at `Malichus Banu Adnan`. That is
  why Muhammad sits 38 generations below Adnan where tradition puts him at about 21.

  **The correct chain is in the dump, unused.** The `Banu Ismail` series (Q85869 → … →
  Q86433) holds the Adnanite/Quraysh sequence in correct order — Nizar, Mudar, Ilyas,
  Kinana, al-Nadr, Malik, Fihr, Ghalib, Lu'ay, Ka'b, Murrah, Kilab — which is exactly the
  segment the Emesene splice displaced. It is wrong at one end: Adnan terminates the chain
  as its youngest member, 22 generations below his own descendants, Ma'ad is missing
  entirely, Qusayy and Abd Manaf are inverted, and seven names appear that are in no
  Quraysh list. Twelve merges and six repairs proposed, nothing applied.

  The hinge is which of the three Adnan records survives, and the data does not decide it:
  Q111364 has the Wikidata id and nothing else, Q86433 has the route to Abraham, Q65555 has
  the descent to Muhammad and nine children. Each is right by a different measure. That one
  goes to Emma, and it has to be decided after the Emesene cut, not before.

  Left untraced and queued: the `Banu Adnan` chain begins with `Ithobaal`, a Tyrian royal
  name, which looks like the same splice a second time.

- **Swept the epic's genealogy claims against the dump; the biggest finding wasn't the one
  I went looking for.** `wikibase/analysis/epic_vs_dump.md` — 432 candidate lines from a
  predicate sweep of `gaiad_full.md`, 153 naming a wikidata-linked figure, 40 assertions
  checked individually. 22 confirmed, 9 data gaps, 4 data errors, 1 prose error, 3
  unresolved. Nothing edited on either side.

  **The Noah node is wearing a Sumerian king's name.** Chapter 132 names the antediluvian
  line down to "Lamech, the father — there was born a son. Noah", then "Shem, Ham,
  Japheth." The dump has that chain, correctly, through Lamech — and then Lamech's son,
  the father of Ham and Japheth, whose two named spouses are Naamah and Emzara, is
  labelled **`Shu-Ilishu` (Q70439)** and carries the Wikidata id of a king of Isin. The
  record actually labelled `Noah` (Q99058) is unrelated and childless. `path_up(Japheth,
  Q99058)` is NO PATH: nothing in the dump is descended from anything called Noah. Same
  overlay one branch over — Joktan's father, who should be Eber, is `Ilum-bani` (Q70454),
  another Isin king. A Mesopotamian king list has been laid over the patriarch line,
  keeping the biblical edges and swapping the names. It sits under the entire Table of
  Nations, including the Turkic chain Bridge A wants to use for Genghis.

  **Jimmu is not descended from Amaterasu, and it's one wrong edge.** Chapter 190 asserts
  the descent four ways; three fail. `Hoori` (Q6460) has the right mother
  (Konohananosakuya-bime) and the wrong father — a Yayoi placeholder node instead of
  **Ninigi (Q6483)** — so Ninigi's own son is missing from his children and the most-cited
  genealogical claim in Japanese tradition has no path in the dump. Repointing one edge
  restores it. The fourth claim is the chapter's fault: Toyotama-hime is Jimmu's
  grandmother, not his great-grandmother, in the myth and in the dump both.

  **The Heo Hwang-ok chapter, which is what sent me looking.** "Bore him ten sons" against
  one child; "two took her surname" against zero descendants labelled Heo; Ayodhya against
  zero parents. "Millions of modern Koreans" is not a defect — that one is true of the
  world and the dump is a genealogy, not a census. Also: chapter 185 is *more* accurate
  than the dump, which collapses Hayk→Aram to one edge where Armenian tradition has six;
  and chapter 191's thirty-generation Adnanite line — which I first reported as absent —
  is present after all. I had checked descendants of `Ishmael` Q129307 and found no Adnan.
  Abraham has **two** Ishmael records, and the whole 36-generation Banu Ismail chain hangs
  off the other one, `Ismail Ancestor of the Arabs` (Q85869). Qedar is duplicated with him,
  and there are three Adnans. The consequential part: Muhammad descends from `'Adnaan Bin
  Imaam 'Udd` (Q65555) in 16 generations — close to the traditional count — and that record
  reaches nothing, while the Adnan that does reach Abraham sits 38 generations above him.
  The fix is a merge, not a build. Report corrected and the queue item rewritten to match.
  Queued both follow-ups.

- **Two of the three "missing" lineage bridges are not missing the way we thought.**
  Drafted `planning/lineage_bridges_proposed.md` (proposals only — nothing applied to the
  dump) plus `wiki-scripts/graph_probe.py`, a read-only walker so every number in it is
  reproducible.

  **Adam → Genghis is one edge, not a bridge.** The Mongol origin lineage is *already in
  the dump and already Adam-descended*: Kosala kings → Sihahanu → Suddhodana → the Buddha
  (Q153343) → Rāhula (Q153331) → БОРТЭЧИНЭ / Börte Chono (Q153311) → the full Secret
  History chain → БОДОНЧАР / Bodonchar (Q153243) → БУКА / Buqa (Q153235) → and then it
  runs out into fourteen content-free "Great Descendant" placeholders and stops. Meanwhile
  Khaidu (Q53399, b. 1030) sits eight generations above Genghis with no parents. Somebody
  imported the Mongol Buddhist chronicle genealogy and left it one edge short of the man
  it exists to explain. Recommended fix: name Q153230 as Dutum Menen, attach Khaidu under
  it, retire the placeholder tail. Fallback that invents nothing: `Haplogroup C` (Q1164)
  is present, Adam-descended, and childless — Genghis is C2-M217, so a C2 node under it
  joins him the same way `Sinitic O2a2b1a2` joins the Yellow Emperor's line.

  **Jimmu ↔ Heo Hwang-ok cannot be drafted and I am not drafting it.** 744 years separate
  them in the dump's own dates, Heo's single child is a Gaya king, and no Japanese or
  Korean source puts her near the Yamato line. Building it means inventing the connecting
  figures, which is the stop condition on the queue item. What *is* available, one edge
  and fully sourced, is Prince Junda (Q9935, son of Muryeong of Baekje) → Yamato no
  Ototsugu (Q7687), currently a parentless root and father of Emperor Kanmu's mother —
  the Shoku Nihongi descent Akihito acknowledged in 2001. That joins Japan to Korea. It
  does not reach Heo. Recommending the bridge be re-scoped rather than forced.

  **Kosala → Heo has the best warrant and the worst data.** The Samguk Yusa's Garakguk-gi
  putting Heo's origin at Ayuta/Ayodhya is a primary source, and it needs exactly one
  parent edge. But the 58 Kosala records are three parallel Geni imports of the same king
  list, so any edge added now lands on an arbitrary duplicate; and the sourced Ayodhya
  list ends at Sumitra in the 4th c. BCE, leaving ~350 years to Heo that no source fills.
  Held behind dedup.

  Incidental defects logged: 138 edge endpoints have no `persons.tsv` row (including
  Q153645, the terminal of that Borjigin chain); Kosala birth dates are positive CE years
  for pre-Buddha kings; Adam (Q152973) has three parents; Prince Junda is recorded as born
  twelve years before his own father.

- **Started using Wikidata, which I should have done from the start.** Everything in
  this day's earlier entries was name heuristics — Roman cognomina, Iberian patronymics,
  BC-date guessing — over a dump where 60,085 records carry a `wikidata_qid` that simply
  answers the question. I had generalised "the dump is the only copy" from CLAUDE.md into
  "don't fetch anything"; that rule is about the dead Miraheze wiki, not about Wikidata,
  which is live. Emma called it. Two new read-only scripts:
  `check_cycles_against_wikidata.py` and `audit_wikidata_ids.py`.

  **Cycle edges vs Wikidata:** 186 confirmed, 33 contradicted, 6 inherited, 289 unknown.
  27 of 70 cycles are decided outright, no heuristics needed.

  **`Pons Hug d'Entença` is Wikidata's bug, not ours.** Q21001415 lists Jussiana
  (Q14083227) as both his mother and his child *on Wikidata*. The dump copied it
  faithfully. Emma's instinct that these were "bullshit wikidata" was right, and it
  means "the import broke it" was the wrong frame for that case.

  **ID audit over all 60,037 distinct IDs** (~4 min threaded): 88.63% ok, 10.38%
  unverifiable (placeholder or cross-script labels — benign), and ~595 records (~1%)
  genuinely wrong: 331 pointing at non-persons, 127 name mismatches, 96 IDs claimed by
  several records, 32 sex conflicts, 9 deleted items.

  **1% is not a 1% problem, because of where they are.** `Ops` -> Paul Bildt, a Dutch
  film actor. `Tros` -> Uranus. `Danaus` -> Oceanus. `Xu Fu` -> Watatsumi, and Xu Fu
  carries the Jimmu descent. All in the mythic tier that sits under 46 of the 67 cycles
  and carries 34,365 descendants.

  **Systemic: Japanese names were romanised through Chinese pinyin.** 69 of the 127 name
  mismatches are Latin-vs-CJK, and consistently so — 徳川 stored as `De Chuan` not
  Tokugawa, 細川 as `Xi Chuan` not Hosokawa, 岩倉 as `Yan Cang` not Iwakura, 池田 as
  `Chi Tian` not Ikeda. The kanji were read as Chinese. Here the `wikidata_qid` is right
  and the local *label* is wrong — the reverse of every other finding — and it explains
  why name matching kept failing across the Japanese block. Also `Q6439` is labelled
  `kontol`, Indonesian profanity, pointing at 帝臨魁: vandalism, not transliteration.

  Two of my own bugs, recorded because both produced confident wrong numbers:
  - The audit first reported 1,961 IDs `missing`. They were batches that failed and
    never reached the cache. Unfetched is not missing; a re-run resolved it to 9.
  - It first reported 1,581 records as `not_a_human`, because the class list did not
    allow biblical figures, kami, naiads, Oceanids or disputed humans — all of which
    this genealogy is full of. Widening it brought the number to 331.

- **Repaired 8 mutual parent pairs in the dump** (`fix_mutual_parent_pairs.py`), on
  Emma's explicit authorisation for this class. This is the first script here that
  writes to the dump; everything else proposes.

  The shape is not what it looked like. The contradiction usually sits inside a *single*
  record: Q78507 carries both `P47 Father = Q78384` and `P20 Child = Q78384`. Marcus
  Granius is a real man with a real wife who picked up one reversed claim about his own
  son, so the repair is deleting that claim, not deleting a node. My earlier "phantom
  duplicate record" reading of these was wrong.

  8 of 22 pairs had independent signals that agreed; 13 claims removed across 13 items,
  255 lines, no reformatting. Left alone: 3 needing merges (both sides have spouse
  co-parent evidence — one person in two records), 1 conflict (Uematsu Takamasa b.1705 /
  Iwakura Hiromasa b.1746: the family record and the dates point opposite ways), and 10
  with no evidence at all, mostly Roman. Direct pairs: 22 -> 14, verified two ways.

  Also corrected: the evidence says Cato the Elder -> Marcus Porcius Censorius is the
  real direction, so Q73167 is likelier his son by Licinia with a wrong epithet than
  Cato duplicated as himself. I overstated that one.

- **Browsable cycle report** — `wikibase/analysis/cycles.html`, built by
  `build_cycles_page.py` from `cycles_page.html`. Regenerate after any repair; it always
  shows what is in the dump now. Self-contained, opens from disk.


- **Q73380 `BAD MERGE` characterized — `wikibase/analysis/Q73380_context.md`** (queue
  item 3, describe-don't-fix). The hypothesis in the queue was right — Icarius of Sparta
  conflated with a Seleucid king, specifically Seleucus IV Philopator on the node's own
  dates and `wikidata_qid` — but **the proposed fix is not a split, because both clean
  halves already exist in the dump as separate unlabelled records**: Q133344 holds the
  Spartan family, Q135914 the Seleucid one. Q73380 is a redundant third record.

  All 4 of its parents, 5 of its 6 spouses and 15 of its 20 children are edges those two
  records already carry. Only five children hang off Q73380 alone (Laodice VI, Antiochus
  V, Alexandros Balas, Antiochus Eupator, Antiochis), and all five are Seleucid by
  co-parent. Deleting the node outright with no reassignment would orphan 7 people;
  reassigning those five to Q135914 orphans none. **Nothing downstream depends on the two
  sides being joined**, so the proposal is to retire the node rather than split it.

  The 29,466 descendants are not Spartan and not really Seleucid — they are the Pontic
  royal house, reached through three daughters (Laodice 29,438, Nysa 29,431, Laodice VI
  29,426) whose descendant sets nearly coincide because the Pontic line marries back into
  itself.

  The find worth acting on is one the item did not anticipate and that retiring Q73380
  does **not** fix: **Q73515 Laodice carries 29,438 descendants and is parented by
  Q133344 — Icarius of Sparta — and Asterodeia**, while her husband and all five children
  are Pontic. That single edge, not the `BAD MERGE` node, is what currently ties the Greek
  mythic tier to the historical backbone here. It survives every step proposed, and
  reattaching her is a genealogical decision rather than a deduplication, so it is left
  for Emma with the evidence written up.

- **Multi-parent proposals written — `wikibase/analysis/qa_multiparent_proposed.tsv`**
  (queue item 2, propose-only). New script `wiki-scripts/propose_multiparent_fixes.py`
  clusters each child's listed parents and proposes one representative per cluster when
  they collapse to a biological pair.

  **Collapse rate: 409 of 1,230 children (33.3%) collapse to ≤2 distinct people.** The
  other 821 (66.7%) do not and are emitted `unresolved` with their clusters shown, per
  the standing rule against rank-and-truncate. Applying every proposal would remove 436
  of the 4,012 listed parent edges. By fan-out: 318 of the 957 three-parent rows resolve,
  and the extreme cases stay open — Sita (Q28324) goes 9 parents → 7 clusters, Marcus
  Livius Drusus (Q73119) 8 → 8.

  The whole difficulty is one pair of examples. `Sancha de Aybar` / `Sancha of Aibar` is
  one person spelled two ways; `Jimena Muñoz` / `Jimena Fernandez de Castro` are two of
  Alfonso VI's partners. Both pairs share a given name and differ in the rest, so any
  single similarity threshold merges both or neither. The rule that separates them
  compares surname tokens individually: every distinguishing token of the shorter label
  must have a fuzzy match in the longer one, so Aybar/Aibar merges and Muñoz/Fernandez
  does not. Verified against both, plus Ramiro I of Aragon, Sancho I of Pamplona,
  Ramon Berenguer I and Alfonso V of León, where the known parentage is checkable.

  One correction found by auditing the merges rather than the misses: `Marcus Livius
  Drusus` and `Marcus Livius maior Drusus` were being merged. *maior* marks the elder of
  two same-named men, so it separates father from son exactly as a regnal number does.
  `maior`/`minor`/`velho` are now generational markers alongside `Junior`/`Senior`, and a
  marker present on only one side of an otherwise identical name now blocks the merge.
  This also feeds `propose_cycle_cuts.py`, which shares the name logic; its output is
  unchanged by the fix.

- **Cycle cut proposals written — `wikibase/analysis/qa_cycles_proposed.tsv`** (queue
  item 1, propose-only). New script `wiki-scripts/propose_cycle_cuts.py` reads the 71
  cycles in `qa_cycles.tsv` and emits one row per cycle: the single edge it proposes to
  cut, the evidence, and a confidence. Nothing in `wikibase/items/*.json` or the source
  extracts was touched.

  **Result: 46 of 71 cycles get a proposal (10 high / 5 medium / 31 low), 25 are left
  `unresolved`.** The 39 distinct proposed edges break 47 cycles between them, verified
  by re-running cycle detection with the cuts applied in memory. The single highest-value
  row is the duplicate pair `Barbara, imperatriz of Rome` (Q82122) / `Bárbara, Princess
  of Rome` (Q99597): it sits on all seven of the long Portuguese/Byzantine chains, so one
  merge clears the biggest cluster in the file.

  Evidence rules, in the order they win: recorded birth-date contradiction; patronymic
  reversal (the parent's own name calls the child its father — Welsh `ap/ferch`, Iberian
  `-es/-ez`); identical-name adjacency (a person listed as parent of their own duplicate);
  birth-year bounds from dated relatives; worst-sourced edge as a last resort.

  Three things went wrong on the way and are worth recording, because each one produced
  confident nonsense before it was caught:

  - **Unbounded date propagation is useless on this graph.** Walking "+12 years per
    generation" over the full 128k edges from the mythic tier produces bounds like "born
    no earlier than 12372" and then fires on every edge in a chain. Anchors are now
    carried a maximum of 3 generations, never through a cycle edge, with the source
    person named in the row.
  - **Unsigned BC dates.** Many Roman republican figures are recorded `+0300` where the
    source meant 300 BC; read as BC the edge order is fine. Those rows are demoted to
    `date_ambiguous_era` at low confidence and say the fix is probably the date, not
    the edge.
  - **Regnal numbers and cognomina are how the data distinguishes father from son.**
    `Guerau IV -> Guerau V` and `Scipio Barbatus -> Scipio` were being proposed as
    duplicate merges. "Duplicate" now requires identical name tokens; a shared
    praenomen+nomen or a differing regnal number is corroboration or an unproven
    homonym instead.

  Coverage caveat stated plainly: only 71 of the 345 nodes in these cycles carry a birth
  date, so most rows rest on name evidence rather than dates, and 31 of the 46 proposals
  are low confidence for that reason. The 25 unresolved rows are unresolved because
  nothing separated the edges — not because the analysis stopped early. Rerunning the
  script reproduces the file byte-for-byte (DFS iterates sorted nodes; Python randomises
  string hashing per process, which made the first two runs disagree).

## 2026-07-01

- **The wiki is GONE — de-linked the site entirely + ran the local genealogy analysis.**
  Correction to the earlier same-day entry below: the wiki was not "migrated to
  wiki.order.life", it was **taken down by Miraheze as off-topic** and is not coming back;
  there is no replacement wiki. (Earlier this session I wrongly repointed redirects at
  wiki.order.life believing it was live — Emma corrected this.) Actions taken:
  - **Removed all wiki links/redirects from the site** (per Emma: "there should not be any
    links on the site to the dead wiki … make it not link-based, because there isn't a
    wiki anymore"). Deleted `generate_wiki_redirects()` + its call from `build.py`
    (`py_compile` clean), deleted `templates/wiki-redirect.html`, and removed the
    wiki-redirect branch from `templates/404.html`. Verified: zero
    `wiki.order.life`/`*.miraheze` refs remain in `build.py`/`templates`/`static`
    (Wikidata + Wikimedia-Commons links are unrelated and stay). The
    `lifeism+Wiki-*.xml` export still feeds baked-in day/month *content* (local, not a link).
  - **Deleted the wiki GitHub Actions** (`wiki-bot.yml`, `calendar-bot.yml`,
    `wikibase-dump.yml`) — they operated the dead wiki. Kept deploy/compile/discord/dotnet.
  - **Wikibase backfill = DONE/archived.** It was a fetch-from-wiki download (never
    wiki-free); the 164,536-item snapshot is committed and is now the only copy. Stripped
    the backfill *operation* sections from `todo.md` + `queue.md` (archived, pointing to
    the analysis outputs). Nothing left to fetch.
  - **Ran the local genealogy analysis + QA** (`genealogy_network_analysis.py`, all local,
    no wiki): 106,926 persons / 128,717 edges; giant component 94.67%; centrality confirms
    Jesus (28,512 desc), Charlemagne (12,539), etc. QA errors enumerated in full:
    `wikibase/analysis/qa_multiparent.tsv` (1,230 children with >2 parents),
    `qa_cycles.tsv` (~70 impossible ancestor cycles, via new `dump_qa_errors.py`),
    summary `wikibase/analysis/GENEALOGY_QA.md`, full run `genealogy_qa_report.txt`. NOT
    auto-fixed — choosing true parents / which cycle-edge to cut is per-record judgement
    (auto-guessing = fabricating scripture); surfaced for Emma. Fixes would be local-dump
    edits since the wiki is gone.
  - Docs updated to "no wiki exists": gaiad `CLAUDE.md` (Wiki Redirects → REMOVED, URL
    structure, Key Branding), `calendar-lib/README.md`.

- **[superseded] Finished the lifeism→wiki.order.life wiki migration in code + docs.** The old
  `lifeism.miraheze.org` wiki closed 2026-04-16 (verified 404; `evolutionism.miraheze.org`
  too). The site's `/wiki/*` redirects, `templates/wiki-redirect.html`, and `templates/404.html`
  had already been migrated to `wiki.order.life`, but the `/w/*` (MediaWiki script-path)
  redirect block in `build.py` and several docs still pointed at the dead wiki — implying it
  was live and sending users to 404s. Fixed: `build.py` `/w/` block now targets
  `wiki.order.life/w/*` (root + Main_Page + JS deep-link + link text); `build.py` compiles
  clean (`py_compile`; did NOT run full build — CI does that). Updated docs to say the wiki is
  closed and `wiki.order.life` is current: gaiad `CLAUDE.md` (Wiki Redirects, URL structure,
  Key Branding — the latter also fixed a "migrating to itself" typo), `calendar-lib/README.md`
  (closure banner + table + roadmap), and removed the now-satisfied "Unlink the wiki from the
  site" item from `STATUS.md` (delete-don't-check).
- **overview-preservation "dead test" — was a mischaracterization, fixed.**
  `test_overview_preservation.py` was never a real pytest test; it's a manual CLI diagnostic
  (`argparse --username/--password`) that pytest only *collected* because of its `test_*.py`
  name + `test_*` functions, yielding 2 `fixture not found` setup errors. Renamed to
  `diagnose_overview_preservation.py` (git mv) and de-`test_`-prefixed its internal functions;
  pytest no longer collects it → **calendar-lib suite now 2 passed / 0 errors**. Corrected the
  wrong "dead, needs live wiki fixture" wording in `devlog.md` + `todo.md`.
- **Wikibase backfill — not deferred, essentially already complete.** Checked disk:
  **164,536 items + 94 properties** present vs ~164,544 on the wiki (snapshot) — only a
  handful outstanding; the "60K / 7h" figure was stale. The git-contention deferral was
  overcautious (`--commit-every` defaults to 0 = no self-push). Real current blocker:
  `wiki.order.life` TLS handshake fails from this machine (`SSLV3_ALERT_HANDSHAKE_FAILURE`
  across curl/PowerShell/Python → edge-side, not client). Can't fetch the last few or
  re-verify the total until the wiki's TLS serves again. Updated `queue.md` accordingly.

## 2026-06-29

- **dotnet-build "first run" item — stale, removed.** Checked CI history: the
  `dotnet-build` workflow has completed `success` repeatedly, including on the
  `setup-dotnet@v5` bump commit (c037669d1, which modified the workflow so it
  actually ran the build job). It restores + builds `GaianNodaTimeWrappers.sln`
  against .NET 8.0.x cleanly — no framework mismatch, no decision needed. Pruned the
  item from queue.md BLOCKED and marked it done in todo.md. Also confirms the
  Node-24 `setup-dotnet@v5` bump is green in CI.
- **calendar-lib test health checked.** `test_page_generation.py` passes 2/2
  (generation logic healthy, offline). The earlier "test_overview_preservation.py
  errors 2/2, dead until a wiki exists" framing was WRONG on two counts (corrected
  2026-07-01): (1) it was never a pytest test — it's a manual CLI diagnostic that
  pytest only *collected* because it was named `test_*.py` with `test_*` functions;
  the "2 errors" were `fixture 'username'/'wiki' not found`, not a wiki problem.
  Renamed to `diagnose_overview_preservation.py` + renamed its internal functions,
  so pytest no longer collects it and the suite is a clean 2 passed / 0 errors.
  (2) It targets `evolutionism.miraheze.org`; both that and `lifeism.miraheze.org`
  are 404 (closed 2026-04-16), so the diagnostic can't run regardless — but that's a
  can't-connect, not a failing test.
- **Chapter 329 missing-title fix.** A read-only structural integrity audit of all
  253 drafted chapter files (`Gaiad/epic/chapter_*.md`) found exactly one mechanical
  defect: `chapter_329.md` opened straight into verse with no `# Chapter N: Title`
  heading (every other chapter has one). Numbering gaps 253-328 / 330-364 are gated
  unwritten chapters, not defects. The heading format is mechanical, but the title
  wording is Emma's authorial call — the planning-table title was flagged stale, so
  asked her via AskUserQuestion + push. She chose **"The Covenant of Peace"** (from
  the poem's closing line). Added `# Chapter 329: The Covenant of Peace`; re-ran the
  audit → 0 missing titles, structurally clean. Audit script in scratchpad.
- **Month-page clobber check — MOOT (resolved, not done).** Queue item 3 asked to
  verify the calendar-bot didn't clobber the 14 Gaian month pages on
  lifeism.miraheze.org. Investigated: the host returns "Wiki not found" (404), and
  `calendar-bot.yml:24` records the bot was disabled 2026-04-16 because that wiki is
  closed. So there are no live pages and the bot never ran against a live wiki — the
  todo entry predates the closure. Pruned the verification item and the now-
  unreachable `Module:GaiadDate` import from both queue.md and todo.md (left the XML
  reference for a possible future wiki). Read-only audit script lives in scratchpad.
- **Wikibase backfill — DEFERRED, not launched.** The script auto-`git push origin
  master` without pull-rebase; running it 7h alongside the work-loop crons would race
  on the git index/push. Downstream use (ch 130–220 genealogy) is gated until Leo
  anyway. Moved to queue.md DEFERRED with run instructions (dedicated job / crons
  paused, or `--commit-every 0`).
- **Node 20 deprecation — DONE.** Bumped GitHub Actions across all 7 workflows to
  the first Node-24 major: `actions/checkout@v4→v5`, `setup-python@v5→v6`,
  `setup-dotnet@v4→v5`. Deliberately did NOT jump to checkout v6/v7 — checkout v6
  changes credential persistence ("persist creds to a separate file"), which risks
  breaking the bot workflows that push commits back via the checkout token. v5/v6/v5
  are single-major bumps whose only breaking change is the node runtime + runner
  min-version (satisfied on GitHub-hosted runners). The `FORCE_JAVASCRIPT_ACTIONS_
  TO_NODE24` env-var interim from todo.md is now moot — today (2026-06-29) is past
  the 2026-06-02 forced-Node24 date; the real fix before the 2026-09-16 Node20
  removal is the tag bump. All 7 YAML files validated as parseable; deploy run
  monitored on push.
- **iCal Phase 2 — DONE.** New dedicated subscribe landing page at
  `/calendar/ical/` (`templates/calendar/ical.html`), generated per-language in
  `build.py` after the gaian-era page. Lists all three feeds (`current.ics`,
  `current_ja.ics`, `gaian-holidays-extended.ics`) with `webcal://` subscribe +
  `https://` download links and step-by-step Google / Apple / Outlook
  instructions. Linked from the calendar overview (quick-link card + "all
  subscribe options" pointer). Verified by running `build.py` (exit 0, no render
  errors): root + `/ja/` + `/es/` pages produced, all feed links present, `.ics`
  files coexist with `index.html`. `site/` is gitignored — CI rebuilds.
- **Autonomous work loop established.** Created `queue.md` from the `todo.md`
  backlog (organized into ACTIVE / BLOCKED-needs-Emma / GATED / pinned tail) and
  started the three session-local crons: work-loop (`0,30`), auto-flush (`15,45`),
  status-report (`:50`). User asked the work-loop to fire on the hour and half-hour.
- **Stale queue hygiene (earlier this session):** verified iCal Phase 1 + the
  universal day-description (Phase 3) were already shipped in `build.py`; pruned the
  stale "needs fixing" entries from `todo.md` (commits `aaf47749a` → life `c969446`
  → hub `c04fab3`). Post-power-interruption check: no stranded work, all repos clean.
