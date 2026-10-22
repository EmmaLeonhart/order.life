"""Records for people the Gaiad names but the genealogy had no record of (parent repo queue, Emma's choice
2026-10-21: "Records for unmatched people").

The names are the Gaiad's unresolved {{c|}} tags (Gaiad/genealogy/_resolution.tsv) tagged three or more
times whose top Wikidata search hit is that person, each checked against its verse lines. Left out on that
check: Seneca (the nation), Teuthis (the squid), Sapa Inca (a title), Hachiman (Ojin in this genealogy),
Yudhishthira and Osceola (the search hit was someone else), and God, Goddess, Genoese, Ilkhanate, Analytical
Engine (not people).

Each record gets the Wikidata English label and description, sex (P55), the Wikidata id (P61), and only the
family links Wikidata itself states (P22 father, P25 mother, P40 child, P26 spouse) to a person who already
has an order.life record (by its P61) or is in this batch: P47/P48/P20/P42 on the new record only, so no
existing file is edited (extract_genealogy.py builds the edges from either side). No dates: the dump's BCE
convention is not settled (Q135519 Cambyses II has birth +0559). A name whose Wikidata labels or aliases
already match an order.life person (wikibase/analysis/person_names.tsv) is reported and not created.
New ids from Q300001: nothing in the repository refers to Q300000-Q300999 (checked 2026-10-21).
Writes the matching rows to Gaiad/genealogy/_overrides.tsv so each tag resolves to its record.

    python wiki-scripts/create_gaiad_person_records.py           # dry run
    python wiki-scripts/create_gaiad_person_records.py --write

Stdlib only.
"""
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
ANA = ROOT / "wikibase" / "analysis"
OVERRIDES = ROOT / "Gaiad" / "genealogy" / "_overrides.tsv"
MALE, FEMALE = "Q153718", "Q153719"
WD_SEX = {"Q6581097": MALE, "Q6581072": FEMALE}
UA = {"User-Agent": "order.life-genealogy/1.0 (https://order.life)"}
FIRST_ID = 300001

# (tag name in the Gaiad, Wikidata id)
PEOPLE = [
    ("Laozi", "Q9333"), ("Ravana", "Q235102"), ("Akhenaten", "Q81794"), ("Ramesses II", "Q1523"),
    ("Cao Cao", "Q204077"), ("Little Turtle", "Q1355169"), ("Napoleon", "Q517"), ("Tupac Amaru", "Q296269"),
    ("Marduk", "Q190123"), ("Thutmose III", "Q157899"), ("Kūkai", "Q222227"), ("Tutankhamun", "Q12154"),
    ("Thucydides", "Q41683"), ("Guan Yu", "Q222797"), ("Xuanzang", "Q42063"), ("Nanak", "Q83322"),
    ("George W. Bush", "Q207"), ("Naram-Sin", "Q297506"), ("Nietzsche", "Q9358"), ("Phidias", "Q177302"),
    ("Ashurbanipal", "Q171191"), ("Liu Bang", "Q7210"), ("Zhuge Liang", "Q198211"), ("Constantine XI", "Q37142"),
    ("Menkaure", "Q200986"), ("Ur-Nammu", "Q297417"), ("Averroes", "Q39837"), ("Parmenion", "Q296233"),
    ("Megasthenes", "Q312548"), ("Vladimir Putin", "Q7747"), ("Putin", "Q7747"), ("Donald Trump", "Q22686"),
    ("Shennong", "Q313336"), ("Mentuhotep II", "Q296439"), ("Dyaus", "Q1133509"), ("Mahavira", "Q9422"),
    ("Copernicus", "Q619"), ("Bindusara", "Q315526"), ("Emperor Wu", "Q7225"), ("Sun Quan", "Q313327"),
    ("Sun Wukong", "Q11773777"), ("Saichō", "Q449943"), ("Murad II", "Q131394"), ("Charles VII", "Q133372"),
    ("Formosus", "Q170499"), ("Mormon", "Q2701214"), ("Joseph Smith", "Q47102"), ("Kangxi", "Q17790"),
    ("Voltaire", "Q9068"), ("Baháʼu'lláh", "Q101054"), ("Paul VI", "Q16975"), ("Deng Xiaoping", "Q16977"),
    ("Osama bin Laden", "Q1317"), ("Saddam Hussein", "Q1316"), ("Barack Obama", "Q76"),
    ("Geoffrey Hinton", "Q92894"), ("Xi Jinping", "Q15031"), ("Aung San Suu Kyi", "Q36740"),
    ("Joe Biden", "Q6279"), ("Alexei Navalny", "Q155979"),
]


def norm(s):
    return re.sub(r"\s+", " ", s.replace("/", " ")).strip().lower()


def wd_entities(ids):
    out = {}
    ids = sorted(set(ids))
    for i in range(0, len(ids), 50):
        url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "wbgetentities", "ids": "|".join(ids[i:i + 50]), "props": "labels|aliases|descriptions|claims",
             "languages": "en", "format": "json"})
        out.update(json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))["entities"])
        time.sleep(0.5)
    return out


def wd_values(ent, pid):
    vals = []
    for c in ent.get("claims", {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            vals.append(v["id"])
    return vals


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid, "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    wd2ol = {}
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["wikidata_qid"]:
                wd2ol.setdefault(r["wikidata_qid"], r["qid"])
    known = defaultdict(set)
    with open(ANA / "person_names.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            known[norm(r["name"])].add(r["qid"])
    ents = wd_entities([wd for _, wd in PEOPLE])

    new, skipped, nid = {}, [], FIRST_ID
    for name, wd in PEOPLE:
        if wd in new or wd in wd2ol:
            continue
        e = ents.get(wd, {})
        label = (e.get("labels", {}).get("en") or {}).get("value", name)
        names = {label, name} | {a["value"] for a in e.get("aliases", {}).get("en", [])}
        clash = sorted({q for n in names for q in known.get(norm(n), ())})
        if clash:
            skipped.append((name, wd, label, clash))
            continue
        while (ITEMS / f"Q{nid}.json").exists():
            nid += 1
        new[wd] = f"Q{nid}"
        nid += 1
    target = {**wd2ol, **new}

    rows = []
    first_name = {}
    for name, wd in PEOPLE:
        first_name.setdefault(wd, name)
    for wd, q in new.items():
        e = ents[wd]
        label = (e.get("labels", {}).get("en") or {}).get("value") or first_name[wd]
        desc = (e.get("descriptions", {}).get("en") or {}).get("value", "")
        claims = {"P61": [{"mainsnak": {"snaktype": "value", "property": "P61",
                                        "datavalue": {"value": wd, "type": "string"}},
                           "type": "statement", "rank": "normal"}]}
        sex = next((WD_SEX[s] for s in wd_values(e, "P21") if s in WD_SEX), None)
        if sex:
            claims["P55"] = [entity_claim("P55", sex)]
        links = []
        for wpid, opid in (("P22", "P47"), ("P25", "P48"), ("P40", "P20"), ("P26", "P42")):
            hits = [target[v] for v in wd_values(e, wpid) if v in target]
            if hits:
                claims[opid] = [entity_claim(opid, h) for h in hits]
                links.append(f"{opid} {' '.join(hits)}")
        rec = {"type": "item", "id": q, "labels": {"en": {"language": "en", "value": label}},
               "descriptions": {"en": {"language": "en", "value": (desc + "; " if desc else "") +
                                       "record created 2026-10-21 for the Gaiad's tags, from Wikidata " + wd}},
               "claims": claims}
        print(f"{q} {label} ({wd}) {'; '.join(links)}")
        if write:
            with open(ITEMS / f"{q}.json", "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    for name, wd in PEOPLE:
        if wd in new:
            rows.append(f"{name}\t{new[wd]}\tnew record for the Gaiad's tags, from Wikidata {wd} "
                        f"(wiki-scripts/create_gaiad_person_records.py, 2026-10-21)\n")
    for s in skipped:
        print(f"NOT CREATED {s[0]} ({s[1]} {s[2]}): Wikidata names already on {', '.join(s[3])}")
    print(f"{len(new)} new records, {len(skipped)} not created, {len(rows)} override rows")
    if write:
        with open(OVERRIDES, "a", encoding="utf-8", newline="\n") as fh:
            fh.writelines(rows)
        bad = [q for q in new.values() if not (ITEMS / f"{q}.json").exists()]
        print("VERIFY FAILED: " + ", ".join(bad) if bad else "verified from disk")
        return 1 if bad else 0
    print("(dry run; --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
