#!/usr/bin/env python
"""Split every record carrying a wikidata_qid into three groups. Nothing else.

    python wiki-scripts/audit_wikidata_ids.py     # fills the label cache
    python wiki-scripts/split_wikidata_links.py

Writes three files to wikibase/analysis/:

    qa_links_match.tsv      the item exists and its name matches
    qa_links_nomatch.tsv    the item exists and its name does NOT match
    qa_links_dead.tsv       the item does not exist on Wikidata

A name counts as matching if the local label matches any label or alias on the item,
in any language. A non-matching name does not prove the id is wrong — transliteration
and exonyms break string comparison — so that file is a worklist, not a verdict.
"""

import csv
import io
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "wikibase" / "analysis"
CACHE = ANALYSIS / ".wikidata_cache_full.json"
BAR = 0.75

csv.field_size_limit(10_000_000)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s or "")
                if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def score(local, names):
    ln = norm(local)
    if not ln or not names:
        return 0.0
    best = 0.0
    for n in names:
        nn = norm(n)
        if not nn:
            continue
        if ln == nn:
            return 1.0
        if len(ln) > 3 and (ln in nn or nn in ln):
            best = max(best, 0.9)
        best = max(best, SequenceMatcher(None, ln, nn).ratio())
    return best


def main():
    if not CACHE.exists():
        sys.exit("no cache — run wiki-scripts/audit_wikidata_ids.py first")
    cache = json.loads(CACHE.read_text(encoding="utf-8"))

    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as fh:
        persons = list(csv.DictReader(fh, delimiter="\t"))

    match, nomatch, dead = [], [], []
    for p in persons:
        w = (p.get("wikidata_qid") or "").strip()
        if not re.fullmatch(r"Q\d+", w):
            continue
        label = " ".join((p.get("label") or "").split())
        e = cache.get(w)
        if e is None:
            dead.append([p["qid"], label, w, "", ""])
            continue
        s = score(label, e["names"])
        wd_name = e["names"][0] if e["names"] else ""
        row = [p["qid"], label, w, wd_name, "%.2f" % s]
        (match if s >= BAR else nomatch).append(row)

    for name, data in (("qa_links_match.tsv", match),
                       ("qa_links_nomatch.tsv", nomatch),
                       ("qa_links_dead.tsv", dead)):
        with open(ANALYSIS / name, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(["qid", "label", "wikidata_qid", "wikidata_name", "name_score"])
            w.writerows(sorted(data, key=lambda r: float(r[4] or 0)))

    total = len(match) + len(nomatch) + len(dead)
    print("records with a wikidata_qid: %d\n" % total)
    print("  exists, name matches      %6d  (%5.2f%%)  qa_links_match.tsv"
          % (len(match), 100.0 * len(match) / total))
    print("  exists, name does NOT     %6d  (%5.2f%%)  qa_links_nomatch.tsv"
          % (len(nomatch), 100.0 * len(nomatch) / total))
    print("  does not exist            %6d  (%5.2f%%)  qa_links_dead.tsv"
          % (len(dead), 100.0 * len(dead) / total))


if __name__ == "__main__":
    main()
