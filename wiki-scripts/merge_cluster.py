"""Dedupe a named cluster of parallel-import duplicates.

This is the generalised form of apply_cato_cluster_merge.py, which was written for one
cluster and is left in place as the record of what ran on 2026-07-31. Everything learned
there is encoded here as rules the tool enforces rather than as prose someone has to
remember.

    python wiki-scripts/merge_cluster.py porcia           # dry run, prints the plan
    python wiki-scripts/merge_cluster.py porcia --write   # apply
    python wiki-scripts/merge_cluster.py --list

THE TWO RULES THIS ENFORCES

1. **Merge INTO the side that has shadow files.** 39,527 qids in this dump are claimed by
   more than one file and extract_genealogy.py keeps only the numerically-lowest. Merging
   B into A rewrites B.json to id=A, which VACATES qid B -- and if B has shadows, one of
   them immediately wins the vacancy and injects its own claims. That is how the phantom
   Q148133 <-> Q73167 2-cycle appeared out of a graph that never contained the edge. So
   the survivor must be the side that has shadows, and the loser the side that has none.
   The tool refuses to run a pair that violates this.

2. **Rewrite every file claiming either qid, not just the canonical one.** An edit to the
   canonical file alone is silently reverted the moment it stops being the lowest
   claimant. check_staged_shadows.py gates this at commit time; the tool does it up front.

MECHANISM, and it is non-destructive: union the loser's genealogical claims into the
survivor, rewriting any reference that points at a record being merged away, then rewrite
the loser's file and every shadow of both sides as a copy of the survivor. Nothing is
deleted and git reverts it cleanly.

WHAT IT DOES NOT DO: third-party records that cite a loser qid are left alone, because
extract_genealogy.py canonicalises every edge through the redirect map. This matches
apply_dup_merge.py. It means item files keep stale-looking references -- Q72624 "Livia"
still lists Q141517 and Q141438 as spouse and child after the Cato merge -- which is
harmless for the graph but surprising to read.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

GEN_PROPS = ("P20", "P42", "P47", "P48", "P61")  # child, spouse, father, mother, wikidata

CLUSTERS = {
    # queue.md item 1 (2026-07-31): the residue the Porcii Catones dedupe deliberately
    # left standing. Cato the Younger came out of that merge with six children because
    # the two import branches contributed overlapping daughters. Resolved here.
    #
    # Q78063 "Porcia Catonis" and Q144042 "Porcia" are the same woman:
    #   - Q144042 carries wd Q255448, whose own Wikidata name is "Porcia Catonis" --
    #     letter for letter Q78063's label.
    #   - both are daughters of Cato the Younger by an Atilia record.
    #   - both are spouses of THE SAME record, Q78066 Marcus Calpurnius Bibulus
    #     (wd Q316775), which already lists both of them as wives -- the duplicate
    #     signature, stated by the dump itself.
    #   - both are the mother of a son of Q78066.
    #
    # That forces the two records above her, or the survivor ends up with two duplicate
    # mothers and Cato the Younger with two duplicate wives:
    #   - Q72493 / Q144102 "Atilia", both wives of Cato the Younger and mothers of the
    #     Porcia pair; Q144102 carries wd Q2334126 ("Atilia").
    #   - Q72681 "Gaius Atilius" / Q144174 "Atilius Serranus", both the father of an
    #     Atilia who married Cato the Younger; Q144174 carries wd Q12275873, whose
    #     Wikidata name is "G. Atilius Serranus" -- the same man Q72681 is named for.
    #
    # Deliberately NOT merged: Q141439 (wd Q18280006) and Q141441 (wd Q94959905) are also
    # Porcia daughters of Cato the Younger, but by Marcia (Q139581), a different wife, and
    # they carry two distinct Wikidata items. They are not this Porcia and not obviously
    # each other. Likewise Q77899 (wd Q3655959, Lucius Calpurnius Bibulus) and Q141508
    # (wd Q104224002, "Calpurnius Bibulus") are both sons of Q78066 who land on the merged
    # Porcia; they are plausibly one man but carry different Wikidata items, so merging
    # them would be a guess.
    "porcia": [
        ("Q72681", "Q144174", "Gaius Atilius Serranus -- wd Q12275873 is named "
                              "'G. Atilius Serranus'; both are the father of Cato the "
                              "Younger's wife Atilia"),
        ("Q72493", "Q144102", "Atilia -- both wives of Cato the Younger and mothers of "
                              "the Porcia pair below; Q144102 carries wd Q2334126"),
        ("Q78063", "Q144042", "Porcia Catonis -- wd Q255448 is named 'Porcia Catonis'; "
                              "both are spouses of the same record Q78066, which lists "
                              "both as wives"),
    ],
}


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(q, d):
    (ITEMS / f"{q}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def claim_id(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else None


def shadows():
    out = collections.defaultdict(list)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                out[r["to_qid"]].append(r["from_qid"])
    return out


def redirect_map():
    """from_qid -> to_qid for every file whose internal id differs from its filename.

    This must be folded into canonicalisation or a merge re-imports references to records
    an EARLIER merge already retired. Caught in dry run on the porcia cluster: Q144102 and
    Q144042 both cite Q141438, which the Porcii Catones merge had already redirected to
    Q72496, so the naive union would have given the merged Porcia two fathers that are the
    same man. The graph would still have canonicalised them to one edge, hiding it.
    """
    out = {}
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                out[r["from_qid"]] = r["to_qid"]
    return out


def label(q):
    d = load(q)
    if not d:
        return "?"
    v = (d.get("labels") or {}).get("en")
    return (v.get("value") if isinstance(v, dict) else v) or "(no label)"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv

    if "--list" in sys.argv or not args:
        print("clusters:")
        for name, pairs in CLUSTERS.items():
            print(f"  {name:10s} {len(pairs)} pair(s)")
        return 0
    name = args[0]
    if name not in CLUSTERS:
        print(f"unknown cluster {name!r}; try --list")
        return 1
    merges = CLUSTERS[name]
    shad = shadows()

    # Rule 1, enforced: survivor must have shadows, loser must have none.
    problems = []
    for surv, loser, _ in merges:
        for q in (surv, loser):
            if load(q) is None:
                problems.append(f"{q}: no item file")
        if shad.get(loser):
            problems.append(
                f"{loser} has shadow files {shad[loser]} -- merging it away vacates a "
                f"shadowed qid, which injects claims. Reverse the pair or repoint first.")
    if problems:
        print("ABORT -- preconditions failed:")
        for p in problems:
            print("  " + p)
        return 1

    alias = {}
    for surv, loser, _ in merges:
        alias[loser] = surv
        for s in list(shad.get(loser, ())) + list(shad.get(surv, ())):
            alias[s] = surv

    redirects = redirect_map()

    def canon(q):
        """Resolve through earlier merges' redirects first, then this cluster's."""
        for _ in range(8):
            nxt = alias.get(q, redirects.get(q, q))
            if nxt == q:
                return q
            q = nxt
        return q

    print(f"cluster {name!r}: {len(merges)} merge(s)\n")
    for surv, loser, why in merges:
        ds, dl = load(surv), load(loser)
        print(f"  {loser} -> {surv}   {label(surv)[:44]}")
        print(f"        {why}")
        for p in GEN_PROPS:
            gained = sorted({canon(v) for v in vals(dl, p)
                             if canon(v) not in set(vals(ds, p)) and canon(v) != surv})
            if gained:
                print(f"        survivor gains {p}: {gained}")
        print(f"        {1 + len(shad.get(surv, ())) + len(shad.get(loser, ()))} "
              f"file(s) rewritten (loser + shadows of both sides)")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    for surv, loser, _ in merges:
        ds, dl = load(surv), load(loser)
        before = {p: len(vals(ds, p)) for p in GEN_PROPS}
        for p in GEN_PROPS:
            have = set(vals(ds, p))
            for c in (dl.get("claims") or {}).get(p, []):
                key = claim_id(c)
                if key is not None:
                    key = canon(key)
                    if key in have or key == surv:
                        continue
                    c = json.loads(json.dumps(c))
                    c["mainsnak"]["datavalue"]["value"]["id"] = key
                    if ("numeric-id" in c["mainsnak"]["datavalue"]["value"]
                            and key[1:].isdigit()):
                        c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(key[1:])
                else:
                    key = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                    if key in have:
                        continue
                ds.setdefault("claims", {}).setdefault(p, []).append(c)
                have.add(key)

        for p in GEN_PROPS:
            kept, seen = [], set()
            for c in (ds.get("claims") or {}).get(p, []):
                key = claim_id(c)
                if key is None:
                    kept.append(c)
                    continue
                key = canon(key)
                if key == surv or key in seen:
                    continue
                seen.add(key)
                c["mainsnak"]["datavalue"]["value"]["id"] = key
                if "numeric-id" in c["mainsnak"]["datavalue"]["value"] and key[1:].isdigit():
                    c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(key[1:])
                kept.append(c)
            if p in (ds.get("claims") or {}):
                ds["claims"][p] = kept
        save(surv, ds)
        after = {p: len(vals(load(surv), p)) for p in GEN_PROPS}

        merged = load(surv)
        n = 0
        for f in [loser] + list(shad.get(loser, ())) + list(shad.get(surv, ())):
            if (ITEMS / f"{f}.json").exists():
                save(f, merged)
                n += 1
        print(f"  {loser} -> {surv}: {before} -> {after}  ({n} file(s) rewritten)")

    print("\nverifying...")
    ok = True
    for surv, loser, _ in merges:
        for f in [surv, loser] + list(shad.get(loser, ())) + list(shad.get(surv, ())):
            d = load(f)
            if d is not None and d.get("id") != surv:
                print(f"  FAIL {f}: internal id is {d.get('id')}, expected {surv}")
                ok = False
        d = load(surv)
        for p in ("P20", "P42", "P47", "P48"):
            if surv in vals(d, p):
                print(f"  FAIL {surv}: is its own {p}")
                ok = False
            stale = [v for v in vals(d, p) if v in alias]
            if stale:
                print(f"  FAIL {surv}: {p} still cites merged-away {stale}")
                ok = False
    print("all files agree with their survivor" if ok else "PROBLEMS ABOVE")
    print("\nNow re-run extract_genealogy.py, dump_qa_errors.py, check_invariants.py.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
