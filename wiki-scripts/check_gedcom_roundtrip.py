"""
Check that every person in gaiad.ged can still be matched back after a program has imported
and re-exported it (Gramps, RootsMagic, MyHeritage, webtrees ...).

Emma, 2026-10-12: entity resolution has to survive "even when programs throw a lot out".
export_gedcom7.py writes each person's order.life QID five ways (UID, EXID, REFN, NOTE, SOUR
PAGE). This reads the original and the round-tripped file, finds which of those carriers each
re-exported person still has, and reports how many of the original people match back, by
which carrier, and whether the parent links between matched people survived.

    python wiki-scripts/check_gedcom_roundtrip.py ORIGINAL.ged ROUNDTRIPPED.ged

Stdlib only. Never trusts @I..@ xrefs across the two files: programs renumber them.
"""
import re
import sys
from collections import Counter, defaultdict

QID = re.compile(r"\bQ\d+\b")
UUID = re.compile(r"[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}")


def records(path):
    """Yield (xref, tag, lines) per level-0 record; lines are (level, tag, value)."""
    cur = None
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        for raw in fh:
            raw = raw.rstrip("\r\n")
            if not raw:
                continue
            parts = raw.split(" ", 2)
            try:
                level = int(parts[0])
            except ValueError:
                continue
            if level == 0:
                if cur:
                    yield cur
                if len(parts) > 2 and parts[1].startswith("@"):
                    cur = (parts[1], parts[2].strip(), [])
                else:
                    cur = (None, parts[1] if len(parts) > 1 else "", [])
                continue
            if cur is None:
                continue
            tag = parts[1] if len(parts) > 1 else ""
            value = parts[2] if len(parts) > 2 else ""
            cur[2].append((level, tag, value))
    if cur:
        yield cur


ORDERLIFE_NOTE = re.compile(r"order\.life[^Q\n]{0,40}\b(Q\d+)\b")


def carriers(lines, notes=None):
    """Map carrier name -> set of order.life QIDs (or UUIDs for UID) found in a person record.

    Wikidata QIDs share the Q-number space with order.life QIDs, so an EXID counts only when
    its TYPE is the order.life URI, a REFN only when its TYPE (if any survives) is not
    Wikidata, and a NOTE only for the QID written after "order.life".
    """
    found = defaultdict(set)
    pending = None  # (carrier, [qids]) of a level-1 EXID/REFN waiting for its TYPE
    def flush():
        if not pending or pending[2] is False or pending[0] == "EVEN":
            return
        # An EXID whose TYPE was dropped cannot be told from the Wikidata one: reported, not used.
        found["EXID untyped" if pending[2] is None else pending[0]].update(pending[1])
    for level, tag, value in lines:
        if level == 1:
            flush()
            pending = None
        if level == 1 and tag in ("UID", "_UID"):
            for u in UUID.findall(value):
                found["UID"].add(u.replace("-", "").lower())
        elif level == 1 and tag == "EVEN":
            # Gramps 6 keeps UID and EXID as custom events: "1 EVEN <value> / 2 TYPE UID|<uri>".
            pending = ["EVEN", [value.strip()], None]
        elif level == 1 and tag == "EXID":
            pending = ["EXID", QID.findall(value), None]   # None = untyped so far
        elif level == 1 and tag == "REFN":
            pending = ["REFN", QID.findall(value), True]
        elif level == 2 and tag == "TYPE" and pending and pending[0] == "EVEN":
            if value.strip() in ("UID", "_UID"):
                pending[:] = ["UID", [u.replace("-", "").lower() for u in UUID.findall(pending[1][0])], True]
            elif "order.life" in value:
                pending[:] = ["EXID", QID.findall(pending[1][0]), True]
            else:
                pending[2] = False
        elif level == 2 and tag == "TYPE" and pending:
            if pending[0] == "EXID":
                pending[2] = "order.life" in value
            elif "wikidata" in value.lower():
                pending[2] = False
        elif tag in ("NOTE", "CONT", "CONC"):
            if level == 1 and tag == "NOTE" and value.strip().startswith("@") and notes is not None:
                value = notes.get(value.strip(), "")
            for q in ORDERLIFE_NOTE.findall(value):
                found["NOTE"].add(q)
        elif level == 2 and tag == "PAGE" and "wikidata.org" not in value:
            # /gaiad.ged also cites @WIKIDATA@ with the Wikidata page as PAGE; that QID is not ours.
            for q in QID.findall(value):
                found["SOUR PAGE"].add(q)
    flush()
    return found


def load(path):
    people = {}   # xref -> (carriers, famc list, name)
    fams = {}     # xref -> (husb, wife, [children])
    notes = {}    # shared NOTE records, which some programs move person notes into
    for xref, tag, lines in records(path):
        if tag.startswith("NOTE"):
            notes[xref] = " ".join([tag[4:].strip()] + [v for lv, t, v in lines if t in ("CONT", "CONC")])
    for xref, tag, lines in records(path):
        if tag == "INDI":
            famc = [v.strip() for lv, t, v in lines if lv == 1 and t == "FAMC"]
            name = next((v for lv, t, v in lines if lv == 1 and t == "NAME"), "")
            people[xref] = (carriers(lines, notes), famc, name)
        elif tag == "FAM":
            husb = next((v.strip() for lv, t, v in lines if lv == 1 and t == "HUSB"), None)
            wife = next((v.strip() for lv, t, v in lines if lv == 1 and t == "WIFE"), None)
            chil = [v.strip() for lv, t, v in lines if lv == 1 and t == "CHIL"]
            fams[xref] = (husb, wife, chil)
    return people, fams


def parent_pairs(people, fams, key):
    """Set of (parent identity, child identity) for every child with a resolvable identity."""
    pairs = set()
    for fx, (h, w, chil) in fams.items():
        for c in chil:
            ck = key.get(c)
            for p in (h, w):
                pk = key.get(p)
                if ck and pk:
                    pairs.add((pk, ck))
    return pairs


def main(orig_path, rt_path):
    op, of = load(orig_path)
    rp, rf = load(rt_path)

    # The original's identity per person is its REFN QID (export_gedcom7 always writes it).
    orig_qid = {}
    uid_to_qid = {}
    for x, (c, _, _) in op.items():
        q = sorted(c.get("REFN") or c.get("EXID") or [])
        if q:
            orig_qid[x] = q[0]
            for u in c.get("UID", ()):
                uid_to_qid[u] = q[0]
    all_q = set(orig_qid.values())

    by_carrier = Counter()
    matched = {}
    ambiguous = 0
    for x, (c, _, _) in rp.items():
        cand = defaultdict(set)
        for name, vals in c.items():
            if name == "EXID untyped":
                continue
            for v in vals:
                q = uid_to_qid.get(v) if name == "UID" else v
                if q in all_q:
                    cand[q].add(name)
        if len(cand) == 1:
            q, via = next(iter(cand.items()))
            matched[x] = q
            for name in via:
                by_carrier[name] += 1
        elif len(cand) > 1:
            ambiguous += 1

    got = set(matched.values())
    lost = all_q - got
    print(f"original: {len(op):,} people, {len(of):,} families")
    print(f"round-tripped: {len(rp):,} people, {len(rf):,} families")
    print(f"matched back by ID: {len(got):,} of {len(all_q):,} ({100 * len(got) / max(1, len(all_q)):.2f}%)")
    print(f"round-tripped records matching more than one person: {ambiguous:,}")
    dup = sum(1 for n in Counter(matched.values()).values() if n > 1)
    print(f"people matched by more than one round-tripped record: {dup:,}")
    print("carriers that survived (records still carrying each):")
    for name in ("UID", "EXID", "REFN", "NOTE", "SOUR PAGE"):
        print(f"  {name:10} {by_carrier[name]:>9,}")
    untyped = sum(1 for c, _, _ in rp.values() if c.get("EXID untyped"))
    print(f"  (records with an EXID whose TYPE was dropped, not used for matching: {untyped:,})")

    op_pairs = parent_pairs(op, of, orig_qid)
    rt_pairs = parent_pairs(rp, rf, matched)
    kept = op_pairs & rt_pairs
    print(f"parent links: {len(kept):,} of {len(op_pairs):,} survive between matched people; "
          f"{len(rt_pairs - op_pairs):,} new ones appeared")
    if lost:
        print("first lost QIDs:", ", ".join(sorted(lost, key=lambda q: int(q[1:]))[:20]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
