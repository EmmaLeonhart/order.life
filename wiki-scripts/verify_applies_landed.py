"""Every repair the apply_*.py scripts declare is actually in edges.tsv -- or is not.

    python wiki-scripts/verify_applies_landed.py

Exits non-zero naming any repair whose edges do not match what its script claims to have
done. Read-only: it touches nothing, it only measures.

WHY THIS EXISTS

On 2026-08-07 apply_lepidus_cut.py removed the false Q72786 -> Q72615 edge, printed
"Verified: Q72615's father is Q144279 alone, on both sides of the edge", and removed
nothing. Q72786.json's P20 spelled the child Q72693 -- the qid merged away into Q72615 a
week earlier, which redirects.tsv still maps across. The drop compared raw qids and matched
nothing; the verify block compared raw qids too, so it saw nothing to complain about and
declared success. Both halves were wrong in the same direction, so the failure was silent
for eight days while queue.md and devlog.md recorded the repair as done.

A check written from the same premise as the operation it checks cannot catch that
operation. So this file deliberately does NOT reuse any script's own helpers, its own
notion of a claim, or its own spelling of a qid. It reads edges.tsv -- which
extract_genealogy.py writes AFTER resolving every redirect -- and asks the only question
that matters: is the edge in the graph, or is it not.

verify_cuts_landed.py already does this for cut_edges.py's declarative cut sets, and passes
on 35 edges across 22 cut sets. That is real evidence about the cut scripts and none at all
about the scripts that edit item files directly, because a no-op there leaves the dump
unchanged with the log claiming otherwise. This closes that gap.

WHAT IT CANNOT TELL YOU

Only that the graph matches the intent recorded here. Whether the intent was right is a
question for the record's sources and for narrative_spine.md, not for this file. It also
says nothing about spouse claims (spouses.tsv) or about non-genealogical properties.

Keep the table below in step with the scripts. An entry that drifts from its script is
worse than no entry, because it will pass while measuring the wrong thing.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "wikibase" / "analysis"

ABSENT, PRESENT = "absent", "present"

# (script, edge (parent, child), expectation, why)
EXPECTED = [
    ("apply_lepidus_cut.py", ("Q72786", "Q72615"), ABSENT,
     "Quintus's father is Q144279; wd Q3625112 lists exactly two children"),

    ("apply_esther_generation.py", ("Q88454", "Q90982"), ABSENT,
     "the elder Esther's mother cannot be her own daughter"),
    ("apply_esther_generation.py", ("Q88454", "Q88380"), ABSENT,
     "same false mother on the parallel import of the elder Esther"),

    ("apply_lleucu_generation.py", ("Q140681", "Q140643"), ABSENT,
     "Rhys c. 1200 cannot have a mother born c. 1370"),

    ("apply_divine_fathers.py", ("Q75039", "Q74991"), ABSENT,
     "Abas: Poseidon is the blessing; Ixion remains the father"),
    ("apply_divine_fathers.py", ("Q153726", "Q138545"), ABSENT,
     "Jesus: Yahweh is the blessing; Joseph and Pantera remain"),
    ("apply_divine_fathers.py", ("Q132482", "Q74991"), PRESENT,
     "the human father the divine-father rule requires to survive"),
    ("apply_divine_fathers.py", ("Q137751", "Q138545"), PRESENT,
     "likewise -- the rule only cuts where a human father remains"),

    ("apply_mentuhotep_queen.py", ("Q85500", "Q85478"), ABSENT,
     "Queen Mentuhotep was a king's wife, not a king's mother"),
    ("apply_mentuhotep_queen.py", ("Q85500", "Q85578"), ABSENT,
     "likewise"),
    ("apply_mentuhotep_queen.py", ("Q85500", "Q195101"), ABSENT,
     "likewise, parallel import"),
    ("apply_mentuhotep_queen.py", ("Q85500", "Q195202"), ABSENT,
     "likewise, parallel import"),
    ("apply_mentuhotep_queen.py", ("Q85514", "Q85500"), PRESENT,
     "Senebhenaf, her attested father, is kept"),

    ("apply_servilii_chain.py", ("Q73332", "Q73170"), ABSENT,
     "the chain's end was tied back to its start, seven links below"),

    ("apply_tereza_eriz.py", ("Q79537", "Q79618"), ABSENT,
     "Estevao Soares c. 1325 cannot father a woman of c. 920"),
    ("apply_tereza_eriz.py", ("Q100140", "Q79618"), PRESENT,
     "Ero Fernandez de Lugo, d. c. 926, is the father the repair wired"),

    ("apply_mamercus_biological_father.py", ("Q72798", "Q72786"), PRESENT,
     "Mamercus was born a Livius Drusus -- biological father, added not replacing"),
    ("apply_mamercus_biological_father.py", ("Q73011", "Q72786"), PRESENT,
     "the adoptive father stays; CLAUDE.md case 2 keeps both"),

    ("apply_sunita_mrityu.py", ("Q2035", "Q153444"), ABSENT,
     "Sunitha's father is Mrityu, not Yama -- first copy"),
    ("apply_sunita_mrityu.py", ("Q50072", "Q153444"), ABSENT,
     "Shyamala is Yama's wife and came with the same conflation"),
    ("apply_sunita_mrityu.py", ("Q200020", "Q153444"), PRESENT,
     "Mrityu, created by the repair, now holds the parentage"),
    ("apply_sunita_mrityu.py", ("Q160673", "Q160640"), ABSENT,
     "same repair, second copy -- both copies or the ring stands"),
    ("apply_sunita_mrityu.py", ("Q160674", "Q160640"), ABSENT,
     "likewise"),
    ("apply_sunita_mrityu.py", ("Q200021", "Q160640"), PRESENT,
     "likewise"),
]


def redirects():
    out = {}
    with open(ANALYSIS / "redirects.tsv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["from_qid"]] = r["to_qid"]
    return out


def resolve(qid, red):
    seen = set()
    while qid in red and qid not in seen:
        seen.add(qid)
        qid = red[qid]
    return qid


def main():
    red = redirects()
    edges = set()
    with open(ANALYSIS / "edges.tsv", encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if len(row) >= 2:
                edges.add((row[0], row[1]))

    scripts = sorted({s for s, _, _, _ in EXPECTED})
    print(f"scripts covered: {len(scripts)}   assertions: {len(EXPECTED)}")

    bad = []
    for script, (parent, child), expect, why in EXPECTED:
        # Resolve the assertion the same way the extractor resolved the graph, or an
        # assertion written with a since-merged qid would silently never match.
        p, c = resolve(parent, red), resolve(child, red)
        found = (p, c) in edges
        ok = (found and expect == PRESENT) or (not found and expect == ABSENT)
        if not ok:
            spelling = ""
            if (p, c) != (parent, child):
                spelling = f"  [resolved {parent}->{p}, {child}->{c}]"
            bad.append(f"{script}: expected {parent} -> {child} {expect}, "
                       f"found {'present' if found else 'absent'}{spelling}\n"
                       f"    {why}")

    if bad:
        print(f"\nFAIL: {len(bad)} of {len(EXPECTED)} assertion(s) do not match the graph:\n")
        for b in bad:
            print("  " + b)
        print("\nA repair that does not appear in edges.tsv did not happen, whatever its\n"
              "script printed. Check whether the claim is spelled under a redirect.")
        return 1

    print(f"\nPASS: all {len(EXPECTED)} declared repairs match edges.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
