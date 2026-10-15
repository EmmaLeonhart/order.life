"""
Write every person's real labels in chosen languages from the wikibase items to a TSV the GEDCOM exporter reads.

The name schema (planning/name-schema.md): "Chinese, Japanese, Korean, English are the primary ones", and each
language directory's files add that directory's language (Emma, 2026-10-14). The items carry labels in 452
languages, about 12 per person; all of them in one GEDCOM would add some 50 MB, so the exporter takes the
primary languages, and per-language files can take their own.

    python wiki-scripts/extract_labels.py [lang ...]     # default: zh ja ko
                                                           # writes wikibase/analysis/labels.tsv

Only labels the items actually carry; nothing is generated or transliterated. Stdlib only.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
ANA = ROOT / "wikibase" / "analysis"


def main(langs):
    persons = set()
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            persons.add(r["qid"])
    rows = []
    for q in sorted(persons, key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        f = ITEMS / f"{q}.json"
        if not f.exists():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        e = d.get("entities")
        d = next(iter(e.values())) if isinstance(e, dict) and e else d
        labs = d.get("labels") or {}
        for lang in langs:
            v = labs.get(lang)
            if v:
                s = (v["value"] if isinstance(v, dict) else str(v)).strip()
                if s:
                    rows.append([q, lang, s])
    out = ANA / "labels.tsv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["qid", "lang", "label"])
        w.writerows(rows)
    print(f"wrote {out.relative_to(ROOT)}: {len(rows):,} labels in {', '.join(langs)}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["zh", "ja", "ko"])
