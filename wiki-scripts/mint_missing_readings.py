"""
Write wikibase/analysis/name_readings_minted.tsv: ja/zh/ko readings for the name words of gaiad.ged's people that
name_readings.tsv does not have, so that one unknown word no longer leaves a whole name without its Chinese,
Japanese and Korean forms (Emma, 2026-10-17: "you should have them because of the very source").

ja and zh come from the genealogy repo's transliteration engine (genealogy/scripts/translit_no.py), the same rule
the table's own "by rule" rows were minted with; ko is read from the katakana. The hand table always wins: this file
only adds words it lacks. Run here (needs the genealogy checkout beside order.life); the site build reads the TSV.

    python wiki-scripts/mint_missing_readings.py [gaiad.ged]
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "wikibase" / "analysis" / "name_readings.tsv"
OUT = ROOT / "wikibase" / "analysis" / "name_readings_minted.tsv"
sys.path.insert(0, str(ROOT.parent / "genealogy" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translit_no import translit  # noqa: E402
from gedcom_features import clean_name_token, special_token  # noqa: E402

# Katakana to Hangul, syllable by syllable (two-kana sounds first).
KANA2 = {"キャ": "캬", "キュ": "큐", "キョ": "쿄", "シャ": "샤", "シュ": "슈", "ショ": "쇼", "チャ": "차", "チュ": "추",
         "チョ": "초", "ニャ": "냐", "ニュ": "뉴", "ニョ": "뇨", "ヒャ": "햐", "ヒュ": "휴", "ヒョ": "효", "ミャ": "먀",
         "ミュ": "뮤", "ミョ": "묘", "リャ": "랴", "リュ": "류", "リョ": "료", "ギャ": "갸", "ギュ": "규", "ギョ": "교",
         "ジャ": "자", "ジュ": "주", "ジョ": "조", "ビャ": "뱌", "ビュ": "뷰", "ビョ": "뵤", "ピャ": "퍄", "ピュ": "퓨",
         "ピョ": "표", "ファ": "파", "フィ": "피", "フェ": "페", "フォ": "포", "ティ": "티", "ディ": "디", "トゥ": "투",
         "ドゥ": "두", "ウィ": "위", "ウェ": "웨", "ウォ": "워", "ヴァ": "바", "ヴィ": "비", "ヴェ": "베", "ヴォ": "보",
         "シェ": "셰", "ジェ": "제", "チェ": "체", "イェ": "예", "デュ": "듀", "テュ": "튜"}
KANA1 = dict(zip("アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲ"
                 "ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポヴ",
                 "아이우에오카키쿠케코사시스세소타치쓰테토나니누네노하히후헤호마미무메모야유요라리루레로와오"
                 "가기구게고자지즈제조다지즈데도바비부베보파피푸페포부"))


def kana_to_hangul(k):
    out, i = [], 0
    while i < len(k):
        two = k[i:i + 2]
        if two in KANA2:
            out.append(KANA2[two]); i += 2; continue
        c = k[i]
        if c == "ン" and out:
            out[-1] = add_final(out[-1], 4)          # ㄴ
        elif c == "ッ" and out:
            out[-1] = add_final(out[-1], 19)         # ㅅ
        elif c == "ー":
            pass
        elif c in "・ ":
            out.append(" ")
        elif c in KANA1:
            out.append(KANA1[c])
        elif c in "ァィゥェォ":
            out.append({"ァ": "아", "ィ": "이", "ゥ": "우", "ェ": "에", "ォ": "오"}[c])
        else:
            return ""
        i += 1
    return "".join(out).strip()


def add_final(syl, fin):
    o = ord(syl) - 0xAC00
    if 0 <= o < 11172 and o % 28 == 0:
        return chr(0xAC00 + o + fin)
    return syl


def main(ged):
    have = set()
    with open(TABLE, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            have.add(r["token"].casefold())
    words = {}
    for line in open(ged, encoding="utf-8-sig"):
        if not line.startswith("1 NAME "):
            continue
        for w in re.split(r"[\s/]+", line[7:].strip()):
            w = clean_name_token(w)
            if not w or special_token(w) or w.casefold() in have or re.search(r"[^\w'\-]", w):
                continue
            if not re.search(r"[A-Za-z]", unicodedata.normalize("NFKD", w)):
                continue   # only Latin-script words: CJK, Arabic and the rest are not read by this engine
            words.setdefault(w.casefold(), w)
    rows = []
    for key, w in sorted(words.items()):
        ja, zh = translit(w)
        ko = kana_to_hangul(ja) if ja else ""
        if ja and zh and ko:
            rows.append((w, ja, zh, ko))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("token\tja\tzh\tko\tnote\n")
        for w, ja, zh, ko in rows:
            f.write(f"{w}\t{ja}\t{zh}\t{ko}\tby rule, minted 2026-10-17 for gaiad.ged (translit_no; ko from kana)\n")
    print(f"{len(words)} missing words, {len(rows)} minted -> {OUT}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "scratch" / "gaiad-english.ged")
