"""Write the missing side of a one-sided PHANTOM edge into the shell that lacks it.

    python wiki-scripts/add_phantom_mirrors.py                 # dry run, whole class
    python wiki-scripts/add_phantom_mirrors.py --limit 200     # dry run, first 200
    python wiki-scripts/add_phantom_mirrors.py --limit 200 --write

RULED BY EMMA 2026-08-05, asked directly: **"ADD the missing side, always."** queue.md
item 16. An edge lives in two places -- the child's P47/P48 and the parent's P20 -- and
1,050 of them are declared on one side only, where the other endpoint is an empty shell.
The ruling is to write the mirror claim into the shell, never to remove the present side,
and never to second-guess it per record: nothing in an empty shell distinguishes a
half-finished deletion from a half-finished import.

SCOPE IS PHANTOM ONLY. `GAP` (219) needs its missing records CREATED and named, which is
item 17. `BOTH-REAL` (2,479) is per-record judgement. Do not let ADD leak out of this class.

WHY THIS IS SAFE TO RUN IN BULK, WHICH ALMOST NOTHING ELSE HERE IS

extract_genealogy.py builds edges.tsv from the UNION of both directions, so the edge is
already in the graph and writing its mirror cannot change it. compare_tangles and
compare_depth must come back completely clean. **Any movement at all is a bug in this
script, not a finding** -- it would mean something other than the mirror of an existing
edge got written.

THE ONE PLACE THIS SCRIPT HAS TO CHOOSE, AND WHERE IT REFUSES TO

A `child-only` edge is mirrored as P20 on the parent, which is unambiguous -- there is one
child property. A `parent-only` edge has to be mirrored as P47 *or* P48 on the child, and
which one depends on the parent's sex. The graph cannot tell them apart, because edges.tsv
records parent->child either way -- so a wrong choice here is a data error the gate is
structurally blind to. The parent's P55 decides it; where P55 is absent or is neither
value, the edge is SKIPPED and counted, not guessed.

READS THE TSV AS A CANDIDATE LIST AND THE ITEM FILES AS THE TRUTH. edge_symmetry_classified.tsv
was built 2026-08-01 and the dump has moved since -- merges have vacated some of these
qids. Every candidate is re-derived from the records before anything is written, and a
candidate whose edge is now two-sided, or gone, is skipped.

Shadow-aware: every file claiming a written qid is rewritten, per the standing rule.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
ANALYSIS = ROOT / "wikibase" / "analysis"
CLASSIFIED = ANALYSIS / "edge_symmetry_classified.tsv"
REDIRECTS = ANALYSIS / "redirects.tsv"

P_FATHER, P_MOTHER, P_CHILD, P_SEX = "P47", "P48", "P20", "P55"
MALE, FEMALE = "Q153718", "Q153719"

_cache = {}


def load(q):
    """The record AT this qid, or None if the file is missing or the qid is vacated."""
    if q not in _cache:
        p = ITEMS / f"{q}.json"
        d = None
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                d = None
            if isinstance(d, dict) and (d.get("id") or q) != q:
                d = None
        _cache[q] = d if isinstance(d, dict) else None
    return _cache[q]


def redirect_map():
    out = {}
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                out[r["from_qid"]] = r["to_qid"]
    return out


REDIR = {}


def canon(q):
    for _ in range(8):
        n = REDIR.get(q, q)
        if n == q:
            return q
        q = n
    return q


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(canon(v["id"]))
    return out


def is_shell(d):
    """Unnamed: no English label and no English alias.

    Deliberately NOT testing the description, and deliberately not re-testing for
    genealogical claims. edge_symmetry.py's own `substantive` test is
    `has_label or has_alias or has_geneal` -- it never looked at descriptions -- so the
    1,050-edge PHANTOM class Emma was shown, and ruled on, includes 217 edges whose shell
    carries a description but no name. `Q130498` "Greek goddess of the night" is one.
    Adding a description test here would silently narrow the ruled class by 217 edges on
    my own initiative, which is exactly the per-record second-guessing the ruling ends.

    Re-testing for genealogical claims would be worse than narrowing: writing the first
    mirror gives a shell a genealogical claim, so the second mirror onto the same shell
    would skip itself. The TSV already filtered on that at classification time.
    """
    if d is None:
        return False
    if ((d.get("labels") or {}).get("en") or {}).get("value"):
        return False
    if (d.get("aliases") or {}).get("en"):
        return False
    return True


def make_claim(pid, target):
    value = {"entity-type": "item", "id": target}
    if target[1:].isdigit():
        value["numeric-id"] = int(target[1:])
    return {
        "mainsnak": {
            "snaktype": "value",
            "property": pid,
            "datavalue": {"value": value, "type": "wikibase-entityid"},
        },
        "type": "statement",
        "rank": "normal",
    }


def claimants(qid):
    out = [qid]
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if r["to_qid"] == qid:
                    out.append(r["from_qid"])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    global REDIR
    REDIR = redirect_map()
    write = "--write" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    if not CLASSIFIED.exists():
        print("edge_symmetry_classified.tsv missing -- run edge_symmetry.py first")
        return 1

    cands = []
    with open(CLASSIFIED, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["verdict"] == "PHANTOM":
                cands.append((r["side"], r["parent"], r["child"]))

    plan = []                       # (target_qid, pid, value, why)
    skipped = collections.Counter()
    for side, parent, child in cands:
        p, c = canon(parent), canon(child)
        dp, dc = load(p), load(c)
        if dp is None or dc is None:
            skipped["endpoint vacated or missing since the TSV was built"] += 1
            continue
        parent_declares = c in vals(dp, P_CHILD)
        child_declares = p in vals(dc, P_FATHER) + vals(dc, P_MOTHER)
        if parent_declares and child_declares:
            skipped["already two-sided"] += 1
            continue
        if not parent_declares and not child_declares:
            skipped["edge no longer declared on either side"] += 1
            continue

        if child_declares:                      # missing side is the parent's P20
            if not is_shell(dp):
                skipped["receiving endpoint is not a shell any more"] += 1
                continue
            plan.append((p, P_CHILD, c,
                         f"{c} names {p} as a parent; mirror the child-claim"))
        else:                                   # missing side is the child's P47/P48
            if not is_shell(dc):
                skipped["receiving endpoint is not a shell any more"] += 1
                continue
            sex = vals(dp, P_SEX)
            if MALE in sex:
                pid = P_FATHER
            elif FEMALE in sex:
                pid = P_MOTHER
            else:
                skipped["parent's sex not recorded -- cannot choose P47 vs P48"] += 1
                continue
            plan.append((c, pid, p,
                         f"{p} names {c} as a child and is "
                         f"{'male' if pid == P_FATHER else 'female'}; mirror as {pid}"))

    print(f"PHANTOM candidates in the TSV: {len(cands)}")
    for reason, n in skipped.most_common():
        print(f"  skipped {n:5d}  {reason}")
    print(f"  to write {len(plan):5d}  mirror claim(s)")
    if limit is not None:
        plan = plan[:limit]
        print(f"  --limit {limit}: writing the first {len(plan)}")

    if not plan:
        print("\nnothing to do")
        return 0

    by_target = collections.defaultdict(list)
    for target, pid, value, why in plan:
        by_target[target].append((pid, value, why))
    print(f"\n{len(by_target)} record(s) receive a claim; first 10:")
    for t in list(by_target)[:10]:
        for pid, value, why in by_target[t][:3]:
            print(f"  {t}  += {pid} -> {value}    ({why})")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    files = 0
    for target, adds in by_target.items():
        d = load(target)
        for pid, value, _why in adds:
            if value in vals(d, pid):
                continue
            d.setdefault("claims", {}).setdefault(pid, []).append(make_claim(pid, value))
        for f in claimants(target):
            fp = ITEMS / f"{f}.json"
            if not fp.exists():
                continue
            fd = json.loads(fp.read_text(encoding="utf-8"))
            if (fd.get("id") or f) != target:
                continue
            fp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
            files += 1
    print(f"  wrote {files} file(s) across {len(by_target)} record(s)")

    print("\nverifying, from the files rather than from the plan...")
    _cache.clear()
    bad = []
    for target, adds in by_target.items():
        for f in claimants(target):
            fp = ITEMS / f"{f}.json"
            if not fp.exists():
                continue
            fd = json.loads(fp.read_text(encoding="utf-8"))
            if (fd.get("id") or f) != target:
                continue
            for pid, value, _why in adds:
                if value not in vals(fd, pid):
                    bad.append(f"{f} (claims {target}) lacks {pid} -> {value}")
    if bad:
        print("FAILED:")
        for b in bad[:20]:
            print("  " + b)
        return 1
    print("  every claimant of every target carries the mirror claim")
    print("\nNow run verify_repair.py. compare_tangles and compare_depth MUST be")
    print("completely clean -- any movement is a bug in this script, not a finding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
