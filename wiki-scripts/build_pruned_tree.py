"""
Build a pruned lineage tree from Adam downward.

Outputs a markdown file with the tree structure, following the
heaviest branch first at each fork. Each node appears only once.
Where a node was already visited, it's marked as a cross-reference.

Segments are identified at major branch points (nodes with >1 child
that each have significant descendant counts).
"""
import csv
import io
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
ANA = REPO / "wikibase" / "analysis"
OUT = ANA / "pruned_tree.md"

# --- load data ---------------------------------------------------------------
persons = {}
with open(ANA / "persons.tsv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        persons[row["qid"]] = row

children_map = defaultdict(set)
parents_map = defaultdict(set)
with open(ANA / "edges.tsv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        children_map[row["parent"]].add(row["child"])
        parents_map[row["child"]].add(row["parent"])

spouses = defaultdict(set)
with open(ANA / "spouses.tsv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        spouses[row["a"]].add(row["b"])
        spouses[row["b"]].add(row["a"])


def lab(q):
    return (persons.get(q, {}).get("label") or q).strip()


# --- descendant counts (memoized BFS) ---------------------------------------
_desc_cache = {}

def desc_count(q):
    if q in _desc_cache:
        return _desc_cache[q]
    seen = {q}
    stack = [q]
    while stack:
        v = stack.pop()
        for c in children_map.get(v, ()):
            if c not in seen:
                seen.add(c)
                stack.append(c)
    _desc_cache[q] = len(seen) - 1
    return _desc_cache[q]


# --- build tree (DFS, visit-once) -------------------------------------------
ROOT = "Q152973"  # Adam Y Chromosomal Adam
MIN_DESC_TO_EXPAND = 3       # only expand children with >= this many descendants
MAX_DEPTH = 30               # safety cap
SEGMENT_THRESHOLD = 50       # nodes with >1 big child get a segment marker

visited = set()
lines = []
segments = []


def indent(depth):
    return "  " * depth


def walk(q, depth):
    if depth > MAX_DEPTH:
        return
    if q in visited:
        lines.append(f"{indent(depth)}- *→ see {lab(q)} ({q}) above*")
        return

    visited.add(q)
    dc = desc_count(q)
    nch = len(children_map.get(q, set()))
    sp = sorted(spouses.get(q, set()))
    spouse_str = ""
    if sp:
        spouse_str = f" ⚭ {', '.join(lab(s) for s in sp[:3])}"
        if len(sp) > 3:
            spouse_str += f" +{len(sp)-3} more"

    lines.append(f"{indent(depth)}- **{lab(q)}** ({q}) — {dc} desc, {nch} ch{spouse_str}")

    # Detect segment-worthy forks
    kids = sorted(children_map.get(q, set()), key=lambda c: -desc_count(c))
    big_kids = [c for c in kids if desc_count(c) >= SEGMENT_THRESHOLD]
    if len(big_kids) > 1:
        segments.append((q, lab(q), [(c, lab(c), desc_count(c)) for c in big_kids]))

    # Recurse into children, heaviest first
    for c in kids:
        cdc = desc_count(c)
        if cdc < MIN_DESC_TO_EXPAND and c in visited:
            continue
        if cdc == 0 and depth > 8:
            # skip terminal leaves deep in tree
            continue
        walk(c, depth + 1)

    # Show pruned leaf children as a summary
    pruned = [c for c in kids if desc_count(c) == 0 and c not in visited and depth > 8]
    if pruned:
        names = ", ".join(lab(c) for c in pruned[:5])
        if len(pruned) > 5:
            names += f" +{len(pruned)-5} more"
        lines.append(f"{indent(depth+1)}- *leaves: {names}*")
        visited.update(pruned)


print(f"Building pruned tree from {lab(ROOT)} ({ROOT})...")
print(f"  Total descendants: {desc_count(ROOT)}")

walk(ROOT, 0)

# --- write output ------------------------------------------------------------
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"# Pruned Lineage Tree from {lab(ROOT)}\n\n")
    f.write(f"Root: **{lab(ROOT)}** ({ROOT}) — {desc_count(ROOT)} total descendants\n\n")
    f.write(f"Nodes shown: {len(visited)} (of {desc_count(ROOT)+1} reachable)\n\n")
    f.write(f"Min descendants to expand: {MIN_DESC_TO_EXPAND}\n\n")

    if segments:
        f.write("## Major Branch Points\n\n")
        for sq, slab, kids in segments:
            f.write(f"- **{slab}** ({sq}) forks into:\n")
            for cq, clab, cdc in kids:
                f.write(f"  - {clab} ({cq}) — {cdc} desc\n")
        f.write("\n")

    f.write("## Tree\n\n")
    for line in lines:
        f.write(line + "\n")

print(f"\nWrote {OUT}")
print(f"Nodes visited: {len(visited)}")
print(f"Major branch points: {len(segments)}")
