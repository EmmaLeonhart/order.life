# order.life — Autonomous Work Queue

Worked top-to-bottom by the autonomous work-loop cron (`:00`/`:30`). Each item is
bounded, verifiable, and unblocked. **Delete an item from this file in the same
commit that completes it** (delete-don't-check). Source backlog: `todo.md`.

**Hard rails:** never fake; never weaken/skip a test to pass; never claim
"works"/"verified" without running it; document real blockers, don't paper over
them. **Chapter gate:** do NOT generate new Gaiad chapters before Leo (2026-08-12).

---

## ACTIVE (do in order)

_All currently-actionable quick items are done (iCal Phase 2, Node 24 bump). The
calendar-bot month-page verification turned out moot — the wiki is closed (below).
Remaining work is DEFERRED, BLOCKED-on-Emma, or GATED until Leo._

---

## DEFERRED — do NOT interleave with the live work-loop

- **Wikibase backfill** (`wiki-scripts/wikibase_fill_missing.py`) — **essentially
  already done** (checked 2026-07-01): **164,536 items + 94 properties on disk** vs
  ~164,544 items on the wiki per the last snapshot, i.e. only a handful outstanding.
  The old "~60K to fetch / ~7h" framing was stale — it got run since 2026-04-15. The
  git-contention worry was also overstated: `--commit-every` defaults to **0 = off**,
  so running the script plain just writes files and never self-pushes (auto-flush
  then commits safely with pull-rebase). **Current blocker to finishing the last
  few / re-verifying the total: `wiki.order.life` is TLS-unreachable from this
  machine** — TLS handshake fails (`SSLV3_ALERT_HANDSHAKE_FAILURE`) across curl,
  PowerShell, and Python; three independent stacks failing points to the Cloudflare
  edge, not a local client quirk. Retry when the wiki's TLS is serving again; it's a
  negligible remainder and downstream use (ch 130–220 genealogy) is gated until Leo
  anyway.

## BLOCKED / NEEDS EMMA (do NOT execute autonomously — surface, don't guess)

- **Genealogy lineage bridges** (Kosala→Heo Hwang-ok, Genghis→Adam, Heo→Jimmu) —
  these invent connecting kings = creative scripture content; needs Emma's call,
  and is adjacent to the chapter gate.
- **Genealogy QA cleanup** — 69 cycles + 1,230 children with >2 parents (Geni merge
  errors) live on the wiki; fixing them is data surgery needing review.

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`0,30 * * * *`),
  auto-flush (`15,45 * * * *`), status-report (`50 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
