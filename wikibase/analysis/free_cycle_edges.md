# The 169 loop edges that cost no record its route to Aster

Generated 2026-08-01 from `edges.tsv`, with that day's Acha cut applied in memory.
**29 tangles, 271 records, 298 internal edges; 169 of them can be removed without any**
**record losing its route to `Q1` Aster.**

**READ THIS FIRST — a free edge is not a correct edge.** The column measures graph cost,
not truth. In the Pepin of Landen tangle the two edges that come out free are *Begga →
Pepin of Herstal* and *Pepin of Herstal → Charles Martel*, which are the real Carolingian
descent; the false edge there is the expensive one. This file says which cuts are cheap,
never which are right.

- **`ancestors lost`** — records the CHILD can no longer reach upward after the cut.
- **`stranded`** — how many of those would be left with **no descendant at all**. Those
  are the ones worth reconnecting rather than dropping.
- **`topmost of the lost branch`** — the highest records in the lost group, i.e. those
  whose own parents are not also lost. Names the branch without listing every member.

Full machine-readable version, including every lost qid where the group is under 400:
`wikibase/analysis/free_cycle_edges.tsv`.

## What this answers

**Almost nothing gets orphaned.** A record the child stops reaching is usually still
reachable from somewhere else — it keeps other descendants and stays in the tree. Across
all 169 free cuts only **52 distinct records** would end up with no descendant at all, and
**each of those is stranded by exactly one specific cut**, never by several. So this is a
per-cut consideration, not a systemic risk, and the `stranded` column is where to look.

The 52, by tangle, with the ones most worth a second thought first:

- **T1 (71 records)** — `Q65489` **Hadrian**, `Q141756` Annia Rupilia Faustina, `Q64388`
  Annia Cornificia Faustina, `Q64355` Gaius Ummidius Quadratus, `Q62255` Aurelia
  Pompeiana, `Q62680` Mariana Minor, `Q70337` Cornelia Pompeia Magna, `Q70340` Lucius
  Scribonius Libo, `Q70343` Marcus Licinius Crassus Dives, `Q70346` Fausta Cornelia,
  `Q70718` Gaius Rubellius Blandus, `Q73083` Publius Licinius Crassus Dives (cos. 97),
  `Q77386` Julia Livia, `Q99408` Publius Licinius Varus Crassus
- **T2** — `Q75558` Clodia Celsina, `Q75634` Caeionia Auchenia Bassa
- **T3** — `Q72786` **Marcus Aemilius Lepidus** (the record queue item 1 is already about)
- **T5** — `Q153429` PRITHU (Vishnu's amsam), `Q153444` SUNITA Anga, `Q2001` Archis
- **T6** — `Q160512` PRACHETAS (10 sons), `Q160539` PRACHINBARHI, `Q160640` SUNITA Anga
- **T7** — `Q73458` Gaius Caecilius, `Q138403` Clodia, `Q139560` Licinia, `Q148066` Marcus
  Caecilius Metellus
- **T8** — `Q136996` Iorwerth Hir, `Q137383` Nest ferch Gwrgan, `Q137384` Ynyr lord of
  Gwent, `Q137385` Ednyfed ab Iorwerth Hir, `Q137878` NN ferch Cynfyn
- **T9** — `Q87840` (unlabelled)  ·  **T10** — six Servilii: `Q73332`, `Q73479`, `Q73599`,
  `Q73710`, `Q73812`, `Q73985`
- **T11** — `Q138061` Joan ferch Ieuan  ·  **T12** — `Q85498` Sekhemre Sementawi Djehuti
- **T15** — `Q123407` Marquesa d'Urgell  ·  **T16** — `Q132367` **Salmoneus**
- **T17** — `Q78752` Publius Claudius-Nero, `Q78812` Tiberius Claudius Nero
- **T18** — `Q148521` Tudur Fongam  ·  **T19** — `Q123845` **Alfhild**
- **T21** — `Q78264` Lucius Pinarius  ·  **T24** — `Q160981`  ·  **T25** — `Q76933` Sergius
  Octavius Pontainus  ·  **T26** — `Q73518` C. Junius Brutus  ·  **T29** — `Q73653` Cassus
  Curvus

**Twelve cuts cost nobody a single ancestor** — the loop is pure redundancy there and the
edge carries nothing:

| tangle | edge |
|---|---|
| T1 | `Q64549` Marcus Annius Verus → `Q63780` Marcus Aurelius |
| T1 | `Q64549` Marcus Annius Verus → `Q65225` Annia Cornificia Faustina |
| T1 | `Q64582` Domitia Lucilla Minor → `Q63780` Marcus Aurelius |
| T1 | `Q64582` Domitia Lucilla Minor → `Q65225` Annia Cornificia Faustina |
| T1 | `Q72657` Publius Licinius Crassus Dives → `Q72933` Marcus Licinius Crassus |
| T1 | `Q72972` Publius Licinius Crassus Dives → `Q73260` Crassus Agelastus |
| T1 | `Q72981` Publius Licinius Crassus → `Q73260` Crassus Agelastus |
| T1 | `Q73665` Publius Licinius Crassus → `Q72972` Publius Licinius Crassus Dives |
| T2 | `Q65002` Sextus Claudius Petronius Probus → `Q75516` Anicius Hermogenianus Olybrius |
| T7 | `Q72984` Quintus Caecilius Metellus → `Q72834` Lucius Caecilius Metellus Calvus |
| T12 | `Q85500` Mentuhotep → `Q85478` Sekhemre Sankhtawy Neferhotep III |
| T12 | `Q85500` Mentuhotep → `Q85578` Sankhenre Mentuhotep VI |

**Every one of the 29 tangles has at least one free edge.** That is a statement about graph
structure only. In tangles 19, 20 and 27 the free edge is the *correct* one — Alfhild →
Olaf, Pepin of Herstal → Charles Martel, the Elder Drusus → the Younger — so those three
still have no usable cheap repair, which is the inversion class in `queue.md` item 2.

---

## Tangle 1 — Flavia Julia Constantia (71 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q72239` Vipsania Agrippina → `Q77611` Drusus Julius Caesar | 2225 | 0 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q114949` father of Basiliscus; `Q115348` Nitzevet … +542 more |
| `Q141756` Annia Rupilia Faustina → `Q65192` Gaius Annianus Verus | 2162 | 1 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q114949` father of Basiliscus; `Q115348` Nitzevet … +529 more |
| `Q65489` Hadrian → `Q64516` Antoninus Pius | 2103 | 1 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q115348` Nitzevet; `Q115372` Maacah … +516 more |
| `Q70152` Rubellia Bassa → `Q68488` Octavia | 1968 | 0 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q115348` Nitzevet; `Q115372` Maacah … +468 more |
| `Q70152` Rubellia Bassa → `Q69972` Octavia Sergia Plotilla | 1966 | 0 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q115348` Nitzevet; `Q115372` Maacah … +468 more |
| `Q77611` Drusus Julius Caesar → `Q138467` Julia Livia | 1963 | 0 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q115348` Nitzevet; `Q115372` Maacah … +471 more |
| `Q77611` Drusus Julius Caesar → `Q77386` Julia Livia | 1963 | 0 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q115348` Nitzevet; `Q115372` Maacah … +471 more |
| `Q62255` Aurelia Pompeiana → `Q61957` Claudia Crispina | 452 | 1 | `Q136810` Diocletian; `Q141492` Lepidus; `Q141604` Livia; `Q144099` Manlia Torquata … +124 more |
| `Q62704` Lucius Aurellius Commodus Pomp → `Q62255` Aurelia Pompeiana | 117 | 0 | `Q141492` Lepidus; `Q141604` Livia; `Q144075` Junia Prima; `Q144242` Sergia Plautilla … +34 more |
| `Q63747` Faustina the Younger → `Q63192` Lucilla | 112 | 0 | `Q141492` Lepidus; `Q141604` Livia; `Q144075` Junia Prima; `Q144242` Sergia Plautilla … +32 more |
| `Q64516` Antoninus Pius → `Q63747` Faustina the Younger | 110 | 0 | `Q141492` Lepidus; `Q141604` Livia; `Q144075` Junia Prima; `Q144242` Sergia Plautilla … +31 more |
| `Q62680` Mariana Minor → `Q62255` Aurelia Pompeiana | 73 | 1 | `Q141756` Annia Rupilia Faustina; `Q144099` Manlia Torquata; `Q151387` Marcus Domitius Calvinus; `Q151389` Salonius … +18 more |
| `Q64355` Gaius Ummidius Quadratus Annia → `Q63684` Ummidia Commificia Antonia | 60 | 1 | `Q141756` Annia Rupilia Faustina; `Q144099` Manlia Torquata; `Q151387` Marcus Domitius Calvinus; `Q151389` Salonius … +13 more |
| `Q65192` Gaius Annianus Verus → `Q64355` Gaius Ummidius Quadratus Annia | 58 | 0 | `Q141756` Annia Rupilia Faustina; `Q144099` Manlia Torquata; `Q151387` Marcus Domitius Calvinus; `Q151389` Salonius … +12 more |
| `Q69296` Marcus Licinius Crassus Frugi → `Q67573` Marcus Licinius Crassus Frugi | 38 | 0 | `Q148208` Lucius Calpurnius Piso; `Q71053` NN (Wife of Marcus Pupius Piso Frugi); `Q71098` Junia Albina; `Q72466` Marcus Licinius Crassus … +13 more |
| `Q70346` Fausta  Cornelia → `Q69296` Marcus Licinius Crassus Frugi | 22 | 1 | `Q71098` Junia Albina; `Q72660` Lucius Caecilius Metellus Dalmaticus; `Q72663` N.N., Wife of Lucius Caecilius Metellu; `Q72669` NN (Wife of Lucius Cornelius Sulla) … +7 more |
| `Q70343` Marcus Licinius Crassus Dives → `Q69296` Marcus Licinius Crassus Frugi | 15 | 1 | `Q148208` Lucius Calpurnius Piso; `Q71053` NN (Wife of Marcus Pupius Piso Frugi); `Q72466` Marcus Licinius Crassus; `Q72469` Marcus Pupius  Pupius … +2 more |
| `Q69263` Scribonia Magna → `Q67573` Marcus Licinius Crassus Frugi | 12 | 0 | `Q70988` Lucius Scribonius Libo Drusus; `Q71002` Sulpicia; `Q72630` Lucius Cornelius Cinna |
| `Q70718` Gaius Rubellius Blandus → `Q70152` Rubellia Bassa | 8 | 1 | `Q138467` Julia Livia; `Q141584` Sergia; `Q71655` NN (Wife of Rubellius Blandus); `Q72341` NN (Wife of Rubellius Blandus) |
| `Q73083` Publius Licinius Crassus Dives → `Q72933` Marcus Licinius Crassus | 7 | 1 | `Q73263` NN (Wife of Marcus Licinius Crassus Ag; `Q73407` NN (Wife of Publius Licinius Crassus); `Q73545` Consul (205 BC) - Publius Licinius Cra; `Q73548` NN (Wife of Publius Licinius Crassus D |
| `Q70340` Lucius Scribonius Libo → `Q69263` Scribonia Magna | 6 | 1 | `Q138489` Lucius Cornelius Cinna; `Q70988` Lucius Scribonius Libo Drusus; `Q71002` Sulpicia |
| `Q72807` Publius Mucius Scaevola → `Q72633` Publius Mucius Scaevola | 5 | 0 | `Q72966` Lincinia  Varus; `Q73305` Publius |
| `Q70337` Cornelia Pompeia Magna → `Q69263` Scribonia Magna | 2 | 1 | `Q70967` Lucius Cornelius Cinna |
| `Q63780` Marcus Aurelius → `Q63192` Lucilla | 1 | 0 | `Q63780` Marcus Aurelius |
| `Q64388` Annia Cornificia Faustina → `Q63684` Ummidia Commificia Antonia | 1 | 1 | `Q64388` Annia Cornificia Faustina |
| `Q64483` Faustina the Elder → `Q63747` Faustina the Younger | 1 | 0 | `Q64483` Faustina the Elder |
| `Q65225` Annia Cornificia Faustina → `Q64355` Gaius Ummidius Quadratus Annia | 1 | 0 | `Q65225` Annia Cornificia Faustina |
| `Q72810` Licinia → `Q72633` Publius Mucius Scaevola | 1 | 0 | `Q72810` Licinia |
| `Q77386` Julia Livia → `Q70152` Rubellia Bassa | 1 | 1 | `Q77386` Julia Livia |
| `Q99408` Publius Licinius Varus Liciniu → `Q72972` Publius Licinius Crassus Dives | 1 | 1 | `Q99408` Publius Licinius Varus Licinius Crassu |
| `Q64549` Marcus Annius Verus → `Q63780` Marcus Aurelius | 0 | 0 | — |
| `Q64549` Marcus Annius Verus → `Q65225` Annia Cornificia Faustina | 0 | 0 | — |
| `Q64582` Domitia Lucilla Minor → `Q63780` Marcus Aurelius | 0 | 0 | — |
| `Q64582` Domitia Lucilla Minor → `Q65225` Annia Cornificia Faustina | 0 | 0 | — |
| `Q72657` Publius Licinius Crassus Dives → `Q72933` Marcus Licinius Crassus | 0 | 0 | — |
| `Q72972` Publius Licinius Crassus Dives → `Q73260` Marcus Licinius Crassus Agelas | 0 | 0 | — |
| `Q72981` Publius Licinius Crassus → `Q73260` Marcus Licinius Crassus Agelas | 0 | 0 | — |
| `Q73665` Publius Licinius  Crassus → `Q72972` Publius Licinius Crassus Dives | 0 | 0 | — |

## Tangle 2 — Petronia (18 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q75603` Demetrias → `Q75558` Clodia Celsina | 2729 | 0 | `Q113011` Anicia Juliana; `Q114949` father of Basiliscus; `Q115348` Nitzevet; `Q115372` Maacah … +709 more |
| `Q75603` Demetrias → `Q75576` Clodius Celsinus Adelphius | 2729 | 0 | `Q113011` Anicia Juliana; `Q114949` father of Basiliscus; `Q115348` Nitzevet; `Q115372` Maacah … +709 more |
| `Q75721` Rufia Procula → `Q75781` Caeionius  Proculus | 988 | 0 | `Q113011` Anicia Juliana; `Q136454` Attalus; `Q136455` Boa; `Q137242` Julius Julianus … +295 more |
| `Q75576` Clodius Celsinus Adelphius → `Q75540` Quintus Clodius Hermogenianus  | 713 | 0 | `Q113011` Anicia Juliana; `Q136454` Attalus; `Q136455` Boa; `Q137242` Julius Julianus … +220 more |
| `Q75558` Clodia Celsina → `Q65002` Sextus Claudius Petronius Prob | 709 | 1 | `Q113011` Anicia Juliana; `Q136454` Attalus; `Q136455` Boa; `Q137242` Julius Julianus … +220 more |
| `Q75522` Anicia Faltonia Proba → `Q75516` Anicius Hermogenianus Olybrius | 675 | 0 | `Q136454` Attalus; `Q136455` Boa; `Q137242` Julius Julianus; `Q137708` Julia Major … +210 more |
| `Q75543` Tyrrania Anicia Juliana → `Q75522` Anicia Faltonia Proba | 671 | 0 | `Q136454` Attalus; `Q136455` Boa; `Q137242` Julius Julianus; `Q137708` Julia Major … +208 more |
| `Q75634` Caeionia Auchenia Bassa → `Q75573` Anicius Auchenius Bassus | 394 | 1 | `Q113011` Anicia Juliana; `Q141789` Gaius Avidius Nigrinus; `Q141791` Quintus Servilius Pudens; `Q144418` Lucius Ceionius Commodus … +118 more |
| `Q75540` Quintus Clodius Hermogenianus  → `Q75522` Anicia Faltonia Proba | 3 | 0 | `Q75576` Clodius Celsinus Adelphius; `Q75579` Faltonia Betitia Proba |
| `Q65002` Sextus Claudius Petronius Prob → `Q75516` Anicius Hermogenianus Olybrius | 0 | 0 | — |

## Tangle 3 — Marcus Aemilius Lepidus (15 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q72786` Marcus Aemilius Lepidus → `Q72615` Quintus Aemilius Lepidus | 80 | 1 | `Q151874` Marcus Claudius; `Q72618` NN WIfe of Quintus Aemilius Lepidus); `Q72696` N.N.; `Q72699` Lucius Appuleius Saturninus … +21 more |
| `Q72801` Cornelia → `Q72786` Marcus Aemilius Lepidus | 67 | 0 | `Q151874` Marcus Claudius; `Q72618` NN WIfe of Quintus Aemilius Lepidus); `Q72696` N.N.; `Q72699` Lucius Appuleius Saturninus … +18 more |
| `Q73131` Cornelia Africana Major → `Q72957` Consul (138 BC) - Publius Corn | 19 | 0 | `Q73269` N.N.; `Q73446` Publius Cornelius Scipio; `Q73575` Manius Pomponius Matho; `Q73578` NN (Wife of Manius Pomponius Matho) … +1 more |
| `Q73128` Publius Cornelius Scipio Nasic → `Q72957` Consul (138 BC) - Publius Corn | 5 | 0 | `Q73443` Gnaeus Cornelius Scipio Calvus; `Q99384` NN (Wife of Publius Cornelius Scipio N; `Q99402` NN (Wife of Gnaeus Cornelius Scipio Ca |

## Tangle 4 — Godo  Arnaldes de Baiao (14 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q79618` Tereza  Eriz de Lugo → `Q99939` Ufa  Ufes | 355 | 0 | `Q100140` Ero  Fernandez de Lugo; `Q100186` Dordia Osorez; `Q100505` Arnaldo  de Spoleto; `Q100667` N.N. … +104 more |
| `Q99939` Ufa  Ufes → `Q100154` Godo  Arnaldes de Baiao | 319 | 0 | `Q100667` N.N.; `Q100673` Munio  Nunez de Lara; `Q101095` Soeiro  Echigues Soares; `Q105311` N.N. … +89 more |
| `Q101113` D. Ausindo Soares → `Q113625` D.Teodoredo Ausendes Soares | 309 | 0 | `Q100142` Ermesenda  Eris de Lugo; `Q100505` Arnaldo  de Spoleto; `Q101095` Soeiro  Echigues Soares; `Q105311` N.N. … +86 more |
| `Q113625` D.Teodoredo Ausendes Soares → `Q79388` D. Ausindo Ximeno | 306 | 0 | `Q100140` Ero  Fernandez de Lugo; `Q100186` Dordia Osorez; `Q100505` Arnaldo  de Spoleto; `Q100667` N.N. … +108 more |
| `Q79388` D. Ausindo Ximeno → `Q79415` D.Soeiro Ausendes | 306 | 0 | `Q100140` Ero  Fernandez de Lugo; `Q100186` Dordia Osorez; `Q100505` Arnaldo  de Spoleto; `Q100667` N.N. … +110 more |
| `Q79435` D.Arnaldo  Ximenes → `Q79438` Sancho  ou Sancho Arnolfo Xime | 305 | 0 | `Q100140` Ero  Fernandez de Lugo; `Q100186` Dordia Osorez; `Q100505` Arnaldo  de Spoleto; `Q100667` N.N. … +110 more |
| `Q79438` Sancho  ou Sancho Arnolfo Xime → `Q79424` Gil  Guille em Narbonne | 280 | 0 | `Q100140` Ero  Fernandez de Lugo; `Q100186` Dordia Osorez; `Q100505` Arnaldo  de Spoleto; `Q100667` N.N. … +104 more |

## Tangle 5 — Aditi Kashyapa (14 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q153381` Aditi Kashyapa → `Q153465` TVASTAR Kashyapa | 61 | 0 | `Q153503` UTTANAPADA Manu; `Q2151` KA; `Q2152` YA; `Q49642` VIRAN Panchajan … +17 more |
| `Q153381` Aditi Kashyapa → `Q1991` Surya Sun God | 61 | 0 | `Q153503` UTTANAPADA Manu; `Q2151` KA; `Q2152` YA; `Q49642` VIRAN Panchajan … +17 more |
| `Q153444` SUNITA Anga → `Q153438` VENA Anga | 30 | 1 | `Q153398` DEVAHUTI Kardama; `Q1939` Marichi; `Q1954` KARDAMA; `Q49642` VIRAN Panchajan … +7 more |
| `Q153460` SANJNA \ Saranyu Saranyu Saran → `Q2035` Yama Dharma King of Death | 3 | 0 | `Q153465` TVASTAR Kashyapa; `Q50261` Rachana |
| `Q153429` PRITHU (Vishnu's amsam) Vena → `Q1989` Vijitashva | 1 | 1 | `Q153429` PRITHU (Vishnu's amsam) Vena |
| `Q1991` Surya Sun God → `Q2035` Yama Dharma King of Death | 1 | 0 | `Q1991` Surya Sun God |
| `Q2001` Archis(Lakshmi's amsam) → `Q1989` Vijitashva | 1 | 1 | `Q2001` Archis(Lakshmi's amsam) |

## Tangle 6 — Aditi Kashyapa (14 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q160615` VENA Anga → `Q160596` PRITHU Vena | 59 | 0 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +17 more |
| `Q160615` VENA Anga → `Q160597` ARCHIS | 59 | 0 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +17 more |
| `Q160539` PRACHINBARHI → `Q160512` PRACHETAS (10 sons) | 58 | 1 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +16 more |
| `Q160576` Vijitashva → `Q160560` HAVIRDHANA | 58 | 0 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +16 more |
| `Q160673` YAMA Dharma → `Q160640` SUNITA Anga | 58 | 0 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +16 more |
| `Q160730` TVASTAR Kashyapa → `Q160707` SANJNA \ Saranyu Saranyu | 58 | 0 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +16 more |
| `Q160489` DAKSHA Prachetas → `Q160460` Aditi Kashyapa | 57 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160536` Paramlocha … +16 more |
| `Q160560` HAVIRDHANA → `Q160539` PRACHINBARHI | 57 | 0 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +16 more |
| `Q160512` PRACHETAS (10 sons) → `Q160489` DAKSHA Prachetas | 56 | 1 | `Q160507` Brahma's mind; `Q160513` VIRAN Panchajan; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu … +15 more |
| `Q160460` Aditi Kashyapa → `Q160580` SURYA Dev aka SUN GOD Kashyap | 47 | 0 | `Q160513` VIRAN Panchajan; `Q160536` Paramlocha; `Q160537` Kandu; `Q160538` SHATADRUTI … +14 more |
| `Q160460` Aditi Kashyapa → `Q160730` TVASTAR Kashyapa | 47 | 0 | `Q160513` VIRAN Panchajan; `Q160536` Paramlocha; `Q160537` Kandu; `Q160538` SHATADRUTI … +14 more |
| `Q160640` SUNITA Anga → `Q160615` VENA Anga | 30 | 1 | `Q160487` Marichi; `Q160509` DEVAHUTI Manu; `Q160510` KARDAMA; `Q160513` VIRAN Panchajan … +7 more |
| `Q160707` SANJNA \ Saranyu Saranyu → `Q160673` YAMA Dharma | 3 | 0 | `Q160730` TVASTAR Kashyapa; `Q160731` Rachana |
| `Q160580` SURYA Dev aka SUN GOD Kashyap → `Q160673` YAMA Dharma | 1 | 0 | `Q160580` SURYA Dev aka SUN GOD Kashyap |
| `Q160596` PRITHU Vena → `Q160576` Vijitashva | 1 | 0 | `Q160596` PRITHU Vena |
| `Q160597` ARCHIS → `Q160576` Vijitashva | 1 | 0 | `Q160597` ARCHIS |

## Tangle 7 — Caecilia Metella (13 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q139550` Quintus Caecilius Metellus Bal → `Q138399` Caecilia Metella | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q72834` Lucius Caecilius Metellus Calv → `Q141414` Caecilia Metella | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q72858` Quintus Caecilius Metellus Mac → `Q139550` Quintus Caecilius Metellus Bal | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q72984` Quintus Caecilius Metellus → `Q72858` Quintus Caecilius Metellus Mac | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q73146` Lucius Caecilius Metellus → `Q148066` Marcus Caecilius Metellus | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q73146` Lucius Caecilius Metellus → `Q72984` Quintus Caecilius Metellus | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q73311` Lucius Caecilius Metellus Dent → `Q73146` Lucius Caecilius Metellus | 52 | 0 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q73458` Gaius Caecilius → `Q73311` Lucius Caecilius Metellus Dent | 52 | 1 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho) … +11 more |
| `Q139560` Licinia → `Q73458` Gaius Caecilius | 51 | 1 | `Q148080` Gaius Licinius Lucullus; `Q151874` Marcus Claudius; `Q73680` NN (Wife of Gaius Claudius Centho); `Q73683` Caecilia Metella … +10 more |
| `Q141414` Caecilia Metella → `Q139559` Lucullus | 49 | 0 | `Q151874` Marcus Claudius; `Q73581` Lucius Caecilius Metellus; `Q73680` NN (Wife of Gaius Claudius Centho); `Q73683` Caecilia Metella … +10 more |
| `Q138403` Clodia → `Q139560` Licinia | 39 | 1 | `Q151874` Marcus Claudius; `Q72858` Quintus Caecilius Metellus Macedonicus; `Q73680` NN (Wife of Gaius Claudius Centho); `Q73683` Caecilia Metella … +10 more |
| `Q138399` Caecilia Metella → `Q138403` Clodia | 17 | 0 | `Q148080` Gaius Licinius Lucullus; `Q73581` Lucius Caecilius Metellus |
| `Q139559` Lucullus → `Q139560` Licinia | 7 | 0 | `Q148066` Marcus Caecilius Metellus; `Q148080` Gaius Licinius Lucullus |
| `Q148066` Marcus Caecilius Metellus → `Q72834` Lucius Caecilius Metellus Calv | 1 | 1 | `Q148066` Marcus Caecilius Metellus |
| `Q72984` Quintus Caecilius Metellus → `Q72834` Lucius Caecilius Metellus Calv | 0 | 0 | — |

## Tangle 8 — Meurig ab Ynyr Gwent (11 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q136996` Iorwerth Hir ap Llywarch Gam o → `Q137385` Ednyfed ab Iorwerth Hir ap Lly | 184 | 1 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +17 more |
| `Q137384` Ynyr, lord of Gwent → `Q137899` Morfudd ferch Ynir | 184 | 1 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +17 more |
| `Q137385` Ednyfed ab Iorwerth Hir ap Lly → `Q136958` Elen ferch Ednyfed ab Iorwerth | 184 | 1 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +17 more |
| `Q137320` Gwerstan ap Gwaithfoed ap Glod → `Q137449` Lleuki|Nest ferch Gwerstan ap  | 183 | 0 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +16 more |
| `Q137320` Gwerstan ap Gwaithfoed ap Glod → `Q137900` Cynfyn ap Gwerstan | 183 | 0 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +16 more |
| `Q137383` Nest ferch Gwrgan ab Ithel ab  → `Q136957` Meurig ab Ynyr Gwent | 183 | 1 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +16 more |
| `Q137878` NN ferch Cynfyn ap Gwerystan a → `Q137383` Nest ferch Gwrgan ab Ithel ab  | 178 | 1 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +16 more |
| `Q137899` Morfudd ferch Ynir → `Q137320` Gwerstan ap Gwaithfoed ap Glod | 166 | 0 | `Q135420` Magnus Maximus; `Q135549` Gloyw Wallt Hir; `Q135564` Ynyr Gwent; `Q136010` Llŷr … +15 more |
| `Q137900` Cynfyn ap Gwerstan → `Q137878` NN ferch Cynfyn ap Gwerystan a | 82 | 0 | `Q135420` Magnus Maximus; `Q135421` Elen; `Q135424` Cadell Ddyrnllwg; `Q135564` Ynyr Gwent … +10 more |
| `Q136958` Elen ferch Ednyfed ab Iorwerth → `Q137384` Ynyr, lord of Gwent | 49 | 0 | `Q135420` Magnus Maximus; `Q135421` Elen; `Q135424` Cadell Ddyrnllwg; `Q135564` Ynyr Gwent … +6 more |
| `Q137449` Lleuki|Nest ferch Gwerstan ap  → `Q136996` Iorwerth Hir ap Llywarch Gam o | 44 | 0 | `Q136985` Owain ap Hywel; `Q137277` Merfyn ap Rhodri Mawr; `Q137321` Nest ferch Cadell ap Brochwel; `Q137382` Ynyr Gwent … +4 more |
| `Q136957` Meurig ab Ynyr Gwent → `Q137384` Ynyr, lord of Gwent | 18 | 0 | `Q136985` Owain ap Hywel; `Q137277` Merfyn ap Rhodri Mawr; `Q137382` Ynyr Gwent; `Q137900` Cynfyn ap Gwerstan … +2 more |

## Tangle 9 — Shaodian (10 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q87840`    → `Q6421` Shaodian | 11 | 1 | `Q87860` 有蟜 |

## Tangle 10 — Gaius Servilius (8 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q73170` Gaius Servilius → `Q73985` Quintus Servilius | 8 | 0 | — |
| `Q73332` Publius Servilius → `Q73170` Gaius Servilius | 8 | 1 | — |
| `Q73479` Quintus Servilius → `Q73332` Publius Servilius | 8 | 1 | — |
| `Q73599` Gnaeus Servilius → `Q73479` Quintus Servilius | 8 | 1 | — |
| `Q73710` Servilius → `Q73599` Gnaeus Servilius | 8 | 1 | — |
| `Q73812` Gaius Servilius → `Q73710` Servilius | 8 | 1 | — |
| `Q73910` Gaius Servilius → `Q73812` Gaius Servilius | 8 | 0 | — |
| `Q73985` Quintus Servilius → `Q73910` Gaius Servilius | 8 | 1 | — |

## Tangle 11 — Joan ferch Ieuan ap Rhys ap Llowdden (7 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q138061` Joan ferch Ieuan ap Rhys ap Ll → `Q138810` Llywelyn Ddû ab Owain | 307 | 1 | `Q112492` Gisèle de France; `Q114107` Hildegard of Flanders; `Q114205` Richard III; `Q115688` Adela d'Anjou … +80 more |
| `Q139067` Gruffudd Foethus ap Llywelyn → `Q140681` Lleucu ferch Gruffudd | 220 | 0 | `Q135845` Pelinor, 'king of Cornwall'; `Q136321` Elen ferch Tudur Mawr; `Q136538` Môr ap Pasgen ab Urien Rheged ap Cynfa; `Q136540` Llyminod Angel ap Pasgen ab Urien Rheg … +52 more |

## Tangle 12 — Sekhemre Sankhtawy Neferhotep III (7 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q85514` Senebhenaf .  → `Q85498` Sekhemre Sementawi Djehuti | 12 | 0 | `Q85552` Horhorkhuwaytef  of Egypt; `Q85556` Id of  Egypt; `Q85558` wife of Id of Egypt; `Q85580` Satmut of Egypt |
| `Q85514` Senebhenaf .  → `Q85500` Mentuhotep .  | 12 | 0 | `Q85552` Horhorkhuwaytef  of Egypt; `Q85556` Id of  Egypt; `Q85558` wife of Id of Egypt; `Q85580` Satmut of Egypt |
| `Q85478` Sekhemre Sankhtawy Neferhotep  → `Q85578` Sankhenre Mentuhotep VI | 2 | 0 | `Q85498` Sekhemre Sementawi Djehuti |
| `Q85498` Sekhemre Sementawi Djehuti → `Q85478` Sekhemre Sankhtawy Neferhotep  | 1 | 1 | `Q85498` Sekhemre Sementawi Djehuti |
| `Q85500` Mentuhotep .  → `Q85478` Sekhemre Sankhtawy Neferhotep  | 0 | 0 | — |
| `Q85500` Mentuhotep .  → `Q85578` Sankhenre Mentuhotep VI | 0 | 0 | — |

## Tangle 13 — Venkatacharyar Jatavallabha (Jatavallabha award by Maha (7 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q171493` Venkatacharyar Jatavallabha (J → `Q171595` Rangacharya Jatavallabha (Jata | 53 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160891` Brahma's navel … +5 more |
| `Q171595` Rangacharya Jatavallabha (Jata → `Q171604` Venkatacharya Jatavallabha (Ja | 53 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160891` Brahma's navel … +5 more |
| `Q171604` Venkatacharya Jatavallabha (Ja → `Q171614` Srinivasacharya Jatavallabha | 53 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160891` Brahma's navel … +5 more |
| `Q171614` Srinivasacharya Jatavallabha → `Q171622` Srinivasacharyar Jatavallabha  | 53 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160891` Brahma's navel … +5 more |
| `Q171622` Srinivasacharyar Jatavallabha  → `Q171636` Venkatacharya Jatavallabha (Ja | 53 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160891` Brahma's navel … +5 more |
| `Q171636` Venkatacharya Jatavallabha (Ja → `Q171648` Rangacharya Jatavallabha (Jata | 53 | 0 | `Q160507` Brahma's mind; `Q160532` PURUSH aka NARAYANA; `Q160534` SHATARUPA Manu; `Q160891` Brahma's navel … +5 more |
| `Q171648` Rangacharya Jatavallabha (Jata → `Q171493` Venkatacharyar Jatavallabha (J | 7 | 0 | — |

## Tangle 14 — Gepaepyris (6 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q139511` Cotys III → `Q138363` Gepaepyris | 172 | 0 | `Q109101` Ino Anastasia; `Q109303` Vigilantia; `Q118392` Ablabius; `Q130984` Nais … +43 more |

## Tangle 15 — Arsende  de Cabrera (5 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q123407` Marquesa d'Urgell → `Q124325` Guerau IV de Cabrera | 1542 | 1 | `Q100003` Hemesinda  Gutierrez; `Q100062` Urraca; `Q100070` Oneca  Velazquez; `Q100178` Na. Mendes de Asturias … +428 more |
| `Q107162` Ermengol VII, Count of Urgell → `Q123407` Marquesa d'Urgell | 1120 | 0 | `Q100140` Ero  Fernandez de Lugo; `Q100168` Nunilona; `Q100178` Na. Mendes de Asturias; `Q100186` Dordia Osorez … +347 more |
| `Q104371` Arsende  de Cabrera → `Q107162` Ermengol VII, Count of Urgell | 992 | 0 | `Q100003` Hemesinda  Gutierrez; `Q100064` Fortun  Garces de Pamplona; `Q100066` Sancho Garces de Pamplona; `Q100116` Diego  'Porcelos' Rodriguez de Castill … +313 more |
| `Q124325` Guerau IV de Cabrera → `Q124326` Guerau V de Cabrera | 254 | 0 | `Q100001` Nuno  Guterres de Celanova; `Q100009` Ildaura  ?; `Q100142` Ermesenda  Eris de Lugo; `Q100190` Aloito  Gutierrez … +72 more |

## Tangle 16 — Tyro (5 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q131896` Tyro → `Q131902` Neleus | 176 | 0 | `Q130452` Coeus; `Q130456` Phoebe; `Q130560` Hera; `Q131064` Idaea … +33 more |
| `Q75123` Deimachus → `Q132251` Enarete | 163 | 0 | `Q130015` Pleione; `Q130019` Asia; `Q130027` Plouto; `Q130067` Scamander … +50 more |
| `Q132251` Enarete → `Q132367` Salmoneus | 149 | 0 | `Q130015` Pleione; `Q130019` Asia; `Q130027` Plouto; `Q130067` Scamander … +46 more |
| `Q132367` Salmoneus → `Q131896` Tyro | 47 | 1 | `Q130027` Plouto; `Q130189` Orseis; `Q130560` Hera; `Q130714` Sterope … +12 more |
| `Q131902` Neleus → `Q75123` Deimachus | 44 | 0 | `Q130189` Orseis; `Q132041` Pandora; `Q74934` Idaea; `Q74937` Xanthus \ Scamander  Scamander ?King o … +12 more |

## Tangle 17 — Appius Claudius Caecus (5 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q73970` Appius Claudius Crassus Inregi → `Q73887` Gaius Claudius Crassus Inrelli | 16 | 0 | `Q151874` Marcus Claudius; `Q73785` N.N., Wife of Appius Claudius Caecus; `Q73890` NN (Wife of Gaius Claudius Crassus); `Q74162` Gaias  Crassus Regillenius … +1 more |
| `Q78812` Tiberius Claudius Nero → `Q78752` Publius  Claudius-Nero | 16 | 1 | `Q151874` Marcus Claudius; `Q73785` N.N., Wife of Appius Claudius Caecus; `Q73890` NN (Wife of Gaius Claudius Crassus); `Q74162` Gaias  Crassus Regillenius … +1 more |
| `Q73782` Appius Claudius Caecus → `Q78812` Tiberius Claudius Nero | 15 | 0 | `Q151874` Marcus Claudius; `Q73890` NN (Wife of Gaius Claudius Crassus); `Q74162` Gaias  Crassus Regillenius; `Q74213` Gaius Claudius Sabinus  Octavius |
| `Q73887` Gaius Claudius Crassus Inrelli → `Q73782` Appius Claudius Caecus | 15 | 0 | `Q151874` Marcus Claudius; `Q73785` N.N., Wife of Appius Claudius Caecus; `Q74162` Gaias  Crassus Regillenius; `Q74213` Gaius Claudius Sabinus  Octavius |
| `Q78752` Publius  Claudius-Nero → `Q73970` Appius Claudius Crassus Inregi | 7 | 1 | `Q73785` N.N., Wife of Appius Claudius Caecus; `Q73890` NN (Wife of Gaius Claudius Crassus) |

## Tangle 18 — Morfudd ferch Tudur Fongam ap Cynwrig Fychan ap Cynwrig (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q148521` Tudur Fongam ap Cynwrig Fychan → `Q144542` Morfudd ferch Tudur Fongam ap  | 58 | 1 | `Q135824` Nefyn ach Brychan; `Q136050` Cynfarch Oer; `Q136865` Afallach; `Q137280` NN … +9 more |

## Tangle 19 — Olaf Geirstad-Alf (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q123845` Alfhild → `Q118732` Olaf Geirstad-Alf | 4 | 1 | — |

## Tangle 20 — Pepin of Landen (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q111320` Begga → `Q135895` Pepin of Herstal | 275 | 0 | `Q109601` NN; `Q109650` Bisinus; `Q110620` General Sabinianus Magnus; `Q110774` Itta of Metz … +108 more |
| `Q135895` Pepin of Herstal → `Q113081` Charles Martel | 126 | 0 | `Q110788` Ute; `Q111219` Teutomer; `Q111334` Gibica; `Q112082` Papianilla … +36 more |

## Tangle 21 — Pinarius (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q77782` Pinarius → `Q78264` Lucius Pinarius | 5 | 0 | `Q78267` Julia Caesaris Major |
| `Q78264` Lucius Pinarius → `Q78108` Lucius Pinarius Scarpus | 5 | 1 | `Q137708` Julia Major |

## Tangle 22 — Jehoiakim (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q4626` Zebudah → `Q135406` Jehoiakim | 14 | 0 | `Q4625` Meshullam the Scribe; `Q60195` ; `Q60198`  |

## Tangle 23 — Maharaja Parameswara @ Raja Iskandar Shah Paduka Sri Ratna Vira Vikrama di-Raja (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q161658` Maharaja Parameswara @ Raja Is → `Q161777` Dewa Amas Sang Aji Kala | 30 | 0 | `Q160069` Person Q160069; `Q160070` Istri Trailokyaraja; `Q160084` Maharaja Sriwijaya Sanggarama; `Q160085` raja SULAN of Amdan Nayara … +5 more |
| `Q161777` Dewa Amas Sang Aji Kala → `Q161966` Demang Lebar Daun Mangkabumi ( | 30 | 0 | `Q160069` Person Q160069; `Q160070` Istri Trailokyaraja; `Q160084` Maharaja Sriwijaya Sanggarama; `Q160085` raja SULAN of Amdan Nayara … +5 more |
| `Q161966` Demang Lebar Daun Mangkabumi ( → `Q162275` Wan Sendari (Radin Ratna Cende | 30 | 0 | `Q160069` Person Q160069; `Q160070` Istri Trailokyaraja; `Q160084` Maharaja Sriwijaya Sanggarama; `Q160085` raja SULAN of Amdan Nayara … +5 more |
| `Q162275` Wan Sendari (Radin Ratna Cende → `Q161658` Maharaja Parameswara @ Raja Is | 4 | 0 | — |

## Tangle 24 — Swammbhu Brambha (4 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q160981` Person Q160981 → `Q160965` Kasayap Muni | 8 | 1 | `Q160929` N.N.; `Q160947` Gobardhan Vishnu; `Q160948` Person Q160948; `Q160966` Surbhi |
| `Q160928` Swammbhu Brambha → `Q160981` Person Q160981 | 7 | 0 | `Q160947` Gobardhan Vishnu; `Q160948` Person Q160948; `Q160966` Surbhi |
| `Q160965` Kasayap Muni → `Q160946` 11 Rudras | 7 | 0 | `Q160929` N.N.; `Q160947` Gobardhan Vishnu; `Q160948` Person Q160948 |
| `Q160946` 11 Rudras → `Q160928` Swammbhu Brambha | 6 | 0 | `Q160929` N.N.; `Q160966` Surbhi |

## Tangle 25 — Sergius Octavius Pontianus Laenes Octavius  Pontainus (3 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q76933` Sergius Octavius Pontainus → `Q76693` Sergius Octavius Pontianus Lae | 4 | 1 | `Q77395` Paullus |

## Tangle 26 — Lucius Junius  Brutus (3 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q73518` C. Junius Junius Brutus  Brutu → `Q73383` Lucius Junius  Brutus | 3 | 1 | — |

## Tangle 27 — Marcus Livius Drusus (3 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q72798` Marcus Livius Drusus → `Q73119` Marcus Livius Drusus | 12 | 0 | `Q148206` ; `Q73122` ; `Q73290` ; `Q73431` Marcus Livius Drusus … +2 more |

## Tangle 28 — Esther  bat Sahlan ben Abraham (2 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q88454` Esther  bat Sahlan ben Abraham → `Q90982` Esther  bat Yosef ben 'Amram h | 3 | 0 | `Q91024` Alluf Abu Amr Sahlan  ben Abraham |

## Tangle 29 — Marcus Flaccus (2 records)

| edge | ancestors lost | stranded | topmost of the lost branch |
|---|---:|---:|---|
| `Q73653` Cassus Curvus → `Q73530` Marcus Flaccus | 3 | 1 | `Q99414` Marcus Curvus |
| `Q73530` Marcus Flaccus → `Q73653` Cassus Curvus | 2 | 0 | — |

