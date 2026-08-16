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
