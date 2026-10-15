"""
Write the Gaiad's cladoplast links to wikibase/analysis/cladoplasts.tsv for the GEDCOM exporter.

"Cladoplast is a Gaiad term" (Emma, 2026-10-12): a character who is the personification of a clade, so the
tree of life and the family tree are one tree. The wikibase records it as P59 "Cladoplast of", an
external id holding the Wikidata item of the clade. This reads every item that has P59 and looks up each
clade's English label on Wikidata (read-only, batches of 50).

    python wiki-scripts/extract_cladoplasts.py

Stdlib only.
"""
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
OUT = ROOT / "wikibase" / "analysis" / "cladoplasts.tsv"
UA = "order.life-genealogy/1.0 (https://order.life/; emma@topazcomputing.com)"


def p59_values(d):
    out = []
    for c in (d.get("claims") or {}).get("P59", []):
        v = (((c.get("mainsnak") or {}).get("datavalue") or {}).get("value"))
        if isinstance(v, str) and v.strip().startswith("Q"):
            out.append(v.strip())
    return out


def main():
    rows = []
    for f in ITEMS.glob("*.json"):
        txt = f.read_text(encoding="utf-8")
        if '"P59"' not in txt:
            continue
        try:
            d = json.loads(txt)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        e = d.get("entities")
        d = next(iter(e.values())) if isinstance(e, dict) and e else d
        for v in p59_values(d):
            rows.append([f.stem, v])
    clades = sorted({v for _, v in rows}, key=lambda x: int(x[1:]))
    labels = {}
    for i in range(0, len(clades), 50):
        q = {"action": "wbgetentities", "format": "json", "props": "labels", "languages": "en",
             "ids": "|".join(clades[i:i + 50])}
        req = urllib.request.Request("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(q),
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            for k, ent in json.load(r).get("entities", {}).items():
                labels[k] = ((ent.get("labels") or {}).get("en") or {}).get("value", "")
        time.sleep(0.3)
    rows.sort(key=lambda r: int(r[0][1:]))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["qid", "clade_wikidata", "clade_label"])
        for q, v in rows:
            w.writerow([q, v, labels.get(v, "")])
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows):,} links to {len(clades):,} clades")


if __name__ == "__main__":
    main()
