"""Check that every family link in a GEDCOM is written from both sides.

Usage: python check_gedcom_links.py [FILE.ged]

Copied from genealogy/new/rootsmagic-import/check_gedcom_links.py (2026-09-29), where it was written for MyHeritage's export
error ("families or individuals that are not stored properly"). Here it fails the build (exit 1) on any problem
(Emma, 2026-10-29: "it probably should be part of a CI/CD and a failed test if it generates like this").
"""
import re, collections, sys
G = sys.argv[1] if len(sys.argv) > 1 else "site/gaiad.ged"
recs = {}; cur = None
for line in open(G, encoding="utf-8-sig"):
    m = re.match(r"0 @(\w+)@ (\w+)", line)
    if m: cur = m.group(1); recs[cur] = (m.group(2), collections.defaultdict(list)); continue
    if line.startswith("0 "): cur = None; continue
    m = re.match(r"1 (FAMC|FAMS|HUSB|WIFE|CHIL) @(\w+)@", line)
    if cur and m: recs[cur][1][m.group(1)].append(m.group(2))
bad = collections.Counter(); ex = {}
def flag(k, v): bad[k] += 1; ex.setdefault(k, v)
for rid, (typ, links) in recs.items():
    if typ == "INDI":
        for f in links["FAMC"]:
            if rid not in recs[f][1]["CHIL"]: flag("FAMC without CHIL", (rid, f))
        for f in links["FAMS"]:
            if rid not in recs[f][1]["HUSB"] + recs[f][1]["WIFE"]: flag("FAMS without HUSB/WIFE", (rid, f))
        for t in ("FAMC", "FAMS"):
            if len(links[t]) != len(set(links[t])): flag("repeated " + t, rid)
        if set(links["FAMC"]) & set(links["FAMS"]): flag("child and spouse in same family", rid)
    elif typ == "FAM":
        for i in links["CHIL"]:
            if rid not in recs[i][1]["FAMC"]: flag("CHIL without FAMC", (rid, i))
        for t in ("HUSB", "WIFE"):
            for i in links[t]:
                if rid not in recs[i][1]["FAMS"]: flag(t + " without FAMS", (rid, i))
            if len(links[t]) > 1: flag("more than one " + t, rid)
        if len(links["CHIL"]) != len(set(links["CHIL"])): flag("repeated CHIL", rid)
        if links["HUSB"] and links["HUSB"] == links["WIFE"]: flag("HUSB is WIFE", rid)
        if not (links["HUSB"] or links["WIFE"] or links["CHIL"]): flag("empty family", rid)
print("problems:" if bad else "no link problems found")
for k, n in bad.most_common(): print(f"  {n} {k}, e.g. {ex[k]}")
sys.exit(1 if bad else 0)
