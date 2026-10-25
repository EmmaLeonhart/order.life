"""
The pharaohs' attested royal names, for monarch_names.py (planning/monarch-names.md: "Pharaohs keep their attested
Horus names; where lost, the gap is restored on the pattern of their dynasty and marked as a restoration").

For every pharaoh in wikibase/analysis/monarchs.tsv, follows the Wikidata item to its English Wikipedia article and
reads the Infobox pharaoh fields (horus, nebty, golden, prenomen, nomen, dynasty). Writes
wikibase/analysis/pharaoh_names.tsv. Network, stdlib only; rerun when monarchs.tsv changes:

    python wiki-scripts/fetch_pharaoh_names.py
"""
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ANA = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"
UA = {"User-Agent": "order.life-research/1.0 (https://order.life)"}
FIELDS = ["horus", "nebty", "golden", "prenomen", "nomen"]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def clean(v):
    """Infobox value 'Netjerkheperu<br>''Nṯrj-ḫprw''<br>''Horus, divine of form''' -> (name, translit, gloss)."""
    v = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", v, flags=re.S)
    v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", v)
    v = re.sub(r"\{\{[^{}]*\}\}", "", v)
    parts = [re.sub(r"'{2,}|<[^>]+>", "", p).strip() for p in re.split(r"<br\s*/?>", v)]
    parts = [p for p in parts if p] + ["", "", ""]
    return parts[0], parts[1], parts[2]


def infobox_fields(text):
    """(field, value) pairs of the article's Infobox pharaoh/royalty/monarch, split on top-level pipes only.
    Field names are lowercased (articles write both "Horus" and "horus")."""
    m = re.search(r"\{\{\s*Infobox (?:pharaoh|royalty|monarch)", text, re.I)
    if not m:
        return []
    i, depth, start, parts = m.start(), 0, None, []
    while i < len(text):
        two = text[i:i + 2]
        if two in ("{{", "[["):
            depth += 1
            i += 2
            continue
        if two in ("}}", "]]"):
            depth -= 1
            i += 2
            if depth == 0:
                break
            continue
        if text[i] == "|" and depth == 1:
            if start is not None:
                parts.append(text[start:i])
            start = i + 1
        i += 1
    if start is not None:
        parts.append(text[start:i - 2])
    out = []
    for p in parts:
        k, eq, v = p.partition("=")
        if eq and re.fullmatch(r"\s*[A-Za-z_]+\s*", k):
            # {{center|X}}, {{align|center|X}} and similar wrappers: keep the last argument.
            v = re.sub(r"\{\{\s*(?:center|align|nowrap)\s*\|(?:[^{}|]*\|)*([^{}]*)\}\}", r"\1", v, flags=re.I)
            out.append((k.strip().lower(), v.strip()))
    return out


def main():
    rows = [r for r in csv.DictReader(open(ANA / "monarchs.tsv", encoding="utf-8"), delimiter="\t")
            if "pharaoh" in r["positions"].lower()]
    # monarchs.tsv's qid is the order.life wikibase id; the Wikidata item is wikidata_qid.
    wd = {r["qid"]: r["wikidata_qid"] for r in rows if r.get("wikidata_qid")}
    qids = sorted(set(wd.values()))
    titles = {}
    for i in range(0, len(qids), 50):
        d = get("https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks&sitefilter=enwiki"
                "&format=json&ids=" + "|".join(qids[i:i + 50]))
        for q, e in d.get("entities", {}).items():
            t = e.get("sitelinks", {}).get("enwiki", {}).get("title")
            if t:
                titles[q] = t
    titles = {q: titles[w] for q, w in wd.items() if w in titles}
    out = []
    for r in rows:
        q = r["qid"]
        rec = {"qid": q, "label": r["label"], "article": titles.get(q, ""), "dynasty": ""}
        for f in FIELDS:
            rec[f] = rec[f + "_translit"] = rec[f + "_gloss"] = ""
        if q in titles:
            d = get("https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext&format=json&formatversion=2"
                    "&redirects=1&page=" + urllib.parse.quote(titles[q]))
            text = d.get("parse", {}).get("wikitext", "")
            for k, v in infobox_fields(text):
                if True:
                    if k in FIELDS and not rec[k]:
                        rec[k], rec[k + "_translit"], rec[k + "_gloss"] = clean(v)
                    elif k == "dynasty":
                        rec["dynasty"] = clean(v)[0]
            time.sleep(0.5)
        out.append(rec)
    cols = ["qid", "label", "article", "dynasty"] + [c for f in FIELDS for c in (f, f + "_translit", f + "_gloss")]
    with open(ANA / "pharaoh_names.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t")
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} pharaohs, {len(titles)} with an English article, "
          f"{sum(1 for o in out if o['horus'])} with an attested Horus name")


if __name__ == "__main__":
    main()
