"""Is the parent/child edge asymmetry systemic, or was it local to Tros?

An edge lives in TWO places in this dump: the parent's P20 (Child) and the child's
P47 (Father) / P48 (Mother). During the Q74698 unmerge, fixing only the child side left
`Danaus -> Nilus` alive through the parent's P20, and two cycles that looked broken were
still closed. This scans every item to find out how widespread that is.

Read-only. Writes a summary to wikibase/analysis/edge_symmetry.txt.

    python wiki-scripts/edge_symmetry.py

Uses os.scandir + binary reads because Path.glob + text decode over 164k files on Windows
exceeded a 15-minute budget.
"""

import collections
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
OUT = ROOT / "wikibase" / "analysis" / "edge_symmetry.txt"


def scan():
    parent_side = set()   # (parent, child) from the parent's P20
    child_side = set()    # (parent, child) from the child's P47/P48
    n = bad = 0
    t0 = time.time()
    with os.scandir(ITEMS) as it:
        for e in it:
            if not e.name.endswith(".json"):
                continue
            try:
                with open(e.path, "rb") as fh:
                    d = json.loads(fh.read())
            except Exception:
                bad += 1
                continue
            if not isinstance(d, dict):
                bad += 1
                continue
            q = d.get("id") or e.name[:-5]
            claims = d.get("claims") or {}
            for c in claims.get("P20", ()):
                v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                if isinstance(v, dict) and v.get("id"):
                    parent_side.add((q, v["id"]))
            for pid in ("P47", "P48"):
                for c in claims.get(pid, ()):
                    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                    if isinstance(v, dict) and v.get("id"):
                        child_side.add((v["id"], q))
            n += 1
            if n % 20000 == 0:
                print(f"  ...{n} items, {time.time() - t0:.0f}s", flush=True)
    return parent_side, child_side, n, bad, time.time() - t0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fwd, rev, n, bad, secs = scan()
    both = fwd & rev
    only_parent = fwd - rev
    only_child = rev - fwd
    union = fwd | rev

    lines = [
        f"items scanned            : {n}  (unreadable/non-dict: {bad})  in {secs:.0f}s",
        f"edges from parent P20    : {len(fwd)}",
        f"edges from child P47/P48 : {len(rev)}",
        "",
        f"declared on BOTH sides   : {len(both):>7d}  ({100*len(both)/len(union):.1f}% of all edges)",
        f"parent side ONLY         : {len(only_parent):>7d}  (child has no P47/P48 back to it)",
        f"child side ONLY          : {len(only_child):>7d}  (parent has no P20 forward to it)",
        f"union (what edges.tsv holds): {len(union):>7d}",
        "",
        "Why this matters: any repair that edits only one side leaves the edge alive in the",
        "other, and the graph still contains it. edges.tsv is built from the UNION, so a",
        "half-removed edge still shows up as a real edge.",
        "",
        "sample parent-side-only edges:",
    ]
    for p, c in sorted(only_parent)[:15]:
        lines.append(f"    {p} -> {c}")
    lines.append("")
    lines.append("sample child-side-only edges:")
    for p, c in sorted(only_child)[:15]:
        lines.append(f"    {p} -> {c}")

    # how concentrated is the asymmetry?
    cnt = collections.Counter()
    for p, c in only_parent:
        cnt[p] += 1
    lines.append("")
    lines.append("records with the most parent-side-only children:")
    for q, k in cnt.most_common(10):
        lines.append(f"    {q}: {k}")

    text = "\n".join(lines)
    print(text)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"\nwritten -> {OUT}")


if __name__ == "__main__":
    main()
