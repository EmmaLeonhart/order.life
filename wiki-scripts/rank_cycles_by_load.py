#!/usr/bin/env python
"""Rank ancestry cycles by what actually breaks if you cut them. READ-ONLY.

    python wiki-scripts/rank_cycles_by_load.py

Writes `wikibase/analysis/qa_cycles_load.tsv`.

Counting descendants does NOT rank these cycles. Thirteen of them score identically at
34,365 because they all sit in the Greek mythic tier that the whole giant component
hangs below — the number measures depth in the graph, not importance.

What matters is whether an edge is a BRIDGE: the only route by which people descend from
the gateway ancestors this project cares about. So for every cycle edge this removes it
and re-walks the graph from the gateways, reporting how many people lose their descent
entirely. An edge whose removal orphans nobody is safe to cut however impressive the
cycle looks; an edge that orphans thousands needs a human before anyone touches it.

Gateways are the load-bearing ancestors named in GENEALOGY_QA.md, plus Adam.
"""

import csv
import io
import sys
from collections import defaultdict, deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "wikibase" / "analysis"
OUT = ANALYSIS / "qa_cycles_load.tsv"

GATEWAYS = {
    "Q138545": "Jesus Christ",
    "Q115039": "Charlemagne",
    "Q65705": "Muhammad",
    "Q87872": "Bustanai",
    "Q37401": "Genghis Khan",
    "Q30266": "Confucius",
    "Q51928": "Heo Hwang-ok",
    "Q152973": "Adam",
}

csv.field_size_limit(10_000_000)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def rows(name):
    with open(ANALYSIS / name, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def reach(children, seeds, skip=None):
    """Everyone descended from `seeds`, optionally ignoring one edge."""
    seen = set(seeds)
    dq = deque(seeds)
    while dq:
        n = dq.popleft()
        for c in children.get(n, ()):
            if skip is not None and (n, c) == skip:
                continue
            if c not in seen:
                seen.add(c)
                dq.append(c)
    return seen


def main():
    persons = {r["qid"]: r for r in rows("persons.tsv")}
    children = defaultdict(set)
    for r in rows("edges.tsv"):
        children[r["parent"]].add(r["child"])

    def lab(q):
        return " ".join((persons.get(q, {}).get("label") or "").split()) or q

    seeds = [q for q in GATEWAYS if q in persons]
    missing = [GATEWAYS[q] for q in GATEWAYS if q not in persons]
    if missing:
        sys.stderr.write("gateway not in dump, skipped: %s\n" % ", ".join(missing))

    base = reach(children, seeds)
    print("people descended from the %d gateways: %d of %d (%.1f%%)"
          % (len(seeds), len(base), len(persons), 100.0 * len(base) / len(persons)))

    cycles = []
    for r in rows("qa_cycles.tsv"):
        chain = r["chain_qids"].split(" -> ")
        cycles.append({"len": int(r["cycle_len"]), "chain": chain,
                       "edges": [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]})

    edges = sorted({e for cy in cycles for e in cy["edges"]})
    sys.stderr.write("testing %d distinct cycle edges...\n" % len(edges))
    orphaned = {}
    for i, e in enumerate(edges, 1):
        orphaned[e] = len(base) - len(reach(children, seeds, skip=e))
        if i % 100 == 0:
            sys.stderr.write("  %d/%d\n" % (i, len(edges)))

    out = []
    for cy in cycles:
        losses = [orphaned[e] for e in cy["edges"]]
        cheapest = min(losses)
        worst = max(losses)
        best_edge = cy["edges"][losses.index(cheapest)]
        out.append({
            "cycle_len": cy["len"],
            "head": "%s (%s)" % (cy["chain"][0], lab(cy["chain"][0])),
            "cheapest_cut_loses": cheapest,
            "worst_edge_loses": worst,
            "cheapest_cut": "%s (%s) -> %s (%s)" % (
                best_edge[0], lab(best_edge[0]), best_edge[1], lab(best_edge[1])),
            "verdict": ("free to cut" if cheapest == 0 else
                        "cheap" if cheapest < 10 else
                        "costly" if cheapest < 1000 else "load-bearing"),
        })

    out.sort(key=lambda r: (-r["cheapest_cut_loses"], -r["cycle_len"]))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n",
                           fieldnames=["cycle_len", "head", "cheapest_cut_loses",
                                       "worst_edge_loses", "cheapest_cut", "verdict"])
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    v = Counter(r["verdict"] for r in out)
    print("\nwrote %s" % OUT)
    print("\ncycles by the cost of their CHEAPEST available cut:")
    for k in ("free to cut", "cheap", "costly", "load-bearing"):
        if v[k]:
            print("  %-14s %d" % (k, v[k]))

    hard = [r for r in out if r["cheapest_cut_loses"] > 0]
    print("\ncycles with no free cut (every edge orphans someone): %d" % len(hard))
    for r in hard[:15]:
        print("  loses %-6d len %-3d %s" % (r["cheapest_cut_loses"], r["cycle_len"],
                                            r["cheapest_cut"][:78]))

    print("\nmost load-bearing single edges in the whole cycle set:")
    for e, n in sorted(orphaned.items(), key=lambda kv: -kv[1])[:12]:
        if n:
            print("  %-7d %s -> %s" % (n, lab(e[0])[:34], lab(e[1])[:34]))


if __name__ == "__main__":
    main()
