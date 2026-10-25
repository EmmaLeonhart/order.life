"""Which zh, ja and ko labels in labels.tsv are the record's own name, checked against Wikidata.

The damaged-labels sweep (2026-10-25, wikibase/analysis/damaged_labels.tsv) found records whose labels in every
language had been copied from the wrong Wikidata item (Trajan "Andhra Pradesh"). The Chinese, Japanese and
Korean lineage phrases in export_gedcom7.py (Y之子X and the like) put two such labels together, so they were
withdrawn until labels could be trusted. This writes wikibase/analysis/cjk_labels_verified.tsv: a zh, ja or ko
label is kept only where it equals a label, in that language, of the Wikidata item the record carries (P61).
Records with no Wikidata id get no verified label.

The Wikidata labels come from an index of the local dump (parent repo, wikidata-fresh/), one line per item:
wikidata id, zh labels (zh, zh-hans, zh-hant, zh-cn, zh-tw, zh-hk; "|"-separated), ja, ko.

    python wiki-scripts/verify_cjk_labels.py <index.tsv>
"""

import csv
import sys
from pathlib import Path

A = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"


def main():
    wd = {}
    with open(sys.argv[1], encoding="utf-8") as fh:
        for line in fh:
            q, zh, ja, ko = line.rstrip("\n").split("\t")
            wd[q] = {"zh": set(filter(None, zh.split("|"))), "ja": set(filter(None, ja.split("|"))),
                     "ko": set(filter(None, ko.split("|")))}
    p61 = {}
    with open(A / "persons.tsv", encoding="utf-8", newline="") as fh:
        for r in csv.reader(fh, delimiter="\t"):
            if len(r) > 6 and r[6].startswith("Q"):
                p61[r[0]] = r[6]
    kept = checked = 0
    with open(A / "labels.tsv", encoding="utf-8", newline="") as fh, \
            open(A / "cjk_labels_verified.tsv", "w", encoding="utf-8", newline="") as out:
        out.write("qid\tlang\tlabel\n")
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["lang"] not in ("zh", "ja", "ko"):
                continue
            checked += 1
            item = wd.get(p61.get(r["qid"], ""))
            if item and r["label"] in item[r["lang"]]:
                out.write(f"{r['qid']}\t{r['lang']}\t{r['label']}\n")
                kept += 1
    print(f"{kept} of {checked} zh/ja/ko labels match the Wikidata item's own label")


if __name__ == "__main__":
    main()
