# Neo-kun'yomi for Abrahamic and Christian names: a draft table

Step 3 of the name schema (`name-schema.md`). **Draft by Claude, 2026-10-15, for Emma's review; not
applied to `/gaiad.ged`.** Naming is hers (`CLAUDE.md`: "NAMING AND NARRATIVE INTENT ARE EMMA'S"), and a
naming system published in the GEDCOM spreads beyond recall ("kind of hyperstitionally there"), so the
table is written and the applying waits for her word.

## Her rule

> "an extremely systematic representation of ... Abrahamic names as standardized kanji form corresponding
> to the root. So all versions of John are the same, all versions of David are the same." (2026-10-13)

Not the primary Japanese form, one representation among others. Her own examples set the method
(`research/glossary.md`, 2026-10-05): **George = 地働** (Greek *geōrgos*, "earth-worker": a calque of the
meaning), **Helensdotter = 平蓮娘**, **-son = 儿**, and "You read Olga as Olga, not as Oruga": the kanji
carry the root's meaning, the reading is the person's own name. So Iván, Juan, Johann and Yahya are all
神恵, read *Iván*, *Juan*, *Johann*, *Yaḥyā*.

## The table

Kanji follow the root's best-attested etymology; where scholars disagree, the note says so. Counts are
records in `wikibase/analysis/persons.tsv` whose given name starts with one of the root's forms
(2026-10-15; 6,531 of 105,129 named records).

| Root | Forms counted | Meaning of the root | Kanji | Records |
|---|---|---|---|---|
| John | Juan, Jean, Johann, Giovanni, Ivan, João, Jan, Hans, Yahya, Seán, Ian | Hebrew *Yəhōḥānān*, "Yah is gracious" | 神恵 | 1,127 |
| Mary | Maria, Marie, Miriam, Maryam, Mariam | uncertain; the common proposal is Egyptian *mry*, "beloved" | 愛 | 952 |
| Peter | Pedro, Pierre, Pietro, Petrus, Piotr, Pyotr | Greek *petros*, "rock" | 岩 | 528 |
| Elizabeth | Isabel, Isabella, Elisabeth, Isabeau | Hebrew *Elisheba*, "my God is an oath" | 神誓 | 521 |
| Muhammad | Mohammed, Mehmed (Ahmad shares the root) | Arabic, "praised" | 讃 | 441 |
| David | Dawud, Daud, Davit, Dafydd | Hebrew *dōḏ*, "beloved"; 寵 to keep it apart from Mary's 愛 | 寵 | 366 |
| Anne | Anna, Ana, Hannah | Hebrew *Ḥannah*, "favour, grace" | 恵 | 339 |
| Francis | Francisco, Francesco, François, Franz | Latin *Franciscus*, "Frankish", the Franks read as "the free" | 由 | 328 |
| Jacob | James, Jacques, Jakob, Jaime, Diego, Giacomo, Yaqub, Santiago | Hebrew *Yaʿaqōḇ*, "heel-holder" | 踵 | 322 |
| Margaret | Margarita, Margarida, Marguerite, Margarethe | Greek *margaritēs*, "pearl" | 珠 | 227 |
| Thomas | Tomás, Tommaso | Aramaic *tʾōmā*, "twin" | 双 | 207 |
| Ali | | Arabic, "high, exalted" | 高 | 178 |
| Catherine | Catalina, Caterina, Katharina, Ekaterina | uncertain; long associated with Greek *katharos*, "pure" | 純 | 175 |
| Joseph | José, Giuseppe, Josef, Yusuf, Iosif | Hebrew *Yōsēp̄*, "he will add" | 加 | 140 |
| Michael | Miguel, Michel, Mikhail | Hebrew *Mīḵāʾēl*, "who is like God?" | 如神 | 111 |
| George | Jorge, Giorgio, Georg, Yuri | Greek *geōrgos*, "earth-worker" (Emma's) | 地働 | 94 |
| Isaac | Ishaq, Yitzhak | Hebrew *Yiṣḥāq*, "he will laugh" | 笑 | 92 |
| Abraham | Ibrahim, Avraham, Abram | Hebrew, "father of many" (Gen 17:5) | 衆父 | 84 |
| Stephen | Esteban, Stefano, Étienne, Stefan | Greek *stephanos*, "crown" | 冠 | 78 |
| Andrew | Andrés, Andrea, André, Andreas, Andrei | Greek *andreios*, "manly, brave" | 勇 | 72 |
| Solomon | Sulayman, Süleyman, Salomon | Hebrew *šālōm*, "peace" | 和 | 42 |
| Matthew | Mateo, Matteo, Matthias, Mathieu | Hebrew *Mattityahu*, "gift of Yah" | 神賜 | 35 |
| Samuel | | Hebrew *Šəmūʾēl*, "God has heard" (one reading) | 神聴 | 30 |
| Paul | Pablo, Paolo, Pavel | Latin *paulus*, "small" | 小 | 29 |
| Daniel | | Hebrew *Dāniyyēl*, "God is my judge" | 神判 | 13 |

## Choices made, for her to overrule

- **God-names take 神**, not 命. On the site 命 replaces 神 in sacred contexts (shrines, the deity); a
  person's name is not one, and 神 is ordinary in Japanese names.
- **Mary 愛 and David 寵** split the one meaning "beloved" so the two roots stay distinct, as her rule needs.
- **Muhammad and Ahmad** share 讃 (one root, ḥ-m-d); Mehmed is Muhammad.
- **James, Diego and Santiago are Jacob** (*Iacobus*), as historical linguistics has it.
- **Yuri is George** (her own "Yuri is George").

## To apply, once she approves

In `export_gedcom7.py`: a typed NAME (`TYPE OTHER`, `PHRASE neo-kun'yomi`) with the kanji and the
person's own name as the reading, e.g. `1 NAME 神恵` / `2 TYPE OTHER` / `3 PHRASE neo-kun'yomi (read Juan)`.
