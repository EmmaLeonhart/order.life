"""
The central authority file for individuals: authority/individuals.tsv (Emma, 2026-11-27/28).

Her design (inochi-no-michikyo queue, 2026-11-27 ~20:0x-22:4x BCDT): "every single individual gets [...] a UUID
assigned to them durably"; "the standard form of UUID that's globally unique. There's no ordering"; "UUIDs have the
ability to redirect"; "a central file that [...] does the sort of universal entity resolution [...] a TSV file";
"First column is the UUID as the primary key. Second column, either [...] a sentinel value [...] or [...] the UUID it
redirects to. And then all the rest of the values are the other keys", in the order "wiki.order.life first, then
family search, then [Geni], then Wikidata, and then any other random thing it might join on." Sentinel: "-". Place
and name: authority/individuals.tsv in order.life (Emma, 2026-11-28: "Yeah do both").

What joins what (nothing is matched by name, position or date; only an id the two records both carry):
  wikibase/analysis/gaiad_legacy_numbers.tsv   one row per legacy number = one individual. Its refn holds the
                                               wiki.order.life Q, its exid the FamilySearch, Geni and Wikidata ids;
                                               for the verse people the legacy number is the tag number
                                               ({{c|4493|Dolly}}) and uid their version-5 UID.
  wikibase/analysis/gaiad_legacy_merges.tsv    "<n> into <m>": n's UUID redirects to m's.
  Gaiad/ancestry/emma-ancestry.ged             each @S@ INDI joins the row that shares one of its ids (REFN Q, EXID
                                               FamilySearch/Geni/Wikidata), only when exactly one row does.

The UUIDs are uuid4, made once and kept in the file: a run reads the existing file first, keeps every UUID it holds
(matched by legacy number) and only adds rows. The values are refreshed from the sources each run.

    python authority/build_individuals.py           writes authority/individuals.tsv and prints the report
Stdlib only.
"""
import collections
import csv
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "wikibase" / "analysis" / "gaiad_legacy_numbers.tsv"
MERGES = ROOT / "wikibase" / "analysis" / "gaiad_legacy_merges.tsv"
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "emma-ancestry.ged"
OUT = Path(__file__).resolve().parent / "individuals.tsv"
SENTINEL = "-"
COLUMNS = ["uuid", "redirect", "wiki_order_life", "familysearch", "geni", "wikidata",
           "gaiad_legacy_number", "gaiad_verse_uid", "emma_ancestry", "other"]

FS_RE = re.compile(r"[0-9A-Z]{4}-[0-9A-Z]{3,4}")
GENI_RE = re.compile(r"6\d{15,18}")
Q_RE = re.compile(r"Q\d+")


def kind(x):
    if FS_RE.fullmatch(x): return "familysearch"
    if GENI_RE.fullmatch(x): return "geni"
    if Q_RE.fullmatch(x): return "wikidata"
    return "other"


def join(vals):
    return "|".join(sorted(set(v for v in vals if v)))


# ---- the legacy table: one individual per legacy number ----
rows = {}
for r in csv.DictReader(open(LEGACY, encoding="utf-8"), delimiter="\t"):
    n = r["legacy_number"]
    rec = {c: set() for c in COLUMNS[2:]}
    rec["gaiad_legacy_number"].add(n)
    if r["uid"]: rec["gaiad_verse_uid"].add(r["uid"])
    for x in filter(None, (r["refn"] or "").split("|")):
        if Q_RE.fullmatch(x): rec["wiki_order_life"].add(x)
    for x in filter(None, (r["exid"] or "").split("|")):
        rec[kind(x)].add(x)
    rows[n] = rec

# ---- emma-ancestry.ged: @S@ joined on an id it shares with exactly one row ----
index = collections.defaultdict(set)
for n, rec in rows.items():
    for col in ("wiki_order_life", "familysearch", "geni", "wikidata"):
        for v in rec[col]:
            index[(col, v)].add(n)
TYPE = {"familysearch.org": "familysearch", "geni.com": "geni", "wikidata.org": "wikidata"}
indi, cur, pending = {}, None, None
for line in open(ANCESTRY, encoding="utf-8-sig", errors="replace"):
    line = line.rstrip("\n")
    m = re.match(r"0 @(S\d+)@ INDI", line)
    if m:
        cur = m.group(1); indi[cur] = set(); continue
    if line.startswith("0 "):
        cur = None; continue
    if not cur: continue
    if line.startswith("1 REFN ") and Q_RE.fullmatch(line[7:].strip()):
        indi[cur].add(("wiki_order_life", line[7:].strip()))
    elif line.startswith("1 EXID "):
        pending = line[7:].strip()
    elif line.startswith("2 TYPE ") and pending:
        col = next((c for k, c in TYPE.items() if k in line), None)
        if col: indi[cur].add((col, pending))
        pending = None
report = collections.Counter()
for s, keys in indi.items():
    hits = set().union(*(index.get(k, set()) for k in keys)) if keys else set()
    if len(hits) == 1:
        rows[next(iter(hits))]["emma_ancestry"].add("@" + s + "@"); report["@S@ joined"] += 1
    elif hits:
        report["@S@ on more than one row (left out)"] += 1
    else:
        report["@S@ sharing no id with any row (left out)"] += 1

# ---- ids that sit on more than one row: listed, never merged here ----
for (col, v), ns in index.items():
    if len(ns) > 1: report[f"{col} id on more than one row"] += 1

# ---- UUIDs: kept from the existing file, new ones made once ----
old = {}
if OUT.exists():
    for r in csv.DictReader(open(OUT, encoding="utf-8"), delimiter="\t"):
        for n in r["gaiad_legacy_number"].split("|"):
            old[n] = r["uuid"]
uid = {n: old.get(n) or str(uuid.uuid4()) for n in rows}
report["new UUIDs"] = sum(1 for n in rows if n not in old)

redirect = {}
for r in csv.DictReader(open(MERGES, encoding="utf-8"), delimiter="\t"):
    if r["action"] == "into" and r["legacy_number"] in uid and r["target"] in uid:
        redirect[r["legacy_number"]] = uid[r["target"]]
report["redirects"] = len(redirect)

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(COLUMNS)
    for n in sorted(rows, key=int):
        rec = rows[n]
        w.writerow([uid[n], redirect.get(n, SENTINEL)] + [join(rec[c]) for c in COLUMNS[2:]])
print(f"{len(rows)} individuals -> {OUT.relative_to(ROOT)}")
for k, v in sorted(report.items()): print(f"  {k}: {v}")
