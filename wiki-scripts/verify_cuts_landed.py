"""Assert that every edge cut_edges.py declares cut is actually absent from edges.tsv.

    python wiki-scripts/verify_cuts_landed.py

Exits non-zero and names the survivors if any declared cut is still in the graph.

WHY THIS EXISTS. On 2026-08-01 `theban-senebhenaf` was applied and `cut_edges.py` reported
"edges gone from both sides, all claimants agree". The edge was still there the next day.
`Q85514` listed both `Q85498` and `Q85518` as children; `Q85518` is a silent redirect to
`Q85498`, so removing the literal qid left the alias behind and extract_genealogy.py
canonicalized it straight back into the same edge. The tool's verify pass compared cited
qids literally, which made it blind to precisely the edge the extractor was building.

That is the same failure as the vacuous I2 check: a gate that could not fail against the
source it was checking. `cut_edges.py` now compares through redirects.tsv, but a tool
verifying itself is what failed here. This checks the OUTPUT instead -- the graph the rest
of the pipeline actually reads -- and it is cheap enough to run after every repair.

Reads edges.tsv, which extract_genealogy.py must have regenerated since the last edit to
wikibase/items/. It does not scan the dump.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGES = ROOT / "wikibase" / "analysis" / "edges.tsv"


def load_cuts():
    spec = importlib.util.spec_from_file_location("cut_edges", Path(__file__).parent / "cut_edges.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CUTS


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not EDGES.exists():
        print("edges.tsv missing -- run extract_genealogy.py first")
        return 1

    edges = set()
    with open(EDGES, encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2:
                edges.add((parts[0], parts[1]))

    cuts = load_cuts()
    declared = 0
    live = []
    for name, rows in sorted(cuts.items()):
        for row in rows:
            parent, child = row[0], row[1]
            declared += 1
            if (parent, child) in edges:
                live.append((name, parent, child))

    print(f"cut sets: {len(cuts)}   edges declared cut: {declared}")
    # The hand-maintained CUTS table is the only record of which cuts were meant to be
    # applied, so a set listed there but never run with --write shows up here too. That is
    # the intended behaviour: "declared and not applied" and "applied and silently undone"
    # are the same defect from the graph's point of view.
    for name, parent, child in live:
        print(f"  STILL LIVE  {name}: {parent} -> {child}")
    if live:
        print(f"\nFAIL: {len(live)} declared cut(s) still in edges.tsv")
        return 1
    print("\nPASS: every declared cut is absent from the graph")
    return 0


if __name__ == "__main__":
    sys.exit(main())
