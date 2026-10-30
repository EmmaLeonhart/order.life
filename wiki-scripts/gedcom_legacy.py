"""
The Gaiad legacy numbers, held in the pipeline: gaiad.ged's numbering, its merges, and one NOTE per person, applied at
the end of build_gaiad_ged.py.

Emma, 2026-10-28: "I want all of the current IDs to be put in place as reference numbers with the string of gaiad
legacy number", "they'd be put in the notes thing", "There's supposed to be one note" (the links first, then the
quotes, then any article), and the duplicates the textual identification makes are merged "in the gedcom generation
process", "we merge to the earlier one". And: "it needs to hold within the pipeline itself. Otherwise, it's useless."

The build numbers people by position (first appearance in the Gaiad, then the ancestry walk), so every chapter edit
moved everyone after it (from I2663 on, 86,224 people moved between 2026-10-20 and 2026-10-29). So here:

  numbering   wikibase/analysis/gaiad_legacy_numbers.tsv holds each person's number for good (frozen from the live
              file of 2026-10-29 04:19 UTC). Every record is matched to its row by a key that does not move: the UID
              for the text's individuals, an id held by that one person alone (FamilySearch, Geni, Wikidata,
              order.life) for the ancestry, else a name held by that one person alone. It carries
              REFN <number> / TYPE Gaiad legacy number. Someone new gets the next free number, in file
              order, and is written into the table, so the number holds from then on (commit the table).
  order       the @I@ numbers are the order of first appearance, made again at every build with the gaps closed
              (Emma, 2026-10-29: the people are created in order of appearance; the legacy numbers are "the internal
              legacy reference numbers", in the REFN). Making each @I@ the legacy number (687c2954b) was a mistake.
  merges      wikibase/analysis/gaiad_legacy_merges.tsv only: "<n> into <m>" moves n's names (as AKA), sources, notes and
              family links onto m and repoints everything at n to m; "<n> drop" removes a record that is not a person.
  one note    all of a person's NOTEs become one, at the place of the first: the links (with the legacy number at
              their head), then the Gaiad's quotes, then the rest.

    python wiki-scripts/gedcom_legacy.py     (no arguments: prints the merge table as it will be applied)

Stdlib only.
"""
import collections
import re
import uuid
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parent.parent / "wikibase" / "analysis"
TABLE = ANALYSIS / "gaiad_legacy_numbers.tsv"
MERGES = ANALYSIS / "gaiad_legacy_merges.tsv"
SPLITS = ANALYSIS / "gaiad_legacy_splits.tsv"
EPIC = ANALYSIS.parent.parent / "Gaiad" / "epic"
NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://order.life/gaiad/individual/")   # as build_gaiad_ged.py
HEADER = "legacy_number\tpart\tfirst_name\tuid\trefn\texid"
POINTER = re.compile(r"^(\d+ (?:[A-Z_]+ )?)@I(\d+)@((?: INDI)?)$")


def load_table():
    rows = [r.split("\t") for r in TABLE.read_text(encoding="utf-8").split("\n")[1:] if r]
    by_uid, ids_of, names = {}, {}, collections.defaultdict(list)
    for num, part, name, uid, refn, exid in rows:
        if part == "text":
            by_uid[uid] = int(num)
        else:
            ids = [x for x in exid.split("|") if x] + [x for x in refn.split("|") if x.startswith("Q")]
            ids_of[int(num)] = ids
            if not ids:
                names[name].append(int(num))
    count = collections.Counter(i for ids in ids_of.values() for i in ids)
    by_id = {i: num for num, ids in ids_of.items() for i in ids if count[i] == 1}
    # an id the frozen file gave two records (a duplicate import) goes to its rows in number order, one per record
    shared = collections.defaultdict(list)
    for num, ids in sorted(ids_of.items()):
        for i in ids:
            if count[i] > 1:
                shared[i].append(num)
    by_name = {name: nums[0] for name, nums in names.items() if len(nums) == 1}
    for name, nums in names.items():   # a name with no id that several records bear: the same, in number order
        if len(nums) > 1:
            shared["name:" + name] = sorted(nums)
    top = max(int(r[0]) for r in rows)
    return by_uid, by_id, by_name, top, shared


def load_splits():
    """gaiad_legacy_splits.tsv: one record that is two people, split at every build (the unmerge of order.life's cycle
    policy). Each row moves, from record <legacy_number> to a new record <new_number> named <new_name>: the NAMEs listed,
    the order.life REFNs listed, the child link to the family of the parent listed, the spouse families with the spouses
    listed (all by legacy number, which hold across builds) and the Wikidata links listed out of its note."""
    if not SPLITS.exists():
        return []
    rows = [r.split("\t") for r in SPLITS.read_text(encoding="utf-8").split("\n")[1:] if r.strip()]
    lst = lambda s: [x for x in s.split("|") if x]
    return [dict(n=int(r[0]), m=int(r[1]), name=r[2], names=lst(r[3]), refn=lst(r[4]),
                 child_of={int(x) for x in lst(r[5])}, spouses={int(x) for x in lst(r[6])}, links=lst(r[7]))
            for r in rows]


def split_records(indis, others, pos):
    """Applies load_splits() to the records (keyed by legacy number) and families (pointers already legacy numbers)."""
    done = 0
    fams = {first.split(" ")[1]: body for first, body in others if first.endswith(" FAM")}
    for s in load_splits():
        n, m = s["n"], s["m"]
        if n not in indis or m in indis:
            continue
        old, new = [], [[f"1 NAME {s['name']}"]]
        primary_seen = False
        for b in indis[n]:
            head = b[0]
            if head.startswith("1 NAME "):
                value = head[7:]
                if value in s["names"]:
                    if value != s["name"]:
                        new.append(b)
                    continue
                if not primary_seen:
                    # the primary name's translations follow the new name where they are its (they were the merged
                    # record's other half); the Gaiad builder took them from the order.life label of the moved item
                    primary_seen = True
                    keep = [b[0]] + [l for l in b[1:] if not l.startswith(("2 TRAN", "3 LANG"))]
                    moved = [l for l in b[1:] if l.startswith(("2 TRAN", "3 LANG"))]
                    if moved:
                        new[0] += moved
                    old.append(keep)
                    continue
                old.append(b)
            elif head.startswith("1 REFN ") and head[7:].strip() in s["refn"]:
                new.append(b)
            elif head.startswith("1 SEX "):
                old.append(b)
                new.append(b)
            elif head.startswith(("1 FAMC ", "1 FAMS ")):
                f = head.split()[2]
                members = {int(POINTER.match(l).group(2)) for l in fams.get(f, []) if POINTER.match(l)}
                if (head.startswith("1 FAMC ") and members & s["child_of"]) or \
                        (head.startswith("1 FAMS ") and members & s["spouses"]):
                    new.append([f"1 {head.split()[1]} {f}"])
                    fams[f][:] = [l.replace(f"@I{n}@", f"@I{m}@") for l in fams[f]]
                else:
                    old.append(b)
            elif head.startswith("1 NOTE ") and s["links"]:
                text = []
                for l in b:
                    for q in s["links"]:
                        l = l.replace(f"Wikidata https://www.wikidata.org/wiki/{q}; ", "") \
                             .replace(f"; Wikidata https://www.wikidata.org/wiki/{q}", "")
                    text.append(l)
                old.append(text)
            else:
                old.append(b)
        if s["links"]:
            new.append(["1 NOTE Links: " + "; ".join(f"Wikidata https://www.wikidata.org/wiki/{q}" for q in s["links"])])
        new.append([f"1 REFN {m}", "2 TYPE Gaiad legacy number"])
        indis[n], indis[m] = old, new
        pos[m] = pos.get(n, 0) + 0.5   # beside the record it came out of
        done += 1
    return done


def load_merges():
    """[(n, "into", m) or (n, "drop", None)], from the table only. A tag ID that is not its name's number is a person of
    its own, never a merge (Emma, 2026-10-29: "The ID indicates who they are"; the merges "get merged after")."""
    out = []
    if MERGES.exists():
        for r in MERGES.read_text(encoding="utf-8").split("\n")[1:]:
            if r.strip():
                n, action, target = r.split("\t")[:3]
                out.append((int(n), action, int(target) if action == "into" else None))
    return out


def ids_of(body):
    ids = [a[7:].strip() for a in body if a.startswith("1 EXID ")]
    ids += [a[7:].strip() for a, b in zip(body, body[1:] + [""]) if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"]
    return ids


def legacy_number(body, by_uid, by_id, by_name, shared=None, used=()):
    for l in body:
        if l.startswith("1 UID ") and l[6:].strip() in by_uid:
            return by_uid[l[6:].strip()]
    ids = ids_of(body)
    for i in ids:
        if i in by_id:
            return by_id[i]
    for i in ids:
        free = [n for n in (shared or {}).get(i, ()) if n not in used]
        if free:
            return free[0]
    if not ids:
        name = next((l[7:] for l in body if l.startswith("1 NAME ")), "")
        free = [n for n in (shared or {}).get("name:" + name, ()) if n not in used]
        return by_name.get(name) or (free[0] if free else None)
    return None


def blocks_of(body):
    blocks = []
    for b in body:
        if b.startswith("1 ") or not blocks:
            blocks.append([b])
        else:
            blocks[-1].append(b)
    return blocks


def one_note(blocks, legacy):
    """One NOTE, in Emma's order (2026-10-29): links, bio, quotes, legacy number(s). legacy: the record's own number
    first, then the numbers merged into it."""
    notes = [b for b in blocks if b[0].startswith("1 NOTE ")]
    links = [b for b in notes if b[0].startswith("1 NOTE Links: ")]
    gaiad = [b for b in notes if b[0].startswith("1 NOTE First named in the Gaiad")]
    rest = [b for b in notes if b not in links and b not in gaiad]
    parts, trans = [], []
    for b in links + rest + gaiad:
        parts.append([b[0][7:]] + [l[7:] for l in b[1:] if l.startswith("2 CONT")])
        tr = [l for l in b[1:] if not l.startswith("2 CONT")]
        for k in range(0, len(tr) - 1):   # one TRAN per language
            if tr[k].startswith("2 TRAN ") and tr[k + 1].startswith("3 LANG ") and tr[k + 1] not in trans:
                trans += tr[k:k + 2]
    word = "number" if len(legacy) == 1 else "numbers"
    parts.append([f"Gaiad legacy {word}: {', '.join(str(x) for x in legacy)}"])
    lines = []
    for k, text in enumerate(parts):
        lines += ([""] if k else []) + text
    note = [f"1 NOTE {lines[0]}"] + [f"2 CONT {l}".rstrip() for l in lines[1:]] + trans
    at = next((k for k, b in enumerate(blocks) if b[0].startswith("1 NOTE ")), len(blocks))
    kept = [b for b in blocks if not b[0].startswith("1 NOTE ")]
    return kept[:at] + [note] + kept[at:]


def apply(lines, register=True):
    """lines: the whole file. Returns (lines, stats)."""
    by_uid, by_id, by_name, top, shared = load_table()
    head, recs, tail = [], [], []   # recs: [xref, [lines]] for every level-0 record after the header
    for l in lines:
        if l.startswith("0 "):
            if l == "0 TRLR":
                tail.append(l)
                continue
            if l == "0 HEAD":
                head.append(l)
                continue
            recs.append([l, []])
        elif recs:
            recs[-1][1].append(l)
        else:
            head.append(l)

    # numbering: every INDI to its legacy number; the new ones to the next free numbers, in file order
    renum, new_rows, used = {}, [], set()
    pos = {}   # legacy number -> place in the build's own order (first appearance, then the ancestry walk)
    for first, body in recs:
        m = re.match(r"0 @I(\d+)@ INDI$", first)
        if m:
            n = legacy_number(body, by_uid, by_id, by_name, shared, used)
            if n is not None and n not in used:
                renum[int(m.group(1))] = n
                used.add(n)
    for first, body in recs:
        m = re.match(r"0 @I(\d+)@ INDI$", first)
        if m and int(m.group(1)) not in renum:
            top += 1
            renum[int(m.group(1))] = top
            uid = next((l[6:].strip() for l in body if l.startswith("1 UID ")), "")
            name = next((l[7:] for l in body if l.startswith("1 NAME ")), "")
            refn = [x for x in ids_of(body) if x.startswith("Q")]
            exid = [x for x in ids_of(body) if not x.startswith("Q")]
            new_rows.append(f"{top}\t{'text' if uid else 'ancestry'}\t{name}\t{uid}\t{'|'.join(refn)}\t{'|'.join(exid)}")

    def point(l):
        m = POINTER.match(l)
        return f"{m.group(1)}@I{renum.get(int(m.group(2)), int(m.group(2)))}@{m.group(3)}" if m else l

    indis = {}
    others = []
    for first, body in recs:
        first, body = point(first), [point(l) for l in body]
        m = re.match(r"0 @I(\d+)@ INDI$", first)
        if m:
            n = int(m.group(1))
            pos[n] = len(pos)
            # the build's own number stays as a REFN (language_gedcom.py keys its matched names on it) beside this one
            blocks = blocks_of(body)
            at = max((k for k, b in enumerate(blocks) if b[0].startswith("1 REFN ")), default=len(blocks) - 1) + 1
            blocks.insert(at, [f"1 REFN {n}", "2 TYPE Gaiad legacy number"])
            indis[n] = blocks
        else:
            others.append([first, body])

    n_split = split_records(indis, others, pos)

    # merges and drops
    target = {}
    for n, action, m in load_merges():
        target[n] = m

    def final(n):
        seen = set()
        while n in target and target[n] is not None and n not in seen:
            seen.add(n)
            n = target[n]
        return n

    n_merged = n_dropped = 0
    absorbed = collections.defaultdict(list)   # the legacy numbers merged into each survivor
    for n, action, m in load_merges():
        if n not in indis:
            continue
        src = indis.pop(n)
        if action == "drop":
            n_dropped += 1
            continue
        into = final(m)
        if into not in indis:
            indis[n] = src
            continue
        n_merged += 1
        absorbed[into] += [n] + absorbed.pop(n, [])
        dst = indis[into]
        for b in src:
            tag = b[0].split(" ")[1] if " " in b[0] else ""
            if tag == "NAME":
                # the merged record's names go with the others, as AKA; its Gothic form stays out (the survivor has its
                # own), and so do its other-script names, which belong to the merged name
                if any(l.startswith("3 PHRASE ") for l in b[1:]):
                    continue
                at = max(k for k, d in enumerate(dst) if d[0].startswith("1 NAME ")) + 1
                dst.insert(at, [b[0], "2 TYPE AKA"] + [l for l in b[1:] if not l.startswith("2 TYPE")])
            elif tag == "NOTE" and b[0].startswith("1 NOTE First named in the Gaiad"):
                continue   # the survivor's own first naming stands; the stanzas stay as its citations
            elif tag == "SEX":
                # the survivor inherits a known sex where it has none or only U
                have = next((d for d in dst if d[0].startswith("1 SEX ")), None)
                if b[0].strip() in ("1 SEX M", "1 SEX F") and (have is None or have[0].strip() == "1 SEX U"):
                    if have is not None:
                        dst.remove(have)
                    at = max(k for k, d in enumerate(dst) if d[0].startswith("1 NAME ")) + 1
                    dst.insert(at, b)
            elif tag in ("SOUR", "NOTE", "FAMC", "FAMS", "OBJE"):
                if b not in dst:
                    dst.append(b)
    gone = {n for n, a, m in load_merges() if n not in indis}
    redirect = {n: final(n) for n in gone if target.get(n) is not None}
    dropped = gone - set(redirect)

    def repoint(rec_lines):
        out, skip = [], None
        for l in rec_lines:
            if skip is not None:
                if int(l.split(" ", 1)[0]) > skip:
                    continue
                skip = None
            m = POINTER.match(l)
            if m and int(m.group(2)) in dropped:
                skip = int(l.split(" ", 1)[0])
                continue
            if m and int(m.group(2)) in redirect:
                l = f"{m.group(1)}@I{redirect[int(m.group(2))]}@{m.group(3)}"
            if l in out and POINTER.match(l) and l.startswith("1 "):
                skip = 1   # the same link twice after a merge: keep the first
                continue
            out.append(l)
        return out

    body_out = []
    for first, body in others:
        body_out += [first] + repoint(body)
    n_joined = 0
    indi_out = []
    for n in sorted(indis, key=lambda x: pos.get(x, len(pos) + x)):
        blocks = blocks_of(repoint([l for b in indis[n] for l in b]))
        n_joined += sum(b[0].startswith("1 NOTE ") for b in blocks) > 1
        blocks = one_note(blocks, [n] + sorted(absorbed.get(n, [])))
        indi_out += [f"0 @I{n}@ INDI"] + [l for b in blocks for l in b]

    if register and new_rows:
        with open(TABLE, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(new_rows) + "\n")
    # the header and sources first, then the people in order of first appearance, then families and the rest
    head_recs, rest_recs, cur = [], [], None
    for l in body_out:
        if l.startswith("0 "):
            cur = head_recs if re.match(r"0 @(S\d+|SUBM)@", l) else rest_recs
        cur.append(l)
    out, n_fam = one_family_per_couple(head + head_recs + indi_out + rest_recs + tail)
    out, n_self = no_child_of_own_family(out)
    out = by_first_appearance(out)
    return out, {"Gaiad legacy numbers": len(indis), "new legacy numbers": len(new_rows), "split": n_split, "merged": n_merged,
                 "dropped": n_dropped, "records whose notes were joined into one": n_joined,
                 "families joined after the merges": n_fam,
                 "child links dropped where the child is a parent of the same family": n_self}


def by_first_appearance(lines):
    """Every @I@ to its place in the file, 1, 2, 3 ... with no gaps: the people are already in order of first
    appearance, so this is that order, made again at every build."""
    order = {}
    for l in lines:
        m = re.match(r"0 @I(\d+)@ INDI$", l)
        if m:
            order[int(m.group(1))] = len(order) + 1

    def point(l):
        m = POINTER.match(l)
        return f"{m.group(1)}@I{order.get(int(m.group(2)), int(m.group(2)))}@{m.group(3)}" if m else l
    return [point(l) for l in lines]


def one_family_per_couple(lines):
    """After a merge two families can have the same two parents (Alpha and Omega's, Aster and Andromeda's): the later
    one's children move to the earlier, and every pointer to it goes to the earlier. A family left with no parents and
    no children, or a person listed twice in one family, is cleaned up the same way."""
    recs, cur = [], None
    for l in lines:
        if l.startswith("0 "):
            cur = [l]
            recs.append(cur)
        else:
            cur.append(l)
    first_of, redirect = {}, {}
    fams = {r[0].split(" ")[1]: r for r in recs if r[0].endswith(" FAM")}
    for x, r in fams.items():
        parents = tuple(sorted(l[7:] for l in r if l.startswith(("1 HUSB ", "1 WIFE "))))
        if len(parents) == 2 and parents[0] != parents[1]:
            if parents in first_of:
                keep = fams[first_of[parents]]
                keep.extend(l for l in r if l.startswith("1 CHIL ") and l not in keep)
                redirect[x] = first_of[parents]
            else:
                first_of[parents] = x
    out = []
    for r in recs:
        x = r[0].split(" ")[1] if r[0].startswith("0 @") else None
        if x in redirect:
            continue
        seen, body = set(), [r[0]]
        skip = False
        for l in r[1:]:
            if l.startswith("1 "):
                m = re.match(r"^1 (FAMC|FAMS) (@F\d+@)$", l)
                if m and m.group(2) in redirect:
                    l = f"1 {m.group(1)} {redirect[m.group(2)]}"
                skip = l.startswith(("1 FAMC ", "1 FAMS ", "1 HUSB ", "1 WIFE ", "1 CHIL ")) and l in seen
                seen.add(l)
            if not skip:
                body.append(l)
        out.extend(body)
    return out, len(redirect)


if __name__ == "__main__":
    for n, action, m in load_merges():
        print(n, action, m if m is not None else "")


def no_child_of_own_family(lines):
    """A person who is HUSB or WIFE of a family is never also its CHIL: the CHIL line and the person's FAMC to that
    family are dropped. MyHeritage refuses to export such a file ("families or individuals that are not stored
    properly"); the known cause and fix, from the RootsMagic import of 2026-09-29 (genealogy/new/rootsmagic-import,
    check_gedcom_links.py: "child and spouse in same family")."""
    fam_of, parents, cur = {}, {}, None
    for l in lines:
        if l.startswith("0 "):
            cur = l.split(" ")[1] if l.endswith(" FAM") else None
            if cur:
                parents[cur] = set()
        elif cur and re.match(r"^1 (HUSB|WIFE) @I\d+@$", l):
            parents[cur].add(l.split(" ")[2])
    bad = set()
    cur = None
    for l in lines:
        if l.startswith("0 "):
            cur = l.split(" ")[1] if l.endswith(" FAM") else None
        elif cur and l.startswith("1 CHIL ") and l.split(" ")[2] in parents[cur]:
            bad.add((l.split(" ")[2], cur))
    out, cur = [], None
    for l in lines:
        if l.startswith("0 "):
            cur = l.split(" ")[1]
        elif l.startswith("1 CHIL ") and (l.split(" ")[2], cur) in bad:
            continue
        elif l.startswith("1 FAMC ") and (cur, l.split(" ")[2]) in bad:
            continue
        out.append(l)
    return out, len(bad)
