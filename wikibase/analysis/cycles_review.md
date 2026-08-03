# Ancestry cycles — every one, with the numbers that decide them

**13 cycles, 101 records caught in one.** Generated from the dump by `wiki-scripts/build_cycles_notion.py`; the source of truth is `wikibase/analysis/cycles_review.md` in the repo and this page is a copy of it.

A cycle here means a **strongly connected component** — a set of records where everyone is reachable from everyone else by following parent links, so at least one person is their own ancestor. That is always an error. Which *edge* is the wrong one usually is not obvious, and this document does not decide it.

## How to read the ancestor column

**`ancestors` is the only column that ranks anything.** It counts the distinct records reachable upward from that person. Cutting an edge that collapses this number is severing a gateway — the thing `cycle_policy.md` says never to do. `descendants` is there as context and deliberately ranks nothing; `qa_cycles_load.tsv` ranks by descendants lost and is wrong to.

`depth` is the longest chain upward, computed over the cycle-condensed graph so it stays well defined. `→Aster` marks whether `Q1` Aster is reachable upward.

Within a cycle every member usually shows the *same* ancestor count, because they can all reach each other and therefore reach the same set. That is the cycle itself showing up in the data.

---

## 1. Marcus Aemilius Lepidus — 15 records

Shortest loop: `Q72434 -> Q73893 -> Q73794 -> Q73692 -> Q73569 -> Q73443 -> Q73293 -> Q73128 -> Q72957 -> Q72801 -> Q72786 -> Q72615 -> Q72434`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q72434` | Marcus Aemilius Lepidus | Q435329 | 120 BC | 77 BC | **896** | 28,732 | 255 | yes |
| `Q72615` | Quintus Aemilius Lepidus | Q11944252 | — | — | **896** | 28,732 | 255 | yes |
| `Q72786` | Marcus Aemilius Lepidus | — | — | — | **896** | 28,732 | 255 | yes |
| `Q72801` | Cornelia | Q100804879 | — | — | **896** | 28,732 | 255 | yes |
| `Q72957` | Consul (138 BC) - Publius Cornelius Scipio Nas | — | 182 BC | 132 BC | **896** | 28,732 | 255 | yes |
| `Q73128` | Publius Cornelius Scipio Nasica Corculum | Q503320 | 205 | 141 | **896** | 28,732 | 255 | yes |
| `Q73131` | Cornelia Africana Major | Q5171151 | 201 | — | **896** | 28,732 | 255 | yes |
| `Q73293` | Publius Cornelius Scipio Nasica | Q453860 | 230 | 171 | **896** | 28,732 | 255 | yes |
| `Q73299` | Scipio Africanus | Q2253 | 235 | 183 | **896** | 28,732 | 255 | yes |
| `Q73443` | Gnaeus Cornelius Scipio Calvus | Q316475 | 256 | 211 | **896** | 28,732 | 255 | yes |
| `Q73446` | Publius Cornelius Scipio | Q3293507 | 255 | 211 | **896** | 28,732 | 255 | yes |
| `Q73569` | Lucius Cornelius Scipio | Q708483 | 306 | 250 | **896** | 28,732 | 255 | yes |
| `Q73692` | Lucius Cornelius Scipio Barbatus | Q374630 | 400 | 300 | **896** | 28,732 | 255 | yes |
| `Q73794` | Gnaeus Cornelius Scipio | Q128598522 | — | — | **896** | 28,732 | 255 | yes |
| `Q73893` | Lucius Cornelius Scipio Asiaticus Aemilianus | Q7234050 | 200 | 77 | **896** | 28,732 | 255 | yes |

**What the data says**

- Q72434, Q72786 share the label “Marcus Aemilius Lepidus”.
- `Q72615` Quintus Aemilius Lepidus has 3 parents: Q72786, Q72789, Q144279.
- `Q72786` Marcus Aemilius Lepidus has 6 parents: Q72789, Q72801, Q73011, Q73110, Q73113, Q73173.
- `Q72801` Cornelia has 3 parents: Q72957, Q73017, Q73428.
- Wikidata contradicts `Q73893` → `Q73794`: Wikidata records no link between them
- Recorded births in this cycle: Marcus Aemilius Lepidus 120 BC; Consul (138 BC) - Publius Co 182 BC; Publius Cornelius Scipio Nas 205; Cornelia Africana Major 201; Publius Cornelius Scipio Nas 230; Scipio Africanus 235; Gnaeus Cornelius Scipio Calv 256; Publius Cornelius Scipio 255; Lucius Cornelius Scipio 306; Lucius Cornelius Scipio Barb 400; Lucius Cornelius Scipio Asia 200

**Decision:** _not made — needs Emma_

---

## 2. Prachetas (10 sons) — 14 records

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

## 3. D. Ausindo Ximeno — 14 records

Shortest loop: `Q79388 -> Q79415 -> Q79435 -> Q79438 -> Q79424 -> Q79450 -> Q79480 -> Q79537 -> Q79618 -> Q99939 -> Q100154 -> Q100519 -> Q101113 -> Q113625 -> Q79388`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q79388` | D. Ausindo Ximeno | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79415` | D.Soeiro Ausendes | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79424` | Gil  Guille em Narbonne | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79435` | D.Arnaldo  Ximenes | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79438` | Sancho  ou Sancho Arnolfo Ximenes | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79450` | Soeiro  Afonso Tangil | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79480` | Fernao  dos de Tangil | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79537` | Estevao  Soares (D.) | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q79618` | Tereza  Eriz de Lugo | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q99939` | Ufa  Ufes | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q100154` | Godo  Arnaldes de Baiao | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q100519` | Soeiro  Guedes | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q101113` | D. Ausindo Soares | — | — | — | **4,903** | 3,658 | 218 | yes |
| `Q113625` | D.Teodoredo Ausendes Soares | — | 1078 | — | **4,903** | 3,658 | 218 | yes |

**Decision:** _not made — needs Emma_

---

## 4. Aditi Kashyapa — 14 records

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

## 5. Gaius Servilius — 8 records

Shortest loop: `Q73170 -> Q73985 -> Q73910 -> Q73812 -> Q73710 -> Q73599 -> Q73479 -> Q73332 -> Q73170`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q73170` | Gaius Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73332` | Publius Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73479` | Quintus Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73599` | Gnaeus Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73710` | Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73812` | Gaius Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73910` | Gaius Servilius | — | — | — | **7** | 19,567 | 0 | no |
| `Q73985` | Quintus Servilius | — | — | — | **7** | 19,567 | 0 | no |

**What the data says**

- Q73170, Q73812, Q73910 share the label “Gaius Servilius”.
- Q73479, Q73985 share the label “Quintus Servilius”.

**Decision:** _not made — needs Emma_

---

## 6. Joan ferch Ieuan ap Rhys ap Llowdden — 7 records

Shortest loop: `Q138061 -> Q138810 -> Q140234 -> Q139067 -> Q140681 -> Q140643 -> Q139043 -> Q138061`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q138061` | Joan ferch Ieuan ap Rhys ap Llowdden | Q110413692 | — | — | **6,495** | 527 | 231 | yes |
| `Q138810` | Llywelyn Ddû ab Owain | Q99086883 | — | — | **6,495** | 527 | 231 | yes |
| `Q139043` | Ieuan ap Rhys | Q99071449 | — | — | **6,495** | 527 | 231 | yes |
| `Q139067` | Gruffudd Foethus ap Llywelyn | Q75905270 | — | — | **6,495** | 527 | 231 | yes |
| `Q140234` | Llywelyn Foethus ap Llywelyn Ddû ab Owain | Q99086873 | — | — | **6,495** | 527 | 231 | yes |
| `Q140643` | Rhys ap Llowdden y Gath | Q99302513 | — | — | **6,495** | 527 | 231 | yes |
| `Q140681` | Lleucu ferch Gruffudd | Q110413685 | — | — | **6,495** | 527 | 231 | yes |

**Decision:** _not made — needs Emma_

---

## 7. Sekhemre Sankhtawy Neferhotep III — 6 records

Shortest loop: `Q85478 -> Q85578 -> Q85554 -> Q85528 -> Q85514 -> Q85500 -> Q85478`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q85478` | Sekhemre Sankhtawy Neferhotep III | — | — | — | **420** | 31,518 | 207 | yes |
| `Q85500` | Mentuhotep . | — | — | — | **420** | 31,518 | 207 | yes |
| `Q85514` | Senebhenaf . | — | — | — | **420** | 31,518 | 207 | yes |
| `Q85528` | Yauyebi of  Egypt | — | 1790 BC | — | **420** | 31,518 | 207 | yes |
| `Q85554` | Sebekemsaf . | — | — | — | **420** | 31,518 | 207 | yes |
| `Q85578` | Sankhenre Mentuhotep VI | — | — | — | **420** | 31,518 | 207 | yes |

**Decision:** _not made — needs Emma_

---

## 8. Gepaepyris — 6 records

Shortest loop: `Q138363 -> Q138365 -> Q148022 -> Q144020 -> Q141360 -> Q139511 -> Q138363`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q138363` | Gepaepyris | Q2720247 | 50 | — | **1,066** | 63 | 264 | yes |
| `Q138365` | Tiberius Julius Cotys I | Q2711623 | — | — | **1,066** | 63 | 264 | yes |
| `Q139511` | Cotys III | Q2998641 | 1 | 19 | **1,066** | 63 | 264 | yes |
| `Q141360` | Rhoemetalces I | Q2713422 | 50 | 12 | **1,066** | 63 | 264 | yes |
| `Q144020` | Cotys II | Q15483438 | — | — | **1,066** | 63 | 264 | yes |
| `Q148022` | Rhescuporis I | Q2713411 | 100 | 60 | **1,066** | 63 | 264 | yes |

**What the data says**

- Recorded births in this cycle: Gepaepyris 50; Cotys III 1; Rhoemetalces I 50; Rhescuporis I 100

**Decision:** _not made — needs Emma_

---

## 9. Pepin of Landen — 4 records

Shortest loop: `Q111318 -> Q111320 -> Q135895 -> Q113081 -> Q111318`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q111318` | Pepin of Landen | Q313373 | — | — | **4,647** | 14,363 | 209 | yes |
| `Q111320` | Begga | Q266765 | — | — | **4,647** | 14,363 | 209 | yes |
| `Q113081` | Charles Martel | Q3301 | — | — | **4,647** | 14,363 | 209 | yes |
| `Q135895` | Pepin of Herstal | Q91392 | 645 | 714 | **4,647** | 14,363 | 209 | yes |

**What the data says**

- `Q111318` Pepin of Landen has 3 parents: Q112100, Q113081, Q154041.
- Wikidata contradicts `Q113081` → `Q111318`: Wikidata records no link between them

**Decision:** _not made — needs Emma_

---

## 10. Olaf Geirstad-Alf — 4 records

Shortest loop: `Q118732 -> Q136091 -> Q135856 -> Q123845 -> Q118732`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q118732` | Olaf Geirstad-Alf | Q2560871 | — | — | **3,788** | 7,987 | 218 | yes |
| `Q123845` | Alfhild | Q122890477 | — | — | **3,788** | 7,987 | 218 | yes |
| `Q135856` | Alfarin | Q5666589 | 750 | 791 | **3,788** | 7,987 | 218 | yes |
| `Q136091` | Gandalf Alfgeirsson | Q4133209 | 705 | 768 | **3,788** | 7,987 | 218 | yes |

**What the data says**

- Recorded births in this cycle: Alfarin 750; Gandalf Alfgeirsson 705

**Decision:** _not made — needs Emma_

---

## 11. Morfudd ferch Tudur Fongam ap Cynwrig Fychan ap Cynwrig — 4 records

Shortest loop: `Q144542 -> Q148522 -> Q146349 -> Q148521 -> Q144542`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q144542` | Morfudd ferch Tudur Fongam ap Cynwrig Fychan a | Q116147500 | — | — | **6,185** | 57 | 230 | yes |
| `Q146349` | Cynwrig Fychan ap Cynwrig | Q99071981 | — | — | **6,185** | 57 | 230 | yes |
| `Q148521` | Tudur Fongam ap Cynwrig Fychan ap Cynwrig ap L | Q116147501 | — | — | **6,185** | 57 | 230 | yes |
| `Q148522` | Dyddgu ferch Cadwgan Fottwm ab Ednyfed ap Cadw | Q110636576 | — | — | **6,185** | 57 | 230 | yes |

**Decision:** _not made — needs Emma_

---

## 12. Marcus Livius Drusus — 3 records

Shortest loop: `Q72798 -> Q73119 -> Q72951 -> Q72798`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q72798` | Marcus Livius Drusus | Q703346 | 155 | 109 | **918** | 28,656 | 267 | yes |
| `Q72951` | Gaius Livius Drusus | Q1270114 | 250 | 250 | **918** | 28,656 | 267 | yes |
| `Q73119` | Marcus Livius Drusus | Q433463 | 124 | 91 | **918** | 28,656 | 267 | yes |

**What the data says**

- Q72798, Q73119 share the label “Marcus Livius Drusus”.
- `Q72798` Marcus Livius Drusus has 3 parents: Q72951, Q72954, Q73431.
- `Q73119` Marcus Livius Drusus has 7 parents: Q72798, Q72801, Q73173, Q78450, Q78453, Q78746, Q151476.
- Wikidata contradicts `Q73119` → `Q72951`: Wikidata records no link between them
- Recorded births in this cycle: Marcus Livius Drusus 155; Gaius Livius Drusus 250; Marcus Livius Drusus 124

**Decision:** _not made — needs Emma_

---

## 13. Esther  bat Sahlan ben Abraham — 2 records

Shortest loop: `Q88454 -> Q90982 -> Q88454`

| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |
|---|---|---|---:|---:|---:|---:|---:|:---:|
| `Q88454` | Esther  bat Sahlan ben Abraham | — | — | — | **3,483** | 2 | 215 | yes |
| `Q90982` | Esther  bat Yosef ben 'Amram haDayyan al-Sijil | — | — | — | **3,483** | 2 | 215 | yes |

**Decision:** _not made — needs Emma_

---

