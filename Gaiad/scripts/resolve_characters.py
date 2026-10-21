"""
Resolve every {{c|}} tag in the Gaiad to a person in the order.life genealogy. Changes nothing.

Step 1 of planning/entity-resolution.md. Reads each chapter's tags with their stanza number (the same
split build.py uses for the #sN anchors) and writes Gaiad/genealogy/_resolution.tsv: one row per tag
occurrence with the order.life QID chosen and the method. Tags and genealogy files are never touched
(Gaiad/TAGS.md: tags are data and are not changed).

Methods, in order:
  override   Gaiad/genealogy/_overrides.tsv: identifications the genealogy makes on purpose, which a label
             cannot show (Noah is the record labelled Shu-Ilishu, wikibase/analysis/patriarch_overlay.md)
  initial    a tag on a single letter (an initial, not a person): not resolved
  file       the QID an existing Gaiad/genealogy/<name>.json already carries (wiki_qid)
  unique     the name matches exactly one person's label or gedcom name in persons.tsv
  alias      no label or gedcom name matches, but persons have it as an English label or alias
             (wikibase/analysis/person_names.tsv, from build_person_names.py), and one of them is linked
             within two steps to the most other names resolved in the same chapter, outright (an alias alone
             is not enough: Sargon is Sargon II's alias, ch 146 is Sargon of Akkad). Not for a name with a
             digit (haplogroups such as E-V38), a name the verse also uses in lower case (life, ancestor), or
             a name the Gaiad also tags as a place or a people ({{p|}}, {{x|}}: Roman, Christian). Other
             languages' aliases are left out: they matched Minotaur to Haltern Hills and Aten to Athena.
             The person's label must share a word with the name (Esarhaddon -> "Esarhaddon, king of
             Assyria"), which keeps out the dump's stray aliases. A label "The X" also matches "X".
  context    several match; the one linked within two steps (parent, child, spouse) to the most other
             names already resolved in the same chapter wins, if it wins outright
  consensus  the name was settled by context in other chapters, always to the same person
  unresolved no match, or several with no outright winner (candidates listed)

    python Gaiad/scripts/resolve_characters.py

Stdlib only.
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EPIC = ROOT / "Gaiad" / "epic"
GEN = ROOT / "Gaiad" / "genealogy"
ANA = ROOT / "wikibase" / "analysis"
OUT = GEN / "_resolution.tsv"
OVERRIDES = GEN / "_overrides.tsv"
PERSON_NAMES = ANA / "person_names.tsv"
OTHER_TAG = re.compile(r"\{\{[px]\|(?:[^}|]*\|)?([^}|]+)\}\}")
TAG = re.compile(r"\{\{c\|(?:([^}|]*)\|)?([^}|]+)\}\}")
TITLE = re.compile(r"^#\s+(?:Chapter\s+\d+:\s*)?(.*)")


LABELS = {}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("/", " ")).strip().lower()


def load_people():
    by_name = defaultdict(set)
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            for n in (r["label"], r["gedcom"]):
                if n and n.strip():
                    by_name[norm(n)].add(r["qid"])
                    # "The Buddha" is also "Buddha"
                    if norm(n).startswith("the "):
                        by_name[norm(n)[4:]].add(r["qid"])
            LABELS[r["qid"]] = r["label"]
    nbr = defaultdict(set)
    for fname, a, b in (("edges.tsv", "parent", "child"), ("spouses.tsv", "a", "b")):
        with open(ANA / fname, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                nbr[r[a]].add(r[b])
                nbr[r[b]].add(r[a])
    return by_name, nbr


def load_aliases():
    by_alias = defaultdict(set)
    if PERSON_NAMES.exists():
        with open(PERSON_NAMES, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["lang"] in ("en", "mul"):
                    by_alias[norm(r["name"])].add(r["qid"])
    return by_alias


def alias_guard():
    """Names an alias may not resolve: the lower-case words and phrases of the verse, and the names tagged
    as places or peoples anywhere in it."""
    words, other, text = set(), set(), []
    for f in sorted(EPIC.glob("chapter_*.md")):
        raw = f.read_text(encoding="utf-8")
        other |= {norm(m.group(1)) for m in OTHER_TAG.finditer(raw)}
        plain = re.sub(r"\{\{[cpx]\|(?:[^}|]*\|)?([^}|]+)\}\}", r"\1", raw)
        text.append(plain)
        words |= set(re.findall(r"\b[a-z][a-z'-]*\b", plain))
    text = "\n".join(text)

    def guarded(name):
        k = norm(name)
        if re.search(r"\d", name) or k in other:
            return True
        parts = k.split()
        if not all(p in words for p in parts):
            return False
        return len(parts) == 1 or re.search(r"\b" + re.escape(k) + r"\b", text) is not None
    return guarded


def within_two(q, nbr):
    one = nbr.get(q, set())
    two = set().union(*(nbr.get(x, set()) for x in one)) if one else set()
    return (one | two) - {q}


def file_qids():
    out = {}
    for f in GEN.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        q = d.get("wiki_qid") or d.get("qid")
        if q and d.get("name"):
            out[norm(d["name"])] = q
    return out


def occurrences():
    for n in range(1, 365):
        f = EPIC / f"chapter_{n:03d}.md"
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8").replace("\r", "")
        m = TITLE.match(raw)
        body = raw[m.end():].lstrip("\n") if m else raw
        stanzas = [s.strip("\n") for s in re.split(r"\n\s*\n", body) if s.strip()]
        for si, st in enumerate(stanzas, 1):
            for line in st.split("\n"):
                for t in TAG.finditer(line):
                    plain = re.sub(r"\{\{[cpx]\|(?:[^}|]*\|)?([^}|]+)\}\}", r"\1", line).strip()
                    yield n, si, t.group(2).strip(), t.group(1) or "", plain


def main():
    by_name, nbr = load_people()
    by_alias = load_aliases()
    guarded = alias_guard()

    def alias_cands(name):
        k = norm(name)
        if k in by_name or not by_alias.get(k) or guarded(name):
            return set()
        # The person's own label must share a word with the name: the dump has stray aliases (Trajan on a
        # record labelled Andhra Pradesh, John VI Kantakouzenos on red squirrel).
        words = set(re.findall(r"\w+", k))
        return {q for q in by_alias[k] if words & set(re.findall(r"\w+", norm(LABELS.get(q, ""))))}
    fq = file_qids()
    over = {}
    if OVERRIDES.exists():
        with open(OVERRIDES, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="	"):
                over[norm(r["name"])] = r["qid"]
    occ = list(occurrences())
    first = {}
    for n, si, name, tid, line in occ:
        k = norm(name)
        if k in over:
            first[(n, k)] = (over[k], "override", "")
        elif len(name) == 1:
            first[(n, k)] = ("", "initial", "")
        elif k in fq:
            first[(n, k)] = (fq[k], "file", "")
        elif len(by_name.get(k, ())) == 1:
            first[(n, k)] = (next(iter(by_name[k])), "unique", "")
    # context pass for names with several candidates
    by_chapter = defaultdict(set)
    for (n, k), (q, _, _) in first.items():
        by_chapter[n].add(q)
    res = {}
    pending = []
    for n, si, name, tid, line in occ:
        k = norm(name)
        if (n, k) in first:
            res[(n, k)] = first[(n, k)]
            continue
        by_alias_only = k not in by_name
        cands = sorted(by_name.get(k, ()) or alias_cands(name), key=lambda q: int(q[1:]))
        # An alias, even a single one, must also be borne out by the chapter (Sargon is Sargon II's alias,
        # but ch 146 is Sargon of Akkad).
        if len(cands) > 1 or (by_alias_only and cands):
            scores = Counter({q: len(within_two(q, nbr) & by_chapter[n]) for q in cands})
            top = scores.most_common(2)
            if top[0][1] > 0 and (len(top) == 1 or top[0][1] > top[1][1]):
                res[(n, k)] = (top[0][0], "alias" if by_alias_only else "context", " ".join(cands))
                continue
        res[(n, k)] = ("", "unresolved", " ".join(cands))
        pending.append((n, k))
    # consensus: a name settled by context elsewhere, always to the same person
    settled = defaultdict(set)
    for (n, k), (q, m, _) in res.items():
        if m == "context":
            settled[k].add(q)
    for (n, k) in pending:
        if len(settled.get(k, ())) == 1 and res[(n, k)][1] == "unresolved":
            res[(n, k)] = (next(iter(settled[k])), "consensus", res[(n, k)][2])
    methods = Counter()
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["chapter", "stanza", "name", "tag_id", "qid", "method", "candidates", "line"])
        for n, si, name, tid, line in occ:
            q, m, c = res[(n, norm(name))]
            methods[m] += 1
            w.writerow([n, si, name, tid, q, m, c, line])
    names = {norm(o[2]) for o in occ}
    print(f"wrote {OUT.relative_to(ROOT)}: {len(occ):,} tag occurrences, {len(names):,} distinct names")
    for m, v in methods.most_common():
        print(f"  {m:10} {v:>7,}  ({100 * v / len(occ):.1f}%)")


if __name__ == "__main__":
    main()
