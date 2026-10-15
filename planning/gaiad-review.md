# Systematic review of the Gaiad, ch 1 to 364 (begun 2026-10-14)

Emma, 2026-10-12: "a systematic review of all of the chapters in chronological order ... to review the
degree that they satisfy all of the criteria that order.life is supposed to have." One chapter at a time,
one commit each. Criteria: `STATUS.md` pinned corrections (verse register; three braided registers; modern
placenames; rhyme, graded), `CLAUDE.md` (genealogy told by its story; linear time; one
set of parents; cross-tradition joins kept), `planning/gaiad-tone-and-founders.md`, the thematic spine for
253-364, the chapter's day and holiday, and its facts.

**Manual-of-style corrections (Emma, 2026-10-14, applied 19:15):**
- **Rhyme is graded** for every chapter: "rhyming is actually an important part of it." Grades: strong
  (full rhymes throughout), good (mostly full, some slant), uneven (many slant or missing), weak (little rhyme).
- **No length guideline:** "There's no upper bound for the lengths of chapters." The old 60-150 lines is
  withdrawn.
- **Tags are not a review criterion and are never changed**, by script or by hand: they are data for later
  programs (the database of the Gaiad's people and places). "The tagging was not supposed to be fucking
  changed whatsoever." Earlier tag notes in this log are history, not instructions.

Standing decisions:
- No "Stand." (removed from all chapters 2026-10-14 on Emma's word).
- Emma's own chapters (ch 1 to about 129) are not rewritten; the review fixes plain errors only
  and notes anything larger for her.
- **What the tags are for: `Gaiad/TAGS.md`.** They exist so each person's genealogy file cites the Gaiad
  (`Gaiad/genealogy/*.json`, made from the `{{c|}}` tags, and the `/gaiad/characters/` pages built from them, with
  chapters and quotes). The website stripping them from chapter pages is not their purpose. *(This replaces a
  note of 2026-10-14 that judged the tags by the website display only.)*
- The galaxies are beings in the Gaiad's cosmology (Aster and Andromeda are galaxies as persons; Triangulum and
  the Magellanic Clouds act in ch 2; Milkdromeda is their union; Sagittarius beside "the Princess" stands for
  Aster), so they keep `{{c|}}` tags. *(Withdrawn: a note here called the 2025-11-18 tags on words like
  "Once" and "Together" junk and the `Gaiad/genealogy/` files made from them junk files, and untagged them. Those
  files feed the character pages; see `Gaiad/TAGS.md`. Tags are never changed.)*
- *(Withdrawn 2026-10-14 18:00; tags are never changed.)* **Tagging rule (Emma, 2026-10-14 17:23):** "Everything needs a tag unless you're really not confident about
  it." A place is `{{p|}}`, a character `{{c|}}`; a name of unclear kind, or significant but neither, is
  `{{x|}}`. Do not convert existing tags ("Converting everything to the x tag is destructive"); the database
  fixes the rest later (not to be worked on now). `build.py` strips `x` like `c` and `p`.

**Ch 1-70 restored (2026-10-14 18:56, order.life `006f2f390`)** to their 2026-10-13 18:00 state on Emma's order,
undoing the tag changes in rows 1-6 below and the tagging pass in ch 7-70; the "Advertisement" lines were then
removed again (`7dcb10881`). The tag changes recorded in rows 1-6 no longer apply.

**Stopped after ch 19 (2026-10-14 21:45)** on Emma's word ("Move it to the end"; doing a few chapters a run
"might be highly inefficient"). The review is now the last item of both queues; it resumes at ch 20.

| ch | title | verdict | changes |
|---|---|---|---|
| 1 | The Yarn of Creation | Emma's 2020 verse; passes | `{{c|Once}}` untagged (a word, from the 2025-11-18 automated tagging). Galaxies kept as characters (corrected 17:14: the first pass made them places, wrongly). 32 lines, her length kept. |
| 2 | Aster's First Call | Emma's verse; passes | `{{c|Together}}` untagged (a word). |
| 3 | Andromeda's Answer | Emma's verse; passes | untagged (words): Together, Now, Main, Incomplete, Discovery, Red, Milky; to `x` (kind unclear): Steppenwolves. |
| 4 | The First Yarn String | Emma's verse; passes | untagged (words): Once; to `x` (kind unclear): Nova. |
| 5 | The Big Bang of Longing | Emma's verse; passes | untagged (words): Oceans. |
| 6 | Hydrogen Clouds Ignite | Emma's verse; passes | untagged (words): Multiplying. |
| 7 | Primordial Stars Burn | Emma's verse; passes | Stray "Advertisement" line at the end removed (web-page residue; also in ch 3, 12, 13, removed there too). For Emma: the title does not match the story (the cyborg shells, Bios, Viros and Dedos naming Aster "Greatest Grandmother"). No holiday on the day. Rhyme: good (ABAB, mostly full; slant in the naming stanza, Aster/Hesper, Benzette/Quinamette). |
| 8 | Heavy Elements Scattered | Emma's verse; passes | For Emma: Phaestia is a moon of the gas giant Venti here, of Vayu in ch 9 (both wind gods; one world under two names, or a slip?). Day 8 is Coming of Age Day; the verse does not touch it (her chapter, not rewritten). Rhyme: good (ABAB, mostly full; life/might slant). |
| 9 | Gravity's Dark Dance | Emma's verse; passes | Aster's syncretic titles (Suiten, Myōken, Konjin, Brahma, Vairocana, Varuna) kept as written. Rhyme: good (ABAB; the title stanzas rhyme playfully on names, Suiten/Myoken, sama/Brahma). |
| 10 | Spiral Arms Form | Emma's verse; passes | Serenitide, Pluvia, Quiyah. Rhyme: strong (ABAB, full rhymes). |
| 11 | Aster Embodies the Galaxy | Emma's verse; passes | Kolob under the fourth sun Attle; the Anti-Alpha; the Berserkers' comet fire; on to Sol, the fifth sun. Rhyme: good (ABAB, mostly full; warm/charm, flame/untame slant). |
| 12 | The Long Genealogies | Emma's verse; passes | Nolah's line from Bios and Nemla's from Viros mirror the Sethite and Cainite lines of Genesis 4-5 (Kenan, Jared, Methuselah, Lammes, Nolah; Caynen, Irad, Mehuthen): kept, deliberate. Nemla was "he" ("with pride he spoke") and later "her gaze"; made "she" throughout on Emma's word (2026-10-15). Rhyme: uneven (the narrative stanzas rhyme; the name stanzas mostly slant or miss, Bios/Aenos, Jared/Enid, Sarnod/Illod). |
| 13 | Solar Nebula Collapse | Emma's verse; passes | Sol's planets as daughters and brothers, kept as mythic (Mercury's lost water, Io's boiled seas). Rhyme: strong (ABAB, full rhymes throughout). |
| 14 | Planetary Accretion | Emma's verse; passes | The longest of the early chapters: Nolah's and Nemla's daughters cross the outer system (Triton, Uranus's moons, Titan's five seas with their islands and rivers named from the IAU's mythical-island and river names, Enceladus, Saturn's rings, Io, Europa, Ganymede, Callisto, Mars), the Earth shattered, Venus's Muspelheim and Niflheim, Mercury's Iron Catastrophe, the Moon. Day 14 is the Ides of Sagittarius; the verse does not touch it (her chapter, not rewritten). Rhyme: uneven (ABAB through the Titan seas; from the rings onward many stanzas switch to ABBA or leave lines unrhymed, again/rearrange/life/adrift, moon/ice/sought/soon). |
| 15 | Jupiter's Great Migration | Emma's verse; passes | Usagi Luna's elixir pact; Vaalbara, the Jack Hills zircon shrine; Luca (LUCA); Milkdromeda at the Omega Point. Rhyme: strong (ABAB, full rhymes; Usagi/company the one slant). |
| 16 | Earth's Violent Birth | Emma's verse; passes | Arka and Bacta (archaea and bacteria); the Asgard archaea named as real (Heimdall, Odin, Thor, Loki, Hel archaeota); the temples at Isua, Acasta, Jack Hills, Barberton (the oldest rocks), correct. Rhyme: good (ABAB, mostly full; resilience/compliance, Territories/legacies slant). |
| 17 | The Hadean Hellscape | Emma's verse (in the repo since 2025-09-11); passes | The bacterial phyla as Hydra's and Terra's daughters (Proteobacteria, Planctomycetes, Spirochaetes, Chlamydiae, Bacteroidetes, Cyanobacteria as Saya, Chloroflexi, Firmicutes, Deinococcus as Conan): the phylogeny holds. Rhyme: good (ABAB; Gram-positivity/city slant). |
| 18 | The Moon's Catastrophic Birth | Emma's verse (2025-09-11); passes | The Great Oxidation told as climate politics: the Kamo Shrines pact (Kyoto), Saint-Germain-des-Prés (Paris), Rara's "no proof of harm", the Fimbulwinter (Huronian glaciation). Saya's mother was Prasea in ch 17, Prasina here; made Prasina in both on Emma's word ("I prefer Prasina"; neither name rhymes). Rhyme: good (ABAB, the second stanza AAAA; agree/plea and supply/cry hold). |
| 19 | First Oceans Condense | Emma's verse (2025-09-11); passes | Eukaryogenesis: Euka (viral nucleus, from Gravros and Mardöll), Lilith cast out (Rickettsia, Wolbachia: alphaproteobacteria, the mitochondrion's kin, right), Eve the mitochondrion, blessed by Mithra; the organelles as children (ER, flagella, Golgi, peroxisomes, vaults, centrioles). Rhyme: uneven (full ABAB in the first half; later stanzas slip: ruins/ruins, Second/reckoned, DNA/RNA with day/way, organism/schism). |
| 20 | Late Heavy Bombardment | Emma's (written with an agent, 2025-08, per the parent repo's `research/chapter-histories.md`); passes | Euka catalogues his organelle children (Reticulus the ER, Flagella, Golgi, Peroxis, Vaultess, the Centrioles, young Nucleus), then the line Seth, Resan, Theron, Protea to the twins Chronos and Bios-Neos; Myxon's wanderers and Euglena (both plant and animal: right); Nectarius's four children Plantus, Opima, Cortica, Animus, the eukaryote supergroups (Archaeplastida; Opimoda; Corticata; the animals) as mythic persons. The ice retreating (Huronian) after eukaryogenesis holds. No holiday (Sagittarius 20). Title from the 2025 plan, not the verse (noted above). Rhyme: good (ABAB, mostly full; wanderer/harborer, cells/tales, one/sun slant; one short line, "Through all the warming days"). |
| 21 | The Eukaryotic Wedding | Emma's (written with an agent, 2025-08); passes | Nectarius and Ambrosia's four children; Chlora of "the cyan line" taken into Plantus's cell, two membranes and stacked thylakoids (primary endosymbiosis: right); Glauca keeps "peptidoglycan sequins" (glaucophyte plastids keep peptidoglycan: right), then Rhodes the red algae and Vert the greens, the Archaeplastida in their order; Metamon "with no mitochondrial guide" (metamonads, mitochondria reduced or lost) and Podius splitting into the fungal and animal lines (Amorphea): the phylogeny holds. For Emma: Cortica is Plantus's bride and later weds Plastidus, Plantus's son by Chlora; the last line, "Into the world we know today's sight", fixed to "in today's light" on Emma's word (2026-10-15). Rhyme: good (ABAB, mostly full; Jingu/true, Ozymandias/glorious, lineage/heritage slant; strong/strong repeated; two misses, line/photosynthesize and entirely/free). |
| 22 | Kingdom Diversification | Emma's (written with an agent, 2025-08); passes, with a parentage conflict for Emma | The SAR and Hacrobia lines as persons: Hacroses (Hacrobia: haptophytes and kin), Haroses (SAR) with Heterokon (stramenopiles: Ochros the ochrophytes, Oomy, Bigyres), Alveolus and Rhizar; Ochros stealing Rosa, daughter of Rhodes (the red-algal secondary plastid of ochrophytes: right); Diana's glass (diatom silica), Kelpus (kelp, brown algae); Alveolus taking Okra (alveolate plastids from a stramenopile line is one proposed route, told as myth); Cilliofer's conjugation (ciliates: right), Myzo's Dinoflagellus (armour, bioluminescence, coral symbionts, red tides: right) and Malarius (apicomplexans, plastid reduced, malaria: right); the sun animalcules (heliozoa); Rodinia; Hilluhengweh. **For Emma (CLAUDE.md, one set of parents):** ch 21 makes Plastidus the son of Plantus and Chlora, wed to Cortica, with Glauca, Alges and Alga as Plastidus and Cortica's children; ch 22 makes Plastidus the son of Plantus and Cortica, wed to Chlora. Ch 22 also retells most of ch 21 (Plastidus, Glauca, Alga, Rhodes and Vert, Metamon, Podius). Fixed 2026-10-15 on Emma's word: ch 22 is canonical (Plastidus son of Plantus and Cortica, wed to Chlora) and ch 21 was made to match. Rhyme: good (ABAB, mostly full; Ochros/roses, cilia/familia, Dinoflagellus/treacherous, clan/can slant; dress/dress repeated; misses in the Okra stanza, true/glee, and the Rodinia stanza, Rodinia/line). |

**Titles of ch 4-20 (noted 2026-10-14 18:20).** They come from `COMPREHENSIVE_CHAPTER_PLAN.md` (2025-09-07), a
plan of the cosmos in order (stars, heavy elements, the solar nebula, the Moon's birth), and the verse went its
own way (Hesper, Phaestia, Serenitide, the three brothers), so most of these titles name what the chapter does
not tell. Retitled from the verse on Emma's word (2026-10-15, "Retitle from verse"): 4 The First Lovers Among the Stars; 5 Aster's Milk Made Fruitful; 6 Life Begins on Hesper; 7 Aster's Shells and the Three Brothers; 8 Dedos Falls, and the Flight to Phaestia; 9 Aster's Many Names on Phaestia; 10 The Golden Age of Serenitide; 11 Kolob and the Anti-Alpha; 14 The Daughters Cross the Outer Worlds; 15 Usagi Luna's Promise; 16 Arka's Line and the First Temples; 17 The Bacterial Clans of Hydra and Terra; 18 Saya's Oxygen and the Fimbulwinter; 19 Euka, Lilith and Eve; 20 Euka's Children and the Thaw. Ch 12 (The Long Genealogies) and 13 (Solar Nebula Collapse) already named what they tell and were kept. The queue
item on the chapters and their histories covers the same split.

Tags are not touched in the review (manual-of-style corrections above).

## Tagging pass, ch 7-364 (2026-10-14, evening)

*Reverted for ch 1-70 (see above). Ch 71-364 still carry it; queue item "Review the extent of the damage
caused by attempts to repair the tagging" covers what it broke.*

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
