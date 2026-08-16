"""How many genealogy claims in the dump still name a qid that redirects somewhere else?

    python wiki-scripts/vacated_qid_audit.py             # scan, report, write the TSV
    python wiki-scripts/vacated_qid_audit.py --quiet     # TSV only

Writes wikibase/analysis/qa_vacated_refs.tsv. Read-only over wikibase/items/. Slow -- it
parses every item file, so give it twenty minutes and run it in the background.

WHY

merge_cluster.py's standing rule is that after a merge NO file may still claim the loser's
qid, because vacating a qid some file still claims lets that file win it and inject its
claims. That is what produced the phantom Cato 2-cycle out of a graph that never contained
the edge.

The rule is enforced at merge time. Nothing enforces it afterwards, and claims naming a
vacated qid can arrive later by other routes -- a hand edit, a script that writes a raw
qid, a bridge tool that read the dump before a merge landed. The Q72693 residue behind
queue.md item 1c is exactly that: five files listing Q72434's father twice, once as Q72615
and once as the qid merged into it on 2026-07-31.

These references are usually harmless to the GRAPH -- extract_genealogy.py resolves both
spellings to the same edge -- which is precisely why they accumulate unseen. What they cost
is elsewhere:

  * a record reads as having two parents in one role when it has one, written twice, so it
    shows up in qa_same_role_parents.tsv and children_over_2_parents as a defect it does
    not have;
  * any script matching raw qids can be fooled in either direction -- silently dropping
    nothing (apply_lepidus_cut.py, eight days) or silently adding a duplicate
    (add_bridge_edges.py, fixed 2026-08-15);
  * and the merge rule's real hazard stays live: if the vacated qid is ever re-issued, the
    stale claim starts pointing at a different person.

This measures the size of the problem. It repairs nothing.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
ANALYSIS = ROOT / "wikibase" / "analysis"
OUT = ANALYSIS / "qa_vacated_refs.tsv"

# father, mother, child, spouse -- the claims that build edges.tsv and spouses.tsv
ROLES = {"P47": "father", "P48": "mother", "P20": "child", "P42": "spouse"}


def redirect_map():
    out = {}
    with open(ANALYSIS / "redirects.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["from_qid"]] = r["to_qid"]
    return out


def resolve(qid, red):
    seen = set()
    while qid in red and qid not in seen:
        seen.add(qid)
        qid = red[qid]
    return qid


def main():
    quiet = "--quiet" in sys.argv
    red = redirect_map()
    print(f"redirect map: {len(red):,} vacated qid(s)")

    files = sorted(ITEMS.glob("*.json"))
    print(f"scanning {len(files):,} item files...")

    rows = []
    dup_rows = []
    malformed = []
    scanned = 0
    for path in files:
        scanned += 1
        if not quiet and scanned % 20000 == 0:
            print(f"  {scanned:,}/{len(files):,}  refs={len(rows):,}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            malformed.append(path.name)
            continue
        # Some item files hold a bare `null` rather than an object. Found 2026-08-15 by
        # this scan crashing on one; they are not errors to fix here, but they must not
        # take the scan down, and they are worth counting.
        if not isinstance(data, dict):
            malformed.append(path.name)
            continue
        owner = data.get("id") or path.stem
        claims = data.get("claims") or {}
        for pid, role in ROLES.items():
            targets = []
            for c in claims.get(pid, []):
                v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                if isinstance(v, dict) and v.get("id"):
                    targets.append(v["id"])
            if not targets:
                continue
            for raw in targets:
                canon = resolve(raw, red)
                if canon != raw:
                    rows.append((path.name, owner, pid, role, raw, canon))
            # The costly case: the same person named twice in one role, once under a
            # vacated spelling. This is what reads as a two-parent defect that is not one.
            seen = {}
            for raw in targets:
                seen.setdefault(resolve(raw, red), []).append(raw)
            for canon, spellings in seen.items():
                if len(spellings) > 1:
                    dup_rows.append((path.name, owner, pid, role, canon,
                                     ",".join(spellings)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("file\towner_qid\tpid\trole\traw_target\tresolves_to\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    print(f"\nfiles scanned:              {scanned:,}")
    if malformed:
        print(f"unparseable / not an object: {len(malformed):,}"
              f"  e.g. {', '.join(malformed[:5])}")
    print(f"claims naming a vacated qid: {len(rows):,}")
    print(f"  ...distinct owner records: {len({r[1] for r in rows}):,}")
    print(f"  ...distinct vacated qids:  {len({r[4] for r in rows}):,}")
    print(f"SAME PERSON TWICE in one role (reads as a false extra parent/child): "
          f"{len(dup_rows):,}")
    for r in dup_rows[:25]:
        print(f"    {r[0]:<16} {r[1]:<10} {r[3]:<7} {r[4]:<10} spelled {r[5]}")
    if len(dup_rows) > 25:
        print(f"    ... and {len(dup_rows) - 25:,} more")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
