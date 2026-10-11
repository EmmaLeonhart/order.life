"""Queue item 16: unmerge the two Fernando Rodríguez de Castros held by Q123528.

Wikidata has two men of the name:
  Q3006087  1280-1304, son of Esteban Fernández de Castro (Q3368946 = dump Q123526) and Aldonza
            Rodríguez de León (Q5664522 = dump Q118368). Q123528 carries this id and these parents,
            on its own record. It stays as it is.
  Q5444910  1125-1185, son of Rodrigo Fernández de Castro (Q9070237 = dump Q113686) and Eilo Álvarez
            (Q101403714 = dump Q115832), father of Pedro Fernández de Castro (Q3848149 = dump Q119242).
            Not in the dump. Rodrigo and Eilo listed Q123528 as their child, and Pedro named Q123528
            as his father, which made a man born about 1090 the grandfather's generation of one born
            in 1280. Created here as Q200038, and those three edges move to him.

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
OLD, NEW = "Q123528", "Q200038"
RODRIGO, EILO, PEDRO = "Q113686", "Q115832", "Q119242"
MALE = "Q153718"


def load(stem):
    p = ITEMS / f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(stem, data):
    with open(ITEMS / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


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


def string_claim(pid, text):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": text, "type": "string"}}, "type": "statement", "rank": "normal"}


def time_claim(pid, year):
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": {"type": "time", "value": {
        "time": f"+{year:04d}-00-00T00:00:00Z", "timezone": 0, "before": 0, "after": 0, "precision": 9,
        "calendarmodel": "http://www.wikidata.org/entity/Q1985727"}}}, "type": "statement", "rank": "normal"}


def repoint(data, pid, old, new):
    changed = False
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id") == old:
            v["id"] = new; v["numeric-id"] = int(new[1:]); changed = True
    return changed


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    sib = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            sib[r["to_qid"]].add(r["from_qid"])
    fam = lambda q: [s for s in sorted(sib.get(q, set()) | {q}, key=lambda x: int(x[1:]))
                     if (d := load(s)) is not None and (d.get("id") or s) == q]
    if "Q3006087" not in values(load(OLD), "P61"): sys.exit(f"ABORT: {OLD} does not carry wd Q3006087")
    if load(NEW) is not None and load(NEW).get("id") != NEW: sys.exit(f"ABORT: {NEW}.json is something else")

    staged, log = {}, []
    get = lambda s: staged.setdefault(s, load(s))
    if load(NEW) is None:
        new = {"type": "item", "id": NEW,
               "labels": {"en": {"language": "en", "value": "Fernando Rodríguez de Castro"}},
               "descriptions": {"en": {"language": "en", "value":
                   "Castilian nobleman and royal steward (1125-1185), lord of the House of Castro; "
                   "split out of Q123528 on 2026-10-10, which is the later man of the name (1280-1304)"}},
               "claims": {"P55": [entity_claim("P55", MALE)], "P47": [entity_claim("P47", RODRIGO)],
                          "P48": [entity_claim("P48", EILO)], "P20": [entity_claim("P20", PEDRO)],
                          "P61": [string_claim("P61", "Q5444910")],
                          "P56": [time_claim("P56", 1125)], "P57": [time_claim("P57", 1185)]}}
        staged[NEW] = new; log.append(f"CREATE {NEW} Fernando Rodríguez de Castro (1125-1185, wd Q5444910)")
    for q in (RODRIGO, EILO):
        for s in fam(q):
            if repoint(get(s), "P20", OLD, NEW): log.append(f"  {s} ({q}): child {OLD} -> {NEW}")
    for s in fam(PEDRO):
        if repoint(get(s), "P47", OLD, NEW): log.append(f"  {s} ({PEDRO}): father {OLD} -> {NEW}")
    for s in fam(OLD):
        d = get(s)
        if PEDRO in values(d, "P20"):
            d["claims"]["P20"] = [c for c in d["claims"]["P20"] if values({"claims": {"x": [c]}}, "x") != [PEDRO]]
            log.append(f"  {s} ({OLD}): drop child {PEDRO}")
    print("\n".join(log) or "nothing to do")
    if not write or not log:
        if log: print("(dry run; --write to apply)")
        return 0
    for s, d in staged.items():
        if d != load(s): save(s, d)
    bad = []
    for q in (RODRIGO, EILO):
        for s in fam(q):
            if OLD in values(load(s), "P20") or NEW not in values(load(s), "P20"): bad.append(s)
    for s in fam(PEDRO):
        if values(load(s), "P47") and (OLD in values(load(s), "P47") or NEW not in values(load(s), "P47")): bad.append(s)
    for s in fam(OLD):
        if set(values(load(s), "P47")) != {"Q123526"} or PEDRO in values(load(s), "P20"): bad.append(s)
    print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
