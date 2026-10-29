# What the Gaiad's tags are for

Read this before touching a `{{c|...}}`, `{{p|...}}` or `{{x|...}}` tag in any chapter, or any script that
reads them.

## The purpose

Emma, 2026-10-14: "the intention behind this was to tag the characters and have it so that there would be,
have it so the Gaiad would be cited on their genealogy files." The tags are **data, not display markup**. They
say who and where each name is, so that every person in the Gaiad has a genealogy file that cites the chapters
and lines they appear in. Later programs (the CI/CD and local tools; a database of the Gaiad's people and
places, the Loka database, with each person's GEDCOM data, "where they are recorded", "the chapters that they
are in, the quotes that they are in") are built on them.

"Even tagging something wrong isn't really a problem", because those programs will sort it out. "The tagging
was not supposed to be fucking changed whatsoever." So: **never change existing tags**, by script or by hand,
and tags are not a review criterion. A tag that looks wrong is not a defect to fix.

## What reads them today (checked 2026-10-14)

- `Gaiad/scripts/extract_characters.py` reads every `{{c|Name}}` in `Gaiad/epic/chapter_*.md` and writes one
  file per character to `Gaiad/genealogy/<name>.json`: the name, `chapters_mentioned_in`, father, mother,
  children and a Wikidata QID. 2,044 files, last regenerated 2026-03-02. Nothing runs it automatically, so the
  files show the tags as they were then.
- `build.py` `load_genealogy()` reads those files and builds a page for every character at
  `/gaiad/characters/<name>/` (`templates/gaiad/character.html`): family links, and the lines of each chapter
  that mention the name, as quotes.
- `Gaiad/scripts/add_character_ids.py` and `Gaiad/scripts/tag_all_characters.py` wrote the tags (the
  2025-11-18 automated passes). The first wrote an ID form, `{{c|453|Osticthus}}` (ch 57); it is a tag with an
  ID, not a broken tag.
- `build.py` `load_chapters()` strips the tags for the chapter pages, so the reader sees plain names. That is
  the only place display comes into it, and it is not what the tags are for.
- `scripts/compile_gaiad.py` (the `compile-gaiad` workflow) keeps the tags in the raw compilations and strips
  them in the readable ones.

## What this means for any change

Before changing a tag, or a word inside one, account for the genealogy files and the pages built from them:
removing a tag (even on a word like "Abandoned") takes a character out of the next regeneration and its page off
the site; re-lettering one moves it between people, places and other things. The 2026-10-14 tagging work did
not do this: it judged the tags by the website display only and called the `Gaiad/genealogy/` files junk. On
Emma's order ch 1-70 were restored to their 2026-10-13 18:00 state; ch 71-364 still carry that day's changes,
and the queue's damage review covers them.

## Every character tag carries its legacy number (2026-10-29)

Emma, 2026-10-29: "The idea is that we mass apply the existing numbers into the templates so that they become
stable". `Gaiad/scripts/stamp_legacy_ids.py` turned every `{{c|Name}}` into the ID form `{{c|N|Name}}`, where N is
that name's own Gaiad legacy number (`wikibase/analysis/gaiad_legacy_numbers.tsv`): `{{c|1|Aster}}`, `{{c|4|Alpha}}`.
Merges are applied after, in the GEDCOM generation, from `wikibase/analysis/gaiad_legacy_merges.tsv` (4 into 1).
Emma: "Aster is 1 and Alpha is 4. The fact that 1 and 4 get merged after is the point." A newly tagged name is
written `{{c|Name}}`; run the stamp script to give it a number. Every reader of the tags accepts the ID form.
