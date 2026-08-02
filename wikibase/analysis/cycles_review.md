# Ancestry cycles — every one, with the numbers that decide them

**27 cycles, 254 records caught in one.** Generated from the dump by `wiki-scripts/build_cycles_notion.py`; the source of truth is `wikibase/analysis/cycles_review.md` in the repo and this page is a copy of it.

A cycle here means a **strongly connected component** — a set of records where everyone is reachable from everyone else by following parent links, so at least one person is their own ancestor. That is always an error. Which *edge* is the wrong one usually is not obvious, and this document does not decide it.

## How to read the ancestor column

**`ancestors` is the only column that ranks anything.** It counts the distinct records reachable upward from that person. Cutting an edge that collapses this number is severing a gateway — the thing `cycle_policy.md` says never to do. `descendants` is there as context and deliberately ranks nothing; `qa_cycles_load.tsv` ranks by descendants lost and is wrong to.

`depth` is the longest chain upward, computed over the cycle-condensed graph so it stays well defined. `→Aster` marks whether `Q1` Aster is reachable upward.

Within a cycle every member usually shows the *same* ancestor count, because they can all reach each other and therefore reach the same set. That is the cycle itself showing up in the data.

---

## 1. Constantius Chlorus — 71 records

Shortest loop: `Q61565 -> Q136506 -> Q73308 -> Q73140 -> Q72966 -> Q72807 -> Q72633 -> Q72451 -> Q72266 -> Q70970 -> Q70337 -> Q69263 -> Q67573 -> Q66488 -> Q65258 -> Q64388 -> Q63684 -> Q63157 -> Q62680 -> Q62255 -> Q61957 -> Q61565`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q61565` | Constantius Chlorus | Q131195 | 250 | 306 | **3,173** | 19,764 | 195 | yes |
| `Q61957` | Claudia Crispina | Q867859 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q62255` | Aurelia Pompeiana | Q109793322 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q62680` | Mariana Minor | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q62704` | Lucius Aurellius Commodus Pompeianus | Q716684 | 176 | 212 | **3,173** | 19,764 | 195 | yes |
| `Q63157` | Pendania | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q63192` | Lucilla | Q242466 | 150 | 182 | **3,173** | 19,764 | 195 | yes |
| `Q63684` | Ummidia Commificia Antonia | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q63747` | Faustina the Younger | Q236936 | 125 | 175 | **3,173** | 19,764 | 195 | yes |
| `Q63780` | Marcus Aurelius | Q1430 | 121 | 180 | **3,173** | 19,764 | 195 | yes |
| `Q64355` | Gaius Ummidius Quadratus Annianus Verus  Fulvi | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q64388` | Annia Cornificia Faustina | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q64483` | Faustina the Elder | Q234734 | 105 | 140 | **3,173** | 19,764 | 195 | yes |
| `Q64516` | Antoninus Pius | Q1429 | 86 | 161 | **3,173** | 19,764 | 195 | yes |
| `Q64549` | Marcus Annius Verus | Q1292169 | 94 | 120 | **3,173** | 19,764 | 195 | yes |
| `Q64582` | Domitia Lucilla Minor | Q1815905 | 100 | — | **3,173** | 19,764 | 195 | yes |
| `Q65192` | Gaius Annianus Verus | Q12275936 | 100 | — | **3,173** | 19,764 | 195 | yes |
| `Q65225` | Annia Cornificia Faustina | Q1284248 | 123 | 152 | **3,173** | 19,764 | 195 | yes |
| `Q65258` | Rupilia Faustina | Q2068391 | 87 | 101 | **3,173** | 19,764 | 195 | yes |
| `Q65489` | Hadrian | Q1427 | 76 | 138 | **3,173** | 19,764 | 195 | yes |
| `Q65552` | Domitia Lucilla | Q12278988 | 50 | — | **3,173** | 19,764 | 195 | yes |
| `Q66488` | Libo Rupilius Frugi | Q1237511 | 1 | 101 | **3,173** | 19,764 | 195 | yes |
| `Q66784` | Andhra Pradesh | Q1159 | 53 | 117 | **3,173** | 19,764 | 195 | yes |
| `Q66916` | Curtilia Mancia | Q107638183 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q67573` | Marcus Licinius Crassus Frugi | Q764528 | 27 | 67 | **3,173** | 19,764 | 195 | yes |
| `Q68283` | Nerva | Q1424 | 30 | 98 | **3,173** | 19,764 | 195 | yes |
| `Q68488` | Octavia | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q69263` | Scribonia Magna | Q774986 | 5 | 47 | **3,173** | 19,764 | 195 | yes |
| `Q69296` | Marcus Licinius Crassus Frugi | Q1233627 | 50 | — | **3,173** | 19,764 | 195 | yes |
| `Q69972` | Octavia Sergia Plotilla | Q12293630 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q70152` | Rubellia Bassa | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q70337` | Cornelia Pompeia Magna | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q70340` | Lucius Scribonius Libo | Q153600 | 50 | — | **3,173** | 19,764 | 195 | yes |
| `Q70343` | Marcus Licinius Crassus Dives | Q3622613 | 50 | — | **3,173** | 19,764 | 195 | yes |
| `Q70346` | Fausta  Cornelia | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q70718` | Gaius Rubellius Blandus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q70970` | Pompeia Magna | Q442503 | 70 | 35 | **3,173** | 19,764 | 195 | yes |
| `Q71026` | Marcus Pupius Piso Frugi | Q11768202 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q71083` | Faustus Cornelius Sulla | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q71628` | Lucius Rubellius Blandus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72239` | Vipsania Agrippina | Q232090 | — | 20 | **3,173** | 19,764 | 195 | yes |
| `Q72266` | Mucia Tertia | Q273616 | 95 | 31 | **3,173** | 19,764 | 195 | yes |
| `Q72278` | Marcus Pupius Piso Frugi Calpurnianus | Q510243 | 114 | — | **3,173** | 19,764 | 195 | yes |
| `Q72338` | Rubellius Blandus | Q111335237 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72425` | Attica | Q152626 | 55 | 28 | **3,173** | 19,764 | 195 | yes |
| `Q72451` | Quintus Mucius Scaevola Pontifex | Q503187 | 140 | 82 | **3,173** | 19,764 | 195 | yes |
| `Q72466` | Marcus Licinius Crassus | Q175121 | 115 | 53 | **3,173** | 19,764 | 195 | yes |
| `Q72603` | Pilia | Q2292963 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72633` | Publius Mucius Scaevola | Q261441 | 180 | 114 | **3,173** | 19,764 | 195 | yes |
| `Q72657` | Publius Licinius Crassus Dives | Q656527 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72774` | Licinia Crassa  Pilius | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72807` | Publius Mucius Scaevola | Q2066659 | 300 | 200 | **3,173** | 19,764 | 195 | yes |
| `Q72810` | Licinia | Q12284962 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72831` | Marcus Licinius Crassus | Q19715630 | 150 | — | **3,173** | 19,764 | 195 | yes |
| `Q72933` | Marcus Licinius Crassus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72966` | Lincinia  Varus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72972` | Publius Licinius Crassus Dives | Q29518656 | — | — | **3,173** | 19,764 | 195 | yes |
| `Q72981` | Publius Licinius Crassus | Q20100913 | 300 | 150 | **3,173** | 19,764 | 195 | yes |
| `Q73083` | Publius Licinius Crassus Dives (consul 97 BC) | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q73140` | Gaius Lincinius  Varus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q73260` | Marcus Licinius Crassus Agelastus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q73308` | Licinius  Varus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q73665` | Publius Licinius  Crassus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q73770` | Publius Licinius  Crassus | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q77386` | Julia Livia | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q77611` | Drusus Julius Caesar | Q313737 | 13 | 23 | **3,173** | 19,764 | 195 | yes |
| `Q99408` | Publius Licinius Varus Licinius Crassus  Crass | — | — | — | **3,173** | 19,764 | 195 | yes |
| `Q136506` | Flavia Julia Constantia | Q238023 | — | 330 | **3,173** | 19,764 | 195 | yes |
| `Q138467` | Julia Livia | Q266030 | 5 | 43 | **3,173** | 19,764 | 195 | yes |
| `Q139746` | Cornelia Magna | Q3656046 | 1 | — | **3,173** | 19,764 | 195 | yes |
| `Q141756` | Annia Rupilia Faustina | Q111988914 | — | — | **3,173** | 19,764 | 195 | yes |

**What the data says**

- Q64388, Q65225 share the label “Annia Cornificia Faustina”.
- Q77386, Q138467 share the label “Julia Livia”.
- Q72466, Q72831, Q72933 share the label “Marcus Licinius Crassus”.
- Q67573, Q69296 share the label “Marcus Licinius Crassus Frugi”.
- Q73665, Q73770 share the label “Publius Licinius  Crassus”.
- Q72657, Q72972 share the label “Publius Licinius Crassus Dives”.
- Q72633, Q72807 share the label “Publius Mucius Scaevola”.
- `Q64516` Antoninus Pius has 3 parents: Q65423, Q65456, Q65489.
- `Q65192` Gaius Annianus Verus has 3 parents: Q66425, Q66455, Q141756.
- `Q65489` Hadrian has 4 parents: Q66718, Q66751, Q66784, Q66817.
- `Q66784` Andhra Pradesh has 3 parents: Q68223, Q68256, Q68283.
- `Q69972` Octavia Sergia Plotilla has 4 parents: Q70122, Q70152, Q70685, Q144242.
- `Q70152` Rubellia Bassa has 3 parents: Q70718, Q70751, Q77386.
- `Q70340` Lucius Scribonius Libo has 3 parents: Q70988, Q71002, Q139746.
- `Q72278` Marcus Pupius Piso Frugi Calpurnianus has 4 parents: Q72463, Q72466, Q72469, Q141610.
- `Q72933` Marcus Licinius Crassus has 3 parents: Q72657, Q73083, Q73098.
- `Q72972` Publius Licinius Crassus Dives has 3 parents: Q72912, Q73665, Q99408.
- `Q73260` Marcus Licinius Crassus Agelastus has 5 parents: Q72969, Q72972, Q72981, Q73407, Q73410.
- Wikidata contradicts `Q72972` → `Q72810`: Wikidata records no link between them
- Wikidata contradicts `Q72981` → `Q72831`: Wikidata records no link between them
- Recorded births in this cycle: Constantius Chlorus 250; Lucius Aurellius Commodus Po 176; Lucilla 150; Faustina the Younger 125; Marcus Aurelius 121; Faustina the Elder 105; Antoninus Pius 86; Marcus Annius Verus 94; Domitia Lucilla Minor 100; Gaius Annianus Verus 100; Annia Cornificia Faustina 123; Rupilia Faustina 87; Hadrian 76; Domitia Lucilla 50; Libo Rupilius Frugi 1; Andhra Pradesh 53; Marcus Licinius Crassus Frug 27; Nerva 30; Scribonia Magna 5; Marcus Licinius Crassus Frug 50; Lucius Scribonius Libo 50; Marcus Licinius Crassus Dive 50; Pompeia Magna 70; Mucia Tertia 95; Marcus Pupius Piso Frugi Cal 114; Attica 55; Quintus Mucius Scaevola Pont 140; Marcus Licinius Crassus 115; Publius Mucius Scaevola 180; Publius Mucius Scaevola 300; Marcus Licinius Crassus 150; Publius Licinius Crassus 300; Drusus Julius Caesar 13; Julia Livia 5; Cornelia Magna 1

**Decision:** _not made — needs Emma_

---

## 2. Petronia — 18 records

Shortest loop: `Q62515 -> Q75817 -> Q75721 -> Q75781 -> Q75694 -> Q75634 -> Q75573 -> Q75543 -> Q75522 -> Q75516 -> Q75603 -> Q75558 -> Q65002 -> Q64169 -> Q63517 -> Q62926 -> Q62515`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q62515` | Petronia | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q62926` | Gnaeus Petronius Probatus Junior  Justus | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q63517` | Petronius  Junior | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q64169` | Petronius | Q120232596 | — | — | **4,259** | 19,331 | 196 | yes |
| `Q65002` | Sextus Claudius Petronius Probus | Q1542092 | 328 | 388 | **4,259** | 19,331 | 196 | yes |
| `Q75516` | Anicius Hermogenianus Olybrius | Q1372249 | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75522` | Anicia Faltonia Proba | Q1154373 | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75540` | Quintus Clodius Hermogenianus Olybrius | Q1148526 | 335 | 380 | **4,259** | 19,331 | 196 | yes |
| `Q75543` | Tyrrania Anicia Juliana | Q12296367 | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75558` | Clodia Celsina | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75573` | Anicius Auchenius Bassus | Q2289711 | 350 | 408 | **4,259** | 19,331 | 196 | yes |
| `Q75576` | Clodius Celsinus Adelphius | Q1147586 | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75603` | Demetrias | Q3625008 | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75634` | Caeionia Auchenia Bassa | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75694` | Caeionius Julianus Camerius | — | — | 334 | **4,259** | 19,331 | 196 | yes |
| `Q75721` | Rufia Procula | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75781` | Caeionius  Proculus | — | — | — | **4,259** | 19,331 | 196 | yes |
| `Q75817` | Publilia | — | — | — | **4,259** | 19,331 | 196 | yes |

**What the data says**

- `Q75573` Anicius Auchenius Bassus has 4 parents: Q75634, Q75637, Q151955, Q154066.
- Wikidata contradicts `Q75603` → `Q75576`: Wikidata records no link between them
- Recorded births in this cycle: Sextus Claudius Petronius Pr 328; Quintus Clodius Hermogenianu 335; Anicius Auchenius Bassus 350

**Decision:** _not made — needs Emma_

---

## 3. Marcus Aemilius Lepidus — 15 records

Shortest loop: `Q72434 -> Q73893 -> Q73794 -> Q73692 -> Q73569 -> Q73443 -> Q73293 -> Q73128 -> Q72957 -> Q72801 -> Q72786 -> Q72615 -> Q72434`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q72434` | Marcus Aemilius Lepidus | Q435329 | 120 BC | 77 BC | **898** | 28,850 | 255 | yes |
| `Q72615` | Quintus Aemilius Lepidus | Q11944252 | — | — | **898** | 28,850 | 255 | yes |
| `Q72786` | Marcus Aemilius Lepidus | — | — | — | **898** | 28,850 | 255 | yes |
| `Q72801` | Cornelia | Q100804879 | — | — | **898** | 28,850 | 255 | yes |
| `Q72957` | Consul (138 BC) - Publius Cornelius Scipio Nas | — | 182 BC | 132 BC | **898** | 28,850 | 255 | yes |
| `Q73128` | Publius Cornelius Scipio Nasica Corculum | Q503320 | 205 | 141 | **898** | 28,850 | 255 | yes |
| `Q73131` | Cornelia Africana Major | Q5171151 | 201 | — | **898** | 28,850 | 255 | yes |
| `Q73293` | Publius Cornelius Scipio Nasica | Q453860 | 230 | 171 | **898** | 28,850 | 255 | yes |
| `Q73299` | Scipio Africanus | Q2253 | 235 | 183 | **898** | 28,850 | 255 | yes |
| `Q73443` | Gnaeus Cornelius Scipio Calvus | Q316475 | 256 | 211 | **898** | 28,850 | 255 | yes |
| `Q73446` | Publius Cornelius Scipio | Q3293507 | 255 | 211 | **898** | 28,850 | 255 | yes |
| `Q73569` | Lucius Cornelius Scipio | Q708483 | 306 | 250 | **898** | 28,850 | 255 | yes |
| `Q73692` | Lucius Cornelius Scipio Barbatus | Q374630 | 400 | 300 | **898** | 28,850 | 255 | yes |
| `Q73794` | Gnaeus Cornelius Scipio | Q128598522 | — | — | **898** | 28,850 | 255 | yes |
| `Q73893` | Lucius Cornelius Scipio Asiaticus Aemilianus | Q7234050 | 200 | 77 | **898** | 28,850 | 255 | yes |

**What the data says**

- Q72434, Q72786 share the label “Marcus Aemilius Lepidus”.
- `Q72615` Quintus Aemilius Lepidus has 3 parents: Q72786, Q72789, Q144279.
- `Q72786` Marcus Aemilius Lepidus has 6 parents: Q72789, Q72801, Q73011, Q73110, Q73113, Q73173.
- `Q72801` Cornelia has 3 parents: Q72957, Q73017, Q73428.
- Wikidata contradicts `Q73893` → `Q73794`: Wikidata records no link between them
- Recorded births in this cycle: Marcus Aemilius Lepidus 120 BC; Consul (138 BC) - Publius Co 182 BC; Publius Cornelius Scipio Nas 205; Cornelia Africana Major 201; Publius Cornelius Scipio Nas 230; Scipio Africanus 235; Gnaeus Cornelius Scipio Calv 256; Publius Cornelius Scipio 255; Lucius Cornelius Scipio 306; Lucius Cornelius Scipio Barb 400; Lucius Cornelius Scipio Asia 200

**Decision:** _not made — needs Emma_

---

## 4. Prachetas (10 sons) — 14 records

Shortest loop: `Q1955 -> Q153390 -> Q153381 -> Q1991 -> Q2035 -> Q153444 -> Q153438 -> Q2001 -> Q1989 -> Q1978 -> Q1968 -> Q1955`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q1955` | Prachetas (10 sons) | — | — | — | **561** | 5,999 | 156 | yes |
| `Q1968` | Prachinbarhi | — | — | — | **561** | 5,999 | 156 | yes |
| `Q1978` | Havirdhana | — | — | — | **561** | 5,999 | 156 | yes |
| `Q1989` | Vijitashva | — | — | — | **561** | 5,999 | 156 | yes |
| `Q1991` | Surya Sun God | — | — | — | **561** | 5,999 | 156 | yes |
| `Q2001` | Archis(Lakshmi's amsam) | — | — | — | **561** | 5,999 | 156 | yes |
| `Q2035` | Yama Dharma King of Death | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153381` | Aditi Kashyapa | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153390` | DAKSHA (reborn as DAKSHA) Prachetas | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153429` | PRITHU (Vishnu's amsam) Vena | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153438` | VENA Anga | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153444` | SUNITA Anga | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153460` | SANJNA \\ Saranyu Saranyu Saranyu/ | — | — | — | **561** | 5,999 | 156 | yes |
| `Q153465` | TVASTAR Kashyapa | — | — | — | **561** | 5,999 | 156 | yes |

**Decision:** _not made — needs Emma_

---

## 5. D. Ausindo Ximeno — 14 records

Shortest loop: `Q79388 -> Q79415 -> Q79435 -> Q79438 -> Q79424 -> Q79450 -> Q79480 -> Q79537 -> Q79618 -> Q99939 -> Q100154 -> Q100519 -> Q101113 -> Q113625 -> Q79388`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q79388` | D. Ausindo Ximeno | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79415` | D.Soeiro Ausendes | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79424` | Gil  Guille em Narbonne | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79435` | D.Arnaldo  Ximenes | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79438` | Sancho  ou Sancho Arnolfo Ximenes | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79450` | Soeiro  Afonso Tangil | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79480` | Fernao  dos de Tangil | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79537` | Estevao  Soares (D.) | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q79618` | Tereza  Eriz de Lugo | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q99939` | Ufa  Ufes | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q100154` | Godo  Arnaldes de Baiao | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q100519` | Soeiro  Guedes | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q101113` | D. Ausindo Soares | — | — | — | **4,914** | 3,663 | 218 | yes |
| `Q113625` | D.Teodoredo Ausendes Soares | — | 1078 | — | **4,914** | 3,663 | 218 | yes |

**Decision:** _not made — needs Emma_

---

## 6. Aditi Kashyapa — 14 records

Shortest loop: `Q160460 -> Q160580 -> Q160673 -> Q160640 -> Q160615 -> Q160596 -> Q160576 -> Q160560 -> Q160539 -> Q160512 -> Q160489 -> Q160460`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q160460` | Aditi Kashyapa | — | — | — | **58** | 6,406 | 10 | no |
| `Q160489` | DAKSHA Prachetas | — | — | — | **58** | 6,406 | 10 | no |
| `Q160512` | PRACHETAS (10 sons) | — | — | — | **58** | 6,406 | 10 | no |
| `Q160539` | PRACHINBARHI | — | — | — | **58** | 6,406 | 10 | no |
| `Q160560` | HAVIRDHANA | — | — | — | **58** | 6,406 | 10 | no |
| `Q160576` | Vijitashva | — | — | — | **58** | 6,406 | 10 | no |
| `Q160580` | SURYA Dev aka SUN GOD Kashyap | — | — | — | **58** | 6,406 | 10 | no |
| `Q160596` | PRITHU Vena | — | — | — | **58** | 6,406 | 10 | no |
| `Q160597` | ARCHIS | — | — | — | **58** | 6,406 | 10 | no |
| `Q160615` | VENA Anga | — | — | — | **58** | 6,406 | 10 | no |
| `Q160640` | SUNITA Anga | — | — | — | **58** | 6,406 | 10 | no |
| `Q160673` | YAMA Dharma | — | — | — | **58** | 6,406 | 10 | no |
| `Q160707` | SANJNA \\ Saranyu Saranyu | — | — | — | **58** | 6,406 | 10 | no |
| `Q160730` | TVASTAR Kashyapa | — | — | — | **58** | 6,406 | 10 | no |

**Decision:** _not made — needs Emma_

---

## 7. Meurig ab Ynyr Gwent — 11 records

Shortest loop: `Q136957 -> Q137384 -> Q137899 -> Q137320 -> Q137900 -> Q137878 -> Q137383 -> Q136957`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q136957` | Meurig ab Ynyr Gwent | Q110560357 | 1030 | — | **183** | 5,272 | 28 | no |
| `Q136958` | Elen ferch Ednyfed ab Iorwerth Hir ap Llywarch | Q110560366 | 1045 | — | **183** | 5,272 | 28 | no |
| `Q136996` | Iorwerth Hir ap Llywarch Gam of Maelor | Q110622211 | — | — | **183** | 5,272 | 28 | no |
| `Q137320` | Gwerstan ap Gwaithfoed ap Gloddieu ap Gwrhydur | Q110153008 | — | — | **183** | 5,272 | 28 | no |
| `Q137383` | Nest ferch Gwrgan ab Ithel ab Idwallon | Q110560364 | — | — | **183** | 5,272 | 28 | no |
| `Q137384` | Ynyr, lord of Gwent | Q110152975 | — | — | **183** | 5,272 | 28 | no |
| `Q137385` | Ednyfed ab Iorwerth Hir ap Llywarch Gam of Cri | Q110560367 | 1015 | — | **183** | 5,272 | 28 | no |
| `Q137449` | Lleuki\|Nest ferch Gwerstan ap Gwaithfoed | Q110582810 | — | — | **183** | 5,272 | 28 | no |
| `Q137878` | NN ferch Cynfyn ap Gwerystan ap Gwaithfoed | Q116052822 | — | — | **183** | 5,272 | 28 | no |
| `Q137899` | Morfudd ferch Ynir | Q110152973 | — | — | **183** | 5,272 | 28 | no |
| `Q137900` | Cynfyn ap Gwerstan | Q5199943 | 990 | 1023 | **183** | 5,272 | 28 | no |

**What the data says**

- Recorded births in this cycle: Meurig ab Ynyr Gwent 1030; Elen ferch Ednyfed ab Iorwer 1045; Ednyfed ab Iorwerth Hir ap L 1015; Cynfyn ap Gwerstan 990

**Decision:** _not made — needs Emma_

---

## 8. Shaodian — 10 records

Shortest loop: `Q6421 -> Q87856 -> Q87854 -> Q87852 -> Q87850 -> Q87848 -> Q87846 -> Q87844 -> Q87842 -> Q87840 -> Q6421`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q6421` | Shaodian | Q4302144 | 2697 BC | — | **273** | 7,656 | 149 | yes |
| `Q87840` | (unlabelled) | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87842` | (unlabelled) | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87844` | (unlabelled) | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87846` | (unlabelled) | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87848` | (unlabelled) | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87850` | Generation 5 | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87852` | Generation 4 | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87854` | Generation 3 | — | — | — | **273** | 7,656 | 149 | yes |
| `Q87856` | Generation 2 | — | — | — | **273** | 7,656 | 149 | yes |

**What the data says**

- `Q6421` Shaodian has 5 parents: Q6433, Q6435, Q51954, Q87840, Q87862.

**Decision:** _not made — needs Emma_

---

## 9. Gaius Servilius — 8 records

Shortest loop: `Q73170 -> Q73985 -> Q73910 -> Q73812 -> Q73710 -> Q73599 -> Q73479 -> Q73332 -> Q73170`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q73170` | Gaius Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73332` | Publius Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73479` | Quintus Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73599` | Gnaeus Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73710` | Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73812` | Gaius Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73910` | Gaius Servilius | — | — | — | **7** | 19,818 | 0 | no |
| `Q73985` | Quintus Servilius | — | — | — | **7** | 19,818 | 0 | no |

**What the data says**

- Q73170, Q73812, Q73910 share the label “Gaius Servilius”.
- Q73479, Q73985 share the label “Quintus Servilius”.

**Decision:** _not made — needs Emma_

---

## 10. Sekhemre Sankhtawy Neferhotep III — 7 records

Shortest loop: `Q85478 -> Q85578 -> Q85554 -> Q85528 -> Q85514 -> Q85498 -> Q85478`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q85478` | Sekhemre Sankhtawy Neferhotep III | — | — | — | **420** | 31,790 | 207 | yes |
| `Q85498` | Sekhemre Sementawi Djehuti | — | — | — | **420** | 31,790 | 207 | yes |
| `Q85500` | Mentuhotep . | — | — | — | **420** | 31,790 | 207 | yes |
| `Q85514` | Senebhenaf . | — | — | — | **420** | 31,790 | 207 | yes |
| `Q85528` | Yauyebi of  Egypt | — | 1790 BC | — | **420** | 31,790 | 207 | yes |
| `Q85554` | Sebekemsaf . | — | — | — | **420** | 31,790 | 207 | yes |
| `Q85578` | Sankhenre Mentuhotep VI | — | — | — | **420** | 31,790 | 207 | yes |

**Decision:** _not made — needs Emma_

---

## 11. Joan ferch Ieuan ap Rhys ap Llowdden — 7 records

Shortest loop: `Q138061 -> Q138810 -> Q140234 -> Q139067 -> Q140681 -> Q140643 -> Q139043 -> Q138061`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q138061` | Joan ferch Ieuan ap Rhys ap Llowdden | Q110413692 | — | — | **6,514** | 527 | 231 | yes |
| `Q138810` | Llywelyn Ddû ab Owain | Q99086883 | — | — | **6,514** | 527 | 231 | yes |
| `Q139043` | Ieuan ap Rhys | Q99071449 | — | — | **6,514** | 527 | 231 | yes |
| `Q139067` | Gruffudd Foethus ap Llywelyn | Q75905270 | — | — | **6,514** | 527 | 231 | yes |
| `Q140234` | Llywelyn Foethus ap Llywelyn Ddû ab Owain | Q99086873 | — | — | **6,514** | 527 | 231 | yes |
| `Q140643` | Rhys ap Llowdden y Gath | Q99302513 | — | — | **6,514** | 527 | 231 | yes |
| `Q140681` | Lleucu ferch Gruffudd | Q110413685 | — | — | **6,514** | 527 | 231 | yes |

**Decision:** _not made — needs Emma_

---

## 12. Venkatacharyar Jatavallabha (Jatavallabha award by Maha — 7 records

Shortest loop: `Q171493 -> Q171595 -> Q171604 -> Q171614 -> Q171622 -> Q171636 -> Q171648 -> Q171493`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q171493` | Venkatacharyar Jatavallabha (Jatavallabha awar | — | — | — | **52** | 40 | 33 | no |
| `Q171595` | Rangacharya Jatavallabha (Jatavallabha award b | — | — | — | **52** | 40 | 33 | no |
| `Q171604` | Venkatacharya Jatavallabha (Jatavallabha award | — | — | — | **52** | 40 | 33 | no |
| `Q171614` | Srinivasacharya Jatavallabha | — | — | — | **52** | 40 | 33 | no |
| `Q171622` | Srinivasacharyar Jatavallabha (Jatavallabha aw | — | — | — | **52** | 40 | 33 | no |
| `Q171636` | Venkatacharya Jatavallabha (Jatavallabha award | — | — | — | **52** | 40 | 33 | no |
| `Q171648` | Rangacharya Jatavallabha (Jatavallabha award b | — | — | — | **52** | 40 | 33 | no |

**What the data says**

- Q171595, Q171648 share the label “Rangacharya Jatavallabha (Jatavallabha award by Maha”.
- Q171604, Q171636 share the label “Venkatacharya Jatavallabha (Jatavallabha award by Maha”.

**Decision:** _not made — needs Emma_

---

## 13. Gepaepyris — 6 records

Shortest loop: `Q138363 -> Q138365 -> Q148022 -> Q144020 -> Q141360 -> Q139511 -> Q138363`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q138363` | Gepaepyris | Q2720247 | 50 | — | **1,068** | 63 | 264 | yes |
| `Q138365` | Tiberius Julius Cotys I | Q2711623 | — | — | **1,068** | 63 | 264 | yes |
| `Q139511` | Cotys III | Q2998641 | 1 | 19 | **1,068** | 63 | 264 | yes |
| `Q141360` | Rhoemetalces I | Q2713422 | 50 | 12 | **1,068** | 63 | 264 | yes |
| `Q144020` | Cotys II | Q15483438 | — | — | **1,068** | 63 | 264 | yes |
| `Q148022` | Rhescuporis I | Q2713411 | 100 | 60 | **1,068** | 63 | 264 | yes |

**What the data says**

- Recorded births in this cycle: Gepaepyris 50; Cotys III 1; Rhoemetalces I 50; Rhescuporis I 100

**Decision:** _not made — needs Emma_

---

## 14. Appius Claudius Caecus — 5 records

Shortest loop: `Q73782 -> Q78812 -> Q78752 -> Q73970 -> Q73887 -> Q73782`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q73782` | Appius Claudius Caecus | Q297783 | 341 BC | 300 BC | **15** | 28,992 | 5 | no |
| `Q73887` | Gaius Claudius Crassus Inrelligensis | Q5759141 | 370 | 337 | **15** | 28,992 | 5 | no |
| `Q73970` | Appius Claudius Crassus Inregillensis | Q657609 | 350 | 349 | **15** | 28,992 | 5 | no |
| `Q78752` | Publius  Claudius-Nero | — | — | — | **15** | 28,992 | 5 | no |
| `Q78812` | Tiberius Claudius Nero | — | — | — | **15** | 28,992 | 5 | no |

**What the data says**

- `Q73970` Appius Claudius Crassus Inregillensis has 3 parents: Q74091, Q78752, Q151743.
- Recorded births in this cycle: Appius Claudius Caecus 341 BC; Gaius Claudius Crassus Inrel 370; Appius Claudius Crassus Inre 350

**Decision:** _not made — needs Emma_

---

## 15. Deimachus — 5 records

Shortest loop: `Q75123 -> Q132251 -> Q132367 -> Q131896 -> Q131902 -> Q75123`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q75123` | Deimachus | Q1183226 | — | — | **192** | 31,659 | 16 | no |
| `Q131896` | Tyro | Q1126715 | — | — | **192** | 31,659 | 16 | no |
| `Q131902` | Neleus | Q637955 | — | — | **192** | 31,659 | 16 | no |
| `Q132251` | Enarete | Q48665 | — | — | **192** | 31,659 | 16 | no |
| `Q132367` | Salmoneus | Q1131643 | — | — | **192** | 31,659 | 16 | no |

**What the data says**

- `Q75123` Deimachus has 4 parents: Q75162, Q75165, Q131902, Q133062.
- Wikidata contradicts `Q131902` → `Q75123`: Wikidata records no link between them

**Decision:** _not made — needs Emma_

---

## 16. Arsende  de Cabrera — 5 records

Shortest loop: `Q104371 -> Q107162 -> Q123407 -> Q124325 -> Q124326 -> Q104371`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q104371` | Arsende  de Cabrera | — | — | — | **6,564** | 34 | 220 | yes |
| `Q107162` | Ermengol VII, Count of Urgell | Q949224 | — | — | **6,564** | 34 | 220 | yes |
| `Q123407` | Marquesa d'Urgell | Q21126997 | 1150 | 1209 | **6,564** | 34 | 220 | yes |
| `Q124325` | Guerau IV de Cabrera | Q4894186 | 1200 | 1228 | **6,564** | 34 | 220 | yes |
| `Q124326` | Guerau V de Cabrera | Q19291067 | — | 1242 | **6,564** | 34 | 220 | yes |

**What the data says**

- `Q107162` Ermengol VII, Count of Urgell has 3 parents: Q104371, Q107158, Q118293.
- `Q124326` Guerau V de Cabrera has 4 parents: Q101441, Q102567, Q119220, Q124325.
- Recorded births in this cycle: Marquesa d'Urgell 1150; Guerau IV de Cabrera 1200

**Decision:** _not made — needs Emma_

---

## 17. Pedaiah — 4 records

Shortest loop: `Q4617 -> Q4626 -> Q135406 -> Q135539 -> Q4617`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q4617` | Pedaiah | Q20101444 | — | — | **509** | 28,960 | 167 | yes |
| `Q4626` | Zebudah | Q30527376 | — | — | **509** | 28,960 | 167 | yes |
| `Q135406` | Jehoiakim | Q319034 | 634 | 598 | **509** | 28,960 | 167 | yes |
| `Q135539` | Jeconiah | Q319049 | 616 | 597 | **509** | 28,960 | 167 | yes |

**What the data says**

- `Q135539` Jeconiah has 3 parents: Q4618, Q60198, Q135406.
- Wikidata contradicts `Q135539` → `Q4617`: Wikidata records no link between them
- Recorded births in this cycle: Jehoiakim 634; Jeconiah 616

**Decision:** _not made — needs Emma_

---

## 18. Pepin of Landen — 4 records

Shortest loop: `Q111318 -> Q111320 -> Q135895 -> Q113081 -> Q111318`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q111318` | Pepin of Landen | Q313373 | — | — | **4,659** | 14,364 | 209 | yes |
| `Q111320` | Begga | Q266765 | — | — | **4,659** | 14,364 | 209 | yes |
| `Q113081` | Charles Martel | Q3301 | — | — | **4,659** | 14,364 | 209 | yes |
| `Q135895` | Pepin of Herstal | Q91392 | 645 | 714 | **4,659** | 14,364 | 209 | yes |

**What the data says**

- `Q111318` Pepin of Landen has 3 parents: Q112100, Q113081, Q154041.
- Wikidata contradicts `Q113081` → `Q111318`: Wikidata records no link between them

**Decision:** _not made — needs Emma_

---

## 19. Olaf Geirstad-Alf — 4 records

Shortest loop: `Q118732 -> Q136091 -> Q135856 -> Q123845 -> Q118732`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q118732` | Olaf Geirstad-Alf | Q2560871 | — | — | **4,424** | 7,993 | 218 | yes |
| `Q123845` | Alfhild | Q122890477 | — | — | **4,424** | 7,993 | 218 | yes |
| `Q135856` | Alfarin | Q5666589 | 750 | 791 | **4,424** | 7,993 | 218 | yes |
| `Q136091` | Gandalf Alfgeirsson | Q4133209 | 705 | 768 | **4,424** | 7,993 | 218 | yes |

**What the data says**

- Recorded births in this cycle: Alfarin 750; Gandalf Alfgeirsson 705

**Decision:** _not made — needs Emma_

---

## 20. Morfudd ferch Tudur Fongam ap Cynwrig Fychan ap Cynwrig — 4 records

Shortest loop: `Q144542 -> Q148522 -> Q146349 -> Q148521 -> Q144542`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q144542` | Morfudd ferch Tudur Fongam ap Cynwrig Fychan a | Q116147500 | — | — | **6,151** | 57 | 230 | yes |
| `Q146349` | Cynwrig Fychan ap Cynwrig | Q99071981 | — | — | **6,151** | 57 | 230 | yes |
| `Q148521` | Tudur Fongam ap Cynwrig Fychan ap Cynwrig ap L | Q116147501 | — | — | **6,151** | 57 | 230 | yes |
| `Q148522` | Dyddgu ferch Cadwgan Fottwm ab Ednyfed ap Cadw | Q110636576 | — | — | **6,151** | 57 | 230 | yes |

**Decision:** _not made — needs Emma_

---

## 21. Swammbhu Brambha — 4 records

Shortest loop: `Q160928 -> Q160981 -> Q160965 -> Q160946 -> Q160928`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q160928` | Swammbhu Brambha | — | — | — | **7** | 6,163 | 1 | no |
| `Q160946` | 11 Rudras | — | — | — | **7** | 6,163 | 1 | no |
| `Q160965` | Kasayap Muni | — | — | — | **7** | 6,163 | 1 | no |
| `Q160981` | Person Q160981 | — | — | — | **7** | 6,163 | 1 | no |

**What the data says**

- `Q160928` Swammbhu Brambha has 3 parents: Q160946, Q160947, Q160948.

**Decision:** _not made — needs Emma_

---

## 22. Maharaja Parameswara @ Raja Iskandar Shah Paduka Sri Ratna Vira Vikrama di-Raja — 4 records

Shortest loop: `Q161658 -> Q161777 -> Q161966 -> Q162275 -> Q161658`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q161658` | Maharaja Parameswara @ Raja Iskandar Shah Padu | — | — | — | **29** | 1,638 | 16 | no |
| `Q161777` | Dewa Amas Sang Aji Kala | — | — | — | **29** | 1,638 | 16 | no |
| `Q161966` | Demang Lebar Daun Mangkabumi (Bendahara I) | — | — | — | **29** | 1,638 | 16 | no |
| `Q162275` | Wan Sendari (Radin Ratna Cenderapuri) | — | — | — | **29** | 1,638 | 16 | no |

**What the data says**

- `Q161658` Maharaja Parameswara @ Raja Iskandar Shah Paduka Sri Ratna Vira Vikrama di-Raja has 3 parents: Q160051, Q162275, Q171395.

**Decision:** _not made — needs Emma_

---

## 23. Marcus Livius Drusus — 3 records

Shortest loop: `Q72798 -> Q73119 -> Q72951 -> Q72798`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q72798` | Marcus Livius Drusus | Q703346 | 155 | 109 | **920** | 28,779 | 267 | yes |
| `Q72951` | Gaius Livius Drusus | Q1270114 | 250 | 250 | **920** | 28,779 | 267 | yes |
| `Q73119` | Marcus Livius Drusus | Q433463 | 124 | 91 | **920** | 28,779 | 267 | yes |

**What the data says**

- Q72798, Q73119 share the label “Marcus Livius Drusus”.
- `Q72798` Marcus Livius Drusus has 3 parents: Q72951, Q72954, Q73431.
- `Q73119` Marcus Livius Drusus has 7 parents: Q72798, Q72801, Q73173, Q78450, Q78453, Q78746, Q151476.
- Wikidata contradicts `Q73119` → `Q72951`: Wikidata records no link between them
- Recorded births in this cycle: Marcus Livius Drusus 155; Gaius Livius Drusus 250; Marcus Livius Drusus 124

**Decision:** _not made — needs Emma_

---

## 24. Lucius Junius  Brutus — 3 records

Shortest loop: `Q73383 -> Q73644 -> Q73518 -> Q73383`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q73383` | Lucius Junius  Brutus | — | — | — | **805** | 28,751 | 246 | yes |
| `Q73518` | C. Junius Junius Brutus  Brutus | — | — | — | **805** | 28,751 | 246 | yes |
| `Q73644` | C. Junius  Brutus | — | — | — | **805** | 28,751 | 246 | yes |

**Decision:** _not made — needs Emma_

---

## 25. Sergius Octavius Pontianus Laenes Octavius  Pontainus — 3 records

Shortest loop: `Q76693 -> Q77155 -> Q76933 -> Q76693`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q76693` | Sergius Octavius Pontianus Laenes Octavius  Po | — | — | — | **3,191** | 19,380 | 214 | yes |
| `Q76933` | Sergius Octavius Pontainus | — | — | — | **3,191** | 19,380 | 214 | yes |
| `Q77155` | Sergius Ovtavius Laenes | — | — | — | **3,191** | 19,380 | 214 | yes |

**What the data says**

- `Q76693` Sergius Octavius Pontianus Laenes Octavius  Pontainus has 5 parents: Q76930, Q76933, Q76936, Q76939, Q76945.

**Decision:** _not made — needs Emma_

---

## 26. Marcus Flaccus — 2 records

Shortest loop: `Q73530 -> Q73653 -> Q73530`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q73530` | Marcus Flaccus | — | — | — | **5** | 28,706 | 3 | no |
| `Q73653` | Cassus Curvus | — | — | — | **5** | 28,706 | 3 | no |

**Decision:** _not made — needs Emma_

---

## 27. Esther  bat Sahlan ben Abraham — 2 records

Shortest loop: `Q88454 -> Q90982 -> Q88454`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q88454` | Esther  bat Sahlan ben Abraham | — | — | — | **3,499** | 2 | 215 | yes |
| `Q90982` | Esther  bat Yosef ben 'Amram haDayyan al-Sijil | — | — | — | **3,499** | 2 | 215 | yes |

**Decision:** _not made — needs Emma_

---

