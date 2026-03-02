#!/usr/bin/env python3
"""
Fix edge cases for genealogy files where names don't match exactly.
Also create missing character files.
"""

import json
import os

GENEALOGY_DIR = os.path.join(os.path.dirname(__file__), '..', 'genealogy')


def load(name):
    path = os.path.join(GENEALOGY_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f), path
    return None, None


def save(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def create_file(filename, name, chapters, father=None, mother=None, children=None, qid=None):
    path = os.path.join(GENEALOGY_DIR, f"{filename}.json")
    data = {
        "name": name,
        "chapters_mentioned_in": chapters,
        "father": father,
        "mother": mother,
        "children": children or [],
        "wiki_qid": qid
    }
    save(data, path)
    print(f"  Created {filename}.json")


def update_file(filename, **kwargs):
    data, path = load(filename)
    if not data:
        print(f"  WARNING: {filename}.json not found")
        return
    changed = False
    for key, value in kwargs.items():
        if key == 'children' and value:
            existing = set(data.get('children', []))
            merged = sorted(existing | set(value))
            if merged != sorted(data.get('children', [])):
                data['children'] = merged
                changed = True
        elif data.get(key) != value and value is not None:
            data[key] = value
            changed = True
    if changed:
        save(data, path)
        print(f"  Updated {filename}.json")


# ---- Create missing files ----
print("Creating missing character files...")

# Bios-Neos: son of Protea, married Plasma-Belle, father of Nectarius
create_file("bios-neos", "Bios-Neos", [20],
            father="Protea", children=["Nectarius"])

# Proto-One: son of Gravros and Mardöll
create_file("proto-one", "Proto-One", [19],
            father="Gravros", mother="Mardöll", children=["Proto-Two"])

# Proto-Two: son of Proto-One and Cellina
create_file("proto-two", "Proto-Two", [19],
            father="Proto-One", mother="Cellina", children=["Euka"])

# Nucleus the Second: son of Euka and Eve
create_file("nucleus-the-second", "Nucleus the Second", [19, 20],
            father="Euka", mother="Eve")

# Metazoa: son of Nectarius and Chlora (Ch20)
create_file("metazoa", "Metazoa", [20],
            father="Nectarius", mother="Chlora")

# Mycon: son of Nectarius and Chlora (Ch20)
create_file("mycon", "Mycon", [20],
            father="Nectarius", mother="Chlora")

# Protist: daughter of Nectarius and Chlora (Ch20)
create_file("protist", "Protist", [20],
            father="Nectarius", mother="Chlora")

# Paul: son of Thaumatus (Ch23)
create_file("paul", "Paul", [23],
            father="Thaumatus", children=["Paulinellus"])

# Segmentus: son of Annelon (Ch37)
create_file("segmentus", "Segmentus", [37],
            father="Annelon", children=["Pleistos", "Amphon"])

# Marattidus: son of Maratton (Ch56) - fix the existing misspelled file
update_file("maratidus", father="Maratton")

# ---- Fix parent references that point to "Proto" instead of specific forms ----
print("\nFixing edge case references...")

# Update Gravros children to include Proto-One
update_file("gravros", children=["Poxus", "Proto-One"])

# Update Protea children to include Bios-Neos
update_file("protea", children=["Chronos", "Bios-Neos"])

# Update Nectarius children to include Metazoa, Mycon, Protist
update_file("nectarius", children=["Metazoa", "Mycon", "Protist"])

# Update Euka children to include Nucleus the Second
update_file("euka", children=["Nucleus the Second"])

# Update Annelon children to include Segmentus
update_file("annelon", children=["Segmentus"])

# Update Thaumatus children to include Paul
update_file("thaumatus", children=["Paul"])

# Update Paulinellus father to Paul
update_file("paulinellus", father="Paul")

# Update Maratton children to include Marattidus entry
update_file("maratton", children=["Leptos", "Maratidus"])

print("\nDone fixing edge cases!")
