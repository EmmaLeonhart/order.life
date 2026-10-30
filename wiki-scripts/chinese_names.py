"""
A Chinese name for everyone without one: the method of planning/chinese-names.md, approved by Emma 2026-10-15
("Build and apply").

Surname: one character for the first syllable of the house or family name (her example: Banu Hashim -> 哈 for
Muhammad). Given name: one or two characters for the first syllables of the person's own given name. Characters come
from a compact form of the standard transliteration table for foreign names (the Xinhua practice: 巴 ba, 卡 ka,
马 ma, 里 ri ...), so the sound is kept. Uniqueness: a full name already taken gets a further syllable of the given
name. Generated names are marked as such in the GEDCOM; people with a real Chinese label keep it and get none.
Stdlib only.
"""
import re
import unicodedata

VOWEL_CHAR = {"a": "阿", "e": "埃", "i": "伊", "o": "奥", "u": "乌", "y": "伊"}
# onset -> vowel -> character
TABLE = {
    "b": dict(a="巴", e="贝", i="比", o="博", u="布"), "c": dict(a="卡", e="塞", i="西", o="科", u="库"),
    "d": dict(a="达", e="德", i="迪", o="多", u="杜"), "f": dict(a="法", e="费", i="菲", o="福", u="富"),
    "g": dict(a="加", e="格", i="吉", o="戈", u="古"), "h": dict(a="哈", e="赫", i="希", o="霍", u="胡"),
    "j": dict(a="贾", e="杰", i="吉", o="乔", u="朱"), "k": dict(a="卡", e="克", i="基", o="科", u="库"),
    "l": dict(a="拉", e="莱", i="利", o="洛", u="卢"), "m": dict(a="马", e="梅", i="米", o="莫", u="穆"),
    "n": dict(a="纳", e="内", i="尼", o="诺", u="努"), "p": dict(a="帕", e="佩", i="皮", o="波", u="普"),
    "q": dict(a="夸", e="奎", i="基", o="阔", u="库"), "r": dict(a="拉", e="雷", i="里", o="罗", u="鲁"),
    "s": dict(a="萨", e="塞", i="西", o="索", u="苏"), "t": dict(a="塔", e="特", i="蒂", o="托", u="图"),
    "v": dict(a="瓦", e="韦", i="维", o="沃", u="武"), "w": dict(a="瓦", e="韦", i="威", o="沃", u="乌"),
    "x": dict(a="夏", e="谢", i="西", o="肖", u="许"), "y": dict(a="亚", e="叶", i="伊", o="约", u="尤"),
    "z": dict(a="扎", e="泽", i="齐", o="佐", u="祖"),
    "sh": dict(a="沙", e="谢", i="希", o="肖", u="舒"), "ch": dict(a="查", e="切", i="奇", o="乔", u="丘"),
    "th": dict(a="塔", e="特", i="西", o="索", u="苏"), "ph": dict(a="法", e="费", i="菲", o="福", u="富"),
    "kh": dict(a="哈", e="赫", i="希", o="霍", u="胡"), "gh": dict(a="加", e="格", i="吉", o="戈", u="古"),
}
FINAL = {"n": "恩", "m": "姆", "r": "尔", "l": "尔", "s": "斯", "t": "特", "d": "德", "k": "克", "g": "格",
         "b": "布", "p": "普", "f": "夫", "v": "夫", "x": "克斯", "z": "兹", "sh": "什", "ch": "奇", "th": "斯"}


def _plain(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalpha() and ord(c) < 128)


def syllables(word):
    """Chinese characters for each syllable of a Latin-script word."""
    w = _plain(word)
    out, i = [], 0
    while i < len(w):
        onset = ""
        for cl in ("sh", "ch", "th", "ph", "kh", "gh"):
            if w.startswith(cl, i):
                onset = cl
                break
        if not onset and w[i] not in "aeiouy":
            onset = w[i]
        j = i + len(onset)
        if j < len(w) and w[j] in "aeiouy":
            v = w[j] if w[j] != "y" else "i"
            out.append(TABLE.get(onset, {}).get(v) if onset else VOWEL_CHAR[v])
            i = j + 1
            while i < len(w) and w[i] in "aeiouy":   # a vowel run is one syllable
                i += 1
        else:
            if onset in FINAL:
                out.append(FINAL[onset])
            i = j if j > i else i + 1
    return [c for c in out if c]


PARTICLES = {"de", "del", "della", "dei", "degli", "di", "da", "das", "dos", "do", "du", "des", "la", "le", "les",
             "van", "von", "der", "den", "ten", "ter", "zu", "y", "e", "of", "the", "son", "daughter", "ibn", "bin",
             "bint", "ben", "bat", "ap", "ab", "ferch", "verch", "al", "el", "mac", "mc", "o", "st", "saint",
             # titles, which a record sometimes carries in the surname slot ("King of Numidia", "Raja Sriwijaya")
             "king", "queen", "prince", "princess", "lord", "lady", "emperor", "empress", "sultan", "raja", "rajah",
             "duke", "duchess", "count", "countess", "earl", "baron", "sir", "dame", "king's", "shah", "khan", "caliph",
             "pharaoh", "chief", "regent", "consort", "maharaja", "tsar", "czar", "infante", "infanta"}


def first_significant(words):
    for w in words.replace("-", " ").split():
        if w.lower().strip(".,'") not in PARTICLES and len(_plain(w)) > 1:
            return w
    return ""


def chinese_name_parts(given, surname, taken):
    """The generated name as (surname, given name), or None; `taken` is the set of names already used, updated here."""
    gw = given.split()[0] if given else ""
    if len(_plain(gw)) < 2:
        return None                      # an initial or a placeholder ("X") is not a name
    g = syllables(gw)
    sw = first_significant(surname) if surname else ""
    if sw and _plain(sw) == _plain(gw):
        return None                      # the same word twice: a clade or a single name, not a family name
    s = syllables(sw) if sw else []
    if not g or not s:
        return None
    for n in (2, 1, 3):
        cand = s[0] + "".join(g[:n])
        if cand not in taken:
            taken.add(cand)
            return s[0], "".join(g[:n])
    return None


def chinese_name(given, surname, taken):
    """The generated name as one string, or None."""
    parts = chinese_name_parts(given, surname, taken)
    return "".join(parts) if parts else None


# Pinyin with tone marks for every character the tables above can produce (one reading each).
PINYIN = {
    "阿": "ā", "埃": "āi", "伊": "yī", "奥": "ào", "乌": "wū",
    "巴": "bā", "贝": "bèi", "比": "bǐ", "博": "bó", "布": "bù", "卡": "kǎ", "塞": "sài", "西": "xī", "科": "kē",
    "库": "kù", "达": "dá", "德": "dé", "迪": "dí", "多": "duō", "杜": "dù", "法": "fǎ", "费": "fèi", "菲": "fēi",
    "福": "fú", "富": "fù", "加": "jiā", "格": "gé", "吉": "jí", "戈": "gē", "古": "gǔ", "哈": "hā", "赫": "hè",
    "希": "xī", "霍": "huò", "胡": "hú", "贾": "jiǎ", "杰": "jié", "乔": "qiáo", "朱": "zhū", "克": "kè", "基": "jī",
    "拉": "lā", "莱": "lái", "利": "lì", "洛": "luò", "卢": "lú", "马": "mǎ", "梅": "méi", "米": "mǐ", "莫": "mò",
    "穆": "mù", "纳": "nà", "内": "nèi", "尼": "ní", "诺": "nuò", "努": "nǔ", "帕": "pà", "佩": "pèi", "皮": "pí",
    "波": "bō", "普": "pǔ", "夸": "kuā", "奎": "kuí", "阔": "kuò", "雷": "léi", "里": "lǐ", "罗": "luó", "鲁": "lǔ",
    "萨": "sà", "索": "suǒ", "苏": "sū", "塔": "tǎ", "特": "tè", "蒂": "dì", "托": "tuō", "图": "tú", "瓦": "wǎ",
    "韦": "wéi", "维": "wéi", "沃": "wò", "武": "wǔ", "威": "wēi", "夏": "xià", "谢": "xiè", "肖": "xiāo", "许": "xǔ",
    "亚": "yà", "叶": "yè", "约": "yuē", "尤": "yóu", "扎": "zhā", "泽": "zé", "齐": "qí", "佐": "zuǒ", "祖": "zǔ",
    "沙": "shā", "舒": "shū", "查": "chá", "切": "qiē", "奇": "qí", "丘": "qiū",
    "恩": "ēn", "姆": "mǔ", "尔": "ěr", "斯": "sī", "夫": "fū", "兹": "zī", "什": "shí",
}


def pinyin(chars):
    """Pinyin for a run of characters, joined as one word ("Lǐchá"), with the apostrophe before a syllable that
    starts with a, e or o; None if a character has no reading here."""
    out = ""
    for k, ch in enumerate(chars):
        py = PINYIN.get(ch)
        if py is None:
            return None
        if k and unicodedata.normalize("NFD", py)[0] in "aeo":
            out += "'"
        out += py
    return out[:1].upper() + out[1:]


# A person whose usual name is not transliterated into Chinese: the Chinese name is theirs, not generated
# (Emma, 2026-10-30: "my name does not get transliterated"). qid -> (surname, given, surname pinyin, given pinyin).
OWN_CHINESE = {"Q2": ("李", "命玥", "Lǐ", "Mìngyuè")}


def chinese_name_lines(sur, giv, sur_py=None, giv_py=None):
    """The Chinese-name object: pinyin with the surname in slashes, the characters as TRAN zh, labelled
    "Chinese name" (Emma, 2026-10-30), generated or not. [] if the pinyin cannot be made."""
    sur_py = sur_py or pinyin(sur)
    giv_py = giv_py or pinyin(giv)
    if not sur_py or not giv_py:
        return []
    return [f"1 NAME /{sur_py}/ {giv_py}", "2 TYPE OTHER", "3 PHRASE Chinese name",
            f"2 TRAN /{sur}/ {giv}", "3 LANG zh", "2 NOTE Chinese name"]
