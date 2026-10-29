"""
Write the GEDCOM of one language directory's download zip from gaiad.ged. Emma, 2026-10-14: those versions "only contain
English, Japanese, Chinese, and then whatever ... other language the directory is in". So the English primary names, the
zh and ja forms and the sources' own original-script forms stay; Korean forms go (TRANs in ko, and the generated names
whose PHRASE is ko) unless the directory is Korean; and each person with a Wikidata id gets Wikidata's label in the
directory's language as a TRAN of the primary name (wikibase/analysis/wikidata_language_labels.tsv, from
make_language_labels.py), where it has one that is not already the English name. A person with no real label in that
language gets, where it exists, the name composed from their Wikidata name items in that language
(wikibase/analysis/composed_names.tsv, from make_composed_names.py) as its own NAME, marked generated in its PHRASE so
it stays apart from the real labels. A person with no Wikidata id gets, the same way, the name composed from the name
items matched to their written name (wikibase/analysis/matched_names.tsv, from make_matched_names.py), keyed on the
Gaiad individual number and applied only where the record's primary name is still the one the row was made from, with
its own PHRASE so it stays apart from the linked ones. Stdlib only; run in the site build.

    python wiki-scripts/language_gedcom.py <gaiad.ged> <lang> <out.ged>
"""
import re
import sys
from pathlib import Path

LABELS = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "wikidata_language_labels.tsv"
COMPOSED = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "composed_names.tsv"
MATCHED = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "matched_names.tsv"


def labels(lang):
    out = {}
    if LABELS.exists():
        for row in LABELS.read_text(encoding="utf-8").splitlines()[1:]:
            q, lg, lb = row.split("\t")
            if lg == lang:
                out[q] = lb
    return out


def composed(lang):
    """qid -> the generated name in `lang`, else in a regional variant of it (zh-hans before zh-hant and the rest)."""
    exact, variant = {}, {}
    if COMPOSED.exists():
        for row in COMPOSED.read_text(encoding="utf-8").splitlines()[1:]:
            q, lg, nm = row.split("\t")
            if lg == lang:
                exact[q] = nm
            elif lg.startswith(lang + "-") and (q not in variant or lg < variant[q][0]):
                variant[q] = (lg, nm)
    return {**{q: nm for q, (_lg, nm) in variant.items()}, **exact}


def matched(lang):
    """REFN -> (Latin name, generated name in `lang`, else in a regional variant of it), for people with no id."""
    exact, variant = {}, {}
    if MATCHED.exists():
        for row in MATCHED.read_text(encoding="utf-8").splitlines()[1:]:
            r, latin, lg, nm, _items = row.split("	")
            if lg == lang:
                exact[r] = (latin, nm)
            elif lg.startswith(lang + "-") and (r not in variant or lg < variant[r][0]):
                variant[r] = (lg, latin, nm)
    return {**{r: (latin, nm) for r, (_lg, latin, nm) in variant.items()}, **exact}


def blocks(lines, level):
    """Split lines into blocks starting at `level` (a block holds its deeper lines)."""
    out = []
    for l in lines:
        if l.startswith(f"{level} ") or not out:
            out.append([l])
        else:
            out[-1].append(l)
    return out


def drop_korean(lines):
    """Remove every TRAN (any level) whose LANG is ko, and every NAME whose PHRASE marks it Korean."""
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r"^(\d+) (TRAN|NAME) ", l)
        if m:
            lv = int(m.group(1))
            j = i + 1
            while j < len(lines) and lines[j][:1].isdigit() and int(lines[j].split(" ", 1)[0]) > lv:
                j += 1
            sub = lines[i + 1:j]
            korean = (m.group(2) == "TRAN" and f"{lv + 1} LANG ko" in sub) or \
                     (m.group(2) == "NAME" and any(re.match(rf"^{lv + 2} PHRASE ko\b", s) for s in sub))
            if korean:
                i = j
                continue
        out.append(l)
        i += 1
    return out


def main():
    src, lang, dest = sys.argv[1], sys.argv[2], sys.argv[3]
    table = labels(lang)
    gen = composed(lang)
    gen_m = matched(lang)
    text = Path(src).read_text(encoding="utf-8-sig").replace("\r", "")
    recs = blocks(text.split("\n"), 0)
    added = generated = by_match = 0
    out = []
    for rec in recs:
        if lang != "ko":
            rec = drop_korean(rec)
        if len(rec) > 1 and rec[0].endswith(" INDI"):
            qid = next((m.group(1) for l in rec for m in [re.match(r"^1 EXID (Q\d+)$", l)] if m), None)
            lb = table.get(qid) if qid else None
            parts = blocks(rec[1:], 1)
            pi = next((k for k, b in enumerate(parts) if b[0].startswith("1 NAME ")), None)
            if lb and pi is not None:
                primary = parts[pi]
                english = " ".join(primary[0][7:].replace("/", " ").split())
                has = any(l == f"3 LANG {lang}" for l in primary)
                if not has and " ".join(lb.split()) != english:
                    primary += [f"2 TRAN {lb}", f"3 LANG {lang}"]
                    added += 1
            nm = gen.get(qid) if qid and not lb else None
            how = "composed from its Wikidata name items"
            if not qid and pi is not None:
                refn = next((a[7:] for a, b in zip(rec, rec[1:])
                             if a.startswith("1 REFN ") and b == "2 TYPE Gaiad individual number"), None)
                latin, mnm = gen_m.get(refn, (None, None))
                if mnm and " ".join(parts[pi][0][7:].replace("/", " ").split()) == latin:
                    nm, how = mnm, "composed from name items matched to its written name"
            real = (f"3 LANG {lang}", f"3 PHRASE {lang} name")   # a real label already there, as TRAN or NAME
            if (nm and pi is not None and not any(l in real for b in parts for l in b)
                    and not any(l.endswith(f" {nm}") for b in parts for l in b)):
                parts.insert(pi + 1, [f"1 NAME {nm}", "2 TYPE OTHER", f"3 PHRASE {lang} name (generated: {how})"])
                generated += 1
                by_match += qid is None
            rec = [rec[0]] + [l for b in parts for l in b]
        out.extend(rec)
    # utf-8-sig: the BOM is the only encoding mark a GEDCOM 7 file has, and without it MyHeritage reads it as ANSI.
    Path(dest).write_text("\n".join(out), encoding="utf-8-sig")
    print(f"{lang}: {added} {lang} labels and {generated} generated {lang} names added "
          f"({by_match} of them from matched name items) -> {dest}")


if __name__ == "__main__":
    main()
