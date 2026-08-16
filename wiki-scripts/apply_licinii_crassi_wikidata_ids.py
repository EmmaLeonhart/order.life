"""Two Licinii Crassi carry Wikidata ids three generations too late. Correct them.

    python wiki-scripts/apply_licinii_crassi_wikidata_ids.py           # dry run
    python wiki-scripts/apply_licinii_crassi_wikidata_ids.py --write   # apply

queue.md item 2e. Touches P61 only -- no parent or child claim changes, so edges.tsv
cannot move. Shadow-aware and idempotent.

WHAT IS CERTAIN: THE CURRENT IDS ARE WRONG

This part needs no identification argument, only arithmetic.

  Q72972 is the father of Q72810 Licinia, wife of Q72807 P. Mucius Scaevola (cos. 175 BC),
  so he belongs around 235-183 BC. Its P61 is Q29518656 = P. Licinius Crassus Dives,
  **tribune of the plebs 110 BC**, son of Mucianus.

  Q72981 is aliased "Publius /Licinius-Crassus/ consul 171 BC" in the dump itself. Its P61
  is Q20100913 = P. Licinius Crassus, **praetor 57 BC**.

Both ids land roughly a century and three generations below the records they sit on, and
Q29518656/Q20100913 are themselves a father-son pair -- so a pair of late-Republican
Wikidata items was matched onto a pair of mid-Republican dump records, on name alone. A
wrong external id is worse than none: qa_links_match.tsv reports the record as confirmed
against a person it is not.

THE REPLACEMENTS, and the evidence for each stated separately

  Q72981 -> Q746582  P. Licinius Crassus, cos. 171 BC.
      STRONG, and confirmed from the child side rather than the name. Wikidata gives
      Q746582 two children: Q19715630 "Marcus Licinius Crassus, grandfather of Crassus the
      triumvir", and Q715499 Mucianus. The dump's Q72981 has child Q73260 "Marcus Licinius
      Crassus Agelastus" -- Agelastus IS the triumvir's grandfather. The dump's own alias
      says cos. 171 independently.

  Q72972 -> Q929472  P. Licinius Crassus Dives, cos. 205 BC, pontifex maximus, b. -235
      d. -183.
      GOOD, but NOT confirmed from the child side: Wikidata lists no children for Q929472.
      It rests on three independent things agreeing. The dates fit a father of a woman who
      married the cos. 175. The dump gives Q72972 both Q72810 Licinia and Q72981 (cos. 171)
      as children, i.e. it makes them siblings. And the standard account of Mucianus's
      adoption is that he was adopted by his MATERNAL UNCLE -- Licinia's brother, the cos.
      171 -- which is exactly the sibling pair the dump already holds. Wikidata carries the
      adoption itself on Q715499 as a second father, Q746582.

      Recorded at this confidence deliberately. If Q929472 is later shown wrong, the
      chronological finding above still stands and the id should go back to empty rather
      than to Q29518656.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_WIKIDATA = "P61"

# qid -> (wrong id we expect to find, correct id to write)
FIXES = {
    "Q72972": ("Q29518656", "Q929472"),
    "Q72981": ("Q20100913", "Q746582"),
}


def siblings():
    out = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["to_qid"]].add(r["from_qid"])
            out[r["to_qid"]].add(r["to_qid"])
    return out


def family_of(qid, sib):
    out = []
    for stem in sorted(sib.get(qid, set()) | {qid}, key=lambda x: int(x[1:])):
        path = ITEMS / f"{stem}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and (data.get("id") or stem) == qid:
            out.append(stem)
    return out


def detect_indent(text, default=2):
    """Preserve the file's own indent -- the dump is indent=2 and rewriting at any other
    width reformats the whole file, drowning a one-line change in thousands of diff lines."""
    for line in text.split("\n")[1:]:
        n = len(line) - len(line.lstrip(" "))
        if n > 0:
            return n
    return default


def wikidata_values(data):
    out = []
    for c in (data.get("claims") or {}).get(P_WIKIDATA, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, str):
            out.append(v)
    return out


def fix_claims(data, wrong, right):
    """Drop the wrong id if the right one is already there; otherwise retarget it.

    Q72981 turned out to hold BOTH Q20100913 and Q746582 -- someone had already added the
    correct id and left the wrong one beside it. Blindly retargeting produced
    ['Q746582', 'Q746582'], a duplicate claim, which is a different defect from the one
    being repaired. Caught by reading the dry run rather than trusting the plan.
    """
    claims = (data.get("claims") or {}).get(P_WIKIDATA, [])
    present = wikidata_values(data)
    if right in present:
        keep = [c for c in claims
                if ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value") != wrong]
        removed = len(claims) - len(keep)
        if keep:
            data["claims"][P_WIKIDATA] = keep
        else:
            del data["claims"][P_WIKIDATA]
        return removed, "dropped"
    n = 0
    for c in claims:
        dv = (c.get("mainsnak") or {}).get("datavalue") or {}
        if dv.get("value") == wrong:
            dv["value"] = right
            n += 1
    return n, "retargeted"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv[1:]
    sib = siblings()

    edits = []
    for qid, (wrong, right) in FIXES.items():
        stems = family_of(qid, sib)
        if not stems:
            sys.exit(f"ABORT: no file claims {qid}")
        print(f"{qid}: {len(stems)} file(s) claim it -> {stems}")
        for stem in stems:
            path = ITEMS / f"{stem}.json"
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
            before = wikidata_values(data)
            # Refuse to touch a record that does not hold the id this repair is about --
            # otherwise a re-run after some other edit would rewrite something unexamined.
            if right in before and wrong not in before:
                print(f"  {stem}.json: already {right}, skipping")
                continue
            if wrong not in before:
                sys.exit(f"ABORT: {stem}.json has P61 {before}, expected to contain {wrong}")
            n, how = fix_claims(data, wrong, right)
            print(f"  {stem}.json: P61 {before} -> {wikidata_values(data)}  "
                  f"({n} claim {how})")
            edits.append((path, data, detect_indent(text)))

    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for path, data, indent in edits:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=indent) + "\n")
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for qid, (wrong, right) in FIXES.items():
        for stem in family_of(qid, sib):
            vals = wikidata_values(json.loads((ITEMS / f"{stem}.json").read_text(encoding="utf-8")))
            if wrong in vals:
                bad.append(f"{stem}.json still has {wrong}")
            if right not in vals:
                bad.append(f"{stem}.json is missing {right}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print("Verified: every file claiming either record now carries the corrected id.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
