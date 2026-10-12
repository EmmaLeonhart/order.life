"""Build content/ancestor_days.json: ancestors' births and deaths by Gaian day.

Emma's spec (2026-10-12): all of her ancestors, plus Abul Hamza and all of his ancestors, merged
from every file that has them, never one file. Rerun when a source is refreshed:

    python scripts/build_ancestor_days.py SOURCE [SOURCE ...]

Each SOURCE is PATH::ID or PATH::ID::self. ID is any text that appears in the root person's
record (a FamilySearch id such as PFR5-LDS, or `fs:PFR5-LDS` in the Geni union); `::self` adds
the root person too. The run of 2026-10-12, from the inochi-no-michikyo checkout:

    genealogy/out/merged.ged::fs:PFR5-LDS                      (Geni union)
    <second_attempt.rmtree as GEDCOM>::PFR5-LDS                 (FamilySearch, via RootsMagic)
    <Abul Hamza hourglass .rmtree as GEDCOM>::GRWG-G82::self    (Abul Hamza and his ancestors)

(.rmtree files are converted with genealogy/new/rootsmagic-import/rmtree_to_gedcom.py first.)

Ancestors are found by walking parent links (FAMC and CHIL) up from the root, so the descendants
and side branches these files also hold are left out. A person in more than one source counts
once: matched on FamilySearch id, else on name and exact birth (or death) date. Dates are placed by
Emma's rules (2026-10-12, "going for abundance here, not for being exact"): an exact date on its
day; month and year on the 1st of the month; year only on 1 January; approximate (abt, est, cal)
on 1 June of the year; before a year on 31 December of the year before (bef 800 -> 31 Dec 799),
after a year on 31 December of that year (aft 800 -> 31 Dec 800); a range on both of its ends.
Anyone with no death event who was born in the last 110 years, or whose birth year is unknown, is
treated as living and left out. Dates are used as written
(proleptic Gregorian; Julian dates are not converted). A date's Gaian day of the year comes from
its ISO week date, as in build.py's gregorian_to_gaian: 1-364, and 365-371 for Horus 1-7.
"""

import datetime
import json
import re
import sys
from pathlib import Path

LIVING_YEARS = 110
OUT = Path(__file__).resolve().parent.parent / "content" / "ancestor_days.json"

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}
DMY = re.compile(r"^(\d{1,2}) ([A-Za-z]+)\.? (\d{3,4})$")
ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
YEAR = re.compile(r"(\d{3,4})")
GENI_XREF = re.compile(r"^@I(6\d{15,})@$")


def records(path):
    """Yield (xref, kind, lines) for each level-0 record; lines are (level, tag, value)."""
    xref = kind = None
    lines = []
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for raw in f:
            parts = raw.rstrip("\r\n").split(" ", 2)
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            if parts[0] == "0":
                if xref:
                    yield xref, kind, lines
                xref = parts[1] if parts[1].startswith("@") else None
                kind = parts[2].strip() if len(parts) > 2 else ""
                lines = []
                continue
            if kind in ("INDI", "FAM"):
                lines.append((int(parts[0]), parts[1], parts[2] if len(parts) > 2 else ""))
    if xref:
        yield xref, kind, lines


def ancestors_of(path, root_id):
    """Pass 1: links only. Return (root xrefs, ancestor xrefs)."""
    famc, parents, roots = {}, {}, set()
    for xref, kind, lines in records(path):
        if kind == "INDI":
            famc[xref] = [v.strip() for lvl, t, v in lines if lvl == 1 and t == "FAMC"]
            if any(root_id in v for _, _, v in lines):
                roots.add(xref)
        elif kind == "FAM":
            parents[xref] = [v.strip() for lvl, t, v in lines if lvl == 1 and t in ("HUSB", "WIFE")]
            for lvl, t, v in lines:
                if lvl == 1 and t == "CHIL":
                    famc.setdefault(v.strip(), [])
                    if xref not in famc[v.strip()]:
                        famc[v.strip()].append(xref)
    anc, stack = set(), list(roots)
    while stack:
        x = stack.pop()
        for fam in famc.get(x, []):
            for p in parents.get(fam, []):
                if p in famc and p not in anc:
                    anc.add(p)
                    stack.append(p)
    return roots, anc


def details(path, wanted):
    """Pass 2: name, ids and birth/death of the wanted people."""
    out = {}
    for xref, kind, lines in records(path):
        if kind != "INDI" or xref not in wanted:
            continue
        p = {"name": "", "fsid": "", "geni": "", "dead": False, "BIRT": "", "DEAT": ""}
        m = GENI_XREF.match(xref)
        if m:
            p["geni"] = m[1]
        current = None
        for level, tag, value in lines:
            if level == 1:
                current = tag
                if tag == "NAME" and not p["name"]:
                    p["name"] = " ".join(value.replace("/", " ").split())
                elif tag == "_FSFTID" and not p["fsid"]:
                    p["fsid"] = value.strip()
                elif tag == "REFN" and value.strip().startswith("fs:") and not p["fsid"]:
                    p["fsid"] = value.strip()[3:]
                elif tag == "DEAT":
                    p["dead"] = True
            elif level == 2 and tag == "DATE" and current in ("BIRT", "DEAT") and not p[current]:
                p[current] = value
        out[xref] = p
    return out


def exact_date(value):
    v = (value or "").strip()
    m = ISO.match(v)
    if m:
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
    else:
        m = DMY.match(v)
        if not m or m[2].lower() not in MONTHS:
            return None
        d, mo, y = int(m[1]), MONTHS[m[2].lower()], int(m[3])
    try:
        return datetime.date(y, mo, d)
    except ValueError:
        return None


MY = re.compile(r"^([A-Za-z]+)\.? (\d{3,4})$")
APPROX = re.compile(r"^(abt|about|est|estimated|cal|calculated|circa|ca|c|int)\.?\s+", re.I)
BEFORE = re.compile(r"^(bef|before)\.?\s+(.+)$", re.I)
AFTER = re.compile(r"^(aft|after)\.?\s+(.+)$", re.I)
RANGE = re.compile(r"^(?:from|bet|between)\.?\s+(.+?)\s+(?:to|and)\s+(.+)$", re.I)
OPEN_RANGE = re.compile(r"^(?:from|to)\.?\s+(.+)$", re.I)


def _plain_date(v):
    """Exact date as it is; month and year -> the 1st; year only -> 1 January."""
    v = v.strip().strip("<>").strip()
    d = exact_date(v)
    if d:
        return d
    try:
        m = MY.match(v)
        if m and m[1].lower() in MONTHS:
            return datetime.date(int(m[2]), MONTHS[m[1].lower()], 1)
        m = re.match(r"^(\d{3,4})(/\d{1,2})?$", v)
        if m:
            return datetime.date(int(m[1]), 1, 1)
    except ValueError:
        pass
    return None


def _period_end(v, before):
    """Before a period: the last day before it starts (bef 800 -> 31 Dec 799). After a period: the
    last day of it (aft 800 -> 31 Dec 800); after an exact date, that date."""
    v = v.strip("<>").strip()
    try:
        d = exact_date(v)
        if d:
            return d - datetime.timedelta(days=1) if before else d
        m = MY.match(v)
        if m and m[1].lower() in MONTHS:
            first = datetime.date(int(m[2]), MONTHS[m[1].lower()], 1)
            if before:
                return first - datetime.timedelta(days=1)
            nxt = datetime.date(first.year + (first.month == 12), first.month % 12 + 1, 1)
            return nxt - datetime.timedelta(days=1)
        y = YEAR.search(v)
        if y:
            return datetime.date(int(y[1]) - 1, 12, 31) if before else datetime.date(int(y[1]), 12, 31)
    except (ValueError, OverflowError):
        return None
    return None


def placed_dates(value):
    """The days an event is kept on, by Emma's rules (2026-10-12), "going for abundance here,
    not for being exact": an exact date on its day; month and year on the 1st of the month; year
    only on 1 January; an approximate date (abt, est, cal) on 1 June of its year; bef and
    aft as in _period_end; a range (from ... to, bet ... and) on both of its ends."""
    v = (value or "").strip().strip("<>").strip()
    if not v:
        return []
    m = RANGE.match(v)
    if m:
        return [d for d in (_plain_date(m[1]), _plain_date(m[2])) if d]
    m = BEFORE.match(v) or AFTER.match(v)
    if m:
        d = _period_end(m[2].strip(), before=bool(BEFORE.match(v)))
        return [d] if d else []
    if APPROX.match(v):
        rest = APPROX.sub("", v, count=1)
        y = YEAR.search(rest)
        try:
            return [datetime.date(int(y[1]), 6, 1)] if y else []
        except ValueError:
            return []
    m = OPEN_RANGE.match(v)
    if m:
        v = m[1]
    d = _plain_date(v)
    return [d] if d else []


def any_year(value):
    m = YEAR.search(value or "")
    return int(m[1]) if m else None


def gaian_doy(d):
    _, week, weekday = d.isocalendar()
    return (week - 1) * 7 + weekday


def main(sources):
    merged, by_fsid, by_name_date = [], {}, {}
    report = []
    for src in sources:
        bits = src.split("::")
        path, root_id, with_self = bits[0], bits[1], len(bits) > 2 and bits[2] == "self"
        roots, anc = ancestors_of(path, root_id)
        if with_self:
            anc |= roots
        people = details(path, anc)
        new = 0
        for p in people.values():
            b = exact_date(p["BIRT"]) or exact_date(p["DEAT"])
            key_nd = (p["name"].lower(), b.isoformat()) if b and p["name"] else None
            i = by_fsid.get(p["fsid"]) if p["fsid"] else None
            if i is None and key_nd:
                i = by_name_date.get(key_nd)
            if i is None:
                merged.append(p)
                i = len(merged) - 1
                new += 1
            else:
                q = merged[i]
                for k in ("fsid", "geni", "BIRT", "DEAT"):
                    if not q[k] and p[k]:
                        q[k] = p[k]
                q["dead"] = q["dead"] or p["dead"]
                if not exact_date(q["BIRT"]) and exact_date(p["BIRT"]):
                    q["BIRT"] = p["BIRT"]
                if not exact_date(q["DEAT"]) and exact_date(p["DEAT"]):
                    q["DEAT"] = p["DEAT"]
            q = merged[i]
            if q["fsid"]:
                by_fsid[q["fsid"]] = i
            if key_nd:
                by_name_date[key_nd] = i
        report.append(f"{Path(path).name} ({root_id}): {len(anc)} people, {new} new")
        print(report[-1])

    cutoff = datetime.date.today().year - LIVING_YEARS
    days, placed, living = {}, 0, 0
    for p in merged:
        by = any_year(p["BIRT"])
        if not p["dead"] and (by is None or by > cutoff):
            living += 1
            continue
        for tag, key in (("BIRT", "births"), ("DEAT", "deaths")):
            for d in placed_dates(p[tag]):
                e = {"name": p["name"] or "(no name)", "date": d.isoformat()}
                if p["fsid"]:
                    e["fsid"] = p["fsid"]
                elif p["geni"]:
                    e["geni"] = p["geni"]
                days.setdefault(str(gaian_doy(d)), {"births": [], "deaths": []})[key].append(e)
                placed += 1
    for v in days.values():
        for key in ("births", "deaths"):
            v[key].sort(key=lambda e: (e["date"], e["name"]))

    out = {
        "_comment": ("Ancestors' births and deaths keyed by Gaian day of the year (365-371 = "
                     "Horus 1-7): Emma's ancestors, and Abul Hamza with his. Generated by "
                     "scripts/build_ancestor_days.py; do not edit by hand."),
        "sources": report,
        "ancestors": len(merged),
        "left_out_as_living": living,
        "events_placed": placed,
        "days": dict(sorted(days.items(), key=lambda kv: int(kv[0]))),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(merged)} people after merging, {living} left out as living, "
          f"{placed} events placed on {len(days)} days -> {OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
