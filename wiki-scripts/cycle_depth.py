"""Classify each ancestry cycle by DEPTH, not width.

Emma, 2026-07-30: the genealogy is a literary device linking people across time and space.
The priority is ancestry going DEEP, not ancestry going WIDE. qa_cycles_load.tsv scores
cycles by descendant count, which is width, which is the wrong metric.

Read-only. Writes nothing. Reproduces wikibase/analysis/cycle_depth.md.

    python wiki-scripts/cycle_depth.py

Per cycle it computes:
  depth_above   longest ancestor chain reachable ABOVE the cycle, not counting cycle members.
                This is the depth the cycle is carrying. If 0, the cycle is the terminal
                point of that line and severing it loses no depth at all.
  entry         cycle members that are a parent of someone OUTSIDE the cycle -- the point
                through which the rest of the genealogy reaches the loop. Emma: keep the
                entry point, drop the rest, when the loop is terminal.
  depth_below   longest descendant chain below the entry point, i.e. how much genealogy is
                hanging off this loop.
  significant   members carrying a wikidata_qid -- real figures that can be looked up.
  unmerge       pairs inside the cycle with near-identical labels but DIFFERENT wikidata
                ids. Emma: these are improper merges; the fix is to unmerge, not to cut.

Verdicts:
  TERMINAL-DROP    depth_above == 0 and no significant figures. Keep entry, drop the rest.
  UNMERGE          a same-name pair with distinct wikidata ids. Unmerge, do not cut.
  DEEP-KEEP        depth_above is large. Do NOT cut blind; the loop is carrying real depth.
  NEEDS-LOOKUP     significant figures present but no clean unmerge pair.
"""

import collections
import csv
import difflib
import re
import sys
from pathlib import Path

A = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"

PERSONS = {r["qid"]: r for r in csv.DictReader(open(A / "persons.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)}
PARENTS, CHILDREN = collections.defaultdict(set), collections.defaultdict(set)
for _r in csv.DictReader(open(A / "edges.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
    PARENTS[_r["child"]].add(_r["parent"])
    CHILDREN[_r["parent"]].add(_r["child"])
PROPOSED = list(csv.DictReader(open(A / "qa_cycles_proposed.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))


def label(q):
    return (PERSONS.get(q) or {}).get("label") or "<no row>"


def wd(q):
    return ((PERSONS.get(q) or {}).get("wikidata_qid") or "").strip()


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", (s or "").lower())).strip()


def bfs(starts, adj, blocked):
    """BFS from `starts` following `adj`, never entering `blocked`.
    Returns (reachable_set, max_level). Well-defined on a cyclic graph -- unlike
    longest-simple-path, which is NP-hard and which an earlier version of this file
    approximated with an unsound memo."""
    seen, level, frontier, lvl = set(), 0, [s for s in starts if s not in blocked], 0
    seen.update(frontier)
    while frontier:
        lvl += 1
        nxt = []
        for node in frontier:
            for n in adj.get(node, ()):
                if n not in blocked and n not in seen:
                    seen.add(n)
                    nxt.append(n)
        if nxt:
            level = lvl
        frontier = nxt
    return seen, level


def lost_if_dropped(nodes, entry):
    """Records reachable upward ONLY through the cycle's non-entry members.
    This is literally 'what disappears if we keep the entry point and drop the rest'."""
    nodeset = set(nodes)
    drop = nodeset - set(entry)
    if not drop:
        return set()
    via_drop, _ = bfs({p for q in drop for p in PARENTS.get(q, ())}, PARENTS, nodeset)
    via_entry, _ = bfs({p for q in entry for p in PARENTS.get(q, ())}, PARENTS, drop | set())
    return via_drop - via_entry


def analyse(chain_qids):
    nodes = list(dict.fromkeys(chain_qids))  # dedupe, preserve order
    nodeset = set(nodes)

    ext_ancestors = {p for q in nodes for p in PARENTS.get(q, ()) if p not in nodeset}
    ext_children = {c for q in nodes for c in CHILDREN.get(q, ()) if c not in nodeset}
    entry = [q for q in nodes if CHILDREN.get(q, set()) - nodeset]

    anc, depth_above = bfs(ext_ancestors, PARENTS, nodeset)
    desc, depth_below = bfs(ext_children, CHILDREN, nodeset)
    lost = lost_if_dropped(nodes, entry)

    significant = [q for q in nodes if wd(q)]

    unmerge = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            la, lb = norm(label(a)), norm(label(b))
            if not la or not lb:
                continue
            sim = difflib.SequenceMatcher(None, la, lb).ratio()
            if sim >= 0.85 and wd(a) and wd(b) and wd(a) != wd(b):
                unmerge.append((a, b, round(sim, 2)))
            elif sim >= 0.95 and not (wd(a) and wd(b)):
                unmerge.append((a, b, round(sim, 2)))

    lost_n = len(lost)
    if lost_n == 0 and not significant:
        verdict = "TERMINAL-DROP"      # nothing above is lost, no lookupable figures
    elif unmerge:
        verdict = "UNMERGE"            # improper merge; unmerge rather than cut
    elif lost_n == 0:
        verdict = "TERMINAL-DROP"
    elif lost_n >= 50:
        verdict = "DEEP-KEEP"          # dropping the loop truncates real depth
    else:
        verdict = "NEEDS-LOOKUP"

    return dict(nodes=nodes, depth_above=depth_above, depth_below=depth_below, entry=entry,
                significant=significant, unmerge=unmerge, verdict=verdict,
                n_anc=len(anc), n_desc=len(desc), lost=len(lost))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    tally = collections.Counter()
    rows = []
    for r in PROPOSED:
        chain = [x.strip() for x in r["chain_qids"].split("->")]
        a = analyse(chain[:-1])
        a["len"] = int(r["cycle_len"])
        a["head"] = chain[0]
        rows.append(a)
        tally[a["verdict"]] += 1

    print("=" * 78)
    print("VERDICT TALLY")
    print("=" * 78)
    for k, v in tally.most_common():
        print(f"  {v:3d}  {k}")
    print()

    for verd in ("TERMINAL-DROP", "UNMERGE", "DEEP-KEEP", "NEEDS-LOOKUP"):
        sel = [x for x in rows if x["verdict"] == verd]
        if not sel:
            continue
        print("=" * 78)
        print(f"{verd}  ({len(sel)} cycles)")
        print("=" * 78)
        for x in sorted(sel, key=lambda y: -y["lost"]):
            print(f"len={x['len']:<3d} LOST={x['lost']:<5d} anc={x['n_anc']:<5d}(d{x['depth_above']:<3d}) "
                  f"desc={x['n_desc']:<5d}(d{x['depth_below']:<3d}) wd={len(x['significant'])}/{len(x['nodes'])}  "
                  f"{x['head']} {label(x['head'])[:30]}")
            if x["entry"]:
                print(f"      entry: " + ", ".join(f"{q} {label(q)[:26]}" for q in x["entry"][:3]))
            for a, b, s in x["unmerge"][:2]:
                print(f"      unmerge sim={s}: {a} {label(a)[:30]} [wd {wd(a) or '-'}]"
                      f"  <->  {b} {label(b)[:30]} [wd {wd(b) or '-'}]")
        print()


if __name__ == "__main__":
    main()
