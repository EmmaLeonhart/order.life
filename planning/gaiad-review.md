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
- `{{x|...}}` (Emma, 2026-10-14): a neutral tag for any proper noun. When it is not plain whether a name is a
  character, a place or a thing, it gets `x`, not a guess; existing `c`/`p` tags stay unless plainly wrong.
  `build.py` strips `x` like `c` and `p`.
- Length (60-150 lines) is a guide for new chapters, not a reason to cut or pad hers.

| ch | title | verdict | changes |
|---|---|---|---|
| 1 | The Yarn of Creation | Emma's 2020 verse; passes | `{{c|Once}}` untagged (a word, from the 2025-11-18 automated tagging). Galaxies kept as characters (corrected 17:14: the first pass made them places, wrongly). 32 lines, her length kept. |
| 2 | Aster's First Call | Emma's verse; passes | `{{c|Together}}` untagged (a word). |
| 3 | Andromeda's Answer | Emma's verse; passes | untagged (words): Together, Now, Main, Incomplete, Discovery, Red, Milky; to `x` (kind unclear): Steppenwolves. |
| 4 | The First Yarn String | Emma's verse; passes | untagged (words): Once; to `x` (kind unclear): Nova. |
| 5 | The Big Bang of Longing | Emma's verse; passes | untagged (words): Oceans. |
| 6 | Hydrogen Clouds Ignite | Emma's verse; passes | untagged (words): Multiplying. |
