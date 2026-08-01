"""Dedupe a named cluster of parallel-import duplicates.

This is the generalised form of apply_cato_cluster_merge.py, which was written for one
cluster and is left in place as the record of what ran on 2026-07-31. Everything learned
there is encoded here as rules the tool enforces rather than as prose someone has to
remember.

    python wiki-scripts/merge_cluster.py porcia           # dry run, prints the plan
    python wiki-scripts/merge_cluster.py porcia --write   # apply
    python wiki-scripts/merge_cluster.py --list

THE TWO RULES THIS ENFORCES

1. **No file may still claim the loser's qid afterwards.** 39,527 qids in this dump are
   claimed by more than one file and extract_genealogy.py keeps only the numerically-lowest.
   Merging B into A rewrites B.json to id=A, which VACATES qid B -- and if any file still
   claims B, it wins the vacancy and injects its own claims. That is how the phantom
   Q148133 <-> Q73167 2-cycle appeared out of a graph that never contained the edge.

   This was first written as an input-side refusal -- "the loser must have no shadows" --
   which was the wrong guard twice over. It is a proxy for the real invariant, and a
   redundant one, because the tool already rewrites every shadow of the loser in the same
   pass. It also forbade safe merges outright: Q72434/Q72514 (Marcus Aemilius Lepidus, both
   carrying wd Q435329) have shadows on BOTH sides and could not be merged in either
   direction. Replaced 2026-07-31 with the outcome-side assertion below, which is strictly
   stronger: after the merge, no file anywhere may still resolve to the loser's qid. A
   loser shadow that cannot be rewritten is still a hard abort, but now it is checked
   against what actually happened rather than guessed from the inputs.

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
    # queue.md item 1 (2026-07-31). qa_tangle_repairs.md ranked this the top DEDUPE:
    # Q72434 and Q72514 both carry wd Q435329 (Marcus Aemilius Lepidus, cos. 78 BC), share
    # the spouse Q72517 Appuleia, and share four of their children outright. Q72434 also
    # holds Q72251 and the birth/death dates -120/-77, which match the consul of 78.
    #
    # This is the pair that exposed the old input-side guard as wrong: BOTH sides have
    # shadow files (Q72434 -> Q87226, Q185444; Q72514 -> Q87280), so no direction was
    # permitted, even though repointing makes either direction safe. Survivor is the lower
    # QID, which also carries strictly more claims.
    #
    # NOT a cascade like the Cato cluster: Q72514's apparently-extra child Q141448 is
    # already a shadow file of Q73893, so it canonicalises to a child Q72434 already has.
    # The survivor gains nothing and simply absorbs a duplicate node.
    # queue.md item 1 (2026-07-31), found while looking for the real defect in the Scipio
    # loop. Q72801 Cornelia has THREE fathers -- Q72957 Scipio Nasica Serapio, Q73425 and
    # Q73017 -- and two of the three are the same man:
    #
    #   Q73425  "Pacuvius Calavius"            sp=[Q73428]         ch=[Q72801]
    #   Q73017  "Pacuvius Calavius  Calavius"  sp=[Q73014,Q73428]  ch=[Q72870,Q72801,Q78746]
    #
    # Same name with the cognomen doubled -- the exact artefact cycle_policy.md names
    # ("Diogo Afonso Afonso de Aguiar, a doubled name") -- married to the same woman
    # Q73428 Claudia Pulcher, and both recorded as the father of the same daughter. Neither
    # carries a Wikidata id, so this is decided on position and name, the same standard used
    # for the Licinia and Salonia pairs in the Porcii Catones cluster.
    #
    # Survivor is Q73017: lower QID, and it holds three children and a second spouse that
    # Q73425 does not. Its label carries the doubled cognomen and is corrected separately
    # after the merge, with the doubled form kept as an alias.
    #
    # This does NOT break the Scipio loop and is not meant to -- the loop runs through
    # Q72957 -> Q72801, not through Calavius. It removes one of Cornelia's three fathers,
    # leaving the sharp question: Scipio Nasica Serapio or Pacuvius Calavius. That one is
    # Emma's.
    "calavius": [
        ("Q73017", "Q73425", "Pacuvius Calavius -- same name with the cognomen doubled, "
                             "same wife Q73428, same daughter Q72801"),
    ],
    "lepidi": [
        ("Q72434", "Q72514", "Marcus Aemilius Lepidus cos. 78 BC -- both carry wd Q435329, "
                             "both married to Q72517 Appuleia, four shared children"),
    ],
    # queue.md item 2 (2026-07-31). The generation directly above the "lepidi" merge above,
    # and it only became legible once that one landed.
    #
    #   Q72615  "Quintus Aemilius Lepidus"  f=[Q72786]           m=Q72789  sp=Q72618  ch=[Q72434]
    #   Q72693  "Quintus Aemilius Lepidus"  f=[Q72786, Q144279]                       ch=[Q72514]
    #
    # Q72514 canonicalises to Q72434, so both men are the father of ONE man -- and Q72434
    # lists both of them as its fathers, which is the dump stating the duplication about
    # itself, the same signature that decided the Porcia pair (Q78066 listing both women as
    # wives). A man has one father, so these two records are one man. They also share their
    # offices (P39 Q153801/Q153802), sex, and the same P94 arms filename.
    #
    # Q72693 carries wd Q11944252 and Q72615 carries none: a gap, not a conflict. Survivor
    # is Q72615 by the lower-QID convention; it also holds the mother and the spouse.
    #
    # WHAT THIS DOES NOT SETTLE, and deliberately does not guess at. Q72693 has TWO fathers,
    # both labelled "Marcus Aemilius Lepidus" -- Q72786 and Q144279 -- so the survivor
    # inherits both. That conflict is not created here, it is pre-existing on Q72693 and both
    # edges are already in edges.tsv; the merge only moves it onto one record where it is
    # visible. It cannot be settled without deciding queue item 1, because Q144279's other
    # child is Q73011, which is one of the three fathers Q72786 claims. Merging Q72786 and
    # Q144279 would therefore close a 2-cycle. Which of those two records is real is Roman
    # prosopography and Emma's call.
    #
    # The merge is correct under EITHER resolution: whichever father record survives, the
    # two sons are still one man. Net effect on multi-parent: Q72434 drops from two fathers
    # to one. Checked before applying -- Q144279 is not a descendant of Q72615 (whose only
    # child is Q72434, and Q144279 is not below that), so the new Q144279 -> Q72615 edge
    # introduces no cycle.
    "quintus-lepidus": [
        ("Q72615", "Q72693", "Quintus Aemilius Lepidus -- both sons of Q72786 and both "
                             "fathers of Q72434, which lists both of them as its fathers"),
    ],
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

    # Rule 1 precondition: every file that claims the loser must exist and be rewritable,
    # so that after the pass nothing is left claiming the vacated qid. The check that it
    # actually worked is in the verify step, which is the guard that matters.
    problems = []
    for surv, loser, _ in merges:
        for q in (surv, loser):
            if load(q) is None:
                problems.append(f"{q}: no item file")
        for s in shad.get(loser, ()):
            if not (ITEMS / f"{s}.json").exists():
                problems.append(
                    f"{loser} has shadow {s} with no file on disk -- it cannot be "
                    f"repointed, so qid {loser} would be left claimable. Aborting.")
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
    carried, conflicts = {}, {}
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

        # Carry over everything else the survivor does not have at all. GEN_PROPS alone is
        # not enough: the loser's file becomes a copy of the survivor, so any property only
        # it held is gone from the dump. The first ten merges of 2026-07-31 dropped 38
        # properties this way -- external ids (P1185 Rodovid, P1819 Geni, P4159, P6821,
        # P9495) and, worse, P56/P57 birth and death dates on six records. Those merges
        # were described as "strictly additive"; that was true of the genealogy and not of
        # the records. Where BOTH sides hold a property, the survivor's value stands and
        # the difference is reported rather than guessed at.
        for p, cl in (dl.get("claims") or {}).items():
            if p in GEN_PROPS:
                continue
            if p not in (ds.get("claims") or {}):
                ds.setdefault("claims", {})[p] = json.loads(json.dumps(cl))
                carried.setdefault(surv, []).append(p)
            else:
                a = sorted(str(v) for v in vals(ds, p))
                b = sorted(str(v) for v in vals(dl, p))
                if a != b:
                    conflicts.setdefault(surv, []).append((p, a, b))

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

    if carried:
        print("\nnon-genealogical properties carried over from the loser:")
        for q, ps in sorted(carried.items()):
            print(f"  {q}: {', '.join(sorted(ps))}")
    if conflicts:
        print("\nboth sides held these and DIFFER -- survivor's value kept, not merged:")
        for q, cs in sorted(conflicts.items()):
            for p, a, b in cs:
                print(f"  {q} {p}: survivor {a} vs loser {b}")

    print("\nverifying...")
    ok = True
    # THE load-bearing check: sweep every item file and assert that nothing anywhere still
    # resolves to a merged-away qid. This is what the old input-side refusal was standing
    # in for, and unlike that refusal it catches a claimant the redirect map did not know
    # about. It reads all 164k filenames but only opens the ones that could matter.
    losers = {loser for _, loser, _ in merges}
    stragglers, unreadable = [], 0
    for path in ITEMS.glob("Q*.json"):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            unreadable += 1
            continue
        # Some files in this dump hold valid JSON that is not an object (extract_
        # genealogy.py skips them the same way). They cannot claim a qid, so they cannot
        # be a straggler, but they are counted so the sweep does not look complete when
        # part of the directory was silently skipped.
        if not isinstance(d, dict):
            unreadable += 1
            continue
        if (d.get("id") or path.stem) in losers:
            stragglers.append(path.stem)
    if unreadable:
        print(f"  note: {unreadable} file(s) were not readable as a JSON object and were "
              f"not checked")
    if stragglers:
        print(f"  FAIL: {len(stragglers)} file(s) still claim a merged-away qid: "
              f"{', '.join(sorted(stragglers)[:10])}")
        ok = False
    else:
        print(f"  no file claims any of the {len(losers)} vacated qid(s)")

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
