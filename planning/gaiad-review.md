# Systematic review of the Gaiad, ch 1 to 364 (begun 2026-10-14)

Emma, 2026-10-12: "a systematic review of all of the chapters in chronological order ... to review the
degree that they satisfy all of the criteria that order.life is supposed to have." One chapter at a time,
one commit each. Criteria: `STATUS.md` pinned corrections (verse register; three braided registers; modern
placenames; `{{c|}}`/`{{p|}}` tagging), `CLAUDE.md` (genealogy told by its story; linear time; one
set of parents; cross-tradition joins kept), `planning/gaiad-tone-and-founders.md`, the thematic spine for
253-364, the chapter's day and holiday, and its facts.

Standing decisions:
- No "Stand." (removed from all chapters 2026-10-14 on Emma's word).
- Emma's own chapters (ch 1 to about 129) are not rewritten; the review fixes tagging and plain errors only
  and notes anything larger for her.
- The site strips the tags (`build.py` `load_chapters`): `{{c|Aster}}` renders as plain "Aster", so tags
  are an index, not links, today. The tags take no display alias, so a name whose tag would point at the wrong
  entity is left untagged. Real links are the later "links are present" item.
- The galaxies are beings in the Gaiad's cosmology (Aster and Andromeda are galaxies as persons; Triangulum and
  the Magellanic Clouds act in ch 2; Milkdromeda is their union; Sagittarius beside "the Princess" stands for
  Aster), so they keep `{{c|}}` tags. Words tagged as characters by the 2025-11-18 automated pass ("Once",
  "Together" and the like, which also made junk files in `Gaiad/genealogy/`) are untagged.
- **Tagging rule (Emma, 2026-10-14 17:23):** "Everything needs a tag unless you're really not confident about
  it." A place is `{{p|}}`, a character `{{c|}}`; a name of unclear kind, or significant but neither, is
  `{{x|}}`. Do not convert existing tags ("Converting everything to the x tag is destructive"); the database
  fixes the rest later (not to be worked on now). `build.py` strips `x` like `c` and `p`.
- Length (60-150 lines) is a guide for new chapters, not a reason to cut or pad hers.

| ch | title | verdict | changes |
|---|---|---|---|
| 1 | The Yarn of Creation | Emma's 2020 verse; passes | `{{c|Once}}` untagged (a word, from the 2025-11-18 automated tagging). Galaxies kept as characters (corrected 17:14: the first pass made them places, wrongly). 32 lines, her length kept. |
| 2 | Aster's First Call | Emma's verse; passes | `{{c|Together}}` untagged (a word). |
| 3 | Andromeda's Answer | Emma's verse; passes | untagged (words): Together, Now, Main, Incomplete, Discovery, Red, Milky; to `x` (kind unclear): Steppenwolves. |
| 4 | The First Yarn String | Emma's verse; passes | untagged (words): Once; to `x` (kind unclear): Nova. |
| 5 | The Big Bang of Longing | Emma's verse; passes | untagged (words): Oceans. |
| 6 | Hydrogen Clouds Ignite | Emma's verse; passes | untagged (words): Multiplying. |
| 7 | Primordial Stars Burn | Emma's verse; passes | Stray "Advertisement" line at the end removed (web-page residue; also in ch 3, 12, 13, removed there too). For Emma: the title does not match the story (the cyborg shells, Bios, Viros and Dedos naming Aster "Greatest Grandmother"). No holiday on the day. |
| 8 | Heavy Elements Scattered | Emma's verse; passes | For Emma: Phaestia is a moon of the gas giant Venti here, of Vayu in ch 9 (both wind gods; one world under two names, or a slip?). Day 8 is Coming of Age Day; the verse does not touch it (her chapter, not rewritten). |
| 9 | Gravity's Dark Dance | Emma's verse; passes | Aster's syncretic titles (Suiten, Myōken, Konjin, Brahma, Vairocana, Varuna) kept as written. |
| 10 | Spiral Arms Form | Emma's verse; passes | Serenitide, Pluvia, Quiyah. |

**Titles of ch 4-20 (noted 2026-10-14 18:20).** They come from `COMPREHENSIVE_CHAPTER_PLAN.md` (2025-09-07), a
plan of the cosmos in order (stars, heavy elements, the solar nebula, the Moon's birth), and the verse went its
own way (Hesper, Phaestia, Serenitide, the three brothers), so most of these titles name what the chapter does
not tell. For Emma: retitle from the verse, or keep the plan's titles. Left as they are until she says. Queue
item 25 (the chapters and their histories) covers the same split.

Line-initial plain-word tags still left (Replication, Consuming, Preferring, Starvation, People, Volcanoes,
Lava, Propelled...) belong to queue item 26 and are not touched in the review.

## Tagging pass, ch 7-364 (2026-10-14, evening)

Done in one pass under the tagging rule above, by eight parallel agents, each file checked: the text with
tags stripped is unchanged. Commits on order.life master: `4a1677c11` (7-50), `1721fca32` (51-95),
`45d4a2c63` (96-140), `3296f1f87` (141-185), `69b8a8e34` (186-230), `06348bbce` (231-275), `2a5ec2a56`
(276-320), `27aae8c38` (321-364). Ch 178-220 had almost no tags before and gained the most.

Then `137cc8ff5`: 560 tags removed from line-initial plain words (adverbs, adjectives, verbs, numbers,
function words: Than, Now, Bold, Fair, Throughout, Together...) left by the 2025-11-18 automated pass. Every
noun kept its tag (Life, Water, Fire, God, King...). Two broken nested tags in ch 57
(`{{c|{{c|453|Osticthus}}}}`, rendered on the site as "453|Osticthus") fixed.

Left for the database (not worked on now): the same name carrying different letters in different chapters
(Devonian, Cambrian, Carboniferous c and x; Shia x in 256, c in 263; China c and p in 220; Andromeda c and p
in 364); multi-word names tagged only in part (`{{c|Iron}} Catastrophe`); names split across a line break
("Three / Kingdoms" 49, "Hundred / Years' War" 216, 219); hyphen compounds (tagged at the name part in
some chapters, untagged in others).
