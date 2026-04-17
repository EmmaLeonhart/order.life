"""
Export the full Charlemagne → Adam ancestry as a formatted markdown document.
Each generation is a section. Stops at Adam (gen 80).
"""
import csv
import io
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
ANA = REPO / "wikibase" / "analysis"
OUT = ANA / "charlemagne_to_adam.md"

ADAM = "Q152973"

# Load data
persons = {}
with open(ANA / "persons.tsv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        persons[row["qid"]] = row

parents_map = defaultdict(set)
with open(ANA / "edges.tsv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        parents_map[row["child"]].add(row["parent"])

spouses = defaultdict(set)
with open(ANA / "spouses.tsv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        spouses[row["a"]].add(row["b"])
        spouses[row["b"]].add(row["a"])


def lab(q):
    return (persons.get(q, {}).get("label") or q).strip()

def birth_str(q):
    b = (persons.get(q, {}).get("birth") or "").strip()
    if not b:
        return ""
    # Parse: +0748-01-01T00:00:00Z -> 748 CE; -0005 -> 5 BCE
    try:
        year_part = b.split("-")[0] if b.startswith("+") else b.split("-")[0]
        if b.startswith("+"):
            year = int(b[1:].split("-")[0])
            return f"{year} CE" if year > 0 else ""
        elif b.startswith("-"):
            year = int(b[1:].split("-")[0])
            return f"{year} BCE" if year > 0 else ""
    except:
        pass
    return ""

def death_str(q):
    d = (persons.get(q, {}).get("death") or "").strip()
    if not d:
        return ""
    try:
        if d.startswith("+"):
            year = int(d[1:].split("-")[0])
            return f"{year} CE" if year > 0 else ""
        elif d.startswith("-"):
            year = int(d[1:].split("-")[0])
            return f"{year} BCE" if year > 0 else ""
    except:
        pass
    return ""

def wikidata(q):
    return (persons.get(q, {}).get("wikidata_qid") or "").strip()

# BFS from Charlemagne upward
current_gen = {"Q115039"}
visited = set()
gen_data = []

gen = 0
while current_gen and gen <= 80:
    gen_members = []
    next_gen = set()
    for q in sorted(current_gen):
        if q in visited:
            continue
        visited.add(q)
        gen_members.append(q)
        if q == ADAM:
            continue  # don't go past Adam
        for p in parents_map.get(q, set()):
            if p not in visited:
                next_gen.add(p)
    if gen_members:
        gen_data.append((gen, gen_members))
    current_gen = next_gen
    gen += 1

# Write markdown
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# West Eurasian Super-Network: Charlemagne to Adam\n\n")
    f.write("Full ancestry of Charlemagne (Q115039, b. 748 CE) traced backward\n")
    f.write(f"through {len(gen_data)} generations to Y-Chromosomal Adam (Q152973).\n\n")
    f.write(f"**Total unique ancestors: {len(visited)}**\n\n")
    f.write("Each generation lists all known ancestors at that depth.\n")
    f.write("QIDs refer to the Lifeism Wikibase (lifeism.miraheze.org).\n\n")
    f.write("---\n\n")

    for gen_num, members in gen_data:
        # Estimate era
        era = ""
        births = [birth_str(q) for q in members if birth_str(q)]
        if births:
            era = f" — circa {births[0]}"

        f.write(f"## Generation {gen_num} ({len(members)} people){era}\n\n")

        for q in members:
            name = lab(q)
            b = birth_str(q)
            d = death_str(q)
            wd = wikidata(q)
            sp = sorted(spouses.get(q, set()))

            line = f"- **{name}** ({q})"
            dates = []
            if b:
                dates.append(f"b. {b}")
            if d:
                dates.append(f"d. {d}")
            if dates:
                line += f" — {', '.join(dates)}"
            if wd:
                line += f" — [Wikidata {wd}](https://www.wikidata.org/wiki/{wd})"
            if sp:
                spouse_names = ", ".join(lab(s) for s in sp[:3])
                if len(sp) > 3:
                    spouse_names += f" +{len(sp)-3} more"
                line += f" ⚭ {spouse_names}"

            f.write(line + "\n")

        f.write("\n")

    # Epilogue
    f.write("---\n\n")
    f.write("## Below Adam\n\n")
    f.write("The graph continues below Adam through:\n")
    f.write("- **Gens 81–90**: Homo sapiens → Australopithecus (evolutionary phylogeny)\n")
    f.write("- **Gens 80–130**: Iranic Ancestors (55 numbered placeholder generations), ")
    f.write("Hittite Ancestors (50 numbered generations), pre-dynastic Egyptian pharaohs ")
    f.write("(Iry-Hor, Scorpion I/II, Ka), Akkadian/Sumerian kings (Gilgamesh, Enmerkar, Lugalbanda), ")
    f.write("banu Numidia chain\n")
    f.write("- **Gens 130–211**: Gaiad cosmogonic figures (LUCA, Gaia, Aster)\n\n")
    f.write("These are not included here as they belong to the pre-human Gaiad chapters (1–129).\n")

print(f"Wrote {OUT}")
print(f"Generations: {len(gen_data)}")
print(f"Unique ancestors: {len(visited)}")
