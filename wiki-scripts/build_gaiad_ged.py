"""
Build /gaiad.ged: one GEDCOM, strictly from the text, then Emma's ancestry. Emma's specification, 2026-10-15.

  I1 Aster, I2 Emma Leonhart, I3 Andromeda   the first three, ceremonial order
  then every other individual                one per distinct {{c|...}} tag name, in order of first appearance
                                             in the Gaiad (chapter 1 onward, line by line). "Strictly text only":
                                             false positives are fine and there are no links among them; splits
                                             and merges come later, by UUIDs put into the tags.
  then Emma's ancestry                       the synoptic tree (every GEDCOM in the repo joined on exact ids)
                                             trimmed to her ancestors and every family any of them is in
                                             (Gaiad/ancestry/emma-ancestry.ged, from synoptic/trim_to_ancestors.py
                                             in the inochi-no-michikyo repo), appended with its families. Her own
                                             record resolves as I2, and order.life's Aster (REFN Q1) and Andromeda
                                             (REFN Q3) as I1 and I3, so her line joins through to them (Emma,
                                             2026-10-15: "plus ancestry from me to Andromeda. Oh, and Aster").
                                             F1 is Aster and Andromeda as husband and wife, with their children
                                             (Emma, 2026-10-17).

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
ANCESTRY = ROOT / "Gaiad" / "ancestry" / "emma-ancestry.ged"
TAG = re.compile(r"\{\{c\|(?:[^}|]*\|)?([^}|]+)\}\}")
TITLE = re.compile(r"^#\s+(?:Chapter\s+\d+:\s*)?(.*)")
NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://order.life/gaiad/individual/")
FIRST = [("Aster", "Aster"), ("Emma Leonhart", "Emma /Leonhart/ 命玥"), ("Andromeda", "Andromeda")]
EMMA_NAMES = ["Emma 李命玥"]  # beside her primary name, Emma /Leonhart/ 命玥 (Emma, 2026-10-16)
FIRST_SEX = {"Aster": "M", "Emma Leonhart": "F", "Andromeda": "F"}  # Emma, 2026-10-16: "Aster has sex. M."
EMMA_FS = "PFR5-LDS"
ORDERLIFE_FIRST = {"Q1": "@I1@", "Q3": "@I3@"}  # order.life ids of Aster and Andromeda


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
    return [r for r in recs if r[1] in ("INDI", "FAM", "SOUR")]  # SOUR: the trees the citations point to


def aster_andromeda_family(recs, imap):
    """One family for Aster and Andromeda, as husband and wife, first among the families (so it is F1).

    Emma, 2026-10-17: they "currently are not displayed as being husband and wife in the family F1, and they should
    be. Instead, both of them are shown as single parents of Benzet." The ancestry file has each of them as a single
    parent of Benzette and the two as a childless couple; every family whose only parents are Aster and/or Andromeda
    becomes that one family, with all their children. Returns the new records and {dropped family: kept family}.
    """
    src = {v: k for k, v in imap.items() if v in ("@I1@", "@I3@")}
    if len(src) < 2:
        return recs, {}
    pair = {src["@I1@"], src["@I3@"]}
    hits = []
    for x, tag, lines in recs:
        if tag == "FAM":
            parents = {l[7:].strip() for l in lines if l.startswith(("1 HUSB ", "1 WIFE "))}
            if parents and parents <= pair:
                hits.append(x)
    if not hits:
        return recs, {}
    keep = hits[0]
    body = [f"1 HUSB {src['@I1@']}", f"1 WIFE {src['@I3@']}"]
    seen = set(body)
    by_x = {x: lines for x, tag, lines in recs if tag == "FAM"}
    for x in hits:
        skip = False
        for l in by_x[x]:
            if l.startswith("1 "):   # a level-1 line and the lines under it go together
                skip = l.startswith(("1 HUSB ", "1 WIFE ")) or (l.startswith("1 CHIL ") and l in seen)
                seen.add(l)
            if not skip:
                body.append(l)
    out, placed = [], False
    for r in recs:
        if r[1] == "FAM" and not placed:
            out.append((keep, "FAM", body))
            placed = True
        if r[1] != "FAM" or r[0] not in hits:
            out.append(r)
    return out, {x: keep for x in hits[1:]}


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
    # Every Gaiad figure has a SEX (Emma, 2026-10-16: "all of us actually have set sexes"): the three first ones as she
    # set them, the others as order.life's genealogy has the person of that name (U where it does not say or the name
    # is not one person there).
    recs = ancestry_records() if ANCESTRY.exists() else []
    feats = None
    if recs:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from gedcom_features import Features
        feats = Features()
    sex_by_label = {}
    if feats:
        seen_labels = {}
        for q, r in feats.persons.items():
            lb = (r.get("label") or "").strip()
            if lb:
                seen_labels.setdefault(lb, set()).add(feats.sex_of.get(q, "U"))
        sex_by_label = {lb: next(iter(s)) for lb, s in seen_labels.items() if len(s) == 1}

    def indi(name, ged_name, where):
        nonlocal n
        n += 1
        add(f"0 @I{n}@ INDI")
        add(f"1 NAME {' '.join(ged_name.split())}")   # a tag wrapped across a line break is one name (UID unchanged)
        if ged_name.count("/") == 2 and ged_name.split("/")[1].strip():
            add(f"2 SURN {ged_name.split('/')[1].strip()}")
        add(f"1 SEX {FIRST_SEX.get(name) or sex_by_label.get(name, 'U')}")
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
        if name == "Emma Leonhart":
            # Her own names (Emma, 2026-10-16): 閻魔日巫女平連娘武李獅心命玥 comes from her label; these two beside it.
            for other in EMMA_NAMES:
                add(f"1 NAME {other}")
                add("2 TYPE AKA")
    firsts = {f[0] for f in FIRST}
    for name, ch, st in apps:
        if name not in firsts:
            indi(name, name, (ch, st))
    n_text = n

    # Emma's ancestry, renumbered after the text block; her record becomes I2, order.life's Aster and Andromeda I1, I3.

    def first_of(lines):
        if any(l.strip() in (f"1 EXID {EMMA_FS}", f"1 _FSFTID {EMMA_FS}") for l in lines):
            return "@I2@"
        for a, b in zip(lines, lines[1:]):
            if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life":
                hit = ORDERLIFE_FIRST.get(a[7:].strip())
                if hit:
                    return hit
        return None

    imap, fmap, nf = {}, {}, 0
    for x, tag, lines in recs:
        if tag == "INDI":
            hit = first_of(lines)
            if hit and hit not in imap.values():
                imap[x] = hit
            else:
                n += 1
                imap[x] = f"@I{n}@"
    recs, merged_into = aster_andromeda_family(recs, imap)
    for x, tag, lines in recs:
        if tag == "FAM":
            nf += 1
            fmap[x] = f"@F{nf}@"
    for x, into in merged_into.items():
        fmap[x] = fmap[into]
    ptr = re.compile(r"@[^@\s]+@")
    # The synoptic tree carries links on the FAM records only; give each person their FAMC/FAMS back.
    back = {}
    for x, tag, lines in recs:
        if tag == "FAM":
            for l in lines:
                if l.startswith(("1 HUSB ", "1 WIFE ", "1 CHIL ")):
                    kind = "FAMC" if l.startswith("1 CHIL ") else "FAMS"
                    back.setdefault(l[7:].strip(), []).append(f"1 {kind} {x}")
    # The per-person features (gedcom_features.py: readings, neo-kun'yomi, Chinese, temple, Horus and Abrahamic names,
    # lineage names, other calendars, links, cladoplasts) for everyone who carries an order.life id.
    links = {}
    for x, tag, lines in recs:
        if tag == "INDI":
            have = {l.strip() for l in lines}
            lines = lines + [l for l in back.get(x, ()) if l not in have]
            if not any(l.startswith("1 SEX ") for l in lines):
                lines.append("1 SEX U")   # every person has a SEX; U where no source gives one
            if feats:
                for a, b in zip(lines, lines[1:]):
                    if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life":
                        lines = lines + feats.lines(a[7:].strip())
        fixed = [ptr.sub(lambda m: imap.get(m.group(0)) or fmap.get(m.group(0)) or m.group(0), l) for l in lines]
        if tag == "INDI":   # a link to a family merged into F1 would otherwise appear twice
            fixed = [l for i, l in enumerate(fixed) if not l.startswith(("1 FAMC ", "1 FAMS ")) or l not in fixed[:i]]
        target = imap.get(x)
        if target in ("@I1@", "@I2@", "@I3@"):
            keep, prev = [], ""
            for l in fixed:   # family links, ids and citations, and the feature lines after the record's own
                if (l.startswith(("1 FAMC", "1 FAMS", "1 EXID", "1 SOUR @"))
                        or (l.startswith(("2 TYPE http", "2 PAGE ")) and prev.startswith(("1 EXID", "1 SOUR @")))
                        or keep and not l.startswith(("1 REFN", "2 TYPE order.life", "1 SEX"))):
                    keep.append(l)
                prev = l
            links[target] = keep
            continue
        add(f"0 {imap.get(x) or fmap.get(x) or x} {tag}")
        w.extend(fixed)
    # Graft the joined records' family links, ids and citations onto I1, I2, I3, at the end of each record (so a
    # NAME keeps its SURN and other parts directly under it).
    for target, fam_lines in links.items():
        if fam_lines:
            i = w.index(f"0 {target} INDI") + 1
            while i < len(w) and not w[i].startswith("0 "):
                i += 1
            w[i:i] = fam_lines
    add("0 TRLR")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(w) + "\n", encoding="utf-8-sig", newline="\n")
    stats = {"text individuals": n_text, "ancestry individuals": n - n_text, "families": nf}
    if feats:
        stats.update({f"feature: {k}": v for k, v in sorted(feats.counts.items())})
    stats["bytes"] = out_path.stat().st_size
    return stats


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "gaiad.ged"
    for k, v in build(dest).items():
        print(f"  {k}: {v:,}")
