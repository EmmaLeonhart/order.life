"""
Temple names and Horus names for the monarchs (planning/monarch-names.md; Emma, 2026-10-15: "Build and apply").

Emma, 2026-10-13: "Every monarch ever ... needs to have a temple name and a Horus name."
- Temple name (廟號), by the ruler's place among the holders of a position (wikibase/analysis/monarchs.tsv),
  ordered by birth year: the first 太祖, the second 太宗, the last 末帝, those between a virtue name in turn.
  Rulers whose own tradition gives temple or era names (Chinese, Korean, Vietnamese, Japanese) are left to those.
- Horus name, the first of the pharaoh's five names: Ḥr kꜣ-nḫt, "Horus, Strong Bull", with the ruler's byname
  where the record has one ("the Great" -> wr). Pharaohs keep their attested Horus names and get none here.
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
    horus = {}
    for r in rows:
        if OWN_TRADITION.search(r["positions"]) and "pharaoh" in r["positions"].lower():
            continue
        m = re.search(r"\bthe ([A-Z][a-z]+)\b", r["label"])
        ep = EPITHET.get(m.group(1).lower()) if m else None
        name, gloss = ("Ḥr kꜣ-nḫt", "Horus, Strong Bull")
        if ep:
            name, gloss = f"{name} {ep[0]}", f"{gloss}, {ep[1]}"
        horus[r["qid"]] = (name, gloss)
    zh = {}
    if (ANA / "labels.tsv").exists():
        for r in csv.DictReader(open(ANA / "labels.tsv", encoding="utf-8"), delimiter="\t"):
            if r["lang"] == "zh":
                zh[r["qid"]] = r["label"]
    abrahamic = {}
    for r in rows:
        if re.search(r"China|Chinese", r["positions"]):
            a = abrahamic_from_temple(r["label"], zh.get(r["qid"], ""))
            if a:
                abrahamic[r["qid"]] = a
    return temple, horus, abrahamic


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
    "哀": ("Job", "lamented"),
}
PINYIN_TEMPLE = {"taizu": "太祖", "gaozu": "高祖", "chengzu": "成祖", "taizong": "太宗", "gaozong": "高",
                 "shizong": "世", "shizu": "世", "renzong": "仁", "yingzong": "英", "xuanzong": "宣", "wuzong": "武",
                 "wenzong": "文", "muzong": "穆", "shenzong": "神", "xiaozong": "孝", "dezong": "德", "ruizong": "睿",
                 "zhongzong": "中", "suzong": "肅", "daizong": "代", "shunzong": "順", "jingzong": "敬",
                 "yizong": "懿", "xizong": "僖", "zhaozong": "昭", "guangzong": "光", "ningzong": "寧",
                 "lizong": "理", "duzong": "度", "mingzong": "明", "xingzong": "興", "zhangzong": "章"}


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
