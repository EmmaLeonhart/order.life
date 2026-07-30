#!/usr/bin/env python
"""Audit every wikidata_qid in the dump against Wikidata itself. READ-ONLY.

    python wiki-scripts/audit_wikidata_ids.py [--limit N]

~56% of the dump's 107k people carry a `wikidata_qid`. Those IDs are load-bearing —
they are the only external check on who a record actually is — and spot-checking the
ancestry-cycle nodes turned up `Ops` pointing at Paul Bildt, a Dutch film actor, and
`Tros` pointing at Uranus. This walks all of them and writes
`wikibase/analysis/qa_wikidata_ids.tsv`.

Per record it reports the worst thing it finds:

  missing        the Wikidata item does not exist (deleted or never did)
  not_a_human    the item exists but is not an instance of human — a film, a place,
                 a disambiguation page. Mythological figures are allowed: Q5 plus the
                 usual mythic classes count as fine
  sex_conflict   both sides record a sex and they disagree
  name_mismatch  labels and aliases share nothing; likely a different person entirely
  unverifiable   the local label is a placeholder (NN) or Wikidata has no label at all,
                 so the id can be neither confirmed nor faulted
  shared_id      several local records claim the same Wikidata item. At most one can
                 be right unless they are duplicates of each other
  ok             label or an alias matches

Results are cached in `.wikidata_cache_full.json`, so a re-run resumes rather than
refetching. Requests go 50 ids at a time with a pause between batches.
"""

import argparse
import csv
import threading
from concurrent.futures import ThreadPoolExecutor
import io
import json
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "wikibase" / "analysis"
OUT = ANALYSIS / "qa_wikidata_ids.tsv"
CACHE = ANALYSIS / ".wikidata_cache_full.json"

API = "https://www.wikidata.org/w/api.php"
UA = "order.life-genealogy-qa/1.0 (emma@topazcomputing.com)"
BATCH = 50
PAUSE = 0.15
# Wikidata serves 50-id batches comfortably; a serial walk of 60k ids takes ~3 hours,
# so batches are fetched by a small worker pool. Kept modest deliberately — this is
# someone else's server and the audit is not urgent.
WORKERS = 8
NAME_BAR = 0.75
# Local labels that carry no identifying information, so nothing can be checked.
PLACEHOLDERS = {"", "nn", "n n", "unknown", "unnamed", "no label", "n"}

HUMAN_CLASSES = {
    "Q5",           # human
    "Q22989102",    # Greek deity
    "Q178885",      # deity
    "Q11688446",    # Roman deity
    "Q95074",       # fictional character
    "Q15632617",    # fictional human
    "Q3241972",     # mythological Greek character
    "Q22988604",    # Roman mythological character
    "Q4271324",     # mythical character
    "Q13002315",    # legendary figure
    "Q21070598",    # semi-legendary figure
    "Q193291",      # spirit
    "Q2239243",     # mythological creature
    # A genealogy that runs from Adam through Greek myth into Japanese kami needs a
    # wide notion of "person". These are all classes the audit's first pass wrongly
    # flagged as non-human on records whose names matched perfectly.
    "Q20643955",    # human biblical figure
    "Q21070568",    # human whose existence is disputed
    "Q124710051",   # legendary human figure
    "Q3346693",     # Greek nymph
    "Q182037",      # naiad
    "Q182406",      # Oceanid
    "Q3027575",     # Potamoi
    "Q3059255",     # Greek water deity
    "Q1916821",     # water deity
    "Q28061975",    # group of Greek mythical characters
    "Q524158",      # kami
    "Q60995523",    # kunitsukami
    "Q60994492",    # amatsukami
    "Q75855169",    # mythical Japanese figure
    "Q16513904",    # character in Germanic heroic legend
    "Q131087",      # valkyrie
    "Q11688446",    # Roman deity
    "Q16334295",    # group of humans
    "Q14524493",    # legendary creature
}

MALE_LOCAL, FEMALE_LOCAL = "Q153718", "Q153719"
MALE_WD, FEMALE_WD = "Q6581097", "Q6581072"

csv.field_size_limit(10_000_000)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s or "")
                if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def name_score(local, names):
    ln = norm(local)
    if not ln or not names:
        return 0.0
    best = 0.0
    for n in names:
        nn = norm(n)
        if not nn:
            continue
        if ln == nn:
            return 1.0
        # a bare given name inside a fuller one is a match, not a mismatch
        if len(ln) > 3 and (ln in nn or nn in ln):
            best = max(best, 0.9)
        best = max(best, SequenceMatcher(None, ln, nn).ratio())
    return best


def script_of(s):
    """Coarse writing system of a string, for deciding whether two names are comparable."""
    for ch in s or "":
        if not ch.isalpha():
            continue
        name = unicodedata.name(ch, "")
        for tag in ("LATIN", "CJK", "HIRAGANA", "KATAKANA", "ARABIC", "CYRILLIC",
                    "HEBREW", "GREEK", "DEVANAGARI", "HANGUL", "ARMENIAN", "GEORGIAN"):
            if name.startswith(tag):
                return "CJK" if tag in ("HIRAGANA", "KATAKANA") else tag
    return ""


def comparable(local, names):
    """False when the local label and every Wikidata name are in different scripts.

    'Ahmad ibn Aqil ibn Abi Talib' against an item labelled only in Arabic is not a
    mismatch, it is a transliteration this script cannot judge.
    """
    ls = script_of(local)
    if not ls:
        return False
    return any(script_of(n) == ls for n in names)


def claim_ids(entity, prop):
    out = []
    for c in entity.get("claims", {}).get(prop, []):
        snak = c.get("mainsnak", {})
        if snak.get("snaktype") != "value":
            continue
        v = snak.get("datavalue", {}).get("value", {})
        if isinstance(v, dict) and "id" in v:
            out.append(v["id"])
    return out


def load_cache():
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            sys.stderr.write("cache unreadable, starting over\n")
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="only check the first N ids (for a quick sample)")
    args = ap.parse_args()

    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as fh:
        persons = list(csv.DictReader(fh, delimiter="\t"))

    holders = defaultdict(list)          # wikidata qid -> [local qids]
    for p in persons:
        w = (p.get("wikidata_qid") or "").strip()
        if re.fullmatch(r"Q\d+", w):
            holders[w].append(p["qid"])

    wanted = sorted(holders)
    if args.limit:
        wanted = wanted[:args.limit]
    print("local people: %d | carrying a wikidata_qid: %d | distinct ids: %d"
          % (len(persons), sum(len(v) for v in holders.values()), len(holders)))

    cache = load_cache()
    todo = [q for q in wanted if q not in cache]
    print("to fetch: %d (cached: %d)\n" % (len(todo), len(wanted) - len(todo)))

    local = threading.local()

    def session():
        if not hasattr(local, "s"):
            local.s = requests.Session()
            local.s.headers["User-Agent"] = UA
        return local.s

    lock = threading.Lock()
    done = [0]

    def fetch_batch(chunk):
        for attempt in range(4):
            try:
                r = session().get(API, params={
                    "action": "wbgetentities", "ids": "|".join(chunk),
                    "format": "json", "props": "claims|labels|aliases",
                }, timeout=90)
                r.raise_for_status()
                ents = r.json().get("entities", {})
                break
            except Exception as exc:                       # noqa: BLE001
                if attempt == 3:
                    sys.stderr.write("  giving up on a batch: %s\n" % exc)
                    return
                time.sleep(3 * (attempt + 1))
        got = {}
        for qid in chunk:
            e = ents.get(qid) or {}
            if not e or "missing" in e:
                got[qid] = None
                continue
            names = [v["value"] for v in e.get("labels", {}).values()]
            for al in e.get("aliases", {}).values():
                names += [a["value"] for a in al]
            got[qid] = {"names": names, "p31": claim_ids(e, "P31"),
                        "sex": claim_ids(e, "P21")}
        with lock:
            cache.update(got)
            done[0] += len(chunk)
            if done[0] % 2500 < BATCH:
                CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                sys.stderr.write("  %d/%d fetched\n" % (done[0], len(todo)))
        time.sleep(PAUSE)

    chunks = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(fetch_batch, chunks))

    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    by_qid = {p["qid"]: p for p in persons}
    out_rows = []
    for w in wanted:
        e = cache.get(w)
        locals_ = holders[w]
        for lq in locals_:
            p = by_qid[lq]
            label = " ".join((p.get("label") or "").split())
            if e is None:
                verdict, detail, score = "missing", "no such Wikidata item", 0.0
            else:
                score = name_score(label, e["names"])
                wd_name = e["names"][0] if e["names"] else "(no label)"
                if e["p31"] and not (set(e["p31"]) & HUMAN_CLASSES):
                    verdict = "not_a_human"
                    detail = "Wikidata item is '%s', instance of %s" % (
                        wd_name, ", ".join(e["p31"][:3]))
                elif len(locals_) > 1:
                    verdict = "shared_id"
                    detail = "%d local records claim this same item ('%s'): %s" % (
                        len(locals_), wd_name, ", ".join(locals_))
                elif (norm(label) in PLACEHOLDERS or not e["names"]
                      or re.fullmatch(r"q\d+", norm(label))
                      or not comparable(label, e["names"])):
                    verdict = "unverifiable"
                    detail = ("local '%s' vs Wikidata '%s' — placeholder or a "
                              "different writing system, so the id can be neither "
                              "confirmed nor faulted" % (label, wd_name))
                elif score < NAME_BAR:
                    verdict = "name_mismatch"
                    detail = "local '%s' vs Wikidata '%s'" % (label, wd_name)
                else:
                    ls = p.get("sex")
                    ws = e["sex"][0] if e["sex"] else None
                    conflict = ((ls == MALE_LOCAL and ws == FEMALE_WD)
                                or (ls == FEMALE_LOCAL and ws == MALE_WD))
                    if conflict:
                        verdict = "sex_conflict"
                        detail = "local sex and Wikidata sex disagree for '%s'" % wd_name
                    else:
                        verdict, detail = "ok", "matches '%s'" % wd_name
            out_rows.append({
                "qid": lq, "label": label, "wikidata_qid": w,
                "verdict": verdict, "name_score": "%.2f" % score, "detail": detail,
            })

    out_rows.sort(key=lambda r: (r["verdict"] == "ok", r["verdict"], r["qid"]))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        wtr = csv.DictWriter(fh, delimiter="\t", lineterminator="\n",
                             fieldnames=["qid", "label", "wikidata_qid", "verdict",
                                         "name_score", "detail"])
        wtr.writeheader()
        wtr.writerows(out_rows)

    counts = Counter(r["verdict"] for r in out_rows)
    total = len(out_rows)
    print("\nwrote %s" % OUT)
    print("records checked: %d" % total)
    for k, n in counts.most_common():
        print("  %-14s %6d  (%5.2f%%)" % (k, n, 100.0 * n / total))
    bad = total - counts["ok"]
    print("\nsuspect: %d of %d (%.2f%%)" % (bad, total, 100.0 * bad / total))
    print("\nworst name mismatches:")
    for r in sorted((r for r in out_rows if r["verdict"] == "name_mismatch"),
                    key=lambda r: float(r["name_score"]))[:25]:
        print("  %-9s %-32s -> %-11s %s"
              % (r["qid"], r["label"][:32], r["wikidata_qid"], r["detail"][:70]))


if __name__ == "__main__":
    main()
