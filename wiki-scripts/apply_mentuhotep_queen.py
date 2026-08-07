"""Queen Mentuhotep was a king's WIFE, not a king's mother. Opens the Theban ring.

    python wiki-scripts/apply_mentuhotep_queen.py           # dry run
    python wiki-scripts/apply_mentuhotep_queen.py --write   # apply

THE RING

    Q85478 Neferhotep III -> Q85578 Mentuhotep VI -> Q85554 Sebekemsaf
        -> Q85528 Yauyebi -> Q85514 Senebhenaf -> Q85500 Mentuhotep -> Q85478

Six records, and it closes because `Q85500` Mentuhotep is recorded as the MOTHER of both
Neferhotep III and Mentuhotep VI while also descending from them five generations down.

WHAT THE SOURCES SAY

Queen Mentuhotep (Wikipedia, from Passalacqua's 1822-25 finds at Dra' Abu el-Naga' and
Wilkinson's record of the now-lost coffin):

    "wife of pharaoh Djehuti" -- Great Royal Wife, and Khenemetneferhedjet
    "She was the daughter of the vizier Senebhenaf and of a woman called Sobekhotep."

**The dump already has her parentage exactly right** -- `Q85500` P47 = `Q85514` Senebhenaf,
P48 = `Q85516` Sobekhotep -- and it already has the attested marriage, `Q85498` Djehuti
P42 = `Q85500`. Everything the sources actually attest is present and correct.

**No child of hers is attested anywhere.** And for the two kings she is given as mother of:

  * Neferhotep III -- Wikipedia records nothing whatever about his father, mother or wife.
    His reign is known from a single damaged Theban stela.
  * Seankhenre Mentuhotepi (Mentuhotep VI) -- nothing about parentage either. He "took the
    throne following" Neferhotep III; the article states a succession, not a descent.

So the two mother-claims are not a reading of the evidence, they are a king list turned
into a pedigree -- the standard hazard with Second Intermediate Period material, where
Ryholt's and Baker's sequence for the 16th Dynasty (Djehuti, Sobekhotep VIII, Neferhotep
III, Mentuhotep VI) is an order of reigns and nothing more.

THE REPAIR

Remove exactly the two mother-claims and their reciprocals. Both must go: dropping only
the Neferhotep III edge leaves the shorter ring Q85500 -> Q85578 -> ... -> Q85514 ->
Q85500 standing.

Nothing attested is touched. Mentuhotep keeps her parents, her titles and her marriage to
Djehuti; Neferhotep III keeps his reconstructed father Djehuti and Mentuhotep VI keeps his
reconstructed father Neferhotep III -- both unattested, but neither forms a loop, and
cutting further would sever the line on no better evidence than the line was built on.

`Q195101` and `Q195202` are redirect qids for `Q85578` and `Q85478`; the false claims name
them too, so they are removed as well, exactly as `Q49634` had to be handled for `Q1955`.

Shadow-aware and idempotent; verifies from disk and walks the ring afterwards.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER, P_SPOUSE = "P20", "P47", "P48", "P42"

QUEEN = "Q85500"          # Mentuhotep, Great Royal Wife of Djehuti
DJEHUTI = "Q85498"        # Sekhemre Sementawi Djehuti -- her attested husband
VIZIER = "Q85514"         # Senebhenaf, her attested father
QUEEN_MOTHER = "Q85516"   # Sobekhotep, her attested mother

# The kings she was wrongly made the mother of, with their redirect qids.
FALSE_SONS = ["Q85478", "Q85578", "Q195101", "Q195202"]
# Files that hold the reciprocal P48 -> QUEEN. Redirect qids resolve to the first two.
FALSE_SON_QIDS = ["Q85478", "Q85578"]


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


def walk(start, sib, limit=60):
    seen, frontier, depth = {start}, {start}, 0
    while frontier and depth < limit:
        nxt = set()
        for node in frontier:
            for p in parents_of(node, sib):
                if p == start:
                    return f"CLOSED at depth {depth+1}"
                if p not in seen:
                    seen.add(p)
                    nxt.add(p)
        frontier = nxt
        depth += 1
    return f"OPEN -- {len(seen)-1} ancestors, none of them itself"


def main():
    write = "--write" in sys.argv
    sib = siblings()

    # The attested facts must be present -- this repair is only correct on top of them.
    checks = [
        (QUEEN, P_FATHER, VIZIER, "the vizier Senebhenaf is her father"),
        (QUEEN, P_MOTHER, QUEEN_MOTHER, "a woman called Sobekhotep is her mother"),
        (DJEHUTI, P_SPOUSE, QUEEN, "Djehuti is her attested husband"),
    ]
    for qid, pid, expect, why in checks:
        if not any(expect in values(load(s), pid) for s in family_of(qid, sib)):
            sys.exit(f"ABORT: {qid} {pid} is missing {expect} ({why}); "
                     f"the dump is not in the state this repair assumes")
    print("Preconditions hold: her attested parents and marriage are all present.\n")

    staged = {}
    for stem in family_of(QUEEN, sib):
        data = staged.get(stem) or load(stem)
        for son in FALSE_SONS:
            n = drop_claim(data, P_CHILD, son)
            if n:
                print(f"  {stem}.json ({QUEEN}): dropped child {son} x{n}")
        staged[stem] = data

    for qid in FALSE_SON_QIDS:
        for stem in family_of(qid, sib):
            data = staged.get(stem) or load(stem)
            n = drop_claim(data, P_MOTHER, QUEEN)
            if n:
                print(f"  {stem}.json ({qid}): dropped mother {QUEEN} x{n}; "
                      f"father kept: {values(data, P_FATHER)}")
            staged[stem] = data

    edits = list(staged.items())
    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for stem in family_of(QUEEN, sib):
        for son in FALSE_SONS:
            if son in values(load(stem), P_CHILD):
                bad.append(f"{stem}.json still lists child {son}")
    for qid in FALSE_SON_QIDS:
        for stem in family_of(qid, sib):
            if QUEEN in values(load(stem), P_MOTHER):
                bad.append(f"{stem}.json still has mother {QUEEN}")
    for qid, pid, expect, why in checks:
        if not any(expect in values(load(s), pid) for s in family_of(qid, sib)):
            bad.append(f"{qid} {pid} lost {expect} -- {why}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1

    print("\nRing walk:")
    closed = False
    for q, name in [(QUEEN, "Mentuhotep"), ("Q85478", "Neferhotep III"),
                    ("Q85578", "Mentuhotep VI"), ("Q85554", "Sebekemsaf")]:
        r = walk(q, sib)
        print(f"  {q} {name}: {r}")
        closed |= r.startswith("CLOSED")
    if closed:
        print("\nStill closed -- the repair did not do what it claims.")
        return 1
    print("\nRing open. She keeps her parents, her titles and her marriage to Djehuti.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
