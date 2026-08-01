"""Compare ANCESTRAL DEPTH between two edges.tsv snapshots. The gate that was missing.

    cp wikibase/analysis/edges.tsv /somewhere/before.tsv    # snapshot, then change something
    python wiki-scripts/extract_genealogy.py                # regenerate
    python wiki-scripts/compare_depth.py /somewhere/before.tsv

With one argument it compares that snapshot against the live edges.tsv; with two it
compares the two files given. Exits non-zero if any record loses more than --max-loss
levels (default 5).

WHY THIS EXISTS

On 2026-07-31 a single edge was cut to break an 18-record tangle. Every gate in the repo
went green -- compare_tangles.py reported 18 records freed, 0 tangles introduced, 0
reshaped -- and the cut had severed the sole upward gateway of the whole Scipio line:

    Q73794 Gnaeus Cornelius Scipio   263 ancestors deep -> 0
    Q73299 Scipio Africanus          267 -> 4

with the severed chain running all the way to Q1 Aster. It was reverted.

The gates all measured WIDTH -- how many records sit inside a tangle, how many descendants
a cut loses. queue.md and cycle_policy.md both say plainly that load-bearing here means
DEPTH, upward: the ancestry reached THROUGH a node, not the descendants hanging off it.
qa_cycles_load.tsv gets this wrong and the rails say so; compare_tangles.py got it wrong
too. Nothing measured the thing that actually matters, so nothing could catch it.

HOW DEPTH IS DEFINED, given the graph has cycles

Longest-chain-upward is ill-defined inside a tangle, so the graph is condensed by strongly
connected component first -- the SCC partition is unique regardless of traversal order --
and the longest path is taken over the condensation, which is a genuine DAG. Each component
contributes its own size, so a 72-record tangle counts as 72 levels rather than 1. Depth is
then well defined for every record, cycle or not, and comparable across runs.

Numbers here will not match a naive DFS chain count, and should not: this one is stable.
"""

import csv
import sys
from collections import defaultdict

DEFAULT_MAX_LOSS = 5


def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)


def read_edges(path):
    par = defaultdict(list)
    nodes = set()
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            p, c = r["parent"], r["child"]
            if p and c and p != c:
                par[c].append(p)
                nodes.add(p)
                nodes.add(c)
    for k in par:
        par[k].sort(key=qnum)
    return par, nodes


def sccs_of(par, nodes):
    """Tarjan over the child -> parents graph, iterative, sorted adjacency."""
    index, low, on_stack, stack, comps, idx = {}, {}, set(), [], [], [0]
    for root in sorted(nodes, key=qnum):
        if root in index:
            continue
        work = [(root, iter(par.get(root, ())))]
        index[root] = low[root] = idx[0]; idx[0] += 1
        stack.append(root); on_stack.add(root)
        while work:
            node, it = work[-1]
            advanced = False
            for nxt in it:
                if nxt not in index:
                    index[nxt] = low[nxt] = idx[0]; idx[0] += 1
                    stack.append(nxt); on_stack.add(nxt)
                    work.append((nxt, iter(par.get(nxt, ()))))
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
                comps.append(comp)
    return comps


def depths(path):
    """qid -> ancestral depth, over the SCC condensation."""
    par, nodes = read_edges(path)
    comps = sccs_of(par, nodes)
    owner, size = {}, {}
    for i, comp in enumerate(comps):
        size[i] = len(comp)
        for q in comp:
            owner[q] = i

    # condensation edges: component -> components of its parents
    cpar = defaultdict(set)
    for child, parents in par.items():
        ci = owner[child]
        for p in parents:
            pi = owner[p]
            if pi != ci:
                cpar[ci].add(pi)

    # longest weighted path upward on the DAG, iterative to survive deep chains
    best = {}
    for start in range(len(comps)):
        if start in best:
            continue
        stack = [(start, False)]
        while stack:
            node, ready = stack.pop()
            if ready:
                best[node] = size[node] + max(
                    (best[p] for p in cpar.get(node, ())), default=0)
                continue
            if node in best:
                continue
            stack.append((node, True))
            for p in cpar.get(node, ()):
                if p not in best:
                    stack.append((p, False))
    # a record's own component counts as itself, not as ancestry
    return {q: best[owner[q]] - size[owner[q]] for q in nodes}, owner, size


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    max_loss = DEFAULT_MAX_LOSS
    for a in sys.argv[1:]:
        if a.startswith("--max-loss="):
            max_loss = int(a.split("=", 1)[1])
    before_path = args[0]
    after_path = (args[1] if len(args) > 1
                  else "wikibase/analysis/edges.tsv")

    label = {}
    try:
        with open("wikibase/analysis/persons.tsv", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                label[r["qid"]] = r.get("label", "")
    except FileNotFoundError:
        pass

    db, _, _ = depths(before_path)
    da, _, _ = depths(after_path)

    print(f"before: {before_path}")
    print(f"after:  {after_path}\n")

    # A record that is ABSENT afterwards did not lose ancestry -- it stopped existing,
    # which is what a merge does to the loser's qid. Counting it as a loss reported
    # Q72693 as "-259 levels" for a dedupe that severed nothing, on 2026-07-31. Dropped
    # records are reported on their own line below; they are not depth losses, and a
    # wholesale deletion still shows up there rather than being hidden.
    dropped = [q for q in db if q not in da]
    absent = set(dropped)

    lost = []
    for q, d in db.items():
        if q in absent:
            continue
        n = da.get(q, 0)
        if n < d:
            lost.append((d - n, q, d, n))
    gained = sum(1 for q, d in da.items() if d > db.get(q, 0))

    total_before = sum(db.values())
    total_after = sum(da.values())
    print(f"  records measured   {len(db):>8,}  ->  {len(da):>8,}")
    print(f"  total depth        {total_before:>8,}  ->  {total_after:>8,}  "
          f"({total_after - total_before:+,})")
    print(f"  records that LOST depth: {len(lost)}")
    print(f"  records that gained:     {gained}")
    if dropped:
        print(f"  records absent afterwards: {len(dropped)} "
              f"(expected after a merge: {', '.join(sorted(dropped, key=qnum)[:8])})")

    lost.sort(reverse=True)
    if lost:
        print(f"\n  worst losses:")
        for delta, q, d, n in lost[:25]:
            print(f"    -{delta:<5} {q:<9} {label.get(q,'')[:44]:<46} {d} -> {n}")
        if len(lost) > 25:
            print(f"    ... and {len(lost) - 25} more")

    worst = lost[0][0] if lost else 0
    print()
    if worst > max_loss:
        print(f"FAIL: a record lost {worst} levels of ancestry (limit {max_loss}).")
        print("Load-bearing means depth upward. If a repair costs this much ancestry the")
        print("severed edge was a gateway -- the real defect is elsewhere in the loop.")
        return 1
    print(f"OK: no record lost more than {max_loss} levels of ancestry "
          f"(worst was {worst}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
