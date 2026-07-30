"""Apply the Q74698 unmerge: separate Ouranos/Caelus from Tros of Dardania.

Q74698 carried BOTH figures. The Trojan half is already held correctly and completely by
Q132327 (wd Q599482) -- same parents, same spouses, same five children -- so this removes
the duplicated Trojan edges from Q74698 rather than creating anything.

Evidence that Q74698 is Ouranos and not Tros:
  * its own English aliases are ['Uranus', 'Caelus', 'Tros', 'Ouranos - - Uranos Caelus']
  * its 65 remaining children, all by Terra (Gaia), are the complete canonical offspring of
    Ouranos and Gaia: Titans, Cyclopes, Hekatoncheires, Gigantes, Erinyes
  * its remaining parents Aether + Dies + Terra are Hyginus's genealogy for Caelus
  * it carries THREE P61 Wikidata ids including Q599482, which is Q132327's own id

Also repoints Nilus's father from Danaus to Oceanus. Nilus is Danaus's ancestor
(Nilus -> Anchiroe -> Danaus); Q90309 Oceanus already lists Nilus among its children.

Idempotent: re-running changes nothing. Verifies before and after, and refuses to write if
the Trojan half is not fully present on Q132327.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"

TROJAN_CHILDREN = ["Q132329", "Q132330", "Q132331", "Q133643", "Q133644"]

# (property, value-qid, why)
REMOVE_FROM_Q74698 = [
    ("P61", "Q599482", "Q132327's own Wikidata id, duplicated onto this record"),
    ("P47", "Q132328", "father Erichthonius of Dardania -- Tros of Dardania's father"),
    ("P48", "Q131114", "mother Astyoche -- Tros of Dardania's mother"),
    ("P42", "Q131068", "spouse Callirhoe -- Tros of Dardania's wife"),
    ("P42", "Q133642", "spouse Acallaris -- Tros of Dardania's wife"),
] + [("P20", c, "child of Tros of Dardania, already on Q132327") for c in TROJAN_CHILDREN]


def load(qid):
    return json.loads((ITEMS / f"{qid}.json").read_text(encoding="utf-8"))


def save(qid, data):
    (ITEMS / f"{qid}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def values(item, pid):
    out = []
    for c in item.get("claims", {}).get(pid, []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def drop(item, pid, qid):
    claims = item.get("claims", {}).get(pid)
    if not claims:
        return 0
    before = len(claims)
    kept = []
    for c in claims:
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if (v.get("id") if isinstance(v, dict) else v) != qid:
            kept.append(c)
    if kept:
        item["claims"][pid] = kept
    else:
        del item["claims"][pid]
    return before - len(kept)


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # --- precondition: the Trojan half must be intact on Q132327 -------------
    tros = load("Q132327")
    problems = []
    if values(tros, "P47") != ["Q132328"]:
        problems.append(f"Q132327 father is {values(tros, 'P47')}, expected ['Q132328']")
    if values(tros, "P48") != ["Q131114"]:
        problems.append(f"Q132327 mother is {values(tros, 'P48')}, expected ['Q131114']")
    if set(values(tros, "P20")) != set(TROJAN_CHILDREN):
        problems.append(f"Q132327 children are {values(tros, 'P20')}, expected the five Trojan children")
    if "Q599482" not in values(tros, "P61"):
        problems.append("Q132327 does not carry wd Q599482")
    if problems:
        print("REFUSING TO WRITE -- the Trojan half is not fully held by Q132327:")
        for p in problems:
            print("   ", p)
        return 1
    print("precondition OK: Q132327 holds the complete Trojan Tros (parents, spouses, 5 children)\n")

    # --- Q74698: strip the duplicated Trojan edges ---------------------------
    ur = load("Q74698")
    print(f"Q74698 before: label={ur['labels']['en']['value']!r} "
          f"children={len(values(ur, 'P20'))} father={values(ur, 'P47')} "
          f"mother={values(ur, 'P48')} spouse={values(ur, 'P42')} P61={values(ur, 'P61')}")
    removed = 0
    for pid, qid, why in REMOVE_FROM_Q74698:
        n = drop(ur, pid, qid)
        removed += n
        print(f"   {'removed' if n else 'absent '} {pid} {qid:9s} -- {why}")

    # relabel: this record is Ouranos. Its own aliases already say so.
    if ur["labels"]["en"]["value"] == "Tros":
        ur["labels"]["en"]["value"] = "Uranus"
        print("   relabelled en: 'Tros' -> 'Uranus'")
    ur["aliases"]["en"] = [a for a in ur["aliases"].get("en", []) if a["value"] != "Tros"]
    d = ur.get("descriptions", {}).get("en")
    if d and d["value"] == "ruler of Troy in Greek mythology":
        d["value"] = "primordial sky god in Greek mythology, father of the Titans"
        print("   description: 'ruler of Troy...' -> primordial sky god")

    print(f"Q74698 after : label={ur['labels']['en']['value']!r} "
          f"children={len(values(ur, 'P20'))} father={values(ur, 'P47')} "
          f"mother={values(ur, 'P48')} spouse={values(ur, 'P42')} P61={values(ur, 'P61')}")
    save("Q74698", ur)

    # --- Q130061 Nilus: father Danaus -> Oceanus -----------------------------
    nilus = load("Q130061")
    print(f"\nQ130061 Nilus before: father={values(nilus, 'P47')} mother={values(nilus, 'P48')}")
    if values(nilus, "P47") == ["Q74973"]:
        oceanus = load("Q90309")
        if "Q130061" not in values(oceanus, "P20"):
            print("   REFUSING: Q90309 Oceanus does not list Nilus as a child")
            return 1
        for c in nilus["claims"]["P47"]:
            v = c["mainsnak"]["datavalue"]["value"]
            if v.get("id") == "Q74973":
                v["id"] = "Q90309"
                v.pop("numeric-id", None)
        print("   father Q74973 (Danaus) -> Q90309 (Oceanus); Oceanus already lists Nilus as a child")
        save("Q130061", nilus)
    else:
        print("   already repointed, nothing to do")
    print(f"Q130061 Nilus after : father={values(load('Q130061'), 'P47')} "
          f"mother={values(load('Q130061'), 'P48')}")

    print(f"\n{removed} claim(s) removed from Q74698.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
