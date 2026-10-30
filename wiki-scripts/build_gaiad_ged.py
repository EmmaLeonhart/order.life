"""
Build /gaiad.ged: one GEDCOM, strictly from the text, then Emma's ancestry. Emma's specification, 2026-10-15.

  I1 Aster, I2 Emma Leonhart, I3 Andromeda   the first three, ceremonial order
  then every other individual                one per distinct {{c|...}} tag name, in order of first appearance
                                             in the Gaiad (chapter 1 onward, line by line). "Strictly text only":
                                             false positives are fine and there are no links among them; splits
                                             and merges come later, by UUIDs put into the tags.
  then Emma's ancestry                       the synoptic tree (every GEDCOM in the repo joined on exact ids)
                                             trimmed to her ancestors and every family any of them is in
                                             (Gaiad/ancestry/emma-ancestry.ged, from synoptic/trim_to_ancestors.py
                                             in the inochi-no-michikyo repo), appended with its families. Her own
                                             record resolves as I2, and order.life's Aster (REFN Q1) and Andromeda
                                             (REFN Q3) as I1 and I3, so her line joins through to them (Emma,
                                             2026-10-15: "plus ancestry from me to Andromeda. Oh, and Aster").
                                             F1 is Aster and Andromeda as husband and wife, with their children
                                             (Emma, 2026-10-17).
  feature lines (2026-10-17)                 text individuals: a source citation for every stanza the name is in,
                                             the first-named note in en/zh/ja/ko, and the order.life person's
                                             features where the entity resolution gives the name one id; ancestry:
                                             features for every order.life id, more ancestors joined on an exact
                                             Wikidata or Geni id, name-only readings and names from the record's own
                                             NAME, other-calendar notes for every exact date, and a Links note
                                             naming its Wikidata, FamilySearch and Geni ids.

    python wiki-scripts/build_gaiad_ged.py [out.ged]

Stdlib only.
"""
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPIC = ROOT / "Gaiad" / "epic"
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "emma-ancestry.ged"
TAG = re.compile(r"\{\{c\|(?:([^}|]*)\|)?([^}|]+)\}\}")   # {{c|<tag id>|Name}}
# Emma, 2026-10-29: "The ID indicates who they are." A text person is its tag ID, not its name: the same name under two
# IDs is two people (the star Rhodes 19 and the red algae king 90839), one ID under two names is one person.
LEGACY = ROOT / "wikibase" / "analysis" / "gaiad_legacy_numbers.tsv"
TITLE = re.compile(r"^#\s+(?:Chapter\s+\d+:\s*)?(.*)")
NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://order.life/gaiad/individual/")
# Emma, 2026-10-29: "Aster's last name is "Alpha" and Andromeda's last name is "Omega"" (the UIDs stay on the bare names).
FIRST = [("Aster", "Aster"), ("Emma Leonhart", "Emma /Leonhart/ 命玥"), ("Andromeda", "Andromeda")]
# Their surnames go in SURN only, not in the NAME line (Emma, 2026-10-29: "NAME Aster / Givn Aster / Surn Alpha").
FIRST_SURN = {"Aster": "Alpha", "Andromeda": "Omega"}
EMMA_NAMES = ["Emma 李命玥"]  # beside her primary name, Emma /Leonhart/ 命玥 (Emma, 2026-10-16)
# The primary name in other languages and scripts, as TRANs under the primary NAME (planning/name-schema.md, "Primary
# names"). Emma, 2026-10-17: "change Emma Leonhart's name to 이명월 in Korean. This is the primary name and the old one
# still stays as an alias". 이명월 is the Korean reading of 李命玥, which stays as her AKA.
# Emma, 2026-10-29: "Aster in Japanese is 宇元親神 / Andromeda is 宇末親神"; no reading of either is recorded, so by her
# word the surnames are "Alpha" and "Omega" in katakana.
PRIMARY_TRAN = {"Emma Leonhart": [("이명월", "ko")],
                "Aster": [("阿斯特尔", "zh"), ("宇元親神 /アルファ/", "ja"), ("아스터", "ko")],
                "Andromeda": [("安德洛墨達", "zh"), ("宇末親神 /オメガ/", "ja"), ("안드로메다", "ko")]}
FIRST_SEX = {"Aster": "M", "Emma Leonhart": "F", "Andromeda": "F"}  # Emma, 2026-10-16: "Aster has sex. M."
EMMA_FS = "PFR5-LDS"
ORDERLIFE_FIRST = {"Q1": "@I1@", "Q3": "@I3@"}  # order.life ids of Aster and Andromeda


def text_uids():
    """Tag ID -> the UID its row in the legacy table holds (each is the UID of that ID's own tag name)."""
    if not LEGACY.exists():
        return {}
    rows = [r.split("\t") for r in LEGACY.read_text(encoding="utf-8").split("\n")[1:] if r]
    return {r[0]: r[3] for r in rows if len(r) > 3 and r[1] == "text" and r[3]}


def appearances():
    """(tag id, name, chapter, stanza) for each distinct tag ID, in order of first appearance; a tag with no ID is
    keyed by its name."""
    seen, out = set(), []
    for n in range(1, 365):
        f = EPIC / f"chapter_{n:03d}.md"
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8").replace("\r", "")
        m = TITLE.match(raw)
        body = raw[m.end():].lstrip("\n") if m else raw
        for si, st in enumerate((s for s in re.split(r"\n\s*\n", body) if s.strip()), 1):
            for t in TAG.finditer(st):
                name = t.group(2).strip()
                key = (t.group(1) or "").strip() or name
                if name and key not in seen:
                    seen.add(key)
                    out.append((key, name, n, si))
    return out


FN = re.compile(r"[ \t]*\{\{fn\|[^{}]*\}\}")
MARKUP = re.compile(r"\{\{[a-z]\|(?:[^}|]*\|)?([^}|]+)\}\}")


def citations():
    """tag id -> [(chapter, stanza, line)], every stanza each tag ID occurs in, the line given without markup."""
    out = {}
    for n in range(1, 365):
        f = EPIC / f"chapter_{n:03d}.md"
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8").replace("\r", "")
        m = TITLE.match(raw)
        body = raw[m.end():].lstrip("\n") if m else raw
        for si, st in enumerate((s for s in re.split(r"\n\s*\n", body) if s.strip()), 1):
            rows = st.split("\n")
            for t in TAG.finditer(st):
                name = t.group(2).strip()
                key = (t.group(1) or "").strip() or name
                got = out.setdefault(key, [])
                if name and not (got and got[-1][:2] == (n, si)):
                    seg = " ".join(rows[st[:t.start()].count("\n"):st[:t.end()].count("\n") + 1])
                    got.append((n, si, " ".join(MARKUP.sub(r"\1", FN.sub("", seg)).split())))
    return out


def in_puranic_block(qid):
    """order.life's Q160xxx block, which is not to be used (Emma, 2026-08-18; order.life CLAUDE.md)."""
    return qid[1:].isdigit() and int(qid[1:]) // 1000 == 160


def resolved_names():
    """Tag name -> order.life qid, where Gaiad/genealogy/_resolution.tsv resolves every occurrence of it to one qid."""
    import csv
    path = ROOT / "Gaiad" / "genealogy" / "_resolution.tsv"
    by = {}
    if path.exists():
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["qid"]:
                    by.setdefault(" ".join(r["name"].split()), set()).add((r["qid"], r["method"]))
    out = {}
    for name, hits in by.items():
        qids = {q for q, _ in hits}
        if len(qids) == 1 and not in_puranic_block(next(iter(qids))):
            out[name] = (next(iter(qids)), sorted({m for _, m in hits}))
    return out


GED_MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


NEG_YEAR = re.compile(r"(?<![^ ])-(\d+)\b")


def bce_years(line):
    """A DATE line with each negative year ("ABT -500", "3 JUN -44") written as GEDCOM 7's "500 BCE".

    The ancestry file carries BC years as "-N" (exact_date reads them so). GEDCOM 7 has no negative years, and
    webtrees drops the sign: on 2026-10-25 its round trip turned 1,627 such dates into AD ones. A "1500-1510" range
    keeps its hyphen, since only a minus at the start of a word is a sign.
    """
    if not re.match(r"\d+ DATE ", line):
        return line
    return NEG_YEAR.sub(lambda m: f"{m.group(1)} BCE", line)


def exact_date(d):
    """(astronomical year, month, day) for an exact GEDCOM or ISO date ("20 OCT 1963", "1996-02-26"); else None."""
    d = d.strip()
    m = re.fullmatch(r"(\d{1,2}) ([A-Z]{3}) (\d{1,4})( BCE| B\.?C\.?)?", d)
    if m and m.group(2) in GED_MONTHS:
        y = int(m.group(3))
        return (1 - y if m.group(4) else y), GED_MONTHS.index(m.group(2)) + 1, int(m.group(1))
    m = re.fullmatch(r"(-?)(\d{3,4})-(\d\d)-(\d\d)", d)
    if m:
        y = int(m.group(2))
        return (1 - y if m.group(1) else y), int(m.group(3)), int(m.group(4))
    return None


def calendar_notes(lines):
    """Birth and death "in other calendars" notes for a record's exact BIRT and DEAT dates."""
    from calendars import calendar_note
    out = []
    for a, b in zip(lines, lines[1:]):
        for tag, what in (("1 BIRT", "Birth"), ("1 DEAT", "Death")):
            if a.startswith(tag) and b.startswith("2 DATE ") and not any(o.startswith(f"1 NOTE {what} ") for o in out):
                ymd = exact_date(b[7:])
                if ymd and ymd[0] != 0 and 1 <= ymd[1] <= 12 and 1 <= ymd[2] <= 31:
                    try:
                        out.append(f"1 NOTE {what} in other calendars: {calendar_note(*ymd)}")
                    except (ValueError, IndexError):
                        pass
    return out


EXID_LINKS = {"http://www.wikidata.org/entity/": ("Wikidata", "https://www.wikidata.org/wiki/"),
              "https://www.familysearch.org/tree/person/details/": ("FamilySearch",
                                                                    "https://www.familysearch.org/tree/person/details/"),
              "https://www.geni.com/profile/index/": ("Geni", "https://www.geni.com/profile/index/")}


ENGLISH_NAMES = Path(__file__).resolve().parent / "data" / "english_names.tsv"
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")
# Scripts genealogy/scripts/romanize_scripts.py reads into Latin (Cyrillic, Greek, Armenian, Hebrew, Arabic,
# Devanagari, Georgian, Ethiopic, Gothic, Kharosthi, Nabataean): a first NAME in one of them also gets an English
# primary with the original as TRAN.
OTHER_SCRIPT = re.compile(r"[Ͱ-ϿЀ-ӿ԰-֏֐-׿؀-ۿऀ-ॿ"
                          r"Ⴀ-ჿἀ-῿ሀ-፿"
                          "\U00010330-\U0001034f\U00010a00-\U00010a5f\U00010880-\U000108af]")
WIKIDATA_CJK = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "wikidata_cjk_labels.tsv"
_WDCJK = {}


def wikidata_cjk():
    """{qid: {lang: label}}: Wikidata's ja/zh/ko labels for people whose names are in other scripts."""
    if not _WDCJK and WIKIDATA_CJK.exists():
        for row in WIKIDATA_CJK.read_text(encoding="utf-8").splitlines()[1:]:
            q, ja, zh, ko = (row.split("	") + ["", "", ""])[:4]
            _WDCJK[q] = {k: v for k, v in (("ja", ja), ("zh", zh), ("ko", ko)) if v}
    return _WDCJK


def english_names():
    """{("name", original) or ("wikidata", qid): (english, lang)} from make_english_names.py's table."""
    out = {}
    if ENGLISH_NAMES.exists():
        for row in ENGLISH_NAMES.read_text(encoding="utf-8").splitlines():
            if row.startswith("#") or not row.strip():
                continue
            kind, key, en, lang = row.split("\t")[:4]
            out[(kind, key)] = (en, lang)
    return out


WIKIDATA_NAMES = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "wikidata_primary_names.tsv"
PLACEHOLDER = re.compile(r"^(nn|n\.n\.|unknown|unnamed|\?+|q\d+)(\s|$)", re.I)


def wikidata_names():
    """{qid: (label, family name)} from make_wikidata_primary_names.py."""
    out = {}
    if WIKIDATA_NAMES.exists():
        for row in WIKIDATA_NAMES.read_text(encoding="utf-8").splitlines()[1:]:
            q, label, fam = (row.split("\t") + ["", ""])[:3]
            out[q] = (label, fam)
    return out


def wikidata_first(lines, table):
    """The primary NAME is the person's Wikidata label (Emma, 2026-10-17: "Wikidata generally gives the better name"),
    with the surname marked from Wikidata's family name (P734), else from the longest surname the tree's own names
    mark that the label contains. The tree's former primary stays, as an AKA."""
    qid = next((m.group(1) for l in lines for m in [re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", l)] if m), None)
    hit = table.get(qid) if qid else None
    if not hit or not hit[0] or PLACEHOLDER.match(hit[0]):
        return lines, False
    label, fam = hit
    i = next((k for k, l in enumerate(lines) if l.startswith("1 NAME ")), None)
    if i is None:
        return lines, False
    surnames = [l[7:].strip() for l in lines if l.startswith("2 SURN ")]
    sur = None
    for cand in ([fam] if fam else []) + sorted(surnames, key=len, reverse=True):
        m = re.search(r"(?<!\w)" + re.escape(cand) + r"(?!\w)", label, re.I) if cand else None
        if m:
            sur = m
            break
    new_text = label if not sur else f"{label[:sur.start()]}/{sur.group(0)}/{label[sur.end():]}"
    new_text = " ".join(new_text.split())
    old = lines[i][7:].strip()
    if " ".join(old.replace("/", " ").split()) == " ".join(new_text.replace("/", " ").split()) and "/" in old:
        return lines, False   # the tree already has this name, with its surname marked
    j = i + 1
    while j < len(lines) and not lines[j].startswith(("0 ", "1 ")):
        j += 1
    old_block = [l for l in lines[i:j] if not l.startswith(("2 TRAN ", "3 LANG ", "3 SURN ", "3 GIVN "))]
    trans = []
    k = i + 1
    while k < j:   # the translations stay under the primary
        if lines[k].startswith("2 TRAN "):
            trans.append(lines[k])
            k += 1
            while k < j and lines[k].startswith("3 "):
                trans.append(lines[k])
                k += 1
            continue
        k += 1
    new = [f"1 NAME {new_text}"] + ([f"2 SURN {sur.group(0)}"] if sur else []) + trans
    aka = ["1 NAME " + old_block[0][7:], "2 TYPE AKA"] + [l for l in old_block[1:] if not l.startswith("2 TYPE")]
    out = lines[:i] + new + aka + lines[j:]
    # A later NAME that is now the same as the primary is a repeat, not another name.
    key = " ".join(new_text.replace("/", " ").split()).casefold()
    res, k = [], 0
    while k < len(out):
        if k > i and out[k].startswith("1 NAME ") and " ".join(out[k][7:].replace("/", " ").split()).casefold() == key:
            k += 1
            while k < len(out) and not out[k].startswith(("0 ", "1 ")):
                k += 1
            continue
        res.append(out[k])
        k += 1
    return res, True


def english_first(lines, table):
    """gaiad.ged is an English file (Emma, 2026-10-17): the first NAME is the English primary name, and a name in
    Chinese, Japanese or Korean script goes under it as a TRAN with its LANG ("cjk are all lesser things")."""
    i = next((k for k, l in enumerate(lines) if l.startswith("1 NAME ")), None)
    if i is None or not (CJK.search(lines[i]) or OTHER_SCRIPT.search(lines[i])):
        return lines, False
    orig = lines[i][7:].strip()
    qid = next((m.group(1) for l in lines for m in [re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", l)] if m), None)
    hit = (table.get(("wikidata", qid)) if qid else None) or table.get(("name", orig))
    if not hit:
        return lines, False
    en, lang = hit
    j = i + 1
    while j < len(lines) and not lines[j].startswith(("0 ", "1 ")):
        j += 1
    sub = [l for l in lines[i + 1:j] if not l.startswith(("2 SURN ", "2 GIVN "))]
    sur = re.search(r"/([^/]*)/", en)
    new = [f"1 NAME {en}"] + ([f"2 SURN {sur.group(1).strip()}"] if sur and sur.group(1).strip() else [])
    new += sub + [f"2 TRAN {orig}", f"3 LANG {lang}"]
    return lines[:i] + new + lines[j:], True


EMMA_NAME_BLOCK = [
    # Emma, 2026-10-17: the primary name with its Chinese, Japanese and Korean translations; the Japanese is the
    # katakana of her Wikidata item (Q140568870). The long name is her ceremonial neo-kun'yomi name, English in the
    # original ("I consider it to be originally English and the Japanese as a translation"), with the kanji as its TRAN.
    "1 NAME Emma /Leonhart/ 命玥", "2 GIVN Emma", "2 SURN Leonhart",
    "2 TRAN 李命玥", "3 LANG zh", "3 SURN 李", "3 GIVN 命玥",
    "2 TRAN エマ・レオンハート", "3 LANG ja",
    "2 TRAN 이명월", "3 LANG ko", "3 SURN 이", "3 GIVN 명월",
    "1 NAME Emma Himiko Helensdotter von Bureus Leonhart no Mikotodama", "2 TYPE OTHER",
    "3 PHRASE ceremonial neo-kun'yomi name", "2 TRAN 閻魔日巫女平連娘武李獅心命玥", "3 LANG ja",
]
CJK_LABELS = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "name_cjk_labels.tsv"
_CJK = {}


def cjk_labels():
    """{primary name: {lang: form}} from make_cjk_name_labels.py (the genealogy repo's label_in)."""
    if not _CJK and CJK_LABELS.exists():
        for row in CJK_LABELS.read_text(encoding="utf-8").splitlines()[1:]:
            name, ja, zh, ko = row.split("	")
            _CJK[name] = {"ja": ja, "zh": zh, "ko": ko}
    return _CJK


NEVER_SPELLED = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "cjk_never_spelled_words.txt"
_NEVER = set()


def spells_out(name):
    """Whether a name holds a word the genealogy repo never spells out in CJK (make_cjk_name_labels.py's list)."""
    if not _NEVER and NEVER_SPELLED.exists():
        _NEVER.update(l.strip() for l in NEVER_SPELLED.read_text(encoding="utf-8").splitlines()
                      if l.strip() and not l.startswith("#"))
    for w in re.split(r"[\s/,()]+", name):
        w = w.strip(".:;\"'")
        if w and w != "I" and w.casefold() in _NEVER:   # "I" is the numeral one, not Norwegian "i"
            return True
    return False


UNKNOWN_MARKERS = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "unknown_name_markers.txt"
_UNKNOWN = set()


def unnamed(name):
    """Whether a name holds one of the genealogy repo's unknown-name markers (NN, "No Name", "Без име"): such a person
    has no Chinese, Japanese or Korean form, not ノ・ナメ (make_cjk_name_labels.py writes the list)."""
    if not _UNKNOWN and UNKNOWN_MARKERS.exists():
        _UNKNOWN.update(l.strip() for l in UNKNOWN_MARKERS.read_text(encoding="utf-8").splitlines()
                        if l.strip() and not l.startswith("#"))
    text = " " + " ".join(name.replace("/", " ").casefold().split()) + " "
    return any(f" {m} " in text for m in _UNKNOWN) or any(w.strip(".,") in _UNKNOWN for w in text.split())


NAME_LANG = re.compile(r"^3 PHRASE (zh|ja|ko) (name|reading \()")


def mark_tran_surnames(primary):
    """Mark the surname inside each TRAN of a primary NAME and give it its pieces (Emma, 2026-10-17: "why it is you're
    not marking the surnames in the other languages"). The surname's own reading, from the same composer, is found at
    the end of the translation: ニルス・オルソン・オストレ・ボレ with Østre Bore read オストレ・ボレ becomes
    ニルス・オルソン・/オストレ・ボレ/, with 3 GIVN and 3 SURN."""
    sur = re.search(r"/([^/]+)/", primary[0][7:])
    if not sur:
        return primary
    reads = cjk_labels().get(" ".join(sur.group(1).split()))
    if not reads:
        return primary
    out, k = [], 0
    while k < len(primary):
        l = primary[k]
        if l.startswith("2 TRAN ") and k + 1 < len(primary) and primary[k + 1].startswith("3 LANG "):
            text, lang = l[7:].strip(), primary[k + 1][7:].strip()[:2]
            sub_end = k + 2
            while sub_end < len(primary) and primary[sub_end].startswith("3 "):
                sub_end += 1
            has_pieces = any(x.startswith(("3 SURN ", "3 GIVN ")) for x in primary[k + 2:sub_end])
            r = reads.get(lang)
            if r and "/" not in text and not has_pieces and text.endswith(r) and len(text) > len(r):
                given = text[: -len(r)]
                sep = given[-1] if given[-1] in "・· " else ""
                given = given.rstrip("・· ")
                if given:
                    out += [f"2 TRAN {given}{sep}/{r}/", primary[k + 1], f"3 GIVN {given}", f"3 SURN {r}"]
                    out += primary[k + 2:sub_end]
                    k = sub_end
                    continue
            # The surname's reading once inside the translation, a whole word, with a title or place after it
            # (콘라드 키르부륵 쿤트 for Conrad /Kyrburg/ Count), or the whole translation: marked where it stands.
            at = text.find(r) if r and "/" not in text and not has_pieces and text.count(r) == 1 else -1
            if at >= 0 and (at == 0 or text[at - 1] in "・· ") and (at + len(r) == len(text)
                                                                   or text[at + len(r)] in "・· "):
                given = text[:at].rstrip("・· ")
                out += [f"2 TRAN {text[:at]}/{r}/{text[at + len(r):]}", primary[k + 1]]
                out += ([f"3 GIVN {given}"] if given else []) + [f"3 SURN {r}"]
                out += primary[k + 2:sub_end]
                k = sub_end
                continue
        out.append(l)
        k += 1
    return out


def name_blocks_to_tran(body, emma=False):
    """gaiad.ged is an English file (Emma, 2026-10-17): one English primary NAME, with its given name, and the
    Chinese, Japanese and Korean forms under it as TRAN (one per language, a native name over a generated reading,
    with its name pieces). Other names (AKA, generated Chinese names, Horus and temple names, neo-kun'yomi) keep their
    own NAME lines."""
    blocks = []
    for l in body:
        if l.startswith("1 ") or not blocks:
            blocks.append([l])
        else:
            blocks[-1].append(l)
    if emma:
        rest = [b for b in blocks if not b[0].startswith("1 NAME ")]
        return EMMA_NAME_BLOCK + [l for b in rest for l in b]
    pi = next((k for k, b in enumerate(blocks) if b[0].startswith("1 NAME ")), None)
    if pi is None:
        return body
    primary = blocks[pi]
    text = primary[0][7:].strip()
    if not any(l.startswith("2 GIVN ") for l in primary):
        given = text.split("/")[0].strip()
        if given and "/" in text:
            primary.insert(1, f"2 GIVN {given}")
    for k in range(len(primary) - 1):   # a Han TRAN written with the Chinese name dot is Chinese, not "undetermined"
        if primary[k].startswith("2 TRAN ") and primary[k + 1] == "3 LANG und-Hani" and "·" in primary[k]:
            primary[k + 1] = "3 LANG zh"
    # A Han form of a name in Latin script is Chinese too: Japanese writes a foreign name in katakana and Korean in
    # Hangul, so 玛加丽塔 for Margareta, 阿佛列大帝 for Alfred the Great, can only be Chinese. The first one becomes the
    # zh TRAN where the record has no other Chinese form (one per language): not where the composer or Wikidata gives
    # one, since an und-Hani form is often a part of the name only (托尔斯特因 for Torstein /Heimnes/).
    qid0 = next((m.group(1) for l in body for m in [re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", l)] if m), None)
    other_zh = ((cjk_labels().get(" ".join(text.replace("/", " ").split())) or {}).get("zh")
                or (wikidata_cjk().get(qid0, {}) if qid0 else {}).get("zh"))
    if not CJK.search(text) and "3 LANG zh" not in primary and not other_zh:
        k = next((k for k in range(len(primary) - 1)
                  if primary[k].startswith("2 TRAN ") and primary[k + 1] == "3 LANG und-Hani"), None)
        if k is not None:
            primary[k + 1] = "3 LANG zh"
    have = {l[7:].strip()[:2] for l in primary if l.startswith("3 LANG ")}
    have_text = {l[7:].strip() for l in primary if l.startswith("2 TRAN ")}
    native, reading = {}, {}
    for k, b in enumerate(blocks):
        if k == pi or not b[0].startswith("1 NAME "):
            continue
        m = next((NAME_LANG.match(l) for l in b if NAME_LANG.match(l)), None)
        if m:
            (native if m.group(2) == "name" else reading).setdefault(m.group(1), k)
    drop = set()
    # "No Name", "Ukjent", "N.N." are markers, as NN is: no generated CJK form (ノ・ナメ, ウヒェント, ン・ン), not even
    # Wikidata's; a CJK name a source itself gives stays.
    marker = unnamed(text)
    composed = None if marker else cjk_labels().get(" ".join(text.replace("/", " ").split()))
    qid = next((m.group(1) for l in body for m in [re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", l)] if m), None)
    wd = wikidata_cjk().get(qid, {}) if qid and not marker else {}
    if marker:
        drop |= set(reading.values())
        reading = {}
    for lg in ("zh", "ja", "ko"):   # Wikidata's own label first (Emma: "try wikidata but then build readers")
        if lg not in native and lg not in have and wd.get(lg):
            primary += [f"2 TRAN {wd[lg]}", f"3 LANG {lg}"]
            have.add(lg)
            if lg in reading:
                drop.add(reading[lg])
    for lg in ("zh", "ja", "ko"):
        if lg not in native and composed and lg not in have:
            # The genealogy repo's label composer (make_cjk_name_labels.py) beats a generated token reading.
            primary += [f"2 TRAN {composed[lg]}", f"3 LANG {lg}"]
            have.add(lg)
            if lg in reading:
                drop.add(reading[lg])
            continue
        k = native.get(lg, reading.get(lg))
        if k is None:
            continue
        if lg not in native and spells_out(text):
            # A word-by-word reading of a name holding a connective, title or territorial word spells that word out
            # ("av Sudreim, heiress of" -> アヴ・スドレイム・ヘイレッス); by the genealogy repo's rule it is dropped.
            drop.add(k)
            continue
        t = blocks[k][0][7:].strip()
        if lg not in have and t not in have_text:
            primary += [f"2 TRAN {t}", f"3 LANG {lg}"]
            sur = re.search(r"/([^/]*)/", t)
            if sur and sur.group(1).strip():
                g = t.split("/")[0].strip()
                primary += ([f"3 GIVN {g}"] if g else []) + [f"3 SURN {sur.group(1).strip()}"]
            have.add(lg)
            drop.add(k)
        elif t in have_text or k in reading.values():
            drop.add(k)
        for kk in (reading.get(lg),):   # a generated reading beside a native name is not kept
            if kk is not None and kk != k and lg in have:
                drop.add(kk)
    blocks[pi] = mark_tran_surnames(primary)
    return [l for k, b in enumerate(blocks) if k not in drop for l in b]


def exids(lines):
    """[(type, value)] for a record's EXIDs."""
    return [(b[7:].strip(), a[7:].strip()) for a, b in zip(lines, lines[1:])
            if a.startswith("1 EXID ") and b.startswith("2 TYPE ")]


def with_links(lines):
    """The record's lines with one "Links:" note that also names its Wikidata, FamilySearch and Geni ids."""
    new = [f"{EXID_LINKS[t][0]} {EXID_LINKS[t][1]}{v}" for t, v in exids(lines) if t in EXID_LINKS]
    at = next((i for i, l in enumerate(lines) if l.startswith("1 NOTE Links: ")), None)
    have = lines[at][len("1 NOTE Links: "):].split("; ") if at is not None else []
    add = [l for l in new if l.split(" ", 1)[1] not in {h.split(" ", 1)[-1] for h in have} and l not in have]
    if not add:
        return lines
    note = "1 NOTE Links: " + "; ".join(have + list(dict.fromkeys(add)))
    return lines[:at] + [note] + lines[at + 1:] if at is not None else lines + [note]


def fam_children_in_order(lines):
    """A FAM record's lines with its CHIL lines (and anything under them) sorted by I-number, in the CHIL slots."""
    blocks, cur = [], None
    for l in lines:
        if l.startswith("1 "):
            cur = [l]
            blocks.append(cur)
        elif cur is not None:
            cur.append(l)
        else:
            blocks.append([l])
    num = lambda b: int(re.search(r"@I(\d+)@", b[0]).group(1)) if re.search(r"@I(\d+)@", b[0]) else 0
    kids = iter(sorted((b for b in blocks if b[0].startswith("1 CHIL ")), key=num))
    return [l for b in blocks for l in (next(kids) if b[0].startswith("1 CHIL ") else b)]


def current_identity(lines, persons):
    """An ancestry record with one order.life id takes that person's current Wikidata id and name from order.life.

    The ancestry file is cut from the synoptic tree, which joined an order.life export of 2026-09-30. Identities
    repaired in order.life after that (the 2026-10-11 import-collision repair, the four town records of 2026-10-20:
    Vicchio, Dompierre-sur-Mer, Scheibenberg and Benfeld, which were Simon I of Saarbrucken, Floris II of Holland,
    Eberhard I of Berg-Altena and Hermes) would otherwise stay wrong in the tree. The wrong id and its name are
    dropped, not kept as an AKA: they belong to someone (or something) else."""
    ol = [a[7:].strip() for a, b in zip(lines, lines[1:]) if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"]
    if len(ol) != 1:
        return lines, False
    row = persons.get(ol[0]) or {}
    right = (row.get("wikidata_qid") or "").strip()
    wd = [a[7:].strip() for a, b in zip(lines, lines[1:])
          if a.startswith("1 EXID ") and b.strip() == "2 TYPE http://www.wikidata.org/entity/"]
    if not right or not wd or right in wd or len(wd) != 1:
        return lines, False
    wrong = wd[0]
    out = [l.replace(f"1 EXID {wrong}", f"1 EXID {right}") if l.strip() == f"1 EXID {wrong}" else
           l.replace(f"wikidata.org/wiki/{wrong}", f"wikidata.org/wiki/{right}") for l in lines]
    name = (row.get("gedcom") or row.get("label") or "").strip()
    i = next((k for k, l in enumerate(out) if l.startswith("1 NAME ")), None)
    if name and i is not None:
        j = i + 1
        while j < len(out) and not out[j].startswith(("0 ", "1 ")):
            j += 1
        out[i:j] = [f"1 NAME {name}"]
    return out, True


def ancestry_records():
    """The ancestry file's level-0 records, as (xref, tag, [lines]), HEAD/TRLR/SUBM dropped."""
    recs, cur = [], None
    for line in ANCESTRY.read_text(encoding="utf-8-sig").replace("\r", "").split("\n"):
        if not line:
            continue
        if line.startswith("0 "):
            if cur:
                recs.append(cur)
            parts = line.split(" ", 2)
            cur = (parts[1], parts[2].strip() if len(parts) > 2 else "", []) if parts[1].startswith("@") else None
            continue
        if cur:
            cur[2].append(line)
    if cur:
        recs.append(cur)
    return [r for r in recs if r[1] in ("INDI", "FAM", "SOUR")]  # SOUR: the trees the citations point to


def aster_andromeda_family(recs, imap):
    """One family for Aster and Andromeda, as husband and wife, first among the families (so it is F1).

    Emma, 2026-10-17: they "currently are not displayed as being husband and wife in the family F1, and they should
    be. Instead, both of them are shown as single parents of Benzet." The ancestry file has each of them as a single
    parent of Benzette and the two as a childless couple; every family whose only parents are Aster and/or Andromeda
    becomes that one family, with all their children. Returns the new records and {dropped family: kept family}.
    """
    src = {v: k for k, v in imap.items() if v in ("@I1@", "@I3@")}
    if len(src) < 2:
        return recs, {}
    pair = {src["@I1@"], src["@I3@"]}
    hits = []
    for x, tag, lines in recs:
        if tag == "FAM":
            parents = {l[7:].strip() for l in lines if l.startswith(("1 HUSB ", "1 WIFE "))}
            if parents and parents <= pair:
                hits.append(x)
    if not hits:
        return recs, {}
    keep = hits[0]
    body = [f"1 HUSB {src['@I1@']}", f"1 WIFE {src['@I3@']}"]
    seen = set(body)
    by_x = {x: lines for x, tag, lines in recs if tag == "FAM"}
    for x in hits:
        skip = False
        for l in by_x[x]:
            if l.startswith("1 "):   # a level-1 line and the lines under it go together
                skip = l.startswith(("1 HUSB ", "1 WIFE ")) or (l.startswith("1 CHIL ") and l in seen)
                seen.add(l)
            if not skip:
                body.append(l)
    out, placed = [], False
    for r in recs:
        if r[1] == "FAM" and not placed:
            out.append((keep, "FAM", body))
            placed = True
        if r[1] != "FAM" or r[0] not in hits:
            out.append(r)
    return out, {x: keep for x in hits[1:]}


def birth_year(lines):
    """The year of a record's first BIRT DATE, BC negative; None if it has none."""
    for a, b in zip(lines, lines[1:]):
        if a.startswith("1 BIRT") and b.startswith("2 DATE "):
            d = b[7:]
            m = re.match(r"(\d{3,4})-\d\d", d.strip())
            nums = [m.group(1)] if m else re.findall(r"\d{3,4}", d) or re.findall(r"\d+", d)
            if nums:
                y = int(nums[-1] if not m else nums[0])
                return -y if re.search(r"B\.?C", d) else y
            return None
    return None


def walk_numbering(recs, imap, n):
    """Number the ancestry people and the families by the FamilySearch-style walk (planning/gaiad-ged-numbering.md).

    Emma, 2026-10-14: "family search style algorithm altogether"; her 2026-10-15 answers: "the FamilySearch walk
    replaces the spouse pass" and "each person's line in turn". For each person in individual order, the ones the
    walk numbers included: their spouse families, then their parents' family, then each generation above it, father's
    side before mother's. In each family the father, the mother, then the children oldest first get the next I-number
    if they have none; each family the next F-number. People the walk never reaches follow, in the file's order.
    imap holds the joined records (I1, I2, I3) and is extended; n is the last number used (the Gaiad's text block).
    """
    fams = {x: lines for x, tag, lines in recs if tag == "FAM"}
    years = {x: birth_year(lines) for x, tag, lines in recs if tag == "INDI"}
    husb, wife, chil, famc, fams_of = {}, {}, {}, {}, {}
    for f, lines in fams.items():
        kids = []
        for l in lines:
            p = l[7:].strip()
            if l.startswith("1 HUSB "):
                husb.setdefault(f, p)
                fams_of.setdefault(p, []).append(f)
            elif l.startswith("1 WIFE "):
                wife.setdefault(f, p)
                fams_of.setdefault(p, []).append(f)
            elif l.startswith("1 CHIL "):
                kids.append(p)
                famc.setdefault(p, []).append(f)
        dated = iter(sorted((k for k in kids if years.get(k) is not None), key=lambda k: years[k]))
        chil[f] = [next(dated) if years.get(k) is not None else k for k in kids]   # undated ones keep their place
    by_num = {int(v[2:-1]): k for k, v in imap.items()}
    fmap, climbed = {}, set()

    def number_person(p):
        nonlocal n
        if p not in imap:
            n += 1
            imap[p] = f"@I{n}@"
            by_num[n] = p

    def number_family(f):
        if f not in fmap:
            fmap[f] = f"@F{len(fmap) + 1}@"
            for p in [husb.get(f), wife.get(f)] + chil[f]:
                if p:
                    number_person(p)

    def walk(p):
        for f in fams_of.get(p, ()):
            number_family(f)
        frontier = list(famc.get(p, ()))
        while frontier:   # one generation at a time, father's side first
            nxt = []
            for f in frontier:
                number_family(f)
                if f in climbed:
                    continue
                climbed.add(f)
                for parent in (husb.get(f), wife.get(f)):
                    nxt.extend(famc.get(parent, ()) if parent else ())
            frontier = nxt

    i = 0
    order = [x for x, tag, _ in recs if tag == "INDI"]
    rest = iter(order)
    while True:
        i += 1
        if i > n:
            p = next((x for x in rest if x not in imap), None)   # the next person the walk has not reached
            if p is None:
                break
            number_person(p)
        p = by_num.get(i)
        if p:
            walk(p)
    for f in fams:   # families with no member reached (none expected: every family has a member)
        if f not in fmap:
            fmap[f] = f"@F{len(fmap) + 1}@"
    return imap, fmap, n


def build(out_path):
    w = []
    add = w.append
    stamp = datetime.now(timezone.utc)
    add("0 HEAD")
    add("1 GEDC")
    add("2 VERS 7.0")
    add("1 SOUR ORDERLIFE")
    add("2 NAME The Gaiad - order.life")
    add(f"1 DATE {stamp.day} {['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][stamp.month-1]} {stamp.year}")
    add("1 NOTE The individuals of the Gaiad in order of first appearance (I1 Aster, I2 Emma Leonhart, I3 Andromeda first),")
    add("2 CONT strictly from the text; then Emma Leonhart's ancestry from her family tree.")
    add("0 @S1@ SOUR")
    add("1 TITL The Gaiad")
    add("1 WWW https://order.life/gaiad/")

    apps = appearances()
    first_seen = {key: (ch, st) for key, name, ch, st in apps}
    key_of = {}
    for key, name, ch, st in apps:
        key_of.setdefault(name, key)
    uid_of = text_uids()
    n = 0
    # Every Gaiad figure has a SEX (Emma, 2026-10-16: "all of us actually have set sexes"): the three first ones as she
    # set them, the others as order.life's genealogy has the person of that name (U where it does not say or the name
    # is not one person there).
    recs = ancestry_records() if ANCESTRY.exists() else []
    feats = None
    if recs:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from gedcom_features import Features
        feats = Features()
    sex_by_label = {}
    if feats:
        seen_labels = {}
        for q, r in feats.persons.items():
            lb = (r.get("label") or "").strip()
            if lb:
                seen_labels.setdefault(lb, set()).add(feats.sex_of.get(q, "U"))
        sex_by_label = {lb: next(iter(s)) for lb, s in seen_labels.items() if len(s) == 1}
    cited = citations()
    resolved = resolved_names() if feats else {}
    n_resolved_text = [0]

    def indi(key, name, ged_name, where):
        nonlocal n
        n += 1
        add(f"0 @I{n}@ INDI")
        add(f"1 NAME {' '.join(ged_name.split())}")   # a tag wrapped across a line break is one name (UID unchanged)
        if ged_name.count("/") == 2 and ged_name.split("/")[1].strip():
            add(f"2 SURN {ged_name.split('/')[1].strip()}")
        if name in FIRST_SURN:
            add(f"2 GIVN {name}")
            add(f"2 SURN {FIRST_SURN[name]}")
        for text, lg in PRIMARY_TRAN.get(name, ()):
            add(f"2 TRAN {text}")
            add(f"3 LANG {lg}")
        # no SEX line where the sex is not known, not SEX U (Emma, 2026-10-29: marked unknown, a merged record's sex
        # "turns into conflicting data about the sex, rather than just it inherits the sex marker")
        sex = FIRST_SEX.get(name) or sex_by_label.get(name)
        if sex:
            add(f"1 SEX {sex}")
        add(f"1 REFN {n}")
        add("2 TYPE Gaiad individual number")
        add(f"1 UID {uid_of.get(key) or uuid.uuid5(NS, name)}")
        if where:
            ch, st = where
            cites = cited.get(key) or [(ch, st, "")]
            k = len(cites)
            many = f"; named in {k} stanzas" if k > 1 else ""
            add(f"1 NOTE First named in the Gaiad, chapter {ch} (https://order.life/gaiad/{ch:03d}/#s{st}){many}.")
            for lg, text in (("zh", f"在《盖亚德》中：首次出现于第{ch}章（Gaiad {ch}.{st}）；共有{k}节提及。"),
                             ("ja", f"『ガイアド』では：第{ch}章（Gaiad {ch}.{st}）に初出、{k}連で言及。"),
                             ("ko", f"《가이아드》에서: 제{ch}장(Gaiad {ch}.{st})에 처음 등장, {k}개 연에서 언급.")):
                add(f"2 TRAN {text}")
                add(f"3 LANG {lg}")
            for c_ch, c_st, line in cites:   # a citation for every stanza the name is in (Emma, 2026-10-14)
                add("1 SOUR @S1@")
                add(f"2 PAGE Gaiad {c_ch}.{c_st}")
                if line:
                    add("2 DATA")
                    add(f"3 TEXT {'@' + line if line.startswith('@') else line}")
                add(f"2 NOTE https://order.life/gaiad/{c_ch:03d}/#s{c_st}")
        # The person the project's entity resolution gives this name (every occurrence to one order.life id; never a
        # fuzzy match) lends the record its feature lines: names in other scripts, calendars, links, cladoplasts.
        hit = resolved.get(" ".join(name.split())) if feats and name not in FIRST_SEX else None
        if hit:
            q, methods = hit
            more = feats.lines(q)
            if more:
                add(f"1 NOTE Resolved to order.life {q} by the Gaiad's entity resolution ({', '.join(methods)}).")
                w.extend(more)
                n_resolved_text[0] += 1

    for name, ged in FIRST:
        indi(key_of.get(name, name), name, ged, first_seen.get(key_of.get(name, name)))
        if name == "Emma Leonhart":
            # Her own names (Emma, 2026-10-16): 閻魔日巫女平連娘武李獅心命玥 comes from her label; these two beside it.
            for other in EMMA_NAMES:
                add(f"1 NAME {other}")
                add("2 TYPE AKA")
    firsts = {key_of.get(f[0], f[0]) for f in FIRST}
    for key, name, ch, st in apps:
        if key not in firsts:
            indi(key, name, name, (ch, st))
    n_text = n

    # Emma's ancestry, renumbered after the text block; her record becomes I2, order.life's Aster and Andromeda I1, I3.

    def first_of(lines):
        if any(l.strip() in (f"1 EXID {EMMA_FS}", f"1 _FSFTID {EMMA_FS}") for l in lines):
            return "@I2@"
        for a, b in zip(lines, lines[1:]):
            if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life":
                hit = ORDERLIFE_FIRST.get(a[7:].strip())
                if hit:
                    return hit
        return None

    imap = {}
    for x, tag, lines in recs:
        if tag == "INDI":
            hit = first_of(lines)
            if hit and hit not in imap.values():
                imap[x] = hit
    recs, merged_into = aster_andromeda_family(recs, imap)
    imap, fmap, n = walk_numbering(recs, imap, n)
    nf = len(fmap)
    for x, into in merged_into.items():
        fmap[x] = fmap[into]
    # Records are written in number order: the numbers are the order (planning/gaiad-ged-numbering.md).
    num = lambda r: int((imap.get(r[0]) or fmap.get(r[0]) or "@X0@")[2:-1])
    recs = (sorted((r for r in recs if r[1] == "INDI"), key=num) + sorted((r for r in recs if r[1] == "FAM"), key=num)
            + [r for r in recs if r[1] not in ("INDI", "FAM")])
    ptr = re.compile(r"@[^@\s]+@")
    # The synoptic tree carries links on the FAM records only; give each person their FAMC/FAMS back.
    back = {}
    for x, tag, lines in recs:
        if tag == "FAM":
            for l in lines:
                if l.startswith(("1 HUSB ", "1 WIFE ", "1 CHIL ")):
                    kind = "FAMC" if l.startswith("1 CHIL ") else "FAMS"
                    back.setdefault(l[7:].strip(), []).append(f"1 {kind} {x}")
    # The per-person features (gedcom_features.py: readings, neo-kun'yomi, Chinese, temple, Horus and Abrahamic names,
    # lineage names, other calendars, links, cladoplasts) for everyone who carries an order.life id.
    # More of her ancestors joined to order.life, on an exact Wikidata or Geni id only: where exactly one order.life
    # person has the id, no other record already carries that person, and exactly one record would take them.
    joins = {}
    if feats:
        def olid(lines):
            return next((a[7:].strip() for a, b in zip(lines, lines[1:])
                         if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"), None)
        carried = {olid(lines) for _, tag, lines in recs if tag == "INDI"} - {None}
        by_wd, by_geni = {}, {}
        for q, r in feats.persons.items():
            for col, into in (("wikidata_qid", by_wd), ("geni_id", by_geni)):
                v = (r.get(col) or "").strip()
                if v:
                    into.setdefault(v, set()).add(q)
        wanted = {}
        for x, tag, lines in recs:
            if tag != "INDI" or olid(lines):
                continue
            ids = dict((t, v) for t, v in exids(lines))
            for t, index in (("http://www.wikidata.org/entity/", by_wd), ("https://www.geni.com/profile/index/", by_geni)):
                qs = index.get(ids.get(t, ""), set())
                if len(qs) == 1:
                    q = next(iter(qs))
                    if q not in carried and not in_puranic_block(q):
                        wanted.setdefault(q, []).append(x)
                    break
        joins = {xs[0]: q for q, xs in wanted.items() if len(xs) == 1}
    n_cal = n_fs = n_en = n_wd = n_ident = 0
    en_table = english_names()
    wd_table = wikidata_names()
    links = {}
    for x, tag, lines in recs:
        if tag == "INDI":
            have = {l.strip() for l in lines}
            lines = lines + [l for l in back.get(x, ()) if l not in have]
            if not any(l.startswith("1 SEX ") for l in lines):
                lines.append("1 SEX U")   # every person has a SEX; U where no source gives one
            if imap[x] not in ("@I1@", "@I2@", "@I3@"):   # those three have theirs already
                lines = lines + [f"1 REFN {imap[x][2:-1]}", "2 TYPE Gaiad individual number"]
            if x in joins:
                lines = lines + [f"1 REFN {joins[x]}", "2 TYPE order.life"]
            if feats:
                lines, done = current_identity(lines, feats.persons)
                n_ident += done
            if feats:
                qs = [a[7:].strip() for a, b in zip(lines, lines[1:])
                      if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"]
                if qs:   # a record can carry more than one order.life id; each gives its lines
                    for q in qs:
                        lines = lines + feats.lines(q)
                else:
                    # Name-only features (readings, neo-kun'yomi, a generated Chinese name) from the record's own
                    # NAME, as the 10-15 build gave her synoptic ancestors; nothing that needs an order.life id.
                    nm = next((l[7:].strip() for l in lines if l.startswith("1 NAME ")), "")
                    if nm:
                        pid = f"ancestry:{x}"
                        feats.persons[pid] = {"qid": pid, "label": " ".join(nm.replace("/", " ").split()), "gedcom": nm}
                        more = feats.lines(pid)
                        del feats.persons[pid]
                        # No generated reading in a language the tree already transcribes the name into.
                        tran = {"zh" if b[7:].strip().startswith(("zh", "und-Hani")) else b[7:].strip()[:2]
                                for a, b in zip(lines, lines[1:]) if a.startswith("2 TRAN ") and b.startswith("3 LANG ")}
                        blocks = []
                        for l in more:
                            if l.startswith("1 ") or not blocks:
                                blocks.append([l])
                            else:
                                blocks[-1].append(l)
                        for b in blocks:
                            ph = next((l for l in b if l.startswith("3 PHRASE ")), "")
                            if b[0].startswith("1 NAME ") and " reading (" in ph and ph[9:11] in tran:
                                feats.counts["readings"] -= 1
                            else:
                                lines = lines + b
                # Every exact date gets its other calendars, not only those order.life holds (Emma, 2026-10-12).
                cal = [c for c in calendar_notes(lines) if not any(l.startswith(c.split(":")[0]) for l in lines)]
                n_cal += len(cal)
                lines = lines + cal
                before = any("familysearch" in l for l in lines if l.startswith("1 NOTE Links: "))
                lines = with_links(lines)
                n_fs += not before and any("familysearch" in l for l in lines if l.startswith("1 NOTE Links: "))
            if imap[x] not in ("@I1@", "@I2@", "@I3@"):   # after the features, which read the original NAME
                lines, done = wikidata_first(lines, wd_table)
                n_wd += done
                lines, done = english_first(lines, en_table)
                n_en += done
        fixed = [ptr.sub(lambda m: imap.get(m.group(0)) or fmap.get(m.group(0)) or m.group(0), l) for l in lines]
        if tag == "INDI":   # a link to a family merged into F1 would otherwise appear twice
            fixed = [l for i, l in enumerate(fixed) if not l.startswith(("1 FAMC ", "1 FAMS ")) or l not in fixed[:i]]
        if tag == "FAM":   # children in the order the walk numbered them, oldest first
            fixed = fam_children_in_order(fixed)
        target = imap.get(x)
        if target in ("@I1@", "@I2@", "@I3@"):
            keep, prev = [], ""
            for l in fixed:   # family links, ids and citations, and the feature lines after the record's own
                if (l.startswith(("1 FAMC", "1 FAMS", "1 EXID", "1 SOUR @"))
                        or (l.startswith(("2 TYPE http", "2 PAGE ")) and prev.startswith(("1 EXID", "1 SOUR @")))
                        or keep and not l.startswith(("1 REFN", "2 TYPE order.life", "1 SEX"))):
                    keep.append(l)
                prev = l
            primary = {t for name, ged in FIRST if f"@I{FIRST.index((name, ged)) + 1}@" == target
                       for t, _ in PRIMARY_TRAN.get(name, ())}
            langs = {lg for name, ged in FIRST if f"@I{FIRST.index((name, ged)) + 1}@" == target
                     for _, lg in PRIMARY_TRAN.get(name, ())}
            if primary:   # a label that is already the primary name's TRAN is not repeated as another NAME, and a
                # name in a language the primary name already has a TRAN for gives way to it (Aster's plain アスター
                # beside her kami title, Emma 2026-10-29)
                blocks = []
                for l in keep:
                    if l.startswith("1 ") or not blocks:
                        blocks.append([l])
                    else:
                        blocks[-1].append(l)
                keep = [l for b in blocks
                        if not (b[0].startswith("1 NAME ") and (b[0][7:].strip() in primary
                                                                or any(f"3 PHRASE {lg} name" == x for lg in langs
                                                                       for x in b)))
                        for l in b]
            links[target] = keep
            continue
        add(f"0 {imap.get(x) or fmap.get(x) or x} {tag}")
        w.extend(fixed)
    # Graft the joined records' family links, ids and citations onto I1, I2, I3, at the end of each record (so a
    # NAME keeps its SURN and other parts directly under it).
    for target, fam_lines in links.items():
        if fam_lines:
            i = w.index(f"0 {target} INDI") + 1
            while i < len(w) and not w[i].startswith("0 "):
                i += 1
            w[i:i] = fam_lines
    # One English primary NAME per person, with the zh, ja and ko forms under it as TRAN.
    out, i = [], 0
    while i < len(w):
        out.append(w[i])
        if w[i].startswith("0 @I") and w[i].endswith(" INDI"):
            j = i + 1
            while j < len(w) and not w[j].startswith("0 "):
                j += 1
            out.extend(name_blocks_to_tran(w[i + 1:j], emma=w[i] == "0 @I2@ INDI"))
            i = j
            continue
        i += 1
    w[:] = [bce_years(line) for line in out]
    add("0 TRLR")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Gothic script for everyone (Emma, 2026-10-25: "applying Gothic as a standard label thing"; gothic.py).
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gothic
    w, n_gothic = gothic.add_names(w)
    # The Gaiad legacy numbers held in the pipeline: xrefs, merges, one NOTE per person (Emma, 2026-10-28; gedcom_legacy.py).
    import gedcom_legacy
    w, legacy_stats = gedcom_legacy.apply(w)
    out_path.write_text("\n".join(w) + "\n", encoding="utf-8-sig", newline="\n")
    stats = {"text individuals": n_text, "ancestry individuals": n - n_text, "families": nf,
             "text individuals with resolved features": n_resolved_text[0],
             "ancestors newly joined to order.life": len(joins), "calendar notes from the tree's own dates": n_cal,
             "link notes newly naming FamilySearch": n_fs, "CJK first names given an English primary name": n_en, "primary names from Wikidata": n_wd,
             "ancestry records given order.life's current Wikidata id and name": n_ident}
    if feats:
        stats.update({f"feature: {k}": v for k, v in sorted(feats.counts.items())})
    stats["gothic names"] = n_gothic
    stats.update(legacy_stats)
    stats["bytes"] = out_path.stat().st_size
    return stats


def next_free(path):
    """gaiad.ged, else gaiad1.ged, gaiad2.ged, ...: the first name not yet on disk. Emma, 2026-10-29: "put 1, 2, 3, 4,
    etc. at the end of the file name ... as a part of the generation"; in CI the directory is new, so it is always
    gaiad.ged there, and locally each build is a new file, which gets around the deduplication some family tree
    programs do on import."""
    path = Path(path)
    k = 0
    while (cand := path if k == 0 else path.with_name(f"{path.stem}{k}{path.suffix}")).exists():
        k += 1
    return cand


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else next_free(ROOT / "site" / "gaiad.ged")
    for k, v in build(dest).items():
        print(f"  {k}: {v:,}")
