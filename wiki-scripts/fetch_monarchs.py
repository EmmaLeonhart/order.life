"""
List the monarchs in the order.life genealogy, for the name schema's temple and Horus names.

Emma, 2026-10-13: "Every monarch ever ... needs to have a temple name and a Horus name." This finds
which people are monarchs by asking Wikidata, for every record with a wikidata_qid, whether they held
a position (P39) that is a kind of monarch (Q116), and writes wikibase/analysis/monarchs.tsv with the
positions found. Read-only against Wikidata; batches of 300 with a pause, and a User-Agent, as WDQS asks.

    python wiki-scripts/fetch_monarchs.py            # all records
    python wiki-scripts/fetch_monarchs.py --limit 300

Stdlib only.
"""
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "wikibase" / "analysis"
OUT = ANALYSIS / "monarchs.tsv"
WDQS = "https://query.wikidata.org/sparql"
UA = "order.life-genealogy/1.0 (https://order.life/; emma@topazcomputing.com)"
BATCH = 300

QUERY = """
SELECT ?item ?pos ?posLabel WHERE {
  VALUES ?item { %s }
  ?item wdt:P39 ?pos .
  ?pos (wdt:P31|wdt:P279)/wdt:P279* wd:Q116 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


def run(qids):
    q = QUERY % " ".join("wd:" + x for x in qids)
    req = urllib.request.Request(WDQS, data=urllib.parse.urlencode({"query": q}).encode(),
                                 headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:  # rate limit or timeout: back off and retry
            wait = 10 * (attempt + 1)
            print(f"  retry in {wait}s after {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("WDQS failed four times on one batch")


def main(limit=None):
    rows = []
    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["wikidata_qid"].startswith("Q"):
                rows.append((r["qid"], r["wikidata_qid"], r["label"]))
    if limit:
        rows = rows[:limit]
    by_wd = {}
    for q, wd, label in rows:
        by_wd.setdefault(wd, []).append((q, label))
    wds = sorted(by_wd)
    found = {}
    for i in range(0, len(wds), BATCH):
        for b in run(wds[i:i + BATCH]):
            wd = b["item"]["value"].rsplit("/", 1)[1]
            found.setdefault(wd, set()).add(b["posLabel"]["value"])
        print(f"  {min(i + BATCH, len(wds)):,} / {len(wds):,} checked, {len(found):,} monarchs", file=sys.stderr)
        time.sleep(1)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["qid", "wikidata_qid", "label", "positions"])
        # A consort is a monarch's spouse, not a monarch, though Wikidata's class tree puts
        # "queen consort" under monarch: drop anyone whose only positions are consort ones.
        found = {wd: ps for wd, ps in found.items() if not all("consort" in p.lower() for p in ps)}
        for wd in sorted(found, key=lambda x: int(x[1:])):
            for q, label in by_wd[wd]:
                w.writerow([q, wd, label, "; ".join(sorted(found[wd]))])
    print(f"wrote {OUT.relative_to(ROOT)}: {len(found):,} monarchs among {len(wds):,} Wikidata ids")


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    main(lim)
