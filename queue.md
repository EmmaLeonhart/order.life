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

**Standing rule for all these items:** do NOT modify `wikibase/items/*.json` or the
`wikibase/analysis/*.tsv` source extracts. Each item's output is a NEW review file that
records, per record, the proposed change AND the evidence for it. Emma approves, and a
later item applies the approved set. Where the evidence does not decide the case, say
so in the row rather than picking — an unresolved row is a correct outcome, a guessed
one is not.

1. **Propose the merge set for the fragmented Ishmael → Adnan → Muhammad descent.**
   Found 2026-07-30 by the epic sweep (`wikibase/analysis/epic_vs_dump.md`, Finding 5).
   Chapter 191's claim is backed by the dump, but the chain is split across duplicate
   records: Abraham has **two Ishmaels** (`Ishmael` Q129307 with the twelve Genesis sons,
   and `Ismail Ancestor of the Arabs` Q85869 carrying the whole 36-generation Banu Ismail
   chain), **two Qedars** (Q129387, childless; Q86435, carrying the chain), and **three
   Adnans** (Q86433 reaching Abraham in 37 generations, Q65555 which Muhammad actually
   descends from in 16 and which reaches nothing, and the stub Q111364). Muhammad's line
   therefore never passes through an Adnan connected to Abraham. Write
   `wikibase/analysis/adnan_merge_proposed.md`: per proposed merge, the records, which
   one should survive and why, what each contributes (children, spouses, wikidata id),
   and what breaks if they are merged the other way. Use the Arabic patronymic label
   strings — `Nizar ibn Ma'ad Aladnani` (Q64253), `Banu Rashaida ibn Ghatafan ibn Qais
   ibn Mudar ibn Nizar ibn Ma'add ibn Adnan` (Q64723) — as the independent cross-check on
   each link, since the labels record the parentage the edges are meant to hold. Propose
   only — do NOT merge anything. Where two records disagree and the labels do not settle
   it, say so in the row.

2. **Characterize the "Mesopotamian king list over the patriarchs" overlay.** Found
   2026-07-30 (`epic_vs_dump.md`, Finding 1). The record occupying **Noah's** slot —
   Lamech's son, father of Ham and Japheth, spouses Naamah and Emzara — is labelled
   `Shu-Ilishu` (Q70439) and carries the Wikidata id of a king of Isin. The record
   occupying **Eber's** slot, Joktan's father, is `Ilum-bani` (Q70454), another Isin
   king, whose father is `Naram-Ilum` (Q70451). This is not two typos; a king list has
   been laid over the biblical patriarch line, keeping the biblical edges and
   substituting the Mesopotamian names. Walk the whole neighbourhood — Q70430–Q70500 and
   everything adjacent to it — and write `wikibase/analysis/patriarch_overlay.md`: per
   record, the label it carries, the Wikidata item that label points at, the biblical
   figure its *edges* say it is, and the evidence for that identification. Say
   explicitly which rows the edges do not decide. Propose only. This node set is
   load-bearing for the Table of Nations, so nothing here is applied without Emma.

---

## DEFERRED — do NOT interleave with the live work-loop

_(none — the Wikibase backfill is DONE; wiki gone, snapshot frozen + committed, 164,536
items in repo. See devlog 2026-07-01. The `fill_missing`/`dump` scripts need a live wiki
and can no longer run; all downstream analysis reads the local dump.)_

## GATED — do not touch before Leo (2026-08-12)
- New Gaiad chapter generation (253–328, 330–364). Editing/polishing only is OK.

---

## PINNED TAIL (always last — keep at bottom on every re-fill)

- **T1. Ensure the three work-loop crons are running** — work-loop (`0,30 * * * *`),
  auto-flush (`15,45 * * * *`), status-report (`50 * * * *`). Restart any that a
  planning burst / queue re-fill killed; start them if this session never did.
- **T2. Run the status-report action once more, independently** — end-of-session
  summary of everything that happened this session.
