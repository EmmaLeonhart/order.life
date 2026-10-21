"""
Write wikibase/analysis/person_names.tsv: every label and alias, in every language, of every person in
wikibase/analysis/persons.tsv, one (qid, kind, lang, name) row each. resolve_characters.py reads it for its
alias method; reading the 164,580 item files directly takes about 25 minutes, so it is cached here.
Rerun when wikibase/items changes.

    python Gaiad/scripts/build_person_names.py

Stdlib only.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ANA = ROOT / "wikibase" / "analysis"
ITEMS = ROOT / "wikibase" / "items"
OUT = ANA / "person_names.tsv"


def main():
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        people = sorted({r["qid"] for r in csv.DictReader(fh, delimiter="\t")}, key=lambda q: int(q[1:]))
    rows = []
    for q in people:
        f = ITEMS / f"{q}.json"
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        seen = set()
        for kind, groups in (("label", {k: [v] for k, v in (d.get("labels") or {}).items()}),
                             ("alias", d.get("aliases") or {})):
            for lang, vs in groups.items():
                for v in vs:
                    name = " ".join(str(v.get("value", "")).split())
                    if name and (kind, lang, name) not in seen:
                        seen.add((kind, lang, name))
                        rows.append((q, kind, lang, name))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["qid", "kind", "lang", "name"])
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows):,} names of {len(people):,} persons")


if __name__ == "__main__":
    main()
