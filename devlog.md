# order.life — Devlog

Dated log of autonomous work-loop progress. Newest first.

## 2026-07-30

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
