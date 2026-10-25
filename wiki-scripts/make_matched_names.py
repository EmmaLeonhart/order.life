"""
Write wikibase/analysis/matched_names.tsv: the gaiad.ged people with NO Wikidata id, each written in every language the
name items of their name are labelled in, composed the way make_composed_names.py composes them. Those people have no
P735/P734 statements to read, so the name items are found from the written name instead, the way the genealogy repo's
own pipelines find them (genealogy/scripts/namemodel.py `store_name_item` and `family_item_fits`):

  - the name is split on the GEDCOM slashes: the words before /surname/ are given names, one name item each; the
    surname is one family name item, whole ("von Ballenstedt" is one item, not two). A name with no slashes counts
    only when it is a single word (a given name); several words with no slashes say nothing about which is which,
    and the person is skipped;
  - a given name is matched against the given-name items (P31 Q202444, Q12308941, Q11879590, Q3409032) in the
    genealogy repo's offline store (out/wikidata/name-items-in-store.tsv.gz), then kept only when its live mul or
    en label is the written form exactly (so the Latin item, never the Hebrew or Cyrillic one for the same name);
  - a family name is matched only by its exact English label with the English description "family name"
    (out/wikidata/family-name-items-en.tsv.gz), the genealogy repo's rule for linking a surname;
  - a token takes an item only when exactly ONE item matches its form and usage; with none or several, the person is
    skipped. Nothing is chosen between candidates;
  - a person is skipped when any word is a patronymic by form (namemodel's PATRONYMIC, and the particles ap, ben,
    bin and the rest before a name), a title or placeholder (King, NN), a regnal numeral, a lower-case particle, or
    carries digits or punctuation:
    those are not given or family names, and one name item per usage forbids filling them with one.

Then each language is composed exactly as in make_composed_names.py (`compose`: every part labelled there, in the
right script, nothing transliterated; the parts' mul/en labels spell the name word for word). A language is skipped
where the record already carries a form in it (any LANG or a Chinese/Japanese/Korean NAME), and a row whose result is
the Latin name letter for letter is dropped.

These rows are kept apart from make_composed_names.py's: those come from name items the person's Wikidata item links,
these from name items matched to the written name. The key is the Gaiad individual number (REFN) with the Latin
name beside it: the numbering follows the tree walk and can shift between builds, so language_gedcom.py applies a row
only to the record whose REFN and primary name both match, and marks it "composed from name items matched to its
written name".

    python wiki-scripts/make_matched_names.py <gaiad.ged> <genealogy repo> [cache.json]

Network: Wikidata wbgetentities (labels), 50 ids a request. Stdlib only.
"""
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_composed_names import compose, fetch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wikibase" / "analysis" / "matched_names.tsv"

# genealogy/scripts/namemodel.py PATRONYMIC, copied (the site build cannot import that repo).
PATRONYMIC = re.compile(
    r".+?("
    r"sen|son|sson|søn|sønn|"
    r"datter|sdatter|dotter|sdotter|"
    r"d[oó]ttir|"
    r"s(?:dtr|d|dr|dt|dtt|dttr)|"
    r"npoika|ntyt[äa]r|"
    r"s?zoon|s?[dt]ochter|"
    r"[oe]vich|[oe]vna|[oe]vi[cć]|wicz|"
    r"[oe]vitch|slavich|(?<=[bdfgkmnprtvw])sz"
    r")\.?$", re.I)
PARTICLES = {"ap", "ab", "verch", "ferch", "ben", "bin", "ibn", "bint", "bat", "bar", "ua", "uí", "ní", "nic",
             "fitz", "mac", "mc"}
# A title or placeholder standing where a name should be ("King //") is not a given name (genealogy: a title is not a
# name), so it never takes the given-name item that happens to share its spelling.
NOT_NAMES = {"king", "queen", "prince", "princess", "lord", "lady", "sir", "saint", "st", "duke", "duchess", "count",
             "countess", "earl", "baron", "emperor", "empress", "pharaoh", "sultan", "shah", "khan", "chief", "unknown",
             "nn", "private", "infant", "son", "daughter", "mr", "mrs", "miss"}
ROMAN = re.compile(r"^[IVXLCDM]+$")
WORD = re.compile(r"^[^\W\d_](?:[^\W\d_]|['’-](?=[^\W\d_]))*$")
GIVEN_CLASSES = {"Q202444", "Q12308941", "Q11879590", "Q3409032"}
CJK_PHRASE = {"Chinese": "zh", "Japanese": "ja", "kun'yomi": "ja", "Korean": "ko"}


def plain(tok):
    return bool(WORD.match(tok)) and not ROMAN.match(tok) and tok[0].isupper() and not PATRONYMIC.match(tok) \
        and tok.casefold() not in PARTICLES and tok.casefold() not in NOT_NAMES


def split_name(value):
    """(given tokens, surname or '') for a usable NAME value, else None."""
    value = " ".join(value.split())
    if "/" in value:
        m = re.match(r"^([^/]*)/([^/]*)/\s*$", value)
        if not m:
            return None
        given, surname = m.group(1).split(), " ".join(m.group(2).split())
        if not given or (surname and not all(plain(w) or w.islower() for w in surname.split())) \
                or (surname and not plain(surname.split()[-1])) \
                or (surname and surname.split()[0].casefold() in PARTICLES):
            return None
    else:
        given, surname = value.split(), ""
        if len(given) != 1:
            return None
    if not all(plain(t) for t in given):
        return None
    return given, surname


def people(ged):
    text = Path(ged).read_text(encoding="utf-8-sig").replace("\r", "")
    out = []
    for rec in re.split(r"\n(?=0 )", text):
        lines = rec.split("\n")
        if not lines[0].endswith(" INDI") or any(re.match(r"^1 EXID Q\d+$", l) for l in lines):
            continue
        name = next((l[7:] for l in lines if l.startswith("1 NAME ")), "")
        refn = next((lines[i][7:] for i in range(len(lines) - 1)
                     if lines[i].startswith("1 REFN ") and lines[i + 1] == "2 TYPE Gaiad individual number"), "")
        have = {l.split(" ", 2)[2] for l in lines if re.match(r"^\d+ LANG ", l)}
        for l in lines:
            if re.match(r"^\d+ PHRASE ", l):
                have |= {lg for w, lg in CJK_PHRASE.items() if w in l}
                m = re.match(r"^\d+ PHRASE ([a-z]{2,3}(?:-[a-z]+)?) name\b", l)
                if m:
                    have.add(m.group(1))
        if name and refn:
            out.append((refn, name, have))
    return out


def main():
    ged, genealogy = sys.argv[1], Path(sys.argv[2])
    cache = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    persons = people(ged)
    split = {r: split_name(n) for r, n, _h in persons}
    usable = {r: s for r, s in split.items() if s}
    print(f"{len(persons)} people with no Wikidata id; {len(usable)} have a name split into given and family names")
    want_given = {t for g, _s in usable.values() for t in g}
    want_family = {s for _g, s in usable.values() if s}

    given_cand = {}                          # token -> store given-name items carrying it as a label (case folded)
    folded = {}
    for t in want_given:
        folded.setdefault(t.casefold(), set()).add(t)
    fold_cand = {}
    with gzip.open(genealogy / "out" / "wikidata" / "name-items-in-store.tsv.gz", "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            qid, kinds, p31, labels = (line.rstrip("\n").split("\t") + ["", "", "", ""])[:4]
            if "given" not in kinds.split("|") or not GIVEN_CLASSES & set(p31.split("|")):
                continue
            for lb in set(labels.split("|")):
                if lb.casefold() in folded:
                    fold_cand.setdefault(lb.casefold(), set()).add(qid)
    for f, ts in folded.items():
        for t in ts:
            given_cand[t] = fold_cand.get(f, set())
    family_cand = {}
    with gzip.open(genealogy / "out" / "wikidata" / "family-name-items-en.tsv.gz", "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            qid, en, desc = (line.rstrip("\n").split("\t") + ["", ""])[:3]
            if desc == "family name" and en in want_family:
                family_cand.setdefault(en, set()).add(qid)
    family_item = {t: next(iter(qs)) for t, qs in family_cand.items() if len(qs) == 1}

    items = sorted({q for qs in given_cand.values() for q in qs} | set(family_item.values()),
                   key=lambda q: int(q[1:]))
    if cache and cache.exists():
        labels = json.loads(cache.read_text(encoding="utf-8"))
    else:
        labels = {}
    missing = [q for q in items if q not in labels]
    print(f"{len(want_given)} given-name and {len(want_family)} family-name forms; "
          f"{len(items)} candidate items, {len(missing)} to fetch")
    if missing:
        got = fetch(missing, "labels")
        for q in missing:
            e = got.get(q)
            labels[q] = {lg: v.get("value", "") for lg, v in ((e or {}).get("labels") or {}).items()}
        if cache:
            cache.write_text(json.dumps(labels, ensure_ascii=False), encoding="utf-8")

    def latin(q):
        return labels.get(q, {}).get("mul") or labels.get(q, {}).get("en") or ""
    given_item = {}
    for t, qs in given_cand.items():
        exact = [q for q in qs if latin(q) == t]
        if len(exact) == 1:
            given_item[t] = exact[0]
    family_item = {t: q for t, q in family_item.items() if latin(q) == t}
    print(f"one item each: {len(given_item)} of {len(want_given)} given names, "
          f"{len(family_item)} of {len(want_family)} family names")

    rows, per_lang, reached = [], Counter(), 0
    for refn, _name, have in persons:
        s = usable.get(refn)
        if not s:
            continue
        given, surname = s
        if any(t not in given_item for t in given) or (surname and surname not in family_item):
            continue
        reached += 1
        parts = [given_item[t] for t in given] + ([family_item[surname]] if surname else [])
        whole = " ".join(given + ([surname] if surname else []))
        for lg in sorted({lg for p in parts for lg in labels.get(p, {})} - {"mul"}):
            if lg in have or lg.split("-")[0] in have:
                continue
            got = compose(parts, lg, labels, whole)
            if got and got.casefold() != whole.casefold() and "\t" not in got:
                rows.append((refn, whole, lg, got, " ".join(parts)))
                per_lang[lg] += 1
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("refn\tlatin\tlang\tname\tname_items\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"{reached} people have one name item for every part of the name")
    print(f"{len(rows)} generated names for {len({r[0] for r in rows})} people in {len(per_lang)} languages -> {OUT}")
    print("top languages: " + ", ".join(f"{lg} {n}" for lg, n in per_lang.most_common(15)))


if __name__ == "__main__":
    main()
