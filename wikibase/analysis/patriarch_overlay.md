# The Mesopotamian king-list overlay on the patriarch line

**Drafted 2026-07-30 by the autonomous work-loop (queue item 1).**

**Propose only. Nothing edited.** No `wikibase/items/*.json` and no
`wikibase/analysis/*.tsv` was modified. Each row gives the label the record carries, the
Wikidata item that label points at, the biblical figure its *edges* say it is, and what
decides the identification. Rows the edges do not decide say so.

Follows from `epic_vs_dump.md` Finding 1, which found two records — `Shu-Ilishu` in Noah's
slot and `Ilum-bani` in Eber's — and called it a systemic overlay. It is. **The whole of
Genesis 11 is present, in order, with every patriarch's name replaced by a Mesopotamian
ruler's, while the patriarchs' children keep their biblical names.**

Reproduce with `python wiki-scripts/graph_probe.py who Q70439 Q70442 Q70445`.

---

## The chain

Reading down from Lamech to Abraham. Every one of these is a single-parent-to-single-child
link in the dump, and the "identified as" column is forced by the children, not guessed
from the names.

| # | Label carried | QID | wd | Points at (real person) | Edges say it is | What decides it |
|---|---|---|---|---|---|---|
| — | Lamech | Q129841 | Q10921342 | Lamech | **Lamech** | unchanged |
| 1 | `Shu-Ilishu` | **Q70439** | Q2997581 | king of Isin, c. 1984 BCE | **Noah** | son of Lamech and Bat-Enosh; fathers Ham, Japheth and Canaan; spouses **Naamah** and **Emzara**, the two traditional names for Noah's wife |
| 2 | `Puzur-Ashur` | **Q70442** | Q200902 | king of Assur | **Shem** | fathers **Elam, Ashur, Lud, Aram** — four of the five sons of Shem in Genesis 10:22, with the fifth (Arpachshad) appearing as row 3 |
| 3 | `Ishme-Dagan` | **Q70445** | Q457520 | king of Isin | **Arpachshad** | son of row 2; fathers **Cainan**, who is Arpachshad's son in the Septuagint |
| 4 | `Naram-Ilum` | **Q70451** | Q1827950 | Akkadian ruler | **Shelah** | sits between Arpachshad and Eber; see the caveat below |
| 5 | `Ilum-bani` | **Q70454** | Q502282 | king of Isin | **Eber** | fathers **Joktan** and row 6 — Eber's two sons in Genesis 10:25 are Peleg and Joktan |
| 6 | `Iddin-Sin` | **Q70457** | Q1648259 | king of Eshnunna | **Peleg** | Joktan's brother by row 5 |
| 7 | `Shu-Sin` | **Q70460** | Q2040793 | king of Ur | **Reu** | position only — see "not decided" |
| 8 | `Ur-Ninurta The Amorite` | **Q70463** | Q2622811 | king of Isin | **Serug** | fathers **Nahor** |
| — | Nahor | Q47345 | Q888890 | Nahor | **Nahor** | unchanged |
| — | Terah | Q129293 | Q586541 | Terah | **Terah** | unchanged |
| — | Abraham | Q85228 | — | Abraham | **Abraham** | unchanged |

**The pattern is exact and it is not random.** Where a patriarch has named children in
Genesis, the children are in the dump under their biblical names — Ham, Japheth, Elam,
Ashur, Lud, Aram, Cainan, Joktan, Nahor. Only the patriarchs *in the direct line of
descent* have been renamed. Whoever built this substituted the spine and left the branches
alone.

Two of the branch names are worth noting as correct rather than corrupt. `Gionitus`
(Q129857), listed among Noah's children, is the apocryphal fourth son of Noah from
Pseudo-Methodius — a deliberate inclusion, not noise. And `Cainan` at row 3 is the
Septuagint's extra generation, absent from the Masoretic text; its presence says the
builder was working from a Greek-text genealogy.

---

## Where the overlay attaches

**Above Noah: the Sargonic dynasty of Akkad.** `Shu-Ilishu` (row 1) has **two fathers** —
`Lamech` (Q129841) and **`Ilushu`** (Q70436). Lamech is the biblical line. Ilushu heads a
second, purely Mesopotamian ancestry:

```
Tashlultum (Q70529) → Rimush of Akkad (Q70526) → Manishtushu (Q70520) → Naram-Sin (Q70517)
  → Shar-Kali-Sharri (Q70511) → Dudu of Akkad (Q70505) → Shu-turul of Akkad (Q70433)
    → Ilushu (Q70436) → Shu-Ilishu / NOAH (Q70439)
```

So the splice point is Noah himself, holding a biblical father and an Akkadian father at
once. This is one of the 1,230 multi-parent records, and it is the load-bearing one: it is
where a real Akkadian king list was welded onto Genesis.

**Off Serug: the First Dynasty of Babylon.** `Ur-Ninurta` (row 8) has three children —
Nahor, `Ithobaal Genarch` (Q51800), and **`Sumuabum King of Babylon`** (Q70466), who heads
the complete Babylonian dynasty: Sumuabum → Sumulael → Sabium → Apil-Sin → Sin-Muballit →
**Hammurabi** (Q70400) → Samsuiluna → Abieshu → Ammiditana → Ammisaduqa → Samsuditana. That
is the real king list, in the real order, hanging off Serug as a side branch.

`Ithobaal Genarch` (Q51800) is a third branch, heading a cluster of eponymous
ancestors — Aramaic, Ugaritic, Samalian, Taymanitic, South Gileadite "Genarchs". **It is a
different record from `Ithobaal Banu Adnan` (Q86403)**, the Tyrian-looking name in the
Adnanite chain, and the two should not be conflated; whether they are the same intended
figure is open, and is part of the queued Banu Adnan item.

---

## What this means for the reports that depend on it

- **`epic_vs_dump.md` Finding 1 understated the scope.** It reported two mislabelled
  records. It is nine, and they form one continuous chain.
- The recommendation there — relabel Q70439 to Noah, Q70454 to Eber — is **dead as of
  Emma's 2026-07-31 decision.** It was wrong in direction, not just incomplete: relabelling
  any of the nine deletes the euhemerism. `epic_vs_dump.md` Finding 1 now carries the
  supersession notice.
- Every chapter claim of the form "descendant of Noah" or "son of Eber" was marked a DATA
  ERROR for the same single reason, and **all of them are withdrawn by the one decision**:
  the dump is right, `Shu-Ilishu` *is* Noah, and the prose and the data agree on the person
  even though they disagree on the name. That disagreement is the euhemerism working.

---

## DECIDED 2026-07-31 by Emma: reading 2, deliberate euhemerism. Nothing is relabelled.

> "the mesopotamian ones is completely intentional euhemerism"

**Fix: none. The nine records keep their Mesopotamian royal labels.** This is not an import
corruption and must not be repaired as one. Rows 1-8 below stay exactly as they are; the
identification of each patriarch with a specific historical Mesopotamian ruler -- Noah as
Shu-Ilishu of Isin, Shem as Puzur-Ashur of Assur -- is the point, and it is the same
deflationary move `mediterranean_connections_to_find.md` describes: showing continuity
where traditions are usually treated as separate.

**The relabel set in reading 1 below is now dead. Do not execute it.** Any future report
proposing to restore biblical names to rows 1-8 is proposing to delete the euhemerism.

Emma notes she had recorded this decision several times already and it kept coming back as
an open question. It should not have been open: **`CLAUDE.md` has listed "the Genesis 11
patriarchs recorded under Mesopotamian royal names" as a confirmed-deliberate import since
2026-07-30**, and this file and `queue.md` went on asking anyway. The rule in `CLAUDE.md`
covers exactly this -- *everything surprising that is not an error was imported
deliberately by Emma; surprising is not evidence of broken* -- and it was not applied.

**Still genuinely open, and unaffected by this decision:** the three rows under "Not
decided by the edges" below, which are position-only identifications and generation errors,
not naming questions. Row 4 `Naram-Ilum` sits in a dump holding the Septuagint and Masoretic
orders simultaneously; `Kanʿān` is recorded as Noah's son rather than grandson. Those are
structural and survive reading 2 intact.

---

## The original three readings, kept as the record of how it was decided

**This may not be an error at all.** Three readings fit the evidence equally:

1. **Import corruption.** A Geni tree merged a Mesopotamian king list into the patriarch
   line by matching positions, and the names overwrote the biblical ones. Fix: relabel all
   nine, keep the edges.
2. **Deliberate euhemerism.** Someone identified each patriarch *with* a specific historical
   Mesopotamian ruler — Noah as Shu-Ilishu of Isin, Shem as Puzur-Ashur of Assur — as a
   historicising claim. The retained biblical children and the Septuagint Cainan both point
   this way: a careless merge would not have kept Naamah and Emzara as Noah's wives while
   renaming Noah. Fix: none; add a note recording the intent.
3. **Both.** A deliberate identification that later imports then corrupted.

**Reading 2 is the one I would bet on** (and it is the one Emma confirmed), because of the spouses. A merge that renamed Noah
to Shu-Ilishu would have no reason to give Shu-Ilishu the wives of Noah. But the evidence
does not settle it, and the fix differs completely between readings 1 and 2, so **this goes
to Emma undecided.** Nothing is applied either way.

If reading 1 is chosen, the relabel set is rows 1–8 above, and it should land together with
the multi-parent repair on Q70439 (dropping `Ilushu` or `Lamech`, whichever the decision
implies) so the graph is never half-converted.

---

## Not decided by the edges

| Row | Why it is not settled |
|---|---|
| 4 `Naram-Ilum` = **Shelah** | Position only. Its parent (row 3, Arpachshad) has **two** children — `Cainan` and this record — so the dump holds the Septuagint order (Arpachshad → Cainan → Shelah) and the Masoretic order (Arpachshad → Shelah) simultaneously, as siblings. One of the two edges is wrong and the dump does not say which |
| 7 `Shu-Sin` = **Reu** | Position only. Reu has no named children in Genesis, so nothing constrains this row from below. It sits between Peleg and Serug, which is Reu's slot, and that is the whole argument |
| 1 Canaan among Noah's children | `Kanʿān` (Q129853) is recorded as Noah's son. In Genesis he is Ham's son and Noah's grandson. A generation error independent of the naming question |
| — Which father Q70439 keeps | Depends entirely on which of the three readings above is chosen |
