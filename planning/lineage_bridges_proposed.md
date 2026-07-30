# Lineage bridges — proposals only

**Drafted 2026-07-30 by the autonomous work-loop (queue item 1).**

**Nothing here has been applied.** No file under `wikibase/items/` and no
`wikibase/analysis/*.tsv` extract was modified to produce this document. Every claim
below was read out of the frozen dump via `edges.tsv`, `persons.tsv` and `spouses.tsv`.
Approval and application are separate, later steps.

This is proposal-drafting, not chapter generation, so the Leo gate (2026-08-12) does not
cover it. Where a bridge cannot be drafted without writing new scripture prose, the
section says so and stops rather than inventing verse.

---

## Method

`wiki-scripts/graph_probe.py` (read-only, added with this document) walks the parent/child
edge set to compute, for any QID, its ancestor closure, its descendant closure, and the set
of parentless "roots" its ancestry terminates in. Every figure below is reproducible from
it — e.g. `python wiki-scripts/graph_probe.py roots Q37401`.
The key global figure: **Adam Y Chromosomal Adam (Q152973) has a descendant closure of
42,144 of the 106,926 records in `persons.tsv`** — so "connected to Adam" is a real
partition of the dump, not a formality. About 60% of the dump is *not* under Adam.

Adam-descent in this dump is carried by Y-haplogroup pseudo-persons. Jimmu's path to
Adam, for example, is 70 steps and passes through `Sinitic O2a2b1a2 (F114)` (Q54433),
`Haplogroup F` (Q1165), `CT` (Q1158) and `A0-T` (Q1137) before reaching Q152973. That
device — a haplogroup node as the join between a named lineage and the root — is already
established practice in the dump and is used as a fallback in Bridge A below.

---

## Bridge A — Adam → Genghis Khan

### The gap, as it actually stands

Genghis Khan (Q37401) has an ancestor closure of **8 records**. In full:

```
Genghis Khan            Q37401   (wd Q720,       b. 1162)
  Yesugei               Q38821   (wd Q573157,    b. 1134)
    Bartan Baator       Q40626   (wd Q3635286,   b. 1120)
      Khabul Khan       Q42887   (wd Q982445,    b. 1085)
        Tumbinai Khan   Q45588   (wd Q4000404,   b. 1080)
          Bashinkhor Dogshin  Q48803  (wd Q114585237)
            Khaidu      Q53399   (wd Q1049910,   b. 1030, d. 1100)   <-- ROOT, no parents
  Hoelun                Q38825   (wd Q378676,    b. 1140)            <-- ROOT, no parents
```

`Q152973 ∉ ancestors(Q37401)`. The single agnatic attachment point is **Khaidu
(Q53399)**.

### The finding that changes this bridge

**The Mongol origin lineage is already in the dump, already Adam-descended, and simply
does not reach Khaidu.** Walking down from the Kosala/Ikshvaku kings:

```
Sihahanu King of Shakya      Q1911
  Suddhodana Gautama         Q153355
    The Buddha               Q153343  (wd Q9441)
      Rāhula                 Q153331  (wd Q218969)
        АЛТАН-САНДАЛИТУ-ХАГАН  Q153321
          БОРТЭЧИНЭ (Börte Chono) Q153311
            Batagi-Kaan      Q49235          [SH: Bataçiqan]
              Tamach         Q49192          [SH: Tamaça]
                Korigar-Mergen  Q49128       [SH: Qoriçar Mergen]
                  Kudzham-Boragul  Q49051    [SH: A'ujam Boro'ul]
                    Eke-Nidda  Q48958        [SH: Yeke Nidün]
                      Sim-Sauchi  Q48870     [SH: Sem Soçi]
                        Kali-Karchi  Q48802  [SH: Qarçu]
                          Bordzhigedei-Mergen  Q48730  [SH: Borjigidai Mergen]
                            ТОРОХОЛДЖИН-БАЯН Борджигин  Q153258  [SH: Toroqoljin Bayan]
                              "- "          Q153250     (unnamed placeholder)
                                БОДОНЧАР Борджигин  Q153243  [SH: Bodonchar Munkhag]
                                  БУКА Борджигин  Q153235    [Rashid al-Din: Buqa]
                                    "- "      Q153230        (unnamed placeholder)
                                      "- "    Q153225        (unnamed placeholder)
                                        БАЙСОНКУР Борджигин  Q153221
                                          … 8 further unnamed/placeholder nodes …
                                            Борджигин  Q153200
                                              Great Descendant Borjin  Q152994
                                                Great Descendant Great Descendant  Q152995
                                                  Q153645  (TERMINAL, no children)
```

Every node on that chain returns `in Adam-descent = True`. The chain is the Mongol
Buddhist chronicle tradition (*Erdeni-yin tobči*, *Altan Tobchi*), which derives the
Borjigin from the Indian kings through Rāhula, then hands off to the *Secret History of
the Mongols* genealogy from Börte Chono forward. Somebody imported it. It then runs out
into a tail of content-free "Great Descendant" placeholders and stops — **without ever
reaching Khaidu, who is standing eight generations above Genghis with no parents.**

So this is not a bridge that has to be built. It is a bridge that was built and left
one edge short.

### Proposal A1 (recommended) — one parent edge on Khaidu

Add `parent(Khaidu Q53399) = <a node on the existing Borjigin chain>`. No new records.
One line in `edges.tsv` equivalent.

**Which node is not decidable from the dump.** Both chronicle traditions agree on the
descent from Bodonchar to Qaidu:

- *Secret History*: Bodonchar → Habich Baatar → Menen Tudun → Qachi Külüg → Qaidu
- *Rashid al-Din*: Bodonchar → Buqa → Dutum Menen → Qaidu

The dump has Bodonchar (Q153243) and Buqa (Q153235), and then **two unnamed placeholder
nodes (Q153230, Q153225) before БАЙСОНКУР (Q153221)**. Under Rashid al-Din, Khaidu
attaches under Q153230 (= Dutum Menen) and the rest of the chain from Q153225 down
becomes a parallel strand with no source. Under the *Secret History*, Khaidu attaches one
generation lower. The placeholders carry no label, no date and no `wikidata_qid`, so
nothing in the dump distinguishes the two readings.

**Recommendation to Emma:** take Rashid al-Din, name Q153235 = Buqa (already so
labelled), name **Q153230 = Dutum Menen / Menen Tudun**, and attach Khaidu Q53399 as its
child. Then retire the tail from Q153225 down to Q153645 — it is fourteen placeholder
nodes ending in a record that does not exist in `persons.tsv` (see Defect 1 below), and
it exists only because the import had nowhere to put the line's continuation. Once Khaidu
is attached, that continuation *is* Genghis.

Cost if approved: 1 edge added, 2 labels set, 14 placeholder records retired.
Gain: Genghis Khan and his 349 recorded descendants enter the Adam component.

**This proposal decides a case the evidence does not fully decide** — flagging it
explicitly per the standing rule. The Bodonchar→Qaidu segment is sourced; the mapping of
*which* unnamed placeholder is Dutum Menen is a judgement call, not a reading.

### Proposal A2 (fallback) — haplogroup join

If Emma does not want the Buddhist-descent chain load-bearing for Genghis, the dump's
other device is available and is cleaner:

**`Haplogroup C` (Q1164) exists, has parent `CF` (Q1160), is Adam-descended, and has zero
children.** Genghis Khan's Y-haplogroup is C2-M217 — the best-attested fact about his
genetics. Add one node `C2 (M217)` under Q1164 and attach Khaidu beneath it, exactly as
`Sinitic O2a2b1a2 (F114)` (Q54433) sits between the Yellow Emperor's line and Adam.

Cost: 1 new node, 2 edges. Gain: identical. Invents nothing — C-M217 is a real clade with
a real position under CF.

A1 and A2 are not exclusive; A2 could carry the descent and A1 could still be repaired as
a separate correctness fix.

---

## Bridge B — Jimmu ↔ Heo Hwang-ok: **cannot be drafted as stated**

### The gap

| | Jimmu (Q6432) | Heo Hwang-ok (Q51928) |
|---|---|---|
| dump birth | −711 | +33 |
| parents in dump | Ugayafukiaezu Q6434, Tamayori-hime Q6436 | **none** |
| children in dump | 6 | **1** (Geodeung of Geumgwan Gaya Q25190) |
| Adam-descended | **yes** (70-step path) | **no** |
| descendant closure | large | 47 |

Jimmu's ancestry runs Ugayafukiaezu → Toyotama-hime (Q6438) → **Xu Fu (Q6462)** → the Xú
clan → the Wu kings → King Tai of Zhou → Hou Ji → Emperor Ku → the Yellow Emperor
(Q6420) → the haplogroup spine → Adam.

Heo's husband **Suro of Geumgwan Gaya (Q51924)** does have parents — 이비가 (Q58665) and
정견모주 (Q58668, the Gaya mountain goddess Jeonggyeon-moju) — but that pair is itself
parentless and also not Adam-descended. The entire Gaya cluster floats.

### Why no bridge is drafted here

A direct Jimmu↔Heo edge has **no legendary basis in either direction and is impossible in
the dump's own chronology**: 744 years separate them, and Heo's single recorded child is
a Gaya king whose line runs to Silla and stops. Nothing in the Kojiki, the Nihon Shoki,
the Samguk Sagi or the Samguk Yusa places Heo Hwang-ok anywhere near the Yamato line.
Drafting the edge would mean writing the connecting figures out of nothing — which is the
stop condition this queue item names. **Stopping here.**

### What *can* be drafted, if Emma re-scopes the bridge to "join Japan to Korea"

**B1 — Prince Junda → Yamato no Ototsugu. One edge, fully sourced, both endpoints already
in the dump.**

`Takano no Niigasa` (Q7502, b. 720), mother of `Emperor Kanmu` (Q7508), has parents
`Yamato no Ototsugu` (Q7687) and `Haji no Maimo` (Q7688). **Q7687 is a parentless root.**
The *Shoku Nihongi* records the Yamato no Fuhito line as descending from **Prince Junda**,
son of **King Muryeong of Baekje** — the descent Emperor Akihito acknowledged publicly in
2001. Both are already present: `Prince Junda` **Q9935** (b. 450, wd Q15113421, currently
childless) and `Muryeong of Baekje` **Q10437** (b. 462, wd Q497878).

Note the dump gives Junda b. 450 and his father Muryeong b. 462 — the son is older than
the father. That is an independent defect on the same records and should be fixed in the
same pass.

Adding `parent(Q7687) = Q9935` puts the Japanese imperial line and a Korean royal house in
one connected component. **It does not reach Heo**: it joins Baekje, not Gaya, and it
joins through Kanmu's mother, not through Jimmu's agnatic descent.

**B2 — Ame-no-Hiboko. Two new nodes, sourced, weaker.**

`Tajimamori` (Q7074) has a two-person ancestry rooting at `Tajima no Kiyohiko` (Q7075).
In the Kojiki, Kiyohiko descends from **Ame-no-Hiboko, a prince of Silla** who crossed to
Japan; the same line produces `Kazuraki no Takanukahime` (Q7000), mother of `Empress
Jingū` (Q153782). **Ame-no-Hiboko is absent from the dump.** Adding him plus one
intermediate and attaching Q7075 beneath him gives a Silla→Japan legendary bridge. It
also does not reach Heo.

### Verdict

**UNRESOLVED.** Bridge B as specified ("Jimmu ↔ Heo Hwang-ok") should be struck and
replaced with B1, or with B1+B2. Emma's call — the evidence rules out the bridge as
written rather than choosing between readings of it.

---

## Bridge C — Kosala → Heo Hwang-ok

### The legendary basis, which is solid

The *Samguk Yusa*'s **Garakguk-gi** states that Heo Hwang-ok came by sea from **아유타국 /
阿踰陀國, "Ayuta"**, traditionally identified with **Ayodhya**, capital of Kosala. This is
the one bridge of the three with a direct primary-source warrant. It needs **one parent
edge on Heo (Q51928)**, who currently has none.

### The Kosala material in the dump

58 records carry "Kosala" in the label. They are **not one king list — they are three
near-identical parallel Geni imports**:

- the **Q19xx–Q26xx** series (has birth dates)
- the **Q49xxx–Q51xxx** series
- the **Q160xxx–Q161xxx** series

e.g. `Prasenajit II of Kosala` appears as Q2247, Q51154 and Q161111; `Divakara, King of
Kosala` as Q2123, Q50564 and Q160843. All three are Adam-descended via the Ikshvaku /
Solar dynasty. **Any edge added before these are deduplicated will land on an arbitrary
one of three duplicates.**

The chain itself is complete and correctly ordered against the Puranic continuation. Below
Hiranyanabha (Q2261) it runs Pusya → Dhruvasandhi → Sudarshana → Agnivarna → Shighra →
Maru → Prasushruta → Susandhi → Amarsha → Shasvant → Vishrutavant → Vishvabahu →
Prasenajit → Takshaka → Brihadbala → Brihatkshatra → … → Pratikanshva (Q2069) → Supratika
(Q153467) → Marudeva → Sunakshatra → Pushkar → Kinnarasva → Suparna → **Sumitra Amitrajit
I (Q1994)** → Brihadhvaj → Dharmi → Kritanjaya → Rananjaya → Jayasena → **Sihahanu King of
Shakya (Q1911)** → Suddhodana → the Buddha.

So the Ayodhya list in the dump runs all the way to Sumitra — the last Ikshvaku king of
Ayodhya, deposed by Mahapadma Nanda in the 4th century BCE — and then turns into the
Shakya branch and exits toward the Buddha.

### The gap that is left

**Sumitra (~4th c. BCE) → Heo Hwang-ok (b. 33 CE) is roughly 350 years, twelve to
fourteen generations, and no source names a single one of them.** This is exactly
STATUS.md's "~15–20 invented kings". The Samguk Yusa asserts the origin and names nobody.

### Options, none of them free

**C1 — one edge, chronology sacrificed.** `parent(Q51928) = Q1994` (Sumitra Amitrajit I),
or whichever king the dedup picks as the canonical last Ayodhya king. Zero new records.
Cost: the dump then asserts a father 350 years older than his daughter, in a graph whose
whole QA programme is about not asserting things like that.

**C2 — chronology respected, 12–14 invented kings.** This is writing new scripture
material. It is the stop condition for this queue item. **Not drafted.**

**C3 — the Dakshina Kosala pair.** `King Sukaushala of Dakshina Kosala` (Q51392) and
`Queen Amritaprabha` (Q51397) are a parentless married couple whose only child is
`Kausalya` (Q51372), Rama's mother. Attaching Heo here is chronologically no better and
gains nothing: **the pair is not Adam-descended**, so the bridge would not even deliver
the descent it exists to deliver. Recorded so the option is not re-proposed later.

### Recommendation

**Hold C behind the Kosala dedup.** Picking the attachment point is meaningless while
three copies of the king list exist. Once dedup lands, C1 is the honest minimum — one
edge, the chronology break documented on the record rather than papered over with
invented generations.

---

## Defects found while doing this (not part of the brief, recorded here so they are not lost)

1. **138 edge endpoints in `edges.tsv` have no row in `persons.tsv`.** Among them
   **Q153645**, which is the terminal node of the Borjigin chain in Bridge A. Sample:
   Q114350, Q134760, Q153645, Q153797, Q164426, Q166980, Q54196, Q65231, Q72356, Q74494.
2. **The Kosala king list is triplicated** across three Geni imports (see Bridge C).
3. **Kosala/Ikshvaku birth dates are positive CE years** — 1075, 1150, 1225, 1650 — for
   kings the same dump places before the Buddha (b. 563). Geni junk; they sort the list
   backwards and cannot be used for ordering.
4. **Adam (Q152973) has three parents**: `Homo sapiens` (Q1131), `Ante Adam`
   (Q105575574), and an unlabelled Q30876. Not wrong for this dump's cosmology, but it
   means "Adam is the root" is false as stated — the root is above him.
5. **Prince Junda (Q9935) is recorded as born 450, his father Muryeong (Q10437) as born
   462.** See Bridge B1.

---

## What Emma has to decide

| # | Decision | Blocking |
|---|---|---|
| 1 | Bridge A: take A1 (attach Khaidu to the existing Borjigin chain), A2 (haplogroup C2-M217), or both | A1 needs the Rashid al-Din vs Secret History generation call |
| 2 | If A1: confirm Q153230 = Dutum Menen, and confirm retiring the 14-node placeholder tail | — |
| 3 | Bridge B: strike "Jimmu ↔ Heo" and substitute B1 (Prince Junda → Yamato no Ototsugu), or drop the bridge | — |
| 4 | Bridge C: hold behind Kosala dedup, then C1 | Kosala dedup |
| 5 | Whether the shipped Heo Hwang-ok chapter's Ayodhya claim is prose to fix or data to build | queue item 2, in progress |
