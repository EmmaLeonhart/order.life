"""Queue item 16, apply step: add the missing side of every CONFIRMED row in one_sided_proposed.tsv
(the pair is recorded on Wikidata). Graph-neutral: extract_genealogy.py already builds each edge
from whichever side declares it; this makes the record say it on both sides.

  child-only  -> the parent gets P20 (child)
  parent-only -> the child gets P47 (father) if the parent's P55 is male, P48 (mother) if female;
                 skipped and counted if the parent has no sex, since nothing decides the property

Every file claiming the record (shadows via redirects.tsv). Idempotent; dry run unless --write;
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
MALE, FEMALE = "Q153718", "Q153719"


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def values(data, pid):
    out = []
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid, "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(AN / "redirects.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    alias = lambda q: set(fam(q)) | {q}
    with open(AN / "one_sided_proposed.tsv", encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if r["verdict"] == "CONFIRMED"]
    print(f"{len(rows)} CONFIRMED edges")

    plan, skipped = [], 0   # (record, pid, value)
    for r in rows:
        p, c = r["parent"], r["child"]
        if r["side"] == "child-only":
            plan.append((p, "P20", c))
        else:
            sex = (values(load(fam(p)[0]), "P55") or [None])[0] if fam(p) else None
            if sex not in (MALE, FEMALE): skipped += 1; continue
            plan.append((c, "P47" if sex == MALE else "P48", p))

    staged, n = {}, 0
    for rec, pid, v in plan:
        for s in fam(rec):
            d = staged.setdefault(s, load(s))
            if alias(v) & set(values(d, pid)): continue
            d.setdefault("claims", {}).setdefault(pid, []).append(entity_claim(pid, v)); n += 1
    touched = {s for s, d in staged.items() if d != load(s)}
    print(f"{n} claim(s) to add in {len(touched)} file(s); {skipped} skipped (parent has no sex)"
          f"{'' if write else ' (dry run; --write to apply)'}")
    if not write: return 0
    for s in touched: save(s, staged[s])
    bad = [f"{s} {pid} {v}" for rec, pid, v in plan for s in fam(rec) if not alias(v) & set(values(load(s), pid))]
    print("VERIFY FAILED: " + ", ".join(bad[:10]) if bad else "verified from disk")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
