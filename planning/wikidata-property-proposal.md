# Draft: a Wikidata property for order.life person IDs

Emma, 2026-10-12 21:46: "I feel like I can probably make my own external identifier system wikidata imports
from at this rate of what I do." This is a draft for her to file at
<https://www.wikidata.org/wiki/Wikidata:Property_proposal/Authority_control> if she wants to. **Nothing is posted
to Wikidata by an agent.** Drafted 2026-10-15.

## The proposal, in the form Wikidata asks for

- **Label (en):** order.life person ID
- **Description (en):** identifier for a person in the order.life genealogy, the synoptic family tree published
  with the Gaiad
- **Data type:** External identifier
- **Domain:** human (Q5), and legendary or mythical figures who appear in genealogies
- **Allowed values:** `Q[1-9]\d*` (the order.life wikibase item number)
- **Example 1:** Muhammad (Q9458) → `Q65705`
- **Example 2:** Confucius (Q4604) → `Q30266`
- **Example 3:** Genghis Khan (Q720) → `Q37401`
- **Formatter URL:** `https://order.life/wikibase/entity/$1`
- **Source:** <https://order.life/gaiad.ged> (GEDCOM 7, 106,786 people; every record carries its order.life ID as an
  EXID and its Wikidata ID where known)
- **Number of IDs in source:** 106,786, of which about 60,000 already carry a Wikidata ID (so a matching tool can
  add most statements at once)
- **Expected completeness:** never complete (a growing genealogy)
- **Mix'n'match:** a catalogue can be made from `wikibase/analysis/persons.tsv` (order.life ID, label, Wikidata ID)

## Motivation (for her to write in her own words)

Points she might make: the IDs are stable (each also has a permanent UUID in the GEDCOM); the tree links people
across traditions; the Wikidata IDs already in it make the mapping two-way. Wikidata reviewers usually ask whether
the source is notable or independent; that is a judgement for her.

## Before filing

- The formatter URL resolves since 2026-10-15: `/wikibase/entity/Q<n>` shows each person's record (label, dates,
  parents, children, links) from the site's entity index (`wiki-scripts/entity_index.py`, read by `404.html`).
  Pages served this way return HTTP 404 with the record drawn by script, which some checkers dislike; a static page
  per person would avoid that at the cost of about 106,786 more pages in the build.
- The three examples are taken from `persons.tsv`, where each record carries that Wikidata ID.
