"""
Rebuild Gaiad/genealogy/*.json from the entity resolution (step 3 of planning/entity-resolution.md).

Reads Gaiad/genealogy/_resolution.tsv (written by resolve_characters.py) and writes one file per tagged
name, in the shape build.py's character pages read (name, chapters_mentioned_in, father, mother, children,
wiki_qid), plus:
  qid           the order.life person, when every resolved tag of the name points to that one person
  wikidata_qid  that person's Wikidata id
  spouses       from spouses.tsv
  citations     every tag occurrence as {chapter, stanza, line}: Gaiad chapter.stanza, /gaiad/NNN/#sS
  people        when the name is shared by several people (or several candidates were left open): the
                QIDs it resolved to; such a file carries no family links, so different people are not
                merged under one name (parent repo, research/tagging-damage.md)
Kept from the old files: each file name (so /gaiad/characters/<name>/ stays) and any wiki_qid they carried.
Tags are never read for anything but this; nothing in the chapters is changed (Gaiad/TAGS.md).

    python Gaiad/scripts/regenerate_genealogy.py           # dry run: counts only
    python Gaiad/scripts/regenerate_genealogy.py --write

Stdlib only.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GEN = ROOT / "Gaiad" / "genealogy"
ANA = ROOT / "wikibase" / "analysis"


def slug(name):
    s = re.sub(r"[^a-zA-Z0-9_-]", "", name.replace(" ", "_")).lower()
    return s or "unknown"


def main(write):
    persons = {}
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            persons[r["qid"]] = r
    parents, children, spouses = defaultdict(list), defaultdict(list), defaultdict(list)
    with open(ANA / "edges.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            parents[r["child"]].append(r["parent"])
            children[r["parent"]].append(r["child"])
    with open(ANA / "spouses.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            spouses[r["a"]].append(r["b"])
            spouses[r["b"]].append(r["a"])

    old = {}
    for f in GEN.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            old[d.get("name")] = (f.name, d)
        except Exception:
            pass

    by_name = defaultdict(list)
    with open(GEN / "_resolution.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["method"] != "initial":
                by_name[r["name"]].append(r)

    def label(q):
        return (persons.get(q, {}).get("label") or q).strip()

    out, people_files, shared = {}, 0, 0
    for name, occ in by_name.items():
        resolved = {r["qid"] for r in occ if r["qid"]}
        open_cands = any(r["method"] == "unresolved" and r["candidates"] for r in occ)
        cites = [{"chapter": int(r["chapter"]), "stanza": int(r["stanza"]), "line": r["line"]} for r in occ]
        d = {"name": name,
             "chapters_mentioned_in": sorted({c["chapter"] for c in cites}),
             "father": None, "mother": None, "children": [], "spouses": [],
             "wiki_qid": None, "citations": cites}
        if len(resolved) == 1 and not open_cands:
            q = next(iter(resolved))
            p = persons.get(q, {})
            d["qid"] = q
            d["wikidata_qid"] = p.get("wikidata_qid") or None
            for pq in parents.get(q, []):
                key = "mother" if persons.get(pq, {}).get("sex") == "Q153719" else "father"
                if d[key] is None:
                    d[key] = label(pq)
            d["children"] = sorted({label(c) for c in children.get(q, [])})
            d["spouses"] = sorted({label(s) for s in spouses.get(q, [])})
            people_files += 1
        elif resolved:
            d["people"] = sorted(resolved, key=lambda x: int(x[1:]))
            shared += 1
        if name in old and old[name][1].get("wiki_qid"):
            d["wiki_qid"] = old[name][1]["wiki_qid"]
        fname = old[name][0] if name in old else slug(name) + ".json"
        out[fname] = d

    kept = set(out)
    dropped = [f for f, _ in old.values() if f not in kept]
    print(f"{len(out):,} files: {people_files:,} resolved to one person (with family), {shared:,} shared by "
          f"several people, {len(out) - people_files - shared:,} unresolved names (citations only)")
    print(f"old files {len(old):,}; old files with no tag left: {len(dropped):,} (kept as they are)")
    if write:
        for fname, d in out.items():
            (GEN / fname).write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
