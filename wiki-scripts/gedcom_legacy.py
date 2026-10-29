"""
The Gaiad legacy numbers and one NOTE per person, applied to gaiad.ged at the end of build_gaiad_ged.py.

Emma, 2026-10-28: "I want all of the current IDs to be put in place as reference numbers with the string of gaiad
legacy number", "they'd be put in the notes thing", and "There's supposed to be one note" (the links first, then the
quotes, then any article). The build's own I-numbers move with every chapter edit (from I2663 on, 86,224 people moved
between 2026-10-20 and 2026-10-29), so the legacy numbers are the ones frozen from the live file she was looking at, in
wikibase/analysis/gaiad_legacy_numbers.tsv, matched back to each record by a key that does not move: the UID for the
text's individuals, an id held by that one person alone (FamilySearch, Geni, Wikidata, order.life) for the ancestry,
else a name held by that one person alone. A record that matches nothing (someone new since the freeze) gets none.

Stdlib only.
"""
import collections
from pathlib import Path

TABLE = Path(__file__).resolve().parent.parent / "wikibase" / "analysis" / "gaiad_legacy_numbers.tsv"


def load_table():
    rows = [r.split("\t") for r in TABLE.read_text(encoding="utf-8").split("\n")[1:] if r]
    by_uid, ids_of, names = {}, {}, collections.defaultdict(list)
    for num, part, name, uid, refn, exid in rows:
        if part == "text":
            by_uid[uid] = num
        else:
            ids = [x for x in exid.split("|") if x] + [x for x in refn.split("|") if x.startswith("Q")]
            ids_of[num] = ids
            if not ids:
                names[name].append(num)
    count = collections.Counter(i for ids in ids_of.values() for i in ids)
    by_id = {i: num for num, ids in ids_of.items() for i in ids if count[i] == 1}
    by_name = {name: nums[0] for name, nums in names.items() if len(nums) == 1}
    return by_uid, by_id, by_name


def legacy_number(body, by_uid, by_id, by_name):
    for l in body:
        if l.startswith("1 UID ") and l[6:].strip() in by_uid:
            return by_uid[l[6:].strip()]
    ids = [a[7:].strip() for a, b in zip(body, body[1:] + [""]) if a.startswith("1 EXID ")]
    ids += [a[7:].strip() for a, b in zip(body, body[1:] + [""]) if a.startswith("1 REFN ") and b.strip() == "2 TYPE order.life"]
    for i in ids:
        if i in by_id:
            return by_id[i]
    if not ids:
        name = next((l[7:] for l in body if l.startswith("1 NAME ")), "")
        return by_name.get(name)
    return None


def one_note(blocks, legacy):
    """blocks: the level-1 blocks of one record. All its NOTEs become one, at the place of the first: the links
    (with the legacy number at their head), then the Gaiad's quotes (the first-named note), then the rest."""
    notes = [b for b in blocks if b[0].startswith("1 NOTE ")]
    if not notes and legacy is None:
        return blocks
    links = [b for b in notes if b[0].startswith("1 NOTE Links: ")]
    gaiad = [b for b in notes if b[0].startswith("1 NOTE First named in the Gaiad")]
    rest = [b for b in notes if b not in links and b not in gaiad]
    head = f"Gaiad legacy number {legacy}" if legacy is not None else None
    parts, trans = [], []
    for b in links + gaiad + rest:
        text = [b[0][7:]] + [l[7:] if len(l) > 7 else "" for l in b[1:] if l.startswith("2 CONT")]
        trans += [l for l in b[1:] if not l.startswith("2 CONT")]
        parts.append(text)
    if head:
        if links:
            parts[0][0] = parts[0][0].replace("Links: ", f"Links: {head}; ", 1)
        else:
            parts.insert(0, [f"Links: {head}"])
    lines = []
    for k, text in enumerate(parts):
        if k:
            lines.append("")
        lines += text
    note = [f"1 NOTE {lines[0]}"] + [f"2 CONT {l}".rstrip() for l in lines[1:]] + trans
    at = next((k for k, b in enumerate(blocks) if b[0].startswith("1 NOTE ")), len(blocks))
    kept = [b for b in blocks if not b[0].startswith("1 NOTE ")]
    return kept[:at] + [note] + kept[at:]


def apply(lines):
    """lines: the whole file. Returns (lines, records given a legacy number, records whose notes were joined)."""
    by_uid, by_id, by_name = load_table()
    out, i, n_legacy, n_joined = [], 0, 0, 0
    while i < len(lines):
        l = lines[i]
        if not (l.startswith("0 @I") and l.endswith(" INDI")):
            out.append(l)
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("0 "):
            j += 1
        body = lines[i + 1:j]
        blocks = []
        for b in body:
            if b.startswith("1 ") or not blocks:
                blocks.append([b])
            else:
                blocks[-1].append(b)
        legacy = legacy_number(body, by_uid, by_id, by_name)
        if legacy is not None:
            n_legacy += 1
            at = max((k for k, b in enumerate(blocks) if b[0].startswith("1 REFN ")), default=len(blocks) - 1) + 1
            blocks.insert(at, [f"1 REFN {legacy}", "2 TYPE Gaiad legacy number"])
        n_joined += sum(b[0].startswith("1 NOTE ") for b in blocks) > 1
        blocks = one_note(blocks, legacy)
        out.append(l)
        out += [x for b in blocks for x in b]
        i = j
    return out, n_legacy, n_joined
