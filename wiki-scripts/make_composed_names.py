"""
Write wikibase/analysis/composed_names.tsv: each gaiad.ged person's name in every language some label is in, COMPOSED
from the labels of the person's Wikidata name items, for the people who have no real Wikidata label in that language.

The method is the genealogy repo's (genealogy/scripts/namemodel.py `compose_label`, and `_name_parts` in
genealogy/scripts/build-garborg-day.py), ported here because the site build cannot import that repo:

  - the parts are the person's name items in name order: given names (P735, by their P1545 ordinal), then
    patronymics (P5056), then family names (P734); deprecated statements are skipped;
  - the name is written in a language only when EVERY part has a label there, nothing is transliterated or guessed;
  - the parts' own mul (else en) labels must spell the person's mul (else en) label word for word, in order, so the
    parts cover the whole name;
  - a part whose label is in the wrong script for the language counts as unlabelled (ja, zh and ko by the genealogy
    repo's LABEL_SCRIPT; other non-Latin languages by NON_LATIN below, which extends the same check);
  - ja parts are joined with a middle dot, zh with the interpunct, everything else with a space.

Rows are kept apart from real labels: a language where the person already has a Wikidata label gets no row, and a
row whose composed form is the person's own mul/en name letter for letter is dropped, since it adds nothing (most
Latin-script languages). Every row is a generated name; the GEDCOM side marks it so (language_gedcom.py).

Why a table and not gaiad.ged: the person-by-language product is tens of thousands of names across hundreds of
languages, and a GEDCOM reader gains nothing from 300 extra NAME lines per person. The table holds all of them;
each language directory's GEDCOM takes its own language from it.

Run here with network (Wikidata API); the site build only reads the TSV. Stdlib only.

    python wiki-scripts/make_composed_names.py <gaiad.ged> [cache.json]

With a cache path, the fetched entities are saved there and reused on the next run.
"""
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wikibase" / "analysis" / "composed_names.tsv"
UA = {"User-Agent": "order.life gaiad.ged builder (emma@topazcomputing.com)"}
NAME_PROPS = ("P735", "P5056", "P734")

_HAN = "㐀-䶿一-鿿豈-﫿"
CJK_SCRIPT = {
    "ja": re.compile("^[぀-ヿㇰ-ㇿ" + _HAN + "・･=＝]+$"),
    "zh": re.compile("^[" + _HAN + "·‧・]+$"),
    "ko": re.compile("^[가-힣ᄀ-ᇿ㄰-㆏" + _HAN + r"\s-]+$"),
}
ONLY_HIRAGANA = re.compile("^[぀-ゟー・]+$")
ZH_LIKE = {"zh", "yue", "wuu", "gan", "lzh", "hak", "cdo", "nan-hani", "zh-classical"}

# Languages written in a non-Latin script: a part's label there must be in that script, not the Latin name reused.
_SCRIPTS = {
    "Ѐ-ӿ": "ru uk be be-tarask bg mk sr sr-ec kk ky tg tt ba cv ce mn os sah udm mhr mrj myv mdf kv koi "
                     "krc lez av ab ady kbd inh tyv xal bxr rue cu kaa-cyrl lbe dar tab",
    "Ͱ-Ͽἀ-῿": "el grc pnt",
    "؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿": "ar fa ur ps ckb arz azb ug sd ks pnb mzn glk ary bal "
                                                         "skr lki bqi",
    "֐-׿": "he yi lad-hebr",
    "ऀ-ॿ": "hi mr ne sa mai bho new awa anp dty gom",
    "ঀ-৿": "bn as bpy mni",
    "਀-੿": "pa",
    "઀-૿": "gu",
    "଀-୿": "or",
    "஀-௿": "ta",
    "ఀ-౿": "te",
    "ಀ-೿": "kn tcy",
    "ഀ-ൿ": "ml",
    "඀-෿": "si",
    "฀-๿": "th",
    "຀-໿": "lo",
    "ក-៿": "km",
    "က-႟": "my shn mnw",
    "Ⴀ-ჿᲐ-Ჿ": "ka xmf",
    "԰-֏": "hy hyw",
    "ሀ-᎟": "am ti",
    "ༀ-࿿": "bo dz",
    "ހ-޿": "dv",
}
NON_LATIN = {lg: re.compile("[" + rng + "]") for rng, langs in _SCRIPTS.items() for lg in langs.split()}
LATIN = re.compile("[A-Za-zÀ-ɏ]")


def family(lang):
    base = lang.split("-")[0]
    if lang in ZH_LIKE or base == "zh":
        return "zh"
    return base if base in ("ja", "ko") else lang


def part_ok(text, lang):
    """A part's label counts in `lang` only in the right script (genealogy's LABEL_SCRIPT, extended), and only when
    it is one form: a label listing several ("Йохан / Юхан") or carrying a disambiguator ("Labán (nombre)") gives no
    single name to compose with."""
    if not text or any(c in text for c in "/()[]0123456789"):
        return False
    fam = family(lang)
    if fam in CJK_SCRIPT:
        return bool(CJK_SCRIPT[fam].match(text)) and not (fam == "ja" and ONLY_HIRAGANA.match(text))
    script = NON_LATIN.get(lang) or NON_LATIN.get(lang.split("-")[0])
    if script:
        return bool(script.search(text)) and not LATIN.search(text)
    return True


def compose(parts, lang, labels, whole):
    """genealogy's namemodel.compose_label over the fetched name-item labels; None when it cannot compose."""
    if not parts or not whole.strip():
        return None
    got = []
    for q in parts:
        text = (labels.get(q, {}).get(lang) or "").strip()
        if not part_ok(text, lang):
            return None
        # A part never gains words in translation: "Pericles o IVAN" for one word is a mislabelled item, not a name.
        own = (labels.get(q, {}).get("mul") or labels.get(q, {}).get("en") or "").split()
        if len(text.split()) > max(1, len(own)):
            return None
        got.append(text)
    latin = " ".join((labels.get(q, {}).get("mul") or labels.get(q, {}).get("en") or "") for q in parts)
    if latin.casefold().split() != whole.casefold().split():
        return None
    return {"ja": "・", "zh": "·"}.get(family(lang), " ").join(got)


def name_parts(entity):
    """genealogy's _name_parts: name-item QIDs in name order, unnumbered statements in the lowest free positions."""
    def ordered(prop):
        out = []
        for i, st in enumerate((entity.get("claims") or {}).get(prop) or []):
            if st.get("rank") == "deprecated":
                continue
            v = ((st.get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}
            if not isinstance(v, dict) or not v.get("id"):
                continue
            ords = [((q.get("datavalue") or {}).get("value") or "")
                    for q in (st.get("qualifiers") or {}).get("P1545") or []]
            try:
                key = int(ords[0]) if ords else None
            except ValueError:
                key = None
            out.append((key, i, v["id"]))
        taken = {k for k, _i, _q in out if k is not None}
        free = (n for n in range(1, len(out) + len(taken) + 2) if n not in taken)
        out = [(k if k is not None else next(free), i, q) for k, i, q in out]
        return [q for _k, _i, q in sorted(out)]
    return [q for p in NAME_PROPS for q in ordered(p)]


def get(ids, props):
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=" + props
           + "&ids=" + "|".join(ids))
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90))
        except (OSError, ValueError):
            time.sleep(5 * (attempt + 1))
    print(f"  gave up on a batch starting {ids[0]}", file=sys.stderr)
    return {}


def fetch(qids, props):
    batches = [qids[i:i + 50] for i in range(0, len(qids), 50)]
    out = {}
    with ThreadPoolExecutor(4) as pool:
        for n, res in enumerate(pool.map(lambda b: get(b, props), batches), 1):
            for q, e in (res.get("entities") or {}).items():
                if "missing" not in e:
                    out[q] = e
            if n % 50 == 0:
                print(f"  {props}: {n}/{len(batches)} batches")
    return out


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    qids = sorted(set(re.findall(r"^1 EXID (Q\d+)$", text, re.M)), key=lambda q: int(q[1:]))
    print(f"{len(qids)} people with a Wikidata id")
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if cache and cache.exists():
        people, labels = json.loads(cache.read_text(encoding="utf-8"))
    else:
        people = {q: {"labels": e.get("labels"), "claims": {p: e.get("claims", {}).get(p) for p in NAME_PROPS}}
                  for q, e in fetch(qids, "labels|claims").items()}
        items = sorted({p for e in people.values() for p in name_parts(e)}, key=lambda q: int(q[1:]))
        labels = {q: {lg: v.get("value", "") for lg, v in (e.get("labels") or {}).items()}
                  for q, e in fetch(items, "labels").items()}
        if cache:
            cache.write_text(json.dumps([people, labels], ensure_ascii=False), encoding="utf-8")
    parts = {q: name_parts(e) for q, e in people.items()}
    print(f"{sum(1 for ps in parts.values() if ps)} have name items; {len(labels)} distinct name items")
    rows, per_lang = [], Counter()
    for q in qids:
        e = people.get(q)
        if not e or not parts.get(q):
            continue
        live = {lg: v.get("value", "") for lg, v in (e.get("labels") or {}).items()}
        whole = live.get("mul") or live.get("en") or ""
        langs = sorted({lg for p in parts[q] for lg in labels.get(p, {})} - {"mul"})
        for lg in langs:
            if live.get(lg):
                continue
            got = compose(parts[q], lg, labels, whole)
            if got and got.casefold() != whole.casefold() and "\t" not in got:
                rows.append((q, lg, got))
                per_lang[lg] += 1
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("qid\tlang\tname\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"{len(rows)} generated names for {len({r[0] for r in rows})} people in {len(per_lang)} languages -> {OUT}")
    print("top languages: " + ", ".join(f"{lg} {n}" for lg, n in per_lang.most_common(15)))


if __name__ == "__main__":
    main()
