"""Remove the divine father where a human father survives.

    python wiki-scripts/apply_divine_fathers.py           # dry run
    python wiki-scripts/apply_divine_fathers.py --write   # apply

RULED BY EMMA 2026-08-07: *"Anyone with two fathers one divine one human we can honestly
just remove the divine father link."* And, on seeing the scoped list: *"I think it is just
this one single guy with two fathers so just remove the divine lol."*

She is right that it is nearly nothing. `find_divine_fathers.py` name-matched 36 records
and 179 children; after reading them, **exactly two children have both a divine father and
a human one.** Everyone else with a divine father -- Romulus, Remus, Perseus, Neleus,
Circe, and 160-odd more -- has only that father, so cutting would orphan them and the rule
does not reach them.

THE TWO

  Q74991  Abas          fathers Poseidon (Q75039) + Ixion (Q132482)   -> drop Poseidon
  Q138545 Jesus Christ  fathers Joseph (Q137751) + Tiberius Julius
                        Abdes Pantera (Q153725) + Yahweh (Q153726)    -> drop Yahweh

Jesus is included because CLAUDE.md names that case explicitly in Emma's own words --
*"I treat Greco-Roman ones **and Jesus** as having the divine father as a sort of blessing
and ignore them literally"* -- and because two human fathers survive the cut, so it
satisfies the rule exactly. **If "one single guy" meant Abas alone, revert the Jesus
half**; it is a self-contained entry in CUTS below.

WHY THIS CARRIES AN EXPLICIT LIST INSTEAD OF CALLING THE FINDER

The finder's name match is loose and noisy on purpose -- it is a net. Its false positives
on the 2026-08-07 run were "Miro II el **Jove**" (Catalan for "the Young"), a dozen Chinese
names containing **Pan**, "Aurelius **Hermes**" (a Roman freedman), "Iago **Ares**" and
"Gontrodo **Sol** Rodriguez" (Galician and Spanish surnames), and "**Proteus**
Ascidiacea", "Proteus", "Helios" and one more from the taxonomic layer -- those last carry
**`P59` "Cladoplast of"**, which is a clean structural tell that a record is a clade and
not a person. Also excluded: euhemerised Latin kings whose regnal names contain a god
("Jasius II **Mars** Italus, King of Latium", "Faunus I King Of Latium", "Cambo Blascon
(**Jupiter** II)"), who are human kings in this genealogy, and "BUDHA (planet Mercury)
Chandra", who is Indian and out of scope entirely -- Surya, Yama and Chandra are real
ancestors here.

Nothing is cut that was not read first.
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

# (child, divine father, the human father(s) that must survive, why)
CUTS = [
    ("Q74991", "Q75039", ["Q132482"],
     "Abas: Poseidon is the blessing; Ixion, son of Aeton, is the father"),
    ("Q138545", "Q153726", ["Q137751", "Q153725"],
     "Jesus: Yahweh is the blessing; Joseph and Tiberius Julius Abdes Pantera remain"),
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


def label(qid):
    d = load(qid)
    return ((d or {}).get("labels", {}).get("en", {}) or {}).get("value", "?")


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


def main():
    write = "--write" in sys.argv
    sib = siblings()
    staged = {}

    for child, divine, humans, why in CUTS:
        fam = family_of(child, sib)
        if not fam:
            sys.exit(f"ABORT: no file claims {child}")

        # The rule is "two fathers, one divine one human". Refuse if the human half is
        # not actually there -- cutting then would orphan the record, not deflate a title.
        present = set()
        for stem in fam:
            present |= set(values(load(stem), P_FATHER))
        surviving = [h for h in humans if h in present]
        if not surviving:
            sys.exit(f"ABORT: {child} has no surviving human father from {humans}; "
                     f"cutting {divine} would orphan it")
        if divine not in present:
            print(f"  {child}: {divine} already absent -- nothing to do")
            continue

        print(f"\n{child} {label(child)} -- {why}")
        print(f"   surviving father(s): "
              f"{', '.join(f'{h} {label(h)}' for h in surviving)}")
        for stem in fam:
            data = staged.get(stem) or load(stem)
            n = drop_claim(data, P_FATHER, divine)
            staged[stem] = data
            if n:
                print(f"   {stem}.json: dropped father {divine} {label(divine)} x{n}")

        for stem in family_of(divine, sib):
            data = staged.get(stem) or load(stem)
            n = drop_claim(data, P_CHILD, child)
            staged[stem] = data
            if n:
                print(f"   {stem}.json ({divine}): dropped child {child} x{n}; "
                      f"children left: {len(values(data, P_CHILD))}")

    edits = list(staged.items())
    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for child, divine, humans, _ in CUTS:
        for stem in family_of(child, sib):
            fathers = values(load(stem), P_FATHER)
            if divine in fathers:
                bad.append(f"{stem}.json still has father {divine}")
            if not any(h in fathers for h in humans):
                bad.append(f"{stem}.json lost every human father -- orphaned")
        for stem in family_of(divine, sib):
            if child in values(load(stem), P_CHILD):
                bad.append(f"{stem}.json still lists child {child}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print("\nVerified: both records keep a human father and neither keeps the divine one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
