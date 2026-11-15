"""
Write wikibase/analysis/wikidata_external_ids.tsv: for every person in Emma's ancestry with a Wikidata id, every
external id on that Wikidata item (property, value). build_gaiad_ged.py writes each as its own EXID (Emma,
2026-11-15: "all the external ids on wikidata are over exids"), TYPE http://www.wikidata.org/entity/Pnnn (the property
as the authority).

FamilySearch (P2889) and Geni (P2600) are left out: those are already EXIDs with their own TYPE.

Source: the local Wikidata item store, wikidata-fresh/items/items-*.jsonl.gz (full items, October 2026). Run here;
the site build reads the TSV.

    python wiki-scripts/make_wikidata_external_ids.py
"""
import gzip
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARENT = ROOT.parent
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "emma-ancestry.ged"
ITEMS = PARENT / "wikidata-fresh" / "items"
OUT = ROOT / "wikibase" / "analysis" / "wikidata_external_ids.tsv"
SKIP = {"P2889", "P2600"}
TITLE = re.compile(r'"title":\s*"(Q\d+)"')


def main():
    want = set()
    for line in ANCESTRY.read_text(encoding="utf-8-sig").splitlines():
        m = re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", line)
        if m:
            want.add(m.group(1))
    rows, found = [], set()
    files = sorted(ITEMS.glob("items-*.jsonl.gz"))
    for k, path in enumerate(files):
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                m = TITLE.search(line, 0, 300)
                if not m or m.group(1) not in want:
                    continue
                d = json.loads(line)
                q = d["id"]
                found.add(q)
                for pid, claims in d.get("claims", {}).items():
                    if pid in SKIP:
                        continue
                    for c in claims:
                        s = c.get("mainsnak", {})
                        if s.get("datatype") != "external-id" or s.get("snaktype") != "value":
                            continue
                        if c.get("rank") == "deprecated":
                            continue
                        v = str(s["datavalue"]["value"]).replace("\t", " ").replace("\n", " ").strip()
                        if v:
                            rows.append((q, pid, v))
        if k % 200 == 0:
            print(f"{k}/{len(files)} files, {len(found)} items found", flush=True)
    rows = sorted(set(rows), key=lambda r: (int(r[0][1:]), int(r[1][1:]), r[2]))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("qid\tproperty\tvalue\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"{len(want)} Wikidata ids in the ancestry, {len(found)} in the store, {len(rows)} external ids -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
