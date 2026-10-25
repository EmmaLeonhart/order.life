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
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_gedcom7 as g7
from chinese_names import chinese_name
from export_gedcom import SEX_FEMALE, SEX_MALE, load
from export_gedcom7 import clean_name, name_lines
from monarch_names import build as build_monarch_names
from neo_kunyomi import kanji_for

ANA = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"


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
            hn, gloss, kind = self.horus[qid]
            name(hn, f"Horus name ({kind}): {gloss}", "Horus names")
        if qid in self.abrahamic:
            an, temple, why = self.abrahamic[qid]
            name(an, f"Abrahamic name, from the temple name {val(temple)} ({val(why)})", "Abrahamic names")
        nm = (row.get("gedcom") or "").replace("/", " ").strip() or (row.get("label") or "").strip()
        toks = nm.split()
        if toks and not clado and all(t in self.readings and self.readings[t][0] for t in toks):
            have = {lg for lg, _ in self.labels.get(qid, [])}
            for k, (lg, sep) in enumerate((("ja", "・"), ("zh", "·"), ("ko", " "))):
                parts = [self.readings[t][k] for t in toks]
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
