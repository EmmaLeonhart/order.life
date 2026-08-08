"""The Portuguese ring: Tereza Eriz de Lugo is a daughter of Ero, not of Estevao Soares.

    python wiki-scripts/apply_tereza_eriz.py           # dry run
    python wiki-scripts/apply_tereza_eriz.py --write   # apply

THE RING (tangle 3, fourteen records) -- the last of the eight

    Q79388 Ausindo Ximeno -> Q79415 Soeiro Ausendes -> Q79435 Arnaldo Ximenes
      -> Q79438 Sancho -> Q79424 Gil -> Q79450 Soeiro Afonso Tangil
      -> Q79480 Fernao de Tangil -> Q79537 Estevao Soares -> Q79618 Tereza Eriz de Lugo
      -> Q99939 Ufa Ufes -> Q100154 Godo Arnaldes de Baiao -> Q100519 Soeiro Guedes
      -> Q101113 Ausindo Soares -> Q113625 Teodoredo Ausendes -> Q79388

WHERE ITEM 10 WAS RIGHT, AND WHERE ITS TEST MISFIRED

Item 10 flagged four edges as contradicted by Portuguese patronymics and declined to pick
between them, warning that toponymics make the test weaker here than in Welsh. That
caution was correct, and three of the four flags are false alarms:

  * `Q79415` Soeiro Ausendes -> `Q79435` Arnaldo **Ximenes** is **attested**: the Casa de
    Baiao lineage has D. Soeiro Ausendes fathering D. Arnaldo Ximenes, who died at **Las
    Navas de Tolosa on 16 July 1212**. So *Ximenes* is a house name here, not a strict
    patronymic, and the same objection to `Q113625` -> `Q79388` falls with it.
  * `Q113625` Teodoredo Ausendes -> `Q79388` Ausindo Ximeno is **chronologically sound**:
    the dump gives Teodoredo **b. 1078** and the Baiao sources give Ausindo Ximeno
    **b. 1115**. A 37-year gap between father and son.

The fourth flag is the real one, and chronology confirms it independently.

THE CONTRADICTION, anchored outside the ring at both ends

  DOWNWARD from Tereza: her descendants reach **D. Mem Viegas de Sousa, b. 1070**, five
  generations below her -- so **Tereza belongs c. 920**. That is exactly right for
  *Eriz de Lugo*: **Ero Fernandez, count of Lugo, died c. 926.**

  UPWARD from Estevao: he stands five generations below **Arnaldo Ximenes, d. 1212**, so
  **Estevao belongs c. 1325.**

Estevao Soares cannot be the father of a woman born four centuries before him. Every other
edge in the ring is consistent with one continuous descent from Tereza c. 920 through the
Baiao house -- Ufa Ufes, Godo Arnaldes de Baiao, Soeiro Guedes, Ausindo Soares, Teodoredo
b. 1078, Ausindo Ximeno b. 1115, Soeiro Ausendes, Arnaldo Ximenes d. 1212 -- and only this
one edge ties the far end of that line back to its head.

HER REAL FATHER IS IN THE DUMP

`Q100140` **Ero Fernandez de Lugo** already carries eight children, and they are her
name-siblings: Gudesindo **Eriz**, Ilduara **Eriz de Lugo** (the historical mother of San
Rosendo), Goto **Eriz**, Diego **Eriz**, Ermesenda **Eris de Lugo** -- and a **Teresa
Eriz** (`Q100413`). So the repair is not merely a cut: it moves her to the father her own
name gives her, beside the siblings the dump already records.

Checked before writing: `Q100140` is not among her 3,658 descendants, so the new edge
closes no loop.

WHAT THIS DOES NOT DO

`Q79618`, `Q100413` "Teresa Eriz" and `Q110516` "Teresa Eris de Lugo" (wd `Q110302349`,
whose father is the other Ero record `Q111013`) are three records for one woman. **That
dedupe is separate work and removes no loop**, so it is filed rather than done here. Her
mother is left unset: Ero had two wives, Adosinda Romanez de Monterroso and Elvira, and
nothing here says which.
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

TEREZA = "Q79618"       # Tereza Eriz de Lugo, c. 920
FALSE_FATHER = "Q79537"  # Estevao Soares, c. 1325
TRUE_FATHER = "Q100140"  # Ero Fernandez de Lugo, d. c. 926

RING = ["Q79388", "Q79415", "Q79435", "Q79438", "Q79424", "Q79450", "Q79480",
        "Q79537", "Q79618", "Q99939", "Q100154", "Q100519", "Q101113", "Q113625"]


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


def walk(start, sib, limit=80):
    seen, frontier, depth = {start}, {start}, 0
    while frontier and depth < limit:
        nxt = set()
        for node in frontier:
            for p in parents_of(node, sib):
                if p == start:
                    return None, f"CLOSED at depth {depth+1}"
                if p not in seen:
                    seen.add(p)
                    nxt.add(p)
        frontier = nxt
        depth += 1
    return seen - {start}, f"open, {len(seen)-1} ancestors"


def main():
    write = "--write" in sys.argv
    sib = siblings()

    # The new father must exist and must not sit below her, or this trades one loop for
    # another.
    if load(TRUE_FATHER) is None:
        sys.exit(f"ABORT: {TRUE_FATHER} does not exist")
    anc, _ = walk(TRUE_FATHER, sib)
    if anc is None or TEREZA in anc:
        sys.exit(f"ABORT: {TRUE_FATHER} descends from {TEREZA}; the new edge would loop")
    print(f"{TRUE_FATHER} Ero Fernandez de Lugo is not below {TEREZA}. Safe to attach.")

    # And he must already carry the name-siblings that justify the identification.
    ero_children = set()
    for stem in family_of(TRUE_FATHER, sib):
        ero_children |= set(values(load(stem), P_CHILD))
    print(f"  He already carries {len(ero_children)} children, "
          f"including the Eriz siblings.\n")

    staged = {}
    for stem in family_of(TEREZA, sib):
        data = staged.get(stem) or load(stem)
        n = drop_claim(data, P_FATHER, FALSE_FATHER)
        m = add_claim(data, P_FATHER, TRUE_FATHER)
        staged[stem] = data
        print(f"  {stem}.json ({TEREZA}): father {FALSE_FATHER} dropped x{n}, "
              f"{TRUE_FATHER} added x{m} -> {values(data, P_FATHER)}")

    for stem in family_of(FALSE_FATHER, sib):
        data = staged.get(stem) or load(stem)
        n = drop_claim(data, P_CHILD, TEREZA)
        staged[stem] = data
        if n:
            print(f"  {stem}.json ({FALSE_FATHER}): dropped child {TEREZA} x{n}; "
                  f"children left: {len(values(data, P_CHILD))}")

    for stem in family_of(TRUE_FATHER, sib):
        data = staged.get(stem) or load(stem)
        m = add_claim(data, P_CHILD, TEREZA)
        staged[stem] = data
        print(f"  {stem}.json ({TRUE_FATHER}): added child {TEREZA} x{m}; "
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
    for stem in family_of(TEREZA, sib):
        f = values(load(stem), P_FATHER)
        if FALSE_FATHER in f:
            bad.append(f"{stem}.json still has father {FALSE_FATHER}")
        if TRUE_FATHER not in f:
            bad.append(f"{stem}.json missing father {TRUE_FATHER}")
    for stem in family_of(FALSE_FATHER, sib):
        if TEREZA in values(load(stem), P_CHILD):
            bad.append(f"{stem}.json still lists child {TEREZA}")
    for stem in family_of(TRUE_FATHER, sib):
        if TEREZA not in values(load(stem), P_CHILD):
            bad.append(f"{stem}.json missing child {TEREZA}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1

    print("\nRing walk across all fourteen:")
    closed = False
    for q in RING:
        _, msg = walk(q, sib)
        if msg.startswith("CLOSED"):
            closed = True
        print(f"  {q}: {msg}")
    if closed:
        print("\nStill closed -- the repair did not do what it claims.")
        return 1
    print("\nRing open. Tereza sits with her Eriz siblings under Ero of Lugo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
