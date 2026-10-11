"""Queue item 16: take Icarius of Sparta out of Q73380 "BAD MERGE".

Q73380 carried three Wikidata ids: Q3356 Antiochus IV Epiphanes and Q2045778 the Seleucid prince
Antiochus (both sons of Antiochus III and Laodice III), and Q1658054 Icarius of Sparta, father of
Penelope. Icarius already has his own record, Q133344, which had no label: his parents Oebalus and
Gorgophone and all thirteen children name him, and his four wives list him as their husband. So
Q73380's Icarius claims (two parents, four wives, thirteen children) were one-sided duplicates of
edges Q133344 already holds. They are removed from Q73380, which is relabelled Antiochus IV
Epiphanes; Q133344 gets the label, the Wikidata id and its four marriages. (The prince/king
conflation inside the Seleucid half is not touched here.)

compare_depth (simulated 2026-10-10): the Seleucids lose nothing. Icarius's children go from 77
levels to 26, which is the false descent being removed: they had reached 77 through Antiochus III,
a Bronze-Age Spartan family descended from a 3rd-century BC king. They keep their mythic line
through Oebalus and Gorgophone. Accepted on the same reasoning as the 2026-08-15 Lepidus repair.

Every file claiming each record (shadows via redirects.tsv). Idempotent; dry run unless --write;
verifies from disk.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"
OLD, ICARIUS = "Q73380", "Q133344"
PARENTS = {"Q90289": "P47", "Q132823": "P48"}
WIVES = ["Q90277", "Q132314", "Q134310", "Q133345"]
CHILDREN = ["Q134318", "Q134312", "Q132139", "Q134319", "Q134311", "Q134320", "Q133346",
            "Q134315", "Q134316", "Q134314", "Q134321", "Q134317", "Q134313"]
MALE = "Q153718"


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def value(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else v


def values(data, pid):
    return [value(c) for c in (data.get("claims") or {}).get(pid, [])]


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid, "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def drop(data, pid, v):
    cl = (data.get("claims") or {}).get(pid, [])
    keep = [c for c in cl if value(c) != v]
    if len(keep) == len(cl): return False
    if keep: data["claims"][pid] = keep
    else: del data["claims"][pid]
    return True


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    if not set(CHILDREN) <= set(values(load(ICARIUS), "P20")):
        sys.exit(f"ABORT: {ICARIUS} does not hold all thirteen children")

    staged, log = {}, []
    get = lambda s: staged.setdefault(s, load(s))
    for s in fam(ICARIUS):
        d = get(s)
        if (d.get("labels") or {}).get("en", {}).get("value") != "Icarius of Sparta":
            d.setdefault("labels", {})["en"] = {"language": "en", "value": "Icarius of Sparta"}; log.append(f"  {s} (Icarius): label")
        if not (d.get("descriptions") or {}).get("en"):
            d.setdefault("descriptions", {})["en"] = {"language": "en", "value": "father of Penelope; son of Oebalus and Gorgophone"}
            log.append(f"  {s} (Icarius): description")
        d.setdefault("claims", {})
        if "Q1658054" not in values(d, "P61"):
            d["claims"].setdefault("P61", []).append({"mainsnak": {"snaktype": "value", "property": "P61",
                "datavalue": {"value": "Q1658054", "type": "string"}}, "type": "statement", "rank": "normal"})
            log.append(f"  {s} (Icarius): wikidata Q1658054")
        if not values(d, "P55"):
            d["claims"]["P55"] = [entity_claim("P55", MALE)]; log.append(f"  {s} (Icarius): sex male")
        for q in WIVES:
            if q not in values(d, "P42"):
                d["claims"].setdefault("P42", []).append(entity_claim("P42", q)); log.append(f"  {s} (Icarius): spouse {q}")
    for s in fam(OLD):
        d = get(s)
        for q, pid in PARENTS.items():
            if drop(d, pid, q): log.append(f"  {s}: drop {pid} {q}")
        for q in WIVES:
            if drop(d, "P42", q): log.append(f"  {s}: drop P42 {q}")
        for q in CHILDREN:
            if drop(d, "P20", q): log.append(f"  {s}: drop P20 {q}")
        if drop(d, "P61", "Q1658054"): log.append(f"  {s}: drop P61 Q1658054")
        if d["labels"]["en"]["value"] != "Antiochus IV Epiphanes":
            d["labels"]["en"]["value"] = "Antiochus IV Epiphanes"; log.append(f"  {s}: relabel")
        al = (d.get("aliases") or {}).get("en", [])
        if any(a["value"] == "Icarius of Sparta" for a in al):
            d["aliases"]["en"] = [a for a in al if a["value"] != "Icarius of Sparta"]; log.append(f"  {s}: drop alias Icarius")
        de = (d.get("descriptions") or {}).get("en", {})
        if de.get("value") == "father of Penelope":
            de["value"] = "king of the Seleucid Empire (175-164 BC)"; log.append(f"  {s}: description")
    print("\n".join(log) or "nothing to do")
    if not write or not log:
        if log: print(f"{len(log)} change(s) (dry run; --write to apply)")
        return 0
    for s, d in staged.items():
        if d != load(s): save(s, d)
    bad = []
    for s in fam(OLD):
        d = load(s)
        left = (set(values(d, "P47") + values(d, "P48")) & set(PARENTS)) | (set(values(d, "P42")) & set(WIVES)) \
            | (set(values(d, "P20")) & set(CHILDREN))
        if left: bad.append(f"{s} still holds {sorted(left)}")
    for s in fam(ICARIUS):
        d = load(s)
        if not set(WIVES) <= set(values(d, "P42")) or "Q1658054" not in values(d, "P61"): bad.append(f"{s} (Icarius) incomplete")
    print("VERIFY FAILED:\n  " + "\n  ".join(bad) if bad else "verified from disk")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
