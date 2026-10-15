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
    return temple, horus
