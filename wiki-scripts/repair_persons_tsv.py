"""persons.tsv is truncated. Restore the missing rows without re-walking the dump.

    python wiki-scripts/repair_persons_tsv.py            # report what is missing
    python wiki-scripts/repair_persons_tsv.py --write    # rebuild the file

THE DEFECT

The committed `persons.tsv` holds **63,976 rows**. `edges.tsv` -- committed alongside it --
references **101,990 distinct qids**, of which **40,740 are absent from persons.tsv**.
Spot-checked, 396 of the first 400 of those have a perfectly good item file on disk with a
real English label ('Arnold I of Chiny', 'Otto II, Count of Chiny'). They are not phantom
qids; they are missing rows.

It is the silent truncation described in commit 91caa7f: `extract_genealogy.py` dies
partway with no stdout and no traceback, and `edges.tsv` is written *later in the same run*
-- so a committed pair can consist of a complete edges.tsv and a short persons.tsv, which
is exactly what is in the repo. That commit measured a correct persons.tsv at 7.53 MB; the
committed file is **4.88 MB**.

WHAT IT BROKE

Everything that treats persons.tsv as the roster. Above all `export_gedcom.py`, which
filters edges to `if p in persons and c in persons` -- so the GEDCOM published at
/gedcom/ has been shipping **63,976 individuals when the genealogy holds well over
100,000**, silently dropping every person and every edge that the truncation removed.
`date_precision.tsv` is built from persons.tsv too and is short by the same set.

THE REPAIR, and why it is not a full regeneration

Re-running `extract_genealogy.py` means walking all 164k item files, which is the job that
overheats Emma's machine and the job that crashes. This reads **only the qids that are
missing** -- roughly 40k targeted reads rather than 164k -- rebuilds the row for each in
the extractor's own format, and rewrites the file in numeric qid order.

It asserts before renaming: the row count must rise, every previously-present qid must
survive unchanged, and every qid in edges.tsv must end up covered. A partial run cannot
masquerade as a complete one.

WHAT IT STILL DOES NOT FIX

Records that are isolated -- no parents and no children -- never appear in edges.tsv, so
this cannot find them. `items_index.txt` (164,544) minus `redirects.tsv` (57,440) suggests
about 107,000 real qids, so a few thousand may still be missing after this. Closing that
gap needs a real regeneration with the temp-file-and-rename guard that queue.md item 0a
already specifies. This makes the file correct for everything edge-connected, which is
everything a family tree is made of.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANA = ROOT / "wikibase" / "analysis"
ITEMS = ROOT / "wikibase" / "items"
OUT = ANA / "persons.tsv"

HEADER = ["qid", "label", "sex", "birth", "death", "gedcom", "wikidata_qid", "geni_id"]

P_SEX, P_BIRTH, P_DEATH = "P55", "P56", "P57"
P_GEDCOM, P_WIKIDATA, P_GENI = "P5", "P61", "P62"


def tsv_escape(s):
    if not s:
        return ""
    return s.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def first(gen):
    for v in gen:
        if v:
            return v
    return ""


def entity_id(claim):
    try:
        m = claim["mainsnak"]
        if m.get("snaktype") != "value":
            return None
        return m["datavalue"]["value"]["id"]
    except (KeyError, TypeError):
        return None


def get_string(claim):
    try:
        m = claim["mainsnak"]
        if m.get("snaktype") != "value":
            return None
        v = m["datavalue"]["value"]
        return v if isinstance(v, str) else v.get("text")
    except (KeyError, TypeError):
        return None


def get_time(claim):
    try:
        m = claim["mainsnak"]
        if m.get("snaktype") != "value":
            return None
        return m["datavalue"]["value"]["time"]
    except (KeyError, TypeError):
        return None


def row_for(qid):
    """Rebuild one persons.tsv row from the item file, in the extractor's format."""
    path = ITEMS / f"{qid}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None

    labels = data.get("labels") or {}
    label = ""
    for code in ("en", "mul", "ja"):
        v = labels.get(code)
        if v and v.get("value"):
            label = v["value"]
            break
    if not label:
        for v in labels.values():
            if isinstance(v, dict) and v.get("value"):
                label = v["value"]
                break

    claims = data.get("claims") or {}
    return [
        qid,
        tsv_escape(label),
        first(entity_id(c) for c in claims.get(P_SEX, [])) or "",
        tsv_escape(first(get_time(c) for c in claims.get(P_BIRTH, []))),
        tsv_escape(first(get_time(c) for c in claims.get(P_DEATH, []))),
        tsv_escape(first(get_string(c) for c in claims.get(P_GEDCOM, []))),
        tsv_escape(first(get_string(c) for c in claims.get(P_WIKIDATA, []))),
        tsv_escape(first(get_string(c) for c in claims.get(P_GENI, []))),
    ]


def main():
    write = "--write" in sys.argv

    existing = {}
    with open(OUT, encoding="utf-8", newline="") as f:
        for row in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if row and row[0] != "qid":
                existing[row[0]] = row
    print(f"persons.tsv: {len(existing):,} rows")

    edge_qids = set()
    with open(ANA / "edges.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            edge_qids.add(r["parent"])
            edge_qids.add(r["child"])
    print(f"edges.tsv references {len(edge_qids):,} distinct qids")

    # spouses.tsv names people who may have neither parent nor child and so appear in no
    # edge at all -- 1,325 of them after the first pass. A marriage is a relationship the
    # GEDCOM exports, so they belong in the roster too.
    with open(ANA / "spouses.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            edge_qids.add(r["a"])
            edge_qids.add(r["b"])
    print(f"with spouses.tsv: {len(edge_qids):,} distinct qids")

    missing = sorted(edge_qids - set(existing),
                     key=lambda q: int(q[1:]) if q[1:].isdigit() else 0)
    print(f"MISSING FROM persons.tsv: {len(missing):,}\n")
    if not missing:
        print("Nothing to repair.")
        return 0

    if not write:
        print("First 10 missing, read from disk to show they are real records:")
        for q in missing[:10]:
            r = row_for(q)
            print(f"  {q:10s} {r[1][:52] if r else '(NO FILE)'}")
        print("\nDry run. Re-run with --write to rebuild persons.tsv.")
        return 0

    recovered, no_file = [], []
    for i, qid in enumerate(missing, 1):
        r = row_for(qid)
        if r is None:
            no_file.append(qid)
        else:
            recovered.append(r)
        if i % 5000 == 0:
            print(f"  {i:,}/{len(missing):,}", flush=True)

    print(f"\nrecovered {len(recovered):,} rows; {len(no_file):,} qids have no item file")

    # A partial run must not masquerade as a complete one. But "missing and unreadable"
    # is a real state -- 4 qids are referenced by edges.tsv and have no item file at all
    # -- so the test is whether anything was silently skipped, not a blunt ratio.
    unaccounted = len(missing) - len(recovered) - len(no_file)
    if unaccounted:
        sys.exit(f"ABORT: {unaccounted} qid(s) neither recovered nor accounted for")
    if no_file and not recovered:
        print(f"Nothing recoverable: all {len(no_file)} missing qids lack an item file.")
        for q in no_file:
            print(f"  {q}")
        return 0

    merged = dict(existing)
    for r in recovered:
        merged[r[0]] = r
    ordered = sorted(merged.values(),
                     key=lambda r: int(r[0][1:]) if r[0][1:].isdigit() else 0)

    # Guards: nothing lost, everything gained, coverage achieved.
    if len(ordered) != len(existing) + len(recovered):
        sys.exit(f"ABORT: row arithmetic wrong -- {len(ordered)} != "
                 f"{len(existing)} + {len(recovered)}")
    for qid, row in existing.items():
        if merged[qid] != row:
            sys.exit(f"ABORT: {qid} would change; this repair must only ADD rows")
    still = edge_qids - set(merged)
    if still - set(no_file):
        sys.exit(f"ABORT: {len(still - set(no_file))} edge qids still uncovered")

    # Written by hand rather than with csv.writer: QUOTE_NONE still demands a real
    # quotechar, and every field has already been through tsv_escape(), so a plain tab
    # join is both correct and byte-for-byte what extract_genealogy.py emits.
    tmp = OUT.with_suffix(".tsv.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for row in ordered:
            f.write("\t".join(row) + "\n")
    tmp.replace(OUT)

    print(f"\nWrote {OUT}: {len(ordered):,} rows "
          f"(+{len(recovered):,}), {OUT.stat().st_size:,} bytes")
    print(f"Every previously-present row is byte-identical; only additions were made.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
