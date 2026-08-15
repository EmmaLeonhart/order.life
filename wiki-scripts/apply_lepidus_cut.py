"""Open the Aemilii Lepidi / Scipiones ring: Quintus's father is Q144279, not Q72786.

    python wiki-scripts/apply_lepidus_cut.py           # dry run
    python wiki-scripts/apply_lepidus_cut.py --write   # apply

The 15-record tangle closes on this edge:

    ... -> Q72957 Scipio Nasica Serapio -> Q72801 Cornelia -> Q72786 -> Q72615 Quintus
        -> Q72434 Marcus Aemilius Lepidus -> ... back into the Scipiones

wikibase/analysis/lepidus_resolved.md settled it by looking the records up on Wikidata
rather than reasoning from the dump. Q72615 "Quintus Aemilius Lepidus" carries TWO fathers,
Q72786 and Q144279, both labelled "Marcus Aemilius Lepidus". Wikidata's Q3625112 -- the
tribunus militum of 190 BC, which is the dump's Q144279, and the identification is certain
because the dump's b=+0210/d=+0190 are Wikidata's -0210/-0190 -- lists exactly two
children: Q3622705 (the consul of 126 BC, the dump's Q73011) and Q11944252 Quintus
Aemilius Lepidus.

So Quintus's father is Q144279, the dump already records it, and the competing Q72786 edge
is the false one. Removing it needs no judgement call: it assigns the son nowhere new, and
the surviving edge is already present. This is the minimum cut that opens the ring.

WHAT THIS DELIBERATELY DOES NOT DO

Q72786 is a name collision -- Wikidata's Q721477 is a *Mamercus* Aemilius Lepidus
Livianus, born a Livius Drusus and adopted into the Aemilii Lepidi, which is why he
carries an Aemilian father and a mother described as "wife of Drusus". The full unmerge
also wants his biological father Q703346 added and the two fathers marked
adoptive-vs-biological, and couples B (Q73113/Q73110) and C (Q73173) assigned to whichever
men they actually belong to. None of that is settled -- those three records carry no
Wikidata ids and have not been identified, and naming the split records is Emma's.

Cutting the false Quintus edge is separable from all of it and is what the ring needs.
The rest stays open in queue.md rather than being guessed at here.

Shadow-aware -- Q72615 is claimed by 5 files and Q72786 by 12, and editing the canonical
file alone reverts the moment it stops being the numerically-lowest claimant. Idempotent.

REDIRECT-AWARE, AND IT WAS NOT (fixed 2026-08-15)

This script ran on 2026-08-07, printed "Verified", and left the edge alive. Q72786's P20
did not spell the child "Q72615"; it spelled it "Q72693", the qid merged away into Q72615
on 2026-07-31, which redirects.tsv still maps to it. drop_claim compared the raw id, so it
matched nothing and removed nothing -- and then the verify block compared the raw id too,
so it also saw nothing and reported success. Both halves were wrong in the same direction,
which is why the failure was silent: extract_genealogy.py resolves redirects, so the edge
reappeared in edges.tsv and the 15-record tangle never opened.

The lesson is queue.md's own, one layer down: an edge lives in the child's P47/P48 AND the
parent's P20, and either side may spell the other under any qid that redirects to it. So
comparisons here resolve through redirects.tsv before matching. A vacated qid is not dead
data -- it is a live alias.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER = "P20", "P47"

CHILD = "Q72615"        # Quintus Aemilius Lepidus
FALSE_FATHER = "Q72786" # the Mamercus record -- not his father
TRUE_FATHER = "Q144279" # M. Aemilius Lepidus, tr. mil. 190 BC (wd Q3625112)


def load(stem):
    path = ITEMS / f"{stem}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def save(stem, data):
    (ITEMS / f"{stem}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


_REDIRECTS = None


def resolve(qid):
    """Map a qid through redirects.tsv, the way extract_genealogy.py does.

    Every comparison in this script goes through here. A claim naming a merged-away qid
    is the same edge as one naming its survivor, because the extractor resolves it before
    writing edges.tsv -- so a cut that matches only the survivor's spelling cuts nothing.
    """
    global _REDIRECTS
    if _REDIRECTS is None:
        _REDIRECTS = {}
        with open(REDIRECTS, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                _REDIRECTS[r["from_qid"]] = r["to_qid"]
    seen = set()
    while qid in _REDIRECTS and qid not in seen:
        seen.add(qid)
        qid = _REDIRECTS[qid]
    return qid


def raw_values(data, pid):
    out = []
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def values(data, pid):
    """Claim targets as the graph sees them -- resolved, so aliases cannot hide an edge."""
    return [resolve(q) for q in raw_values(data, pid)]


def drop_claim(data, pid, qid):
    target = resolve(qid)
    claims = (data.get("claims") or {}).get(pid)
    if not claims:
        return 0
    def points_at_target(c):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        return isinstance(v, dict) and v.get("id") and resolve(v["id"]) == target
    keep = [c for c in claims if not points_at_target(c)]
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


def main():
    write = "--write" in sys.argv
    sib = siblings()

    # Refuse to cut unless the surviving father really is already recorded -- otherwise
    # this orphans Quintus instead of correcting him.
    child_files = family_of(CHILD, sib)
    if not child_files:
        sys.exit(f"ABORT: no file claims {CHILD}")
    for stem in child_files:
        fathers = values(load(stem), P_FATHER)
        if TRUE_FATHER not in fathers and FALSE_FATHER in fathers:
            sys.exit(f"ABORT: {stem}.json has {FALSE_FATHER} but not {TRUE_FATHER}; "
                     f"cutting would leave Quintus fatherless")

    edits = []
    print(f"{CHILD} (Quintus): {len(child_files)} file(s) claim it -> {child_files}")
    for stem in child_files:
        data = load(stem)
        n = drop_claim(data, P_FATHER, FALSE_FATHER)
        print(f"  {stem}.json: dropped father {FALSE_FATHER} x{n}; "
              f"fathers left: {values(data, P_FATHER)}")
        edits.append((stem, data))

    parent_files = family_of(FALSE_FATHER, sib)
    print(f"{FALSE_FATHER}: {len(parent_files)} file(s) claim it -> {parent_files}")
    for stem in parent_files:
        data = load(stem)
        n = drop_claim(data, P_CHILD, CHILD)
        print(f"  {stem}.json: dropped child {CHILD} x{n}; "
              f"children left: {len(values(data, P_CHILD))}")
        edits.append((stem, data))

    dupes = [s for s, n in collections.Counter(s for s, _ in edits).items() if n > 1]
    if dupes:
        sys.exit(f"ABORT: {dupes} staged twice")

    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for stem in family_of(CHILD, sib):
        data = load(stem)
        if FALSE_FATHER in values(data, P_FATHER):
            bad.append(f"{stem}.json still has father {FALSE_FATHER}")
        if TRUE_FATHER not in values(data, P_FATHER):
            bad.append(f"{stem}.json lost father {TRUE_FATHER}")
    for stem in family_of(FALSE_FATHER, sib):
        if CHILD in values(load(stem), P_CHILD):
            bad.append(f"{stem}.json still lists child {CHILD}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"Verified: {CHILD}'s father is {TRUE_FATHER} alone, on both sides of the edge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
