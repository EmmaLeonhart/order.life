"""Cost every edge of a cycle by the ancestry that cutting it would destroy.

    python wiki-scripts/cheapest_cycle_break.py Q138467

Takes a qid, finds a cycle through it, and reports for EACH edge in that cycle how much
ancestral depth cutting it would cost: how many records lose depth, the worst single loss,
and the total. Reads edges.tsv and writes nothing -- every cut is simulated in memory.

WHY THIS EXISTS

cycle_policy.md says that if a loop can only be broken by cutting a gateway, the real
defect is elsewhere in the loop. That is the right rule and it was being applied by
guessing: pick the chronologically impossible edge, cut it, measure, discover it was
load-bearing, revert. That is what happened to the Scipio cut on 2026-07-31 -- 263
generations amputated, reverted the same day -- and again on 2026-08-01, when all three
candidate edges in the Licinius stretch turned out to cost 19,700 records their ancestry.

Guessing which edge to test is the wrong loop. Cost them all, then look at the cheap ones.

A CHEAP EDGE IS NOT AUTOMATICALLY THE RIGHT CUT. This ranks by damage, not by
correctness. It tells you where a cut is affordable; whether the edge is actually wrong is
a separate judgement, and the repair order still puts UNMERGE and DEDUPE ahead of CUT. An
edge that is cheap AND chronologically impossible is a candidate; an edge that is merely
cheap is not.
"""

import csv
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "wikibase" / "analysis"


def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)


def read_edges():
    edges = []
    with (A / "edges.tsv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            p, c = r["parent"], r["child"]
            if p and c and p != c:
                edges.append((p, c))
    return edges


def depths(edges):
    """qid -> ancestral depth over the SCC condensation. Same definition as
    compare_depth.py: a component contributes its own size, so a 72-record tangle counts
    as 72 levels rather than 1, and depth is well defined for records inside a cycle."""
    par = defaultdict(list)
    nodes = set()
    for p, c in edges:
        par[c].append(p)
        nodes.add(p)
        nodes.add(c)
    for k in par:
        par[k].sort(key=qnum)

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

    owner, size = {}, {}
    for i, comp in enumerate(comps):
        size[i] = len(comp)
        for q in comp:
            owner[q] = i
    cpar = defaultdict(set)
    for child, parents in par.items():
        ci = owner[child]
        for p in parents:
            if owner[p] != ci:
                cpar[ci].add(owner[p])
    best = {}
    for start in range(len(comps)):
        if start in best:
            continue
        st = [(start, False)]
        while st:
            node, ready = st.pop()
            if ready:
                best[node] = size[node] + max(
                    (best[p] for p in cpar.get(node, ())), default=0)
                continue
            if node in best:
                continue
            st.append((node, True))
            for p in cpar.get(node, ()):
                if p not in best:
                    st.append((p, False))
    return {q: best[owner[q]] - size[owner[q]] for q in nodes}


def find_cycle(edges, start):
    chi = defaultdict(set)
    for p, c in edges:
        chi[p].add(c)
    prev, dq, seen = {}, deque([start]), {start}
    while dq:
        x = dq.popleft()
        for y in sorted(chi.get(x, ()), key=qnum):
            if y == start:
                path, c = [x], x
                while c != start and c in prev:
                    c = prev[c]
                    path.append(c)
                path.reverse()
                return path + [start]
            if y not in seen:
                seen.add(y); prev[y] = x; dq.append(y)
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    start = args[0]

    label = {}
    with (A / "persons.tsv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            label[r["qid"]] = r.get("label", "")

    edges = read_edges()
    cycle = find_cycle(edges, start)
    if not cycle:
        print(f"no cycle through {start}")
        return 1
    ring = list(zip(cycle, cycle[1:]))
    print(f"cycle through {start}: {len(ring)} edges\n")

    base = depths(edges)
    base_total = sum(base.values())
    eset = set(edges)

    rows = []
    for p, c in ring:
        if (p, c) not in eset:
            continue
        after = depths([e for e in edges if e != (p, c)])
        lost = [(base[q] - after.get(q, base[q])) for q in base
                if after.get(q, base[q]) < base[q]]
        rows.append({
            "p": p, "c": c,
            "n": len(lost),
            "worst": max(lost) if lost else 0,
            "total": base_total - sum(after.values()),
        })
        print(f"  cut {p} -> {c:<9} "
              f"records losing depth {rows[-1]['n']:>6,}   "
              f"worst -{rows[-1]['worst']:<4}  total {rows[-1]['total']:>+12,}")

    rows.sort(key=lambda r: (r["worst"], r["n"]))
    print("\n" + "=" * 72)
    print("  CHEAPEST BREAKS (least ancestry destroyed first)")
    print("=" * 72)
    for r in rows[:6]:
        print(f"  -{r['worst']:<4} worst, {r['n']:>6,} records   "
              f"{r['p']} {label.get(r['p'],'')[:26]}")
        print(f"        -> {r['c']} {label.get(r['c'],'')[:26]}")
    print("\nA cheap edge is where a cut is AFFORDABLE, not where it is CORRECT.")
    print("Check the chronology and the repair order before cutting anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
