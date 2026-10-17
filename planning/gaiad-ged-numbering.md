# Numbering in Gaiad.ged: individuals I1, I2, I3 ... and families F1, F2 ...

From Emma's message of 2026-10-14 about 20:50 (verbatim in the parent repo,
`data_lake/emma-message_2026-10-14_gaiad-ged-numbering.md`). Written 2026-10-15 as a spec for
`wiki-scripts/export_gedcom7.py`. Where the dictated message is open to more than one reading, the
reading taken is marked, and the question is listed at the end for her.

## Why

> "I want there to be a relatively stable ordering of this, and ordering stuff like this makes it so that
> related people are close to each other in any kind of export ... a lot of GEDCOM merging programs preserve
> ordering too, even if they get rid of things like reference numbers."

So the numbers are the order records are written in, and the same numbers are the xref (`@I1@`) and the
`REFN`. "Yes this has some odd properties, no I don't care these are the REFN of everything in Gaiad.ged
and the individual number." Every person also keeps their permanent identity: the `UID` (UUIDv5 of the
order.life QID) and the `EXID` carrying the QID stay as they are, so matching back never depends on the
numbers.

## Individuals

1. **I1 Aster, I2 Emma Leonhart, I3 Andromeda.** ("12=Emma Leonhart" in the message is I2, typed.)
2. **Then everyone in order of first appearance in the Gaiad**, chapter 1 onward, the order their tags
   first occur: "Afterwards individuals go in order of showing up in the Gaiad. Just to the end."
3. **Then everyone else, in the order the family walk below reaches them.** Her final word replaces the
   earlier "ahnentafel, then descendants" and the "spouses not in the Gaiad" pass: "Yeah, no, actually,
   no, family search style algorithm altogether."

## Families, and the walk that numbers the rest

For each person in individual order (I1, I2, I3, then the Gaiad appearances): add their **spouse
family** first, then their **parents' family**, then **both grandparents' families**, and so on upward.
Within each family, members are taken **father, then mother, then the children oldest to youngest**; a
person not yet numbered gets the next I-number when the walk reaches them, and each family the next
F-number. Her worked example for herself (unmarried): F2 is her parents' family, numbered father,
mother, Emma, her brother; then her paternal grandfather's family, then her father's parents'...,
then her mother's parents' family.

*Reading taken:* "and so on" means the walk climbs one generation at a time for each person, paternal
side before maternal, before moving to the next person in individual order; descendants are reached as
children of the families walked. People the walk never reaches (no link to any numbered person) come
last, by order.life QID.

**F1 = Aster + Andromeda.**

## When

**Applied 2026-10-17** in `wiki-scripts/build_gaiad_ged.py` (`walk_numbering`), which builds `/gaiad.ged` (the
Gaiad's text block plus her ancestry, not `export_gedcom7.py`). I1-I3 and the text block keep their numbers; the
walk starts at I1 and runs through every person in number order, the ones it numbers included, so it reaches
everyone joined to Aster, Emma or Andromeda. Each family's ancestry is climbed once. People it never reaches follow
in the ancestry file's order (that file carries no QID for most of them). Children are numbered by birth year where
a BIRT DATE gives one; undated children keep their place in the CHIL list, and the CHIL lines themselves stay in the
source order. Every ancestry person now has `REFN <n>` with `TYPE Gaiad individual number`, and records are written
in number order. Result: F1 Aster + Andromeda + Benzette (I4726); F2 her parents' family (I4727 father,
I4728 mother, I2 Emma, I4729 her brother); F3 her paternal grandparents' family.

The paragraph below was the plan before; the text block is still unresolved, so its tags have no links yet.

Order of first appearance needs every chapter tag resolved to a person, which is the entity-resolution
work at the end of the parent repo's queue (today only 7 genealogy files carry an id). Numbering before
that would renumber everyone later and break the stability that is the point, so this is applied
together with entity resolution, not before. The round-trip checker (`check_gedcom_roundtrip.py`)
already matches people by UID, EXID and NOTE, so moving `REFN` from the QID to the I-number loses
nothing.

## Questions for Emma

- Spouses who are not in the Gaiad: her first idea was a pass of them right after the Gaiad appearances;
  the FamilySearch walk then reaches them anyway, as spouse families. Taken: the walk replaces the pass.
- Within the walk, does each person's whole ancestry come before the next person's, or one generation for
  everyone at a time? Taken: each person's line in turn, which keeps a person's ancestors together.
- Her brother and parents in a public file: her real parents are placeholders ("Father", "Mother") in
  order.life today, and the published GEDCOM shows only those. Taken: placeholders stay unless she adds
  them.
