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


def chinese_name(given, surname, taken):
    """The generated name, or None; `taken` is the set of names already used, updated here."""
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
            return cand
    return None
