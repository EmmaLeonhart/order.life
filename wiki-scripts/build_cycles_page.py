#!/usr/bin/env python
"""Build the browsable ancestry-cycle report from the current dump extracts.

    python wiki-scripts/build_cycles_page.py

Reads `qa_cycles.tsv`, `persons.tsv`, `edges.tsv`, `spouses.tsv` and writes a
self-contained page to `wikibase/analysis/cycles.html` — no external assets, so it
opens straight from disk and can be published as-is.

Regenerate it after any repair pass; the page always shows the cycles that are in
the dump right now, not the ones that were there when it was last written.
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "wikibase" / "analysis"
TEMPLATE = Path(__file__).resolve().parent / "cycles_page.html"
OUT = ANALYSIS / "cycles.html"

SEX = {"Q153718": "M", "Q153719": "F"}

# Mutual parent pairs already repaired by fix_mutual_parent_pairs.py.
REPAIRED_PAIRS = 8

csv.field_size_limit(10_000_000)


def year_of(stamp):
    if not stamp:
        return None
    try:
        y = int(stamp[1:].split("-")[0])
    except (ValueError, IndexError):
        return None
    if y == 0 or y > 100_000:
        return None
    return -y if stamp[0] == "-" else y


def rows(name):
    with open(ANALYSIS / name, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    persons = {r["qid"]: r for r in rows("persons.tsv")}
    par, ch, sp = defaultdict(set), defaultdict(set), defaultdict(set)
    for r in rows("edges.tsv"):
        par[r["child"]].add(r["parent"])
        ch[r["parent"]].add(r["child"])
    for r in rows("spouses.tsv"):
        sp[r["a"]].add(r["b"])
        sp[r["b"]].add(r["a"])

    cycles = []
    for r in rows("qa_cycles.tsv"):
        chain = r["chain_qids"].split(" -> ")[:-1]      # drop the repeated closer
        nodes = []
        for q in chain:
            p = persons.get(q, {})
            nodes.append({
                "q": q,
                "l": " ".join((p.get("label") or "").split()) or "(no label)",
                "s": SEX.get(p.get("sex"), ""),
                "b": year_of(p.get("birth")),
                "d": year_of(p.get("death")),
                "wd": p.get("wikidata_qid") or "",
                "g": 1 if p.get("geni_id") else 0,
                "np": len(par[q]), "nc": len(ch[q]), "ns": len(sp[q]),
            })
        cycles.append({"len": int(r["cycle_len"]), "nodes": nodes})

    freq = defaultdict(int)
    for c in cycles:
        n = c["nodes"]
        for i in range(len(n)):
            freq[(n[i]["q"], n[(i + 1) % len(n)]["q"])] += 1
    for c in cycles:
        n = c["nodes"]
        c["edges"] = [freq[(n[i]["q"], n[(i + 1) % len(n)]["q"])] for i in range(len(n))]

    data = json.dumps(cycles, ensure_ascii=False, separators=(",", ":"))
    if "</script" in data:
        sys.exit("a label contains a closing script tag; refusing to inline")

    # How many mutual pairs the repair pass has already cleared, so the page can say
    # so rather than silently showing a shorter list than last time.
    mutual = sum(1 for c in cycles if len(c["nodes"]) == 2)
    repaired = json.dumps({"fixed": REPAIRED_PAIRS, "left": mutual})

    html = TEMPLATE.read_text(encoding="utf-8")
    for token in ("__DATA__", "__REPAIRED__"):
        if token not in html:
            sys.exit("template %s has no %s placeholder" % (TEMPLATE, token))
    OUT.write_text(html.replace("__DATA__", data).replace("__REPAIRED__", repaired),
                   encoding="utf-8")

    people = {n["q"] for c in cycles for n in c["nodes"]}
    print("wrote %s" % OUT)
    print("  cycles %d | people %d | links %d"
          % (len(cycles), len(people), sum(len(c["nodes"]) for c in cycles)))
    if cycles:
        lens = [len(c["nodes"]) for c in cycles]
        print("  shortest %d | longest %d | direct pairs %d"
              % (min(lens), max(lens), sum(1 for l in lens if l == 2)))


if __name__ == "__main__":
    main()
