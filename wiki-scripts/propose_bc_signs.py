"""Queue item 0b: propose sign fixes for BC dates stored as positive years, where the record has only
ONE date (so the `death < birth` detector in cycle_chronology.py cannot see it).

For every record in wikibase/analysis/persons.tsv with exactly one of birth/death, that date not
negative, and a Wikidata id, fetch the same field (P569 birth / P570 death) from Wikidata and compare
years. Proposes only; edits nothing in wikibase/items/.

Usage: python wiki-scripts/propose_bc_signs.py [persons.tsv]   (default wikibase/analysis/persons.tsv)
Writes wikibase/analysis/bc_sign_proposed.tsv (one row per record) and prints a summary.
Wikidata answers are cached in wikibase/analysis/wd_dates_cache.json, so a rerun fetches only what
is missing. stdlib only (urllib, explicit User-Agent: without one Wikidata returns 403).

Verdicts:
  FLIP        Wikidata has the field as BC and its year matches the dump's within 1 -> make it negative
  AD          Wikidata has it as AD and the year matches within 1 -> the dump is right
  MISMATCH    Wikidata has the field with a different year (sign shown) -> needs a look
  NO_WD_DATE  Wikidata lacks the field -> another source needed
  WD_MISSING  the Wikidata id does not resolve (deleted or redirected away)
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
PERSONS, OUT, CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else AN / "persons.tsv", AN / "bc_sign_proposed.tsv", AN / "wd_dates_cache.json"
UA = "order.life-genealogy/1.0 (https://order.life; BC sign check)"
FIELD = {"birth": "P569", "death": "P570"}


def year(s):
    """'+0141-00-00T...' -> (sign, 141); None if not a date."""
    s = (s or "").strip()
    if not s or s == "None": return None
    sign = "-" if s.startswith("-") else "+"
    try: return sign, int(s.lstrip("+-").split("-")[0])
    except ValueError: return None


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


def dates(entity):
    """{'P569': ['-0141-...', ...], 'P570': [...]} from a wbgetentities entity, or None if missing."""
    if not entity or "missing" in entity or "claims" not in entity: return None
    out = {}
    for p in ("P569", "P570"):
        out[p] = [c["mainsnak"]["datavalue"]["value"]["time"] for c in entity["claims"].get(p, [])
                  if c.get("mainsnak", {}).get("snaktype") == "value" and c.get("rank") != "deprecated"]
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    with open(PERSONS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            b, d = year(r["birth"]), year(r["death"])
            if (b is None) == (d is None): continue
            field = "birth" if b else "death"
            sign, y = b or d
            wd = (r.get("wikidata_qid") or "").split("|")[0].split(",")[0].strip()
            if sign == "-" or not wd.startswith("Q"): continue
            rows.append((r["qid"], r["label"], field, r[field], y, wd))
    print(f"{len(rows)} one-date, non-negative records with a Wikidata id")

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    need = sorted({wd for *_, wd in rows if wd not in cache}, key=lambda q: int(q[1:]) if q[1:].isdigit() else 0)
    print(f"{len(need)} Wikidata ids to fetch ({len(cache)} cached)")
    for i in range(0, len(need), 50):
        batch = need[i:i + 50]
        ents = fetch(batch)
        for q in batch: cache[q] = dates(ents.get(q))
        if (i // 50) % 20 == 0:
            CACHE.write_text(json.dumps(cache), encoding="utf-8"); print(f"  {i + len(batch)}/{len(need)}")
        time.sleep(0.5)
    CACHE.write_text(json.dumps(cache), encoding="utf-8")

    counts = {}
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["qid", "label", "field", "dump_value", "wikidata_qid", "wikidata_values", "verdict"])
        for qid, label, field, raw, y, wd in rows:
            got = cache.get(wd)
            if got is None: v, vals = "WD_MISSING", []
            else:
                vals = got[FIELD[field]]
                ys = [year(t) for t in vals if year(t)]
                if not ys: v = "NO_WD_DATE"
                elif any(s == "-" and abs(n - y) <= 1 for s, n in ys): v = "FLIP"
                elif any(s == "+" and abs(n - y) <= 1 for s, n in ys): v = "AD"
                else: v = "MISMATCH"
            counts[v] = counts.get(v, 0) + 1
            w.writerow([qid, label, field, raw, wd, "|".join(vals), v])
    for k in ("FLIP", "AD", "MISMATCH", "NO_WD_DATE", "WD_MISSING"):
        print(f"{k:11s} {counts.get(k, 0)}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
