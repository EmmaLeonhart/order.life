# Chinese names for everyone: a draft method

Step 4 of the name schema (`name-schema.md`). **Draft by Claude, 2026-10-15, for Emma's review; not
applied to `/gaiad.ged`**, for the same reason as the neo-kun'yomi table: naming is hers, and the GEDCOM
spreads.

## Her rule (2026-10-13)

- Every person gets a Chinese name "independent of the transliteration".
- Aim for **uniqueness** and a **phonetic relation** to the person's name.
- The surname can come **from the clan, not the given name**: "Muhammad's surname could be Ma, but given
  name would be something different"; "something Quraysh-derived. Hashemite is an option ... something
  like Ha" (哈).

## Method

1. **People who already have a Chinese name keep it** (Chinese people; Japanese and Korean people take
   their names in hanzi, simplified only where the source is). Nothing below touches them.
2. **Surname: one character from the house or clan**, taken from the first syllable of its name by the
   standard Xinhua transliteration table (the one behind 《世界人名翻译大辞典》), choosing among that
   syllable's characters one that is also an attested Chinese surname. Muhammad: Banu Hashim → 哈 *Hā*,
   as she proposed. Where the house is unknown, the person's own family name is used the same way.
3. **Given name: one or two characters**, the first one or two syllables of the given name by the same
   table, preferring characters with good meanings over the table's neutral ones where the sound is equal
   (the long practice behind 林肯, 伯克). The given-name characters do not repeat the surname character.
4. **Uniqueness:** where two people would share a full name, the later-born takes a second given-name
   character from the next syllable of their name, then from their canonical parent's name
   (`canonical_line.tsv`), so the difference still means something.

## Worked examples (to show the method, not settled names)

| Person | House or clan | Surname | Given name | Chinese name |
|---|---|---|---|---|
| Muhammad (Q65705) | Banu Hashim | 哈 Hā | 穆 Mù (Mu-) | 哈穆 |
| Charlemagne (Charles) | Carolingian | 加 Jiā (Ca-) | 查 Chá (Char-) | 加查 |
| William the Conqueror | Normandy | 诺 Nuò (Nor-) | 威廉 Wēilián | 诺威廉 |
| Johannes Bureus | Bure | 布 Bù | 约翰 Yuēhàn | 布约翰 |
| Isabella I of Castile | Trastámara | 特 Tè (Tra-) | 伊莎 Yīshā | 特伊莎 |

Notes on the examples: 威廉 and 约翰 are the established Chinese forms of William and John and are kept as
given names, which the method allows where the standard form is already two characters. Charlemagne's
house name gives 加, an attested surname.

## To apply, once she approves

A Chinese NAME in `export_gedcom7.py` (`TYPE OTHER`, `PHRASE Chinese name`, with `TRAN` `LANG zh`), built
from a table of house names to surname characters and the Xinhua syllable table, run over everyone
without a Chinese name of their own; then the uniqueness pass.
