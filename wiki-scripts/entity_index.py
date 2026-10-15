"""
Write the person index behind https://order.life/wikibase/entity/Q<n>, the URL the GEDCOM's EXIDs name.

The site has no page per person (106,786 of them), so build.py calls this to write small JSON buckets,
site/wikibase/entity/_index/<n // 1000>.json, and templates/404.html shows the record of any
/wikibase/entity/Q<n> from its bucket: label, dates, parents and children (each linked the same way),
the Gaiad character page if there is one, Wikidata and Geni. It is also what a Wikidata property for
order.life ids would point at (planning/wikidata-property-proposal.md). Stdlib only.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANA = ROOT / "wikibase" / "analysis"
GEN = ROOT / "Gaiad" / "genealogy"


def year_of(ts):
    if not ts:
        return ""
    m = re.match(r"([+-]?)0*(\d+)-(\d\d)-(\d\d)", ts.strip())
    if not m:
        return ""
    y = int(m.group(2))
    return f"{y} BCE" if m.group(1) == "-" else str(y)


def build(out_dir):
    persons = {}
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            persons[r["qid"]] = r
    parents, children = defaultdict(list), defaultdict(list)
    with open(ANA / "edges.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            parents[r["child"]].append(r["parent"])
            children[r["parent"]].append(r["child"])
    page = {}
    for f in GEN.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("qid") and d.get("name"):
            slug = re.sub(r"[^a-zA-Z0-9_-]", "", d["name"].replace(" ", "_")).lower()
            if slug:
                page.setdefault(d["qid"], slug)
    buckets = defaultdict(dict)
    for q, r in persons.items():
        if not q[1:].isdigit():
            continue
        rec = {"l": (r.get("label") or "").strip(), "b": year_of(r.get("birth")), "d": year_of(r.get("death")),
               "p": parents.get(q, [])[:4], "c": children.get(q, [])[:60]}
        if r.get("wikidata_qid"):
            rec["w"] = r["wikidata_qid"]
        if (r.get("geni_id") or "").isdigit():
            rec["g"] = r["geni_id"]
        if q in page:
            rec["s"] = page[q]
        buckets[int(q[1:]) // 1000][q] = rec
    # Names of linked people travel with each record's bucket only, so a record shows its relatives' labels.
    for b in buckets.values():
        for rec in b.values():
            rec["n"] = {x: (persons.get(x, {}).get("label") or x).strip() for x in rec["p"] + rec["c"]}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for k, b in buckets.items():
        (out_dir / f"{k}.json").write_text(json.dumps(b, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(persons), len(buckets)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else "entity_index_out"))
