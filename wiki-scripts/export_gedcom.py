"""
Export the whole Gaiad genealogy as a GEDCOM 5.5.1 file.

Reads the three committed extracts in wikibase/analysis/ -- persons.tsv, edges.tsv,
spouses.tsv -- and writes a single .ged. Stdlib only, so build.py can call it in CI.

Run standalone:  python wiki-scripts/export_gedcom.py [out.ged]
"""
import csv
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ANA = REPO / "wikibase" / "analysis"

SEX_MALE = "Q153718"
SEX_FEMALE = "Q153719"
# Q153721 ("Aster") and Q1 (Aster the person) appear in the sex column on ~39 records.
# Neither is a sex; both fall through to U.

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

GEDCOM_YEAR_MAX = 9999

EMPTY_SURNAME_RE = re.compile(r"/\s*/")
# A single backslash separates name variants in the source labels and is meaningful.
# Runs of them are import corruption: 134 records carry P5 values that are thousands of
# backslashes long, one of them 24,635 characters.
BACKSLASH_RUN_RE = re.compile(r"\\\s*(?=\\)")
# GEDCOM 5.5.1 caps a physical line at 255 characters.
NAME_MAX = 200


def esc(text):
    """GEDCOM has one escape: a literal @ is doubled. Also flatten whitespace."""
    if not text:
        return ""
    return " ".join(text.replace("@", "@@").split())


def clean_name(text):
    """Normalise one name value: collapse corrupt backslash runs and bound the length.

    Kept separate from esc() because the collapsing is specific to names -- the source
    uses " \\ " to separate name variants, so single backslashes must survive.
    """
    text = BACKSLASH_RUN_RE.sub("", esc(text)).strip(" \\").strip()
    if len(text) > NAME_MAX:
        text = text[:NAME_MAX].rsplit(" ", 1)[0].rstrip(" \\")
    return text


def parse_ged_date(raw, precision=None):
    """Wikidata-style timestamp -> a GEDCOM DATE string, or None if unrepresentable.

    `precision` is the Wikidata code: 11 day, 10 month, 9 year, 8 decade, 7 century,
    lower still for deeper time. It matters because a year-precision date is stored as
    "+0594-01-01T00:00:00Z" -- rendering the month and day would assert a 1 January the
    dump never claimed. Missing precision falls back to whatever the timestamp shows.

    Returns None when the year is outside GEDCOM's 1..9999 range: deep time (Aster's
    -13000000000) has no GEDCOM representation, so the caller preserves the raw value
    in a NOTE rather than dropping it.
    """
    if not raw:
        return None
    s = raw.strip()
    neg = s.startswith("-")
    if s[0] in "+-":
        s = s[1:]
    head = s.split("T", 1)[0]
    bits = head.split("-")
    if not bits or not bits[0].isdigit():
        return None
    year = int(bits[0])
    if year == 0 or year > GEDCOM_YEAR_MAX:
        return None
    month = int(bits[1]) if len(bits) > 1 and bits[1].isdigit() else 0
    day = int(bits[2]) if len(bits) > 2 and bits[2].isdigit() else 0

    prec = 11
    if precision not in (None, ""):
        try:
            prec = int(precision)
        except (TypeError, ValueError):
            prec = 11
    if prec < 10:
        month = day = 0
    elif prec == 10:
        day = 0

    out = []
    if 1 <= month <= 12:
        if 1 <= day <= 31:
            out.append(f"{day:02d}")
        out.append(MONTHS[month - 1])
    out.append(str(year))
    if neg:
        out.append("B.C.")
    date = " ".join(out)
    # Decade and coarser: the year itself is an approximation, so say so.
    return f"ABT {date}" if prec <= 8 else date


def name_lines(label, gedcom_name):
    """Return the NAME values for one person, primary first.

    P5's own description: the gedcom-formatted name becomes the primary name when it
    matches the label apart from the /surname/ slashes, and a secondary search name
    otherwise. Honour that rather than picking one and discarding the other.
    """
    label = clean_name(label)
    gedcom_name = clean_name(gedcom_name)
    # An empty surname arrives as a trailing "//"; drop the empty pair, keep real ones.
    gedcom_name = EMPTY_SURNAME_RE.sub("", gedcom_name).strip()
    if not gedcom_name:
        return [label] if label else []
    if not label:
        return [gedcom_name]
    if gedcom_name.replace("/", "").strip() == label:
        return [gedcom_name]
    return [label, gedcom_name]


def load():
    persons = {}
    with open(ANA / "persons.tsv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            persons[row["qid"]] = row

    parents_of = defaultdict(list)
    with open(ANA / "edges.tsv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            p, c = row["parent"], row["child"]
            if p in persons and c in persons and p != c:
                parents_of[c].append(p)

    spouse_pairs = set()
    with open(ANA / "spouses.tsv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            a, b = row["a"], row["b"]
            if a in persons and b in persons and a != b:
                spouse_pairs.add(frozenset((a, b)))

    # Optional: written by extract_date_precision.py. Absent it, dates fall back to
    # whatever the timestamp shows, which over-asserts 1 January on year-precision rows.
    precision = {}
    prec_path = ANA / "date_precision.tsv"
    if prec_path.exists():
        with open(prec_path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                precision[row["qid"]] = (row["birth_precision"], row["death_precision"])

    return persons, parents_of, spouse_pairs, precision


def couples_for_child(parents, sex_of, spouse_pairs):
    """Split one child's parent set into (husband, wife) family keys.

    Multiple parentage is deliberate here, so this never discards a parent. It pairs
    what the spouse table says is a couple, pairs a lone father across several mothers
    (and vice versa) so contradictory parentages each get their own family, and gives
    anything left over a single-parent family.
    """
    males = [p for p in parents if sex_of.get(p) == "M"]
    females = [p for p in parents if sex_of.get(p) == "F"]
    others = [p for p in parents if sex_of.get(p) not in ("M", "F")]

    pairs = []
    mm, ff = list(males), list(females)

    # 1. attested couples first
    for m in list(mm):
        for f in list(ff):
            if frozenset((m, f)) in spouse_pairs:
                pairs.append((m, f))
                mm.remove(m)
                ff.remove(f)
                break

    # 2. one parent on one side fans out across the other side
    if mm and ff:
        if len(mm) == 1:
            pairs += [(mm[0], f) for f in ff]
            mm, ff = [], []
        elif len(ff) == 1:
            pairs += [(m, ff[0]) for m in mm]
            mm, ff = [], []
        else:
            n = min(len(mm), len(ff))
            pairs += list(zip(mm[:n], ff[:n]))
            mm, ff = mm[n:], ff[n:]

    # 3. leftovers get single-parent families; unknown sex sits in the husband slot
    pairs += [(m, None) for m in mm]
    pairs += [(None, f) for f in ff]
    pairs += [(u, None) for u in others]
    return pairs


def build_gedcom(out_path):
    persons, parents_of, spouse_pairs, precision = load()

    sex_of = {}
    for qid, row in persons.items():
        raw = row.get("sex") or ""
        sex_of[qid] = "M" if raw == SEX_MALE else "F" if raw == SEX_FEMALE else "U"

    # ── families ──────────────────────────────────────────────────────────────
    fam_children = defaultdict(set)
    for child, parents in parents_of.items():
        for key in couples_for_child(parents, sex_of, spouse_pairs):
            fam_children[key].add(child)

    # childless marriages still deserve a FAM so the spouse link survives
    for pair in spouse_pairs:
        a, b = sorted(pair)
        if sex_of.get(a) == "F" and sex_of.get(b) != "F":
            a, b = b, a
        if (a, b) not in fam_children and (b, a) not in fam_children:
            fam_children[(a, b)]  # touch: creates an empty child set

    fam_ids = {}
    for i, key in enumerate(sorted(fam_children, key=lambda k: (k[0] or "", k[1] or "")), 1):
        fam_ids[key] = f"F{i}"

    fams = defaultdict(list)   # person -> families they are a spouse in
    famc = defaultdict(list)   # person -> families they are a child in
    for key, children in fam_children.items():
        fid = fam_ids[key]
        husb, wife = key
        if husb:
            fams[husb].append(fid)
        if wife:
            fams[wife].append(fid)
        for c in children:
            famc[c].append(fid)

    # ── write ─────────────────────────────────────────────────────────────────
    stamp = datetime.now(timezone.utc)
    out = []
    w = out.append

    w("0 HEAD")
    w("1 SOUR ORDERLIFE")
    w("2 NAME The Gaiad genealogy — order.life")
    w("2 CORP Lifeism (命道教)")
    w("3 WWW https://order.life/")
    w("1 DEST ANY")
    w(f"1 DATE {stamp.day:02d} {MONTHS[stamp.month - 1]} {stamp.year}")
    w(f"2 TIME {stamp.strftime('%H:%M:%S')}")
    w("1 FILE gaiad.ged")
    w("1 CHAR UTF-8")
    w("1 LANG English")
    w("1 GEDC")
    w("2 VERS 5.5.1")
    w("2 FORM LINEAGE-LINKED")
    w("1 SUBM @SUBM@")
    w("1 NOTE The synoptic ancestry of the Gaiad: Greek, Near Eastern, Egyptian,")
    w("2 CONT Trojan, Chinese, Mongol, Indian, Japanese and biblical lines integrated")
    w("2 CONT into a single descent. Records carry their wikibase QID as REFN.")
    w("2 CONT Dates outside GEDCOM's 1..9999 year range are preserved as notes.")
    w("0 @SUBM@ SUBM")
    w("1 NAME order.life")
    w("1 WWW https://order.life/gedcom/")

    n_indi = n_dates_noted = 0
    for qid in sorted(persons, key=lambda q: int(q[1:]) if q[1:].isdigit() else 0):
        row = persons[qid]
        w(f"0 @I{qid}@ INDI")
        names = name_lines(row.get("label", ""), row.get("gedcom", ""))
        if not names:
            names = [f"[{qid}]"]
        for nm in names:
            w(f"1 NAME {nm}")
        w(f"1 SEX {sex_of[qid]}")

        prec_birth, prec_death = precision.get(qid, ("", ""))
        for tag, col, prec in (("BIRT", "birth", prec_birth), ("DEAT", "death", prec_death)):
            raw = (row.get(col) or "").strip()
            if not raw:
                continue
            date = parse_ged_date(raw, prec)
            w(f"1 {tag}")
            if date:
                w(f"2 DATE {date}")
            else:
                w(f"2 NOTE Outside GEDCOM date range: {esc(raw)}")
                n_dates_noted += 1

        for fid in famc[qid]:
            w(f"1 FAMC @{fid}@")
        for fid in fams[qid]:
            w(f"1 FAMS @{fid}@")

        w(f"1 REFN {qid}")
        wd = (row.get("wikidata_qid") or "").strip()
        if wd:
            w(f"1 _WIKIDATA {esc(wd)}")
        n_indi += 1

    for key in sorted(fam_ids, key=lambda k: int(fam_ids[k][1:])):
        fid = fam_ids[key]
        husb, wife = key
        w(f"0 @{fid}@ FAM")
        if husb:
            w(f"1 HUSB @I{husb}@")
        if wife:
            w(f"1 WIFE @I{wife}@")
        for c in sorted(fam_children[key], key=lambda q: int(q[1:]) if q[1:].isdigit() else 0):
            w(f"1 CHIL @I{c}@")
        if husb and wife and frozenset((husb, wife)) in spouse_pairs:
            w("1 MARR")

    w("0 TRLR")
    w("")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(out))
    tmp.replace(out_path)

    return {
        "individuals": n_indi,
        "families": len(fam_ids),
        "deep_time_dates": n_dates_noted,
        "bytes": out_path.stat().st_size,
    }


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ANA / "gaiad.ged"
    stats = build_gedcom(dest)
    print(f"Wrote {dest}")
    for k, v in stats.items():
        print(f"  {k}: {v:,}")
