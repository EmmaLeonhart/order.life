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
  - a word that is a patronymic by form (namemodel's PATRONYMIC), in the given part or as a one-word surname, is a
    patronymic unless the father's recorded name carries the same word, which makes it an inherited surname
    (namemodel.patronymic_or_surname). A patronymic is matched against the patronymic items: the store's (kind
    patronymic), Wikidata's instances of Q110874 patronymic and Q1076664 matronymic, and every P5056 value on
    Wikidata, keeping the one whose live mul or en label is the written form exactly. An inherited surname in the
    surname slot is matched as a family name. Parts stay in written order;
  - a token takes an item only when exactly ONE item matches its form and usage. Between several given-name items
    with the same label the person's GEDCOM SEX chooses, as genealogy/scripts/resolve-ambiguous-names.py does: the
    one male (Q12308941) or female (Q11879590) given-name item for that sex; failing that, the one candidate left
    once the items of the other sex only are set aside (a unisex Q3409032 or plain Q202444 item); failing that, its
    second rule, the one left whose own mul label is the written form (Anna Q666578 over the Japanese Anna items,
    which carry the name only as an en label). Otherwise the person is skipped;
  - a person is skipped when any word is a particle before a name (ap, ben, bin and the rest), a title or
    placeholder (King, NN), a regnal numeral, a lower-case particle, or carries digits or punctuation: those are not
    given or family names, and one name item per usage forbids filling them with one;
  - a Roman name (namemodel.is_roman_name: a praenomen followed by a nomen-shaped word) is skipped: the genealogy
    repo gives Roman names no name items at all, since praenomen, nomen and cognomen are not given and family names.

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

Network: Wikidata wbgetentities (labels), 50 ids a request, and two SPARQL queries for the patronymic items. With a
cache path, labels and the patronymic item list are saved there and reused. Stdlib only.
"""
import gzip
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_composed_names import UA, compose, fetch  # noqa: E402

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
# genealogy/scripts/namemodel.py ROMAN_PRAENOMEN and ROMAN_NOMEN, copied.
ROMAN_PRAENOMEN = frozenset("""
    gaius caius marcus lucius publius quintus titus aulus gnaeus cnaeus decimus servius
    tiberius appius manius spurius numerius sextus kaeso caeso mamercus vibius statius salvius
""".split())
ROMAN_NOMEN = re.compile(r"(ius|ianus|inus|ulus|illa|ina)$", re.I)
WORD = re.compile(r"^[^\W\d_](?:[^\W\d_]|['’-](?=[^\W\d_]))*$")
GIVEN_CLASSES = {"Q202444", "Q12308941", "Q11879590", "Q3409032"}
MALE, FEMALE = "Q12308941", "Q11879590"
PATRONYMIC_QUERIES = (
    "SELECT DISTINCT ?i WHERE { VALUES ?c { wd:Q110874 wd:Q1076664 } ?i wdt:P31 ?c }",
    "SELECT DISTINCT ?i WHERE { ?s wdt:P5056 ?i }",
)
CJK_PHRASE = {"Chinese": "zh", "Japanese": "ja", "kun'yomi": "ja", "Korean": "ko"}


def word(tok):
    return bool(WORD.match(tok)) and not ROMAN.match(tok) and tok[0].isupper() \
        and tok.casefold() not in PARTICLES and tok.casefold() not in NOT_NAMES


def plain(tok):
    return word(tok) and not PATRONYMIC.match(tok)


def is_roman_name(tokens):
    """genealogy namemodel.is_roman_name: a praenomen followed by a nomen-shaped token."""
    return bool(tokens) and tokens[0].casefold().strip("().,") in ROMAN_PRAENOMEN \
        and any(ROMAN_NOMEN.search(t.strip("().,")) for t in tokens[1:])


def split_name(value, father=frozenset()):
    """[(token, usage)] in written order for a usable NAME value, usage given, patronymic or family; else None.
    `father` is the set of words in the father's recorded name, case folded."""
    value = " ".join(value.split())
    if "/" in value:
        m = re.match(r"^([^/]*)/([^/]*)/\s*$", value)
        if not m:
            return None
        given, surname = m.group(1).split(), " ".join(m.group(2).split())
        if not given:
            return None
    else:
        # No slashes is no surname: every word is in the given part, as in a GIVN field. Several plain words there
        # say nothing about which is a given name and which a family name, so only a single word counts, or words
        # where the patronymic is told by form ("Snorri Sturluson"), the way classify_fields reads a GIVN.
        given, surname = value.split(), ""
        if len(given) != 1 and not any(word(t) and PATRONYMIC.match(t) for t in given):
            return None
    if is_roman_name(given + surname.split()):
        return None
    out = []
    for t in given:
        if plain(t):
            out.append((t, "given"))
        elif word(t) and PATRONYMIC.match(t) and t.casefold() not in father:
            out.append((t, "patronymic"))
        else:
            return None
    if surname:
        ws = surname.split()
        if len(ws) == 1 and word(ws[0]) and PATRONYMIC.match(ws[0]):
            out.append((surname, "family" if surname.casefold() in father else "patronymic"))
        elif all(plain(w) or w.islower() for w in ws) and plain(ws[-1]) and ws[0].casefold() not in PARTICLES:
            out.append((surname, "family"))
        else:
            return None
    return out


def people(ged):
    """(refn, primary name, languages the record already has a form in, SEX, words of the father's name) for each
    person with no Wikidata id."""
    text = Path(ged).read_text(encoding="utf-8-sig").replace("\r", "")
    recs = re.split(r"\n(?=0 )", text)
    names, husband = {}, {}
    for rec in recs:
        head = rec.split("\n", 1)[0]
        if head.endswith(" INDI"):
            m = re.search(r"^1 NAME (.*)$", rec, re.M)
            names[head.split()[1]] = m.group(1) if m else ""
        elif head.endswith(" FAM"):
            m = re.search(r"^1 HUSB (@[^@]+@)$", rec, re.M)
            if m:
                husband[head.split()[1]] = m.group(1)
    out = []
    for rec in recs:
        lines = rec.split("\n")
        if not lines[0].endswith(" INDI") or any(re.match(r"^1 EXID Q\d+$", l) for l in lines):
            continue
        name = next((l[7:] for l in lines if l.startswith("1 NAME ")), "")
        refn = next((lines[i][7:] for i in range(len(lines) - 1)
                     if lines[i].startswith("1 REFN ") and lines[i + 1] == "2 TYPE Gaiad individual number"), "")
        sex = next((l[6:].strip() for l in lines if l.startswith("1 SEX ")), "")
        father = set()
        for l in lines:
            if l.startswith("1 FAMC "):
                father |= set(names.get(husband.get(l[7:].strip()), "").replace("/", " ").casefold().split())
        have = {l.split(" ", 2)[2] for l in lines if re.match(r"^\d+ LANG ", l)}
        for l in lines:
            if re.match(r"^\d+ PHRASE ", l):
                have |= {lg for w, lg in CJK_PHRASE.items() if w in l}
                m = re.match(r"^\d+ PHRASE ([a-z]{2,3}(?:-[a-z]+)?) name\b", l)
                if m:
                    have.add(m.group(1))
        if name and refn:
            out.append((refn, name, have, sex, frozenset(father)))
    return out


def sparql(query):
    url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/sparql-results+json"})
    rows = json.load(urllib.request.urlopen(req, timeout=300))["results"]["bindings"]
    ids = (r["i"]["value"].rsplit("/", 1)[1] for r in rows)
    return {q for q in ids if re.match(r"^Q\d+$", q)}


def choose_given(token, cands, sex, classes, labels):
    """The one given-name item for `token`, else None, by genealogy resolve-ambiguous-names.resolve: the candidate
    whose mul (else en) label is the token; among several, the person's sex first (the one item of that sex, else the
    one left once the other sex's items are set aside), then the one whose own mul label is the token."""
    def latin(q):
        return labels.get(q, {}).get("mul") or labels.get(q, {}).get("en") or ""
    exact = sorted(q for q in cands if latin(q) == token)
    if len(exact) <= 1:
        return exact[0] if exact else None
    pool = exact
    if sex in ("M", "F"):
        want, other = (MALE, FEMALE) if sex == "M" else (FEMALE, MALE)
        own = [q for q in exact if want in classes.get(q, set()) and other not in classes.get(q, set())]
        left = [q for q in exact if not (other in classes.get(q, set()) and want not in classes.get(q, set()))]
        pool = own or left
        if len(pool) == 1:
            return pool[0]
    same = [q for q in pool if labels.get(q, {}).get("mul") == token]
    return same[0] if len(same) == 1 else None


def main():
    ged, genealogy = sys.argv[1], Path(sys.argv[2])
    cache = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    persons = people(ged)
    usable = {r: s for r, n, _h, _x, fa in persons for s in [split_name(n, fa)] if s}
    print(f"{len(persons)} people with no Wikidata id; {len(usable)} have a name split into given names, "
          f"patronymics and family names")
    want = {u: {t for s in usable.values() for t, uu in s if uu == u} for u in ("given", "patronymic", "family")}

    folded = {}
    for t in want["given"] | want["patronymic"]:
        folded.setdefault(t.casefold(), set()).add(t)
    given_fold, patr_fold, classes = {}, {}, {}
    store_patr = set()
    with gzip.open(genealogy / "out" / "wikidata" / "name-items-in-store.tsv.gz", "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            qid, kinds, p31, labels = (line.rstrip("\n").split("\t") + ["", "", "", ""])[:4]
            kinds, p31 = set(kinds.split("|")), set(p31.split("|"))
            is_given = "given" in kinds and GIVEN_CLASSES & p31
            is_patr = "patronymic" in kinds
            if not (is_given or is_patr):
                continue
            if is_given:
                classes[qid] = p31
            if is_patr:
                store_patr.add(qid)
            for lb in set(labels.split("|")):
                if lb.casefold() in folded:
                    if is_given:
                        given_fold.setdefault(lb.casefold(), set()).add(qid)
                    if is_patr:
                        patr_fold.setdefault(lb.casefold(), set()).add(qid)
    given_cand = {t: given_fold.get(t.casefold(), set()) for t in want["given"]}
    family_cand = {}
    with gzip.open(genealogy / "out" / "wikidata" / "family-name-items-en.tsv.gz", "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            qid, en, desc = (line.rstrip("\n").split("\t") + ["", ""])[:3]
            if desc == "family name" and en in want["family"]:
                family_cand.setdefault(en, set()).add(qid)
    family_item = {t: next(iter(qs)) for t, qs in family_cand.items() if len(qs) == 1}

    stored = json.loads(cache.read_text(encoding="utf-8")) if cache and cache.exists() else {}
    if "labels" not in stored:                      # an older cache held the labels dict alone
        stored = {"labels": stored}
    labels = stored["labels"]
    if "patronymic_items" not in stored:
        stored["patronymic_items"] = sorted(set().union(*(sparql(q) for q in PATRONYMIC_QUERIES)),
                                            key=lambda q: int(q[1:]))
    patr_items = store_patr | set(stored["patronymic_items"])
    print(f"{len(patr_items)} patronymic items ({len(store_patr)} in the store, "
          f"{len(stored['patronymic_items'])} from Wikidata)")

    items = sorted({q for qs in given_cand.values() for q in qs} | set(family_item.values()) | patr_items,
                   key=lambda q: int(q[1:]))
    missing = [q for q in items if q not in labels]
    print(f"{len(want['given'])} given-name, {len(want['patronymic'])} patronymic and {len(want['family'])} "
          f"family-name forms; {len(items)} candidate items, {len(missing)} to fetch")
    if missing:
        got = fetch(missing, "labels")
        for q in missing:
            e = got.get(q)
            labels[q] = {lg: v.get("value", "") for lg, v in ((e or {}).get("labels") or {}).items()}
    if cache:
        cache.write_text(json.dumps(stored, ensure_ascii=False), encoding="utf-8")

    def latin(q):
        return labels.get(q, {}).get("mul") or labels.get(q, {}).get("en") or ""
    by_latin = {}
    for q in patr_items:
        by_latin.setdefault(latin(q), set()).add(q)
    patr_item = {t: next(iter(by_latin[t])) for t in want["patronymic"] if len(by_latin.get(t, ())) == 1}
    family_item = {t: q for t, q in family_item.items() if latin(q) == t}
    one_given = sum(1 for t, qs in given_cand.items() if len([q for q in qs if latin(q) == t]) == 1)
    several = sum(1 for t, qs in given_cand.items() if len([q for q in qs if latin(q) == t]) > 1)
    print(f"one item each: {one_given} of {len(want['given'])} given names ({several} more with several, "
          f"for the person's sex to choose), {len(patr_item)} of {len(want['patronymic'])} patronymics, "
          f"{len(family_item)} of {len(want['family'])} family names")

    rows, per_lang, reached = [], Counter(), Counter()
    for refn, _name, have, sex, _fa in persons:
        s = usable.get(refn)
        if not s:
            continue
        parts, by_sex = [], False
        for t, u in s:
            if u == "given":
                q = choose_given(t, given_cand.get(t, set()), sex, classes, labels)
                by_sex |= q is not None and len([c for c in given_cand.get(t, ()) if latin(c) == t]) > 1
            else:
                q = (patr_item if u == "patronymic" else family_item).get(t)
            if not q:
                break
            parts.append(q)
        else:
            reached["all"] += 1
            reached["by sex"] += by_sex
            reached["with a patronymic"] += any(u == "patronymic" for _t, u in s)
            whole = " ".join(t for t, _u in s)
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
    print(f"{reached['all']} people have one name item for every part of the name "
          f"({reached['by sex']} with a given name chosen by sex, {reached['with a patronymic']} with a patronymic)")
    people_rows = {r[0] for r in rows}
    print(f"{len(rows)} generated names for {len(people_rows)} people in {len(per_lang)} languages -> {OUT}")
    print("top languages: " + ", ".join(f"{lg} {n}" for lg, n in per_lang.most_common(15)))


if __name__ == "__main__":
    main()
