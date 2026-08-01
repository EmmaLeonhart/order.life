"""Fold the Wikidata cross-check into the cycle proposals, keyed to the CURRENT tangles.

    python wiki-scripts/propose_tangle_repairs.py

Writes wikibase/analysis/qa_tangle_repairs.tsv (one row per edge inside a tangle) and
wikibase/analysis/qa_tangle_repairs.md (a readable per-tangle summary).

WHY THIS REPLACES qa_cycles_proposed.tsv

That file was generated before qa_cycles_vs_wikidata.tsv existed and never saw it, which
is what queue.md asked to fix. But it also cannot simply be joined against, because it is
keyed to a cycle enumeration that no longer exists: until 2026-07-31 the enumerator walked
`set`s of qid strings under Python's randomised string hashing, so its "cycle 7 of 25" is
not a stable referent -- consecutive runs disagreed on how many cycles there even were.

So this rebuilds from the one object that is well defined: the strongly connected
component. Every ancestry cycle lies inside exactly one SCC, and the partition is unique
regardless of traversal order. Each tangle's internal edges are listed with the Wikidata
verdict attached, and a repair is proposed under the cycle_policy.md order.

WIKIDATA IS THE REFERENCE, NOT GOSPEL -- and this is the whole reason the fold needs care.
"contradicted" mostly means "Wikidata records no link between them", which is an absence,
not a refutation: Wikidata is incomplete and demonstrably holds impossible loops of its
own. Three currently-live edges carry that verdict and are nonetheless CORRECT, because
cycle_policy.md decided them on other grounds -- Belus and Anchiroe really are Danaus's
parents there. Cutting on the cross-check alone would sever exactly the cross-tradition
joins the genealogy exists to make. Those edges are listed in PROTECTED below and the tool
refuses to propose cutting them, whatever Wikidata says.

Only one verdict is treated as decisive: "the link the other way round", where Wikidata
records the SAME pair with parent and child swapped. That is a refutation of a specific
direction rather than an absence of evidence.
"""

import collections
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "wikibase" / "analysis"

# Edges that must never be proposed for cutting, with the source of the decision.
# Sourced from cycle_policy.md, not inferred.
PROTECTED = {
    ("Q90576", "Q74973"): "Belus -> Danaus. cycle_policy.md: 'His parents are Belus and "
                          "Anchiroe.' A cross-tradition join and the point of the structure.",
    ("Q131024", "Q74973"): "Anchiroe -> Danaus. cycle_policy.md, same sentence.",
    ("Q75225", "Q74973"): "Iapetos -> Danaus, Titan tier. cycle_policy.md protects the "
                          "Titan descent.",
    ("Q74698", "Q74677"): "Uranus -> Ops. Was held in PENDING_UNMERGE as 'Tros -> Ops' "
                          "pending Emma naming the primordial half of Q74698. That block "
                          "was stale -- the unmerge is done, Q74698 is Ouranos/Caelus, and "
                          "Ops is Rhea, so this is the correct Titan-tier parentage.",
}

# Edges that are residue of an unmerge that was proposed but never finished, so they are
# neither correct nor free to cut -- the record has to be split first.
#
# EMPTY as of 2026-07-31. The one entry here was Q74698 -> Q74677 "Tros -> Ops", held
# pending Emma naming the primordial half of the Tros/primordial merge. That block was
# STALE: the unmerge had already been carried out. Q74698 is now labelled "Uranus" with
# aliases Uranus / Caelus / Ouranos, its parents are Aether and Dies -- which is Hyginus's
# parentage for Caelus -- and its 59 children are the complete Ouranos roster (the Titans,
# the Cyclopes, the Hecatoncheires, the Gigantes, the Erinyes) with ZERO Trojan claims
# left on it. Nothing remains to name or to split.
#
# The edge itself moved to PROTECTED above: Ops is Rhea, and Ouranos -> Rhea is correct.
PENDING_UNMERGE = {}


def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)


def norm_label(s):
    """Normalise a label for duplicate detection.

    Collapses case and whitespace, and -- the part that matters -- collapses a word
    repeated adjacent to itself. That artefact is real and recurring in this dump:
    "Pacuvius Calavius  Calavius" against "Pacuvius Calavius" (merged 2026-07-31), and
    "Diogo Afonso Afonso de Aguiar" which cycle_policy.md names in the Iberian chains.
    Without the collapse those pairs do not match and the signal misses them.
    """
    words = (s or "").casefold().split()
    out = []
    for w in words:
        if not out or w != out[-1]:
            out.append(w)
    return " ".join(out)


def read_tsv(name):
    p = A / name
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    label = {r["qid"]: r.get("label", "") for r in read_tsv("persons.tsv")}
    wd = {r["qid"]: r.get("wikidata_qid", "") for r in read_tsv("persons.tsv")}

    edges = set()
    for r in read_tsv("edges.tsv"):
        if r["parent"] and r["child"] and r["parent"] != r["child"]:
            edges.add((r["parent"], r["child"]))

    # Whole-graph adjacency, not tangle-local: the shared child or parent that corroborates
    # a duplicate pair frequently sits OUTSIDE the tangle. Q72434, the record that named
    # both Quintus Aemilius Lepidus records as its fathers, is itself in the tangle -- but
    # nothing guarantees that in general, and restricting to tangle members would silently
    # drop the corroboration.
    children_of = collections.defaultdict(set)
    parents_of = collections.defaultdict(set)
    for p, c in edges:
        children_of[p].add(c)
        parents_of[c].add(p)

    tangles = []
    for r in read_tsv("qa_cycles.tsv"):
        if r.get("tangle_qids"):
            tangles.append(sorted(r["tangle_qids"].split(","), key=qnum))
    if not tangles:
        print("no tangle_qids column in qa_cycles.tsv -- re-run dump_qa_errors.py")
        return 1

    # Wikidata verdict per edge. The cross-check writes "Q123 (Label)" in its columns.
    verdict, detail = {}, {}
    for r in read_tsv("qa_cycles_vs_wikidata.tsv"):
        p = r["parent"].split(" ")[0]
        c = r["child"].split(" ")[0]
        verdict[(p, c)] = r["verdict"]
        detail[(p, c)] = r["detail"]

    REVERSED = "the link the other way round"

    rows, summaries = [], []
    for comp in tangles:
        inside = set(comp)
        internal = sorted(((p, c) for p, c in edges if p in inside and c in inside),
                          key=lambda e: (qnum(e[0]), qnum(e[1])))
        # duplicate signature 1: two records in the tangle sharing a Wikidata id
        by_wd = collections.defaultdict(list)
        for q in comp:
            if wd.get(q):
                by_wd[wd[q]].append(q)
        dupes = {k: v for k, v in by_wd.items() if len(v) > 1}

        # duplicate signatures 2 and 3: identical labels, positionally corroborated.
        #
        # Added 2026-07-31 (queue.md item 2). The Wikidata-id detector above is blind to a
        # whole class of duplicate, because it needs BOTH sides to carry an id. It missed
        # Q72615/Q72693 "Quintus Aemilius Lepidus", where only one side had one, and it
        # missed Q73425/Q73017 "Pacuvius Calavius", where neither did.
        #
        # A shared label ALONE is far too weak here and must never be enough on its own:
        # this dump is full of Romans with repeating cognomina, and queue.md warns that the
        # long Roman tangles are exactly a repeating-cognomen collision. So each signal
        # requires the label match PLUS a positional corroboration from the graph:
        #
        #   SHARED-CHILD  both records are parents of the SAME record. This is the strong
        #                 one -- one man has one father, so if a child names two
        #                 identically-labelled fathers, the dump is stating the duplication
        #                 about itself. It is what decided Q72615/Q72693 (Q72434 listed
        #                 both as its fathers) and the Porcia pair (Q78066 listed both women
        #                 as wives). Treated as decisive as the shared-wd-id signal.
        #   SHARED-PARENT both records are children of the same record: identically-named
        #                 siblings. Weaker -- report it, rank it above a bare REVIEW, but do
        #                 NOT present it as decided. Two brothers really can share a
        #                 praenomen; the full identical label makes it suspicious, not
        #                 settled.
        by_label = collections.defaultdict(list)
        for q in comp:
            n = norm_label(label.get(q, ""))
            if n:
                by_label[n].append(q)

        label_shared_child, label_shared_parent = {}, {}
        for n, qs in by_label.items():
            if len(qs) < 2:
                continue
            for i in range(len(qs)):
                for j in range(i + 1, len(qs)):
                    a, b = qs[i], qs[j]
                    kids = children_of.get(a, set()) & children_of.get(b, set())
                    rents = parents_of.get(a, set()) & parents_of.get(b, set())
                    if kids:
                        label_shared_child.setdefault(n, []).append((a, b, sorted(kids, key=qnum)))
                    elif rents:
                        label_shared_parent.setdefault(n, []).append((a, b, sorted(rents, key=qnum)))

        decisive = [e for e in internal
                    if verdict.get(e) == "contradicted"
                    and REVERSED in detail.get(e, "")
                    and e not in PROTECTED]
        contradicted = [e for e in internal
                        if verdict.get(e) == "contradicted" and e not in PROTECTED
                        and e not in decisive]
        protected_here = [e for e in internal if e in PROTECTED]
        pending_here = [e for e in internal if e in PENDING_UNMERGE]

        def _pairs(d):
            return "; ".join(
                f"`{a}`/`{b}` “{label.get(a,'')}” via "
                + ",".join(x)
                for pairs in d.values() for a, b, x in pairs)

        if dupes:
            action, why = "DEDUPE", (
                "two records in this tangle share a Wikidata id: "
                + "; ".join(f"{k} claimed by {','.join(v)}" for k, v in sorted(dupes.items())))
        elif label_shared_child:
            action, why = "DEDUPE", (
                "identical labels, and a single record names BOTH of them as its parents -- "
                "one man has one father, so the dump is stating the duplication about "
                "itself: " + _pairs(label_shared_child))
        elif label_shared_parent:
            action, why = "DEDUPE-CANDIDATE", (
                "identical labels on records sharing a parent, i.e. identically-named "
                "siblings. SUSPICIOUS, NOT SETTLED -- no Wikidata id and no shared child "
                "corroborates it, and this dump has genuine repeating cognomina. Confirm "
                "by hand before merging: " + _pairs(label_shared_parent))
        elif decisive:
            action, why = "CUT", (
                "Wikidata records the same pair with parent and child swapped, which "
                "refutes a specific direction rather than merely lacking evidence")
        elif pending_here:
            action, why = "BLOCKED-UNMERGE", "; ".join(
                PENDING_UNMERGE[e] for e in pending_here)
        elif contradicted:
            action, why = "REVIEW", (
                f"{len(contradicted)} edge(s) Wikidata records no link for. That is an "
                "absence, not a refutation -- needs a human reading before any cut")
        else:
            action, why = "REVIEW", (
                "no Wikidata evidence against any internal edge; the contradiction is "
                "either inherited from Wikidata or purely local")

        for p, c in internal:
            flag = ("PROTECTED" if (p, c) in PROTECTED else
                    "PENDING-UNMERGE" if (p, c) in PENDING_UNMERGE else
                    "DECISIVE" if (p, c) in decisive else "")
            rows.append({
                "tangle_size": len(comp),
                "tangle_head": comp[0],
                "parent": p, "parent_label": label.get(p, ""),
                "child": c, "child_label": label.get(c, ""),
                "wd_verdict": verdict.get((p, c), "not-checked"),
                "flag": flag,
                "action": action,
                "detail": detail.get((p, c), ""),
            })
        summaries.append({
            "size": len(comp), "head": comp[0], "action": action, "why": why,
            "members": comp, "internal": internal, "decisive": decisive,
            "contradicted": contradicted, "protected": protected_here,
            "pending": pending_here, "dupes": dupes,
        })

    # DEDUPE-CANDIDATE outranks CUT deliberately: cycle_policy.md's repair order puts
    # dedupe above cut, so an unconfirmed dedupe lead is still worth reading before
    # proposing to sever an edge.
    order = {"DEDUPE": 0, "DEDUPE-CANDIDATE": 1, "CUT": 2, "REVIEW": 3,
             "BLOCKED-UNMERGE": 4}
    summaries.sort(key=lambda s: (order.get(s["action"], 9), -s["size"], qnum(s["head"])))

    with open(A / "qa_tangle_repairs.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=[
            "tangle_size", "tangle_head", "parent", "parent_label", "child",
            "child_label", "wd_verdict", "flag", "action", "detail"])
        w.writeheader()
        for r in sorted(rows, key=lambda r: (order.get(r["action"], 9), -r["tangle_size"],
                                             qnum(r["tangle_head"]), qnum(r["parent"]))):
            w.writerow(r)

    counts = collections.Counter(s["action"] for s in summaries)
    with open(A / "qa_tangle_repairs.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("# Tangle repairs, with the Wikidata cross-check folded in\n\n")
        f.write("**Generated by `wiki-scripts/propose_tangle_repairs.py`. "
                "Regenerate after any change to the dump.**\n\n")
        f.write(f"{len(tangles)} tangles, {sum(len(t) for t in tangles)} records inside "
                f"one, {len(rows)} edges internal to a tangle.\n\n")
        for k, v in sorted(counts.items()):
            f.write(f"- **{k}**: {v}\n")
        f.write("\n`contradicted` from the cross-check usually means *Wikidata records no "
                "link between them* — an absence of evidence, not a refutation, and "
                "Wikidata is incomplete. Only *the link the other way round* is treated as "
                "decisive. Edges listed in `PROTECTED` are never proposed for cutting "
                "however Wikidata votes; `cycle_policy.md` decided them on other grounds.\n")
        for s in summaries:
            f.write(f"\n---\n\n## {s['head']} — {label.get(s['head'],'')} "
                    f"({s['size']} records) → **{s['action']}**\n\n{s['why']}\n\n")
            if s["dupes"]:
                for k, v in sorted(s["dupes"].items()):
                    f.write(f"- duplicate Wikidata id `{k}`: {', '.join(v)}\n")
            for tag, group in (("DECISIVE", s["decisive"]), ("protected", s["protected"]),
                               ("pending unmerge", s["pending"]),
                               ("no Wikidata link", s["contradicted"])):
                for p, c in group:
                    f.write(f"- *{tag}* `{p}` {label.get(p,'')} → `{c}` "
                            f"{label.get(c,'')} — {detail.get((p,c),'')}\n")
            f.write(f"\nmembers: {', '.join(s['members'])}\n")

    print(f"qa_tangle_repairs.tsv: {len(rows)} edges across {len(tangles)} tangles")
    for k, v in sorted(counts.items()):
        print(f"  {k:16s} {v}")
    print("\ndecisive cuts available now:")
    for s in summaries:
        for p, c in s["decisive"]:
            print(f"  {p} -> {c}   {label.get(p,'')} -> {label.get(c,'')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
