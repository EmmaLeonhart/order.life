"""Break the Roman mutual-parent cycles, preserving every record.

Roman tria nomina repeat father-to-son, so a name-matching import linked father and son in
BOTH directions. The result is a 2-cycle: each man is his own father. Nothing is deleted --
only the wrong direction of each edge is removed, and an edge must be removed from BOTH
places it lives (the parent's P20 and the child's P47/P48).

Three pairs checked and found ALREADY one-directional, left untouched:
    Publius Aelius Marullinus  Q70388 -> Q69886   (descriptions confirm: great-great-
                                                   grandfather -> great-grandfather of Hadrian)
    Marcus Granius             Q78507 -> Q78384
    Gaius Servilius            Q73910 -> Q73812
Those were listed as cut candidates in cycle_origins.md off qa_cycles_proposed.tsv, which is
stale -- commit 9c0299d8 already repaired them.

Idempotent. Verifies after writing.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"

# (parent, child, why) -- the WRONG direction, to be removed from both sides.
BAD_EDGES = [
    ("Q73470", "Q73323",
     "Titus Manlius Torquatus: Q73323's real father is Lucius Manlius Capitolinus "
     "Imperiosus (Q73901), already recorded. Q73470 is his SON, not also his father."),
    ("Q99410", "Q73470",
     "Titus Manlius Torquatus: Q99410 is an unnamed stub recorded as both father and "
     "child of Q73470. Keep it as the child, drop the father direction."),
    ("Q73872", "Q73958",
     "Lucius Fulvius: the dump's own numbering gives Q73958 'Lucius Fulvius, II' a father "
     "'Lucius Fulvius, I' (Q99418). The line is I -> II -> Curvus, so Curvus (Q73872) is "
     "II's son, not also his father."),
    ("Q78615", "Q78501",
     "Valerius: Q78501 'Marcus Valerius' already has a father outside the cycle, "
     "'Marcus Valerius' Q99737. Manius (Q78615) is his son, not also his father."),
]

# pairs deliberately NOT touched -- asserted clean, and checked at runtime
ALREADY_CLEAN = [("Q70388", "Q69886"), ("Q78507", "Q78384"), ("Q73910", "Q73812")]


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(q, d):
    (ITEMS / f"{q}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def drop(d, pid, qid):
    claims = (d.get("claims") or {}).get(pid)
    if not claims:
        return 0
    kept = []
    for c in claims:
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if (v.get("id") if isinstance(v, dict) else v) != qid:
            kept.append(c)
    n = len(claims) - len(kept)
    if kept:
        d["claims"][pid] = kept
    elif n:
        del d["claims"][pid]
    return n


def lab(q):
    d = load(q)
    return (d["labels"].get("en", {}).get("value", "?") if d else "?")


def edge_live(p, c):
    dp, dc = load(p), load(c)
    return (dp and c in vals(dp, "P20")) or (dc and p in vals(dc, "P47") + vals(dc, "P48"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    print("=== pairs asserted already one-directional ===")
    ok = True
    for a, b in ALREADY_CLEAN:
        back = edge_live(b, a)
        print(f"  {a} -> {b} : reverse edge present? {back}  "
              f"({lab(a)!r})")
        if back:
            ok = False
    if not ok:
        print("  WARNING: a pair assumed clean is actually mutual. Not writing.")
        return 1

    print("\n=== removing the wrong direction of each mutual edge ===")
    total = 0
    for parent, child, why in BAD_EDGES:
        print(f"\n  {parent} ({lab(parent)}) -> {child} ({lab(child)})")
        print(f"    {why}")
        dp = load(parent)
        n1 = drop(dp, "P20", child) if dp else 0
        if n1:
            save(parent, dp)
        dc = load(child)
        n2 = drop(dc, "P47", parent) if dc else 0
        n3 = drop(dc, "P48", parent) if dc else 0
        if n2 or n3:
            save(child, dc)
        print(f"    removed: parent-side P20 x{n1}, child-side P47 x{n2}, P48 x{n3}")
        total += n1 + n2 + n3

    print("\n=== verify: every targeted edge gone, every record still present ===")
    for parent, child, _ in BAD_EDGES:
        print(f"  {parent} -> {child} still live? {edge_live(parent, child)}   "
              f"| reverse {child} -> {parent} kept? {edge_live(child, parent)}")
    for q in sorted({q for e in BAD_EDGES for q in e[:2]}):
        print(f"  record {q} exists: {load(q) is not None}  ({lab(q)!r})")
    print(f"\n{total} claim(s) removed. No record deleted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
