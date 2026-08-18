"""Restore terms that merges dropped before merge_cluster.py learned to carry them.

    python wiki-scripts/backfill_merged_terms.py           # dry run
    python wiki-scripts/backfill_merged_terms.py --write   # apply

WHY THIS EXISTS

`merge_cluster.py` carried every CLAIM from the loser and silently dropped every TERM --
description, aliases, label. That is the 38-dropped-properties bug of 2026-07-31 one layer
up, and it was found the same way: by measuring after the fact instead of trusting the word
"additive". Three losses across the five Magadha/Kosala passes, found 2026-08-18 by diffing
each loser's pre-merge file against its survivor's current one:

  Q50436 <- Q153485   description "Gaiad character", and the survivor has none
  Q28300 <- Q52256    alias "SAHADEVA of Magadha Jarasandha"
  Q2302  <- Q52228    alias "SRUTASRAVA of Magadha"

**The two aliases are the interesting ones and they are why this is not cosmetic.**
Q52228 and Q52256 are two of the eleven nameless shells merged on 2026-08-18 on the
strength of their position in the king list -- same father, same mother, same child as a
named king. Each of them carried an alias naming that exact king. That is the dump
independently confirming an identification made from graph structure alone, and the merge
destroyed the confirmation in the act of using it. The merge notes went on describing all
eleven as "no label, no aliases, no description", which was true of nine and not of those
two.

Q2302's alias is byte-identical to Q2302's own label, so there is nothing to restore there
and the entry below records it rather than writing it. The evidence lives in the git
history and in the devlog either way.

Shadow-aware: every file claiming a touched qid is rewritten, per the standing rule that
editing the canonical file alone is undone the moment it stops being the lowest claimant.
Graph-neutral by construction -- it writes no claims at all.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

# (survivor, lost-from, kind, lang, value, why)
RESTORE = [
    ("Q50436", "Q153485", "description", "en", "Gaiad character",
     "kosala-diwakar; the loser was 'BRIHADASVA of Kosala Placeholder surname' and "
     "carried the description, the survivor has none"),
    ("Q28300", "Q52256", "alias", "en", "SAHADEVA of Magadha Jarasandha",
     "magadha-somapi; the nameless shell's own alias names the man it was merged into, "
     "which is the dump confirming the positional identification"),
    ("Q2302", "Q52228", "alias", "en", "SRUTASRAVA of Magadha",
     "magadha-senajit; same shape as Q52256, but this string is byte-identical to "
     "Q2302's own label, so it is recorded here and not written"),
]


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(q, d):
    (ITEMS / f"{q}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def claimants(qid):
    """Every filename whose internal id is qid -- the canonical file and its shadows."""
    out = [qid]
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if r["to_qid"] == qid:
                    out.append(r["from_qid"])
    return out


def apply_term(d, kind, lang, value):
    """Returns True if the record changed."""
    if kind == "description":
        if lang in (d.get("descriptions") or {}):
            return False
        d.setdefault("descriptions", {})[lang] = {"language": lang, "value": value}
        return True
    have = {a.get("value") for a in (d.get("aliases") or {}).get(lang, [])}
    have.add(((d.get("labels") or {}).get(lang) or {}).get("value"))
    if value in have:
        return False
    d.setdefault("aliases", {}).setdefault(lang, []).append(
        {"language": lang, "value": value})
    return True


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    touched = 0
    for surv, loser, kind, lang, value, why in RESTORE:
        d = load(surv)
        if d is None:
            print(f"  {surv}: no item file -- skipped")
            continue
        probe = json.loads(json.dumps(d))
        if not apply_term(probe, kind, lang, value):
            print(f"  {surv} <- {loser}  {kind}[{lang}] {value!r}")
            print(f"        already present on the survivor, nothing to write")
            print(f"        {why}")
            continue
        files = claimants(surv)
        print(f"  {surv} <- {loser}  {kind}[{lang}] {value!r}")
        print(f"        {why}")
        print(f"        {len(files)} file(s) to rewrite: {', '.join(files)}")
        if write:
            for f in files:
                fd = load(f)
                if fd is None or (fd.get("id") or f) != surv:
                    continue
                apply_term(fd, kind, lang, value)
                save(f, fd)
                touched += 1

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print(f"\nwrote {touched} file(s)")
    print("verifying, from the files rather than from the plan...")
    bad = []
    for surv, _loser, kind, lang, value, _why in RESTORE:
        for f in claimants(surv):
            fd = load(f)
            if fd is None or (fd.get("id") or f) != surv:
                continue
            probe = json.loads(json.dumps(fd))
            if apply_term(probe, kind, lang, value):
                bad.append(f"{f} (claims {surv}) still lacks {kind}[{lang}] {value!r}")
    if bad:
        print("FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print("  every claimant of every survivor carries the restored term")
    print("\nNo claim was written, so edges.tsv cannot move. Run verify_repair.py anyway.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
