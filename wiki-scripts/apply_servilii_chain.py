"""The eight Servilii: a bridging chain whose end was tied back to its start.

    python wiki-scripts/apply_servilii_chain.py           # dry run
    python wiki-scripts/apply_servilii_chain.py --write   # apply

THE RING (tangle 5, eight records)

    Q73170 -> Q73985 -> Q73910 -> Q73812 -> Q73710 -> Q73599 -> Q73479 -> Q73332 -> Q73170

Eight placeholder Servilii, each with exactly one father and one in-ring child. Not one
carries a Wikidata id, a date or a cognomen -- "Gaius Servilius" x3, "Quintus Servilius"
x2, "Publius Servilius", "Gnaeus Servilius" and one bare "Servilius". queue.md item 11
concluded there was "no evidence in it at all" and that six of the eight edges were
indistinguishable.

The evidence is not in the ring. It is in the two branches that leave it.

DATING THE TWO EXITS -- both anchors are OUTSIDE the ring, so this is not circular

Only two members have a child outside the ring, and both of those lines are datable:

  Q73170 -> Q73008 Marcus Servilius
      -> 5 generations -> Q71173 **Publius Servilius Vatia Isauricus, b. 120 BC**
         (wd Q392647; the dump stores it +0120 under the positive-sign bug)
      So Q73170 stands six generations above 120 BC: **c. 300 BC.**

  Q73910 -> Q78378 Gaius Servilius
      -> 10 generations -> Q89776 **Claudia Acilia, b. 185 AD**, and on to the Anicii
      So Q73910 stands eleven generations above AD 185: **c. 145 BC.**

THE CONTRADICTION, and which single edge carries it

The ring's first arc, Q73170 -> Q73985 -> Q73910, makes Q73910 two generations younger
than Q73170: c. 300 BC + 60 = c. 240 BC against his anchor of c. 145 BC. Loose, but the
right direction, and item 11 already ruled those two edges out on exactly that ground.

The ring's remaining arc runs the other way round: Q73910 -> Q73812 -> Q73710 -> Q73599
-> Q73479 -> Q73332 -> Q73170, making Q73170 **six generations younger than Q73910** --
c. 145 BC + 180 = **c. AD 35**, against his own external anchor of **c. 300 BC**. A
contradiction of roughly 335 years.

Every edge in that arc is consistent with a chain descending from Q73910. Only the last
one collides with an externally dated record: **Q73332 -> Q73170**, which asks a man of
c. 90 BC to father a man of c. 300 BC. That is the cut.

WHAT IT COSTS: NOTHING

Verified against the dump before writing: Q73170's only ancestors are the other seven ring
members, and **the component does not reach Aster**. Cutting his father edge severs no
line, because there is no line above it -- it makes him a root, which is what an
unattested placeholder at the head of a bridging chain should be.

What is left is the chain the eight records were presumably built to be: Republican
Servilii at the top, the Imperial branch hanging off the third link, and nothing looping
back. Where that chain should attach above Q73170 is a question about the story, and
therefore Emma's; it is filed in todo.md rather than guessed at here.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER = "P20", "P47", "P48"

CHILD = "Q73170"    # Gaius Servilius, c. 300 BC by his Vatia Isauricus descent
FATHER = "Q73332"   # Publius Servilius, c. 90 BC -- seven links below him in the ring

RING = ["Q73170", "Q73985", "Q73910", "Q73812", "Q73710",
        "Q73599", "Q73479", "Q73332"]


def load(stem):
    path = ITEMS / f"{stem}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def save(stem, data):
    (ITEMS / f"{stem}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def values(data, pid):
    out = []
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def drop_claim(data, pid, qid):
    claims = (data.get("claims") or {}).get(pid)
    if not claims:
        return 0
    keep = []
    for c in claims:
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id") == qid:
            continue
        keep.append(c)
    removed = len(claims) - len(keep)
    if keep:
        data["claims"][pid] = keep
    else:
        del data["claims"][pid]
    return removed


def siblings():
    out = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["to_qid"]].add(r["from_qid"])
            out[r["to_qid"]].add(r["to_qid"])
    return out


def family_of(qid, sib):
    out = []
    for stem in sorted(sib.get(qid, set()) | {qid}, key=lambda x: int(x[1:])):
        data = load(stem)
        if data is not None and (data.get("id") or stem) == qid:
            out.append(stem)
    return out


def parents_of(qid, sib):
    out = set()
    for stem in family_of(qid, sib):
        data = load(stem)
        out |= set(values(data, P_FATHER)) | set(values(data, P_MOTHER))
    return out


def ancestors(start, sib, limit=200):
    """Returns (set of ancestors, whether start is its own ancestor)."""
    seen, frontier, closed, depth = {start}, {start}, False, 0
    while frontier and depth < limit:
        nxt = set()
        for node in frontier:
            for p in parents_of(node, sib):
                if p == start:
                    closed = True
                if p not in seen:
                    seen.add(p)
                    nxt.add(p)
        frontier = nxt
        depth += 1
    return seen - {start}, closed


def main():
    write = "--write" in sys.argv
    sib = siblings()

    # Refuse to run if cutting would cost real ancestry. The whole justification is that
    # this component hangs from nothing, so check it rather than repeat item 11's claim.
    anc, _ = ancestors(CHILD, sib)
    outside = anc - set(RING)
    print(f"{CHILD} ancestors today: {len(anc)} -- {sorted(anc)}")
    if outside:
        sys.exit(f"ABORT: {CHILD} has ancestry outside the ring ({sorted(outside)}); "
                 f"cutting would sever a real line, so the defect is elsewhere")
    if "Q1" in anc:
        sys.exit(f"ABORT: {CHILD} reaches Aster; cutting would disconnect it")
    print("Its only ancestors are the other ring members, and it does not reach Aster.\n")

    staged = {}
    for stem in family_of(CHILD, sib):
        data = staged.get(stem) or load(stem)
        n = drop_claim(data, P_FATHER, FATHER)
        staged[stem] = data
        if n:
            print(f"  {stem}.json ({CHILD}): dropped father {FATHER} x{n} "
                  f"-- fathers left: {values(data, P_FATHER) or 'none, now a root'}")
    for stem in family_of(FATHER, sib):
        data = staged.get(stem) or load(stem)
        n = drop_claim(data, P_CHILD, CHILD)
        staged[stem] = data
        if n:
            print(f"  {stem}.json ({FATHER}): dropped child {CHILD} x{n} "
                  f"-- children left: {len(values(data, P_CHILD))}")

    edits = list(staged.items())
    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for stem in family_of(CHILD, sib):
        if FATHER in values(load(stem), P_FATHER):
            bad.append(f"{stem}.json still has father {FATHER}")
    for stem in family_of(FATHER, sib):
        if CHILD in values(load(stem), P_CHILD):
            bad.append(f"{stem}.json still lists child {CHILD}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1

    print("\nRing walk -- expecting a straight chain, 0 ancestors at the head:")
    closed_any = False
    for q in RING:
        a, closed = ancestors(q, sib)
        closed_any |= closed
        print(f"  {q}: {'CLOSED' if closed else 'open'}, {len(a)} ancestors")
    if closed_any:
        print("\nStill closed -- the repair did not do what it claims.")
        return 1
    print("\nRing open. Eight Servilii in a line, Republican at the head.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
