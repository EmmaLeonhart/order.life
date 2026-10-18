"""
Write wikibase/analysis/wikidata_primary_names.tsv: for every person in Emma's ancestry with a Wikidata id, the
item's English label (or mul) and the label of its family name (P734). build_gaiad_ged.py makes that label the
primary NAME, with the P734 surname marked (Emma, 2026-10-17: "Wikidata generally gives the better name ... Wikidata
itself oftentimes contains the surname too ... it links to a surname object").

The labels and P734 come from the caches synoptic/wikidata_names.py writes from the Wikidata store
(wikidata-fresh/out/wikidata/labels.tsv, p734.tsv; research/wikidata-family-name-labels.tsv). Run here; the site
build reads the TSV.

    python wiki-scripts/make_wikidata_primary_names.py
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARENT = ROOT.parent
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "emma-ancestry.ged"
LABELS = PARENT / "wikidata-fresh" / "out" / "wikidata" / "labels.tsv"
P734 = PARENT / "wikidata-fresh" / "out" / "wikidata" / "p734.tsv"
SURNAMES = PARENT / "research" / "wikidata-family-name-labels.tsv"
OUT = ROOT / "wikibase" / "analysis" / "wikidata_primary_names.tsv"
csv.field_size_limit(10 ** 8)


def main():
    want = set()
    for line in ANCESTRY.read_text(encoding="utf-8-sig").splitlines():
        m = re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", line)
        if m:
            want.add(m.group(1))
    labels = {}
    with open(LABELS, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["qid"] in want:
                labels[r["qid"]] = (r.get("en") or r.get("mul") or "").strip()
    fam = {}
    with open(P734, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["qid"] in want:
                fam.setdefault(r["qid"], r["p734"])
    sur = {}
    with open(SURNAMES, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sur[r["qid"]] = r["label"]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("qid\tlabel\tfamily_name\n")
        for q in sorted(want):
            lb = labels.get(q, "")
            if lb:
                f.write(f"{q}\t{lb}\t{sur.get(fam.get(q, ''), '')}\n")
    print(f"{len(want)} Wikidata ids in the ancestry, {sum(1 for q in want if labels.get(q))} with a label -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
