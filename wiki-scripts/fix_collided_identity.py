"""Strip a wrong identity that an import wrote over a record, and give it its own.

The 2026-04-15 Wikibase fill wrote the labels, aliases, descriptions and external ids of unrelated
(mostly modern German) people over some mythic records, while their family claims stayed right:
Q130001 got a 17th-century count, Mnemosyne got a tennis player, Urania a secretary. This replaces
the terms (labels and aliases in every language, description) and removes the collided external ids
(P61 Wikidata, P2949 WikiTree, P1185 Rodovid, P94 arms file, P62 Geni, P535 Find a Grave), then sets
the right Wikidata id if one is given. Family claims are not touched.

    python wiki-scripts/fix_collided_identity.py Q130458 "Mnemosyne" "titaness of memory, mother of the Muses" Q132302
    ... --write to apply. Give "-" for no Wikidata id.

Identify the record from its edges and look the id up on Wikidata first; say why in the commit and
devlog. Shadow-aware (redirects.tsv); idempotent; verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"
DROP = ("P61", "P2949", "P1185", "P94", "P62", "P535")


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def target(q, label, desc, wd):
    def apply(d):
        d["labels"] = {"en": {"language": "en", "value": label}}
        d["aliases"] = {}
        d["descriptions"] = {"en": {"language": "en", "value": desc}}
        for p in DROP: d.setdefault("claims", {}).pop(p, None)
        if wd != "-":
            d["claims"]["P61"] = [{"mainsnak": {"snaktype": "value", "property": "P61",
                                                "datavalue": {"value": wd, "type": "string"}},
                                   "type": "statement", "rank": "normal"}]
        return d
    return apply


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--write"]
    if len(args) != 4:
        print(__doc__); return 1
    q, label, desc, wd = args
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    files = [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
             if (d := load(s)) is not None and (d.get("id") or s) == q]
    if not files: print(f"ABORT: no file claims {q}"); return 1
    fix = target(q, label, desc, wd)
    n = 0
    for s in files:
        d = load(s)
        new = fix(json.loads(json.dumps(d)))
        if new == d: continue
        old = (d.get("labels") or {}).get("en", {}).get("value")
        print(f"  {s}: {old!r} -> {label!r}; drop {', '.join(p for p in DROP if p in d.get('claims', {}))}")
        n += 1
        if write: save(s, new)
    print(f"{n} file(s){'' if write else ' (dry run; --write to apply)'}")
    if write:
        bad = [s for s in files if fix(json.loads(json.dumps(load(s)))) != load(s)]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
