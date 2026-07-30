# order.life — Devlog

Dated log of autonomous work-loop progress. Newest first.

## 2026-07-30

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
