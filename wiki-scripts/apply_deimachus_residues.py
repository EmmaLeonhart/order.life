"""Queue item 6: the two claims the 2026-08-01 Deimachus unmerge could not write.

1. Q200002 (Deimachus son of Neleus) gets his mother Q133062 Chloris, on both sides of the edge.
   Wikidata Q1183222 "son of Neleus" has mother Q28122362 Chloris = dump Q133062 (checked 2026-10-10).
2. The Wikidata id Q1183222 moves from Q75123 to Q200002. Q75123 keeps Q1183226. Leaving both ids on
   Q75123 invited a later re-merge, since a doubled id is how the defect was found.

Shadow-aware (every file claiming Q75123, Q200002 or Q133062). Idempotent; dry run unless --write;
verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"
DEIMACHUS, OTHER, CHLORIS, WD = "Q200002", "Q75123", "Q133062", "Q1183222"


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
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]

    wd_claim = next((c for c in load(OTHER)["claims"].get("P61", [])
                     if c["mainsnak"]["datavalue"]["value"] == WD), None)
    staged, log = {}, []
    get = lambda s: staged.setdefault(s, load(s))
    for s in fam(DEIMACHUS):
        d = get(s)
        if CHLORIS not in values(d, "P48"):
            d.setdefault("claims", {}).setdefault("P48", []).append(entity_claim("P48", CHLORIS)); log.append(f"{s}: + mother {CHLORIS}")
        if WD not in values(d, "P61"):
            if wd_claim is None: sys.exit(f"ABORT: {WD} is on neither {OTHER} nor {DEIMACHUS}")
            d["claims"].setdefault("P61", []).append(json.loads(json.dumps(wd_claim))); log.append(f"{s}: + wikidata {WD}")
    for s in fam(CHLORIS):
        d = get(s)
        if DEIMACHUS not in values(d, "P20"):
            d.setdefault("claims", {}).setdefault("P20", []).append(entity_claim("P20", DEIMACHUS)); log.append(f"{s}: + child {DEIMACHUS}")
    for s in fam(OTHER):
        d = get(s)
        if WD in values(d, "P61"):
            d["claims"]["P61"] = [c for c in d["claims"]["P61"] if c["mainsnak"]["datavalue"]["value"] != WD]
            log.append(f"{s}: - wikidata {WD}")
    print("\n".join(log) or "nothing to do")
    if not write or not log:
        print("(dry run; --write to apply)" if log else ""); return 0
    for s in {l.split(":")[0] for l in log}: save(s, staged[s])

    bad = [s for s in fam(DEIMACHUS) if CHLORIS not in values(load(s), "P48") or WD not in values(load(s), "P61")]
    bad += [s for s in fam(CHLORIS) if DEIMACHUS not in values(load(s), "P20")]
    bad += [s for s in fam(OTHER) if WD in values(load(s), "P61") or values(load(s), "P61") != ["Q1183226"]]
    print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
