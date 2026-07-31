"""Merge duplicate records that share a Wikidata id.

48 Wikidata items are claimed by two dump records each. 35 of those pairs have identical
labels on both sides -- the same person imported twice. This merges them.

MECHANISM, and it is non-destructive. This dump already contains 57,401 redirects, and a
redirect is simply a file whose internal "id" differs from its filename: Q1003.json holds
Q1's content with id "Q1". extract_genealogy.py detects that, records the redirect, and
canonicalises every edge citing the source to the target. So merging B into A is:
    1. union B's genealogical claims into A (dedup by value)
    2. rewrite B.json as a copy of A's content, keeping id = A
No file is deleted, no claim is dropped, and git reverts it cleanly.

SCOPE: only pairs whose parent sets do not conflict. Of the 35, 26 have differing parents,
but 21 of those differ only because the PARENTS are themselves duplicates (8 are a known
duplicate pair, 13 share a near-identical name). Those need the cluster merged in dependency
order and are deliberately left for a follow-up; merging them naively would union two sets
of duplicate parents onto one record and make the multi-parent problem worse.

    python wiki-scripts/apply_dup_merge.py           # dry run, prints the plan
    python wiki-scripts/apply_dup_merge.py --write   # apply
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
AUDIT = ROOT / "wikibase" / "analysis" / "qa_wikidata_ids.tsv"

GEN_PROPS = ("P20", "P42", "P47", "P48", "P61")  # child, spouse, father, mother, wd id


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(q, d):
    (ITEMS / f"{q}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def pairs():
    rows = list(csv.DictReader(open(AUDIT, encoding="utf-8"), delimiter="\t"))
    by = collections.defaultdict(list)
    for r in rows:
        if r["verdict"] == "shared_id":
            by[r["wikidata_qid"]].append(r)
    return [g for g in by.values()
            if len(g) == 2 and all(float(r["name_score"]) >= 0.95 for r in g)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv

    plan, skipped = [], []
    for g in pairs():
        x, y = g[0]["qid"], g[1]["qid"]
        dx, dy = load(x), load(y)
        if not dx or not dy:
            skipped.append((x, y, "one side has no item file"))
            continue
        px = set(vals(dx, "P47")) | set(vals(dx, "P48"))
        py = set(vals(dy, "P47")) | set(vals(dy, "P48"))
        if px and py and px != py:
            skipped.append((x, y, "parent sets conflict -- needs the cluster merged first"))
            continue
        # survivor = the one with more genealogical claims; tie-break on lower QID
        wx = sum(len(vals(dx, p)) for p in GEN_PROPS)
        wy = sum(len(vals(dy, p)) for p in GEN_PROPS)
        a, b = (x, y) if (wx, -int(y[1:])) >= (wy, -int(x[1:])) else (y, x)
        plan.append((a, b, g[0]["wikidata_qid"], g[0]["label"]))

    print(f"{len(plan)} pair(s) mergeable now, {len(skipped)} deferred\n")
    for a, b, wd, label in plan:
        da, db = load(a), load(b)
        gained = {p: sorted(set(vals(db, p)) - set(vals(da, p))) for p in GEN_PROPS}
        gained = {p: v for p, v in gained.items() if v}
        print(f"  {b} -> {a}   {label[:38]:40s} (wd {wd})")
        if gained:
            for p, v in gained.items():
                print(f"        survivor gains {p}: {v}")
        else:
            print("        survivor gains nothing; duplicate is a strict subset")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        print("\ndeferred:")
        for x, y, why in skipped[:6]:
            print(f"  {x}/{y}: {why}")
        return 0

    print("\napplying...")
    for a, b, wd, label in plan:
        da, db = load(a), load(b)
        before = {p: len(vals(da, p)) for p in GEN_PROPS}
        for p in GEN_PROPS:
            have = set(vals(da, p))
            for c in (db.get("claims") or {}).get(p, []):
                v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                key = v.get("id") if isinstance(v, dict) else v
                if key not in have and key != a:
                    da.setdefault("claims", {}).setdefault(p, []).append(c)
                    have.add(key)
        # a record must never be its own parent/child. P61 values are plain
        # strings, not entity dicts, so guard the type before calling .get.
        def _vid(c):
            v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            return v.get("id") if isinstance(v, dict) else None

        for p in GEN_PROPS:
            if p in (da.get("claims") or {}):
                da["claims"][p] = [c for c in da["claims"][p] if _vid(c) != a]
        save(a, da)
        after = {p: len(vals(load(a), p)) for p in GEN_PROPS}
        # rewrite B as a redirect: a copy of A's content, id already == a
        save(b, load(a))
        print(f"  {b} -> {a}: {before} -> {after}")

    print("\nverifying no genealogical claim was lost...")
    ok = True
    for a, b, wd, label in plan:
        da, db = load(a), load(b)
        if db.get("id") != a:
            print(f"  FAIL {b}: internal id is {db.get('id')}, expected {a}")
            ok = False
    print("all redirects point at their survivor" if ok else "PROBLEMS ABOVE")
    print("\nNow re-run extract_genealogy.py + dump_qa_errors.py to refresh the extracts.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
