# order.life — Devlog

Dated log of autonomous work-loop progress. Newest first.

## 2026-07-01

- **Finished the lifeism→wiki.order.life wiki migration in code + docs.** The old
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
