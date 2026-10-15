# Temple names and Horus names for every monarch: a draft method

Step 5 of the name schema (`name-schema.md`). **Draft by Claude, 2026-10-15, for Emma's review; not
applied.** The monarch list itself is data, not naming, and is built: `wiki-scripts/fetch_monarchs.py`
writes `wikibase/analysis/monarchs.tsv` (everyone with a Wikidata id who held a position that is a kind
of monarch, Q116, with the positions; consorts dropped): 2,672 records on 2026-10-15, the commonest being "king", Emperor of China, khan, Emperor of Japan, pharaoh.

## Her rule (2026-10-13)

"Every monarch ever ... needs to have a temple name and a Horus name." Chinese emperors also get a
Christian or Muslim name; pharaohs' lost name parts are restored and Hellenized names standardized.
Presidents probably not ("but I'm not sure about that"); decided 2026-10-15: monarchs only.

## Temple names (廟號)

Follow the Chinese practice the name comes from, where the temple name records the ruler's place in
the dynasty, read in each language (Taizu, Taiso, Taejo):

| Place in the house | Temple name |
|---|---|
| founder of the house's rule | 太祖 Tàizǔ |
| second ruler, who secures it | 太宗 Tàizōng |
| a ruler who restores it after a break | 世祖 Shìzǔ, or 中宗 Zhōngzōng if within the same line |
| the last ruler | 末帝 Mòdì (the practice's own term for a last ruler without a temple name) |
| others | from a short list of virtue names by reign character: 高宗 (long reign), 仁宗 (benevolent), 英宗, 宣宗, 憲宗 ... |

Rulers who already have a temple name (Chinese, Korean and Vietnamese monarchs) keep theirs. "Place in
the house" comes from the position held and the order of holders in `monarchs.tsv`; a house's rulers are
those sharing a position and a paternal or canonical line.

## Horus names

The first of the pharaoh's five names, built on the pattern *Ḥr* + epithet ("Horus, Strong Bull ..."),
written in hieroglyphs inside a serekh and given in transliteration and English. For non-Egyptian
monarchs, the epithet is drawn from the ruler's recorded byname or reign (Alfred the Great: *Ḥr kꜣ-nḫt
wr*, "Horus, Strong Bull, the Great"). Pharaohs keep their attested Horus names; where lost, the gap is
restored on the pattern of their dynasty and marked as a restoration.

## Christian or Muslim names for Chinese emperors

A baptismal-style name chosen from the saint or prophet whose day or story is nearest the emperor's
recorded deeds, in the neo-kun'yomi table where the root is there (`neo-kunyomi-names.md`).

## To apply, once she approves

Typed NAME records in `export_gedcom7.py` (`PHRASE temple name`, `PHRASE Horus name`), and a column on
the person pages.
