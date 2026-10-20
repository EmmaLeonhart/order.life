"""
Put the portraits (static/portraits/, scripts/make_portraits.py) into a GEDCOM 7 file (Emma, 2026-10-20: "And in the
gedcom of course"). A person gets a portrait when their record links the portrait's Gaiad character page or carries
one of its ids (static/portraits/index.tsv). With a zip dir, the image is copied into <zip dir>/media/portraits/ and
named by relative path, as GEDZIP wants; without one, it is named by its URL on order.life. Stdlib only; run by
deploy.yml.

    python wiki-scripts/gedcom_portraits.py <in.ged> <out.ged> [zip dir]
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTRAITS = ROOT / "static" / "portraits"


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    zdir = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    match, names = {}, {}
    for row in (PORTRAITS / "index.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        file, name, keys = row.split("\t")
        names[file] = name
        match.update({k: file for k in keys.split(",")})

    text = src.read_text(encoding="utf-8-sig").splitlines()
    # Which INDI bears which portrait: a character-page link in its notes, or an EXID.
    bearer, cur = {}, None
    for line in text:
        if line.startswith("0 "):
            m = re.match(r"0 (@[^@]+@) INDI", line)
            cur = m.group(1) if m else None
        elif cur and cur not in bearer:
            keys = re.findall(r"order\.life/gaiad/characters/([a-z0-9_-]+)/", line)
            if line.startswith("1 EXID "):
                keys.append(line[7:].strip())
            hit = next((match[k] for k in keys if k in match), None)
            if hit:
                bearer[cur] = hit

    objs = {f: f"@PORTRAIT{i + 1}@" for i, f in enumerate(sorted(set(bearer.values())))}
    if zdir:
        (zdir / "media" / "portraits").mkdir(parents=True, exist_ok=True)
    records = []
    for f, xref in objs.items():
        if zdir:
            shutil.copyfile(PORTRAITS / f, zdir / "media" / "portraits" / f)
            path = f"media/portraits/{f}"
        else:
            path = f"https://order.life/static/portraits/{f}"
        records.append(f"0 {xref} OBJE\n1 FILE {path}\n2 FORM image/jpeg\n2 TITL Portrait of {names[f]} "
                       "(imagined; made with a local model, CC0)")

    lines = []
    for line in text:
        if line == "0 TRLR":
            lines += records
        lines.append(line)
        m = re.match(r"0 (@[^@]+@) INDI", line)
        if m and m.group(1) in bearer:
            lines.append(f"1 OBJE {objs[bearer[m.group(1)]]}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"portraits: {len(bearer)} people given {len(objs)} portraits -> {out}")


if __name__ == "__main__":
    main()
