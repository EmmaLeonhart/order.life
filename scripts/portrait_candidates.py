"""
Choose who gets a portrait in the larger batch (Emma, 2026-10-20: "More portraits too", everyone with a character
page and no likeness from life) and write scripts/portrait_batch.tsv for scripts/make_portraits.py.

Many character files are not people (peoples, empires, words), so "everyone" is read as the people in gaiad.ged whose
record links a character page. Left out: anyone Wikidata gives an image (P18) and a birth from 1400 on, whose likeness
from life exists; haplogroups; and those already in make_portraits.py's hand-written batch. Each row's description is
Wikidata's and the first line the Gaiad cites the character in. Ordered by how often the Gaiad cites them, so the
most-read people are drawn first. Run here with network.

    python scripts/portrait_candidates.py <gaiad.ged>
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "portrait_batch.tsv"
UA = {"User-Agent": "order.life portraits (emma@topazcomputing.com)"}
HAND = {"abraham", "david", "rama", "hammurabi", "zarathustra", "zoroaster", "huangdi", "yellow_emperor", "ashoka",
        "confucius", "cain", "abel", "seth", "makeda"}


def wikidata(qids):
    info = {}
    for i in range(0, len(qids), 50):
        url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=claims|descriptions&languages=en"
               "&format=json&ids=" + "|".join(qids[i:i + 50]))
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        for q, e in d.get("entities", {}).items():
            c = e.get("claims", {})
            birth = None
            for x in c.get("P569", []):
                t = x["mainsnak"].get("datavalue", {}).get("value", {}).get("time")
                if t:
                    m = re.match(r"([+-])0*(\d+)", t)
                    birth = int(m.group(2)) * (-1 if m.group(1) == "-" else 1)
                    break
            info[q] = {"image": bool(c.get("P18")), "birth": birth,
                       "desc": e.get("descriptions", {}).get("en", {}).get("value", "")}
        time.sleep(0.1)
    return info


def main():
    people = {}   # slug: {"q": wikidata id or None, "ids": [...]}
    cur = None
    for line in Path(sys.argv[1]).read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("0 "):
            cur = {"slugs": [], "ids": []} if re.match(r"0 @[^@]+@ INDI", line) else None
            continue
        if cur is None:
            continue
        if line.startswith("1 EXID "):
            cur["ids"].append(line[7:].strip())
        for slug in re.findall(r"order\.life/gaiad/characters/([a-z0-9_-]+)/", line):
            if slug not in people:
                people[slug] = cur
    rows, qids = [], set()
    for slug, rec in people.items():
        f = ROOT / "Gaiad" / "genealogy" / f"{slug}.json"
        if slug in HAND or not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        name = d["name"]
        if re.search(r"haplogroup", name, re.I) or re.match(r"^[A-T]\d", name):
            continue
        q = d.get("wikidata_qid") or next((i for i in rec["ids"] if re.fullmatch(r"Q\d+", i)), None)
        qids.add(q)
        cites = d.get("citations", [])
        lines = [re.sub(r"\{\{[cpx]\|(?:[^}|]*\|)?([^}|]+)\}\}", r"\1", c["line"]) for c in cites]
        first = next((x for x in lines if name in x), lines[0] if lines else "")   # a line naming them, if any
        rows.append({"slug": slug, "name": name, "q": q, "first": first.strip(),
                     "n": len(cites) or len(d.get("chapters_mentioned_in", [])),
                     "match": [slug] + [i for i in rec["ids"] if "\t" not in i and "," not in i]})
    info = wikidata(sorted(q for q in qids if q))
    out, skipped = [], 0
    for r in rows:
        w = info.get(r["q"], {})
        if w.get("image") and w.get("birth") is not None and w["birth"] >= 1400:
            skipped += 1
            continue
        # Both, where there are both: a character file's Wikidata id can be a namesake (plato.json's is a son of Lycaon).
        desc = "; ".join(x for x in (w.get("desc"), f"in the Gaiad: {r['first']}" if r["first"] else "") if x) \
            or "figure of the Gaiad"
        out.append((r["n"], r["slug"], r["name"], re.sub(r"\s+", " ", desc), ",".join(r["match"])))
    out.sort(key=lambda r: (-r[0], r[1]))
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("slug\tname\tdescription\tmatch\n")
        for _, slug, name, desc, match in out:
            fh.write(f"{slug}\t{name}\t{desc}\t{match}\n")
    print(f"{len(people)} character pages linked from gaiad.ged; {len(out)} to draw, {skipped} left out as having a "
          f"likeness from life -> {OUT}")


if __name__ == "__main__":
    main()
