"""
The per-person GEDCOM features built on 2026-10-15 for export_gedcom7.py, as one function the new /gaiad.ged build
(build_gaiad_ged.py) calls for every person who carries an order.life id. Emma, 2026-10-15: "a lot of that code here
needs to be linked in with the pipeline, and once it's linked in with the pipeline, then it should just generate."

For order.life person Q<n>, feature_lines() gives, each only where its rule produces something:
  names in zh/ja/ko from the item's own labels (wikibase/analysis/labels.tsv)
  neo-kun'yomi (neo_kunyomi.py), a generated Chinese name (chinese_names.py)
  temple, Horus and Abrahamic names (monarch_names.py)
  ja/zh/ko readings from the genealogy repo's token table (name_readings.tsv)
  patronymic and matronymic forms and lineage notes (canonical_line.tsv)
  the birth and death dates in the Gaian, Hebrew, Islamic and solar Hijri calendars
  links (order.life character page, Wikidata, Geni) and cladoplast FACTs (cladoplasts.tsv)
The helpers are export_gedcom7.py's, unchanged; only the loop that called them is here.
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_gedcom7 as g7
from chinese_names import chinese_name
from export_gedcom import SEX_FEMALE, SEX_MALE, clean_name, load, name_lines
from monarch_names import build as build_monarch_names
from neo_kunyomi import kanji_for

ANA = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"

# Words of a name that are not names (Emma, 2026-10-17: a single one of them was leaving 30,937 people with no
# Chinese, Japanese or Korean form at all). Placeholders are skipped; regnal numbers and titles are read as such.
PLACEHOLDERS = {"n.n.", "n.n", "nn", "unknown", "?", "(?)", "-", "–", "n", "nn.", "x"}
ROMAN = re.compile(r"^(?=[MDCLXVI])M{0,3}(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$")
KANJI_NUM = "〇一二三四五六七八九十"
NAME_TITLES = {"queen": ("女王", "女王", "여왕"), "king": ("王", "王", "왕"), "prince": ("王子", "王子", "왕자"),
               "princess": ("王女", "公主", "공주"), "duke": ("公", "公爵", "공작"), "duchess": ("公妃", "公爵夫人", "공작부인"),
               "count": ("伯", "伯爵", "백작"), "countess": ("伯妃", "伯爵夫人", "백작부인"), "emperor": ("皇帝", "皇帝", "황제"),
               "empress": ("皇后", "皇后", "황후"), "lord": ("卿", "勋爵", "경"), "lady": ("夫人", "夫人", "부인"),
               "saint": ("聖", "圣", "성"), "st.": ("聖", "圣", "성"), "of": ("の", "之", "의")}


def clean_name_token(t):
    """A name word with the punctuation a label drags in stripped (as genealogy's extend-transliterations.py)."""
    return (t or "").strip("\"'“”«»‘’()[]{}<>,;:.!?·•")


def _roman(s):
    vals, total, prev = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}, 0, 0
    for ch in reversed(s):
        v = vals[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def _kanji(n):
    if n <= 10:
        return KANJI_NUM[n]
    if n < 20:
        return "十" + KANJI_NUM[n - 10]
    if n < 100:
        return KANJI_NUM[n // 10] + "十" + (KANJI_NUM[n % 10] if n % 10 else "")
    return str(n)


def special_token(t):
    """'skip' for a placeholder, (ja, zh, ko) for a regnal number or a title, None for an ordinary name word."""
    low = t.casefold()
    if not t or low in PLACEHOLDERS or not any(ch.isalnum() for ch in t):
        return "skip"
    if ROMAN.match(t.rstrip(".,")) and t.rstrip(".,"):
        n = _roman(t.rstrip(".,"))
        return (f"{_kanji(n)}世", f"{_kanji(n)}世", f"{n}세")
    return NAME_TITLES.get(low)


class Features:
    def __init__(self):
        self.persons, _parents, _spouses, self.precision = load()
        self.sex_of = {q: "M" if r.get("sex") == SEX_MALE else "F" if r.get("sex") == SEX_FEMALE else "U"
                       for q, r in self.persons.items()}
        self.canon = g7.load_canonical_line()
        g7.load_gaiad_citations()   # fills g7.PAGE_NAME, the character page names
        self.cladoplasts = defaultdict(list)
        self.labels = defaultdict(list)
        for path, into, cols in ((ANA / "cladoplasts.tsv", self.cladoplasts, ("clade_wikidata", "clade_label")),
                                 (ANA / "labels.tsv", self.labels, ("lang", "label"))):
            if path.exists():
                with open(path, encoding="utf-8", newline="") as fh:
                    for r in csv.DictReader(fh, delimiter="\t"):
                        into[r["qid"]].append((r[cols[0]], r[cols[1]]))
        self.readings = g7.load_readings()
        minted = ANA / "name_readings_minted.tsv"   # words the hand table lacks, from mint_missing_readings.py
        if minted.exists():
            with open(minted, encoding="utf-8", newline="") as fh:
                for r in csv.DictReader(fh, delimiter="\t"):
                    self.readings.setdefault(r["token"], (r["ja"], r["zh"], r["ko"]))
        self.readings_ci = {}
        for t, v in self.readings.items():
            self.readings_ci.setdefault(t.casefold(), v)
        self.temple, self.horus, self.abrahamic = build_monarch_names()
        self.zh_taken = {lb for v in self.labels.values() for lg, lb in v if lg == "zh"}
        self.counts = Counter()

    def lines(self, qid):
        """GEDCOM lines (level 1 and below) for order.life person qid; [] for an id order.life does not hold."""
        row = self.persons.get(qid)
        if not row:
            return []
        out, c, val = [], self.counts, g7.val
        lang_of = g7.lang_of

        def name(text, phrase, key):
            out.extend([f"1 NAME {val(text)}", "2 TYPE OTHER", f"3 PHRASE {phrase}"])
            c[key] += 1

        names = name_lines(row.get("label", ""), row.get("gedcom", "")) or []
        for lg, lb in self.labels.get(qid, []):
            if lg in g7.PRIMARY_LANGS and lb not in names:
                name(lb, f"{lg} name", "labels zh/ja/ko")
        gv = g7.given_name(row)
        clado = qid in self.cladoplasts
        kj = kanji_for(gv) if gv and not clado else None
        if kj:
            name(kj, f"neo-kun'yomi (read {val(gv.split()[0])})", "neo-kun'yomi")
        if gv and not clado and not any(lg == "zh" for lg, _ in self.labels.get(qid, [])):
            ged = clean_name(row.get("gedcom") or "")
            sur = ged.split("/")[1].strip() if ged.count("/") >= 2 else ""
            zh = chinese_name(gv, sur, self.zh_taken) if sur and not lang_of(gv + sur) else None
            if zh:
                name(zh, "Chinese name (generated)", "Chinese names")
        if qid in self.temple:
            tn, why = self.temple[qid]
            name(tn, f"temple name (generated; {val(why)})", "temple names")
        if qid in self.horus:
            hn, gloss = self.horus[qid]
            name(hn, f"Horus name (generated): {gloss}", "Horus names")
        if qid in self.abrahamic:
            an, temple, why = self.abrahamic[qid]
            name(an, f"Abrahamic name, from the temple name {val(temple)} ({val(why)})", "Abrahamic names")
        nm = (row.get("gedcom") or "").replace("/", " ").strip() or (row.get("label") or "").strip()
        toks = []
        for t in nm.split():   # punctuation stripped, placeholders skipped, numbers and titles read as such
            t = clean_name_token(t) if not ROMAN.match(t.rstrip(".,")) else t.rstrip(".,")
            sp = special_token(t)
            if sp == "skip":
                continue
            toks.append(sp if sp else self.readings.get(t) or self.readings_ci.get(t.casefold()))
        if toks and not clado and all(r and r[0] for r in toks):
            have = {lg for lg, _ in self.labels.get(qid, [])}
            of = NAME_TITLES["of"]
            for k, (lg, sep) in enumerate((("ja", "・"), ("zh", "·"), ("ko", " "))):
                parts = [r[k] for r in toks]
                if of in toks and 0 < toks.index(of) < len(toks) - 1:   # "A of B" reads "B's A" in all three
                    i = toks.index(of)
                    left, right = [r[k] for r in toks[:i]], [r[k] for r in toks[i + 1:] if r is not of]
                    joint = {"ja": "の", "zh": "的", "ko": "의 "}[lg]
                    parts = [sep.join(right) + joint + sep.join(left)]
                if lg not in have and all(parts):
                    name(sep.join(parts), f"{lg} reading (transcription, not a "
                         f"{'Chinese name' if lg == 'zh' else 'native name'})", "readings")
        more, notes = g7.lineage_extras(qid, self.persons, self.sex_of, self.canon, self.labels)
        for n, phrase in g7.lineage_names(qid, self.persons, self.sex_of, self.canon) + more:
            name(n, phrase, "lineage names")
        for note in notes:
            out.append(f"1 NOTE {val(note)}")
            c["lineage notes"] += 1
        pb, pd = self.precision.get(qid, ("", ""))
        for what, col, prec in (("Birth", "birth", pb), ("Death", "death", pd)):
            note = g7.other_calendars((row.get(col) or "").strip(), prec) if row.get(col) else None
            if note:
                out.append(f"1 NOTE {what} in other calendars: {val(note)}")
                c["calendar notes"] += 1
        links = []
        page = g7.PAGE_NAME.get(qid)
        if page:
            import re
            slug = re.sub(r"[^a-zA-Z0-9_-]", "", page.replace(" ", "_")).lower()
            if slug:
                links.append(f"order.life https://order.life/gaiad/characters/{slug}/")
        wd = (row.get("wikidata_qid") or "").strip()
        if wd:
            links.append(f"Wikidata https://www.wikidata.org/wiki/{wd}")
        geni = (row.get("geni_id") or "").strip()
        if geni.isdigit():
            links.append(f"Geni https://www.geni.com/profile/index/{geni}")
        if links:
            out.append(f"1 NOTE Links: {'; '.join(links)}")
            c["link notes"] += 1
        for clade, clabel in self.cladoplasts.get(qid, []):
            out.extend([f"1 FACT {val(clabel or clade)}", "2 TYPE Cladoplast of",
                        f"2 NOTE Wikidata {clade}: https://www.wikidata.org/wiki/{clade}"])
            c["cladoplasts"] += 1
        if out:
            c["people with features"] += 1
        return out
