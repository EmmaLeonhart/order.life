"""The Welsh ring: Lleucu cannot be the mother of a man born six generations before her.

    python wiki-scripts/apply_lleucu_generation.py           # dry run
    python wiki-scripts/apply_lleucu_generation.py --write   # apply

THE RING (tangle 6, seven records)

    Q138061 Joan ferch Ieuan ap Rhys ap Llowdden
      -> Q138810 Llywelyn Ddu ab Owain -> Q140234 Llywelyn Foethus
      -> Q139067 Gruffudd Foethus -> Q140681 Lleucu ferch Gruffudd
      -> Q140643 Rhys ap Llowdden y Gath -> Q139043 Ieuan ap Rhys -> Q138061 Joan

Six of the seven edges are confirmed by the patronymics, which in Welsh ARE the pedigree.
Only two maternal claims are unconfirmed -- Joan as mother of Llywelyn Ddu, and Lleucu as
mother of Rhys -- and queue.md item 9 was right that both are spouse-consistent and that
Wikidata carries the identical ring, mirrored on both sides, so it arbitrates nothing.

WHAT SETTLES IT: AN EXTERNAL DATE, AND IT IS NOT CIRCULAR

`Q137927` Owain's mother is `Q137334` Gwenllian, daughter of Cadwgan ab Owain by
`Q136930` a daughter of **Rhys Gryg**. Rhys Gryg -- 'Rhys the Hoarse', prince of
Deheubarth, fourth son of the Lord Rhys -- **died in 1234** at Llandeilo Fawr of wounds
taken attacking Carmarthen (Dictionary of Welsh Biography), born c. 1165.

That fixes Owain's generation from outside the ring, and both arms run outward from him
along links the patronymics confirm:

    Rhys Gryg d. 1234       ->  daughter c. 1200  ->  Gwenllian c. 1225
      ->  Owain c. 1250  ==  m. Joan c. 1255

    DOWN (all patronymic):  Llywelyn Ddu ab Owain c. 1280 -> Llywelyn Foethus c. 1310
                            -> Gruffudd Foethus c. 1340 -> Lleucu c. 1370
    UP (Joan's own name,
     "ferch Ieuan ap Rhys
      ap Llowdden"):        Ieuan ap Rhys c. 1230 -> Rhys ap Llowdden c. 1200
                            -> Llowdden y Gath c. 1170

**Lleucu c. 1370 cannot be the mother of Rhys c. 1200.** The gap is about 170 years.

The argument does not depend on which maternal claim is true. Llywelyn Ddu's date is fixed
by his *father* Owain whoever his mother was, and Rhys's date is fixed by Joan's own
patronymic and her marriage to Owain. Cutting the other maternal claim instead would leave
this impossibility standing -- which is why the cheap cut item 9 warned against
(`Q138061` -> `Q138810`, free and tangle-dissolving) is the wrong one.

THE MECHANISM, and it is the shape this dump keeps producing

Welsh papponymy: Llowdden Hen -> Rhys -> Llowdden y Gath -> Rhys -> Ieuan -> Joan. The
names alternate down the generations, and two women called Lleucu ferch Gruffudd have been
merged into one record -- the same collapse as the two Esthers, as Yama and Mrityu, and as
Mamercus and Marcus.

The dump says so itself: `Q140681` carries **two husbands two centuries apart** --
`Q140557` Morgan ap Dafydd of Rhydodyn, whose other wife is a granddaughter of **Ifor
Hael** (Dafydd ap Gwilym's patron, fl. c. 1340-60) and who therefore belongs c. 1370
exactly like her; and `Q142996` Llowdden y Gath, c. 1170. **Wikidata carries neither
marriage** -- it has no spouse claim on her at all -- so the Llowdden marriage is a
dump-side addition, and it is the wrong one.

THE REPAIR

Remove the mother-claim and the impossible marriage, both sides each. Lleucu keeps her
parents, and keeps Morgan of Rhydodyn, who fits her generation. Rhys ap Llowdden's mother
becomes unrecorded, which is honest: the woman who married Llowdden y Gath c. 1190 is a
different Lleucu, and naming her wants Bartrum's *Welsh Genealogies* Llowdden charts.
She is not invented here.
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

LLEUCU = "Q140681"       # Lleucu ferch Gruffudd (Foethus), c. 1370
RHYS = "Q140643"         # Rhys ap Llowdden y Gath, c. 1200
LLOWDDEN = "Q142996"     # Llowdden y Gath, c. 1170
GRUFFUDD = "Q139067"     # Gruffudd Foethus, her father -- kept
MORGAN = "Q140557"       # Morgan ap Dafydd of Rhydodyn, her real husband -- kept

FALSE_CLAIMS = [
    (RHYS, P_MOTHER, LLEUCU,
     "Rhys c. 1200 cannot have a mother born c. 1370"),
    (LLEUCU, P_CHILD, RHYS,
     "reciprocal of the above"),
    (LLEUCU, P_SPOUSE, LLOWDDEN,
     "Llowdden y Gath belongs c. 1170; this marriage is two centuries out and is "
     "carried by no source outside the dump"),
    (LLOWDDEN, P_SPOUSE, LLEUCU,
     "reciprocal of the above"),
]


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

    # What must survive: her real parentage and her chronologically-fitting marriage.
    keep = [
        (LLEUCU, P_FATHER, GRUFFUDD, "Gruffudd Foethus is her father"),
        (LLEUCU, P_SPOUSE, MORGAN, "Morgan of Rhydodyn is her husband"),
    ]
    for qid, pid, expect, why in keep:
        if not any(expect in values(load(s), pid) for s in family_of(qid, sib)):
            sys.exit(f"ABORT: {qid} {pid} is missing {expect} ({why})")
    print("Preconditions hold: Lleucu's parentage and Rhydodyn marriage are present.\n")

    staged = {}
    for holder, pid, target, why in FALSE_CLAIMS:
        fam = family_of(holder, sib)
        if not fam:
            sys.exit(f"ABORT: no file claims {holder}")
        for stem in fam:
            data = staged.get(stem) or load(stem)
            n = drop_claim(data, pid, target)
            staged[stem] = data
            if n:
                print(f"  {stem}.json ({holder}): dropped {pid} -> {target} x{n}")
                print(f"      {why}")

    edits = list(staged.items())
    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for holder, pid, target, _ in FALSE_CLAIMS:
        for stem in family_of(holder, sib):
            if target in values(load(stem), pid):
                bad.append(f"{stem}.json still has {pid} -> {target}")
    for qid, pid, expect, why in keep:
        if not any(expect in values(load(s), pid) for s in family_of(qid, sib)):
            bad.append(f"{qid} {pid} lost {expect} -- {why}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1

    print("\nRing walk:")
    closed = False
    for q, name in [(LLEUCU, "Lleucu"), ("Q138061", "Joan"), ("Q138810", "Llywelyn Ddu"),
                    (RHYS, "Rhys ap Llowdden"), ("Q139067", "Gruffudd Foethus")]:
        r = walk(q, sib)
        print(f"  {q} {name}: {r}")
        closed |= r.startswith("CLOSED")
    if closed:
        print("\nStill closed -- the repair did not do what it claims.")
        return 1
    print("\nRing open. Lleucu keeps her father and the husband who fits her century.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
