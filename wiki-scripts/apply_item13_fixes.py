"""Queue item 13's two small defects (2026-10-10):

1. 37 records carry sex P55 = Q1. Q1 is Aster, not a sex: an import error (Japanese kami and
   sukune, e.g. Futsunushi, Ii Yoshinao). The claim is removed, leaving the sex unrecorded rather
   than guessed.
2. Q74677 Ops carries Wikidata id Q96761, which is "Paul Bildt", a German actor. Removed; its other
   id, Q859392 Ops, stays.

Every file claiming each record (shadows via redirects.tsv). Idempotent; dry run unless --write;
verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
AN = ROOT / "wikibase" / "analysis"


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def value(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else v


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(AN / "redirects.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    with open(AN / "persons.tsv", encoding="utf-8", newline="") as f:
        bad_sex = [r["qid"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if r["sex"] == "Q1"]
    drops = [(q, "P55", "Q1") for q in bad_sex] + [("Q74677", "P61", "Q96761")]
    print(f"{len(bad_sex)} records with sex = Q1")

    n, touched = 0, []
    for q, pid, v in drops:
        for s in fam(q):
            d = load(s)
            cl = (d.get("claims") or {}).get(pid, [])
            keep = [c for c in cl if value(c) != v]
            if len(keep) == len(cl): continue
            n += 1; touched.append((s, pid, v))
            if write:
                if keep: d["claims"][pid] = keep
                else: del d["claims"][pid]
                save(s, d)
    print(f"{n} file edit(s){'' if write else ' (dry run; --write to apply)'}")
    if write:
        bad = [f"{s} {pid}" for s, pid, v in touched if any(value(c) == v for c in (load(s).get("claims") or {}).get(pid, []))]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
