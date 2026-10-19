"""
Write wikibase/analysis/name_cjk_labels.tsv: the Chinese, Japanese and Korean form of every person's primary name in
gaiad.ged, made by the genealogy repo's own label composer, so gaiad.ged carries them as TRAN (Emma, 2026-10-17: "you
should have them because of the very source").

Nothing here reads a name itself. The composer is genealogy/scripts/build-garborg-day.py `label_in`: it drops
markers and estates, renders titles and places from cjk_titles.py (an unknown place is dropped, never transliterated),
reads epithets and regnal numbers, and transliterates through the repo's token table. Words the table lacks are added
first by the repo's own tools for growing it: extend-transliterations.py `_extend` (ja, zh) and
refresh-rule-transliterations.py `_ko` (ko). Run here, with the genealogy checkout beside order.life; the site build only reads the TSV.

    python wiki-scripts/make_cjk_name_labels.py [gaiad.ged]
"""
import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT.parent / "genealogy" / "scripts"
TAB, NL = chr(9), chr(10)
OUT = ROOT / "wikibase" / "analysis" / "name_cjk_labels.tsv"
SKIP_WORDS = ROOT / "wikibase" / "analysis" / "cjk_never_spelled_words.txt"
UNKNOWN_MARKERS = ROOT / "wikibase" / "analysis" / "unknown_name_markers.txt"
sys.path.insert(0, str(GEN))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, GEN / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def primary_names(ged, surnames=None):
    """Every person's primary name, plain; the /surname/ parts go into `surnames` when given."""
    out, want = [], False
    for line in open(ged, encoding="utf-8-sig"):
        if line.startswith("0 "):
            want = line.rstrip().endswith(" INDI")
        elif want and line.startswith("1 NAME "):
            out.append(" ".join(line[7:].replace("/", " ").split()))
            if surnames is not None:
                surnames.update(" ".join(m.split()) for m in re.findall(r"/([^/]+)/", line[7:]) if m.strip())
            want = False
    return out


def main(ged):
    surnames = set()
    names = sorted(set(n for n in primary_names(ged, surnames) if n) | surnames)   # surnames alone too, to mark them
    # Words the genealogy table lacks, added by its own tools: extend-transliterations `_extend` for ja/zh, then
    # refresh-rule-transliterations `_ko` for ko (label_in needs all three). Connectives (cjk_titles) never go in.
    ext = load("extend_transliterations", "extend-transliterations.py")
    rr = load("refresh_rule_transliterations", "refresh-rule-transliterations.py")
    cjk = load("cjk_titles", "cjk_titles.py")
    with open(ext.TABLE, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=TAB)
        fields, rows = reader.fieldnames, list(reader)
    have = {r["token"]: r for r in rows}
    need = {ext.clean_token(t).strip("-–") for n in names for t in n.split()}
    need = {t for t in need if t and t.casefold() not in ext.SKIP and t.casefold() not in ext.TITLES
            and not t.isdigit() and not cjk._CONNECTIVE_RE.fullmatch(t)}
    missing = sorted(t for t in need if t not in have)
    print(f"{len(names)} names, {len(need)} tokens, {len(missing)} not in the genealogy table")
    ext._extend(rows, have, missing, argparse.Namespace(dry_run=False, placeholders=False, two_hops=False))
    with open(ext.TABLE, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=TAB)
        fields, rows = reader.fieldnames, list(reader)
    new = set(missing)
    filled = 0
    for r in rows:
        if r["token"] in new and not (r.get("ko") or ""):
            r["ko"] = rr._ko(r["token"]) or ""
            filled += bool(r["ko"])
    with open(ext.TABLE, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=TAB, lineterminator=NL)
        w.writeheader()
        w.writerows(rows)
    print(f"{filled} new rows given ko by refresh-rule-transliterations._ko")
    # The genealogy repo's words that are never spelled out in CJK (connectives, titles, territorial openers, SKIP),
    # copied for build_gaiad_ged.py, which drops a word-by-word fallback reading of a name holding one.
    nm = load("namemodel", "namemodel.py")
    words = (set(ext.SKIP) | set(ext.TITLES) | set(re.findall(r"[a-z]+", cjk._CONNECTIVE))
             | set(nm.TITLE_WORDS) | set(nm.TITLE_CONNECTIVES) | set(nm.TERRITORIAL_OPENERS))
    with open(SKIP_WORDS, "w", encoding="utf-8", newline="\n") as f:
        f.write("# from genealogy: extend-transliterations SKIP and TITLES, cjk_titles._CONNECTIVE, namemodel TITLE_WORDS,\n"
                "# TITLE_CONNECTIVES and TERRITORIAL_OPENERS (written by make_cjk_name_labels.py)\n")
        f.writelines(w + "\n" for w in sorted(w.casefold() for w in words))
    print(f"{len(words)} never-spelled-out words -> {SKIP_WORDS}")
    # The genealogy repo's unknown-name markers (NN, "No Name", "Без име", ...), for build_gaiad_ged.py: a person whose
    # primary name is one gets no Chinese, Japanese or Korean form, as NN gets none.
    import labels
    markers = sorted(m.casefold() for m in labels.NARROW_MARKERS | labels.WORDS_MEANING_UNKNOWN)
    with open(UNKNOWN_MARKERS, "w", encoding="utf-8", newline="\n") as f:
        f.write("# from genealogy: labels.NARROW_MARKERS and WORDS_MEANING_UNKNOWN (written by make_cjk_name_labels.py)\n")
        f.writelines(m + "\n" for m in markers)
    print(f"{len(markers)} unknown-name markers -> {UNKNOWN_MARKERS}")
    bgd = load("build_garborg_day", "build-garborg-day.py")
    table = bgd.translit()
    done = 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("name\tja\tzh\tko\n")
        for n in names:
            ja, zh, ko = bgd.label_in(n, table)
            if ja and zh and ko:
                f.write(f"{n}\t{ja}\t{zh}\t{ko}\n")
                done += 1
    print(f"{done} of {len(names)} names with all three -> {OUT}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "scratch" / "gaiad-english.ged")
