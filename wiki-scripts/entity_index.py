"""
Write the person index behind https://order.life/wikibase/entity/Q<n>, the URL the GEDCOM's EXIDs name.

build.py calls this to write small JSON buckets, site/wikibase/entity/_index/<n // 1000>.json, and a
static page per person, site/wikibase/entity/Q<n>.html, so the URL answers 200 (templates/404.html still
shows a record from its bucket if the page is missing). Each shows: label, dates, parents and children
(each linked the same way), the Gaiad character page if there is one, Wikidata and Geni. It is also what a Wikidata property for
order.life ids would point at (planning/wikidata-property-proposal.md). Stdlib only.
"""
import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANA = ROOT / "wikibase" / "analysis"
GEN = ROOT / "Gaiad" / "genealogy"


def year_of(ts):
    if not ts:
        return ""
    m = re.match(r"([+-]?)0*(\d+)-(\d\d)-(\d\d)", ts.strip())
    if not m:
        return ""
    y = int(m.group(2))
    return f"{y} BCE" if m.group(1) == "-" else str(y)


def build(out_dir):
    persons = {}
    with open(ANA / "persons.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            persons[r["qid"]] = r
    parents, children = defaultdict(list), defaultdict(list)
    with open(ANA / "edges.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            parents[r["child"]].append(r["parent"])
            children[r["parent"]].append(r["child"])
    page = {}
    for f in GEN.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("qid") and d.get("name"):
            slug = re.sub(r"[^a-zA-Z0-9_-]", "", d["name"].replace(" ", "_")).lower()
            if slug:
                page.setdefault(d["qid"], slug)
    portraits = {}   # {slug or id: file}, static/portraits/index.tsv from scripts/make_portraits.py
    index = ROOT / "static" / "portraits" / "index.tsv"
    if index.exists():
        for row in index.read_text(encoding="utf-8").splitlines()[1:]:
            file, _, match = row.split("\t")
            portraits.update({m: file for m in match.split(",")})
    buckets = defaultdict(dict)
    for q, r in persons.items():
        if not q[1:].isdigit():
            continue
        rec = {"l": (r.get("label") or "").strip(), "b": year_of(r.get("birth")), "d": year_of(r.get("death")),
               "p": parents.get(q, [])[:4], "c": children.get(q, [])[:60]}
        if r.get("wikidata_qid"):
            rec["w"] = r["wikidata_qid"]
        if (r.get("geni_id") or "").isdigit():
            rec["g"] = r["geni_id"]
        if q in page:
            rec["s"] = page[q]
        if page.get(q) in portraits or r.get("wikidata_qid") in portraits:
            rec["i"] = f"/static/portraits/{portraits.get(page.get(q)) or portraits[r['wikidata_qid']]}"
        buckets[int(q[1:]) // 1000][q] = rec
    # Names of linked people travel with each record's bucket only, so a record shows its relatives' labels.
    for b in buckets.values():
        for rec in b.values():
            rec["n"] = {x: (persons.get(x, {}).get("label") or x).strip() for x in rec["p"] + rec["c"]}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for k, b in buckets.items():
        (out_dir / f"{k}.json").write_text(json.dumps(b, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        # A real page per record, so /wikibase/entity/Q<n> answers 200 (GitHub Pages serves Q<n>.html there);
        # through 404.html alone the record showed but the status was 404.
        for q, rec in b.items():
            (out_dir.parent / f"{q}.html").write_text(entity_page(q, rec), encoding="utf-8")
    return len(persons), len(buckets)


def entity_page(q, r):
    """The same record 404.html renders from the bucket, as static HTML."""
    esc = html.escape
    label = r["l"] or q

    def link(x):
        return f'<a href="/wikibase/entity/{x}">{esc(r["n"].get(x) or x)}</a>'

    dates = f' · {esc(r["b"] or "?")} – {esc(r["d"])}' if r["b"] or r["d"] else ""
    body = f'<div class="section-hero"><h1>{esc(label)}</h1><p>order.life {q}{dates}</p></div>'
    if r.get("i"):
        body += (f'<div class="container"><img src="{r["i"]}" alt="Portrait of {esc(label)}" width="224" '
                 'height="288" style="display:block;margin:1rem auto;border-radius:6px"></div>')
    body += '<div class="container section-content">'
    if r["p"]:
        body += "<p><strong>Parents:</strong> " + ", ".join(map(link, r["p"])) + "</p>"
    if r["c"]:
        body += "<p><strong>Children:</strong> " + ", ".join(map(link, r["c"])) + "</p>"
    out = []
    if r.get("s"):
        out.append(f'<a href="/gaiad/characters/{r["s"]}/">In the Gaiad</a>')
    if r.get("w"):
        out.append(f'<a href="https://www.wikidata.org/wiki/{r["w"]}">Wikidata {r["w"]}</a>')
    if r.get("g"):
        out.append(f'<a href="https://www.geni.com/profile/index/{r["g"]}">Geni</a>')
    out.append('<a href="/gaiad.ged" download>the whole tree (GEDCOM 7)</a>')
    body += "<p>" + " · ".join(out) + "</p></div>"
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"<title>{esc(label)} — order.life {q}</title>\n"
            '<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">\n'
            '<link rel="stylesheet" href="/static/css/style.css">\n</head>\n'
            f"<body>\n{body}\n<footer><p>命道教 · Lifeism · Order of Life</p></footer>\n</body>\n</html>\n")


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1] if len(sys.argv) > 1 else "entity_index_out"))
