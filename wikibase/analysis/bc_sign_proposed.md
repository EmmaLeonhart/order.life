# BC dates stored as positive years: the one-date records (queue item 0b), 2026-10-10

`death < birth` catches a BC record stored with `+` signs only when it has both dates. This checks
the ones it cannot see: records with exactly one date, that date not negative, and a Wikidata id.
Script: `wiki-scripts/propose_bc_signs.py` (Wikidata answers cached in `wd_dates_cache.json`).
Rows: `bc_sign_proposed.tsv`. **Nothing in `wikibase/items/` has been changed.**

| verdict | records | meaning |
|---|---:|---|
| **FLIP** | **749** | Wikidata has the same field as BC, same year within 1: the sign should be `-` |
| AD | 10,382 | Wikidata has it as AD, same year within 1: the dump is right |
| MISMATCH | 59 | Wikidata has the field with another year; 10 of them are BC on Wikidata with a different year (e.g. `Q2086` Bhagabhadra, dump +0083, Wikidata 100 BC) |
| NO_WD_DATE | 33 | Wikidata lacks the field |
| WD_MISSING | 0 | |
| **total** | **11,223** | the count the queue item predicted on 2026-08-05 |

The item's own example is in the FLIP set: `Q2175` Agnimitra, stored `+0141`, Wikidata 141 BC.
Spot-checked FLIPs: Ptolemy Philadelphus (36 BC), Cyrus I (d. 580 BC), the Zhou-era dukes of Qi and
Lu, Eunoë, Aryeong (b. 100 BC). All are BC.

**Proposed repair:** flip the sign of the one date on each of the 749 FLIP records, in every shadow
file, and keep the year as it is (Wikidata agrees on it). The 59 mismatches and 33 without a date are
left alone: their years need a source each, and the item rules out bulk sign-flipping by heuristic.
