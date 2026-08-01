"""Compare the tangles of two edges.tsv snapshots. The correct way to verify a repair.

    cp wikibase/analysis/edges.tsv /somewhere/before.tsv     # snapshot, then make the change
    python wiki-scripts/extract_genealogy.py                 # regenerate
    python wiki-scripts/compare_tangles.py /somewhere/before.tsv

With one argument it compares that snapshot against the live wikibase/analysis/edges.tsv.
With two it compares the two files given.

WHY THIS EXISTS, and why you must not verify a repair by diffing qa_cycles.tsv.

A "cycle count" is not a well-defined quantity in this graph. One tangle of n nodes can
contain exponentially many distinct cycles, and any enumerator has to pick some subset.
Until 2026-07-31 dump_qa_errors.py picked its subset by DFS over *sets of qid strings* --
and Python randomises string hashing per process, so three consecutive runs over one
unchanged edges.tsv returned 45, 50 and 46 cycles. Every before/after cycle figure in this
repo predating that date is unsound.

The well-defined object is the strongly connected component. Every ancestry cycle lies
inside exactly one SCC, "X is its own ancestor" is exactly "X sits in an SCC of size > 1",
and the SCC partition is unique no matter what order you traverse in. So this compares
partitions: which tangles appeared, which vanished, which changed membership. A correct
dedupe should show none of the three.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "wikibase" / "analysis" / "edges.tsv"


def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)


def read_edges(path):
    edges = set()
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            p, c = r["parent"], r["child"]
            if p and c and p != c:
                edges.add((p, c))
    return edges


def tangles(edges):
    """Tarjan over sorted adjacency. Returns SCCs of size > 1, each sorted."""
    adj, nodes = defaultdict(list), set()
    for p, c in edges:
        adj[p].append(c)
        nodes.add(p)
        nodes.add(c)
    for k in adj:
        adj[k].sort(key=qnum)
    index, low, on_stack, stack, sccs, idx = {}, {}, set(), [], [], [0]
    for root in sorted(nodes, key=qnum):
        if root in index:
            continue
        work = [(root, iter(adj.get(root, ())))]
        index[root] = low[root] = idx[0]; idx[0] += 1
        stack.append(root); on_stack.add(root)
        while work:
            node, it = work[-1]
            advanced = False
            for nxt in it:
                if nxt not in index:
                    index[nxt] = low[nxt] = idx[0]; idx[0] += 1
                    stack.append(nxt); on_stack.add(nxt)
                    work.append((nxt, iter(adj.get(nxt, ()))))
                    advanced = True
                    break
                if nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                comp = []
                while True:
                    w = stack.pop(); on_stack.discard(w); comp.append(w)
                    if w == node:
                        break
                if len(comp) > 1:
                    sccs.append(tuple(sorted(comp, key=qnum)))
    return sccs


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    before_path = args[0]
    after_path = args[1] if len(args) > 1 else LIVE

    eb, ea = read_edges(before_path), read_edges(after_path)
    tb, ta = tangles(eb), tangles(ea)
    sb, sa = set(tb), set(ta)

    print(f"before: {before_path}")
    print(f"after:  {after_path}\n")
    print(f"  edges              {len(eb):>8,}  ->  {len(ea):>8,}  ({len(ea)-len(eb):+,})")
    print(f"  tangles            {len(tb):>8,}  ->  {len(ta):>8,}  ({len(ta)-len(tb):+,})")
    print(f"  records in tangles {sum(map(len, tb)):>8,}  ->  {sum(map(len, ta)):>8,}"
          f"  ({sum(map(len, ta))-sum(map(len, tb)):+,})")
    print(f"  largest tangle     {max(map(len, tb), default=0):>8,}  ->  "
          f"{max(map(len, ta), default=0):>8,}")

    gained, lost = sa - sb, sb - sa
    print(f"\ntangles ONLY after  (introduced): {len(gained)}")
    for c in sorted(gained, key=len, reverse=True)[:15]:
        print(f"   size {len(c):<4} {','.join(c[:10])}{' ...' if len(c) > 10 else ''}")
    print(f"tangles ONLY before (removed):    {len(lost)}")
    for c in sorted(lost, key=len, reverse=True)[:15]:
        print(f"   size {len(c):<4} {','.join(c[:10])}{' ...' if len(c) > 10 else ''}")

    # A node moving between tangles matters even when the counts match.
    def owner(sccs):
        return {q: c for c in sccs for q in c}
    ob, oa = owner(tb), owner(ta)
    moved = sorted({q for q in set(ob) & set(oa) if ob[q] != oa[q]}, key=qnum)
    print(f"\nrecords that changed tangle: {len(moved)}")
    for q in moved[:15]:
        print(f"   {q}: size {len(ob[q])} -> {len(oa[q])}")
    entered = sorted(set(oa) - set(ob), key=qnum)
    left = sorted(set(ob) - set(oa), key=qnum)
    print(f"records newly inside a tangle: {len(entered)}"
          + (f"  {','.join(entered[:15])}" if entered else ""))
    print(f"records no longer in a tangle: {len(left)}"
          + (f"  {','.join(left[:15])}" if left else ""))

    clean = not gained and not lost and not moved and not entered
    print("\n" + ("UNCHANGED -- no tangle introduced, removed or reshaped"
                  if clean else "TANGLES CHANGED -- read the lists above"))
    return 0 if not gained and not entered else 1


if __name__ == "__main__":
    sys.exit(main())
