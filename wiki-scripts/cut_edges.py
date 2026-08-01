"""Remove specific parent -> child edges, from both sides and every shadow file.

    python wiki-scripts/cut_edges.py scipio           # dry run, prints the plan
    python wiki-scripts/cut_edges.py scipio --write   # apply
    python wiki-scripts/cut_edges.py --list

CUT is step 3 of the repair order in cycle_policy.md and the tool of last resort: it is
only correct when UNMERGE and DEDUPE do not apply -- when the records are genuinely
distinct people and one relationship between them is simply false. **Never cut an edge
that is the only link between two traditions.** Every entry below has to say why the
gentler repairs were ruled out.

AN EDGE LIVES IN TWO PLACES. `Father(C) = P` and `Child(P) = C` are the same edge, and
extract_genealogy.py builds the graph from the UNION, so removing one direction leaves it
alive. This bit the Tros unmerge. This tool always removes both, and rewrites every file
claiming either qid, because editing the canonical file alone is undone the moment it stops
being the numerically-lowest claimant.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_FATHER, P_MOTHER, P_CHILD = "P47", "P48", "P20"

CUTS = {
    # queue.md item 2 (2026-08-01). Two of the six mutual-parent pairs that
    # fix_mutual_parent_pairs.py declines to touch. It reports both as "two records of one
    # person that need a MERGE"; hand-checking says neither is, and each is a different
    # defect. That script edits the dump, so its misdiagnoses are written up in queue.md.
    #
    # (a) Q90982 <-> Q88454, THE TWO ESTHERS: **NOT CUT. I claimed the patronymics decided
    #     the direction; they do not, and I retracted it before committing.**
    #
    #       Q88454  "Esther bat Sahlan ben Abraham"          father Q91024 Sahlan
    #       Q90982  "Esther bat Yosef ben 'Amram haDayyan"   father Q88316 Yosef
    #
    #     Both readings are naming-consistent, which is the whole problem:
    #       A: Esther bat Sahlan married Yosef  -> their daughter is "Esther bat Yosef"
    #       B: Esther bat Yosef married Sahlan  -> their daughter is "Esther bat Sahlan"
    #     Under EITHER, each woman is correctly named for her own father and each recorded
    #     father-claim is right. The patronymics confirm both fathers and settle nothing
    #     about who descends from whom -- which is exactly why fix_mutual_parent_pairs.py
    #     reports spouse-coparent evidence on BOTH sides.
    #
    #     I cut it under reading A, and the depth gate then failed: Q88454 fell from 318
    #     levels to 1, because all 3,525 of her ancestors reached her through Q90982. That
    #     is not proof either way -- under reading A the inheritance was spurious and the
    #     loss is correct, under reading B it is real ancestry and the cut is an amputation.
    #     The gate cannot tell those apart, and neither can I. Reverted; needs a source.
    #
    # (b) Q78719 <-> Q78402, BOTH directions. Cleopatra III lists Q78402 as her mother AND
    #     as her child, and Q78402 DOES NOT EXIST -- no file, no shadow claiming the qid,
    #     absent from persons.tsv. It is one of the 138 dangling endpoints. A record that
    #     does not exist cannot be anyone's mother, so both claims are removable with no
    #     judgement call at all. Cleopatra keeps her real mother Q73194 Cleopatra II.
    #     Why not UNMERGE/DEDUPE: there is nothing on the other side to merge with.
    "mutual-parent-residue": [
        ("Q78402", "Q78719", "Q78402 does not exist -- dangling mother claim on "
                             "Cleopatra III"),
        ("Q78719", "Q78402", "Q78402 does not exist -- dangling child claim on "
                             "Cleopatra III"),
    ],
    # queue.md item 1 (2026-07-31). The edge that closes the 18-record Roman tangle:
    #   Q72434 -> Q73893 -> Q73794 -> Q73692 -> ... -> Q72957 -> Q72801 -> Q72786 -> Q72434
    #
    # Q73893 is Lucius Cornelius Scipio Asiaticus Aemilianus (wd Q7234050), consul 83 BC,
    # an Aemilius by birth -- which is why he is CORRECTLY a child of the Lepidus record.
    # The dump dates him b. 200 / d. 77, stored unsigned; d. 77 BC is right for him.
    #
    # He is recorded as the father of Q73794 Gnaeus Cornelius Scipio, whose son Q73692 is
    # Scipio Barbatus, consul 298 BC, dated 400/300 in the dump. Read the dates as the BC
    # magnitudes they are -- and they must be, since Q72957 and Q72434 in the same chain
    # are stored SIGNED negative, and Q73443's +0211 is exactly Scipio Calvus's death in
    # 211 BC -- and the descent below Q73794 runs cleanly forward:
    #     Q73692 400/300 -> Q73569 306/250 -> Q73443 256/211 -> Q73293 230/171
    #     -> Q73128 205/141 -> Q72957 -182/-132
    # while Q73893 sits at 200/77. His grandson is born some 140-200 years before him.
    #
    # This is the trap the queue item warned about: under a naive AD reading the edge
    # looks fine (200 then 400), which is presumably how it survived. Under the correct
    # BC reading it is impossible. The repeating-cognomen collision -- the ancient
    # Scipiones hung under a 1st-century Scipio because both are "Cornelius Scipio".
    #
    # Why not UNMERGE: Q73893 holds ONE identity, not two. Its parents are the Lepidi, its
    # Wikidata id is the 1st-century Aemilianus, and its other child Q72248 (Cornelius
    # Scipio Salvito, wd Q1269233, Caesar's associate at Thapsus in 46 BC) is 1st-century
    # too. Only the Q73794 attachment is out of place. Q73794 likewise carries no second
    # identity -- its only claims are this false parentage and its son.
    # Why not DEDUPE: Q73794's wd Q128598522 is unique here; it duplicates nothing.
    # Not a tradition join: both sides are Roman.
    #
    # BOTH parents are cut, not just the one that closes the loop. Q99342 Aemilia Paula is
    # Q73893's wife and Q73794's recorded mother, and her only other child is the
    # 1st-century Salvito. There is no reading where she mothers a 4th-century man.
    # Cutting only the father -- which alone would break the tangle, since Q99342 is not in
    # it -- would leave an equally impossible claim standing just because no cycle ran
    # through it.
    #
    # Q73794 is left parentless, which is honest: the dump does not record Barbatus's
    # grandfather, and inventing one is not this tool's business. His descent below is
    # untouched.
    # REVERTED 2026-07-31, same day, by Emma's question: "no risk of load bearing ancestor
    # gateways being lost?" There was, and I had not checked.
    #
    # The chronology above is still correct -- that edge cannot be right. But it was the
    # SOLE upward gateway for the entire Scipio line. Measured after the fact:
    #
    #     Q73794 Gnaeus Cornelius Scipio   263 ancestors deep  ->  0
    #     Q73692 Scipio Barbatus           264                 ->  1
    #     Q73299 Scipio Africanus          267                 ->  4
    #     Q72957 Nasica Serapio            269                 ->  12
    #
    # and the 263-link chain ran all the way up to Q1 Aster, the root of the genealogy.
    # Cutting it made Scipio Africanus, Barbatus, the Nasicae and Cornelia a rootless
    # island. cycle_policy.md is explicit about this exact situation: "If a cycle can only
    # be broken by cutting such a join, that is a signal the real defect is elsewhere in
    # the loop -- go find it." I broke the cycle instead of finding the defect.
    #
    # What I got wrong methodologically: I verified with compare_tangles.py, which measures
    # WIDTH -- how many records sit in a tangle. It reported 18 records freed and 0 tangles
    # introduced, which looked like a clean win. Load-bearing here means DEPTH, upward, and
    # nothing I ran measured that. A repair can be green on every existing gate and still
    # amputate 263 generations.
    #
    # Kept, disabled, as the record. The real work is queue item 1: find which edge in
    # Q73794 -> ... -> Q72957 -> Q72801 -> Q72786 -> Q72615 -> Q72434 -> Q73893 is the
    # false one, so the loop opens without detaching the Scipiones from Aster.
    "scipio-REVERTED-do-not-apply": [],
}


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def vals(d, pid):
    # Tolerates a missing record. A qid with no file lists nothing, so the empty answer is
    # the correct one rather than a crash. Guarding at each call site instead was the
    # wrong shape: on 2026-08-01 this cut set hit the same NoneType three separate times
    # -- plan, apply, then verify -- and the second crash landed AFTER the first edge had
    # already been written to disk. One guard at the root beats three at the edges.
    if d is None:
        return []
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def label(q):
    d = load(q)
    if not d:
        return "?"
    v = (d.get("labels") or {}).get("en")
    return (v.get("value") if isinstance(v, dict) else v) or "(no label)"


def claimants():
    out = collections.defaultdict(set)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                out[r["to_qid"]].add(r["from_qid"])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    if "--list" in sys.argv or not args:
        print("cut sets:")
        for k, v in CUTS.items():
            print(f"  {k:10s} {len(v)} edge(s)")
        return 0
    name = args[0]
    if name == "selfloops":
        # Data-driven, from what the extractor recorded rather than a hand-kept list.
        #
        # A record that is its own parent is an error under any reading -- there is no
        # tradition in which someone fathers himself -- so this needs no adjudication, and
        # unlike every other cut it carries NO risk of severing a join: a self-edge links a
        # node to itself, so it can never be the only link between two traditions.
        # extract_genealogy.py already excludes self-edges from the graph, so removing them
        # cannot change edges.tsv at all. This only makes the item files agree with the
        # graph that was always computed from them, and lets invariant I2 go green
        # honestly instead of vacuously.
        path = ROOT / "wikibase" / "analysis" / "qa_self_edges.tsv"
        if not path.exists():
            print("qa_self_edges.tsv missing -- run extract_genealogy.py first")
            return 1
        with open(path, encoding="utf-8") as f:
            todo = [r["qid"] for r in csv.DictReader(f, delimiter="\t") if r.get("qid")]
        cuts = [(q, q, "record lists itself as its own parent/child") for q in todo]
    elif name not in CUTS:
        print(f"unknown cut set {name!r}; try --list")
        return 1
    else:
        cuts = CUTS[name]
    fam = claimants()

    plan = []
    for parent, child, why in cuts:
        dp, dc = load(parent), load(child)
        # A DANGLING endpoint has no file on either side of the edge. Refusing the whole
        # cut because one side does not exist was the wrong guard: the claim still sits on
        # the side that DOES exist, pointing at nothing, and that claim is exactly what
        # needs removing. Cleopatra III (Q78719) lists Q78402 as both her mother and her
        # child, and Q78402 has no file, no shadow claiming the qid, and no persons.tsv
        # row -- one of the 138 dangling endpoints. Abort only if NEITHER side exists,
        # which would leave nothing to edit.
        if dp is None and dc is None:
            print(f"ABORT: neither {parent} nor {child} has an item file -- nothing to edit")
            return 1
        if dp is None or dc is None:
            missing = parent if dp is None else child
            print(f"  note: {missing} has no item file (dangling endpoint) -- removing the "
                  f"claim from the side that exists")
        on_parent = dp is not None and child in vals(dp, P_CHILD)
        on_child = ([p for p in (P_FATHER, P_MOTHER) if parent in vals(dc, p)]
                    if dc is not None else [])
        if not on_parent and not on_child:
            print(f"  {parent} -> {child}: already absent on both sides, nothing to do")
            continue
        plan.append((parent, child, why, on_parent, on_child))

    print(f"cut set {name!r}: {len(plan)} edge(s)\n")
    for parent, child, why, on_parent, on_child in plan:
        print(f"  {parent} ({label(parent)[:34]}) -> {child} ({label(child)[:34]})")
        print(f"        {why}")
        print(f"        declared on parent {P_CHILD}: {on_parent}; "
              f"on child: {on_child or 'no'}")
        n = len({parent} | fam.get(parent, set())) + len({child} | fam.get(child, set()))
        print(f"        {n} file(s) will be rewritten")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    removed = 0
    dirty = set()
    # Both sides are skipped when their file does not exist. The plan phase already
    # allows a dangling endpoint through -- guarding only there and not here is what made
    # this crash mid-run on 2026-08-01, after it had already written the first cut.
    for parent, child, _, _, _ in plan:
        dp = load(parent)
        if dp is not None:
            cl = (dp.get("claims") or {})
            if P_CHILD in cl:
                keep = [c for c in cl[P_CHILD]
                        if ((c.get("mainsnak") or {}).get("datavalue") or {})
                        .get("value", {}).get("id") != child]
                removed += len(cl[P_CHILD]) - len(keep)
                if keep:
                    cl[P_CHILD] = keep
                else:
                    del cl[P_CHILD]
            write_family(parent, dp, fam)
            dirty.add(parent)

        dc = load(child)
        if dc is not None:
            cl = (dc.get("claims") or {})
            for p in (P_FATHER, P_MOTHER):
                if p in cl:
                    keep = [c for c in cl[p]
                            if ((c.get("mainsnak") or {}).get("datavalue") or {})
                            .get("value", {}).get("id") != parent]
                    removed += len(cl[p]) - len(keep)
                    if keep:
                        cl[p] = keep
                    else:
                        del cl[p]
            write_family(child, dc, fam)
            dirty.add(child)

    print(f"removed {removed} claim(s) across {len(dirty)} record(s)")

    print("\nverifying...")
    ok = True
    for parent, child, _, _, _ in plan:
        dp, dc = load(parent), load(child)
        if child in vals(dp, P_CHILD):
            print(f"  FAIL {parent} still lists {child} as a child")
            ok = False
        for p in (P_FATHER, P_MOTHER):
            if parent in vals(dc, p):
                print(f"  FAIL {child} still lists {parent} as {p}")
                ok = False
    for q in sorted(dirty):
        ref = None
        for f in sorted({q} | fam.get(q, set())):
            d = load(f)
            if d is None or (d.get("id") or f) != q:
                continue
            cur = {p: sorted(vals(d, p)) for p in (P_FATHER, P_MOTHER, P_CHILD)}
            if ref is None:
                ref = cur
            elif cur != ref:
                print(f"  FAIL {q}: shadow {f} disagrees after the cut")
                ok = False
    print("edges gone from both sides, all claimants agree" if ok else "PROBLEMS ABOVE")
    print("\nRe-run extract_genealogy.py, dump_qa_errors.py, compare_tangles.py.")
    return 0 if ok else 1


def write_family(q, data, fam):
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for f in sorted({q} | fam.get(q, set())):
        fp = ITEMS / f"{f}.json"
        if fp.exists():
            fp.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
