# The epic's genealogy claims vs. the dump

**Swept 2026-07-30 by the autonomous work-loop (queue item 2).**

**Propose only. Nothing was edited.** No chapter text and no dump file was changed to
produce this. Each row says what the epic asserts, what the dump holds, and which side has
to move — Emma decides. Chapter *editing* is allowed outside the Leo gate, but this item
stops at the report by design.

Reproduce any row with `wiki-scripts/graph_probe.py`, e.g.
`python wiki-scripts/graph_probe.py path Q6432 Q6590`.

---

## Scope, and what this sweep does not cover

`gaiad_full.md` is 51,202 lines. A pattern sweep over genealogical predicates (`son of`,
`daughter of`, `bore him`, `begat`, `descend*`, `lineage`, `ancestor*`, `grandson`,
`trace* descent`, `line of`, `house of`, `born to`, `fathered`) found **432 lines** whose
surrounding stanza also names at least one figure resolvable to a dump record. Of those,
**153 name a figure carrying a `wikidata_qid`** — i.e. a real historical or scriptural
person the dump is meant to back, rather than one of the Gaiad's own cosmological
characters.

**33 claims across 15 chapters were then checked individually against the edge set.** That
is the contents of this report. The remaining ~120 wikidata-linked lines are mostly
rhetorical or collective ("descendants of the Yellow Emperor", "the lineage is vast") and
assert nothing a graph can falsify; they were read and set aside, not verified. **This is
not a complete audit of the epic's genealogy.** The predicate list will also have missed
claims phrased without any of those words.

---

## Verdict summary

**40 individual assertions were checked.**

| Verdict | Count | Meaning |
|---|---|---|
| CONFIRMED | 22 | the dump backs the verse |
| DATA GAP | 9 | the verse is right; the dump is missing the people or the edges |
| DATA ERROR | 4 | the verse is right; the dump holds something actively wrong |
| PROSE ERROR | 1 | the dump is right; the verse is wrong |
| EITHER SIDE | 1 | fixable from the verse or the data, and the choice is Emma's |
| UNRESOLVED | 3 | neither side decides it — flagged, not guessed |

---

## Finding 1 — The Noah node is labelled with a Sumerian king's name, and it is load-bearing

**This is the largest thing the sweep found, and it was not what the sweep was looking for.**

Chapter 132 ("Noah and the Crossing", L26884–26910) names the antediluvian line
explicitly — Seth → Enosh → Kenan → Mahalalel → Jared → Enoch → Methuselah → **Lamech, the
father — there was born a son. Noah** — and then "Shem, Ham, Japheth. Three sons."

The dump has that chain, correctly, through Lamech. Then:

```
Lamech (Q129841, wd Q10921342)
  └── Shu-Ilishu (Q70439, wd Q2997581)          <-- occupies Noah's slot
        ├── Ham      (Q129614, wd Q229702)
        ├── Japheth  (Q129720, wd Q200637)
        ├── Kanʿān   (Q129853)
        ├── Gionitus (Q129857)
        └── Puzur-Ashur (Q70442, wd Q200902)
      spouses: Naamah (Q129845), Emzara (Q131420), "Spouse of Shu-Ilishu" (Q70478)
```

The record **is** Noah — it is Lamech's son, it fathers Ham and Japheth, and its two named
spouses, **Naamah** and **Emzara**, are the two traditional names for Noah's wife. But it
is labelled `Shu-Ilishu` and carries `Q2997581`, the Wikidata item for **Shu-Ilishu, king
of Isin** (c. 1984 BCE). Meanwhile the record actually labelled `Noah` (**Q99058**) is an
unrelated node with parent `alMohsen` (Q98535) and **zero children**.

`path_up(Japheth, Q99058)` returns **NO PATH**. In the dump as it stands, **Japheth is not
descended from anything called Noah.**

**This is systemic, not a one-off.** The same overlay appears one branch over: chapter 191
says "Joktan son of **Eber**", and the dump gives Joktan (Q129712) the father
**`Ilum-bani`** (Q70454, wd Q502282) — another Isin king — whose own father is
`Naram-Ilum` (Q70451, wd Q1827950). A Mesopotamian king list has been laid over the
biblical patriarch line in this region of the graph, keeping the biblical *edges* and
substituting the Sumerian *names*.

**Consequence.** This node is the junction between the antediluvian patriarchs and the
Table of Nations. Everything downstream of Japheth hangs off it — Gomer, Magog, Togarmah,
Hayk and the whole Armenian descent (chapter 185), Ashkenaz, and the Turkic chain that
Bridge A in `planning/lineage_bridges_proposed.md` proposes to use for Genghis Khan. Any
chapter that says "descendant of Noah" is currently unsupported, not because the edge is
missing but because the node is wearing the wrong name.

**Verdict: DATA ERROR. The dump moves, not the chapter.** Recommended: relabel Q70439 to
Noah and repoint its `wikidata_qid` at Wikidata's Noah item — **look that identifier up
before applying; this report does not assert it** — then merge or retire Q99058, and
relabel Q70454 to Eber.
**Do not apply before Emma approves** — Q70439 also carries a spurious third parent
(`Ilushu` Q70436 alongside Lamech and Bat-Enosh), so it is already on the multi-parent
worklist and the two fixes should land together.

---

## Finding 2 — Jimmu is not descended from Amaterasu in the dump, because one edge is wrong

Chapter 190 ("Jimmu to Jingū", L40626–40659) makes four genealogical assertions. Three of
them fail, and they fail for one reason.

| Claim (ch. 190) | Dump | Verdict |
|---|---|---|
| "Jimmu is said to have descended from Amaterasu" | `path_up(Q6432, Q6590)` = **NO PATH** | DATA GAP |
| "the imperial line descends from the sun goddess through her grandson Ninigi" | Amaterasu → Ninigi is confirmed (grandparent). But Ninigi → Jimmu = **NO PATH** | DATA GAP |
| "Jimmu's great-grandfather was Ninigi" | **NO PATH** | DATA GAP |
| "Jimmu's great-grandmother was Toyotamahime … who bore Ugayafukiaezu, Jimmu's father" | Toyotama-hime (Q6438) is Jimmu's **grandmother**, one generation nearer than the verse says. The rest is right: she bore Ugayafukiaezu, who is Jimmu's father | PROSE ERROR |

**The single broken edge.** `Hoori` (Q6460) — Jimmu's grandfather — has parents
`Kokorohiro-no-Mikoto` (Q70230) and `Konohananosakuya-bime` (Q6485). The mother is right.
The father should be **Ninigi (Q6483)**, and instead it is a node from the Yayoi-era
placeholder chain. Correspondingly Ninigi's recorded children are `Honosusori`, `Honoakari`
and `Hoderi` — **Hoori is missing from his own father's children.**

Repointing one edge (`parent(Q6460) = Q6483` in place of Q70230) restores Ninigi → Hoori →
Ugayafukiaezu → Jimmu, and with it the descent from Amaterasu, which is the most-cited
genealogical claim in Japanese tradition and is asserted as fact in the verse.

**The prose error is separate and real.** Ninigi is Jimmu's great-grandfather; Toyotama-hime
married Ninigi's *son* Hoori, so she is Jimmu's grandmother. The chapter's parallel
couplet — "Jimmu's great-grandfather was Ninigi / Jimmu's great-grandmother was
Toyotamahime" — makes them a generational pair they are not, in the myth or in the dump.
**Fix the verse.**

**Also noted, not resolved here:** the chapter says Toyotama-hime is "daughter of the sea
dragon god"; the dump gives her father as **Xu Fu (Q6462)**. The 2026-07-30 Wikidata audit
already flagged Q6462 as carrying Watatsumi's identifier, so this may be that same known
ID defect rather than a second one. **UNRESOLVED** — it belongs to the ID-repair worklist,
not to this sweep.

---

## Finding 3 — Chapter 181, Heo Hwang-ok: the claim that started this item

Chapter 181 ("Buddhism Enters China", L39610–39636). This is the case STATUS.md item 7
recorded as a lineage gap and then declared "does not block chapter writing"; the prose
shipped, and it asserts what the graph was supposed to back.

| Claim | Dump | Verdict |
|---|---|---|
| "the legend of Heo Hwang-ok, **princess of Ayodhya**" | Heo (Q51928) has **zero parents**. Not connected to any Kosala or Ikshvaku record. Not in Adam's descent | DATA GAP — Bridge C |
| "princess of the **Kingdom of Ayuta in India**, who sailed across the sea to Korea in the first century" | Consistent with her recorded birth (+33) and with her spouse Suro (+42). Origin unsupported | DATA GAP |
| "She married King Suro of Geumgwan Gaya" | Confirmed — spouse edge Q51928 ↔ Q51924 | CONFIRMED |
| "**bore him ten sons**" | **One child**: Geodeung of Geumgwan Gaya (Q25190) | PROSE ERROR or DATA GAP |
| "two took her surname, founding the **Kimhae Heo** lineage" | **No descendant of hers carries "Heo" in its label.** 16 of her 46 descendants carry "Kim" | DATA GAP |
| "The Kimhae Heo and Kimhae Kim clans **both** trace descent from Heo Hwang-ok" | Only the Kim side exists in the dump | DATA GAP |
| "**Millions** of modern Koreans trace their lineage back" | **46 descendants** | NO ACTION, see below |

The "millions" line is not a defect. It is a claim about the world, and it is true — the
Gimhae Kim and Gimhae Heo clans together number in the millions. The dump holds 46 people
because the dump is a genealogy of named individuals, not a census. **No action.** Rows
that assert *named* structure — ten sons, two surnamed Heo — are different, because those
are exactly the kind of thing the dump is supposed to hold.

**Recommendation:** the "ten sons" figure comes from the Garakguk-gi and is defensible in
verse. The cheapest coherent fix is on the data side — add the nine further sons and the
two who take the Heo surname — but that is inventing named individuals, so it needs Emma's
call, and it is the same decision as Bridge C. **The Ayodhya row cannot be closed on the
prose side without deleting a line the Samguk Yusa actually supports.**

---

## Finding 4 — Chapter 185, Armenia: the verse is right and the dump collapsed the line

| Claim (ch. 185, L40120–40127) | Dump | Verdict |
|---|---|---|
| "Hayk, descendant of Noah **through Japheth's son**" | Japheth (Q129720) → Gomer (Q129867) → Togarmah (Q130310) → Hayk (Q131382). Japheth is Hayk's great-grandfather — matching Armenian tradition, where Togarmah is Japheth's grandson. The verse's "Japheth's son" is loose but not wrong in the tradition's own terms | CONFIRMED (with the caveat below) |
| "…descendant of **Noah**" | Fails — see Finding 1. Japheth's father in the dump is `Shu-Ilishu` | DATA ERROR |
| "from **Aram**, another ancestor, **descendant of Hayk through several fall**" | The dump makes Aram (Q132711) Hayk's **direct son** | DATA ERROR |

On the Aram row the verse is the more accurate of the two. Armenian tradition runs Hayk →
Armenak → Aramais → Amasia → Gegham → Harma → Aram, six generations, which is what "through
several fall" says. The dump has collapsed it to one edge. **Fix the dump.**

---

## Finding 5 — Chapter 191, Arabia: the Adnanite line is entirely absent

| Claim (ch. 191, L40751–40757) | Dump | Verdict |
|---|---|---|
| "Qahtan … descended from **Joktan son of Eber**" | Joktan (Q129712) exists; his father is `Ilum-bani` (Q70454), not Eber. See Finding 1 | DATA ERROR |
| "**Adnan** … descended from **Ishmael son of Abraham**" | Ishmael (Q129307) ← Abraham (Q85228) + Hagar: **CONFIRMED**. But Ishmael has only **19 descendants** in the dump and **not one of them mentions Adnan** | DATA GAP |
| "through a line of **thirty generations** laid" | Three records are named `Adnan` (Q86433, Q99030, Q111364). **None is connected to Ishmael.** The thirty-generation chain does not exist | DATA GAP |
| "Adnan had twelve sons" | Not checkable — no canonical Adnan record | UNRESOLVED |

Dozens of records carry Adnan in *patronymic strings* — `Nizar ibn Ma'ad Aladnani`
(Q64253), `Banu Rashaida ibn Ghatafan ibn Qais ibn Mudar ibn Nizar ibn Ma'add ibn Adnan`
(Q64723) — so the Adnanite genealogy is present in the dump **as text inside labels** and
absent from it **as edges**. That is a tractable extraction job and probably worth its own
queue item; it is not in this item's scope.

---

## Confirmed — the dump backs the verse

Recorded so these are not re-checked later.

| Chapter | Claim | Dump |
|---|---|---|
| 132 | Sethite line: Seth → Enosh → Kenan → Mahalalel → Jared → Enoch → Methuselah → Lamech | exact, in order |
| 154 | Jacob is son of Isaac | parent edge |
| 154 | Jacob is grandson of Abraham | 2 generations |
| 154 | Jacob, "father of twelve sons who become the twelve tribes" | all 12 present, plus Dinah — see defect 2 below |
| 159 | Rama born to Dasharatha and Kausalya | both parent edges |
| 159 | Bharata, whose mother wants him crowned instead | Bharata (Q170349) ← Dasharatha + Kaikeyi |
| 161 | "Zhou traced their lineage to Hou Ji" | Hou Ji (Q6478) → King Tai of Zhou (Q6605), 12 generations |
| 161 | King Wu, son of King Wen | parent edge |
| 164 | David is son of Jesse | parent edge; David is listed last of Jesse's 9 children |
| 166 | Nebuchadnezzar II, son of Nabopolassar | parent edge |
| 174 | Alexander, son of Philip | parent edge |
| 186 | Menelik I, son of Solomon and Sheba | both parent edges |
| 190 | Amaterasu is Ninigi's grandmother | 2 generations |
| 195 | Pepin the Short, son of Charles Martel | parent edge |
| 199 | William the Conqueror's ancestor Rollo | 5 generations |
| 203 | Jochi and Tolui, sons of Genghis and Börte | both parent edges |
| 211 | Timur "was not a direct descendant of the Mongol line" | no Timur record appears among Genghis's 349 descendants — the dump agrees with the verse's negative claim |
| 218 | Marozia, daughter of Theophylact and Theodora; her son became Pope John XI | all three edges |
| 231 | Mulek, son of Zedekiah | parent edge |

"David is the **youngest** son of Jesse" is listed as confirmed on the parentage only. The
dump records no birth order and gives Jesse seven sons against the Bible's eight, so
"youngest" is **consistent with, but not verified by,** the dump.

---

## Incidental defects (not claim mismatches — recorded so they are not lost)

1. **`Shu-Ilishu` (Q70439) has three parents** — Lamech, `Ilushu` (Q70436) and `Bat-Enosh`
   (Q70475). Bat-Enosh is the traditional name of Lamech's wife, so father + mother are
   right and `Ilushu` is spurious. Belongs to the 1,230 multi-parent worklist; fix it with
   the Finding 1 relabel.
2. **Dinah is duplicated** as Jacob's child — `Dinah` (Q129439) and `Dinah daughter of
   Jacob` (Q70568). Jacob shows 14 children where the verse says 12 sons; 12 sons + Dinah +
   duplicate Dinah = 14. The verse is right.
3. **Marozia is duplicated** — Q124161 and Q205922, both carrying `wd Q231054`, with
   different mothers (`Theodora` Q143970 vs `Theodora` Q205798) and different children.
   Pope John XI appears twice (Q143973, Q205795), as does Alberic II (Q125640, Q207190).
4. **Menelik I is duplicated** — Q113342 and `Menelik I Dawit I Emperor of Ethiopia`
   (Q71751), both children of the Queen of Sheba.
5. **Marcus Aurelius (Q63780) has three parents** — `Marcus Annius Verus` plus two records
   for his mother, `Domitia Lucilla Minor` (Q64582) and `Calvisia Domitia Lucilla`
   (Q139826).

---

## Which side moves — the decision list

| # | Chapter | Decision | Recommendation |
|---|---|---|---|
| 1 | 132, 185, 191 | The Noah node: relabel Q70439 → Noah and Q70454 → Eber, or rewrite every "descendant of Noah" line | **Dump.** The edges are already right; only the names are wrong |
| 2 | 190 | Jimmu ← Amaterasu: repoint `parent(Hoori Q6460)` from Q70230 to Ninigi Q6483 | **Dump.** One edge restores the whole descent |
| 3 | 190 | "Jimmu's great-grandmother was Toyotamahime" | **Prose.** She is his grandmother, in the myth and in the dump |
| 4 | 181 | Heo Hwang-ok "bore him ten sons" and "two took her surname" | **Emma.** Data-side fix means inventing nine named sons; prose-side fix means dropping a Garakguk-gi detail |
| 5 | 181 | Heo as princess of Ayodhya | **Blocked on Bridge C** (`planning/lineage_bridges_proposed.md`), which is itself held behind the Kosala dedup |
| 6 | 185 | Aram as Hayk's direct son | **Dump.** Restore the six intervening Haykazuni generations; the verse is right |
| 7 | 191 | The thirty-generation Adnanite line | **New queue item.** The genealogy is in the dump as label text and needs extracting into edges |
| 8 | 190 | Toyotama-hime's father recorded as Xu Fu | **UNRESOLVED** — likely the known Q6462/Watatsumi ID defect; belongs to the ID-repair pass |
