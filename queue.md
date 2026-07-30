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

1. **Extract the Adnanite genealogy from label text into proposed edges.** Found
   2026-07-30 by the epic sweep (`wikibase/analysis/epic_vs_dump.md`, Finding 5).
   Chapter 191 asserts the northern Arabs descend from Ishmael through thirty
   generations to Adnan. Ishmael (Q129307) has **19 descendants in the dump and none of
   them is Adnan**, yet dozens of records carry the chain inside their *labels* as Arabic
   patronymics — `Nizar ibn Ma'ad Aladnani` (Q64253), `Banu Rashaida ibn Ghatafan ibn
   Qais ibn Mudar ibn Nizar ibn Ma'add ibn Adnan` (Q64723), and so on. The genealogy is
   present as text and absent as edges. Parse the `ibn`/`bin` chains out of
   `persons.tsv` labels, resolve each named ancestor to an existing record where one
   exists, and write `wikibase/analysis/adnan_chain_proposed.md`: per proposed edge, the
   two records, the label the chain was read out of, and whether the ancestor resolved
   to an existing QID or would need a new one. Propose only — do NOT write edges. Where
   two labels disagree about a link, record both rather than picking.

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
