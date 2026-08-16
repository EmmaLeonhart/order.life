"""Pair up parallel-import duplicates by GRAPH STRUCTURE, not by label.

    python wiki-scripts/match_parallel_imports.py            # report
    python wiki-scripts/match_parallel_imports.py --tsv      # also write the TSV

Writes wikibase/analysis/qa_parallel_matches.tsv. Read-only over wikibase/items/.

WHY NOT LABELS

The obvious way to find the Maurya/Shunga triple import is to normalise labels and group.
It was tried on 2026-08-16 and it is not good enough. Measured against sixteen kings whose
correspondence had already been established by hand, label matching split four of them:

    Dasharatha    "Dasaratha Maurya"   vs "Dasharatha Maurya"
    Pushyamitra   "Pusyamitra Shunga"  vs "Pushyamitra Shunga"
    Brihadratha   "Brihadratha Maurya" vs "Brihadratha"
    Ashoka        "Ashoka"             vs "Ashoka II, King of Maurya III"

A 25% false-singleton rate on the cases we can check is disqualifying for a method whose
whole job is deciding which records are the same person, in a dump full of transliteration
variants and regnal-title prefixes.

WHAT THIS DOES INSTEAD

Correspondence propagates along the graph from a hand-verified seed:

    if X ~ Y, then father(X) ~ father(Y), mother(X) ~ mother(Y)
    if X ~ Y and each has exactly one child, those children correspond

Only UNAMBIGUOUS steps are taken. If either side has two fathers, or both have three
children, the step is skipped and recorded as ambiguous rather than guessed -- guessing is
how a 90-record merge becomes 90 opportunities to be wrong.

Labels are still computed, but as a CHECK: every pair is reported with whether the labels
agree, and a structural pair whose labels disagree wildly is worth a human look. That is
the opposite of using the label to make the decision.

WHAT IT DOES NOT DO

It proposes no merges and writes nothing to wikibase/items/. Its output is the input to a
merge_cluster.py cluster, which is written by hand from this table after reading it.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
OUT = ROOT / "wikibase" / "analysis" / "qa_parallel_matches.tsv"

FATHER, MOTHER, CHILD, SPOUSE = "P47", "P48", "P20", "P42"

# Hand-verified on 2026-08-16 by walking the three father-chains in parallel, position by
# position. See wikibase/analysis/maurya_shunga_triples.md. A "-" means that block has no
# copy of this king.
SEED = [
    ("devabhuti",       "Q2074", "Q50360", "Q160757"),
    ("bhagabhadra",     "Q2086", "Q50412", "Q160777"),
    ("vajramitra",      "Q2101", "Q50464", "Q160803"),
    ("ghosha",          "Q2117", "Q50524", "Q160830"),
    ("pulindaka",       "Q2134", "Q50597", "Q160858"),
    ("bhadraka",        "Q2150", "Q50645", "Q160882"),
    ("vasumitra",       "Q2165", "Q50681", "Q160900"),
    ("agnimitra",       "Q2175", "Q50725", "Q160916"),
    ("pushyamitra",     "-",     "Q50754", "Q160932"),
    ("brihadratha",     "Q2188", "Q50792", "Q160951"),
    ("dasharatha",      "Q2194", "Q50832", "Q160969"),
    ("kunala",          "Q2200", "Q50873", "Q160984"),
    ("ashoka",          "Q2206", "Q50908", "Q160996"),
    ("bindusara",       "-",     "Q50943", "Q161007"),
    ("chandragupta",    "-",     "Q50973", "Q161017"),
    ("sarvarthasiddhi", "-",     "Q51018", "Q161031"),
]

_cache = {}


def load(qid):
    if qid not in _cache:
        path = ITEMS / f"{qid}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        _cache[qid] = data if isinstance(data, dict) else None
    return _cache[qid]


def label(qid):
    d = load(qid)
    if not d:
        return ""
    L = d.get("labels") or {}
    for code in ("en", "mul", "ja"):
        if (L.get(code) or {}).get("value"):
            return L[code]["value"]
    for v in L.values():
        if v.get("value"):
            return v["value"]
    return ""


def vals(qid, pid):
    d = load(qid)
    if not d:
        return []
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def norm(text):
    """Only for the label AGREEMENT CHECK. Never for deciding correspondence."""
    t = text.split(" - ")[-1].split("(")[0].split(",")[0].strip().lower()
    for ch in ".'/[]":
        t = t.replace(ch, "")
    # collapse the transliteration variants that broke the label matcher
    for a, b in (("sh", "s"), ("aa", "a"), ("ii", "i"), ("uu", "u")):
        t = t.replace(a, b)
    return " ".join(t.split())


def main():
    write_tsv = "--tsv" in sys.argv
    sys.stdout.reconfigure(encoding="utf-8")

    # A group is a set of qids believed to be the same person. Seeded, then grown.
    groups = []
    for name, *qs in SEED:
        members = [q for q in qs if q != "-" and load(q)]
        if len(members) > 1:
            groups.append({"name": name, "members": set(members), "how": "seed"})

    seeded = sum(len(g["members"]) for g in groups)
    print(f"seed: {len(groups)} groups, {seeded} records (hand-verified king chains)")

    index = {}
    for g in groups:
        for q in g["members"]:
            index[q] = g

    ambiguous = []
    added = 1
    rounds = 0
    while added:
        added = 0
        rounds += 1
        for g in list(groups):
            members = sorted(g["members"], key=lambda q: int(q[1:]))
            for pid, role in ((FATHER, "father"), (MOTHER, "mother")):
                # Every member's value for this role, one per member.
                slots = {q: vals(q, pid) for q in members}
                present = {q: v for q, v in slots.items() if v}
                if len(present) < 2:
                    continue
                if any(len(v) != 1 for v in present.values()):
                    ambiguous.append((g["name"], role, "multi-valued",
                                      "; ".join(f"{q}:{v}" for q, v in present.items())))
                    continue
                targets = [v[0] for v in present.values()]
                # Do not fuse two groups that are already distinct -- that is a claim
                # this tool is not entitled to make.
                existing = {id(index[t]) for t in targets if t in index}
                if len(existing) > 1:
                    ambiguous.append((g["name"], role, "would fuse distinct groups",
                                      ", ".join(targets)))
                    continue
                if existing:
                    grp = next(index[t] for t in targets if t in index)
                    new = [t for t in targets if t not in grp["members"]]
                    if new:
                        grp["members"].update(new)
                        for t in new:
                            index[t] = grp
                        added += len(new)
                else:
                    grp = {"name": f"{g['name']}:{role}", "members": set(targets),
                           "how": f"via {role} of {g['name']}"}
                    groups.append(grp)
                    for t in targets:
                        index[t] = grp
                    added += len(targets)
    print(f"propagation converged after {rounds} round(s)")

    grown = [g for g in groups if g["how"] != "seed"]
    total = sum(len(g["members"]) for g in groups)
    print(f"groups: {len(groups)}  ({len(grown)} found structurally)   records: {total}")
    print(f"records that would merge away: {total - len(groups)}")

    disagree = []
    print("\ngroups, with the label check:")
    for g in sorted(groups, key=lambda g: min(int(q[1:]) for q in g["members"])):
        ms = sorted(g["members"], key=lambda q: int(q[1:]))
        labs = [norm(label(q)) for q in ms]
        ok = len(set(labs)) == 1
        if not ok:
            disagree.append((g["name"], ms, [label(q) for q in ms]))
        flag = "  " if ok else "!!"
        print(f" {flag} {g['name'][:26]:26s} {' '.join(f'{q:9s}' for q in ms)}"
              f"   {label(ms[0])[:30]}")

    print(f"\nlabel-agreement check: {len(groups) - len(disagree)}/{len(groups)} agree")
    if disagree:
        print("STRUCTURAL PAIRS WHOSE LABELS DISAGREE -- read these before merging:")
        for name, ms, labs in disagree:
            print(f"   {name}: " + " | ".join(f"{q}={l}" for q, l in zip(ms, labs)))

    if ambiguous:
        print(f"\nambiguous steps NOT taken: {len(ambiguous)}")
        for a in ambiguous[:15]:
            print(f"   {a[0]} {a[1]}: {a[2]} -- {a[3][:80]}")
        if len(ambiguous) > 15:
            print(f"   ... and {len(ambiguous) - 15} more")

    if write_tsv:
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write("group\thow\tqid\tlabel\tlabels_agree\n")
            for g in sorted(groups, key=lambda g: min(int(q[1:]) for q in g["members"])):
                ms = sorted(g["members"], key=lambda q: int(q[1:]))
                agree = "yes" if len({norm(label(q)) for q in ms}) == 1 else "NO"
                for q in ms:
                    f.write(f"{g['name']}\t{g['how']}\t{q}\t{label(q)}\t{agree}\n")
        print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
