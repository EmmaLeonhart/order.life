# Vendored copy of EmmaLeonhart/rootsmagic-import rmtree_to_gedcom.py at 98fa97d (that repo is private, so CI here
# cannot fetch it). Used by .github/workflows/ancestor-days.yml. Re-copy if the original changes.
"""Convert a RootsMagic (.rmtree, RootsMagic 8-11) database to GEDCOM 5.5.1.

Usage:
    python rmtree_to_gedcom.py INPUT.rmtree OUTPUT.ged [--no-merge]

The database is opened read-only. By default, family records that share the
same father and mother are merged into one family (the RootsMagic import this
was written for created up to a dozen copies of the same couple); every child
link and every distinct marriage event is kept. A one-parent family is also
folded into its parent's two-parent family when that parent has exactly one.
--no-merge writes each
RootsMagic family record as its own GEDCOM family.

Covered: people, names (all name records), sex, person and family events with
dates, places and details, notes, families, child links, FamilySearch IDs
(_FSFTID). A place name too long for a GEDCOM line becomes a note on the
event. Not covered (empty in the source database): sources, citations,
media, tasks, groups, addresses.
"""

import argparse
import sqlite3
import sys

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# RootsMagic date qualifiers that have a GEDCOM equivalent. The certainty
# qualifiers ('?', '1'-'6') have none and are dropped.
QUALIFIERS = {"A": "ABT", "C": "ABT", "S": "ABT", "E": "EST", "L": "CAL"}

SEX = {0: "M", 1: "F"}

# GEDCOM lines are limited to 255 characters; "2 PLAC " takes 7.
MAX_PLACE = 248


# B.C. inference. The source database stores B.C. years without a sign, so
# each person's era is judged from all of their dates and their relatives'.
PRESENT_YEAR = 2026
# Cost of an A.D. parent with a B.C. child. Heavy, but not absolute, so one
# bad date on a descendant cannot pull every ancestor into B.C.
LINE_CROSS_BACK = 4
# B.C. has to be earned: a small cost per dated person breaks ties to A.D.
BC_PRIOR = 0.25
# Only someone born this close to year 0 can be born B.C. and die A.D.
CROSSING_BORN_WITHIN = 150
BIRT, CHR, DEAT, BURI = 1, 3, 2, 4


def _year(value):
    """Year of the first part of an RM date string, or 0."""
    if value and value[0] == "D" and len(value) >= 7:
        return int(value[3:7])
    return 0


def _signed(years, bc):
    return {t: (-y if bc else y) for t, y in years.items()}


def _own_cost(y):
    """Broken constraints among one person's own (signed) dates, weighted:
    a date in the future or a death before birth is strong evidence."""
    cost = 3 * sum(1 for v in y.values() if v > PRESENT_YEAR)
    b, d = _born(y), _died(y)
    if b is not None and d is not None:
        cost += 2 * (d < b) + (d - b > 120)
    if DEAT in y and BURI in y:
        cost += y[BURI] < y[DEAT]
    if BIRT in y and CHR in y:
        cost += y[CHR] < y[BIRT]
    return cost


def _born(y):
    return y.get(BIRT, y.get(CHR))


def _died(y):
    return y.get(DEAT, y.get(BURI))


def _parent_cost(par, child):
    """Broken constraints between a parent's and a child's (signed) dates."""
    cost = 0
    pb, cb = _born(par), _born(child)
    if pb is not None and cb is not None:
        cost += not 12 <= cb - pb <= 80
    pd = _died(par)
    if pd is not None and cb is not None:
        cost += cb > pd + 1
    cd = _died(child)
    if pb is not None and cb is None and cd is not None:
        cost += not 12 <= cd - pb <= 200
    return cost


def _sibling_cost(a, b):
    ab, bb = _born(a), _born(b)
    return int(ab is not None and bb is not None and abs(ab - bb) > 40)


def _spouse_cost(a, b, marriages):
    """marriages: years signed as a's era."""
    cost = 0
    ab, bb = _born(a), _born(b)
    if ab is not None and bb is not None:
        cost += abs(ab - bb) > 50
    for m in marriages:
        for y in (a, b):
            if _born(y) is not None and m < _born(y) + 10:
                cost += 1
            if _died(y) is not None and m > _died(y) + 1:
                cost += 1
    return cost


def infer_bc(years, parent_child, couples=(), marriages=None, siblings=()):
    """Return the set of people whose stored years are B.C.

    years: person -> {event type: year} (unsigned, as stored).
    parent_child: (parent, child) pairs; couples: (husband, wife) pairs;
    marriages: (husband, wife) -> marriage years; siblings: pairs.

    Each person is A.D. or B.C. Every line of descent crosses from B.C. to
    A.D. once, so a B.C. person's parents should be B.C. (a heavy penalty,
    LINE_CROSS_BACK, rather than a hard rule, so one bad date cannot drag a
    whole ancestry across).
    Each person costs the date constraints their own dates break in each
    era; each parent/child, sibling and spouse pair costs the constraints
    broken between them. The assignment with the least total cost over the
    whole tree is found exactly as a minimum s-t cut (the costs are
    submodular). No single date decides anyone.
    """
    import networkx as nx
    from networkx.algorithms.flow import boykov_kolmogorov

    marriages = marriages or {}
    sig = lambda pid, bc: _signed(years.get(pid, {}), bc)
    # Source side = B.C. Edge s->p is cut when p is A.D., p->t when B.C.,
    # i->j when i is B.C. and j is A.D.
    unary = {}

    def add_unary(pid, ad, bc):
        u = unary.setdefault(pid, [0, 0])
        u[0] += ad
        u[1] += bc

    g = nx.DiGraph()

    def add_edge(a, b, cap):
        if cap > 0:
            if g.has_edge(a, b):
                g[a][b]["capacity"] += cap
            else:
                g.add_edge(a, b, capacity=cap)

    def add_pair(i, j, energy, j_bc_i_ad_penalty=0):
        e00, e01, e10, e11 = (energy(bool(xi), bool(xj))
                              for xi, xj in ((0, 0), (0, 1), (1, 0), (1, 1)))
        e01 += j_bc_i_ad_penalty
        # E = e00 + (e10-e00) x_i + (e11-e10) x_j + w [x_i=0, x_j=1]
        for pid, k in ((i, e10 - e00), (j, e11 - e10)):
            add_unary(pid, max(-k, 0), max(k, 0))
        add_edge(j, i, max(e01 + e10 - e00 - e11, 0))

    for pid in years:
        add_unary(pid, _own_cost(sig(pid, False)),
                  _own_cost(sig(pid, True)) + BC_PRIOR)
    for par, child in parent_child:
        add_pair(par, child,
                 lambda pb, cb: _parent_cost(sig(par, pb), sig(child, cb)),
                 j_bc_i_ad_penalty=LINE_CROSS_BACK)
    for a, b in siblings:
        add_pair(a, b, lambda ab, bb: _sibling_cost(sig(a, ab), sig(b, bb)))
    for h, w in couples:
        ms = marriages.get((h, w), [])
        add_pair(h, w, lambda hb, wb: _spouse_cost(
            sig(h, hb), sig(w, wb), [-m if hb else m for m in ms]))

    for pid, (ad, bc) in unary.items():
        base = min(ad, bc)
        add_edge("s", pid, ad - base)
        add_edge(pid, "t", bc - base)
    if "s" not in g or "t" not in g:
        return set()
    _, (source_side, _) = nx.minimum_cut(g, "s", "t",
                                         flow_func=boykov_kolmogorov)
    return {pid for pid in source_side if pid != "s"}


def _one_date(sign, ymd, bc_upto=0):
    """Format one RM yyyymmdd date part; '' when the year is 0.

    With bc_upto, a year not above it is written as B.C.
    """
    year, month, day = int(ymd[0:4]), int(ymd[4:6]), int(ymd[6:8])
    if year == 0:
        return ""
    if bc_upto and year <= bc_upto:
        sign = "-"
    parts = []
    if day and month:
        parts.append(str(day))
    if month:
        parts.append(MONTHS[month - 1])
    parts.append(str(year) + (" B.C." if sign == "-" else ""))
    return " ".join(parts)


def rm_date_to_gedcom(value, bc_upto=0):
    """Translate a RootsMagic encoded date string to a GEDCOM date.

    Layout of a 'D' date: [0]='D', [1]=modifier, [2]=sign, [3:11]=yyyymmdd,
    [11]=double-date flag, [12]=qualifier, then a second date in [13:24]
    with the same layout (used by ranges).

    bc_upto: for a person judged B.C., their reference year. Years not above
    it are B.C. (a B.C. person's later events have smaller year numbers);
    larger years are A.D.
    """
    if not value or value == ".":
        return ""
    if value[0] == "T":
        text = value[1:].strip()
        return f"({text})" if text else ""
    if value[0] != "D" or len(value) < 13:
        return ""
    modifier = value[1]
    first = _one_date(value[2], value[3:11], bc_upto)
    qualifier = value[12]
    second = (_one_date(value[13], value[14:22], bc_upto)
              if len(value) >= 22 else "")
    if first.endswith("B.C.") and second.endswith("B.C."):
        first, second = second, first  # 1612 B.C. comes before 1592 B.C.
    if not first:
        return ""
    if modifier == "B":
        return f"BEF {first}"
    if modifier == "A":
        return f"AFT {first}"
    if modifier in "RSO" and second:
        if modifier == "S":
            return f"FROM {first} TO {second}"
        return f"BET {first} AND {second}"
    if qualifier in QUALIFIERS:
        return f"{QUALIFIERS[qualifier]} {first}"
    return first


def _clean(text):
    return " ".join((text or "").split())


def _note_lines(level, text):
    """NOTE with CONT for line breaks and CONC for long lines."""
    out = []
    for i, line in enumerate((text or "").replace("\r\n", "\n").split("\n")):
        tag = "NOTE" if i == 0 else "CONT"
        lvl = level if i == 0 else level + 1
        chunks = [line[j:j + 200] for j in range(0, len(line), 200)] or [""]
        out.append(f"{lvl} {tag} {chunks[0]}".rstrip())
        out.extend(f"{level + 1} CONC {c}" for c in chunks[1:])
    return out


def _event_lines(level, tag, name, date, place, details, note):
    head = f"{level} {tag}"
    if tag == "EVEN" or details:
        head += f" {_clean(details)}" if details else ""
    lines = [head]
    if tag == "EVEN":
        lines.append(f"{level + 1} TYPE {name}")
    if date:
        lines.append(f"{level + 1} DATE {date}")
    if place:
        lines.append(f"{level + 1} PLAC {place}")
    if note:
        lines += _note_lines(level + 1, note)
    return lines


def convert(conn, out, merge=True, submitter="Unknown"):
    """Write GEDCOM for the RootsMagic database `conn` to text stream `out`.

    Returns a dict of counts.
    """
    # RootsMagic defines a custom collation; any query touching an indexed
    # text column needs it registered.
    conn.create_collation(
        "RMNOCASE", lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
    q = lambda sql: conn.execute(sql).fetchall()

    places = dict(q("SELECT PlaceID, Name FROM PlaceTable"))
    fact_types = {fid: (name, tag) for fid, name, tag in
                  q("SELECT FactTypeID, Name, GedcomTag FROM FactTypeTable")}
    fsids = dict(q("SELECT rmID, fsID FROM FamilySearchTable "
                   "WHERE LinkType = 0 AND fsID <> ''"))
    # A web link on the person (OwnerType 0, same as a person event). The
    # ancestor-day builder reads a Wikidata URL back out of this line.
    urls = {}
    if conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='URLTable'"
            ).fetchone():
        for owner, url in q(
                "SELECT OwnerID, URL FROM URLTable "
                "WHERE OwnerType = 0 AND URL <> '' ORDER BY LinkID"):
            urls.setdefault(owner, url)

    # Families: map every RM FamilyID to an output family.
    fam_key = {}      # output key -> (father, mother, first note)
    fam_of = {}       # RM FamilyID -> output key
    fam_with_events = {oid for (oid,) in q(
        "SELECT DISTINCT OwnerID FROM EventTable WHERE OwnerType = 1")}
    for fid, father, mother, note in q(
            "SELECT FamilyID, FatherID, MotherID, Note FROM FamilyTable "
            "ORDER BY FamilyID"):
        if not father and not mother:
            # No parents: grouping these by (0, 0) would make every child in
            # them siblings. With no event or note they carry nothing, so drop.
            if merge and not note and fid not in fam_with_events:
                continue
            key = fid
        else:
            key = (father, mother) if merge else fid
        fam_of[fid] = key
        if key not in fam_key:
            fam_key[key] = [father, mother, []]
        if note:
            fam_key[key][2].append(note)
    if merge:
        # A one-parent family whose parent has exactly one two-parent family
        # (in the same role) is folded into that family.
        couples = {}
        pairs = [k for k in fam_key if isinstance(k, tuple)]
        for father, mother in pairs:
            if father and mother:
                couples.setdefault((0, father), []).append((father, mother))
                couples.setdefault((1, mother), []).append((father, mother))
        kids = {}
        for child, fid in q("SELECT ChildID, FamilyID FROM ChildTable"):
            if fid in fam_of:
                kids.setdefault(fam_of[fid], set()).add(child)
        redirect = {}
        for father, mother in pairs:
            if bool(father) != bool(mother):
                target = couples.get((0, father) if father else (1, mother), [])
                # Never fold a child into a family where that child is a
                # parent (the source has a mother also recorded as her
                # son's wife).
                if len(target) == 1 and not set(target[0]) & kids.get(
                        (father, mother), set()):
                    redirect[(father, mother)] = target[0]
        for fid, key in fam_of.items():
            fam_of[fid] = redirect.get(key, key)
        for key, target in redirect.items():
            fam_key[target][2].extend(fam_key.pop(key)[2])
    fam_xref = {key: f"@F{i}@" for i, key in enumerate(fam_key, 1)}

    children = {key: [] for key in fam_key}
    famc = {}
    for child, fid in q("SELECT ChildID, FamilyID FROM ChildTable "
                        "ORDER BY FamilyID, ChildOrder, RecID"):
        key = fam_of.get(fid)
        if key is None:
            continue
        if child not in children[key]:
            children[key].append(child)
        famc.setdefault(child, [])
        if key not in famc[child]:
            famc[child].append(key)
    fams = {}
    for key, (father, mother, _) in fam_key.items():
        for pid in (father, mother):
            if pid:
                fams.setdefault(pid, []).append(key)

    names = {}
    for row in q("SELECT OwnerID, Surname, Given, Prefix, Suffix, Nickname, "
                 "IsPrimary FROM NameTable ORDER BY OwnerID, IsPrimary DESC, NameID"):
        names.setdefault(row[0], []).append(row[1:])

    person_events, family_events = {}, {}
    for etype, otype, oid, date, pid, details, note in q(
            "SELECT EventType, OwnerType, OwnerID, Date, PlaceID, Details, Note "
            "FROM EventTable ORDER BY SortDate, EventID"):
        if otype == 0:
            person_events.setdefault(oid, []).append(
                (etype, date, pid, details, note))
        elif otype == 1 and oid in fam_of:
            evs = family_events.setdefault(fam_of[oid], [])
            ev = (etype, date, pid, details, note)
            if ev not in evs:  # merged families repeat the same marriage
                evs.append(ev)

    # Every dated person event, by type (first of each type), for B.C.
    years = {}
    for pid, evs in person_events.items():
        for e in evs:
            if e[0] in (BIRT, CHR, DEAT, BURI) and _year(e[1]):
                years.setdefault(pid, {}).setdefault(e[0], _year(e[1]))
    parent_child = [(par, child) for key, kids in children.items()
                    for par in fam_key[key][:2] if par for child in kids]
    couples = [(f, m) for f, m, _ in fam_key.values() if f and m]
    marriages = {}
    for key, evs in family_events.items():
        f, m, _ = fam_key[key]
        for e in evs:
            if f and m and _year(e[1]):
                marriages.setdefault((f, m), []).append(_year(e[1]))
    siblings = [(kids[i], kids[i + 1]) for kids in children.values()
                for i in range(len(kids) - 1)]
    bc = infer_bc(years, parent_child, couples, marriages, siblings)
    # A B.C. person's later events have smaller year numbers; a year above
    # their birth year is A.D. (someone born B.C. who died A.D.).
    bc_upto = {}
    for pid in bc:
        born = _born(years.get(pid, {}))
        bc_upto[pid] = born if born and born <= CROSSING_BORN_WITHIN else 9999

    def event(level, etype, date, pid, details, note, upto=0):
        name, tag = fact_types.get(etype, ("Event", ""))
        tag = tag if tag and tag.isalpha() and tag.isupper() else "EVEN"
        place = _clean(places.get(pid, ""))
        if len(place) > MAX_PLACE:
            # Too long for a GEDCOM line: it is prose, not a place name.
            note = place + ("\n" + note if note else "")
            place = ""
        return _event_lines(level, tag, name, rm_date_to_gedcom(date, upto),
                            place, details, note)

    w = lambda line: out.write(line + "\n")
    for line in ["0 HEAD", "1 SOUR rootsmagic-import",
                 "2 NAME rmtree_to_gedcom.py", "1 GEDC", "2 VERS 5.5.1",
                 "2 FORM LINEAGE-LINKED", "1 CHAR UTF-8", "1 SUBM @SUBM1@",
                 "0 @SUBM1@ SUBM", f"1 NAME {submitter}"]:
        w(line)

    n_people = 0
    for pid, sex, note in q("SELECT PersonID, Sex, Note FROM PersonTable "
                            "ORDER BY PersonID"):
        n_people += 1
        w(f"0 @I{pid}@ INDI")
        for surname, given, prefix, suffix, nick, _primary in names.get(pid, []):
            surname, given = _clean(surname), _clean(given)
            full = " ".join(p for p in (given, f"/{surname}/", _clean(suffix)) if p)
            w(f"1 NAME {full}")
            for tag, val in (("NPFX", prefix), ("GIVN", given), ("NICK", nick),
                             ("SURN", surname), ("NSFX", suffix)):
                if _clean(val):
                    w(f"2 {tag} {_clean(val)}")
        w(f"1 SEX {SEX.get(sex, 'U')}")
        for ev in person_events.get(pid, []):
            for line in event(1, *ev, upto=bc_upto.get(pid, 0)):
                w(line)
        for key in famc.get(pid, []):
            w(f"1 FAMC {fam_xref[key]}")
        for key in fams.get(pid, []):
            w(f"1 FAMS {fam_xref[key]}")
        if pid in fsids:
            w(f"1 _FSFTID {fsids[pid]}")
        if pid in urls:
            w(f"1 WWW {_clean(urls[pid])}")
        if note:
            for line in _note_lines(1, note):
                w(line)

    for key, (father, mother, notes) in fam_key.items():
        w(f"0 {fam_xref[key]} FAM")
        if father:
            w(f"1 HUSB @I{father}@")
        if mother:
            w(f"1 WIFE @I{mother}@")
        for child in children[key]:
            w(f"1 CHIL @I{child}@")
        upto = bc_upto.get(father, 0) or bc_upto.get(mother, 0)
        for ev in family_events.get(key, []):
            for line in event(1, *ev, upto=upto):
                w(line)
        for note in dict.fromkeys(notes):
            for line in _note_lines(1, note):
                w(line)
    w("0 TRLR")

    return {"people": n_people,
            "source_families": q("SELECT COUNT(*) FROM FamilyTable")[0][0],
            "families": len(fam_key),
            "child_links": sum(len(c) for c in children.values()),
            "bc_people": len(bc)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--no-merge", action="store_true",
                    help="keep duplicate family records instead of merging them")
    ap.add_argument("--submitter", default="Unknown")
    args = ap.parse_args(argv)
    conn = sqlite3.connect(f"file:{args.input}?mode=ro", uri=True)
    with open(args.output, "w", encoding="utf-8", newline="\n") as out:
        stats = convert(conn, out, merge=not args.no_merge,
                        submitter=args.submitter)
    for k, v in stats.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    sys.exit(main())
