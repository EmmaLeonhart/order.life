"""Replace a wrong Wikidata id (P61) on a record with the right one, in every file claiming it.

    python wiki-scripts/fix_wikidata_ids.py Q74973:Q161419:Q210883            # dry run
    python wiki-scripts/fix_wikidata_ids.py Q74973:Q161419:Q210883 --write    # apply

Each argument is record:wrong:right. Give right as "-" to only remove the wrong id. Look the right
id up on Wikidata first and say why in the commit and devlog; this tool keeps no list of its own.
Shadow-aware (redirects.tsv); idempotent; verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def ids(data):
    return [((c.get("mainsnak") or {}).get("datavalue") or {}).get("value") for c in (data.get("claims") or {}).get("P61", [])]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    fixes = [a.split(":") for a in sys.argv[1:] if not a.startswith("--")]
    if not fixes or any(len(f) != 3 for f in fixes):
        print(__doc__); return 1
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    done = []
    for rec, wrong, right in fixes:
        if not fam(rec): print(f"ABORT: no file claims {rec}"); return 1
        for s in fam(rec):
            d = load(s)
            have = ids(d)
            if wrong not in have and (right == "-" or right in have): continue
            cl = [c for c in d["claims"].get("P61", []) if c["mainsnak"]["datavalue"]["value"] != wrong]
            if right != "-" and right not in have:
                cl.append({"mainsnak": {"snaktype": "value", "property": "P61",
                                        "datavalue": {"value": right, "type": "string"}},
                           "type": "statement", "rank": "normal"})
            print(f"  {s} ({rec}): {wrong} -> {right}")
            done.append((s, wrong, right))
            if write:
                if cl: d["claims"]["P61"] = cl
                else: del d["claims"]["P61"]
                save(s, d)
    print(f"{len(done)} file edit(s){'' if write else ' (dry run; --write to apply)'}")
    if write:
        bad = [s for s, wrong, right in done if wrong in ids(load(s)) or (right != "-" and right not in ids(load(s)))]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
