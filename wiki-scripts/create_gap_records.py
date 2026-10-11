"""Queue item 17: create the four records that other records point to but that have no file.

Identified on 2026-10-10 from their neighbours (research, not naming: each is a well-known figure
whose place in the dump leaves no doubt):
  Q74656  Zeus           child of Saturn Q74680 and Ops Q74677; 60 consorts (Metis, Eurynome,
                         Dione, ...); 144 children (Aphrodite, the Horae, Dike, Eirene, ...). wd Q34201
  Q75282  Apollo         child of Leto Q131510; consorts Calliope, Cyrene, Hecuba, ...; children
                         Linus, Aristaeus, Troilus, Miletus, ... wd Q37340
  Q54196  Neoptera       clade between Q30622 and Eumetabola Q1435 / Polyneoptera Q30715 in the
                         evolutionary taxonomy. wd Q23005
  Q78402  Cleopatra IV   child of Ptolemy VIII and Cleopatra III; married Ptolemy IX, then Antiochus
                         IX. wd Q40023

Each new record gets its label, Wikidata id, sex (not for the clade) and the family claims its
neighbours already declare about it (parent's P20 -> its P47/P48 by the parent's sex; a child's
P47/P48 -> its P20; a spouse's P42 -> its P42). Graph-neutral: extract_genealogy.py already builds
these edges from the neighbours' side. Dry run unless --write; verifies from disk.
"""

import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
MALE, FEMALE = "Q153718", "Q153719"
GAPS = {
    "Q74656": ("Zeus", "king of the gods in Greek mythology, son of Saturn (Cronus) and Ops (Rhea)", "Q34201", MALE),
    "Q75282": ("Apollo", "god in Greek and Roman mythology, son of Leto", "Q37340", MALE),
    "Q54196": ("Neoptera", "infraclass of insects", "Q23005", None),
    "Q78402": ("Cleopatra IV", "queen of Egypt (116-115 BC), daughter of Ptolemy VIII and Cleopatra III", "Q40023", FEMALE),
}


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid, "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def value(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else v


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    found = collections.defaultdict(lambda: collections.defaultdict(set))   # gap -> pid -> neighbours
    pattern = "|".join(f'"{q}"' for q in GAPS)
    names = subprocess.run(["git", "grep", "-l", "-E", pattern, "--", "wikibase/items/*.json"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8").stdout.split()
    for n in names:
        d = json.loads((ROOT / n).read_text(encoding="utf-8"))
        if not isinstance(d, dict): continue
        who = d.get("id") or Path(n).stem
        sex = next((value(c) for c in (d.get("claims") or {}).get("P55", [])), None)
        for pid in ("P20", "P47", "P48", "P42"):
            for c in (d.get("claims") or {}).get(pid, []):
                g = value(c)
                if g not in GAPS: continue
                if pid == "P20":
                    if sex in (MALE, FEMALE): found[g]["P47" if sex == MALE else "P48"].add(who)
                    else: found[g]["P47?"].add(who)
                elif pid in ("P47", "P48"): found[g]["P20"].add(who)
                else: found[g]["P42"].add(who)
    for g, (label, desc, wd, sex) in GAPS.items():
        if (ITEMS / f"{g}.json").exists():
            print(f"{g}: file exists, skipped"); continue
        f = found[g]
        print(f"{g} {label}: " + ", ".join(f"{p} {len(v)}" for p, v in sorted(f.items())))
        if f.get("P47?"): print(f"   parents with no sex, left out: {sorted(f['P47?'])}")
        claims = {"P61": [{"mainsnak": {"snaktype": "value", "property": "P61",
                                        "datavalue": {"value": wd, "type": "string"}},
                           "type": "statement", "rank": "normal"}]}
        if sex: claims["P55"] = [entity_claim("P55", sex)]
        for pid in ("P47", "P48", "P42", "P20"):
            if f.get(pid): claims[pid] = [entity_claim(pid, q) for q in sorted(f[pid], key=lambda x: int(x[1:]))]
        rec = {"type": "item", "id": g, "labels": {"en": {"language": "en", "value": label}},
               "descriptions": {"en": {"language": "en", "value": desc + " (record created 2026-10-10; "
                                       "other records already pointed to it)"}}, "claims": claims}
        if write:
            with open(ITEMS / f"{g}.json", "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    if write:
        bad = [g for g in GAPS if not (ITEMS / f"{g}.json").exists()]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    print("(dry run; --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
