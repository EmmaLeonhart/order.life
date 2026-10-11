"""Queue item 0b, apply step: make the one date negative on the 749 FLIP rows of
wikibase/analysis/bc_sign_proposed.tsv (BC on Wikidata, same year; see bc_sign_proposed.md).

Only the sign changes; the year, month, day and precision stay as stored. Every file claiming the
qid (the record and its shadows, via redirects.tsv) gets the same edit. Idempotent; dry run unless
--write; verifies from disk afterwards.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
AN = ROOT / "wikibase" / "analysis"
PROP = {"birth": "P56", "death": "P57"}


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    (ITEMS / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(AN / "redirects.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    with open(AN / "bc_sign_proposed.tsv", encoding="utf-8", newline="") as f:
        flips = [r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if r["verdict"] == "FLIP"]
    print(f"{len(flips)} FLIP rows")

    files = changed = already = 0
    touched = []
    for r in flips:
        q, pid, year = r["qid"], PROP[r["field"]], r["dump_value"].lstrip("+-").split("-")[0]
        for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:])):
            d = load(s)
            if d is None or (d.get("id") or s) != q: continue
            hit = False
            for c in (d.get("claims") or {}).get(pid, []):
                v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                if not isinstance(v, dict) or "time" not in v: continue
                t = v["time"]
                if t.lstrip("+-").split("-")[0] != year: continue
                if t.startswith("-"): already += 1; continue
                v["time"] = "-" + t.lstrip("+"); hit = True; changed += 1
            if hit:
                files += 1; touched.append((s, q, pid, year))
                if write: save(s, d)
    print(f"{changed} date(s) flipped in {files} file(s); {already} already negative"
          f"{'' if write else ' (dry run; --write to apply)'}")
    if write:
        bad = []
        for s, q, pid, year in touched:
            for c in load(s)["claims"][pid]:
                t = c["mainsnak"]["datavalue"]["value"]["time"]
                if t.lstrip("+-").split("-")[0] == year and not t.startswith("-"): bad.append(f"{s} ({q}) {pid} {t}")
        print("VERIFY FAILED:\n  " + "\n  ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
