# Entity resolution: each tagged name in the Gaiad to a person in the genealogy

Emma, 2026-10-14: regenerate the genealogy files from the chapters' tags, then "link each person to their
record and their parents and children, turning them into the actual vision": each person's genealogy file
citing the Gaiad chapters and quotes they appear in, feeding the GEDCOM and the Loka database. Read
`Gaiad/TAGS.md` first: tags are data and are never changed. Plan written 2026-10-15.

## Why not just rerun extract_characters.py

The parent repo's `research/tagging-damage.md`: rerun as it is, it would wipe the 7 Wikidata ids the files
carry and merge different people into 26 existing files through 105 tags added on 2026-10-14 (God, Christ,
William, Peter ...), because it keys a file on the bare name. So the files are rebuilt from a resolution
step that keys on the person, not the name.

## What the tags give (measured 2026-10-15)

4,794 distinct `{{c|}}` names. Against `wikibase/analysis/persons.tsv` (labels and gedcom names): 1,022
match exactly one person, 350 match several (Aster ×2, Andromeda ×4, Viros ×3 ...), 3,422 match none
(tagged common words such as Now and Throughout, the Gaiad's coinages without a record yet, and people whose
record carries a longer label).

## Steps

1. **Resolve, changing nothing.** `Gaiad/scripts/resolve_characters.py` reads every tag occurrence (chapter,
   stanza, name) and writes `Gaiad/genealogy/_resolution.tsv`: the QID chosen and how. Methods, in order:
   - the QID an existing genealogy file already carries (the 7);
   - a unique label match;
   - among several matches, the candidate linked in `edges.tsv`/`spouses.tsv` (parent, child, spouse,
     within two steps) to the most other names resolved in the same chapter: the story's context decides;
   - otherwise unresolved, listed with its candidates.
   No tag and no genealogy file is touched.
2. **Check.** Sample each method; count; list the ambiguous ones the context could not settle.
3. **Regenerate the files** from the resolution: one file per person (keyed by QID, keeping each existing file
   name so `/gaiad/characters/<name>/` URLs stay), carrying the order.life QID and Wikidata id, father,
   mother, spouses and children from the graph, and every citation as Gaiad chapter.stanza with its line.
   Names that resolve to no person still keep a file with their citations (nothing that has a page loses
   it); tagged common words with no person behind them are listed, not given new files.
4. **Pages:** the character pages cite stanzas as `/gaiad/NNN/#sS` links.
5. **GEDCOM:** the numbering in `planning/gaiad-ged-numbering.md` (appearance order now known) and a source
   citation per person for each stanza.
