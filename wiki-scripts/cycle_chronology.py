"""Find the chronologically impossible edge in each remaining cycle.

BC dates in this dump are stored with a '+' sign: Quintus Mucius Scaevola Pontifex has
birth +0140 and death +0082, i.e. he dies 58 years before he is born. So `death < birth`
is a reliable detector for "this record is BC and the sign is wrong", and correcting it
makes chronology usable.

A parent must be born before their child. Once signs are fixed, the edge with the largest
violation in a cycle is the one to look at first -- in the big Roman cycle it is a
4th-century-AD Constantinian descending into the 3rd-century-BC Republic, a ~550 year jump.

Read-only. Prints a ranked cut list; applies nothing.

    python wiki-scripts/cycle_chronology.py
"""

import collections
import csv
import re
import sys
from pathlib import Path

A = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"

PERSONS = {r["qid"]: r for r in
           csv.DictReader(open(A / "persons.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)}


def _raw(q, field):
    m = re.match(r"([+-])(\d+)", (PERSONS.get(q) or {}).get(field) or "")
    if not m:
        return None
    y = int(m.group(2))
    return -y if m.group(1) == "-" else y


def year(q):
    """Birth year with the BC sign repaired. Returns (year, confident)."""
    b, d = _raw(q, "birth"), _raw(q, "death")
    if b is None:
        return None, False
    if d is not None and d < b:
        # dies before born => both are BC stored positive
        return -b, True
    if d is not None:
        return b, True
    return b, False          # no death date: sign unverifiable, treat as weak


def label(q):
    return (PERSONS.get(q) or {}).get("label") or "?"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = list(csv.DictReader(open(A / "qa_cycles.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    violations = collections.Counter()
    detail = {}
    for r in rows:
        ch = [x.strip() for x in r["chain_qids"].split("->")]
        worst, worst_edge = 0, None
        for p, c in zip(ch, ch[1:]):
            yp, cp = year(p)
            yc, cc = year(c)
            if yp is None or yc is None or not (cp and cc):
                continue
            gap = yp - yc          # parent born AFTER child => positive gap => impossible
            if gap > worst:
                worst, worst_edge = gap, (p, c)
        if worst_edge:
            violations[worst_edge] += 1
            detail[worst_edge] = worst

    print(f"{len(rows)} cycles; {len(violations)} distinct worst-violation edges\n")
    print(f"{'cycles':>7s} {'gap_yrs':>8s}  edge")
    for edge, n in violations.most_common():
        p, c = edge
        yp, _ = year(p)
        yc, _ = year(c)
        print(f"{n:7d} {detail[edge]:8d}  {p} {label(p)[:34]:36s} (b {yp:>5d})")
        print(f"{'':7s} {'':8s}  -> {c} {label(c)[:34]:36s} (b {yc:>5d})")

    covered = sum(violations.values())
    print(f"\n{covered} of {len(rows)} cycles have at least one provably impossible edge")
    print(f"{len(rows) - covered} have none -- undated, or dates too weak to judge")


if __name__ == "__main__":
    main()
