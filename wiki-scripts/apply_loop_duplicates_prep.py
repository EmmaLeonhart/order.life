"""Queue item 7, step 1 of 2: remove the two false edges that merging the loop-work duplicates would
otherwise carry onto the survivors. Step 2 is `merge_cluster.py loop-duplicates`.

1. Q104369 Leocadia de Castro -> Q104371 "Arsende de Cabrera" (mother). Q104371 is a duplicate of
   Q118293 Arsenda de Cabrera, whose mothers on Wikidata (Q21126905) are Q19289994 Berenguera de
   Queralt (= dump Q123448, already her mother) and Q111457114 Sancha; no Leocadia. Two biological
   mothers is the ordinary error. Leocadia has no parents of her own, so no ancestry is lost.
2. Q78264 Lucius Pinarius <-> Q78267 "Julia Caesaris Major" (spouse). Q78267 has the same parents as
   Q137708 Julia Major, Lucius's own mother, and is merged into her in step 2; kept, the marriage would
   make him his mother's husband.

Both sides of each edge, in every file claiming either record. Idempotent; dry run unless --write.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

# (record, property on it, the other record)
DROP = [("Q104371", "P48", "Q104369"), ("Q104369", "P20", "Q104371"),
        ("Q78264", "P42", "Q78267"), ("Q78267", "P42", "Q78264")]


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def target(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    alias = lambda q: set(fam(q)) | {q}
    n, bad = 0, []
    for rec, pid, other in DROP:
        for s in fam(rec):
            d = load(s)
            cl = (d.get("claims") or {}).get(pid, [])
            keep = [c for c in cl if target(c) not in alias(other)]
            if len(keep) == len(cl): continue
            n += 1; print(f"  {s} ({rec}): drop {pid} {other}")
            if write:
                if keep: d["claims"][pid] = keep
                else: del d["claims"][pid]
                save(s, d)
    print(f"{n} file edit(s){'' if write else ' (dry run; --write to apply)'}")
    if write:
        for rec, pid, other in DROP:
            for s in fam(rec):
                if any(target(c) in alias(other) for c in (load(s).get("claims") or {}).get(pid, [])):
                    bad.append(f"{s} {pid} {other}")
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
