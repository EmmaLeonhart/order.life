"""Read-only probe over the frozen genealogy extracts in wikibase/analysis/.

Written 2026-07-30 for the lineage-bridge proposals (planning/lineage_bridges_proposed.md).
It only reads persons.tsv / edges.tsv / spouses.tsv. It writes nothing, ever — the standing
rule for the genealogy QA work is propose, don't apply.

Usage:
    python wiki-scripts/graph_probe.py who Q37401
    python wiki-scripts/graph_probe.py up Q37401          # ancestor tree
    python wiki-scripts/graph_probe.py down Q51928        # descendant tree
    python wiki-scripts/graph_probe.py path Q6432 Q152973 # child -> ancestor path
    python wiki-scripts/graph_probe.py roots Q37401       # parentless ancestors
    python wiki-scripts/graph_probe.py find kosala        # label substring search
    python wiki-scripts/graph_probe.py adam Q37401 Q6432  # in Adam's descent?
    python wiki-scripts/graph_probe.py orphans            # edge endpoints with no persons row
"""

import collections
import csv
import sys
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"
ADAM = "Q152973"


def load():
    persons = {}
    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            persons[row["qid"]] = row

    parents = collections.defaultdict(set)
    children = collections.defaultdict(set)
    with open(ANALYSIS / "edges.tsv", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            parents[row["child"]].add(row["parent"])
            children[row["parent"]].add(row["child"])

    spouses = collections.defaultdict(set)
    with open(ANALYSIS / "spouses.tsv", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            spouses[row["a"]].add(row["b"])
            spouses[row["b"]].add(row["a"])

    return persons, parents, children, spouses


PERSONS, PARENTS, CHILDREN, SPOUSES = load()


def lbl(q):
    p = PERSONS.get(q)
    if not p:
        return f"{q} <NO persons.tsv ROW>"
    bits = [q]
    if p.get("wikidata_qid"):
        bits.append("wd " + p["wikidata_qid"])
    if p.get("birth"):
        bits.append("b." + p["birth"][:11])
    return f"{p['label']} [{', '.join(bits)}]"


def closure(start, adj):
    seen = {start}
    queue = collections.deque([start])
    while queue:
        for nxt in adj.get(queue.popleft(), ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def tree(root, adj, maxdepth=200):
    seen = set()
    out = []

    def rec(q, d):
        if q in seen:
            out.append("  " * d + lbl(q) + "   (already shown)")
            return
        if d > maxdepth:
            out.append("  " * d + lbl(q) + "   (depth cap)")
            return
        seen.add(q)
        out.append("  " * d + lbl(q))
        for nxt in sorted(adj.get(q, ())):
            rec(nxt, d + 1)

    rec(root, 0)
    return out


def path_up(src, dst):
    queue = collections.deque([(src, [src])])
    seen = {src}
    while queue:
        cur, path = queue.popleft()
        if cur == dst:
            return path
        for p in PARENTS.get(cur, ()):
            if p not in seen:
                seen.add(p)
                queue.append((p, path + [p]))
    return None


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, args = argv[0], argv[1:]

    if cmd == "who":
        for q in args:
            print("===", lbl(q))
            print("  parents :", [lbl(p) for p in sorted(PARENTS.get(q, ()))] or "none")
            print("  children:", [lbl(c) for c in sorted(CHILDREN.get(q, ()))] or "none")
            print("  spouses :", [lbl(s) for s in sorted(SPOUSES.get(q, ()))] or "none")
    elif cmd == "up":
        print("\n".join(tree(args[0], PARENTS)))
    elif cmd == "down":
        print("\n".join(tree(args[0], CHILDREN)))
    elif cmd == "path":
        p = path_up(args[0], args[1])
        if not p:
            print(f"no parent-path from {args[0]} up to {args[1]}")
        else:
            for i, q in enumerate(p):
                print(f"{i:4d} {lbl(q)}")
    elif cmd == "roots":
        up = closure(args[0], PARENTS)
        roots = [q for q in up if not PARENTS.get(q)]
        print(f"ancestor closure {len(up)}, parentless roots {len(roots)}")
        for q in sorted(roots):
            print("   ", lbl(q))
    elif cmd == "find":
        needle = args[0].lower()
        hits = [q for q, p in PERSONS.items() if needle in (p["label"] or "").lower()]
        print(f"{len(hits)} match {needle!r}")
        for q in hits[:200]:
            print(f"   {lbl(q)}  par={len(PARENTS.get(q, ()))} ch={len(CHILDREN.get(q, ()))}")
    elif cmd == "adam":
        desc = closure(ADAM, CHILDREN)
        print(f"Adam ({ADAM}) descendant closure: {len(desc)} of {len(PERSONS)} persons")
        for q in args:
            print(f"  {q in desc!s:5s}  {lbl(q)}")
    elif cmd == "orphans":
        ends = set(PARENTS) | set(CHILDREN)
        for s in PARENTS.values():
            ends |= s
        for s in CHILDREN.values():
            ends |= s
        missing = sorted(q for q in ends if q not in PERSONS)
        print(f"{len(missing)} edge endpoints have no persons.tsv row")
        for q in missing:
            print("   ", q, "parents:", sorted(PARENTS.get(q, ())), "children:", sorted(CHILDREN.get(q, ())))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
