# Build a GEDCOM 7 of the old order.life Wikibase from its family tables (Emma, 2026-11-17: "these TSV files essentially
# could ... have us construct an entire GEDCOM of the old wiki base ... I want to do network analysis on it").
# Built on every deploy and published as /wikibase.ged beside /gaiad.ged (deploy.yml, 2026-11-18).
#
#   python wiki-scripts/build_wikibase_ged.py [wikibase/analysis] [out.ged]
#
# Inputs: persons.tsv (qid, label, sex, birth, death, gedcom, wikidata_qid, geni_id), edges.tsv (parent, child),
# spouses.tsv (a, b). People are INDI @<qid>@; families are one per parent pair (from edges, plus couples from
# spouses.tsv with no children). Records whose label contains "<private>" (living people from tree exports) are left
# out, with every link to them. Sex: Q153718 male, Q153719 female (Aster, Q1, is Q153719), anything else U.
import collections, csv, re, sys

A = sys.argv[1] if len(sys.argv) > 1 else "wikibase/analysis"
OUT = sys.argv[2] if len(sys.argv) > 2 else "site/wikibase.ged"
SEX = {"Q153718": "M", "Q153719": "F"}

persons = {r["qid"]: r for r in csv.DictReader(open(f"{A}/persons.tsv", encoding="utf-8"), delimiter="\t")}
private = {q for q, r in persons.items() if "<private>" in (r["label"] or "")}
keep = lambda q: q in persons and q not in private

parents = collections.defaultdict(set)
for r in csv.DictReader(open(f"{A}/edges.tsv", encoding="utf-8"), delimiter="\t"):
    if keep(r["parent"]) and keep(r["child"]):
        parents[r["child"]].add(r["parent"])
couples = set()
for r in csv.DictReader(open(f"{A}/spouses.tsv", encoding="utf-8"), delimiter="\t"):
    if keep(r["a"]) and keep(r["b"]) and r["a"] != r["b"]:
        couples.add(tuple(sorted((r["a"], r["b"]))))

fams = collections.defaultdict(list)          # parent tuple -> children
for c, ps in parents.items():
    ps = sorted(ps)
    if len(ps) <= 2:
        fams[tuple(ps)].append(c)
    else:                                       # more than two parents: one family per parent (data error kept visible)
        for p in ps:
            fams[(p,)].append(c)
for cp in sorted(couples):   # sorted: set order changes between runs, and builds should diff cleanly
    fams.setdefault(cp, [])

def date(s):
    m = re.match(r"([+-])?(\d+)-(\d\d)-(\d\d)", s or "")
    if not m:
        return None
    y, mo, d = int(m.group(2)), int(m.group(3)), int(m.group(4))
    bc = " BCE" if m.group(1) == "-" else ""
    mon = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    if mo and d:
        return f"{d} {mon[mo-1]} {y}{bc}"
    if mo:
        return f"{mon[mo-1]} {y}{bc}"
    return f"{y}{bc}"

famid = {k: f"F{i+1}" for i, k in enumerate(sorted(fams))}
famc = collections.defaultdict(list); fams_of = collections.defaultdict(list)
for k, kids in fams.items():
    for p in k:
        fams_of[p].append(famid[k])
    for c in kids:
        famc[c].append(famid[k])

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    w = lambda s: f.write(s + "\n")
    w("0 HEAD"); w("1 GEDC"); w("2 VERS 7.0"); w("1 SOUR build_wikibase_ged.py")
    w("1 NOTE The old order.life Wikibase (wikibase/analysis tables), private records left out.")
    for q, r in persons.items():
        if q in private:
            continue
        w(f"0 @{q}@ INDI")
        name = (r["gedcom"] or r["label"] or "").strip() or "?"
        if q == "Q2":  # her name; the old Q2 is wrong ("Emma H. Leonhart"; INTENT.md, 2026-11-17)
            name = "Emma /Leonhart/"
        w(f"1 NAME {name}")
        w(f"1 SEX {SEX.get(r['sex'], 'U')}")
        for tag, key in (("BIRT", "birth"), ("DEAT", "death")):
            d = date(r[key])
            if d:
                w(f"1 {tag}"); w(f"2 DATE {d}")
        w(f"1 REFN {q}"); w("2 TYPE order.life")
        if r.get("wikidata_qid"):
            w(f"1 EXID {r['wikidata_qid']}"); w("2 TYPE http://www.wikidata.org/entity/")
        if r.get("geni_id"):
            w(f"1 EXID {r['geni_id']}"); w("2 TYPE https://www.geni.com/profile/index/")
        for fid in sorted(famc.get(q, []), key=lambda x: int(x[1:])):
            w(f"1 FAMC @{fid}@")
        for fid in sorted(fams_of.get(q, []), key=lambda x: int(x[1:])):
            w(f"1 FAMS @{fid}@")
    for k, kids in fams.items():
        w(f"0 @{famid[k]}@ FAM")
        # GEDCOM 7 allows one HUSB and one WIFE; they are partner slots, sex is on the INDI. Two parents of the same
        # sex (or unknown) take both slots, so family links stay single-valued (check_gedcom_links.py).
        roles = ['WIFE' if SEX.get(persons[p]['sex']) == 'F' else 'HUSB' for p in k]
        if len(k) == 2 and roles[0] == roles[1]:
            roles = ['HUSB', 'WIFE']
        for p, role in zip(k, roles):
            w(f"1 {role} @{p}@")
        for c in kids:
            w(f"1 CHIL @{c}@")
    w("0 TRLR")
print(f"{OUT}: {len(persons)-len(private):,} people ({len(private)} private left out), {len(fams):,} families")
