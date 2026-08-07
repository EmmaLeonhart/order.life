"""Mamercus was born a Livius Drusus. Wire in the biological father the dump is missing.

    python wiki-scripts/apply_mamercus_biological_father.py           # dry run
    python wiki-scripts/apply_mamercus_biological_father.py --write   # apply

WHO MAMERCUS IS

`Q72786`, labelled "Marcus Aemilius Lepidus" in the dump, is **Mamercus Aemilius Lepidus
Livianus, consul 77 BC** -- Wikidata `Q721477`, born c. 150 BC. Not a Marcus. The dump's
label is a name collision, and it is what made this record look like it held three
contradictory parentages.

The cognomen is self-documenting: *Livianus* marks a man **born a Livius Drusus and
adopted into the Aemilii Lepidi**. That is why his recorded mother is described on
Wikidata as "wife of Drusus" while he himself carries an Aemilian name, and why his two
siblings are a Livius Drusus and a Livia.

Wikidata carries both fathers, and the asymmetry with his brother is the adoption:

    Q721477 Mamercus Aemilius Lepidus Livianus
        father Q703346  Marcus Livius Drusus (opponent of Gaius Gracchus)  BIOLOGICAL
        father Q3622705 Marcus Aemilius Lepidus, cos. 126 BC               ADOPTIVE
        mother Q100804879 Cornelia
        siblings Q433463 M. Livius Drusus the tribune, Q432100 Livia

His brother `Q433463` carries only `Q703346`. One brother stayed a Livius Drusus; the
other was adopted and took *Livianus* to record where he came from.

WHICH DUMP RECORD IS THE BIOLOGICAL FATHER -- the question this item was actually blocked on

`lepidus_resolved.md` left this open: there are nine "Livius Drusus" records in the dump
and it warned that the right one "must be checked before wiring anything". It is
**`Q72798`**, and the identification is not a judgement call:

  * `Q72798` carries **`P61` = `Q703346`** -- the Wikidata id is on the record itself
  * dates `+0155` / `+0109` against Wikidata's `-0155` / `-0109` -- the same numbers,
    differing only by the positive-sign bug documented in `lepidus_resolved.md`
  * spouse `Q72801` Cornelia = wd `Q100804879`, the attested mother
  * children `Q72624` Livia and `Q73119` (which itself carries `P61` = `Q433463`, the
    tribune) -- two of Wikidata's three children for `Q703346`

**And the third child is missing: Mamercus.** Exactly as predicted -- `Q72786` is not
wrong to have an Aemilian father, it is missing the Livian one.

WHAT THIS DOES, AND WHAT IT DELIBERATELY DOES NOT

Adds the one missing edge, on both sides. Checked first: `Q72786` is not an ancestor of
`Q72798`, so the edge closes no loop.

It does NOT touch couples B (`Q73113`/`Q73110`) and C (`Q73173`), which remain
unidentified and are the rest of the unmerge, and it does NOT relabel the record --
naming is Emma's. **There is also no adoption property in this wikibase**, so the
adoptive-vs-biological distinction is recorded in the record's own description rather
than modelled; adding a kinship-type property is a schema decision and is Emma's too.
Both are filed in todo.md.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER, P_WIKIDATA = "P20", "P47", "P48", "P61"

MAMERCUS = "Q72786"        # wd Q721477, Mamercus Aemilius Lepidus Livianus, cos. 77 BC
BIO_FATHER = "Q72798"      # wd Q703346, M. Livius Drusus, opponent of Gaius Gracchus
ADOPTIVE_FATHER = "Q73011"  # wd Q3622705, M. Aemilius Lepidus, cos. 126 BC
MOTHER = "Q72801"          # wd Q100804879, Cornelia

DESCRIPTION = (
    "Mamercus Aemilius Lepidus Livianus, consul 77 BC (Wikidata Q721477) -- NOT a Marcus; "
    "the label is a name collision. Born a Livius Drusus and adopted into the Aemilii "
    "Lepidi, which the cognomen Livianus records. Of the fathers on this record, "
    f"{BIO_FATHER} (M. Livius Drusus) is BIOLOGICAL and {ADOPTIVE_FATHER} "
    "(M. Aemilius Lepidus cos. 126 BC) is ADOPTIVE -- both are correct and neither is a "
    "two-father defect. The remaining father/mother couples on this record belong to other "
    "men and are an open unmerge. This wikibase has no adoption property; see todo.md."
)


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


def raw_values(data, pid):
    out = []
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, str):
            out.append(v)
    return out


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid,
                                                 "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def add_claim(data, pid, qid):
    if qid in values(data, pid):
        return 0
    data.setdefault("claims", {}).setdefault(pid, []).append(entity_claim(pid, qid))
    return 1


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


def main():
    write = "--write" in sys.argv
    sib = siblings()

    # 1. The identification must hold on the record itself, not just in my reasoning.
    bio = load(BIO_FATHER)
    if "Q703346" not in raw_values(bio, P_WIKIDATA):
        sys.exit(f"ABORT: {BIO_FATHER} does not carry P61=Q703346; "
                 f"it is not the man Wikidata names as Mamercus's biological father")
    if MOTHER not in values(bio, "P42"):
        sys.exit(f"ABORT: {BIO_FATHER} is not married to {MOTHER} Cornelia; "
                 f"the identification does not hold")
    print(f"{BIO_FATHER} confirmed as wd Q703346 (P61 on the record, spouse {MOTHER}).")

    # 2. The new edge must close no loop.
    seen, frontier, depth = {BIO_FATHER}, {BIO_FATHER}, 0
    while frontier and depth < 80:
        nxt = set()
        for node in frontier:
            for p in parents_of(node, sib):
                if p == MAMERCUS:
                    sys.exit(f"ABORT: {MAMERCUS} is an ancestor of {BIO_FATHER}; "
                             f"this edge would close a loop")
                if p not in seen:
                    seen.add(p)
                    nxt.add(p)
        frontier = nxt
        depth += 1
    print(f"No loop: {MAMERCUS} is not among {BIO_FATHER}'s {len(seen)-1} ancestors.\n")

    staged = {}
    for stem in family_of(MAMERCUS, sib):
        data = staged.get(stem) or load(stem)
        n = add_claim(data, P_FATHER, BIO_FATHER)
        data.setdefault("descriptions", {})["en"] = {
            "language": "en", "value": DESCRIPTION}
        staged[stem] = data
        print(f"  {stem}.json ({MAMERCUS}): father {BIO_FATHER} added x{n}; "
              f"description set")

    for stem in family_of(BIO_FATHER, sib):
        data = staged.get(stem) or load(stem)
        n = add_claim(data, P_CHILD, MAMERCUS)
        staged[stem] = data
        print(f"  {stem}.json ({BIO_FATHER}): child {MAMERCUS} added x{n}; "
              f"children now {len(values(data, P_CHILD))}")

    edits = list(staged.items())
    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for stem in family_of(MAMERCUS, sib):
        d = load(stem)
        if BIO_FATHER not in values(d, P_FATHER):
            bad.append(f"{stem}.json missing father {BIO_FATHER}")
        if ADOPTIVE_FATHER not in values(d, P_FATHER):
            bad.append(f"{stem}.json lost adoptive father {ADOPTIVE_FATHER}")
    for stem in family_of(BIO_FATHER, sib):
        if MAMERCUS not in values(load(stem), P_CHILD):
            bad.append(f"{stem}.json missing child {MAMERCUS}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"\nVerified. {MAMERCUS} now has both fathers -- {BIO_FATHER} biological, "
          f"{ADOPTIVE_FATHER} adoptive -- and the edge is declared on both sides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
