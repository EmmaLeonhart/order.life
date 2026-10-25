"""
Temple names and Horus names for the monarchs (planning/monarch-names.md; Emma, 2026-10-15: "Build and apply").

Emma, 2026-10-13: "Every monarch ever ... needs to have a temple name and a Horus name."
- Temple name (廟號), by the ruler's place among the holders of a position (wikibase/analysis/monarchs.tsv),
  ordered by birth year: the first 太祖, the second 太宗, the last 末帝, those between a virtue name in turn.
  Rulers whose own tradition gives temple or era names (Chinese, Korean, Vietnamese, Japanese) are left to those.
- Horus name, the first of the pharaoh's five names: Ḥr kꜣ-nḫt, "Horus, Strong Bull", a second element from the
  meaning of the ruler's temple name, and the ruler's byname where the record has one ("the Great" -> wr).
  Pharaohs keep their attested Horus names (pharaoh_names.tsv); where none is recorded, one is restored on
  the pattern of the dynasty and marked as restored.
Both are written to the GEDCOM marked as generated. Stdlib only.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

ANA = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"
VIRTUE = ["高宗", "仁宗", "英宗", "宣宗", "憲宗", "睿宗", "德宗", "順宗", "穆宗", "敬宗", "文宗", "武宗",
          "孝宗", "光宗", "寧宗", "理宗", "度宗", "神宗", "哲宗", "徽宗", "欽宗", "明宗", "昭宗", "興宗"]
OWN_TRADITION = re.compile(r"China|Chinese|Korea|Joseon|Goryeo|Silla|Baekje|Goguryeo|Gaya|Vietnam|Japan|"
                           r"Emperor of Japan|Empress of Japan|pharaoh|Egypt", re.I)
EPITHET = {"great": ("wr", "the Great"), "wise": ("sꜣꜣ", "the Wise"), "good": ("nfr", "the Good"),
           "pious": ("mnḫ", "the Pious"), "brave": ("nḫt-ḥpš", "Strong of Arm"), "just": ("mꜣꜥ-ḫrw", "the Just"),
           "conqueror": ("ṯꜣ-tꜣwj", "Seizer of the Lands"), "generous": ("ꜥꜣ-ḥnwt", "Great of Gifts"),
           "elder": ("smsw", "the Elder"), "younger": ("šrj", "the Younger"), "chaste": ("wꜥb", "the Pure"),
           "confessor": ("ḥm-nṯr", "Servant of the God"), "bear": ("kꜣ-nḫt", "the Bear")}


def year(ts):
    m = re.match(r"([+-]?)0*(\d+)", (ts or "").strip())
    if not m or not m.group(2).isdigit():
        return None
    y = int(m.group(2))
    return -y if m.group(1) == "-" else y


def build():
    births = {}
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            births[r["qid"]] = year(r.get("birth"))
    rows = list(csv.DictReader(open(ANA / "monarchs.tsv", encoding="utf-8"), delimiter="\t"))
    holders = defaultdict(list)
    for r in rows:
        for p in r["positions"].split("; "):
            if not OWN_TRADITION.search(p):
                holders[p].append(r["qid"])
    temple = {}
    for p, qs in holders.items():
        if len(qs) < 2:
            continue
        qs = sorted(set(qs), key=lambda q: (births.get(q) is None, births.get(q) or 0, int(q[1:])))
        for i, q in enumerate(qs):
            if q in temple:
                continue
            if i == 0:
                temple[q] = ("太祖", f"founder among the holders of {p}")
            elif i == 1:
                temple[q] = ("太宗", f"second holder of {p}")
            elif i == len(qs) - 1:
                temple[q] = ("末帝", f"last holder of {p}")
            else:
                temple[q] = (VIRTUE[(i - 2) % len(VIRTUE)], f"holder {i + 1} of {p}")
    zh = {}
    if (ANA / "labels.tsv").exists():
        for r in csv.DictReader(open(ANA / "labels.tsv", encoding="utf-8"), delimiter="\t"):
            if r["lang"] == "zh":
                zh[r["qid"]] = r["label"]
    # Chinese emperors whose record gives no temple name: their place among the holders of their Chinese
    # position, as for everyone else, only to derive the Abrahamic name (the temple name itself is left to
    # their own tradition).
    china = defaultdict(list)
    for r in rows:
        for p in r["positions"].split("; "):
            if re.search(r"China|Chinese", p):
                china[p].append(r["qid"])
    place = {}
    for p, qs in china.items():
        qs = sorted(set(qs), key=lambda q: (births.get(q) is None, births.get(q) or 0, int(q[1:])))
        for i, q in enumerate(qs):
            if q in place:
                continue
            if i == 0:
                place[q] = ("太祖", f"first among the holders of {p}")
            elif i == 1 and len(qs) > 2:
                place[q] = ("太宗", f"second holder of {p}")
            elif i == len(qs) - 1:
                place[q] = ("末帝", f"last holder of {p}")
            else:
                place[q] = (VIRTUE[(i - 2) % len(VIRTUE)], f"holder {i + 1} of {p}")
    abrahamic = {}
    for r in rows:
        if re.search(r"China|Chinese", r["positions"]):
            a = abrahamic_from_temple(r["label"], zh.get(r["qid"], ""))
            if not a and r["qid"] in place:
                t, how = place[r["qid"]]
                key = t if t in TEMPLE_TO_ABRAHAMIC else t[0]
                if key in TEMPLE_TO_ABRAHAMIC:
                    a = (TEMPLE_TO_ABRAHAMIC[key][0], t, f"{TEMPLE_TO_ABRAHAMIC[key][1]}; no recorded temple "
                                                         f"name, so by place: {how}")
            if a:
                abrahamic[r["qid"]] = a
    # Horus names: Strong Bull and a second element, as in the New Kingdom (kꜣ-nḫt mrj-mꜣꜥt, "Strong Bull,
    # Beloved of Maat", Ramesses II). The second element comes from the meaning of the ruler's temple name
    # (generated, recorded, or by place); with none, from the qid, so that names vary. A byname still adds its
    # epithet at the end.
    horus = {}
    for r in rows:
        if OWN_TRADITION.search(r["positions"]) and "pharaoh" in r["positions"].lower():
            continue
        q = r["qid"]
        t = (temple.get(q) or (None,))[0] or (abrahamic.get(q) or (None, None))[1] or (place.get(q) or (None,))[0]
        if t and t.isascii():
            t = PINYIN_TEMPLE.get(t.lower())
        el = (HORUS_ELEMENT.get(t) or HORUS_ELEMENT.get(t[0])) if t else None
        if not el:
            el = HORUS_FALLBACK[int(q[1:]) % len(HORUS_FALLBACK)] if q[1:].isdigit() else HORUS_FALLBACK[0]
        name, gloss = f"Ḥr kꜣ-nḫt {el[0]}", f"Horus, Strong Bull, {el[1]}"
        m = re.search(r"\bthe ([A-Z][a-z]+)\b", r["label"])
        ep = EPITHET.get(m.group(1).lower()) if m else None
        if ep:
            name, gloss = f"{name} {ep[0]}", f"{gloss}, {ep[1]}"
        horus[q] = (name, gloss, "generated")
    horus.update(pharaoh_horus(rows))
    return temple, horus, abrahamic


HIERO_CODE = re.compile(r"^[A-Z]{1,2}\d+[a-z]?(?:[:*-][A-Z]{1,2}\d+[a-z]?)*$")
EGYPTOLOGICAL = re.compile(r"[ꜣꜥḥḫẖšḳṯḏˁȝ3]|\.(?:f|wj|tj)\b")


def pharaoh_horus(rows):
    """Pharaohs' Horus names: the attested name from wikibase/analysis/pharaoh_names.tsv (fetch_pharaoh_names.py),
    else one restored on the pattern of the dynasty and marked as a restoration (planning/monarch-names.md)."""
    path = ANA / "pharaoh_names.tsv"
    attested = {}
    if path.exists():
        for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
            attested[r["qid"]] = r
    out = {}
    for r in rows:
        if "pharaoh" not in r["positions"].lower():
            continue
        q = r["qid"]
        a = attested.get(q, {})
        parts = [re.sub(r"\{\{[^|{}]*\|(?:[^|{}]*\|)*|\}\}|^\"|\"$", "", (a.get(k) or "")).strip()
                 for k in ("horus", "horus_translit", "horus_gloss")]
        parts = [x for x in parts if x and not HIERO_CODE.match(x) and "?" not in x]
        if parts:
            translit = next((x for x in parts if EGYPTOLOGICAL.search(x)), parts[0])
            gloss = next((x for x in parts if x != translit and re.match(r"^[A-Z\"(]", x) and " " in x), "")
            reading = next((x for x in parts if x not in (translit, gloss)), "")
            text = "; ".join(x for x in (reading, gloss) if x) or translit
            out[q] = (translit, f"{text} (attested; en.wikipedia {a.get('article', '')})", "attested")
            continue
        dyn = (a.get("dynasty") or "").lower()
        if "ptolem" in dyn or "argead" in dyn:
            # The Ptolemaic Horus names open on ḥwnw, "the youth" (Ptolemy V, VIII, XII, Caesarion).
            out[q] = ("Ḥr ḥwnw", "Horus, the Youth (restored on the Ptolemaic pattern)", "restored")
        elif re.search(r"dynasty 0|predynastic|naqada|\b(?:1st|first|2nd|second|3rd|third)\b", dyn):
            # The earliest kings are known by the Horus name alone: Horus and the king's own name.
            base = re.sub(r"\s*\(.*\)$", "", a.get("article") or "") or re.split(r"\s{2,}|,|\"", r["label"])[0].strip()
            out[q] = (f"Ḥr {base}", f"Horus {base} (restored on the Early Dynastic pattern, Horus and the "
                                     f"king's name)", "restored")
        else:
            out[q] = ("Ḥr kꜣ-nḫt", "Horus, Strong Bull (restored: no Horus name is recorded; Strong Bull opens "
                                    "most Horus names from the New Kingdom on)", "restored")
    return out


# The second element of a Horus name, by the temple name or its first character. Elements are taken from or
# built on attested Horus names: mrj-tꜣwj (Pepi I), sḥtp-tꜣwj (Teti), smꜣ-tꜣwj (Mentuhotep II), wḥm-mswt
# (Amenemhat I), mrj-mꜣꜥt (Ramesses II), wsr-pḥtj and nḫt-ḥpš (New Kingdom epithets).
HORUS_ELEMENT = {
    "太祖": ("grg-tꜣwj", "Founder of the Two Lands"), "高祖": ("grg-tꜣwj", "Founder of the Two Lands"),
    "成祖": ("smꜣ-tꜣwj", "Uniter of the Two Lands"), "太宗": ("smn-tꜣwj", "Who Makes the Two Lands Firm"),
    "末帝": ("ḥtp-ḥr-mꜣꜥt", "Content with Maat"), "末": ("ḥtp-ḥr-mꜣꜥt", "Content with Maat"),
    "高": ("ḳꜣ-šwtj", "High of Plumes"), "仁": ("mrj-tꜣwj", "Beloved of the Two Lands"),
    "惠": ("mrj-tꜣwj", "Beloved of the Two Lands"), "英": ("nḫt-ḥpš", "Strong of Arm"),
    "宣": ("sḫꜥ-mꜣꜥt", "Who Makes Maat Appear"), "憲": ("mrj-mꜣꜥt", "Beloved of Maat"),
    "宪": ("mrj-mꜣꜥt", "Beloved of Maat"), "度": ("mrj-mꜣꜥt", "Beloved of Maat"), "理": ("mrj-mꜣꜥt", "Beloved of Maat"),
    "睿": ("sꜣꜣ-jb", "Wise of Heart"), "哲": ("sꜣꜣ-jb", "Wise of Heart"), "思": ("sꜣꜣ-jb", "Wise of Heart"),
    "寧": ("sḥtp-tꜣwj", "Who Pacifies the Two Lands"), "宁": ("sḥtp-tꜣwj", "Who Pacifies the Two Lands"),
    "武": ("wsr-pḥtj", "Great of Strength"), "文": ("rḫ-ḫt", "Knower of Things"), "章": ("rḫ-ḫt", "Knower of Things"),
    "穆": ("snṯr-nṯrw", "Who Honours the Gods"), "肅": ("snṯr-nṯrw", "Who Honours the Gods"),
    "肃": ("snṯr-nṯrw", "Who Honours the Gods"), "敬": ("snṯr-nṯrw", "Who Honours the Gods"),
    "欽": ("snṯr-nṯrw", "Who Honours the Gods"), "順": ("ḥtp-jb", "Content of Heart"), "顺": ("ḥtp-jb", "Content of Heart"),
    "德": ("nfr-jb", "Good of Heart"), "懿": ("nfr-jb", "Good of Heart"), "端": ("nfr-jb", "Good of Heart"),
    "徽": ("nfr-ḫꜥw", "Perfect of Appearances"), "興": ("wḥm-mswt", "Repeater of Births"),
    "兴": ("wḥm-mswt", "Repeater of Births"), "孝": ("mrj-jt.f", "Beloved of His Father"),
    "景": ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"), "明": ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"),
    "光": ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"), "昭": ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"),
    "熙": ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"), "熹": ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"),
    "聖": ("nṯrj-ḫpr", "Divine of Form"), "圣": ("nṯrj-ḫpr", "Divine of Form"), "神": ("nṯrj-ḫpr", "Divine of Form"),
    "玄": ("štꜣ-ḫprw", "Hidden of Forms"), "中": ("smꜣ-tꜣwj", "Uniter of the Two Lands"),
    "世": ("wꜣḥ-nswt", "Enduring in Kingship"), "代": ("wꜣḥ-nswt", "Enduring in Kingship"),
    "僖": ("ꜣw-jb", "Joyful of Heart"), "哀": ("ḥtp-ḥr-mꜣꜥt", "Content with Maat"),
}
HORUS_FALLBACK = [("mrj-mꜣꜥt", "Beloved of Maat"), ("mrj-tꜣwj", "Beloved of the Two Lands"),
                  ("wsr-pḥtj", "Great of Strength"), ("sḥtp-tꜣwj", "Who Pacifies the Two Lands"),
                  ("nḫt-ḥpš", "Strong of Arm"), ("ḫꜥ-m-ꜣḫt", "Appearing on the Horizon"),
                  ("wꜣḥ-nswt", "Enduring in Kingship"), ("nfr-jb", "Good of Heart")]


# ── Abrahamic names for Chinese emperors, from their temple names (Emma, 2026-10-15: "Abrahamic names of Chinese
# emperors come from temple names"; by meaning, her choice): the temple name's first character, matched to the
# Abrahamic name whose root means the same (the neo-kun'yomi table run backwards, plus a few roots beyond it).
TEMPLE_TO_ABRAHAMIC = {
    "太祖": ("Abraham", "founder, as Abraham is father of many"), "高祖": ("Abraham", "founder"),
    "成祖": ("Joshua", "the accomplisher, who completed the conquest"), "太宗": ("Isaac", "the second, as Isaac"),
    "高": ("Ali", "高 high, Ali's kanji"), "世": ("Seth", "the line renewed; Seth the appointed one"),
    "代": ("Seth", "the succession"), "仁": ("John", "benevolent; Yah is gracious"), "惠": ("John", "kind; gracious"),
    "英": ("Andrew", "heroic; brave"), "宣": ("Muhammad", "proclaimed; praised"), "憲": ("Daniel", "law; God is my judge"),
    "宪": ("Daniel", "law"), "度": ("Daniel", "measure; judgement"), "理": ("Daniel", "principle; judgement"),
    "睿": ("Solomon", "wise"), "哲": ("Solomon", "wise"), "思": ("Solomon", "thoughtful"), "寧": ("Solomon", "peace"),
    "宁": ("Solomon", "peace"), "武": ("David", "martial, as the warrior king"), "文": ("Ezra", "cultured; the scribe"),
    "章": ("Ezra", "statute; the scribe"), "穆": ("Simeon", "reverent; heard"), "肅": ("Simeon", "solemn"),
    "肃": ("Simeon", "solemn"), "敬": ("Simeon", "reverent"), "順": ("Samuel", "compliant; God has heard"),
    "顺": ("Samuel", "compliant"), "德": ("Tobias", "virtue; God is good"), "懿": ("Tobias", "virtuous"),
    "端": ("Tobias", "upright"), "興": ("Joseph", "rising; he will add"), "兴": ("Joseph", "rising; he will add"),
    "孝": ("Joseph", "filial, as Joseph to Jacob"), "景": ("Uriah", "bright; my light is Yah"),
    "明": ("Uriah", "bright"), "光": ("Uriah", "light"), "昭": ("Uriah", "illustrious"), "熙": ("Uriah", "bright"),
    "熹": ("Uriah", "bright"), "聖": ("Michael", "holy; who is like God"), "圣": ("Michael", "holy"),
    "神": ("Michael", "divine; who is like God"), "玄": ("Enoch", "profound; Enoch who walked with God"),
    "中": ("Nehemiah", "the restorer midway, as the rebuilder"), "僖": ("Isaac", "joyful; he will laugh"),
    "哀": ("Job", "lamented"), "末帝": ("Job", "the last, who endured"), "徽": ("Tobias", "excellent; God is good"),
    "欽": ("Simeon", "respectful"),
}
PINYIN_TEMPLE = {"taizu": "太祖", "gaozu": "高祖", "chengzu": "成祖", "taizong": "太宗", "gaozong": "高",
                 "shizong": "世", "shizu": "世", "renzong": "仁", "yingzong": "英", "xuanzong": "宣", "wuzong": "武",
                 "wenzong": "文", "muzong": "穆", "shenzong": "神", "xiaozong": "孝", "dezong": "德", "ruizong": "睿",
                 "zhongzong": "中", "suzong": "肅", "daizong": "代", "shunzong": "順", "jingzong": "敬",
                 "yizong": "懿", "xizong": "僖", "zhaozong": "昭", "guangzong": "光", "ningzong": "寧",
                 "lizong": "理", "duzong": "度", "mingzong": "明", "xingzong": "興", "zhangzong": "章",
                 "shengzong": "聖", "huizong": "徽", "qinzong": "欽", "aizong": "哀", "xianzong": "憲",
                 "zhezong": "哲", "gongzong": "敬"}


def abrahamic_from_temple(label, zh_label):
    """(name, temple name, reason) for a Chinese emperor whose record gives a temple name, else None."""
    m = re.search(r"(.)(祖|宗)", zh_label or "")
    key = None
    if m:
        whole = m.group(1) + m.group(2)
        key = whole if whole in TEMPLE_TO_ABRAHAMIC else m.group(1)
        temple = whole
    else:
        p = re.search(r"\b([A-Za-z]+(?:zu|zong))\b", label or "")
        if p and p.group(1).lower() in PINYIN_TEMPLE:
            key = PINYIN_TEMPLE[p.group(1).lower()]
            temple = p.group(1)
    if key and key in TEMPLE_TO_ABRAHAMIC:
        name, why = TEMPLE_TO_ABRAHAMIC[key]
        return name, temple, why
    return None
