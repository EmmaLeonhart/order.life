#!/usr/bin/env python
"""Propose parent sets for children recorded with >2 parents — PROPOSE ONLY.

Reads `wikibase/analysis/qa_multiparent.tsv` and writes the review file
    wikibase/analysis/qa_multiparent_proposed.tsv
with columns:
    child_qid, child_label, n_parents, clusters, proposed_parents, unresolved, reason

Nothing in `wikibase/items/*.json` or the source extracts is modified.

Method (as specified in queue.md): the cause is Geni merge duplication, so cluster the
listed parents and treat near-identical records as one person. If a child's parents
collapse to <= 2 distinct people, propose one representative per cluster. If they do
NOT collapse, the row is emitted unresolved WITH the clusters shown — it is never
rank-and-truncated to two, because picking two out of three genuinely distinct claimed
parents is genealogical judgement, not deduplication.

Two records are merged into one cluster only on evidence that they are the same record:

  same_external_id  identical non-empty wikidata_qid or geni_id — decisive
  same_name         identical normalised label, or identical token multiset
                    ('Marcus Livius Drusus' == 'Drusus, Marcus Livius')
  near_name         SequenceMatcher >= 0.90 AND the same given name AND no
                    conflicting recorded sex

Deliberately NOT merged, carrying over the false positives found while proposing the
cycle cuts (see wiki-scripts/propose_cycle_cuts.py):

  - regnal / generational numbering: 'Guerau IV' and 'Guerau V' are two people, and the
    number is precisely what says so
  - Roman cognomen distinctions: 'Scipio Barbatus' and 'Scipio' are father and son
  - records with conflicting recorded sex
  - labels too short or absent to carry information

Clustering is single-linkage: A~B and B~C puts all three together. That is deliberate
for duplicate detection, where a chain of near-identical labels is one person recorded
several times, but it means a cluster should be eyeballed before it is applied.
"""

import csv
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from propose_cycle_cuts import (  # noqa: E402
    ANALYSIS, FEMALE, MALE, given_name, label_similarity, norm,
    ordinal_relation, sourcing_score, tokens,
)

NEAR_NAME = 0.90
# Fuzzy bar for one surname token being a spelling variant of another
# ('Aybar'/'Aibar', 'Castille'/'Castile', 'Nunez'/'Nunes').
VARIANT_TOKEN = 0.80

# Name particles carry no identifying information on their own.
PARTICLES = {
    "de", "del", "della", "di", "da", "do", "dos", "das", "of", "the", "y", "e",
    "la", "le", "el", "los", "las", "von", "van", "der", "den", "bin", "ibn",
    "ben", "bat", "al", "and", "ap", "ab", "st", "san", "santa",
}


def distinguishing_tokens(lbl):
    """Name tokens after the given name, minus particles and punctuation."""
    out = []
    for t in tokens(lbl)[1:]:
        n = "".join(ch for ch in norm(t) if ch.isalnum())
        if len(n) > 1 and n not in PARTICLES:
            out.append(n)
    return out


def _covered(tok, others):
    return any(tok == o or SequenceMatcher(None, tok, o).ratio() >= VARIANT_TOKEN
               for o in others)


def name_variant(la, lb):
    """Is one label a spelling variant or extension of the other?

    'Sancha de Aybar' / 'Sancha of Aibar'  -> yes, one person spelled two ways.
    'Jimena Munoz' / 'Jimena Fernandez de Castro' -> no; the surnames are different
    words, and these really are two of Alfonso VI's partners.

    Both labels must carry at least one distinguishing token, so a bare given name
    is never absorbed into a fuller name.
    """
    if not given_name(la) or given_name(la) != given_name(lb):
        return False
    ta, tb = distinguishing_tokens(la), distinguishing_tokens(lb)
    if not ta or not tb:
        return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return all(_covered(t, long_) for t in short)


def load_persons():
    persons = {}
    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            persons[row["qid"]] = row
    return persons


def lab(persons, qid):
    return " ".join((persons.get(qid, {}).get("label") or "").split()) or qid


def same_person(a, b, persons):
    """(bool, evidence) — are these two records the same person duplicated?"""
    pa, pb = persons.get(a, {}), persons.get(b, {})
    la, lb = lab(persons, a), lab(persons, b)

    for field, name in (("wikidata_qid", "Wikidata ID"), ("geni_id", "Geni ID")):
        va, vb = pa.get(field), pb.get(field)
        if va and vb and va == vb:
            return True, "same %s (%s)" % (name, va)

    sa, sb = pa.get("sex"), pb.get("sex")
    if sa and sb and sa != sb and {sa, sb} <= {MALE, FEMALE}:
        return False, ""

    if ordinal_relation(la, lb) or ordinal_relation(lb, la):
        return False, ""          # regnal numbering distinguishes them

    na, nb = norm(la), norm(lb)
    if len(na) < 4 or len(nb) < 4:
        return False, ""
    if na == nb:
        return True, "identical label '%s'" % la
    if sorted(norm(t) for t in tokens(la)) == sorted(norm(t) for t in tokens(lb)):
        return True, "same name tokens ('%s' / '%s')" % (la, lb)

    sim = label_similarity(la, lb)
    if sim >= NEAR_NAME and given_name(la) == given_name(lb):
        return True, "labels %.0f%% identical, same given name ('%s' / '%s')" % (
            sim * 100, la, lb)
    if name_variant(la, lb):
        return True, ("same given name and every surname token matches as a spelling "
                      "variant ('%s' / '%s')" % (la, lb))
    return False, ""


def cluster(parents, persons):
    """Single-linkage clustering. Returns (list-of-clusters, list-of-evidence)."""
    parent = {q: q for q in parents}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    evidence = []
    for i, a in enumerate(parents):
        for b in parents[i + 1:]:
            ok, why = same_person(a, b, persons)
            if ok:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
                evidence.append("%s+%s: %s" % (a, b, why))

    groups = defaultdict(list)
    for q in parents:
        groups[find(q)].append(q)
    return [sorted(g) for g in groups.values()], evidence


def representative(group, persons):
    """Best-sourced member of a cluster; QID order breaks ties deterministically."""
    return sorted(group, key=lambda q: (-sourcing_score(persons.get(q)), q))[0]


def describe(groups, persons):
    out = []
    for g in sorted(groups, key=lambda g: g[0]):
        names = " = ".join("%s '%s'" % (q, lab(persons, q)) for q in g)
        out.append("[%s]" % names)
    return " ; ".join(out)


def main():
    persons = load_persons()

    rows = []
    with open(ANALYSIS / "qa_multiparent.tsv", encoding="utf-8") as fh:
        src = list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))

    stats = Counter()
    parents_before = 0
    parents_after = 0

    for row in src:
        child = row["child_qid"]
        parents = [q for q in row["parent_qids"].split(",") if q]
        n = len(parents)
        parents_before += n

        groups, evidence = cluster(parents, persons)
        k = len(groups)
        stats["n%d_to_%d" % (n, k)] += 1

        sexes = Counter()
        for g in groups:
            s = persons.get(representative(g, persons), {}).get("sex")
            sexes[s] += 1

        if k <= 2:
            reps = [representative(g, persons) for g in sorted(groups, key=lambda g: g[0])]
            parents_after += len(reps)
            merged = n - k
            reason = ("%d listed parents collapse to %d distinct person(s): %d record(s) "
                      "are duplicates of another listed parent. Evidence — %s"
                      % (n, k, merged, "; ".join(evidence) or "none"))
            if k == 2 and sexes.get(MALE) == 1 and sexes.get(FEMALE) == 1:
                reason += ". The two survivors are one male and one female, as a "
                reason += "biological parent pair should be"
            elif k == 2 and sexes.get(MALE) == 2:
                reason += ". NOTE both survivors are recorded male — the collapse is "
                reason += "clean but the resulting pair is not a biological one; a "
                reason += "further duplicate may be hiding behind differing labels"
            elif k == 2 and sexes.get(FEMALE) == 2:
                reason += ". NOTE both survivors are recorded female — see above"
            elif k == 1:
                reason += ". Only one person survives, so this child ends up with a "
                reason += "single recorded parent; the other parent is missing from "
                reason += "the dump rather than wrong"
            rows.append({
                "child_qid": child,
                "child_label": row["child_label"],
                "n_parents": n,
                "clusters": describe(groups, persons),
                "proposed_parents": ",".join(reps),
                "unresolved": "no",
                "reason": reason,
            })
            stats["resolved"] += 1
        else:
            parents_after += n
            reason = ("%d listed parents do NOT collapse: they cluster into %d distinct "
                      "people, more than a biological pair. Deduplication cannot decide "
                      "which %d are the real parents, and choosing among %d genuinely "
                      "different claimed parents is genealogical judgement, not a merge. "
                      "Clusters are shown for a human to rule on."
                      % (n, k, 2, k))
            if evidence:
                reason += " Partial merges found — %s" % "; ".join(evidence)
            rows.append({
                "child_qid": child,
                "child_label": row["child_label"],
                "n_parents": n,
                "clusters": describe(groups, persons),
                "proposed_parents": "",
                "unresolved": "yes",
                "reason": reason,
            })
            stats["unresolved"] += 1

    out = ANALYSIS / "qa_multiparent_proposed.tsv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n",
                           fieldnames=["child_qid", "child_label", "n_parents",
                                       "clusters", "proposed_parents", "unresolved",
                                       "reason"])
        w.writeheader()
        w.writerows(rows)

    total = len(src)
    resolved = stats["resolved"]
    print("wrote %s" % out)
    print("children with >2 parents:   %d" % total)
    print("collapse to <=2 (proposed): %d  (%.1f%%)" % (resolved, 100.0 * resolved / total))
    print("do not collapse (unresolved): %d  (%.1f%%)"
          % (stats["unresolved"], 100.0 * stats["unresolved"] / total))
    print("parent edges listed: %d -> %d if every proposal were applied "
          "(%d removed)" % (parents_before, parents_after, parents_before - parents_after))
    print()
    print("n_parents -> n_clusters distribution:")
    for key in sorted(k for k in stats if k.startswith("n")):
        print("  %-12s %d" % (key.replace("_to_", " parents -> ") + " clusters",
                              stats[key]))


if __name__ == "__main__":
    main()
