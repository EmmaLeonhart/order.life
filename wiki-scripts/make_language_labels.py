"""
Write wikibase/analysis/wikidata_language_labels.tsv: Wikidata's label in each of the site's other languages (es, hi, ar,
fr, ru, uk) for every person in gaiad.ged with a Wikidata id, for the per-language download zips. Emma, 2026-10-14: a
language directory's zip holds "English, Japanese, Chinese, and then whatever ... other language the directory is in";
language_gedcom.py adds the directory's language from this table. Run here with network; the site build reads the TSV.

    python wiki-scripts/make_language_labels.py <gaiad.ged>
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wikibase" / "analysis" / "wikidata_language_labels.tsv"
LANGS = ("es", "hi", "ar", "fr", "ru", "uk")
UA = {"User-Agent": "order.life gaiad.ged builder (emma@topazcomputing.com)"}


def get(ids):
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&format=json&languages="
           + "|".join(LANGS) + "&ids=" + "|".join(ids))
    for attempt in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except OSError:
            time.sleep(5 * (attempt + 1))
    return {}


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    qids = sorted(set(re.findall(r"^1 EXID (Q\d+)$", text, re.M)), key=lambda q: int(q[1:]))
    rows = []
    for i in range(0, len(qids), 50):
        for q, e in get(qids[i:i + 50]).get("entities", {}).items():
            for lg in LANGS:
                lb = e.get("labels", {}).get(lg, {}).get("value", "")
                if lb and "\t" not in lb:
                    rows.append((q, lg, lb))
        time.sleep(0.1)
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("qid\tlang\tlabel\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"{len(qids)} people with a Wikidata id, {len(rows)} labels -> {OUT}")


if __name__ == "__main__":
    main()
