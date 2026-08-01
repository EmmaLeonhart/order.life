"""Add the lineage-bridge edges from planning/lineage_bridges_proposed.md.

    python wiki-scripts/add_bridge_edges.py adam-genghis           # dry run
    python wiki-scripts/add_bridge_edges.py adam-genghis --write   # apply

Data-driven and shadow-aware, like merge_cluster.py. Everything it does is additive:
it creates records that do not exist and appends parent/child claims. It never removes a
claim, so `git checkout -- wikibase/items` reverts it completely.

WHY A SCRIPT AND NOT A HAND EDIT

An edge lives in TWO places -- the child's P47/P48 and the parent's P20 -- and
extract_genealogy.py builds edges.tsv from the union, so a half-declared edge still reads
as real while any one-sided repair silently fails. That is what made the Tros fix look
done while two cycles were still closed. This writes both directions and asserts both
afterwards.

And a record's claims must be propagated to every file claiming its qid, or the edit
reverts the moment that file stops being the numerically-lowest claimant. None of the
records touched by the adam-genghis bridge currently has a shadow, but that is a fact
about today's dump and not a property to rely on, so the propagation runs regardless.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
ANALYSIS = ROOT / "wikibase" / "analysis"

# A bridge is: records to create, then parent -> child edges to declare.
BRIDGES = {
    # planning/lineage_bridges_proposed.md, Bridge A. DECIDED BY EMMA 2026-07-31: "Both?"
    # -- take A1 AND A2, not one or the other. The report anticipated this: "A1 and A2 are
    # not exclusive; A2 could carry the descent and A1 could still be repaired as a
    # separate correctness fix."
    #
    # Khaidu Q53399 is the root of the Borjigin line: 401 descendants including Genghis
    # Khan (Q37401), and ZERO ancestors. Neither edge below can create a cycle -- checked
    # against edges.tsv before writing: neither Q153230 nor Q1164 is a descendant of
    # Khaidu, and both reach Aster Q1.
    "adam-genghis": {
        "create": [
            # A2. Haplogroup C (Q1164) exists, is Adam-descended, and has no children.
            # C2-M217 is a real clade with a real position under C, and is the
            # best-attested fact about Genghis Khan's genetics -- so this invents no
            # person. It mirrors Q54433 "Sinitic O2a2b1a2 (F114)", which sits between the
            # Yellow Emperor's line and Adam in exactly this way.
            {
                "qid": "Q200000",
                "label": "C2 (M217)",
                "aliases": ["Haplogroup C2", "C-M217"],
                "note": "haplogroup bridge node, created 2026-07-31 for Bridge A2",
            },
        ],
        "edges": [
            # A2: Haplogroup C -> C2 (M217) -> Khaidu
            ("Q1164", "Q200000", "A2: C2-M217 is a clade under Haplogroup C"),
            ("Q200000", "Q53399", "A2: Khaidu attaches beneath the C2-M217 node, as "
                                  "Youxiong attaches beneath Q54433"),
            # A1: the Borjigin chain itself. Rashid al-Din's descent is
            # Bodonchar -> Buqa -> Dutum Menen -> Qaidu, which puts Khaidu under Q153230.
            # THE REPORT FLAGS THIS AS A JUDGEMENT CALL AND SO DOES THIS COMMENT: the
            # Secret History has Bodonchar -> Habich Baatar -> Menen Tudun -> Qachi Kulug
            # -> Qaidu, which would attach Khaidu one generation lower, at Q153225. Both
            # placeholders are unlabelled and carry no date and no wikidata_qid, so
            # nothing in the dump distinguishes them. Moving the edge down one node is the
            # whole correction if Emma prefers the Secret History reading.
            ("Q153230", "Q53399", "A1: Rashid al-Din -- Khaidu is the son of Dutum Menen"),
        ],
    },
}

FATHER, CHILD = "P47", "P20"


def load(qid):
    p = ITEMS / f"{qid}.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return d if isinstance(d, dict) else None


def save(qid, data):
    (ITEMS / f"{qid}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def claim_ids(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def make_claim(pid, target):
    num = int(target[1:]) if target[1:].isdigit() else None
    value = {"entity-type": "item", "id": target}
    if num is not None:
        value["numeric-id"] = num
    return {
        "mainsnak": {
            "snaktype": "value",
            "property": pid,
            "datavalue": {"value": value, "type": "wikibase-entityid"},
        },
        "type": "statement",
        "rank": "normal",
    }


def shadows_of(qid):
    """Every file whose internal id is qid but whose filename is not."""
    out = []
    path = ANALYSIS / "redirects.tsv"
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            i_from, i_to = header.index("from_qid"), header.index("to_qid")
        except ValueError:
            return out
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > max(i_from, i_to) and parts[i_to] == qid:
                out.append(parts[i_from])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv[1:]
    if not args or args[0] not in BRIDGES:
        print(__doc__)
        print("bridges: " + ", ".join(sorted(BRIDGES)))
        return 1
    name = args[0]
    spec = BRIDGES[name]

    print(f"bridge {name!r}\n")

    problems = []
    for rec in spec["create"]:
        if load(rec["qid"]) is not None:
            problems.append(f"{rec['qid']} already exists -- refusing to overwrite it")
    for parent, child, _why in spec["edges"]:
        for q in (parent, child):
            if load(q) is None and not any(r["qid"] == q for r in spec["create"]):
                problems.append(f"{q} does not exist and is not being created")
    if problems:
        print("ABORT -- preconditions failed:")
        for p in problems:
            print("  " + p)
        return 1

    for rec in spec["create"]:
        print(f"  CREATE {rec['qid']}  {rec['label']!r}")
        print(f"         {rec['note']}")
    for parent, child, why in spec["edges"]:
        pd, cd = load(parent), load(child)
        have_down = pd is not None and child in claim_ids(pd, CHILD)
        have_up = cd is not None and parent in claim_ids(cd, FATHER)
        state = ("already both directions" if (have_down and have_up)
                 else "parent side only" if have_down
                 else "child side only" if have_up else "new")
        print(f"  EDGE   {parent} -> {child}   ({state})")
        print(f"         {why}")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    for rec in spec["create"]:
        d = {
            "type": "item",
            "id": rec["qid"],
            "labels": {"en": {"language": "en", "value": rec["label"]}},
            "aliases": {"en": [{"language": "en", "value": a}
                               for a in rec.get("aliases", [])]},
            "descriptions": {},
            "claims": {},
        }
        save(rec["qid"], d)
        print(f"  created {rec['qid']}")

    touched = set()
    for parent, child, _why in spec["edges"]:
        pd = load(parent)
        if child not in claim_ids(pd, CHILD):
            pd.setdefault("claims", {}).setdefault(CHILD, []).append(
                make_claim(CHILD, child))
            save(parent, pd)
        cd = load(child)
        if parent not in claim_ids(cd, FATHER):
            cd.setdefault("claims", {}).setdefault(FATHER, []).append(
                make_claim(FATHER, parent))
            save(child, cd)
        touched.update((parent, child))
        print(f"  declared {parent} -> {child} on both sides")

    # Propagate to every file claiming a touched qid. None of these records has a shadow
    # today; that is a fact about the current dump, not a guarantee, so this runs anyway.
    n = 0
    for q in sorted(touched):
        final = load(q)
        for s in shadows_of(q):
            if (ITEMS / f"{s}.json").exists():
                save(s, final)
                n += 1
    print(f"  propagated to {n} shadow file(s)")

    print("\nverifying, from the files rather than from the plan...")
    ok = True
    for parent, child, _why in spec["edges"]:
        pd, cd = load(parent), load(child)
        down = child in claim_ids(pd, CHILD)
        up = parent in claim_ids(cd, FATHER)
        if not (down and up):
            print(f"  FAIL {parent} -> {child}: parent-side={down} child-side={up}")
            ok = False
    for q in sorted(touched):
        final = load(q)
        for s in shadows_of(q):
            if (ITEMS / f"{s}.json").exists() and load(s) != final:
                print(f"  FAIL shadow {s} disagrees with {q}")
                ok = False
    if ok:
        print("  every edge is declared on BOTH sides; all shadows agree")
    print("\nNow run: python wiki-scripts/verify_repair.py")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
