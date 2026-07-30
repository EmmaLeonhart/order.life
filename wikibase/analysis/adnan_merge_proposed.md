# Ishmael → Adnan → Muhammad: the merge set

**Drafted 2026-07-30 by the autonomous work-loop (queue item 1).**

> ## ⚠ R1 IS DECIDED — Emma, 2026-07-30: *"Muhammad's genealogy there is 100% intentional."*
>
> **The Emesene splice stays. R1 is withdrawn — do not cut
> `parent(Fihr Q153798) = Iamblichus Q153799`.** Muhammad's descent through the
> Sampsigeramids of Emesa is authored, not an import artifact, and this report treated it
> as a defect throughout. Read the whole "Finding" section below as *description of an
> intended structure*, not as a fault report.
>
> **What that invalidates, by this report's own logic** (see "Recommendation: decide R1
> first"): with the splice kept, **the `Banu Ismail` chain is not the correct spine waiting
> to replace it** — it is a parallel line, and merging it into Muhammad's line would
> destroy the authored route. **M5–M12 are withdrawn.** The `Banu Adnan` chain is likewise
> intentional, not filler, and its fifteen records stay.
>
> **What survives:** M1, M2, M3, M4, R2–R6, and the `Creator BRAHMA` cut — none of those
> depend on the splice. See "After the decision" at the end.
>
> **What is still open:** whether "intentional" extends to the `Banu Ismail` chain and the
> three Adnan records, or stops at the Emesene route. M3 turns on that. Asked, not assumed.

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

---

# Addendum — the two chains left untraced

**Added 2026-07-30, same day, by the following work-loop item.** Still propose-only.

## (a) The `Banu Adnan` chain — a constructed bridge, not a tradition

Fifteen records between Adnan and the Emesene splice, ancestor to descendant:

```
Adnan Banu Ismail  Q86433
  Imran Q86431 → Harith Q86429 → Salih Q86427 → Nashir Q86425 → Hani Q86423
  → Malik Q86419 → Zayd Q86415 → Qays Q86411 → Amr Q86409 → Hudhayfah Q86407
  → Aziz Q86405
      ├── Ithobaal Banu Adnan  Q86403 ──┐
      └── N.N.                 Q49799 ──┴──→ N.N. Q49763 → Malichus Banu Adnan Q49687
                                                              ├── Sampsiceramus I Q72535
                                                              └── Creator BRAHMA Q1952
```

**Correcting the queue item that scheduled this.** It said the chain runs "from `Ithobaal`
down to `Imran`" and treated Ithobaal as the chain's head. The direction is the other way:
Adnan is at the top and Ithobaal sits second from the bottom, as one of the two recorded
parents of `N.N.` Q49763 — almost certainly father and mother, since Q49799 is Ithobaal's
sibling by Aziz and the pair converge on one child. Ithobaal is in the direct line, but he
does not begin it.

**Verdict: filler, with one bad merge.**

- **Not a tradition.** Imran, Harith, Salih, Nashir, Hani, Malik, Zayd, Qays, Amr,
  Hudhayfah, Aziz are ordinary Arab given names in no recognised Adnanite king list. Eleven
  single-child generations of common names, followed by two unnamed `N.N.` records, is the
  signature of a bridge someone built to span a gap, not of a transmitted genealogy.
- **It runs the wrong way to be Adnanite.** A genuine Adnanite chain descends from Adnan
  toward Quraysh. This one descends from Adnan toward **Emesa** — it exists to reach
  `Sampsiceramus I`, which is the splice this report's main section proposes cutting (R1).
  Its entire purpose is the thing under question.
- **`Ithobaal` is a red herring.** I flagged the name as Tyrian and suspected a second
  splice. It is not connected to `Ithobaal I` of Tyre (Q38158, Jezebel's father), nor to
  `Ithobaal Genarch` (Q51800) in the patriarch overlay. Three unrelated records share the
  name. **No second splice — I was wrong to suspect one.**
- **One real defect:** `Malichus` (Q49687) has two children, `Sampsiceramus I` and
  **`Creator BRAHMA` (Q1952)**. Brahma also has `India Genarch` and an `N.N.` as parents, so
  he belongs to the eponymous-ancestor "Genarch" layer and the Malichus edge is spurious.
  **Proposed: cut `parent(Q1952) = Q49687`.** Confidence: **decided** — nothing places the
  Hindu creator god among the sons of a Nabataean dynast, and Brahma's other parent already
  gives him a coherent position.

**Recommendation: this chain lives or dies with R1.** If the Emesene splice is cut, all
fifteen records lose their only purpose and should be retired with it. If it is kept, they
stay as the bridge they were built to be. **Do not decide them separately.**

## (b) The `'Udd` / `Humaisi` tangle — a real tradition, triplicated

Above `'Adnaan Bin Imaam 'Udd` (Q65555), which carries **three** parents:

| QID | Label | Parents | Note |
|---|---|---|---|
| Q65555 | `'Adnaan Bin Imaam 'Udd` | Q66394, Q66382, Q66385 | three parents |
| Q66385 | `Imaam 'Udd \ Add Ben Add Ben ?'Udadh` | Q67555, Q67549, Q67552 | three parents |
| Q66394 | `Udd son of Umaisi` | Q67561 | |
| Q67549 | `'Udadh ('Udaz) Beyt Kedar` | Q67561, Q69287 | |
| Q67552 | `Humaisi' direct to Addi \ Udd  desc Malchut ben Abraham` | Q67561, Q69287 | **the label is an editorial working note** |
| Q67561 | `Humaisi \ Umaisi  Umaisi ?` | Q69293, blank | |
| Q66382 | `al-Mutamattarah 'Ali bin Jarham` | — | parentless root |
| Q69287, Q69293, Q69299, Q67555 | `N.N.` / `Salaman` / blank | — | parentless roots |

**Verdict: the bottom link is right and everything above it is unresolved working notes.**

`'Udd` (also `Udad`) **is** Adnan's father in the standard short Adnanite genealogy —
Adnan ← Udad ← Muqawwim ← Nahur ← Tayrah ← Ya'rub ← Yashjub ← Nabit ← Ishmael. So Q65555's
parentage is orthodox, and this cluster is a genuine attempt at the real tradition, not
invention.

What went wrong is transmission, not content. `Udd`/`Udad`/`Udadh`/`Addi` and
`Humaisi`/`Umaisi` each appear as several records; Q67561 fathers three of them, which then
reconverge; two records carry three parents apiece; and **Q67552's label is not a name at
all** — "Humaisi' direct to Addi \ Udd desc Malchut ben Abraham" is somebody's note about
how to route the chain, saved into the label field. Five parentless roots terminate it
without reaching Ishmael.

**Proposed:** merge the `Udd`/`Udadh`/`Addi` records into one and the `Humaisi`/`Umaisi`
records into one; the multi-parent rows resolve themselves once the duplicates collapse.
**Confidence: probable, not decided** — the transliterations are close enough that they are
plausibly one figure each, but Arabic genealogies do repeat names across generations, and
nothing here proves `'Udadh` and `Udd` are not grandfather and grandson. **Flagging rather
than asserting.** Q67552's label should be moved to a note field whichever way the merge
goes.

**Relation to M3.** This does not change the M3 recommendation. Q65555 still reaches nothing
above these roots, so it still cannot supply Muhammad a descent from Abraham — but its
parentage is now known to be *orthodox and broken* rather than fabricated, which is an
argument for preserving its edges through the merge rather than discarding them.

---

# After the decision — Emma, 2026-07-30

*"Muhammad's genealogy there is 100% intentional."*

R1 is answered: **the Emesene splice stays.** Recording what that changes, because most of
this report was written on the assumption that the splice was a defect and it is not.

## What I got wrong, and why it matters

The report's reasoning ran: Fihr's father should be Ghalib; here it is a Hellenistic
priest-king; the correct chain is present elsewhere in the dump and unused; therefore the
splice is an import artifact and the `Banu Ismail` chain is the spine waiting to replace
it. The premise was that no author would deliberately route Quraysh through Roman Syria.

I even noted the counter-evidence and walked past it. The record's own label —
**`Fihr born of Iamblichus`** — is not what a name-collision merge produces; it is what
somebody writes when they mean it. I read that as "the splice is deliberate" and then
concluded it was still wrong, which does not follow. Same with the Sampsigeramids being a
genuinely Arab dynasty: I wrote that connecting Quraysh to them "is a real (if minority)
genealogical speculation" and then filed it as a defect anyway.

## Withdrawn

| # | Was | Now |
|---|---|---|
| **R1** | cut Fihr → Iamblichus, repoint to Ghalib | **withdrawn.** The route is authored |
| **M5** | merge `Fihr Banu Ismail` Q86475 into Q153798 | **withdrawn.** It was paired with R1; merging now would import a second father onto an intentional record |
| **M6–M12** | merge the `Banu Ismail` duplicates (Ghalib, Lu'ay, Ka'b, Murrah, Kilab, Qusayy, Abd Manaf) into Muhammad's line | **withdrawn.** With the splice kept, these are not duplicates of Muhammad's ancestors — they are a parallel line, and collapsing them would pull the authored route apart |
| **Addendum (a)** | the `Banu Adnan` chain is "filler, a constructed bridge" | **withdrawn.** It is the authored connective tissue between Adnan and Emesa. Fifteen records stay |

## Still standing — none of these touch the splice

| # | Item | Status |
|---|---|---|
| M1 | `Ismail Ancestor of the Arabs` Q85869 → `Ishmael` Q129307 | see the open question below |
| M2 | `Qedar Banu Ismail` Q86435 → `Qedar (person)` Q129387 | same |
| M3 | the three Adnans → one | **still the hinge**, and the decision did not settle it |
| M4 | `Ma'ad` Q64732 → Q110802 | unaffected |
| R2 | Adnan sits at the wrong end of the `Banu Ismail` chain | unaffected — an internal error in that chain regardless of what the chain is for |
| R3 | seven records in no Quraysh list | unaffected, still "probable" |
| R4 | Qusayy/Abd Manaf inverted | unaffected — the dump contradicts itself here |
| R5 | Khuzayma missing | unaffected |
| R6 | **Q153797 has no `persons.tsv` row** | unaffected, and now *more* urgent: it sits inside an authored line, so it is a hole in intended structure rather than in junk |
| — | cut `parent(Creator BRAHMA Q1952) = Malichus Q49687` | unaffected. Nothing makes the Hindu creator god a son of a Nabataean dynast, intentionally or otherwise |

## The question the decision does not answer

**Does "intentional" cover the `Banu Ismail` chain and the three Adnan records, or only the
Emesene route?**

The two readings give opposite instructions and I am not guessing between them:

- **If the Emesene route is the only authored part**, then `Banu Ismail` is still import
  duplication — M1 and M2 proceed, and M3 resolves toward Q86433, the Adnan the authored
  route actually reaches.
- **If `Banu Ismail` is authored too**, it is a second deliberate descent line running
  parallel to the Emesene one, and M1/M2 must not be applied — merging its head into
  `Ishmael` Q129307 would fuse two lines that were built separate. M3 then has no answer at
  all, because three Adnans would be three intended figures.

One detail leans toward the second reading and is worth weighing: `Ismail Ancestor of the
Arabs` (Q85869) records **Sarah** as Ishmael's mother, not Hagar. I filed that as the
clinching evidence that Q85869 is a corrupt duplicate. It is equally the signature of a
deliberately distinct figure. I no longer think that row settles anything.

**Owner: Emma. Blocks: M1, M2, M3.** Everything else above can proceed on its own.
