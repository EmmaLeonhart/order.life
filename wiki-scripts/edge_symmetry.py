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
    # qid -> True if ANY file claiming it carries identifying or genealogical content.
    # A qid absent from this map has no file at all. Collected here rather than in a
    # second pass because the scan already reads every file and takes ~10 minutes.
    substantive = {}
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
            has_label = bool(((d.get("labels") or {}).get("en") or {}).get(
                "value", "").strip())
            has_alias = any(a.get("value", "").strip()
                            for a in (d.get("aliases") or {}).get("en", []))
            has_geneal = any(claims.get(p) for p in ("P47", "P48", "P20", "P42"))
            substantive[q] = (substantive.get(q, False)
                              or has_label or has_alias or has_geneal)

            n += 1
            if n % 20000 == 0:
                print(f"  ...{n} items, {time.time() - t0:.0f}s", flush=True)
    return parent_side, child_side, substantive, n, bad, time.time() - t0


CLASSIFIED = ROOT / "wikibase" / "analysis" / "edge_symmetry_classified.tsv"


def classify(only_parent, only_child, substantive):
    """Bucket every one-sided edge by what its endpoints actually are.

    queue.md item 4 says: decide per record whether the missing side should be ADDED or
    the present side REMOVED, and do NOT blanket-add, because some one-sided edges are
    half-finished deletions. 4,723 individual judgements is not a plan. This splits them
    so the unambiguous ones can be handled as a batch and the genuine judgement calls are
    what is left.

      DANGLING  an endpoint has no record anywhere -- no file, nothing claiming the qid.
                The edge points at nothing, so the declared side is removable with no
                judgement at all. This is the Q78402 shape: Cleopatra III named a
                nonexistent record as her mother, and removing it eliminated a tangle.
      PHANTOM   an endpoint exists but carries no label, alias or genealogical claim.
                A shell. Usually the one-sided edge is the only reason it is in the graph.
      BOTH-REAL both endpoints are substantive records. THESE ARE THE JUDGEMENT CALLS and
                the tool says nothing about which way they should go.
    """
    rows = []
    for side, edges in (("parent-only", only_parent), ("child-only", only_child)):
        for p, c in edges:
            sp = ("real" if substantive.get(p) else
                  "phantom" if p in substantive else "missing")
            sc = ("real" if substantive.get(c) else
                  "phantom" if c in substantive else "missing")
            if "missing" in (sp, sc):
                verdict = "DANGLING"
            elif "phantom" in (sp, sc):
                verdict = "PHANTOM"
            else:
                verdict = "BOTH-REAL"
            rows.append((verdict, side, p, sp, c, sc))
    rows.sort()
    return rows


def redirect_map():
    """from_qid -> to_qid, as extract_genealogy.py resolves them."""
    m = {}
    p = ROOT / "wikibase" / "analysis" / "redirects.tsv"
    if not p.exists():
        return m
    with p.open(encoding="utf-8") as f:
        for r in __import__("csv").DictReader(f, delimiter="\t"):
            m[r["from_qid"]] = r["to_qid"]
    return m


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fwd, rev, substantive, n, bad, secs = scan()

    # CANONICALISE THE ENDPOINTS BEFORE COMPARING THE TWO SIDES.
    #
    # Claims cite raw qids, and 39,521 qids in this dump are claimed by more than one
    # file, so a parent may name a child by a qid that redirects elsewhere while the child
    # declares the canonical one. Comparing raw pairs then reports a symmetric edge as
    # one-sided. extract_genealogy.py canonicalises for exactly this reason -- it turns
    # 129,282 raw parent edges into 128,669 canonical ones -- and this scan did not, so
    # every figure it produced before 2026-08-01 overstated the asymmetry.
    #
    # Found by spot-checking the classifier's DANGLING bucket: Q104933, Q107385 and
    # Q107411 were reported as records that do not exist, and all three are ordinary
    # shadow files whose internal id differs from their filename. The qid is vacated; the
    # person is not missing.
    red = redirect_map()

    def canon(q):
        for _ in range(8):
            nxt = red.get(q, q)
            if nxt == q:
                return q
            q = nxt
        return q

    raw_fwd, raw_rev = len(fwd), len(rev)
    fwd = {(canon(p), canon(c)) for p, c in fwd}
    fwd = {(p, c) for p, c in fwd if p != c}
    rev = {(canon(p), canon(c)) for p, c in rev}
    rev = {(p, c) for p, c in rev if p != c}

    both = fwd & rev
    only_parent = fwd - rev
    only_child = rev - fwd
    union = fwd | rev

    lines = [
        f"items scanned            : {n}  (unreadable/non-dict: {bad})  in {secs:.0f}s",
        f"edges from parent P20    : {len(fwd)}  (raw {raw_fwd}, before canonicalising)",
        f"edges from child P47/P48 : {len(rev)}  (raw {raw_rev})",
        "",
        "ENDPOINTS ARE CANONICALISED through redirects.tsv before the two sides are",
        "compared, as extract_genealogy.py does. Without that, a parent naming a child by",
        "a redirected qid while the child declares the canonical one reads as a one-sided",
        "edge when it is nothing of the kind. Every figure this file reported before",
        "2026-08-01 lacked that step and overstated the asymmetry.",
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

    rows = classify(only_parent, only_child, substantive)
    counts = collections.Counter(r[0] for r in rows)
    lines += [
        "",
        "ONE-SIDED EDGES BY WHAT THEIR ENDPOINTS ARE  (queue.md item 4)",
        f"  DANGLING  {counts['DANGLING']:>6d}  an endpoint has no record anywhere; the "
        f"edge points at nothing",
        f"  PHANTOM   {counts['PHANTOM']:>6d}  an endpoint is a shell with no label, alias "
        f"or genealogy",
        f"  BOTH-REAL {counts['BOTH-REAL']:>6d}  both endpoints are real records -- these "
        f"are the judgement calls",
        "",
        "DANGLING is removable with no judgement: a record that does not exist cannot be",
        "anyone's parent or child. PHANTOM is nearly so, but the shell exists and may be",
        "load-bearing elsewhere. BOTH-REAL is the part queue.md warns against blanket-",
        f"fixing, and it is {counts['BOTH-REAL']} of the {len(rows)}.",
        "",
        f"Per-edge detail: {CLASSIFIED.name}",
    ]

    with CLASSIFIED.open("w", encoding="utf-8", newline="") as f:
        f.write("verdict\tside\tparent\tparent_kind\tchild\tchild_kind\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    text = "\n".join(lines)
    print(text)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"\nwritten -> {OUT}")
    print(f"written -> {CLASSIFIED}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
