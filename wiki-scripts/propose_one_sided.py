"""Queue item 16: classify the BOTH-REAL one-sided edges against Wikidata, per edge.

Reads edge_symmetry_classified.tsv (rebuild it first with edge_symmetry.py) and persons.tsv. For
each BOTH-REAL edge whose two endpoints both carry a Wikidata id, fetches the child's father (P22)
and mother (P25) and the parent's children (P40), and gives a verdict:

  CONFIRMED     Wikidata records this parent-child pair (either direction) -> add the missing side;
                graph-neutral, since extract_genealogy.py already builds the edge from either side
  CONTRADICTED  Wikidata gives the child a different parent in the same role (father for a male
                parent, mother for a female one) and does not list the child under this parent ->
                the present side may be false; needs a look, nothing automatic
  SILENT        both have Wikidata ids but Wikidata records neither the pair nor a rival
  NO_WD         one or both endpoints have no Wikidata id

Proposes only. Writes wikibase/analysis/one_sided_proposed.tsv; Wikidata answers cached in
wikibase/analysis/wd_family_cache.json. stdlib only, explicit User-Agent.
"""

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AN = ROOT / "wikibase" / "analysis"
OUT, CACHE = AN / "one_sided_proposed.tsv", AN / "wd_family_cache.json"
UA = "order.life-genealogy/1.0 (https://order.life; one-sided edge check)"
MALE, FEMALE = "Q153718", "Q153719"


def fetch(qids):
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "wbgetentities", "ids": "|".join(qids), "props": "claims", "format": "json"})
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return json.load(urllib.request.urlopen(req, timeout=60)).get("entities", {})
        except Exception as e:
            print("  retry", attempt + 1, e); time.sleep(5 * (attempt + 1))
    raise RuntimeError("Wikidata fetch failed")


def family(entity):
    if not entity or "missing" in entity or "claims" not in entity: return None
    get = lambda p: [c["mainsnak"]["datavalue"]["value"]["id"] for c in entity["claims"].get(p, [])
                     if c.get("mainsnak", {}).get("snaktype") == "value" and c.get("rank") != "deprecated"]
    return {"P22": get("P22"), "P25": get("P25"), "P40": get("P40")}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    persons = {}
    with open(AN / "persons.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            persons[r["qid"]] = r
    with open(AN / "edge_symmetry_classified.tsv", encoding="utf-8", newline="") as f:
        edges = [r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if r["verdict"] == "BOTH-REAL"]
    wd = lambda q: (persons.get(q, {}).get("wikidata_qid") or "").strip()
    print(f"{len(edges)} BOTH-REAL edges")

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    need = sorted({w for e in edges for w in (wd(e["parent"]), wd(e["child"]))
                   if w.startswith("Q") and wd(e["parent"]) and wd(e["child"]) and w not in cache})
    print(f"{len(need)} Wikidata ids to fetch ({len(cache)} cached)")
    for i in range(0, len(need), 50):
        batch = need[i:i + 50]
        ents = fetch(batch)
        for q in batch: cache[q] = family(ents.get(q))
        time.sleep(0.5)
    CACHE.write_text(json.dumps(cache), encoding="utf-8")

    counts = {}
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["parent", "parent_label", "child", "child_label", "side", "parent_wd", "child_wd",
                    "role", "wikidata_says", "verdict"])
        for e in edges:
            p, c = e["parent"], e["child"]
            pw, cw = wd(p), wd(c)
            sex = persons.get(p, {}).get("sex")
            role = "P22" if sex == MALE else "P25" if sex == FEMALE else ""
            says, v = "", "NO_WD"
            if pw and cw:
                fc, fp = cache.get(cw), cache.get(pw)
                if fc is None or fp is None: v = "SILENT"
                elif pw in fc["P22"] + fc["P25"] or cw in fp["P40"]:
                    v, says = "CONFIRMED", "pair recorded"
                elif role and fc[role]:
                    v, says = "CONTRADICTED", f"child's {'father' if role == 'P22' else 'mother'}: {'|'.join(fc[role])}"
                else: v = "SILENT"
            counts[v] = counts.get(v, 0) + 1
            w.writerow([p, persons.get(p, {}).get("label", ""), c, persons.get(c, {}).get("label", ""),
                        e["side"], pw, cw, role, says, v])
    for k in ("CONFIRMED", "CONTRADICTED", "SILENT", "NO_WD"):
        print(f"{k:12s} {counts.get(k, 0)}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
