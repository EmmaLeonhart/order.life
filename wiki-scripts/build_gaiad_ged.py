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
  feature lines (2026-10-17)                 text individuals: a source citation for every stanza the name is in,
                                             the first-named note in en/zh/ja/ko, and the order.life person's
                                             features where the entity resolution gives the name one id; ancestry:
                                             features for every order.life id, more ancestors joined on an exact
                                             Wikidata or Geni id, name-only readings and names from the record's own
                                             NAME, other-calendar notes for every exact date, and a Links note
                                             naming its Wikidata, FamilySearch and Geni ids.

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
# The primary name in other languages and scripts, as TRANs under the primary NAME (planning/name-schema.md, "Primary
# names"). Emma, 2026-10-17: "change Emma Leonhart's name to 이명월 in Korean. This is the primary name and the old one
# still stays as an alias". 이명월 is the Korean reading of 李命玥, which stays as her AKA.
PRIMARY_TRAN = {"Emma Leonhart": [("이명월", "ko")]}
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


MARKUP = re.compile(r"\{\{[a-z]\|(?:[^}|]*\|)?([^}|]+)\}\}")


def citations():
    """name -> [(chapter, stanza, line)], every stanza each tag name occurs in, the line given without markup."""
    out = {}
    for n in range(1, 365):
        f = EPIC / f"chapter_{n:03d}.md"
        if not f.exists():
            continue
        raw = f.read_text(encoding="utf-8").replace("\r", "")
        m = TITLE.match(raw)
        body = raw[m.end():].lstrip("\n") if m else raw
        for si, st in enumerate((s for s in re.split(r"\n\s*\n", body) if s.strip()), 1):
            rows = st.split("\n")
            for t in TAG.finditer(st):
                name = t.group(1).strip()
                got = out.setdefault(name, [])
                if name and not (got and got[-1][:2] == (n, si)):
                    seg = " ".join(rows[st[:t.start()].count("\n"):st[:t.end()].count("\n") + 1])
                    got.append((n, si, " ".join(MARKUP.sub(r"\1", seg).split())))
    return out


def in_puranic_block(qid):
    """order.life's Q160xxx block, which is not to be used (Emma, 2026-08-18; order.life CLAUDE.md)."""
    return qid[1:].isdigit() and int(qid[1:]) // 1000 == 160


def resolved_names():
    """Tag name -> order.life qid, where Gaiad/genealogy/_resolution.tsv resolves every occurrence of it to one qid."""
    import csv
    path = ROOT / "Gaiad" / "genealogy" / "_resolution.tsv"
    by = {}
    if path.exists():
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["qid"]:
                    by.setdefault(" ".join(r["name"].split()), set()).add((r["qid"], r["method"]))
    out = {}
    for name, hits in by.items():
        qids = {q for q, _ in hits}
        if len(qids) == 1 and not in_puranic_block(next(iter(qids))):
            out[name] = (next(iter(qids)), sorted({m for _, m in hits}))
    return out


GED_MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def exact_date(d):
    """(astronomical year, month, day) for an exact GEDCOM or ISO date ("20 OCT 1963", "1996-02-26"); else None."""
    d = d.strip()
    m = re.fullmatch(r"(\d{1,2}) ([A-Z]{3}) (\d{1,4})( BCE| B\.?C\.?)?", d)
    if m and m.group(2) in GED_MONTHS:
        y = int(m.group(3))
        return (1 - y if m.group(4) else y), GED_MONTHS.index(m.group(2)) + 1, int(m.group(1))
    m = re.fullmatch(r"(-?)(\d{3,4})-(\d\d)-(\d\d)", d)
    if m:
        y = int(m.group(2))
        return (1 - y if m.group(1) else y), int(m.group(3)), int(m.group(4))
    return None


def calendar_notes(lines):
    """Birth and death "in other calendars" notes for a record's exact BIRT and DEAT dates."""
    from calendars import calendar_note
    out = []
    for a, b in zip(lines, lines[1:]):
        for tag, what in (("1 BIRT", "Birth"), ("1 DEAT", "Death")):
            if a.startswith(tag) and b.startswith("2 DATE ") and not any(o.startswith(f"1 NOTE {what} ") for o in out):
                ymd = exact_date(b[7:])
                if ymd and ymd[0] != 0 and 1 <= ymd[1] <= 12 and 1 <= ymd[2] <= 31:
                    try:
                        out.append(f"1 NOTE {what} in other calendars: {calendar_note(*ymd)}")
                    except (ValueError, IndexError):
                        pass
    return out


EXID_LINKS = {"http://www.wikidata.org/entity/": ("Wikidata", "https://www.wikidata.org/wiki/"),
              "https://www.familysearch.org/tree/person/details/": ("FamilySearch",
                                                                    "https://www.familysearch.org/tree/person/details/"),
              "https://www.geni.com/profile/index/": ("Geni", "https://www.geni.com/profile/index/")}


def exids(lines):
    """[(type, value)] for a record's EXIDs."""
    return [(b[7:].strip(), a[7:].strip()) for a, b in zip(lines, lines[1:])
            if a.startswith("1 EXID ") and b.startswith("2 TYPE ")]


def with_links(lines):
    """The record's lines with one "Links:" note that also names its Wikidata, FamilySearch and Geni ids."""
    new = [f"{EXID_LINKS[t][0]} {EXID_LINKS[t][1]}{v}" for t, v in exids(lines) if t in EXID_LINKS]
    at = next((i for i, l in enumerate(lines) if l.startswith("1 NOTE Links: ")), None)
    have = lines[at][len("1 NOTE Links: "):].split("; ") if at is not None else []
    add = [l for l in new if l.split(" ", 1)[1] not in {h.split(" ", 1)[-1] for h in have} and l not in have]
    if not add:
        return lines
    note = "1 NOTE Links: " + "; ".join(have + list(dict.fromkeys(add)))
    return lines[:at] + [note] + lines[at + 1:] if at is not None else lines + [note]


def fam_children_in_order(lines):
    """A FAM record's lines with its CHIL lines (and anything under them) sorted by I-number, in the CHIL slots."""
    blocks, cur = [], None
    for l in lines:
        if l.startswith("1 "):
            cur = [l]
            blocks.append(cur)
        elif cur is not None:
            cur.append(l)
        else:
            blocks.append([l])
    num = lambda b: int(re.search(r"@I(\d+)@", b[0]).group(1)) if re.search(r"@I(\d+)@", b[0]) else 0
    kids = iter(sorted((b for b in blocks if b[0].startswith("1 CHIL ")), key=num))
    return [l for b in blocks for l in (next(kids) if b[0].startswith("1 CHIL ") else b)]


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


def birth_year(lines):
    """The year of a record's first BIRT DATE, BC negative; None if it has none."""
    for a, b in zip(lines, lines[1:]):
        if a.startswith("1 BIRT") and b.startswith("2 DATE "):
            d = b[7:]
            m = re.match(r"(\d{3,4})-\d\d", d.strip())
            nums = [m.group(1)] if m else re.findall(r"\d{3,4}", d) or re.findall(r"\d+", d)
            if nums:
                y = int(nums[-1] if not m else nums[0])
                return -y if re.search(r"B\.?C", d) else y
            return None
    return None


def walk_numbering(recs, imap, n):
    """Number the ancestry people and the families by the FamilySearch-style walk (planning/gaiad-ged-numbering.md).

    Emma, 2026-10-14: "family search style algorithm altogether"; her 2026-10-15 answers: "the FamilySearch walk
    replaces the spouse pass" and "each person's line in turn". For each person in individual order, the ones the
    walk numbers included: their spouse families, then their parents' family, then each generation above it, father's
    side before mother's. In each family the father, the mother, then the children oldest first get the next I-number
    if they have none; each family the next F-number. People the walk never reaches follow, in the file's order.
    imap holds the joined records (I1, I2, I3) and is extended; n is the last number used (the Gaiad's text block).
    """
    fams = {x: lines for x, tag, lines in recs if tag == "FAM"}
    years = {x: birth_year(lines) for x, tag, lines in recs if tag == "INDI"}
    husb, wife, chil, famc, fams_of = {}, {}, {}, {}, {}
    for f, lines in fams.items():
        kids = []
        for l in lines:
            p = l[7:].strip()
            if l.startswith("1 HUSB "):
                husb.setdefault(f, p)
                fams_of.setdefault(p, []).append(f)
            elif l.startswith("1 WIFE "):
                wife.setdefault(f, p)
                fams_of.setdefault(p, []).append(f)
            elif l.startswith("1 CHIL "):
                kids.append(p)
                famc.setdefault(p, []).append(f)
        dated = iter(sorted((k for k in kids if years.get(k) is not None), key=lambda k: years[k]))
        chil[f] = [next(dated) if years.get(k) is not None else k for k in kids]   # undated ones keep their place
    by_num = {int(v[2:-1]): k for k, v in imap.items()}
    fmap, climbed = {}, set()

    def number_person(p):
        nonlocal n
        if p not in imap:
            n += 1
            imap[p] = f"@I{n}@"
            by_num[n] = p

    def number_family(f):
        if f not in fmap:
            fmap[f] = f"@F{len(fmap) + 1}@"
            for p in [husb.get(f), wife.get(f)] + chil[f]:
                if p:
                    number_person(p)

    def walk(p):
        for f in fams_of.get(p, ()):
            number_family(f)
        frontier = list(famc.get(p, ()))
        while frontier:   # one generation at a time, father's side first
            nxt = []
            for f in frontier:
                number_family(f)
                if f in climbed:
                    continue
                climbed.add(f)
                for parent in (husb.get(f), wife.get(f)):
                    nxt.extend(famc.get(parent, ()) if parent else ())
            frontier = nxt

    i = 0
    order = [x for x, tag, _ in recs if tag == "INDI"]
    rest = iter(order)
    while True:
        i += 1
        if i > n:
            p = next((x for x in rest if x not in imap), None)   # the next person the walk has not reached
            if p is None:
                break
            number_person(p)
        p = by_num.get(i)
        if p:
            walk(p)
    for f in fams:   # families with no member reached (none expected: every family has a member)
        if f not in fmap:
            fmap[f] = f"@F{len(fmap) + 1}@"
    return imap, fmap, n


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
    cited = citations()
    resolved = resolved_names() if feats else {}
    n_resolved_text = [0]

    def indi(name, ged_name, where):
        nonlocal n
        n += 1
        add(f"0 @I{n}@ INDI")
        add(f"1 NAME {' '.join(ged_name.split())}")   # a tag wrapped across a line break is one name (UID unchanged)
        if ged_name.count("/") == 2 and ged_name.split("/")[1].strip():
            add(f"2 SURN {ged_name.split('/')[1].strip()}")
        for text, lg in PRIMARY_TRAN.get(name, ()):
            add(f"2 TRAN {text}")
            add(f"3 LANG {lg}")
        add(f"1 SEX {FIRST_SEX.get(name) or sex_by_label.get(name, 'U')}")
        add(f"1 REFN {n}")
        add("2 TYPE Gaiad individual number")
        add(f"1 UID {uuid.uuid5(NS, name)}")
        if where:
            ch, st = where
            cites = cited.get(name) or [(ch, st, "")]
            k = len(cites)
            many = f"; named in {k} stanzas" if k > 1 else ""
            add(f"1 NOTE First named in the Gaiad, chapter {ch} (https://order.life/gaiad/{ch:03d}/#s{st}){many}.")
            for lg, text in (("zh", f"在《盖亚德》中：首次出现于第{ch}章（Gaiad {ch}.{st}）；共有{k}节提及。"),
                             ("ja", f"『ガイアド』では：第{ch}章（Gaiad {ch}.{st}）に初出、{k}連で言及。"),
                             ("ko", f"《가이아드》에서: 제{ch}장(Gaiad {ch}.{st})에 처음 등장, {k}개 연에서 언급.")):
                add(f"2 TRAN {text}")
                add(f"3 LANG {lg}")
            for c_ch, c_st, line in cites:   # a citation for every stanza the name is in (Emma, 2026-10-14)
                add("1 SOUR @S1@")
                add(f"2 PAGE Gaiad {c_ch}.{c_st}")
                if line:
                    add("2 DATA")
                    add(f"3 TEXT {'@' + line if line.startswith('@') else line}")
                add(f"2 NOTE https://order.life/gaiad/{c_ch:03d}/#s{c_st}")
        # The person the project's entity resolution gives this name (every occurrence to one order.life id; never a
        # fuzzy match) lends the record its feature lines: names in other scripts, calendars, links, cladoplasts.
        hit = resolved.get(" ".join(name.split())) if feats and name not in FIRST_SEX else None
        if hit:
            q, methods = hit
            more = feats.lines(q)
            if more:
                add(f"1 NOTE Resolved to order.life {q} by the Gaiad's entity resolution ({', '.join(methods)}).")
                w.extend(more)
                n_resolved_text[0] += 1

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

    imap = {}
    for x, tag, lines in recs:
        if tag == "INDI":
            hit = first_of(lines)
            if hit and hit not in imap.values():
                imap[x] = hit
    recs, merged_into = aster_andromeda_family(recs, imap)
    imap, fmap, n = walk_numbering(recs, imap, n)
    nf = len(fmap)
    for x, into in merged_into.items():
        fmap[x] = fmap[into]
    # Records are written in number order: the numbers are the order (planning/gaiad-ged-numbering.md).
    num = lambda r: int((imap.get(r[0]) or fmap.get(r[0]) or "@X0@")[2:-1])
    recs = (sorted((r for r in recs if r[1] == "INDI"), key=num) + sorted((r for r in recs if r[1] == "FAM"), key=num)
            + [r for r in recs if r[1] not in ("INDI", "FAM")])
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
    # More of her ancestors joined to order.life, on an exact Wikidata or Geni id only: where exactly one order.life
    # person has the id, no other record already carries that person, and exactly one record would take them.
    joins = {}
    if feats:
        def olid(lines):
            return next((a[7:].strip() for a, b in zip(lines, lines[1:])
                         if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"), None)
        carried = {olid(lines) for _, tag, lines in recs if tag == "INDI"} - {None}
        by_wd, by_geni = {}, {}
        for q, r in feats.persons.items():
            for col, into in (("wikidata_qid", by_wd), ("geni_id", by_geni)):
                v = (r.get(col) or "").strip()
                if v:
                    into.setdefault(v, set()).add(q)
        wanted = {}
        for x, tag, lines in recs:
            if tag != "INDI" or olid(lines):
                continue
            ids = dict((t, v) for t, v in exids(lines))
            for t, index in (("http://www.wikidata.org/entity/", by_wd), ("https://www.geni.com/profile/index/", by_geni)):
                qs = index.get(ids.get(t, ""), set())
                if len(qs) == 1:
                    q = next(iter(qs))
                    if q not in carried and not in_puranic_block(q):
                        wanted.setdefault(q, []).append(x)
                    break
        joins = {xs[0]: q for q, xs in wanted.items() if len(xs) == 1}
    n_cal = n_fs = 0
    links = {}
    for x, tag, lines in recs:
        if tag == "INDI":
            have = {l.strip() for l in lines}
            lines = lines + [l for l in back.get(x, ()) if l not in have]
            if not any(l.startswith("1 SEX ") for l in lines):
                lines.append("1 SEX U")   # every person has a SEX; U where no source gives one
            if imap[x] not in ("@I1@", "@I2@", "@I3@"):   # those three have theirs already
                lines = lines + [f"1 REFN {imap[x][2:-1]}", "2 TYPE Gaiad individual number"]
            if x in joins:
                lines = lines + [f"1 REFN {joins[x]}", "2 TYPE order.life"]
            if feats:
                qs = [a[7:].strip() for a, b in zip(lines, lines[1:])
                      if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"]
                if qs:   # a record can carry more than one order.life id; each gives its lines
                    for q in qs:
                        lines = lines + feats.lines(q)
                else:
                    # Name-only features (readings, neo-kun'yomi, a generated Chinese name) from the record's own
                    # NAME, as the 10-15 build gave her synoptic ancestors; nothing that needs an order.life id.
                    nm = next((l[7:].strip() for l in lines if l.startswith("1 NAME ")), "")
                    if nm:
                        pid = f"ancestry:{x}"
                        feats.persons[pid] = {"qid": pid, "label": " ".join(nm.replace("/", " ").split()), "gedcom": nm}
                        more = feats.lines(pid)
                        del feats.persons[pid]
                        # No generated reading in a language the tree already transcribes the name into.
                        tran = {"zh" if b[7:].strip().startswith(("zh", "und-Hani")) else b[7:].strip()[:2]
                                for a, b in zip(lines, lines[1:]) if a.startswith("2 TRAN ") and b.startswith("3 LANG ")}
                        blocks = []
                        for l in more:
                            if l.startswith("1 ") or not blocks:
                                blocks.append([l])
                            else:
                                blocks[-1].append(l)
                        for b in blocks:
                            ph = next((l for l in b if l.startswith("3 PHRASE ")), "")
                            if b[0].startswith("1 NAME ") and " reading (" in ph and ph[9:11] in tran:
                                feats.counts["readings"] -= 1
                            else:
                                lines = lines + b
                # Every exact date gets its other calendars, not only those order.life holds (Emma, 2026-10-12).
                cal = [c for c in calendar_notes(lines) if not any(l.startswith(c.split(":")[0]) for l in lines)]
                n_cal += len(cal)
                lines = lines + cal
                before = any("familysearch" in l for l in lines if l.startswith("1 NOTE Links: "))
                lines = with_links(lines)
                n_fs += not before and any("familysearch" in l for l in lines if l.startswith("1 NOTE Links: "))
        fixed = [ptr.sub(lambda m: imap.get(m.group(0)) or fmap.get(m.group(0)) or m.group(0), l) for l in lines]
        if tag == "INDI":   # a link to a family merged into F1 would otherwise appear twice
            fixed = [l for i, l in enumerate(fixed) if not l.startswith(("1 FAMC ", "1 FAMS ")) or l not in fixed[:i]]
        if tag == "FAM":   # children in the order the walk numbered them, oldest first
            fixed = fam_children_in_order(fixed)
        target = imap.get(x)
        if target in ("@I1@", "@I2@", "@I3@"):
            keep, prev = [], ""
            for l in fixed:   # family links, ids and citations, and the feature lines after the record's own
                if (l.startswith(("1 FAMC", "1 FAMS", "1 EXID", "1 SOUR @"))
                        or (l.startswith(("2 TYPE http", "2 PAGE ")) and prev.startswith(("1 EXID", "1 SOUR @")))
                        or keep and not l.startswith(("1 REFN", "2 TYPE order.life", "1 SEX"))):
                    keep.append(l)
                prev = l
            primary = {t for name, ged in FIRST if f"@I{FIRST.index((name, ged)) + 1}@" == target
                       for t, _ in PRIMARY_TRAN.get(name, ())}
            if primary:   # a label that is already the primary name's TRAN is not repeated as another NAME
                skip, kept = False, []
                for l in keep:
                    if l.startswith("1 "):
                        skip = l.startswith("1 NAME ") and l[7:].strip() in primary
                    if not skip:
                        kept.append(l)
                keep = kept
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
    stats = {"text individuals": n_text, "ancestry individuals": n - n_text, "families": nf,
             "text individuals with resolved features": n_resolved_text[0],
             "ancestors newly joined to order.life": len(joins), "calendar notes from the tree's own dates": n_cal,
             "link notes newly naming FamilySearch": n_fs}
    if feats:
        stats.update({f"feature: {k}": v for k, v in sorted(feats.counts.items())})
    stats["bytes"] = out_path.stat().st_size
    return stats


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "gaiad.ged"
    for k, v in build(dest).items():
        print(f"  {k}: {v:,}")
