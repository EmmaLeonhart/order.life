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
    for r in csv.DictReader(f, delimiter="\t"):
        label[r["qid"]] = r.get("label","")

parents = defaultdict(set)
with open(ANA/"edges.tsv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
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

# cycles via DFS back-edge detection
children = defaultdict(set)
for c, ps in parents.items():
    for p in ps:
        children[p].add(c)
WHITE, GREY, BLACK = 0, 1, 2
color = defaultdict(int)
cycles = []
nodes = set(parents) | set(children)
for start in nodes:
    if color[start] != WHITE:
        continue
    stack = [(start, iter(children[start]))]
    path = [start]
    onpath = {start}
    while stack:
        node, it = stack[-1]
        color[node] = GREY
        advanced = False
        for nxt in it:
            if color[nxt] == GREY and nxt in onpath:
                i = path.index(nxt)
                cycles.append(path[i:] + [nxt])
            elif color[nxt] == WHITE:
                stack.append((nxt, iter(children[nxt])))
                path.append(nxt); onpath.add(nxt)
                advanced = True
                break
        if not advanced:
            color[node] = BLACK
            stack.pop()
            onpath.discard(node); path.pop()
with open(ANA/"qa_cycles.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["cycle_len","chain_qids","chain_labels"])
    for cyc in cycles:
        w.writerow([len(cyc)-1, " -> ".join(cyc), " -> ".join(label.get(q,q) for q in cyc)])
print(f"qa_cycles.tsv: {len(cycles)} cycles")
