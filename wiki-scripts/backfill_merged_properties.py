"""Restore non-genealogical properties that the 2026-07-31 merges dropped.

    python wiki-scripts/backfill_merged_properties.py           # dry run
    python wiki-scripts/backfill_merged_properties.py --write   # apply

WHAT WENT WRONG

merge_cluster.py and apply_cato_cluster_merge.py unioned only GEN_PROPS -- P20 child,
P42 spouse, P47 father, P48 mother, P61 wikidata -- and then rewrote the loser's file as a
copy of the survivor. Any property ONLY the loser held therefore vanished from the dump.
The ten merges applied on 2026-07-31 dropped 38 properties that way:

  external identifiers  P1185 (Rodovid), P1819 (Geni), P4159, P6821 (Alvin), P9495, P64
  biographical          P56 birth and P57 death, on six records

Those merges were reported as "strictly additive". That was true of the genealogy and not
of the records, and the distinction was not made at the time. The graph was unaffected --
edges.tsv reads only GEN_PROPS -- but persons.tsv carries birth and death, so six people
silently lost their dates.

THE REPAIR

For each merged pair, read the loser's file as it stood at BEFORE_MERGES and copy over
every property the survivor still does not have. Where the survivor already holds the
property, its value stands and the difference is reported -- this script does not
adjudicate. Every file claiming the survivor's qid is rewritten, per the shadow rule.

merge_cluster.py now carries these properties itself, so this is a one-off catch-up.
"""

import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

# Last commit before any of the 2026-07-31 merges.
BEFORE_MERGES = "ee6dc8263"

GEN_PROPS = ("P20", "P42", "P47", "P48", "P61")

PAIRS = [
    ("Q73005", "Q148133"), ("Q73002", "Q148134"), ("Q73329", "Q151388"),
    ("Q72855", "Q144170"), ("Q73167", "Q148135"), ("Q72684", "Q141517"),
    ("Q72496", "Q141438"),                                    # Porcii Catones
    ("Q72681", "Q144174"), ("Q72493", "Q144102"), ("Q78063", "Q144042"),  # Porcia
]


def at_commit(q):
    r = subprocess.run(["git", "show", f"{BEFORE_MERGES}:wikibase/items/{q}.json"],
                       cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout.decode("utf-8"))
    except Exception:
        return None


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def claimants():
    out = collections.defaultdict(set)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                out[r["to_qid"]].add(r["from_qid"])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    fam = claimants()

    plan, conflicts = [], []
    for surv, loser in PAIRS:
        old = at_commit(loser)
        cur = load(surv)
        if old is None or cur is None:
            print(f"  skip {surv}/{loser}: missing file")
            continue
        add = {}
        for p, cl in (old.get("claims") or {}).items():
            if p in GEN_PROPS:
                continue
            if p not in (cur.get("claims") or {}):
                add[p] = cl
            else:
                a = sorted(str(v) for v in vals(cur, p))
                b = sorted(str(v) for v in vals(old, p))
                if a != b:
                    conflicts.append((surv, loser, p, a, b))
        if add:
            plan.append((surv, loser, add))

    print(f"{len(plan)} survivor(s) to backfill, "
          f"{sum(len(a) for _, _, a in plan)} propert(ies) total\n")
    for surv, loser, add in plan:
        detail = []
        for p, cl in sorted(add.items()):
            v = [((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                 for c in cl]
            v = [x.get("id") if isinstance(x, dict) and x.get("id")
                 else (x.get("time") if isinstance(x, dict) else x) for x in v]
            detail.append(f"{p}={v}")
        print(f"  {surv} <- {loser}: {'; '.join(detail)}")

    if conflicts:
        print("\nboth sides held these and differ -- NOT touched, survivor's value stands:")
        for surv, loser, p, a, b in conflicts:
            print(f"  {surv}/{loser} {p}: survivor {a} vs loser {b}")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    total = 0
    for surv, loser, add in plan:
        d = load(surv)
        for p, cl in add.items():
            d.setdefault("claims", {})[p] = json.loads(json.dumps(cl))
            total += 1
        text = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
        n = 0
        for f in sorted({surv} | fam.get(surv, set())):
            fp = ITEMS / f"{f}.json"
            if fp.exists():
                fp.write_text(text, encoding="utf-8")
                n += 1
        print(f"  {surv}: +{len(add)} propert(ies), {n} file(s) rewritten")

    print(f"\nrestored {total} propert(ies)")
    print("verifying...")
    ok = True
    for surv, loser, add in plan:
        d = load(surv)
        missing = [p for p in add if p not in (d.get("claims") or {})]
        if missing:
            print(f"  FAIL {surv}: still missing {missing}")
            ok = False
        for f in sorted({surv} | fam.get(surv, set())):
            fd = load(f)
            if fd is None or (fd.get("id") or f) != surv:
                continue
            if sorted((fd.get("claims") or {})) != sorted((d.get("claims") or {})):
                print(f"  FAIL {surv}: shadow {f} disagrees on which properties exist")
                ok = False
    print("all backfilled records complete and consistent" if ok else "PROBLEMS ABOVE")
    print("\nRe-run extract_genealogy.py to refresh persons.tsv (dates changed).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
