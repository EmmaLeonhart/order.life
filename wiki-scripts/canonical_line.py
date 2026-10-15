"""
Each person's canonical line to Aster (Q1) and Andromeda (Q3): which parent it runs through.

The name schema (planning/name-schema.md) sets a person's patronymic or matronymic by this line,
"not defaulting to patronymic" (Emma, 2026-10-13: "my canonical line goes through my mother").
The canonical line is the shortest descent from the person up to Q1 or Q3; its first link is a
father (patronymic) or a mother (matronymic), by that parent's recorded sex.

A person with no route to either root (most of the graph today) falls back to the parent with
the larger known ancestry, since "load-bearing" in this repo means the ancestors reached upward
through a node (CLAUDE.md); a tie there goes to the mother. These rows say "fallback".

Her own words override the computation where she has said which line is hers (OVERRIDES).

When both parents are equally near, the tie goes to the parent whose own line is shorter to the
*other* root as well (so a line reaching both Aster and Andromeda wins), then to the mother, since
the schema refuses the patronymic default. Every tie is counted in the output so the rule can be
revisited.

    python wiki-scripts/canonical_line.py      # writes wikibase/analysis/canonical_line.tsv

Stdlib only. Reads persons.tsv and edges.tsv (parent, child).
"""
import csv
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "wikibase" / "analysis"
OUT = ANALYSIS / "canonical_line.tsv"
ROOTS = ("Q1", "Q3")
MALE, FEMALE = "Q153718", "Q153719"
# Lines a person has named themselves. Q2's parents are placeholders in this graph (her real
# ancestry is in the genealogy repository), so the computation cannot see her line.
OVERRIDES = {"Q2": ("mother", "Emma, 2026-10-13: \"my canonical line goes through my mother\"")}
ANCESTOR_CAP = 5000  # enough to rank two parents; stops runaway counts in large trees


def load():
    sex, label = {}, {}
    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sex[r["qid"]] = r["sex"]
            label[r["qid"]] = r["label"]
    parents, children = defaultdict(set), defaultdict(set)
    with open(ANALYSIS / "edges.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            parents[r["child"]].add(r["parent"])
            children[r["parent"]].add(r["child"])
    return sex, label, parents, children


def descent_distances(root, children):
    """Generations from root down to every descendant (BFS over parent -> child)."""
    dist = {root: 0}
    q = deque([root])
    while q:
        p = q.popleft()
        for c in children.get(p, ()):
            if c not in dist:
                dist[c] = dist[p] + 1
                q.append(c)
    return dist


def ancestor_count(q, parents, cache):
    """Distinct ancestors above q, counted up to ANCESTOR_CAP (BFS, so cycles are safe)."""
    if q in cache:
        return cache[q]
    seen, frontier = set(), [q]
    while frontier and len(seen) < ANCESTOR_CAP:
        nxt = []
        for x in frontier:
            for p in parents.get(x, ()):
                if p not in seen:
                    seen.add(p)
                    nxt.append(p)
        frontier = nxt
    cache[q] = len(seen)
    return cache[q]


def main():
    sex, label, parents, children = load()
    d = {r: descent_distances(r, children) for r in ROOTS}
    inf = float("inf")

    def near(q):
        return min(d[r].get(q, inf) for r in ROOTS)

    rows, links, ties, cache = [], Counter(), Counter(), {}
    for q in sorted(set(sex) | set(parents), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        dq = near(q)
        if q in ROOTS:
            rows.append([q, 0, q, "", "root", 0, label.get(q, "")])
            continue
        if q in OVERRIDES:
            want, why = OVERRIDES[q]
            ps = sorted(parents.get(q, ()))
            pick = next((p for p in ps if sex.get(p) == (FEMALE if want == "mother" else MALE)), None)
            if pick is None:  # placeholders with no sex: take the one labelled for the role
                pick = next((p for p in ps if label.get(p, "").lower().startswith(want)), ps[0] if ps else "")
            rows.append([q, "" if dq == inf else dq, "override", pick, want, len(ps), label.get(q, "")])
            links[want] += 1
            continue
        if dq == inf:
            ps = sorted(parents.get(q, ()), key=lambda p: (-ancestor_count(p, parents, cache),
                                                          sex.get(p) != FEMALE, p))
            if not ps:
                rows.append([q, "", "", "", "none", 0, label.get(q, "")])
                links["none"] += 1
                continue
            p = ps[0]
            link = {MALE: "father", FEMALE: "mother"}.get(sex.get(p), "parent")
            links["fallback " + link] += 1
            rows.append([q, "", "fallback", p, link, len(ps), label.get(q, "")])
            continue
        cands = [p for p in parents.get(q, ()) if near(p) == dq - 1]
        if len(cands) > 1:
            ties["tie"] += 1
            # Prefer a parent that reaches both roots most closely, then the mother.
            cands.sort(key=lambda p: (sum(d[r].get(p, inf) for r in ROOTS), sex.get(p) != FEMALE, p))
        p = cands[0]
        link = {MALE: "father", FEMALE: "mother"}.get(sex.get(p), "parent")
        links[link] += 1
        reach = "+".join(r for r in ROOTS if d[r].get(q) == dq)
        rows.append([q, dq, reach, p, link, len(cands), label.get(q, "")])

    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["qid", "generations", "root", "canonical_parent", "link", "candidates", "label"])
        w.writerows(rows)
    total = sum(links.values())
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows):,} rows")
    for k, v in links.most_common():
        print(f"  {k:8} {v:>8,}  ({100 * v / max(1, total):.1f}%)")
    print(f"  ties between parents at the same distance: {ties['tie']:,}")
    return rows


if __name__ == "__main__":
    rows = main()
    if len(sys.argv) > 1:
        for q in sys.argv[1:]:
            print(next((r for r in rows if r[0] == q), q))
