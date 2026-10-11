"""Unmerge Q72786 "Marcus Aemilius Lepidus" (queue item 1; the ring itself was cut 2026-08-15).

Q72786 carried three father+mother couples plus a wife who was also recorded as its mother:

  A  Q73011 M. Aemilius Lepidus cos. 126 BC + Q72801 Cornelia, and Q72798 M. Livius Drusus
     -> these are MAMERCUS Aemilius Lepidus Livianus (wd Q721477; lepidus_resolved.md), who
        already has his own record, Q139719 (wd Q721477, father Q73011, mother Q72801, a wife and
        a child). So A is a parallel import: its edges come off Q72786, and the one thing Q139719
        lacked, the biological father Q72798 Livius Drusus, is added there. Adoptive (Q73011) +
        biological (Q72798) is the legitimate two-father case (CLAUDE.md, case 2).
  B  Q73113 M. Aemilius Lepidus (son of Q73275, praetor 218/213 BC) + Q73110 NN his wife
     -> a different Marcus. Split out to a NEW record, Q200037.
  C  Q73173 "M. Aemilius Lepidus, Consul"
     -> stays on Q72786, which keeps its label "Marcus Aemilius Lepidus".
  Q72789 "NN (Wife of Marcus Aemilius Lepidus)" was both Q72786's wife and its mother. A woman is
     not her husband's mother: the mother edge is dropped, the marriage kept.

Q72786 has no children, so no record below it loses ancestry. Every file sharing a qid (the
shadows; redirects.tsv) gets the same edit. Idempotent; dry run unless --write; verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER, P_SPOUSE, P_SEX, P_INST, P_ARMS = "P20", "P47", "P48", "P42", "P55", "P39", "P94"
MALE = "Q153718"
OLD, MAMERCUS, NEW_B = "Q72786", "Q139719", "Q200037"

# (qid, pid, value, action) -- action is "drop" or "add"; applied to every file claiming qid
EDITS = [
    (OLD, P_FATHER, "Q73011", "drop"), (OLD, P_MOTHER, "Q72801", "drop"),   # couple A
    (OLD, P_FATHER, "Q72798", "drop"),                                      # Mamercus's biological father
    (OLD, P_FATHER, "Q73113", "drop"), (OLD, P_MOTHER, "Q73110", "drop"),   # couple B
    (OLD, P_MOTHER, "Q72789", "drop"),                                      # his wife, not his mother
    ("Q73011", P_CHILD, OLD, "drop"), ("Q72801", P_CHILD, OLD, "drop"),     # A's son is Q139719, already listed
    ("Q72798", P_CHILD, OLD, "drop"), ("Q72798", P_CHILD, MAMERCUS, "add"),
    (MAMERCUS, P_FATHER, "Q72798", "add"),
    ("Q73113", P_CHILD, OLD, "drop"), ("Q73113", P_CHILD, NEW_B, "add"),
    ("Q73110", P_CHILD, OLD, "drop"), ("Q73110", P_CHILD, NEW_B, "add"),
    ("Q72789", P_CHILD, OLD, "drop"),
]

OLD_DESC = ("Marcus Aemilius Lepidus, son of Q73173 \"M. Aemilius Lepidus, Consul\" and husband of "
            "Q72789. Unmerged 2026-10-10: the parentage of Mamercus Aemilius Lepidus Livianus moved "
            "to his own record Q139719, and a second Marcus (son of Q73113) split out as Q200037. "
            "The Geni ids on this record came from the merged profiles and were not re-assigned.")
MAMERCUS_DESC = ("Roman consul 77 BC. Born a Livius Drusus (biological father Q72798 M. Livius "
                 "Drusus) and adopted into the Aemilii Lepidi (adoptive father Q73011 M. Aemilius "
                 "Lepidus, cos. 126 BC); the cognomen Livianus records it. Both fathers are correct.")
NEW_B_DESC = ("Marcus Aemilius Lepidus, son of Q73113 M. Aemilius Lepidus and Q73110 his wife; "
              "split out of Q72786 on 2026-10-10. Not yet identified in the prosopography.")


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    (ITEMS / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def values(data, pid):
    out = []
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid, "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def family():
    """qid -> every file stem that claims it (the record and its shadows)."""
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    return lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                      if (d := load(s)) is not None and (d.get("id") or s) == q]


def alias_set(q, fam):
    return set(fam(q)) | {q}


def apply_edit(data, pid, value, action, aliases):
    claims = (data.setdefault("claims", {})).setdefault(pid, [])
    if action == "drop":
        keep = [c for c in claims if (((c.get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}).get("id") not in aliases]
        changed = len(keep) != len(claims)
        data["claims"][pid] = keep
        if not keep: del data["claims"][pid]
        return changed
    if any(v in aliases for v in values(data, pid)): return False
    claims.append(entity_claim(pid, value)); return True


def set_desc(data, text):
    if (data.get("descriptions") or {}).get("en", {}).get("value") == text: return False
    data.setdefault("descriptions", {})["en"] = {"language": "en", "value": text}; return True


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    fam = family()
    for q in (OLD, MAMERCUS, "Q73011", "Q72801", "Q72798", "Q73113", "Q73110", "Q72789"):
        if not fam(q): sys.exit(f"ABORT: no file claims {q}")
    if load(NEW_B) is not None and load(NEW_B).get("id") != NEW_B:
        sys.exit(f"ABORT: {NEW_B}.json exists and is something else")
    if "Q721477" not in values(load(MAMERCUS), "P61"):
        sys.exit(f"ABORT: {MAMERCUS} does not carry wd Q721477")

    staged, n = {}, 0
    get = lambda s: staged.setdefault(s, load(s))
    if load(NEW_B) is None:
        new = {"type": "item", "id": NEW_B,
               "labels": {"en": {"language": "en", "value": "Marcus Aemilius Lepidus"}},
               "descriptions": {"en": {"language": "en", "value": NEW_B_DESC}}, "claims": {}}
        for pid, v in ((P_SEX, MALE), (P_FATHER, "Q73113"), (P_MOTHER, "Q73110")):
            new["claims"].setdefault(pid, []).append(entity_claim(pid, v))
        old = load(OLD)
        for pid in (P_INST, P_ARMS):
            if pid in old["claims"]: new["claims"][pid] = json.loads(json.dumps(old["claims"][pid]))
        staged[NEW_B] = new; n += 1; print(f"CREATE {NEW_B} 'Marcus Aemilius Lepidus' (son of Q73113 + Q73110)")
    for q, pid, v, action in EDITS:
        aliases = alias_set(v, fam) if v != NEW_B else {NEW_B}
        for s in fam(q):
            if apply_edit(get(s), pid, v, action, aliases):
                n += 1; print(f"  {s:8s} ({q}) {action} {pid} {v}")
    for q, text in ((OLD, OLD_DESC), (MAMERCUS, MAMERCUS_DESC)):
        for s in fam(q):
            if set_desc(get(s), text): n += 1; print(f"  {s:8s} ({q}) description")

    print(f"\n{n} change(s){'' if write else ' (dry run; --write to apply)'}")
    if not write or not n: return 0
    for s, d in staged.items(): save(s, d)

    # verify from disk, across every file of every touched qid
    bad = []
    for s in fam(OLD):
        d = load(s)
        if values(d, P_FATHER) != ["Q73173"] or values(d, P_MOTHER) or values(d, P_SPOUSE) != ["Q72789"]:
            bad.append(f"{s}: F={values(d, P_FATHER)} M={values(d, P_MOTHER)} S={values(d, P_SPOUSE)}")
    for s in fam(MAMERCUS):
        if set(values(load(s), P_FATHER)) != {"Q73011", "Q72798"}: bad.append(f"{s}: F={values(load(s), P_FATHER)}")
    for q in ("Q73011", "Q72801", "Q72798", "Q73113", "Q73110", "Q72789"):
        for s in fam(q):
            if alias_set(OLD, fam) & set(values(load(s), P_CHILD)): bad.append(f"{s} ({q}) still lists {OLD} as a child")
    for q in ("Q73113", "Q73110"):
        for s in fam(q):
            if NEW_B not in values(load(s), P_CHILD): bad.append(f"{s} ({q}) lacks child {NEW_B}")
    print("VERIFY FAILED:\n  " + "\n  ".join(bad) if bad else "verified from disk")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
