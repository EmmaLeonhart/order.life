"""
Write wikibase/analysis/wikidata_arms.tsv: the real coat of arms of every person in gaiad.ged with a Wikidata id, as a
Commons file, for the coats-of-arms item (queue, Emma 2026-10-20). A person's own coat-of-arms image (P94) is taken
first; failing that, the image of their coat-of-arms item (P237 -> P94, or P18). People without either are left for
the invented-arms step. Only items that are humans (P31 Q5) count: a few ids in gaiad.ged are places. Run here with
network; make_arms.py reads the TSV.

    python wiki-scripts/make_arms_table.py <gaiad.ged>
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wikibase" / "analysis" / "wikidata_arms.tsv"
UA = {"User-Agent": "order.life gaiad.ged builder (emma@topazcomputing.com)"}


def claims(ids):
    """{qid: claims} for up to 50 ids."""
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=claims&format=json&ids=" + "|".join(ids))
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
            return {q: e.get("claims", {}) for q, e in d.get("entities", {}).items()}
        except OSError:
            time.sleep(5 * (attempt + 1))
    return {}


def values(cl, prop):
    out = []
    for c in cl.get(prop, []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(v, dict) and "id" in v:
            out.append(v["id"])
        elif isinstance(v, str):
            out.append(v)
    return out


def in_batches(ids):
    got = {}
    for i in range(0, len(ids), 50):
        got.update(claims(ids[i:i + 50]))
        time.sleep(0.1)
    return got


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    qids = sorted(set(re.findall(r"^1 EXID (Q\d+)$", text, re.M)), key=lambda q: int(q[1:]))
    people = in_batches(qids)
    rows, via_item, not_human = [], {}, []
    for q in qids:
        cl = people.get(q, {})
        if "Q5" not in values(cl, "P31"):
            # gaiad.ged has some ids that are not people (Q22776 is the town of Benfeld); their arms are not a person's.
            if values(cl, "P94") or values(cl, "P237"):
                not_human.append(q)
            continue
        files = values(cl, "P94")
        if files:
            rows.append((q, files[0], "P94"))
        elif values(cl, "P237"):
            via_item[q] = values(cl, "P237")[0]
    items = in_batches(sorted(set(via_item.values())))
    for q, item in via_item.items():
        files = values(items.get(item, {}), "P94") or values(items.get(item, {}), "P18")
        if files:
            rows.append((q, files[0], f"P237 {item}"))
    rows.sort(key=lambda r: int(r[0][1:]))
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("qid\tfile\tvia\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"{len(qids)} people with a Wikidata id; {len(rows)} with arms "
          f"({sum(r[2] == 'P94' for r in rows)} by P94); {len(via_item)} with a P237 item -> {OUT}")
    print(f"left out, not a human (P31 Q5) but with arms: {' '.join(not_human)}")


if __name__ == "__main__":
    main()
