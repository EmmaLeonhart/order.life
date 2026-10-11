# Closed repairs — how each tangle was actually settled, and what must not be re-tried

Moved out of `queue.md` on 2026-08-16. These items were finished but kept on the board for
days because deleting them would have thrown away the reasoning, and `queue.md` is the
cockpit's rendering of this repo — a finished item sitting in it reads as live work.

**This file exists so the deletion was safe.** Every trap below is here because someone
(usually me) was about to repeat it.

**The dump has held `tangled_components = 0` since 2026-08-15.** There is no ancestry cycle
left. Re-read the live number from `check_invariants.py`, never from a document.

---

## ⚠ THE ONE THAT MUST NOT BE RE-PROPOSED: Daksha (old item 3)

**The Puranic ring was NOT closed by splitting Daksha. That split was applied and reverted
the same day, 2026-08-07. Do not re-propose it.**

Splitting Daksha *did* open both rings, and it was still the wrong repair:

- **The sixty daughters belong to the SECOND Daksha.** Aditi, Diti, Danu and Kadru married
  to Kashyapa, the 27 nakshatras married to Chandra, the 10 married to Dharmadeva — that
  whole set is canonically the issue of **Prachetasa Daksha by Asikni**. The first Daksha,
  Brahma's son, married Prasuti and fathered Sati. The dump's 63 children are unmistakably
  the second set. The split moved them onto a first-birth Daksha to open the ring, which is
  backwards, and **it only opened the ring *because* it was backwards.**
- **The real defect was one edge away.** `Q153444` "SUNITA Anga" had `Q2035` Yama as her
  father. Sunitha, wife of Anga and mother of Vena, is the daughter of **Mrityu** — Death
  personified, a separate figure carried on Wikidata as `Q12735987`. Two death-figures
  conflated into one, the same shape as the Lepidus record.

**The repair that stands is `apply_sunita_mrityu.py`** — Mrityu created in both copies
(`Q200020`, `Q200021`), Sunitha's parentage moved onto him, Shyamala dropped as her mother
since she is *Yama's* wife and came with the same conflation. Both rings open, Daksha keeps
his Prachetas parentage and all sixty daughters.

**The general lesson, and it is `cycle_policy.md`'s own: opening a loop is not evidence of
having found its defect.** The split was reachable from the ring alone, and wrong. If the
only way to open a loop is to move something that belongs where it is, the defect is
elsewhere.

Emma's ruling that a genuine rebirth ring gets split still governs — the Gaiad's descent is
linear. But **check first that the loop is actually a rebirth** and not a conflation of two
figures one edge away.

**One narrower trap worth keeping:** `Q49634.json` is a shadow file whose own `id` is
`Q1955` — byte-identical, and `redirects.tsv` maps one to the other. Daksha's "two fathers"
were one man referenced twice, once directly and once through a redirect qid. **Check
whether a second father is a redirect before reading it as a second parentage.**

---

## The four rings closed by external evidence, 2026-08-07

The pattern in all four: **the evidence was never in the dump.** Each had been filed as
undecidable, and each fell to one lookup or one date.

### Joan / Llywelyn Ddû — `apply_lleucu_generation.py`, 3 files

False edge: `Q140681` Lleucu → `Q140643` Rhys ap Llowdden y Gath.

`Q137927` Owain's mother `Q137334` Gwenllian is a granddaughter of **Rhys Gryg, who died in
1234** (Dictionary of Welsh Biography). That fixes Owain's generation from outside the ring,
and both arms run outward from him along patronymically-confirmed links — down to Lleucu at
c. 1370, up through Joan's own name to Rhys at c. 1200. **Lleucu cannot be the mother of a
man born 170 years before her**, and the argument holds whichever maternal claim is true,
because Llywelyn Ddû is dated by his *father*.

The mechanism is **Welsh papponymy**: Llowdden Hen → Rhys → Llowdden y Gath → Rhys → Ieuan
→ Joan. Two women called Lleucu ferch Gruffudd merged into one record — the dump said so
itself, since she carried **two husbands two centuries apart**. Wikidata carries neither
marriage.

Rhys's mother is now unrecorded. The woman who married Llowdden y Gath c. 1190 is a
different Lleucu; naming her wants Bartrum's Llowdden charts and she is **not invented
here**.

### The Portuguese ring — `apply_tereza_eriz.py`, 6 files

False edge: `Q79537` Estêvão Soares → `Q79618` Tereza **Eriz** de Lugo.

**Three of the four flags raised against this ring were false alarms**, and that is the
part worth remembering. `Q79415` Soeiro Ausendes → `Q79435` Arnaldo **Ximenes** is
*attested* — the Casa de Baião lineage has exactly that father and son, and Arnaldo died at
**Las Navas de Tolosa, 16 July 1212**. So *Ximenes* is a **house name here, not a
patronymic**, and the objection to `Q113625` → `Q79388` falls with it.

The fourth flag is real, and chronology confirms it from outside the ring. Tereza's
descendants reach **D. Mem Viegas de Sousa, b. 1070** five generations down, placing her
**c. 920** — exactly right for *Eriz de Lugo*, since **Ero Fernandez, count of Lugo, died
c. 926**. Estêvão stands five generations below Arnaldo (d. 1212), so **c. 1325**. A gap of
about 400 years. Her real father `Q100140` Ero Fernandez de Lugo was already in the dump.

### The eight Servilii — `apply_servilii_chain.py`, 12 files

False edge: `Q73332` → `Q73170`.

**Both exits from the ring are externally datable, which is what makes the argument
non-circular.** `Q73170` → `Q73008` → five generations → `Q71173` **P. Servilius Vatia
Isauricus, b. 120 BC** (wd `Q392647`), so `Q73170` stands six generations above 120 BC:
**c. 300 BC**. `Q73910` → `Q78378` → ten generations → `Q89776` **Claudia Acilia, b. AD
185**, so `Q73910` is eleven generations above that: **c. 145 BC**.

The ring's long arc makes `Q73170` six generations *younger* than `Q73910` — c. AD 35
against his own anchor of c. 300 BC, a **335-year contradiction**. Only the last edge
collides with an externally dated record, asking a man of c. 90 BC to father one of c. 300
BC.

It cost nothing: verified before writing that `Q73170`'s only ancestors were the other seven
members, and that the component does not reach Aster.

### The two Esthers — `apply_esther_generation.py`, 8 files

**Abu 'Amr Sahlan ben Abraham married Esther, daughter of Joseph ben 'Amram, chief judge of
Sijilmasa. The ketubba survives, dated September 1037** (Encyclopedia of Jews in the Islamic
World, s.v. Sahlān b. Abraham). So reading **B**: Esther *bat Yosef* married Sahlan, and
their daughter is Esther *bat Sahlan*. Reading A — cut and reverted on 2026-08-01 — would
marry Esther bat Sahlan to her own maternal grandfather.

The dump corroborated it unaided: `Q90982` already carried `P42` = `Q91024` Sahlan, and both
already listed `Q88454` as their child. **The defect was that `Q88454` held her mother's
life on top of her own** — recorded as Yosef's wife and as her own mother's mother. A
same-name collapse across two generations, which papponymic naming is what made possible.

**The lesson, and it generalises to everything above:** the queue called this "genuinely
undecidable from the dump" and was right — and it was decidable in **two web searches**.
**Undecidable from the dump is not undecidable.**

---

## The Licinii Vari (old item 2) — closed 2026-08-15, and a finding withdrawn

**The line is fine. Do not repair it.** The Republic descends through `Q73308` → `Q73140`
Gaius Licinius Varus (cos. 236 BC) → `Q72966` Licinia, who married `Q72963` Q. Mucius
Scaevola and bore `Q72807` P. Mucius Scaevola (cos. 175 BC). All three Vari records carry
Geni ids and no Wikidata id, **and that is fine** — Emma, 2026-08-15.

For a few hours that day this was written up as a defect: that `Q72966` and `Q72810` were
one Licinia imported twice a generation apart. **Withdrawn.** They are two distinct Geni
profiles; two Licinias marrying into the Mucii Scaevolae in successive generations is
ordinary Roman prosopography; and Wikidata's silence was read as refutation, against this
repo's own written rule. Full account in `licinii_vari_resolved.md`.

**The transferable part:** that mistake came directly after six consecutive ticks of finding
*real* defects of the same silhouette — duplicate imports, displaced generations, GEDCOM
artifacts with no Wikidata id. **Being freshly primed by genuine finds made the false
positive more likely, not less.** A record matching the shape of the last six defects has
earned more scepticism, not less.


## Magadha/Kosala dedupe (queue item 0f) — closed; moved out of queue.md 2026-10-10

The rest was ruled out by Emma on 2026-08-18 (the `Q160xxx` block), so the item held only its record. Verbatim:

0f. **FINISH THE MAGADHA/KOSALA DEDUPE. Senajit up to VRIHADRATHA and Diwakar up to
   Prativyoma are merged; the levels above each remain.**

   **DONE:** 131 merges (`magadha-triple`), 27 stale refs cleared, 11 more merges
   (`magadha-tail`), and on **2026-08-18** three more clusters — `magadha-senajit`
   (17 merges: the three dropped SENAJIT pairs, every generation above them as far as
   SOMAPI, and the six nameless shells that were blocking all of it) and
   `kosala-diwakar` (9 merges: the five copies of Sahdev Diwakar, Divakara, Bhanu,
   Prativyoma, and the BRIHADASVA pair `magadha-tail` dropped), then `magadha-somapi`
   (9 merges: SOMAPI, SAHADEVA, JARASANDHA, two more nameless VRIHADRATHA copies, and the
   two wives they hang from). All six gates green on all three;
   `children_over_2_parents` **1200 → 1199 → 1198 → 1196**, and the 1200 → 1199 is exactly
   the number this item predicted from the cause it named. **177 duplicate records gone
   in total.**

   **THE PRESCRIBED REPAIR FOR THE SHELLS WAS WRONG AND THIS IS WHY.** This item called
   `Q52176` and `Q52188` "empty records in parent slots" and said to cut. They are a
   **fourth, nameless copy of the Magadha king list**, running beside the `Q2xxx`,
   `Q51xxx` and `Q161xxx` copies. Nothing on the record says so — no label, no alias, no
   description, one non-genealogical claim — but every one of them sits in a named king's
   exact slot, offset one generation at a time:

   | shell | child of | father of | therefore |
   |---|---|---|---|
   | `Q52176` | `Q2292` SUKSHATRA | `Q2286` SENAJIT | BRIHATKARMAN |
   | `Q52188` | `Q2296` NIRAMITRA | `Q2289` BRIHATKARMAN | SUKSHATRA |
   | `Q52204` | `Q2299` AYUTAYUS | `Q2292` SUKSHATRA | NIRAMITRA |
   | `Q52216` | `Q2302` SRUTASRAVA | `Q2296` NIRAMITRA | AYUTAYUS |
   | `Q52228` | `Q28284` SOMAPI | `Q2299` AYUTAYUS | SRUTASRAVA |
   | `Q52240` | `Q28300` SAHADEVA | `Q2302` SRUTASRAVA | SOMAPI |

   That sequence is the Vishnu Purana's Brihadratha succession, which the named chain also
   records in order. The last line was not read off the position at all —
   `match_parallel_imports.py` propagated the correspondence structurally and landed
   `Q52240` opposite `Q161236` "SOMAPI Sahadeva" on its own, which is what made the
   "empty slot" reading collapse. **Cutting would have removed the six father-edges and
   left six nameless childless records hanging off the kings above them; merging removes
   the same edges and retires the record.** DEDUPE outranks CUT in `cycle_policy.md` and
   this is the case it is for. The cut was written, applied, and reverted before
   committing.

   **Two rules confirmed on live data, worth keeping:**

   - **A nameless record is not necessarily contentless.** Position is evidence. Six
     records with one claim between them turned out to be six kings.
   - **A shell whose child would be orphaned is not cuttable and was not cut.** `Q52240`
     was `Q2302` SRUTASRAVA's *only* declared father. Same condition as the divine-father
     rule: only remove a parent where a named one survives.

   **STILL OPEN — and the shape of what is left is known, which it was not before.**

   **EVERY CLUSTER OF THIS KIND MUST STOP ONE LEVEL SHORT, so this is iterative by
   construction and not one big merge.** Each level's copies each carry their own copy of
   the next man up, so the TOP group of any cluster inherits three unmerged fathers and
   fails I4. `magadha-triple`, `magadha-tail`, `magadha-senajit`, `kosala-diwakar` and
   `magadha-somapi` each stopped for exactly this reason. It is not a compromise and it is
   not a bug to fix — plan on one cluster per few generations.

   **STOPPED BY EMMA, 2026-08-18 — `CLAUDE.md` § *The `Q160xxx` Puranic block*.**

   Everything that was open here ran through the `Q160xxx` block: the Magadha chain above
   King VRIHADRATHA, the Kosala chain above Prativyoma, and the 67-pair closure that
   scored 1196 → 1195. Asked whether that block is duplicates or deliberate, she ruled
   **do not use that portion of the tree at all.** So none of it is pending work and none
   of it is blocked — it is ruled out, which is a different thing, and the queue should
   not carry it as either.

   **What remains of item 0f is the record of what was done**, above: 177 duplicate
   records retired across five passes, `children_over_2_parents` 1200 → 1196,
   `qa_vacated_refs` 0, every gate green on every pass. That stands; the ruling was about
   what to do next, not about undoing it.

   **⚠ "A DEDUPE HERE GAINS DEPTH" IS DISPROVEN. Five times now.** Item 0d argued the
   merge would hand the surviving chain ancestry it lacked, because `Q2206` Ashoka had no
   father. All five merges measured **0 records gained depth and 0 lost**; total depth
   fell only because duplicate nodes stopped existing (−40,120, then −4,459, then −5,700, then −3,612, then −2,313).
   The chains were parallel **and already joined**, so collapsing them removes nodes
   without changing anyone's reach. The reason to do this is that 177 phantom people are
   gone, not depth. **Do not re-file the depth argument.**


## Brahma and the eleven Rudras (queue item 4) — closed 2026-10-10, the cut stands

Decided without Emma, on the instruction to make the call: the cut stands and is not reverted. Every record in it (`Q160946`, `Q160966`, `Q160947`) is in the `Q160xxx` block, which Emma ruled out of use on 2026-08-18 ("the best rule is to not use that portion of the order.life tree at all"), so no further change there, a revert included. If she wants the Shaiva reading, the revert is one command (`cut_edges.py`, cut set `brahma-rudras`). The item, verbatim:

4. **ONE CUT TO SANITY-CHECK IF YOU DISAGREE — Brahma and the eleven Rudras
   (2026-08-02, applied).** Tangle 15 was cut on the reading that `Q160946` "11 Rudras" is
   the **Kashyapa-and-Surabhi** set of the Vishnu Purana — its mother in the dump is
   `Q160966` **Surbhi** — and therefore Brahma's descendant, not his parent. Brahma keeps
   `Q160947` **Gobardhan Vishnu**, his canonical birth.

   **The reading I rejected, in case it was yours:** in Shaiva cosmology Shiva *does*
   generate Brahma, and a Shaiva/Vaishnava synthesis is exactly the kind of cross-tradition
   join this project exists to make. I ruled it out because the record is the *eleven*
   Rudras with a named father and mother, not Rudra-Shiva the creator. **If the intent was
   the Shaiva reading, this cut is wrong and is one revert** — `cut_edges.py`, cut set
   `brahma-rudras`.
