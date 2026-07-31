"""How much of the genealogy is decided by filename order?

39,533 qids in this dump are claimed by more than one file (57,410 shadow files).
extract_genealogy.py keeps only the FIRST file it encounters per qid:

    qid = data.get("id") or file_qid
    if qid in seen_ids: continue

`files` is sorted NUMERICALLY by QID, so the winner is the lowest QID number -- and shadow
files often carry genealogical claims the winner does not. Every such disagreement is an edge
that exists, or fails to exist, because of a filename.

This found the Cato cycle: canonical Q73005.json had P47=[], while five shadows all carry
P47=['Q73167']. Q73005 is numerically lowest so it won and suppressed them. Merging it into
Q148133 vacated qid Q73005, a shadow won instead, and the injected edge closed a loop.

Read-only. Writes wikibase/analysis/shadow_audit.md.

    python wiki-scripts/shadow_audit.py
"""

import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
OUT = ROOT / "wikibase" / "analysis" / "shadow_audit.md"

GEN = ("P20", "P47", "P48")  # child, father, mother -- the claims that make edges
NAMES = {"P20": "child", "P47": "father", "P48": "mother"}


def vals(claims, pid):
    out = set()
    for c in claims.get(pid, ()):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.add(v["id"])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # qid -> {filename: {pid: set(values)}}
    byqid = collections.defaultdict(dict)
    n = 0
    with os.scandir(ITEMS) as it:
        for e in it:
            if not e.name.endswith(".json"):
                continue
            try:
                with open(e.path, "rb") as fh:
                    d = json.loads(fh.read())
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            fq = e.name[:-5]
            qid = d.get("id") or fq
            claims = d.get("claims") or {}
            byqid[qid][fq] = {p: vals(claims, p) for p in GEN}
            n += 1
            if n % 40000 == 0:
                print(f"  ...{n}", flush=True)

    multi = {q: fs for q, fs in byqid.items() if len(fs) > 1}
    disagree = {}
    lost_edges = 0
    phantom_edges = 0
    for q, files in multi.items():
        # extract_genealogy.py sorts NUMERICALLY, not lexicographically:
        #     files = sorted(ITEMS.glob("Q*.json"), key=lambda p: int(p.stem[1:]))
        # so the winner is the LOWEST QID NUMBER. Getting this wrong names the wrong
        # winner for every record whose shadows differ in digit count.
        winner = min(files, key=lambda f: int(f[1:]))
        wclaims = files[winner]
        union = {p: set().union(*(f[p] for f in files.values())) for p in GEN}
        diff = {p: sorted(union[p] - wclaims[p]) for p in GEN if union[p] - wclaims[p]}
        if diff:
            disagree[q] = (winner, diff)
            for p, v in diff.items():
                lost_edges += len(v)
        # claims the winner has that no other file has -- these exist only by filename luck
        others = {p: set().union(*(f[p] for fn, f in files.items() if fn != winner)) for p in GEN}
        for p in GEN:
            phantom_edges += len(wclaims[p] - others[p])

    lines = [
        "# How much of the genealogy is decided by filename order?",
        "",
        "**2026-07-30. Read-only audit, produced by `wiki-scripts/shadow_audit.py`.**",
        "",
        "`extract_genealogy.py` keeps only the first file it sees per qid, and sorts files",
        "NUMERICALLY by QID, so the winner is the **lowest QID number**. Shadow files carry",
        "genealogical claims the winner does not. Each disagreement is an edge that exists,",
        "or fails to exist, because of a filename.",
        "",
        "## Scale",
        "",
        f"- items read: **{n:,}**",
        f"- distinct qids: **{len(byqid):,}**",
        f"- qids claimed by more than one file: **{len(multi):,}**",
        f"- of those, qids where the files DISAGREE on parents/children: **{len(disagree):,}**",
        f"- edges suppressed because the winning file lacks them: **{lost_edges:,}**",
        f"- edges present ONLY because the winner happens to have them: **{phantom_edges:,}**",
        "",
        "The suppressed edges are the dangerous ones for merges: vacating a qid lets a",
        "shadow win and injects them, which is exactly how the Cato 2-cycle appeared.",
        "",
        "## Worst offenders (most suppressed claims)",
        "",
        "| qid | winning file | suppressed claims |",
        "|---|---|---|",
    ]
    ranked = sorted(disagree.items(), key=lambda kv: -sum(len(v) for v in kv[1][1].values()))
    for q, (winner, diff) in ranked[:25]:
        desc = "; ".join(f"{NAMES[p]}={v}" for p, v in diff.items())
        lines.append(f"| {q} | {winner}.json | {desc[:90]} |")

    lines += [
        "",
        "## What this means",
        "",
        "The graph as it stands is not the union of what the dump asserts -- it is one",
        "arbitrary selection from it. Re-sorting the item directory, or renaming a file,",
        "would silently change the genealogy. Because the sort is numeric, the winner is",
        "simply whichever import happened to land on the smaller QID, which carries no",
        "meaning at all.",
        "",
        "**Not resolved here, deliberately.** Deciding whether the winner or a shadow is",
        "right is a per-record judgement, and this dump is a synoptic mythology where",
        "surprising content is usually intentional. Options, for Emma:",
        "",
        "1. **Union everything** -- take every claim any file makes. Maximises connection,",
        "   which suits a genealogy built to link traditions, but will add cycles and",
        "   multi-parent records.",
        "2. **Keep winner-takes-all** -- accept the status quo, but make it explicit rather",
        "   than accidental by collapsing shadows into their target.",
        "3. **Union only where it adds no cycle** -- run `check_invariants.py` per batch and",
        "   keep the claims that do not regress it.",
        "",
        "Option 1 is the one most in keeping with what the genealogy is for; option 3 is the",
        "one that will not make the cycle backlog worse. They can be combined by unioning",
        "first and treating the resulting cycles as ordinary repair work.",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:22]))
    print(f"\nwritten -> {OUT}")


if __name__ == "__main__":
    main()
