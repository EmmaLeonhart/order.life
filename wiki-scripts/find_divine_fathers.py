"""Find children who have BOTH a Greco-Roman divine father and a human one.

    python wiki-scripts/find_divine_fathers.py            # report
    python wiki-scripts/find_divine_fathers.py --tsv      # machine-readable

RULED BY EMMA 2026-08-07: *"Anyone with two fathers one divine one human we can honestly
just remove the divine father link."* This finds them; apply_divine_fathers.py cuts them.

SCOPE, and it is narrow on purpose

CLAUDE.md: *"I treat **Greco-Roman ones and Jesus** as having the divine father as a sort
of blessing and ignore them literally."* That is the whole scope. **Indian devas are NOT
in it** -- Surya, Yama, Chandra and Daksha are real genealogical ancestors in this
project, and the 2026-08-07 Puranic repair depends on their being so. Naming a god is not
enough; it has to be a Greco-Roman hero-fathering, or Yahweh over Jesus.

WHY THE "HUMAN FATHER ALSO PRESENT" CONDITION IS THE REAL SAFETY RAIL

The Greek primordials and Titans -- Ouranos, Kronos, Oceanus, Hyperion, Iapetus -- are the
backbone of the Greek descent to Aster, and they are gods too. Cutting them would sever
the line rather than a blessing. They are safe here for a structural reason, not because
of a name list: **they are their children's ONLY father**, so they never satisfy the
two-fathers condition. Nothing is removed unless a non-divine father survives it.

IT IS A FINDER, NOT AN ORACLE. The name match is deliberately loose and its false
positive rate is high -- on the 2026-08-07 run it caught "Miro II el **Jove**" (Catalan
for "the Young", not Jupiter), "Li **Pan**" and "Wei **Pan**" (Chinese names),
"**Proteus** Ascidiacea" (a taxon) and "Aurelius **Hermes**" (a Roman freedman). Every hit
must be read before it is cut; apply_divine_fathers.py therefore carries an explicit,
reviewed QID list rather than calling this at runtime.

Reads persons.tsv and edges.tsv, then does targeted per-qid reads of only the candidate
children -- never a walk over the dump.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANA = ROOT / "wikibase" / "analysis"
ITEMS = ROOT / "wikibase" / "items"

P_FATHER = "P47"

# Greco-Roman divinities that father heroes, plus the Jesus case. Whole-word matched
# against the label so "Apollo" does not catch "Apollodotus" or "Apollonius".
DIVINE = [
    "Zeus", "Jupiter", "Iuppiter", "Jove",
    "Poseidon", "Neptune", "Neptunus",
    "Ares", "Mars",
    "Apollo", "Phoebus",
    "Hermes", "Mercury", "Mercurius",
    "Hephaestus", "Hephaistos", "Vulcan", "Vulcanus",
    "Dionysus", "Dionysos", "Bacchus", "Liber",
    "Hades", "Pluto", "Plouton",
    "Helios", "Sol",
    "Eros", "Cupid", "Amor",
    "Pan", "Faunus", "Silenus", "Priapus",
    "Boreas", "Zephyrus", "Notus", "Eurus", "Aeolus",
    "Triton", "Nereus", "Proteus", "Glaucus", "Phorcys",
    "Asclepius", "Aesculapius",
    "Yahweh", "Jehovah", "Holy Spirit", "God the Father",
]
DIVINE_RE = re.compile(r"\b(" + "|".join(re.escape(d) for d in DIVINE) + r")\b", re.I)


def is_divine(label):
    return bool(DIVINE_RE.search(label or ""))


def load_persons():
    persons = {}
    with open(ANA / "persons.tsv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            persons[row["qid"]] = row.get("label", "")
    return persons


def father_claims(qid):
    """Targeted read: the P47 values on the canonical file for this qid."""
    path = ITEMS / f"{qid}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    out = []
    for c in (data.get("claims") or {}).get(P_FATHER, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    as_tsv = "--tsv" in sys.argv
    persons = load_persons()

    gods = {q: l for q, l in persons.items() if is_divine(l)}
    if not as_tsv:
        print(f"{len(gods)} record(s) carry a Greco-Roman divine name.\n")

    # children of those records, from the committed edge list
    children_of_gods = defaultdict(set)
    with open(ANA / "edges.tsv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if row["parent"] in gods:
                children_of_gods[row["child"]].add(row["parent"])

    if not as_tsv:
        print(f"{len(children_of_gods)} child record(s) name one as a parent. "
              f"Reading those {len(children_of_gods)} files only.\n")

    cut, sole, notfather = [], [], 0
    for child, godparents in sorted(children_of_gods.items(),
                                    key=lambda kv: int(kv[0][1:])):
        fathers = father_claims(child)
        if fathers is None:
            continue
        divine_fathers = [f for f in fathers if f in gods]
        human_fathers = [f for f in fathers if f not in gods]
        if not divine_fathers:
            notfather += 1          # named as mother, or as child, not as father
            continue
        rec = (child, persons.get(child, "?"),
               [(d, gods[d]) for d in divine_fathers],
               [(h, persons.get(h, "?")) for h in human_fathers])
        (cut if human_fathers else sole).append(rec)

    if as_tsv:
        w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
        w.writerow(["child", "child_label", "divine_father", "divine_label",
                    "surviving_human_fathers"])
        for child, clabel, divs, hums in cut:
            for dq, dl in divs:
                w.writerow([child, clabel, dq, dl,
                            ";".join(f"{q}={l}" for q, l in hums)])
        return 0

    print("=" * 78)
    print(f"CUT -- divine father WITH a human father surviving: {len(cut)}")
    print("=" * 78)
    for child, clabel, divs, hums in cut:
        print(f"  {child:9s} {clabel[:40]:42s}")
        for dq, dl in divs:
            print(f"      DROP  {dq:9s} {dl}")
        for hq, hl in hums:
            print(f"      KEEP  {hq:9s} {hl}")

    print()
    print("=" * 78)
    print(f"LEAVE ALONE -- divine father is the ONLY father: {len(sole)}")
    print("  Cutting these would orphan the record, so Emma's rule does not reach them.")
    print("=" * 78)
    for child, clabel, divs, _ in sole[:40]:
        names = ", ".join(dl for _, dl in divs)
        print(f"  {child:9s} {clabel[:42]:44s} <- {names}")
    if len(sole) > 40:
        print(f"  ... and {len(sole)-40} more")

    print(f"\n{notfather} record(s) name a divine record as a parent but not via P47.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
