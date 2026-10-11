"""Queue item 16: Q130001 carries the labels and identifiers of Georg Friedrich of
Hohenlohe-Neuenstein-Weikersheim (wd Q96124, a 17th-century Bohemian count), written over it by the
2026-04-15 Wikibase fill. Its genealogy is mythic: female, mother Tethys Q74970, husband Melissus of
Crete Q130666, child Adrasteia Q130057. So the count's terms and ids are removed (labels and aliases
in every language, P61 Q96124, WikiTree P2949, Rodovid P1185, the arms file P94), and the record is
labelled by the dump's convention for an unnamed wife. Her edges are not touched.

Every file claiming Q130001. Idempotent; dry run unless --write; verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"
Q = "Q130001"
LABEL = "NN (Wife of Melissus of Crete)"
DESC = ("daughter of Tethys, wife of Melissus of Crete and mother of Adrasteia. The labels and "
        "identifiers of Georg Friedrich of Hohenlohe-Neuenstein-Weikersheim (wd Q96124), written over "
        "this record by an import, were removed on 2026-10-10")
DROP_PROPS = ("P61", "P2949", "P1185", "P94")


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    files = [s for s in sorted(sib.get(Q, set()) | {Q}, key=lambda x: int(x[1:]))
             if (d := load(s)) is not None and (d.get("id") or s) == Q]
    want = lambda d: (d.get("labels") == {"en": {"language": "en", "value": LABEL}}
                      and not d.get("aliases") and not any(p in d.get("claims", {}) for p in DROP_PROPS))
    n = 0
    for s in files:
        d = load(s)
        if want(d): continue
        n += 1; print(f"  {s}: replace terms, drop {', '.join(p for p in DROP_PROPS if p in d.get('claims', {}))}")
        if write:
            d["labels"] = {"en": {"language": "en", "value": LABEL}}
            d["aliases"] = {}
            d["descriptions"] = {"en": {"language": "en", "value": DESC}}
            for p in DROP_PROPS: d.get("claims", {}).pop(p, None)
            save(s, d)
    print(f"{n} file(s){'' if write else ' (dry run; --write to apply)'}")
    if write:
        bad = [s for s in files if not want(load(s))]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
