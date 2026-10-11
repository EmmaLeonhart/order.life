"""Remove specific claims (record, property, value) from every file claiming the record.

    python wiki-scripts/drop_claims.py Q102901:P42:Q123443 Q123443:P42:Q102901           # dry run
    python wiki-scripts/drop_claims.py Q102901:P42:Q123443 Q123443:P42:Q102901 --write   # apply

For one-off false claims that are not parent edges (cut_edges.py handles those, both sides at once):
spouses, wrong Wikidata ids, bogus values. Give both sides of a relationship explicitly. A value is
matched against an item id or a plain string. Shadow-aware (redirects.tsv); idempotent; verifies
from disk. Say why in the commit and devlog; this tool keeps no list of its own.
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


def value(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else v


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    triples = [a.split(":") for a in sys.argv[1:] if not a.startswith("--")]
    if not triples or any(len(t) != 3 for t in triples):
        print(__doc__); return 1
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    touched = []
    for rec, pid, v in triples:
        files = fam(rec)
        if not files: print(f"ABORT: no file claims {rec}"); return 1
        for s in files:
            d = load(s)
            cl = (d.get("claims") or {}).get(pid, [])
            keep = [c for c in cl if value(c) != v]
            if len(keep) == len(cl): continue
            print(f"  {s} ({rec}): drop {pid} {v}")
            touched.append((s, pid, v))
            if write:
                if keep: d["claims"][pid] = keep
                else: del d["claims"][pid]
                save(s, d)
    print(f"{len(touched)} file edit(s){'' if write else ' (dry run; --write to apply)'}")
    if write:
        bad = [f"{s} {pid} {v}" for s, pid, v in touched
               if any(value(c) == v for c in (load(s).get("claims") or {}).get(pid, []))]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
