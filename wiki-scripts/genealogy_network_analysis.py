"""Network analysis of wikibase genealogy TSVs.

Addresses the STATUS.md action items:
- field coverage (sex/birth/death/external IDs)
- degree stats + fan-out QA (conflation suspects)
- cycle detection
- weakly-connected components
- centrality: gateway-ancestor test for Charlemagne / Bustanai / Jesus / Muhammad
"""
import csv
import io
import sys
import re
from collections import defaultdict, deque, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
ANA = REPO / "wikibase" / "analysis"

# --- load persons ------------------------------------------------------------
persons = {}
with open(ANA / "persons.tsv", encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for row in rd:
        persons[row["qid"]] = row

N_persons = len(persons)
print(f"persons: {N_persons}")

cov = Counter()
for p in persons.values():
    for k in ("label", "sex", "birth", "death", "gedcom", "wikidata_qid", "geni_id"):
        if p.get(k):
            cov[k] += 1
print("field coverage:")
for k, v in cov.most_common():
    print(f"  {k:14s} {v:7d}  ({100*v/N_persons:5.1f}%)")

# --- load edges --------------------------------------------------------------
parents = defaultdict(set)    # child -> {parents}
children = defaultdict(set)   # parent -> {children}
edges = 0
with open(ANA / "edges.tsv", encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for row in rd:
        p, c = row["parent"], row["child"]
        if p and c and p != c:
            parents[c].add(p)
            children[p].add(c)
            edges += 1
print(f"\nedges: {edges}")

all_nodes = set(parents) | set(children) | set(persons)
print(f"nodes in graph (persons ∪ edges endpoints): {len(all_nodes)}")

roots = [n for n in all_nodes if not parents.get(n)]
leaves = [n for n in all_nodes if not children.get(n)]
print(f"roots (no parent): {len(roots)}")
print(f"leaves (no child): {len(leaves)}")

# --- degree / fan-out --------------------------------------------------------
child_fanout = Counter({n: len(children[n]) for n in children})
parent_indeg = Counter({n: len(parents[n]) for n in parents})

def label(q):
    p = persons.get(q, {})
    return p.get("label") or q

print("\ntop 15 by child count (fan-out — watch for conflation):")
for q, c in child_fanout.most_common(15):
    print(f"  {c:4d}  {q}  {label(q)}")

print("\nindegree histogram (parents per child):")
h = Counter(parent_indeg.values())
for k in sorted(h):
    if k <= 4 or k > 2:
        print(f"  {k} parents: {h[k]}")
    if k > 6:
        break
too_many = [n for n, d in parent_indeg.items() if d > 2]
print(f"children with >2 parents (data error): {len(too_many)}")
for q in too_many[:10]:
    print(f"  {q} {label(q)}  parents={sorted(parents[q])[:5]}")

# --- cycle detection (DFS) ---------------------------------------------------
WHITE, GRAY, BLACK = 0, 1, 2
color = {n: WHITE for n in all_nodes}
cycle_count = 0
cycle_examples = []

sys.setrecursionlimit(1_000_000)

def iterative_dfs(start):
    global cycle_count
    stack = [(start, iter(children.get(start, ())))]
    color[start] = GRAY
    path = [start]
    while stack:
        node, it = stack[-1]
        nxt = next(it, None)
        if nxt is None:
            color[node] = BLACK
            stack.pop()
            path.pop()
            continue
        if color[nxt] == GRAY:
            cycle_count += 1
            if len(cycle_examples) < 5:
                i = path.index(nxt)
                cycle_examples.append(path[i:] + [nxt])
        elif color[nxt] == WHITE:
            color[nxt] = GRAY
            path.append(nxt)
            stack.append((nxt, iter(children.get(nxt, ()))))

for n in all_nodes:
    if color[n] == WHITE:
        iterative_dfs(n)

print(f"\nback-edges (cycles) found: {cycle_count}")
for cyc in cycle_examples:
    print("  cycle:", " -> ".join(f"{q}({label(q)})" for q in cyc))

# --- weakly connected components (undirected) --------------------------------
und = defaultdict(set)
for c, ps in parents.items():
    for p in ps:
        und[c].add(p); und[p].add(c)

# include spouse edges for connectivity check
with open(ANA / "spouses.tsv", encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f, delimiter="\t")
    spouse_count = 0
    for row in rd:
        a, b = row.get("a"), row.get("b")
        if a and b:
            und[a].add(b); und[b].add(a)
            spouse_count += 1
print(f"spouse edges: {spouse_count}")

seen = set()
comps = []
for start in all_nodes:
    if start in seen:
        continue
    comp = []
    q = deque([start])
    seen.add(start)
    while q:
        v = q.popleft()
        comp.append(v)
        for u in und.get(v, ()):
            if u not in seen:
                seen.add(u)
                q.append(u)
    comps.append(comp)
comps.sort(key=len, reverse=True)
print(f"\nweakly-connected components: {len(comps)}")
print(f"giant component: {len(comps[0])}  ({100*len(comps[0])/len(all_nodes):.2f}%)")
isolates = sum(1 for c in comps if len(c) == 1)
print(f"isolates: {isolates}")
print("top 10 components by size:")
for c in comps[:10]:
    sample = ", ".join(label(q) for q in c[:3])
    print(f"  size {len(c):6d}  e.g. {sample}")

# --- gateway-ancestor centrality -------------------------------------------
# For specific target QIDs: how many descendants do they have in the graph?
# Descendants = BFS through children dict.
def descendants(root):
    if root not in all_nodes:
        return set()
    seen = {root}
    q = deque([root])
    while q:
        v = q.popleft()
        for c in children.get(v, ()):
            if c not in seen:
                seen.add(c); q.append(c)
    seen.discard(root)
    return seen

# Try to find test figures by label match.
def find_by_label(pattern):
    rx = re.compile(pattern, re.I)
    hits = []
    for q, p in persons.items():
        if p.get("label") and rx.search(p["label"]):
            hits.append((q, p["label"]))
    return hits

targets_patterns = {
    "Charlemagne": r"^Charlemagne$|^Charles the Great",
    "Bustanai": r"^Bustanai",
    "Jesus": r"^Jesus of Nazareth$|^Jesus Christ$|^Jesus$",
    "Muhammad": r"^Muhammad$|^Mohammed$",
    "Heo Hwang-ok": r"Heo Hwang|Hwang[- ]ok",
    "Genghis Khan": r"Genghis Khan|Temüjin|Temujin",
    "Confucius": r"^Confucius$",
}

print("\ngateway-ancestor descendant counts (graph-walked):")
for name, rx in targets_patterns.items():
    hits = find_by_label(rx)
    if not hits:
        print(f"  {name}: no label match")
        continue
    for q, lab in hits[:3]:
        d = len(descendants(q))
        print(f"  {name:15s} {q:8s} {lab:40s} descendants={d}")

# Global descendant-count leaderboard: who actually has the biggest downstream?
print("\ntop 25 by descendant count (real gateway ancestors):")
# Expensive — limit to nodes with >=50 direct children, then BFS. Tighten further if slow.
candidates = [n for n, k in child_fanout.items() if k >= 20]
print(f"  candidates (>=20 direct children): {len(candidates)}")
scored = []
for q in candidates:
    d = len(descendants(q))
    scored.append((d, q))
scored.sort(reverse=True)
for d, q in scored[:25]:
    print(f"  {d:6d}  {q:8s}  {label(q)}")
