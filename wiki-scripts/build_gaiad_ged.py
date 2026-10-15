"""
Build /gaiad.ged: one GEDCOM, strictly from the text, then Emma's ancestry. Emma's specification, 2026-10-15.

  I1 Aster, I2 Emma Leonhart, I3 Andromeda   the first three, ceremonial order
  then every other individual                one per distinct {{c|...}} tag name, in order of first appearance
                                             in the Gaiad (chapter 1 onward, line by line). "Strictly text only":
                                             false positives are fine and there are no links among them; splits
                                             and merges come later, by UUIDs put into the tags.
  then Emma's ancestry                       her family tree file (Gaiad/ancestry/second_attempt.ged, her
                                             FamilySearch tree from RootsMagic), appended with its families,
                                             her own record resolved as I2.

    python wiki-scripts/build_gaiad_ged.py [out.ged]

Stdlib only.
"""
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPIC = ROOT / "Gaiad" / "epic"
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "second_attempt.ged"
TAG = re.compile(r"\{\{c\|(?:[^}|]*\|)?([^}|]+)\}\}")
TITLE = re.compile(r"^#\s+(?:Chapter\s+\d+:\s*)?(.*)")
NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://order.life/gaiad/individual/")
FIRST = [("Aster", "Aster"), ("Emma Leonhart", "Emma /Leonhart/"), ("Andromeda", "Andromeda")]
EMMA_FS = "PFR5-LDS"


def appearances():
    """(name, chapter, stanza) for each distinct tag name, in order of first appearance."""
    seen, out = set(), []
    for n in range(1, 365):
        f = EPIC / f"chapter_{n:03d}.md"
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8").replace("\r", "")
        m = TITLE.match(raw)
        body = raw[m.end():].lstrip("\n") if m else raw
        for si, st in enumerate((s for s in re.split(r"\n\s*\n", body) if s.strip()), 1):
            for t in TAG.finditer(st):
                name = t.group(1).strip()
                if name and name not in seen:
                    seen.add(name)
                    out.append((name, n, si))
    return out


def ancestry_records():
    """The ancestry file's level-0 records, as (xref, tag, [lines]), HEAD/TRLR/SUBM dropped."""
    recs, cur = [], None
    for line in ANCESTRY.read_text(encoding="utf-8-sig").replace("\r", "").split("\n"):
        if not line:
            continue
        if line.startswith("0 "):
            if cur:
                recs.append(cur)
            parts = line.split(" ", 2)
            cur = (parts[1], parts[2].strip() if len(parts) > 2 else "", []) if parts[1].startswith("@") else None
            continue
        if cur:
            cur[2].append(line)
    if cur:
        recs.append(cur)
    return [r for r in recs if r[1] in ("INDI", "FAM")]


def build(out_path):
    w = []
    add = w.append
    stamp = datetime.now(timezone.utc)
    add("0 HEAD")
    add("1 GEDC")
    add("2 VERS 7.0")
    add("1 SOUR ORDERLIFE")
    add("2 NAME The Gaiad - order.life")
    add(f"1 DATE {stamp.day} {['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][stamp.month-1]} {stamp.year}")
    add("1 NOTE The individuals of the Gaiad in order of first appearance (I1 Aster, I2 Emma Leonhart, I3 Andromeda first),")
    add("2 CONT strictly from the text; then Emma Leonhart's ancestry from her family tree.")
    add("0 @S1@ SOUR")
    add("1 TITL The Gaiad")
    add("1 WWW https://order.life/gaiad/")

    apps = appearances()
    first_seen = {name: (ch, st) for name, ch, st in apps}
    n = 0

    def indi(name, ged_name, where):
        nonlocal n
        n += 1
        add(f"0 @I{n}@ INDI")
        add(f"1 NAME {ged_name}")
        add(f"1 REFN {n}")
        add("2 TYPE Gaiad individual number")
        add(f"1 UID {uuid.uuid5(NS, name)}")
        if where:
            ch, st = where
            add("1 SOUR @S1@")
            add(f"2 PAGE Gaiad {ch}.{st}")
            add(f"1 NOTE First named in the Gaiad, chapter {ch} (https://order.life/gaiad/{ch:03d}/#s{st}).")

    for name, ged in FIRST:
        indi(name, ged, first_seen.get(name))
    firsts = {f[0] for f in FIRST}
    for name, ch, st in apps:
        if name not in firsts:
            indi(name, name, (ch, st))
    n_text = n

    # Emma's ancestry, renumbered after the text block; her own record becomes I2.
    recs = ancestry_records() if ANCESTRY.exists() else []
    emma_x = next((x for x, tag, lines in recs if tag == "INDI" and any(EMMA_FS in l for l in lines)), None)
    imap, fmap, nf = {}, {}, 0
    for x, tag, _ in recs:
        if tag == "INDI":
            if x == emma_x:
                imap[x] = "@I2@"
            else:
                n += 1
                imap[x] = f"@I{n}@"
        else:
            nf += 1
            fmap[x] = f"@F{nf}@"
    ptr = re.compile(r"@[^@\s]+@")
    emma_links = []
    for x, tag, lines in recs:
        fixed = [ptr.sub(lambda m: imap.get(m.group(0)) or fmap.get(m.group(0)) or m.group(0), l) for l in lines]
        if x == emma_x:
            emma_links = [l for l in fixed if l.startswith(("1 FAMC", "1 FAMS"))]
            continue
        add(f"0 {imap.get(x) or fmap.get(x)} {tag}")
        w.extend(fixed)
    # Graft Emma's family links onto I2 (inserted after her REFN line).
    if emma_links:
        i = w.index("0 @I2@ INDI")
        w[i + 2:i + 2] = emma_links
    add("0 TRLR")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(w) + "\n", encoding="utf-8-sig", newline="\n")
    return {"text individuals": n_text, "ancestry individuals": n - n_text, "families": nf,
            "bytes": out_path.stat().st_size}


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "gaiad.ged"
    for k, v in build(dest).items():
        print(f"  {k}: {v:,}")
