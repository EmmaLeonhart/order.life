"""Where do the ancestry cycles come from?

Read-only over wikibase/analysis/. Writes nothing. Every figure in
wikibase/analysis/cycle_origins.md is produced by this script.

    python wiki-scripts/cycle_origins.py

Sections:
  1. provenance    -- are cycle members GEDCOM/Geni/Wikidata-sourced, vs the dump baseline
  2. conventions   -- naming-convention enrichment inside cycles vs the dump
  3. duplicates    -- per-cycle duplicate-name signature
  4. rootcause     -- shared edges, and the minimum edge set that breaks all cycles
"""

import collections
import csv
import difflib
import re
import sys
from pathlib import Path

A = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"

PERSONS = {r["qid"]: r for r in csv.DictReader(open(A / "persons.tsv", encoding="utf-8"), delimiter="\t")}
PROPOSED = list(csv.DictReader(open(A / "qa_cycles_proposed.tsv", encoding="utf-8"), delimiter="\t"))

CONVENTIONS = [
    ("Roman repeating names", r"\b(Publius|Marcus|Lucius|Gaius|Quintus|Titus|Aemilius|Livius|Caecilius"
                              r"|Mucius|Claudius|Licinia|Scipio|Drusus|Lepidus|Metellus|Scaevola|Cornelia"
                              r"|Antonia|Annia)\b"),
    ("Iberian patronymic", r"\b(Ximenes|Soares|Nunes|Peres|Bai[aã]o|Mendes|Rodrigues|Gon[cç]al)"),
    ("Welsh patronymic", r"\b(ap|ab|ferch|verch)\b"),
    ("Arabic patronymic", r"\b(ibn|bin|bint)\b|\bal-"),
    ("CJK", r"[一-鿿]"),
]


def label(q):
    return (PERSONS.get(q) or {}).get("label") or "<no persons.tsv row>"


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", (s or "").lower())).strip()


def cycles():
    """Each cycle as a list of (parent, child) edges."""
    out = []
    for r in PROPOSED:
        chain = [x.strip() for x in r["chain_qids"].split("->")]
        out.append(list(zip(chain, chain[1:])))
    return out


def members():
    s = set()
    for c in cycles():
        for a, b in c:
            s.add(a)
            s.add(b)
    return s


def provenance():
    mem = [PERSONS[q] for q in members() if q in PERSONS]
    allp = list(PERSONS.values())

    def fill(rows, key):
        return 100.0 * sum(1 for r in rows if (r.get(key) or "").strip()) / len(rows)

    print(f"cycle members with a persons.tsv row: {len(mem)}   dump: {len(allp)}\n")
    print(f"{'field':16s}{'in cycles':>12s}{'in dump':>12s}{'enrichment':>12s}")
    for key in ("gedcom", "geni_id", "wikidata_qid"):
        a, b = fill(mem, key), fill(allp, key)
        print(f"{key:16s}{a:11.1f}%{b:11.1f}%{a / b:11.2f}x")


def conventions():
    mem = [label(q) for q in members() if q in PERSONS]
    allp = [r["label"] or "" for r in PERSONS.values()]
    print(f"{'convention':24s}{'in cycles':>12s}{'in dump':>12s}{'enrichment':>12s}")
    for name, pat in CONVENTIONS:
        rx = re.compile(pat)
        a = 100.0 * sum(1 for l in mem if rx.search(l)) / len(mem)
        b = 100.0 * sum(1 for l in allp if rx.search(l)) / len(allp)
        print(f"{name:24s}{a:11.1f}%{b:11.2f}%{(a / b if b else 0):11.1f}x")


def duplicates():
    sig = collections.Counter()
    for c in cycles():
        nodes = [a for a, _ in c]
        labs = {q: norm(label(q)) for q in nodes}
        wds = {q: (PERSONS.get(q) or {}).get("wikidata_qid") or "" for q in nodes}
        pairs = [(a, b) for i, a in enumerate(nodes) for b in nodes[i + 1:]]
        if any(wds[a] and wds[a] == wds[b] for a, b in pairs):
            sig["same wikidata_qid twice in the cycle"] += 1
        elif any(labs[a] and labs[a] == labs[b] for a, b in pairs):
            sig["identical label twice in the cycle"] += 1
        elif any(labs[a] and labs[b] and labs[a] != labs[b]
                 and difflib.SequenceMatcher(None, labs[a], labs[b]).ratio() >= 0.72 for a, b in pairs):
            sig["near-identical labels (>=0.72)"] += 1
        elif len(nodes) == 2:
            sig["2-cycle, no name overlap"] += 1
        else:
            sig["no duplicate signature"] += 1
    for k, v in sig.most_common():
        print(f"  {v:3d}  {k}")
    print(f"\n  cycle length distribution: {dict(sorted(collections.Counter(len(c) for c in cycles()).items()))}")


def rootcause():
    cs = cycles()
    freq = collections.Counter()
    for c in cs:
        for e in c:
            freq[e] += 1
    print(f"distinct edges inside cycles: {len(freq)}")
    print(f"edges appearing in more than one cycle: {sum(1 for v in freq.values() if v > 1)}\n")
    print("most-shared edges:")
    for (a, b), n in freq.most_common(8):
        print(f"  in {n:2d} cycles  {a:9s} {label(a)[:32]:34s} -> {b:9s} {label(b)[:32]}")

    # greedy minimum feedback arc set over the enumerated cycles
    remaining, chosen = [set(c) for c in cs], []
    while any(remaining):
        cnt = collections.Counter()
        for c in remaining:
            for e in c:
                cnt[e] += 1
        e = cnt.most_common(1)[0][0]
        chosen.append(e)
        remaining = [c for c in remaining if e not in c]
    print(f"\nminimum cut set: {len(chosen)} edges break all {len(cs)} cycles")
    for a, b in chosen:
        print(f"  {a:9s} {label(a)[:34]:36s} -> {b:9s} {label(b)[:34]}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for name, fn in (("1. PROVENANCE", provenance), ("2. NAMING CONVENTIONS", conventions),
                     ("3. DUPLICATE SIGNATURES", duplicates), ("4. ROOT CAUSE", rootcause)):
        print("=" * 74)
        print(name)
        print("=" * 74)
        fn()
        print()


if __name__ == "__main__":
    main()
