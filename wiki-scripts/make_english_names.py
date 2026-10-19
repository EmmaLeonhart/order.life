"""
Write wiki-scripts/data/english_names.tsv: an English primary name for every person in Emma's ancestry whose first NAME
is in Chinese, Japanese or Korean script. gaiad.ged is an English file (Emma, 2026-10-17: "the first name better be the
'primary name' ... English default plus Chinese, Japanese, and Korean representation ... cjk are all lesser things"),
and build_gaiad_ged.py reads this table to put the English name first and the original under it as a TRAN.

The English name is the Wikidata English label where the record carries a Wikidata id; otherwise a romanization:
pinyin for Han script (titles such as 皇后, 公主, 氏 in English), Revised Romanization for Hangul, Hepburn for kana.
Run again when the ancestry file gains new CJK names. Needs pypinyin here; the site build does not (it reads the TSV).

    python wiki-scripts/make_english_names.py
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parent.parent
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "emma-ancestry.ged"
OUT = ROOT / "wiki-scripts" / "data" / "english_names.tsv"
WIKIDATA_PRIMARY = ROOT / "wikibase" / "analysis" / "wikidata_primary_names.tsv"
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")
HAN = re.compile(r"[㐀-鿿]+")
# Surnames whose surname reading differs from the common one.
SURNAMES = {"單": "Shan", "单": "Shan", "解": "Xie", "仇": "Qiu", "尉遲": "Yuchi", "尉迟": "Yuchi", "長孫": "Zhangsun",
            "长孙": "Zhangsun", "曾": "Zeng", "樂": "Yue", "区": "Ou", "區": "Ou", "查": "Zha", "万俟": "Moqi", "覃": "Qin"}
# Titles at the end of a name, put in English in front of the rest ("王皇后" -> "Empress Wang").
TITLES = [("太皇太后", "Grand Empress Dowager"), ("皇太后", "Empress Dowager"), ("太后", "Empress Dowager"),
          ("皇后", "Empress"), ("皇帝", "Emperor"), ("長公主", "Grand Princess"), ("长公主", "Grand Princess"),
          ("大長公主", "Great Grand Princess"), ("公主", "Princess"), ("夫人", "Lady"), ("孺人", "Lady"), ("氏", "Lady"),
          ("公", "Duke"), ("侯", "Marquis"), ("王", "King")]
# Endings that mark a Japanese name written only in kanji (kami and the old court names).
JA_END = {"命": "no Mikoto", "尊": "no Mikoto", "神": "no Kami", "大神": "no Ōkami"}
JA_HINT = re.compile(r"(命|尊|神|比売|毘売|毘古|日子|姫|彦|之男|之女)$")


def pinyin(s, surname=False):
    s = s.strip()
    if surname and s.endswith("姓") and len(s) > 1:   # "姬姓" is "the surname Ji"
        s = s[:-1]
    if surname and s in SURNAMES:
        return SURNAMES[s]
    syl = [x.replace("ü", "u") for x in lazy_pinyin(s) if x.strip()]
    if not syl:
        return s
    word = syl[0]
    for x in syl[1:]:
        word += ("'" if x[0] in "aeo" else "") + x
    return word.capitalize()


def han_token(tok, surname=False):
    """One space-separated token: romanize every Han run; a title at its end goes in English in front."""
    for zh, en in TITLES:
        if tok.endswith(zh) and tok != zh:
            return en, pinyin(tok[: -len(zh)], surname)
    return None, HAN.sub(lambda m: pinyin(m.group(0), surname), tok)


def han_name(name):
    """A GEDCOM name in Han script, romanized, keeping the /surname/ marks; titles put in English in front."""
    if re.search(r"[A-Za-zÀ-ɏ]", name):   # a Latin name already in the record ("Bù Kū 不窟 /Jī 姬/")
        kept = []
        for part in re.split(r"(/[^/]*/)", name):
            if part.startswith("/") and part.endswith("/"):
                inner = " ".join(w for w in part[1:-1].split() if not CJK.search(w))
                kept.append(f"/{inner}/" if inner else "")
            else:
                kept.append(" ".join(w for w in part.split() if not CJK.search(w)))
        out = " ".join(" ".join(kept).split())
        if re.search(r"[A-Za-z]", out):
            return out
    parts = re.split(r"(/[^/]*/)", name)
    titles, out = [], []
    for part in parts:
        if part.startswith("/") and part.endswith("/"):
            inner = part[1:-1].strip()
            en, rom = han_token(inner, surname=True) if inner else (None, "")
            if en and not rom:
                titles.append(en)
            elif en:
                titles.append(f"{en} {rom}")
            else:
                out.append(f"/{rom}/")
            continue
        for tok in part.split():
            title = next((en for zh, en in TITLES if tok == zh), None)
            if title:                       # a bare title token: 氏 after a surname, 公 after a name
                titles.append(title)
                continue
            en, rom = han_token(tok)
            if en:
                titles.append(f"{en} {rom}")
            else:
                out.append(rom)
    if "Lady" in titles and len(titles) > 1:   # "/李/ 氏 太平公主": the 氏 only marks the clan
        titles.remove("Lady")
    words = " ".join(titles + out).split()
    return " ".join(words) if words else name


INI = "g kk n d tt r m b pp s ss  j jj ch k t p h".split(" ")
MED = "a ae ya yae eo e yeo ye o wa wae oe yo u wo we wi yu eu ui i".split(" ")
FIN = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t", "ng",
       "t", "t", "k", "t", "p", "t"]


KO_SURNAMES = {"김": "Kim", "이": "Lee", "박": "Park", "최": "Choi", "정": "Jung", "유": "Yu", "윤": "Yoon", "조": "Cho"}


def hangul_word(s, surname=False):
    if surname and s in KO_SURNAMES:
        return KO_SURNAMES[s]
    out = []
    for ch in s:
        o = ord(ch) - 0xAC00
        out.append(INI[o // 588] + MED[(o % 588) // 28] + FIN[o % 28] if 0 <= o < 11172 else ch)
    return "".join(out).capitalize()


def hangul(name):
    out = []
    for part in re.split(r"(/[^/]*/)", name):
        if part.startswith("/") and part.endswith("/"):
            out.append("/" + " ".join(hangul_word(w, True) for w in part[1:-1].split()) + "/")
        else:
            out.append(" ".join(hangul_word(w) if re.search(r"[가-힯]", w) else w.capitalize() for w in part.split()))
    return " ".join(" ".join(out).split())


KANA = dict(zip("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
                "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ",
                "a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo "
                "ya yu yo ra ri ru re ro wa o n ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo pa pi pu pe "
                "po".split()))


def kana(s):
    hira = "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)
    return " ".join("".join(KANA.get(c, c) for c in hira).split()).title()


_KAKASI = None


def japanese(name):
    global _KAKASI
    if _KAKASI is None:
        import pykakasi
        _KAKASI = pykakasi.kakasi()
    bare = "".join(name.replace("/", " ").split())
    suffix = ""
    for end in sorted(JA_END, key=len, reverse=True):
        if bare.endswith(end) and len(bare) > len(end):
            bare, suffix = bare[: -len(end)], JA_END[end]
            break
    words = " ".join(x["hepburn"] for x in _KAKASI.convert(bare)).split()
    return (" ".join(words).title() + (" " + suffix if suffix else "")).strip()


_ROM = None


def other_script(name):
    """The genealogy reader for a name in a script romanize_scripts.py reads (Cyrillic, Greek, Arabic, Hebrew, ...)."""
    global _ROM
    if _ROM is None:
        sys.path.insert(0, str(ROOT.parent / "genealogy" / "scripts"))
        import romanize_scripts as _r
        _ROM = _r
    return None if CJK.search(name) else _ROM.reader_for(name) and _ROM


def needs_english(name):
    return bool(CJK.search(name) or other_script(name))


def english(name):
    rom = other_script(name)
    if rom:   # read into Latin by genealogy/scripts/romanize_scripts.py (Emma: "try wikidata but then build readers")
        latin, lang = rom.romanize(name)
        return (latin, lang, "romanized (genealogy romanize_scripts)") if latin else None
    bare = "".join(name.replace("/", " ").split())
    if JA_HINT.search(bare) and not re.search(r"[A-Za-z]", bare):
        return japanese(name), "ja", "romanized (Hepburn, pykakasi)"
    if re.search(r"[가-힯]", name):
        return hangul(name), "ko", "romanized (Revised Romanization)"
    if re.search(r"[぀-ヿ]", name):
        return kana(name), "ja", "romanized (Hepburn)"
    return han_name(name), "zh", "romanized (pinyin)"


def wikidata_labels(qids):
    out = {}
    qids = sorted(qids)
    for i in range(0, len(qids), 50):
        url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=en&format=json&ids="
               + "|".join(qids[i:i + 50]))
        req = urllib.request.Request(url, headers={"User-Agent": "order.life gaiad.ged builder (emma@topazcomputing.com)"})
        data = json.load(urllib.request.urlopen(req, timeout=60))
        for q, e in data.get("entities", {}).items():
            lb = e.get("labels", {}).get("en", {}).get("value")
            if lb:
                out[q] = lb
    return out


def wikidata_by_ja_label(names):
    """English labels of items whose Japanese label is exactly the name (one hit only)."""
    out = {}
    for name in names:
        bare = "".join(name.replace("/", " ").split())
        url = ("https://www.wikidata.org/w/api.php?action=wbsearchentities&language=ja&uselang=en&type=item&limit=5"
               "&format=json&search=" + urllib.parse.quote(bare))
        req = urllib.request.Request(url, headers={"User-Agent": "order.life gaiad.ged builder (emma@topazcomputing.com)"})
        hits = [h for h in json.load(urllib.request.urlopen(req, timeout=60)).get("search", [])
                if h.get("match", {}).get("text") == bare and h.get("match", {}).get("type") == "label"]
        if len(hits) == 1 and hits[0].get("label") and not CJK.search(hits[0]["label"]):
            out[name] = hits[0]["label"]
    return out


# Names the rules cannot read, set by hand.
MANUAL = {"ヴィフェ・オフ・ホプニ": ("Wife of Hophni", "ja", "katakana of the English name, set by hand")}
# Kami of the Kojiki, whose names are read in kun and man'yōgana, not the on'yomi pykakasi gives ("Dai Choku Bi no Kami"
# for 大直毘神). The Kojiki's own readings, checked against Wikidata where it has the kami (Ōkamuzumi, Tokihakashi,
# Nakisawame, Kumanokusubi, Chigaeshi, Akiguinoushi); its paired items ("Kamunaobi and Ōnaobi") give one each.
KOJIKI = "Kojiki reading, set by hand"
MANUAL.update({
    "上筒之男神": ("Uwatsutsunoo no Kami", "ja", KOJIKI), "中筒之男神": ("Nakatsutsunoo no Kami", "ja", KOJIKI),
    "底筒之男神": ("Sokotsutsunoo no Kami", "ja", KOJIKI), "八十禍津日神": ("Yasomagatsuhi no Kami", "ja", KOJIKI),
    "大禍津日神": ("Ōmagatsuhi no Kami", "ja", KOJIKI), "大直毘神": ("Ōnaobi no Kami", "ja", KOJIKI),
    "神直毘神": ("Kamunaobi no Kami", "ja", KOJIKI), "和豆良比能宇斯能神": ("Wazurainoushi no Kami", "ja", KOJIKI),
    "奥津甲斐弁羅神": ("Okitsukaibera no Kami", "ja", KOJIKI), "辺津甲斐弁羅神": ("Hetsukaibera no Kami", "ja", KOJIKI),
    "奥津那芸佐毘古神": ("Okitsunagisabiko no Kami", "ja", KOJIKI),
    "辺津那芸佐毘古神": ("Hetsunagisabiko no Kami", "ja", KOJIKI),
    "奥疎神": ("Okizakaru no Kami", "ja", KOJIKI), "辺疎神": ("Hezakaru no Kami", "ja", KOJIKI),
    "時量師神": ("Tokihakashi no Kami", "ja", KOJIKI), "衝立船戸神": ("Tsukitatsufunado no Kami", "ja", KOJIKI),
    "道俣神": ("Chimata no Kami", "ja", KOJIKI), "道之長乳歯神": ("Michinonagachiha no Kami", "ja", KOJIKI),
    "飽咋之宇斯能神": ("Akiguinoushi no Kami", "ja", KOJIKI), "道返之大神": ("Chigaeshi no Ōkami", "ja", KOJIKI),
    "意富加牟豆美命": ("Ōkamuzumi no Mikoto", "ja", KOJIKI), "泣沢女神": ("Nakisawame no Kami", "ja", KOJIKI),
    "活津日子命": ("Ikutsuhiko no Mikoto", "ja", KOJIKI), "火之夜藝速男神": ("Hinoyagihayao no Kami", "ja", KOJIKI),
    "熊野久須毘命": ("Kumanokusubi no Mikoto", "ja", KOJIKI),
})


def main():
    rows, qid_of = dict(MANUAL), {}
    cur = None
    for line in ANCESTRY.read_text(encoding="utf-8-sig").replace("\r", "").split("\n"):
        if line.startswith("0 "):
            cur = {"name": None, "qid": None}
            continue
        if cur is None:
            continue
        if line.startswith("1 NAME ") and cur["name"] is None:
            cur["name"] = line[7:].strip()
            if needs_english(cur["name"]):
                got = english(cur["name"])
                if got:
                    rows.setdefault(cur["name"], got)
        m = re.search(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", line)
        if m and cur["name"] and needs_english(cur["name"]):
            qid_of[m.group(1)] = cur["name"]
    # A Wikidata label build_gaiad_ged.py makes the primary NAME (wikidata_first) can itself be in another script,
    # where the item has no English or mul label (Дрогон, Q56367490): it is read the same way.
    if WIKIDATA_PRIMARY.exists():
        for row in WIKIDATA_PRIMARY.read_text(encoding="utf-8").splitlines()[1:]:
            label = (row.split("\t") + [""])[1]
            if label and other_script(label):
                got = english(label)
                if got:
                    rows.setdefault(label, got)
    labels = wikidata_labels(qid_of) if qid_of else {}
    # Their ja/zh/ko from Wikidata too, for the names in other scripts (Emma: "try wikidata" first).
    other = sorted(q for q, n in qid_of.items() if other_script(n))
    cjk_rows = []
    for i in range(0, len(other), 50):
        url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=ja|zh|ko&format=json"
               "&ids=" + "|".join(other[i:i + 50]))
        req = urllib.request.Request(url, headers={"User-Agent": "order.life gaiad.ged builder (emma@topazcomputing.com)"})
        for q, e in json.load(urllib.request.urlopen(req, timeout=60)).get("entities", {}).items():
            got = {lg: e.get("labels", {}).get(lg, {}).get("value", "") for lg in ("ja", "zh", "ko")}
            if any(got.values()):
                cjk_rows.append((q, got["ja"], got["zh"], got["ko"]))
    with (ROOT / "wikibase" / "analysis" / "wikidata_cjk_labels.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("qid\tja\tzh\tko\n")
        for row in cjk_rows:
            f.write("\t".join(row) + "\n")
    print(f"{len(other)} people in other scripts with a Wikidata id, {len(cjk_rows)} with ja/zh/ko labels")
    for name, en in wikidata_by_ja_label([n for n, r in rows.items() if r[1] == "ja"]).items():
        rows[name] = (en, "ja", "Wikidata English label (by Japanese label)")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# key_type\tkey\tenglish\tlang\tsource   (from make_english_names.py)\n")
        for q, lb in sorted(labels.items()):
            f.write(f"wikidata\t{q}\t{lb}\t{(english(qid_of[q]) or ("", "und", ""))[1]}\tWikidata English label\n")
        for name, (en, lang, src) in sorted(rows.items()):
            f.write(f"name\t{name}\t{en}\t{lang}\t{src}\n")
    print(f"{len(rows)} names, {len(labels)} Wikidata labels -> {OUT}")


if __name__ == "__main__":
    main()
