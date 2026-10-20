"""
Give everyone in a GEDCOM 7 file a coat of arms, for a GEDZIP (the coats-of-arms item; Emma's rule, 2026-10-20,
"Inherit, else invent"). Stdlib only; run by deploy.yml on each zip's GEDCOM.

A person's arms are, in order: their own real arms (wikibase/analysis/wikidata_arms.tsv, a Commons file, from
make_arms_table.py); else the nearest real arms up the father's line, then the mother's; else the arms their father's
line (then mother's) began with; and a founder of a line with no real arms gets an invented design from the pool
(static/arms/pool.txt, drawn by make_arms.py), pool[sha1(key) % pool size], where the key is the person's UID, else
their first EXID (the source's own id), so it does not change between builds.

The file gets one OBJE record per coat of arms borne, pointed to from each person who bears it. Invented arms are
copied into <zip dir>/media/arms/ as SVG and PNG and named by relative path, as GEDZIP wants; real arms are named by
their Commons URL (and, for an SVG, the PNG Commons renders from it).

    python wiki-scripts/gedcom_arms.py <in.ged> <out.ged> <zip dir>
"""
import csv
import hashlib
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARMS = ROOT / "static" / "arms"


def arms_key(blazon):
    """The file name (without extension) of an invented design's SVG and PNG in static/arms/ (as make_arms.py)."""
    return hashlib.sha1(blazon.encode()).hexdigest()[:12]


def commons(file, width=None):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(file.replace(" ", "_"))
    return f"{url}?width={width}" if width else url


def read_gedcom(lines):
    """Each INDI's key, Wikidata id and (father, mother)."""
    uid, exid, real_q, famc, fam = {}, {}, {}, {}, {}
    people, cur, kind = [], None, None
    for line in lines:
        if line.startswith("0 "):
            m = re.match(r"0 (@[^@]+@) (INDI|FAM)", line)
            cur, kind = (m.group(1), m.group(2)) if m else (None, None)
            if kind == "FAM":
                fam[cur] = {}
            elif kind == "INDI":
                people.append(cur)
        elif kind == "INDI":
            if line.startswith("1 UID "):
                uid[cur] = line[6:].strip()
            elif line.startswith("1 EXID "):
                exid.setdefault(cur, line[7:].strip())
                if re.fullmatch(r"Q\d+", line[7:].strip()):
                    real_q[cur] = line[7:].strip()
            elif line.startswith("1 FAMC "):
                famc.setdefault(cur, line[7:].strip())
        elif kind == "FAM":
            if line.startswith("1 HUSB "):
                fam[cur]["f"] = line[7:].strip()
            elif line.startswith("1 WIFE "):
                fam[cur]["m"] = line[7:].strip()
    # Most records have no UID; an EXID is the source's own id and does not move between builds as an xref can.
    key = {x: uid.get(x) or exid.get(x) or x for x in people}
    parents = {i: (fam.get(f, {}).get("f"), fam.get(f, {}).get("m")) for i, f in famc.items()}
    return key, real_q, parents


def assign(people, real, parents):
    """{xref: (kind, value, from_xref)} by the rule above; a parent still being worked out (a cycle) counts as absent."""
    done, busy = {}, set()

    def ups(p):
        return [] if p in real else [x for x in parents.get(p, (None, None)) if x in people]

    for start in people:
        # Depth-first without recursion: lines run thousands of generations deep.
        stack = [start]
        while stack:
            p = stack[-1]
            if p in done:
                stack.pop()
                continue
            if p not in busy:
                busy.add(p)
                stack += [x for x in ups(p) if x not in done and x not in busy]
                continue
            stack.pop()
            busy.discard(p)
            if p in real:
                done[p] = ("real", real[p], p)
                continue
            got = [done[x] for x in parents.get(p, (None, None)) if x in done]
            done[p] = next((x for x in got if x[0] == "real"), got[0] if got else ("invented", None, p))
    return done


def main():
    src, out, zdir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    text = src.read_text(encoding="utf-8-sig").splitlines()
    key, real_q, parents = read_gedcom(text)
    files = {}
    with open(ROOT / "wikibase" / "analysis" / "wikidata_arms.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            files[r["qid"]] = r["file"]
    real = {x: files[q] for x, q in real_q.items() if q in files}
    result = assign(set(key), real, parents)
    pool = (ARMS / "pool.txt").read_text(encoding="utf-8").splitlines()

    objs, bearer = {}, {}
    for x, (kind, value, src_x) in result.items():
        if kind == "invented":
            value = pool[int(hashlib.sha1(key[src_x].encode()).hexdigest(), 16) % len(pool)]
        bearer[x] = objs.setdefault((kind, value), f"@ARMS{len(objs) + 1}@")

    media = zdir / "media" / "arms"
    media.mkdir(parents=True, exist_ok=True)
    records = []
    for (kind, arms), xref in objs.items():
        if kind == "invented":
            k = arms_key(arms)
            for ext in ("svg", "png"):
                shutil.copyfile(ARMS / f"{k}.{ext}", media / f"{k}.{ext}")
            entries = [(f"media/arms/{k}.svg", "image/svg+xml"), (f"media/arms/{k}.png", "image/png")]
            title = arms
        else:
            svg = arms.lower().endswith(".svg")
            entries = [(commons(arms), "image/svg+xml" if svg else "image/jpeg" if re.search(r"\.jpe?g$", arms, re.I)
                        else "image/png")] + ([(commons(arms, 256), "image/png")] if svg else [])
            title = "Coat of arms"
        rec = [f"0 {xref} OBJE"]
        for path, form in entries:
            rec += [f"1 FILE {path}", f"2 FORM {form}", f"2 TITL {title}"]
        records.append("\n".join(rec))

    lines = []
    for line in text:
        if line == "0 TRLR":
            lines += records
        lines.append(line)
        m = re.match(r"0 (@[^@]+@) INDI", line)
        if m and m.group(1) in bearer:
            lines.append(f"1 OBJE {bearer[m.group(1)]}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    kinds = [k for k, _, _ in result.values()]
    print(f"arms: {len(result)} people, {kinds.count('real')} with real arms ({len(real)} their own), "
          f"{kinds.count('invented')} invented from {sum(1 for x, r in result.items() if r[2] == x and r[0] == 'invented')}"
          f" founders; {len(objs)} OBJE records -> {out}")


if __name__ == "__main__":
    main()
