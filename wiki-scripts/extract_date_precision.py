"""
Pull the precision qualifier off every birth/death claim into date_precision.tsv.

persons.tsv keeps only the timestamp, so a year-precision date arrives looking like
"+0594-01-01T00:00:00Z" and any consumer renders it as 1 January. In a 400-record
sample, 211 of 609 dates were year-precision -- so roughly a third of the dates in the
export would otherwise assert a day the dump never claimed.

Reads only the ~20k item files that persons.tsv says have a date, not the whole dump.
Writes via temp-file-and-rename with a row-count assertion, so a partial run cannot
masquerade as a complete one (see commit 91caa7f).

Run:  python wiki-scripts/extract_date_precision.py
"""
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANA = REPO / "wikibase" / "analysis"
ITEMS = REPO / "wikibase" / "items"
OUT = ANA / "date_precision.tsv"

P_BIRTH = "P56"
P_DEATH = "P57"


def precision_of(claims, prop):
    for claim in claims.get(prop, []):
        try:
            mainsnak = claim["mainsnak"]
            if mainsnak.get("snaktype") != "value":
                continue
            return str(mainsnak["datavalue"]["value"]["precision"])
        except (KeyError, TypeError):
            continue
    return ""


def main():
    wanted = []
    with open(ANA / "persons.tsv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if row.get("birth") or row.get("death"):
                wanted.append(row["qid"])

    print(f"{len(wanted):,} persons carry a birth or death date", flush=True)

    rows = []
    missing = 0
    for i, qid in enumerate(wanted, 1):
        path = ITEMS / f"{qid}.json"
        if not path.exists():
            missing += 1
            continue
        try:
            with open(path, encoding="utf-8") as f:
                claims = json.load(f).get("claims", {})
        except (OSError, ValueError):
            missing += 1
            continue
        b = precision_of(claims, P_BIRTH)
        d = precision_of(claims, P_DEATH)
        if b or d:
            rows.append((qid, b, d))
        if i % 5000 == 0:
            print(f"  {i:,}/{len(wanted):,}", flush=True)

    if len(rows) < len(wanted) * 0.8:
        sys.exit(f"ABORT: only {len(rows):,} of {len(wanted):,} resolved -- run looks partial")

    tmp = OUT.with_suffix(".tsv.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write("qid\tbirth_precision\tdeath_precision\n")
        for qid, b, d in rows:
            f.write(f"{qid}\t{b}\t{d}\n")
    tmp.replace(OUT)

    print(f"Wrote {OUT}: {len(rows):,} rows ({missing:,} items unreadable)")


if __name__ == "__main__":
    main()
