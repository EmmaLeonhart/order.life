"""Generate the full per-cycle review document -- the sync source for the Notion page.

    python wiki-scripts/build_cycles_notion.py

Writes wikibase/analysis/cycles_review.md: one section per tangle, every member listed
with its ancestor count, and observations. That file is the SINGLE SOURCE OF TRUTH; the
Notion page is a copy of it. See docs/notion_sync.md.

WHY IT EXISTS. Repairs were being proposed and applied one at a time, each justified in a
commit message Emma had to go read, with the reasoning spread across tool docstrings and
devlog entries. That put her in the position of auditing decisions after the fact instead
of making them. This puts every cycle on one surface, with the number that actually
decides load-bearingness, and proposes nothing.

ANCESTORS IS THE COLUMN THAT MATTERS. cycle_policy.md and queue.md both say load-bearing
means the ancestry reached THROUGH a node -- depth and breadth upward, never descendant
count. qa_cycles_load.tsv ranks by descendants lost and is wrong to. Descendants are
included below because they are useful context, not because they rank anything.

Three ancestor measures, because they answer different questions:
  ancestors  distinct records reachable upward. The headline: what this person's line
             actually reaches. A cut that collapses this is severing a gateway.
  depth      longest chain upward, over the SCC condensation so it is well defined
             despite the cycles.
  to_root    whether Q1 Aster is reachable upward at all.
"""

import csv
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "wikibase" / "analysis"
OUT = A / "cycles_review.md"
ROOT_QID = "Q1"


def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)


def read_tsv(name):
    p = A / name
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    persons = {r["qid"]: r for r in read_tsv("persons.tsv")}
    par, chi = defaultdict(set), defaultdict(set)
    for r in read_tsv("edges.tsv"):
        p, c = r["parent"], r["child"]
        if p and c and p != c:
            par[c].add(p)
            chi[p].add(c)

    verdict, detail = {}, {}
    for r in read_tsv("qa_cycles_vs_wikidata.tsv"):
        k = (r["parent"].split(" ")[0], r["child"].split(" ")[0])
        verdict[k] = r["verdict"]
        detail[k] = r["detail"]

    tangles, shortest = [], {}
    for r in read_tsv("qa_cycles.tsv"):
        if r.get("tangle_qids"):
            comp = sorted(r["tangle_qids"].split(","), key=qnum)
            tangles.append(comp)
            shortest[comp[0]] = r.get("chain_qids", "")
    if not tangles:
        print("no tangles found -- run dump_qa_errors.py first")
        return 1

    def reach(start, adj):
        seen, q = {start}, deque([start])
        while q:
            n = q.popleft()
            for m in adj.get(n, ()):
                if m not in seen:
                    seen.add(m)
                    q.append(m)
        seen.discard(start)
        return seen

    def lab(q):
        return (persons.get(q, {}).get("label") or "").strip() or "(unlabelled)"

    def yr(q, key):
        v = (persons.get(q, {}).get(key) or "").strip()
        if not v:
            return ""
        neg = v.startswith("-")
        try:
            n = int(v.lstrip("+-").split("-")[0])
        except ValueError:
            return ""
        return f"{n} BC" if neg else str(n)

    def wd(q):
        return (persons.get(q, {}).get("wikidata_qid") or "").strip()

    lines = []
    add = lines.append
    total_in = sum(len(t) for t in tangles)
    add("# Ancestry cycles — every one, with the numbers that decide them")
    add("")
    add(f"**{len(tangles)} cycles, {total_in} records caught in one.** Generated from the "
        f"dump by `wiki-scripts/build_cycles_notion.py`; the source of truth is "
        f"`wikibase/analysis/cycles_review.md` in the repo and this page is a copy of it.")
    add("")
    add("A cycle here means a **strongly connected component** — a set of records where "
        "everyone is reachable from everyone else by following parent links, so at least "
        "one person is their own ancestor. That is always an error. Which *edge* is the "
        "wrong one usually is not obvious, and this document does not decide it.")
    add("")
    add("## How to read the ancestor column")
    add("")
    add("**`ancestors` is the only column that ranks anything.** It counts the distinct "
        "records reachable upward from that person. Cutting an edge that collapses this "
        "number is severing a gateway — the thing `cycle_policy.md` says never to do. "
        "`descendants` is there as context and deliberately ranks nothing; "
        "`qa_cycles_load.tsv` ranks by descendants lost and is wrong to.")
    add("")
    add("`depth` is the longest chain upward, computed over the cycle-condensed graph so "
        "it stays well defined. `→Aster` marks whether `Q1` Aster is reachable upward.")
    add("")
    add("Within a cycle every member usually shows the *same* ancestor count, because they "
        "can all reach each other and therefore reach the same set. That is the cycle "
        "itself showing up in the data.")
    add("")
    add("---")
    add("")

    order = sorted(range(len(tangles)), key=lambda i: (-len(tangles[i]),
                                                       qnum(tangles[i][0])))
    for rank, i in enumerate(order, 1):
        comp = tangles[i]
        inside = set(comp)
        add(f"## {rank}. {lab(comp[0])} — {len(comp)} records")
        add("")
        chain = shortest.get(comp[0], "")
        if chain:
            add(f"Shortest loop: `{chain}`")
            add("")
        add("| qid | who | wikidata | born | died | **ancestors** | descendants | depth | →Aster |")
        add("|---|---|---|---:|---:|---:|---:|---:|:---:|")
        for q in comp:
            anc = reach(q, par)
            des = reach(q, chi)
            d = 0
            seen, frontier = set(comp), set(comp)
            # depth: BFS levels upward outside the component
            lvl = 0
            frontier = {p for m in comp for p in par.get(m, ()) if p not in inside}
            seen = set(comp) | frontier
            while frontier:
                lvl += 1
                nxt = set()
                for m in frontier:
                    for p in par.get(m, ()):
                        if p not in seen:
                            seen.add(p)
                            nxt.add(p)
                frontier = nxt
            d = lvl
            add(f"| `{q}` | {lab(q)[:46]} | {wd(q) or '—'} | {yr(q,'birth') or '—'} | "
                f"{yr(q,'death') or '—'} | **{len(anc):,}** | {len(des):,} | {d} | "
                f"{'yes' if ROOT_QID in anc else 'no'} |")
        add("")

        # observations, stated as observations
        notes = []
        by_wd = defaultdict(list)
        for q in comp:
            if wd(q):
                by_wd[wd(q)].append(q)
        for k, v in sorted(by_wd.items()):
            if len(v) > 1:
                notes.append(f"**{', '.join(v)} all carry the same Wikidata id `{k}`** — "
                             f"they may be the same person imported more than once.")
        by_lab = defaultdict(list)
        for q in comp:
            by_lab[lab(q).strip().lower()].append(q)
        for k, v in sorted(by_lab.items()):
            if len(v) > 1 and k != "(unlabelled)":
                notes.append(f"{', '.join(v)} share the label “{lab(v[0])}”.")
        multi = [q for q in comp if len(par.get(q, ())) > 2]
        for q in multi:
            notes.append(f"`{q}` {lab(q)} has {len(par[q])} parents: "
                         f"{', '.join(sorted(par[q], key=qnum))}.")
        for e in sorted(((p, c) for p in comp for c in chi.get(p, ()) if c in inside),
                        key=lambda e: (qnum(e[0]), qnum(e[1]))):
            if verdict.get(e) == "contradicted":
                notes.append(f"Wikidata contradicts `{e[0]}` → `{e[1]}`: "
                             f"{detail.get(e,'')}")
        dated = [(q, yr(q, "birth")) for q in comp if yr(q, "birth")]
        if len(dated) > 1:
            notes.append("Recorded births in this cycle: "
                         + "; ".join(f"{lab(q)[:28]} {y}" for q, y in dated))
        if notes:
            add("**What the data says**")
            add("")
            for n in notes:
                add(f"- {n}")
            add("")
        add("**Decision:** _not made — needs Emma_")
        add("")
        add("---")
        add("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT} written: {len(tangles)} cycles, {total_in} records, "
          f"{len('\n'.join(lines)):,} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
