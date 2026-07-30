# Ishmael → Adnan → Muhammad: the merge set

**Drafted 2026-07-30 by the autonomous work-loop (queue item 1).**

**Propose only. Nothing merged, nothing edited.** No `wikibase/items/*.json` and no
`wikibase/analysis/*.tsv` was modified. Every row below records the proposed change and
the evidence for it; rows the evidence does not settle say so.

Follows from `epic_vs_dump.md` Finding 5. That report concluded the fix here was a merge
of duplicate records. Working it produced a larger finding: **the duplication is real, but
it is downstream of a splice.** Muhammad's recorded ancestry leaves the Arab genealogy
entirely for twelve generations and passes through the Roman client kings of Emesa.

Reproduce any row with `wiki-scripts/graph_probe.py`, e.g.
`python wiki-scripts/graph_probe.py path Q65705 Q86433`.

---

## Finding — Muhammad's line above Fihr runs through the priest-kings of Emesa

Walking Muhammad (Q65705) up his agnatic line:

```
  0  Muhammad                              Q65705   (wd Q9458, b. 570)
  1  Abd Allah born Abd al-Muttalib        Q65702
  2  Abd al-Muttalib born of Hashim        Q65008   (wd Q380479)
  3  Hashim ibn 'Abd Manaf                 Q64474   (wd Q553241)
  4  Abd Manaf ibn Qusai                   Q64029   (wd Q2475244)
  5  Qusai born of Kilab                   Q63556   (wd Q2724873)
  6  Kilab born of Murrah                  Q63233   (wd Q2327777)
  7  Murrah born of Ka'b                   Q62968   (wd Q12242034)
  8  Ka'b born of Lu'ayy                   Q62815   (wd Q12234967)
  9  Lu'ay born of Ghalib                  Q86975   (wd Q12236836)
 10  <Ghalib>                              Q153797  ** NO persons.tsv ROW **
 11  Fihr born of Iamblichus               Q153798  (wd Q12231260, b. 272)
 12  Iamblichus                            Q153799  (wd Q12238331, b. 240)
 13  Antonious Sampsigeramus, Priest-King of Emesa   Q85845
 14  Uranius I Antoninus, Priest-King of Emesa       Q85843
 15  Gaius Iulius Sulpicius, Priest-King of Emesa    Q85841
 16  Iamblichus of Emesa                             Q85839
 ...  eight more Emesene / Sampsigeramid generations ...
 24  Malichus  Banu Adnan                  Q49687   <-- rejoins the Arab genealogy here
 ...  fourteen `Banu Adnan` generations ...
 38  Adnan  Banu Ismail                    Q86433
```

Steps 0–11 are the traditional Quraysh line and are correct. At step 11 the record's own
label gives it away: **`Fihr born of Iamblichus`**. In every Arab genealogy Fihr's father
is **Ghalib**, and above him Malik, al-Nadr, Kinana, and so on up to Adnan. Here Fihr's
father is a Hellenistic priest-king of Emesa, and the line spends twelve generations in
Roman Syria before rejoining an Arab chain at `Malichus Banu Adnan`.

The result: Muhammad sits **38 generations** below Adnan where the tradition puts him at
about 21, and the surplus is exactly the spliced-in Emesene segment.

**This is not obviously an error.** The Sampsigeramids of Emesa were an Arab dynasty, and
connecting Quraysh to them is a real (if minority) genealogical speculation. What makes it
a defect here is that **the correct chain is also in the dump, sitting unused**, and the
splice is what forces every downstream duplicate.

---

## The correct chain is already present, as the `Banu Ismail` series

`Ismail Ancestor of the Arabs` (Q85869) → … → `Adnan Banu Ismail` (Q86433), 36 generations,
every node with exactly one child:

| # | Label | QID | Reading |
|---|---|---|---|
| 0 | Ismail Ancestor of the Arabs | Q85869 | Ishmael |
| 1–13 | Qedar, Amr, Jusham, Nabit, Yashjub, Taima, Mishma, Hadhad, Yathrib, Nabit II, Harith, Saba, Abd Shams | Q86435–Q86459 | the traditional Qedar→Adnan bridge |
| 14 | Nizar | Q86461 | **Nizar ibn Ma'ad** |
| 15 | Mudhar | Q86463 | Mudar |
| 16 | Ilyas | Q86465 | Ilyas |
| 17 | Mudar | Q86467 | **Mudrika** — misrendered; a second copy of the name Mudar |
| 18 | Kinana | Q86469 | Kinana — **Khuzayma is missing between 17 and 18** |
| 19 | Nazr | Q86471 | al-Nadr (Quraysh) |
| 20 | Malik | Q86473 | Malik |
| 21 | Fihr | Q86475 | Fihr |
| 22 | Ghalib | Q86477 | Ghalib |
| 23 | Luhay | Q86479 | Lu'ay |
| 24 | Kenan | Q86481 | Ka'b |
| 25 | Murrah | Q86483 | Murrah |
| 26 | Kilab | Q86485 | Kilab |
| 27–30 | Humayd, Mazin, Hisham, Nizar | Q86487–Q86493 | **not in any Quraysh list** |
| 31 | Abd Manaf | Q86495 | Abd Manaf — **inverted with Qusayy** |
| 32 | Qusay | Q86497 | Qusayy |
| 33–35 | Zayd, Harith, Nabhan | Q86499–Q86503 | **not in any Quraysh list** |
| 36 | Adnan Banu Ismail | Q86433 | Adnan — **at the wrong end of the chain** |

**Rows 14–26 are the Adnanite/Quraysh sequence in correct ancestor-to-descendant order**,
and they are exactly the segment Muhammad's own line is missing — the segment the Emesene
splice replaced.

**Row 36 is the chain's central error.** Adnan belongs at row 14, immediately above Nizar,
with **Ma'ad** between them. Instead he terminates the chain as its youngest member, 22
generations below his own descendants. **Ma'ad is absent from this chain entirely** — the
`Ma'ad` records in the dump (Q64732, Q110802) belong to the other two Adnan clusters.

So the chain is right in the middle, wrong at the bottom, and the four unattested names at
rows 27–30 and 33–35 are what fills the space the inversion opens up.

---

## Three Adnans, two Ishmaels, two Qedars

| Record | Route up | Children | Muhammad below it | Wikidata |
|---|---|---|---|---|
| `Adnan Banu Ismail` **Q86433** | 36 gens to Q85869, 37 to Abraham | 1 (`Imran Banu Adnan` Q86431) | 38 gens | none |
| `'Adnaan Bin Imaam 'Udd` **Q65555** | **none** — runs into the `'Udd`/`Humaisi`/`N.N.` placeholder tangle | **9** | **16 gens**, via a maternal path through `'Atikah binte Murrah` (Q64468) | none |
| `Adnan` **Q111364** | **none** — parentless stub | 2 (`Ma'ad` Q110802, `Al-Dith` Q111366) | no path | **Q22338875** |

| Record | Parents | Children |
|---|---|---|
| `Ishmael` **Q129307** (wd Q183403) | Abraham + **Hagar** | the twelve sons of Genesis 25, incl. `Qedar (person)` Q129387 |
| `Ismail Ancestor of the Arabs` **Q85869** | Abraham + **Sarah** | one: `Qedar Banu Ismail` Q86435 |
| `Qedar (person)` **Q129387** (wd Q21087985) | Q129307 | **none** |
| `Qedar Banu Ismail` **Q86435** | Q85869 | `Amr Banu Ismail` Q86437 — carries the whole chain |

`Ismail Ancestor of the Arabs` records **Sarah** as Ishmael's mother. Every tradition gives
Hagar, and Q129307 has it right. That alone settles which record survives.

---

## Proposed merges

**None of this is applied.** Ordered so that each step is checkable on its own.

| # | Merge | Survivor | Why | Confidence |
|---|---|---|---|---|
| M1 | `Ismail Ancestor of the Arabs` Q85869 → `Ishmael` Q129307 | **Q129307** | Q129307 has the correct mother (Hagar), the Wikidata id, and the twelve sons. Q85869 contributes only the edge down to Qedar | **decided** |
| M2 | `Qedar Banu Ismail` Q86435 → `Qedar (person)` Q129387 | **Q129387** | Q129387 carries the Wikidata id and sits among his eleven brothers; Q86435 contributes the child edge to `Amr` Q86437 | **decided** |
| M3 | The three Adnans → one | **Q111364** | It is the only one carrying a Wikidata id (Q22338875). Q86433 contributes the parent edge; Q65555 contributes nine children and the descent to Muhammad | **needs Emma** — see below |
| M4 | `Ma'ad ibn Adnan Aladnani` Q64732 → `Ma'ad ibn Adnan` Q110802 | **Q110802** | Q110802 carries wd Q12244037; Q64732 carries seven children and a spouse | **needs Emma** |
| M5 | `Fihr Banu Ismail` Q86475 → `Fihr born of Iamblichus` Q153798 | **Q153798** | Q153798 carries wd Q12231260 and Muhammad's descent. **Its parent edge to Iamblichus must be cut in the same move** — see R1 | **decided, paired with R1** |
| M6 | `Ghalib Banu Ismail` Q86477 → Q153797 | **Q86477** | Q153797 has **no `persons.tsv` row at all** — it exists only as an edge endpoint. Merging into the orphan would be merging into nothing | **decided** |
| M7 | `Luhay` Q86479 → `Lu'ay born of Ghalib` Q86975 | **Q86975** | wd Q12236836 | **decided** |
| M8 | `Kenan` Q86481 → `Ka'b born of Lu'ayy` Q62815 | **Q62815** | wd Q12234967. "Kenan" is a transliteration of Ka'b, not the Sethite Kenan | **probable** — the label similarity to Sethite Kenan (Q134022) is a trap; flagging rather than asserting |
| M9 | `Murrah` Q86483 → `Murrah born of Ka'b` Q62968 | **Q62968** | wd Q12242034 | **decided** |
| M10 | `Kilab` Q86485 → `Kilab born of Murrah` Q63233 | **Q63233** | wd Q2327777 | **decided** |
| M11 | `Qusay` Q86497 → `Qusai born of Kilab` Q63556 | **Q63556** | wd Q2724873 | **decided** |
| M12 | `Abd Manaf` Q86495 → `Abd Manaf ibn Qusai` Q64029 | **Q64029** | wd Q2475244 | **decided** |

## Proposed repairs, which the merges depend on

| # | Repair | Evidence | Confidence |
|---|---|---|---|
| R1 | **Cut `parent(Fihr Q153798) = Iamblichus Q153799`** and repoint Fihr's parent to Ghalib (Q86477 post-M6) | The record's own label says "Fihr born of Iamblichus", so the splice is deliberate, not accidental. But no Arab genealogy gives Fihr a Hellenistic father, and the correct chain above Fihr is present in the dump | **needs Emma** — this is the load-bearing call. Cutting it detaches the Emesene dynasty from the Arab line entirely |
| R2 | **Move `Adnan` from the bottom of the Banu Ismail chain to above Nizar Q86461**, and insert Ma'ad between them | Rows 14–26 are the traditional sequence in correct order; Adnan at row 36 is 22 generations below his own descendants | **decided** on the direction; the exact insertion point is R3 |
| R3 | Retire rows 27–30 (`Humayd`, `Mazin`, `Hisham`, `Nizar` — Q86487–Q86493) and 33–35 (`Zayd`, `Harith`, `Nabhan` — Q86499–Q86503) | None appears in any Quraysh ancestor list. They occupy the space the Adnan inversion opens up | **probable** — retiring named records on an argument from absence; recommend Emma sight them |
| R4 | Invert rows 31–32: Qusayy is Abd Manaf's father, not his son | Every tradition, and Muhammad's own line in this dump (Q63556 → Q64029), has Qusayy above Abd Manaf. The Banu Ismail chain has it backwards | **decided** — the dump contradicts itself and one side is orthodox |
| R5 | Insert **Khuzayma** between `Mudrika` (Q86467, mislabelled `Mudar`) and `Kinana` (Q86469); relabel Q86467 | Standard in every list; the chain skips it | **decided** on Khuzayma; the relabel of Q86467 is **probable** |
| R6 | Create a `persons.tsv` row for **Q153797**, or drop the edge | It is an edge endpoint with no record — one of the 138 such orphans. It sits inside Muhammad's agnatic line | **decided** — resolved by M6 either way |

---

## The one that cannot be settled from the data

**M3, which Adnan survives, is genuinely undecided, and it is the hinge of the whole set.**

- **Q111364** has the Wikidata identifier and nothing else — no parents, two children.
- **Q86433** is the one with a route to Abraham, but only through the 36-generation chain
  whose bottom end R2 says is wrong. Its single child `Imran Banu Adnan` (Q86431) heads a
  twelve-generation `Banu Adnan` chain that runs up to `Malichus` (Q49687) and thence
  into the Emesene splice — so it is entangled with exactly the thing R1 proposes to cut.
- **Q65555** is the one Muhammad's line actually reaches, at 16 generations, which is the
  count closest to tradition. It has nine children, which is nearest to the "twelve sons"
  chapter 191 asserts. And it reaches nothing upward.

Each of the three is the right answer by a different measure — identifier, ancestry,
posterity. Merging them collapses three different construction attempts, and which set of
edges survives determines whether Muhammad's descent from Abraham runs through Adnan (as
chapter 191 says) or through Emesa (as the dump currently says).

**Recommendation: decide R1 first.** If the Emesene splice is cut, Q86433's route becomes
the spine and it should survive, taking Q111364's identifier and Q65555's children. If the
splice is kept, the Banu Ismail chain is decorative and the merge set below M2 is not worth
applying at all. **The order matters and I am not choosing it.**

---

## Not covered

The `Banu Adnan` chain (Q86403–Q86431, twelve records from `Ithobaal` down to `Imran`) and the `'Udd`/`Humaisi` tangle above Q65555 were both read but not traced.
`Ithobaal` is a Tyrian royal name, not an Arab one, which suggests the same kind of splice
as the Emesene one and may be the same defect twice. **Worth its own item; not asserted
here.**
