"""Queue item 17c: find records whose Wikidata id belongs to someone else (import collisions).

The 2026-04-15 Wikibase fill wrote unrelated people's labels and ids over some records while their
family claims stayed right (Q130001, Mnemosyne, Urania and five Muses, found 2026-10-10). Such a
record's Wikidata birth year is impossible against its family. This fetches P569 for every Wikidata
id in persons.tsv (cached in wikibase/analysis/wd_birth_cache.json) and, for each record with a
Wikidata birth year and at least two dated neighbours (parents and children, by their own Wikidata
birth years), counts the impossible edges: a parent born after the child, or more than 120 years
before. A record impossible against most of its family is listed; one bad edge is more likely a
false edge than a collision, and is listed separately.

Read-only. Writes wikibase/analysis/collision_candidates.tsv. stdlib only, explicit User-Agent.
"""

import collections
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AN = ROOT / "wikibase" / "analysis"
CACHE, OUT = AN / "wd_birth_cache.json", AN / "collision_candidates.tsv"
UA = "order.life-genealogy/1.0 (https://order.life; import-collision check)"


def fetch(qids):
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "wbgetentities", "ids": "|".join(qids), "props": "claims|labels", "languages": "en",
         "format": "json"})
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return json.load(urllib.request.urlopen(req, timeout=90)).get("entities", {})
        except Exception as e:
            print("  retry", attempt + 1, e); time.sleep(5 * (attempt + 1))
    raise RuntimeError("Wikidata fetch failed")


def birth(entity):
    if not entity or "missing" in entity: return None
    label = entity.get("labels", {}).get("en", {}).get("value", "")
    for c in entity.get("claims", {}).get("P569", []):
        if c.get("mainsnak", {}).get("snaktype") == "value" and c.get("rank") != "deprecated":
            t = c["mainsnak"]["datavalue"]["value"]["time"]
            try: return [int(t[0] + t[1:].split("-")[0]), label]
            except ValueError: pass
    return [None, label]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    persons = {}
    with open(AN / "persons.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            persons[r["qid"]] = r
    par, kid = collections.defaultdict(set), collections.defaultdict(set)
    with open(AN / "edges.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            par[r["child"]].add(r["parent"]); kid[r["parent"]].add(r["child"])
    wd = {q: r["wikidata_qid"].strip() for q, r in persons.items() if r["wikidata_qid"].strip().startswith("Q")}

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    need = sorted({w for w in wd.values() if w not in cache})
    print(f"{len(wd)} records with a Wikidata id; {len(need)} to fetch ({len(cache)} cached)")
    for i in range(0, len(need), 50):
        batch = need[i:i + 50]
        ents = fetch(batch)
        for q in batch: cache[q] = birth(ents.get(q))
        if (i // 50) % 40 == 0:
            CACHE.write_text(json.dumps(cache), encoding="utf-8"); print(f"  {i + len(batch)}/{len(need)}")
        time.sleep(0.3)
    CACHE.write_text(json.dumps(cache), encoding="utf-8")

    year = lambda q: (cache.get(wd.get(q)) or [None])[0] if q in wd else None
    rows = []
    for q in wd:
        y = year(q)
        if y is None: continue
        checks = [(p, year(p), "parent") for p in par[q]] + [(c, year(c), "child") for c in kid[q]]
        checks = [(n, ny, rel) for n, ny, rel in checks if ny is not None]
        if len(checks) < 2: continue
        bad = [(n, ny, rel) for n, ny, rel in checks
               if (rel == "parent" and not (0 < y - ny <= 120)) or (rel == "child" and not (0 < ny - y <= 120))]
        if not bad: continue
        kind = "COLLISION?" if len(bad) * 2 > len(checks) else "EDGE?"
        rows.append((kind, q, persons[q]["label"], wd[q], (cache.get(wd[q]) or [None, ""])[1], y,
                     f"{len(bad)}/{len(checks)}", "; ".join(f"{rel} {n} {persons.get(n, {}).get('label', '')[:25]} ({ny})" for n, ny, rel in bad[:4])))
    rows.sort(key=lambda r: (r[0] != "COLLISION?", -int(r[6].split("/")[0])))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["kind", "qid", "label", "wikidata_qid", "wikidata_label", "wd_birth", "bad", "impossible_edges"])
        w.writerows(rows)
    c = collections.Counter(r[0] for r in rows)
    print(f"COLLISION? {c['COLLISION?']}  EDGE? {c['EDGE?']}  -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
