"""Dump the FULL genealogy QA error lists (not just samples) to TSVs.
Local-only: reads wikibase/analysis/{persons,edges}.tsv. No wiki access.
Errors it enumerates:
  - qa_multiparent.tsv : every child with >2 parents (Geni merge errors)
  - qa_cycles.tsv      : every ancestry cycle (impossible self-ancestor loops)
"""
import csv, io, sys
from collections import defaultdict
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ANA = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"

label = {}
with open(ANA/"persons.tsv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
        label[r["qid"]] = r.get("label","")

parents = defaultdict(set)
with open(ANA/"edges.tsv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
        p, c = r["parent"], r["child"]
        if p and c and p != c:
            parents[c].add(p)

# multi-parent
mp = [(c, ps) for c, ps in parents.items() if len(ps) > 2]
mp.sort(key=lambda x: (-len(x[1]), x[0]))
with open(ANA/"qa_multiparent.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["child_qid","child_label","n_parents","parent_qids"])
    for c, ps in mp:
        w.writerow([c, label.get(c,""), len(ps), ",".join(sorted(ps))])
print(f"qa_multiparent.tsv: {len(mp)} children with >2 parents")

# Cycles, one representative per tangle.
#
# This used to be a colour-marked DFS that appended a cycle on every back-edge. It was
# wrong twice over and the numbers it produced are not comparable across runs:
#
#   1. It iterated `set`s of qid strings. Python randomises string hashing per process,
#      so the traversal order -- and therefore which cycles were found -- changed on
#      every invocation. Three consecutive runs over one unchanged edges.tsv on
#      2026-07-31 returned 45, 50 and 46 cycles. Every "cycles went from X to Y" claim
#      in devlog.md and queue.md that came from this script is unsound, including the
#      "52 -> 54" that check_invariants.py was written to catch.
#   2. It marked nodes BLACK on pop and never revisited them, so it found *some* cycles
#      per tangle, never all of them. The count was never a count of cycles anyway -- a
#      single tangle of n nodes can hold exponentially many.
#
# What is well defined is the strongly connected component. Every ancestry cycle lies
# inside exactly one SCC, the SCC partition is unique regardless of traversal order, and
# "this record is its own ancestor" is precisely "this record sits in an SCC of size > 1".
# So: Tarjan over sorted adjacency for the tangles, then one canonical shortest cycle per
# tangle as a readable handle on it. Deterministic, and the row count is now a real
# quantity -- the number of tangles, which is what check_invariants.py has always
# measured as `tangled_components`.
children = defaultdict(set)
for c, ps in parents.items():
    for p in ps:
        children[p].add(c)

def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)

nodes = sorted(set(parents) | set(children), key=qnum)
adj = {n: sorted(children.get(n, ()), key=qnum) for n in nodes}

# Tarjan, iterative, over the sorted adjacency above.
index, low, on_stack, stack, sccs, idx = {}, {}, set(), [], [], [0]
for root in nodes:
    if root in index:
        continue
    work = [(root, iter(adj[root]))]
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
                sccs.append(sorted(comp, key=qnum))

def shortest_cycle(comp):
    """Shortest cycle through the component's lowest-numbered node. BFS stays inside
    the component, so the path found is a real ancestry loop and not a detour."""
    inside = set(comp)
    src = comp[0]
    prev, queue = {src: None}, [src]
    while queue:
        nxt_level = []
        for node in queue:
            for kid in adj.get(node, ()):
                if kid == src:
                    path, cur = [src], node
                    while cur is not None:
                        path.append(cur); cur = prev[cur]
                    return list(reversed(path))
                if kid in inside and kid not in prev:
                    prev[kid] = node
                    nxt_level.append(kid)
        queue = nxt_level
    return [src, src]

rows = [(comp, shortest_cycle(comp)) for comp in sccs]
rows.sort(key=lambda r: (-len(r[0]), qnum(r[1][0])))

with open(ANA/"qa_cycles.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["cycle_len","chain_qids","chain_labels","tangle_size","tangle_qids"])
    for comp, cyc in rows:
        w.writerow([len(cyc) - 1, " -> ".join(cyc),
                    " -> ".join(label.get(q,q) for q in cyc),
                    len(comp), ",".join(comp)])
print(f"qa_cycles.tsv: {len(rows)} tangles, "
      f"{sum(len(c) for c in sccs)} records inside one")
