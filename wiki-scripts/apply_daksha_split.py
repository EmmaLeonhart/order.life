"""Split Daksha into two people, in both imported copies. Dissolves tangles 2 and 4.

    python wiki-scripts/apply_daksha_split.py           # dry run
    python wiki-scripts/apply_daksha_split.py --write   # apply

RULED BY EMMA 2026-08-05, asked directly: "Split Daksha into two records."

    "this mythology does not have the sort of cyclical view of history and extremely
    long-term time abyss stuff on the same characters. It definitely has time abyss
    stuff, but the time abyss stuff in the Gaiad is its own stuff."

The Gaiad's descent is linear -- one person, one birth, one set of parents. The Puranas
have Daksha born of Brahma, destroyed at Shiva's hands, and reborn as the son of the ten
Prachetas; every edge in the ring is canonical, and the ring is still a defect here,
because a cyclic cosmology arrived along with the names. The names are wanted.

WHAT THE QUEUE GOT WRONG, AND WHY THIS SCRIPT DIFFERS FROM IT

queue.md item 3 says Q153390 "carries two fathers: Q49634 (first birth) and Q1955 the
Prachetas (rebirth)", and directs the split to keep Q49634 on Daksha I.

Q49634 is not a first birth. **Q49634.json is a shadow file whose own `id` is Q1955** --
the two are byte-identical, same label, same parents, same spouse, same coat of arms --
and redirects.tsv maps Q49634 -> Q1955. Daksha's "two fathers" are one man referenced
twice, once directly and once through a redirect qid.

So there is no first-life parentage anywhere in the dump to preserve: Brahma is not wired
to this block at all. Daksha I therefore comes out with NO recorded parents, which is
honest -- he is a root here, not falsely attached to somebody.

THE SPLIT, identical in both copies

  Daksha I  -- keeps the qid, the spouse Asikni, and every child (Aditi and her
               siblings). Loses the Prachetas father and the Marisa mother, which belong
               to the second life. This is the edge that closed the ring.
  Daksha II -- a NEW qid: son of the Prachetas by Marisa, no children, no spouse.
               Created so the split loses nothing -- the Prachetas really are recorded as
               having had a son called Daksha, and that survives on its own record.

NAMING IS EMMA'S, per the Tros precedent. The labels written here are placeholders and
are flagged as such in the record description. Renaming them later is a one-line edit.

Both copies are done in one pass on purpose: the Q153xxx/Q19xx block and the Q160xxx
block are the same figures imported twice, and splitting one copy leaves the other tangle
standing. The dedupe of the two copies is a separate, still-open task -- not this one.

Shadow-aware: every file claiming a touched qid is rewritten, or the edit reverts as soon
as that file stops being the numerically-lowest claimant. Idempotent.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER, P_SPOUSE, P_SEX = "P20", "P47", "P48", "P42", "P55"
MALE = "Q153718"

# One entry per imported copy of the Puranic genealogy.
SPLITS = [
    {
        "copy": "Q153xxx/Q19xx block",
        "daksha_i": "Q153390",       # "DAKSHA (reborn as DAKSHA) Prachetas"
        "father": "Q1955",           # Prachetas (10 sons)
        "mother": "Q49638",          # Marisa-Tarkshi
        # Q49634 is a redirect qid pointing at Q1955; the claim exists and must go too.
        "extra_father_refs": ["Q49634"],
        "daksha_ii": "Q200020",
        "label": "Daksha, son of the Prachetas",
        "aliases": ["Daksha II", "Prachetasa Daksha", "Daksha Prachetasa"],
    },
    {
        "copy": "Q160xxx block",
        "daksha_i": "Q160489",       # "DAKSHA Prachetas"
        "father": "Q160512",         # PRACHETAS (10 sons)
        "mother": "Q160511",         # Marisa-Tarkshi
        "extra_father_refs": [],
        "daksha_ii": "Q200021",
        "label": "Daksha, son of the Prachetas",
        "aliases": ["Daksha II", "Prachetasa Daksha", "Daksha Prachetasa"],
    },
]

DESCRIPTION = (
    "the second Daksha: born to the ten Prachetas by Marisa, split from the ancestor "
    "Daksha on 2026-08-07 so the Gaiad's descent stays linear. PLACEHOLDER LABEL -- "
    "naming is Emma's."
)


# ── plumbing ──────────────────────────────────────────────────────────────────

def load(stem):
    path = ITEMS / f"{stem}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save(stem, data):
    (ITEMS / f"{stem}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def values(data, pid):
    out = []
    for c in (data.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def entity_claim(pid, qid):
    return {
        "mainsnak": {
            "snaktype": "value",
            "property": pid,
            "datavalue": {
                "value": {"entity-type": "item", "id": qid,
                          "numeric-id": int(qid[1:])},
                "type": "wikibase-entityid",
            },
        },
        "type": "statement",
        "rank": "normal",
    }


def drop_claim(data, pid, qid):
    """Remove every claim of pid pointing at qid. Returns how many went."""
    claims = (data.get("claims") or {}).get(pid)
    if not claims:
        return 0
    keep = []
    for c in claims:
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id") == qid:
            continue
        keep.append(c)
    removed = len(claims) - len(keep)
    if keep:
        data["claims"][pid] = keep
    else:
        del data["claims"][pid]
    return removed


def add_claim(data, pid, qid):
    """Append a claim if it is not already there. Returns 1 if written."""
    if qid in values(data, pid):
        return 0
    data.setdefault("claims", {}).setdefault(pid, []).append(entity_claim(pid, qid))
    return 1


def family_of(qid, sib):
    """Every existing file whose own id is qid -- the canonical file and its shadows."""
    out = []
    for stem in sorted(sib.get(qid, set()) | {qid}, key=lambda x: int(x[1:])):
        data = load(stem)
        if data is not None and (data.get("id") or stem) == qid:
            out.append(stem)
    return out


def siblings():
    out = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["to_qid"]].add(r["from_qid"])
            out[r["to_qid"]].add(r["to_qid"])
    return out


# ── the repair ────────────────────────────────────────────────────────────────

def main():
    write = "--write" in sys.argv
    sib = siblings()
    edits = []          # (stem, data) staged writes
    log = []

    for spec in SPLITS:
        d1, d2 = spec["daksha_i"], spec["daksha_ii"]
        father, mother = spec["father"], spec["mother"]
        drop_fathers = [father] + spec["extra_father_refs"]

        log.append(f"\n=== {spec['copy']}: {d1} -> {d1} (ancestor) + {d2} (son) ===")

        # 1. Daksha I loses the second life's parents, in every file claiming the qid.
        fam1 = family_of(d1, sib)
        if not fam1:
            sys.exit(f"ABORT: no file claims {d1}")
        log.append(f"  {d1}: {len(fam1)} file(s) claim it -> {fam1}")
        for stem in fam1:
            data = load(stem)
            n = sum(drop_claim(data, P_FATHER, f) for f in drop_fathers)
            n += drop_claim(data, P_MOTHER, mother)
            log.append(f"    {stem}.json: dropped {n} parent claim(s); "
                       f"children kept: {len(values(data, P_CHILD))}")
            edits.append((stem, data))

        # 2. Daksha II is created, unless it already is.
        if load(d2) is None:
            new = {
                "type": "item",
                "id": d2,
                "labels": {"en": {"language": "en", "value": spec["label"]}},
                "aliases": {"en": [{"language": "en", "value": a}
                                   for a in spec["aliases"]]},
                "descriptions": {"en": {"language": "en", "value": DESCRIPTION}},
                "claims": {},
            }
            add_claim(new, P_SEX, MALE)
            add_claim(new, P_FATHER, father)
            add_claim(new, P_MOTHER, mother)
            edits.append((d2, new))
            log.append(f"  {d2}: CREATE '{spec['label']}' "
                       f"(father {father}, mother {mother})")
        else:
            log.append(f"  {d2}: already exists, left alone")

        # 3. The parents' child-claims move from Daksha I to Daksha II -- both sides of
        #    the edge, or the half-declared edge still reads as real.
        for parent in (father, mother):
            fam = family_of(parent, sib)
            log.append(f"  {parent}: {len(fam)} file(s) claim it -> {fam}")
            for stem in fam:
                data = load(stem)
                removed = drop_claim(data, P_CHILD, d1)
                added = add_claim(data, P_CHILD, d2)
                log.append(f"    {stem}.json: child {d1} removed x{removed}, "
                           f"child {d2} added x{added}")
                edits.append((stem, data))

    print("\n".join(log))

    # Merge staged writes -- a stem can be touched twice (e.g. a parent that is also a
    # shadow); last write wins and each edit was computed from the file on disk, so
    # re-load and re-apply would be needed if that ever overlapped. Assert it does not.
    seen = collections.Counter(stem for stem, _ in edits)
    dupes = [s for s, n in seen.items() if n > 1]
    if dupes:
        sys.exit(f"ABORT: {dupes} staged twice; edits would clobber each other")

    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    # Verify from disk rather than trusting the writes.
    bad = []
    for spec in SPLITS:
        d1, d2 = spec["daksha_i"], spec["daksha_ii"]
        for stem in family_of(d1, sib):
            data = load(stem)
            for f in [spec["father"]] + spec["extra_father_refs"]:
                if f in values(data, P_FATHER):
                    bad.append(f"{stem}.json still has father {f}")
            if spec["mother"] in values(data, P_MOTHER):
                bad.append(f"{stem}.json still has mother {spec['mother']}")
        d2data = load(d2)
        if not d2data or spec["father"] not in values(d2data, P_FATHER):
            bad.append(f"{d2} missing father {spec['father']}")
        for parent in (spec["father"], spec["mother"]):
            for stem in family_of(parent, sib):
                data = load(stem)
                if d1 in values(data, P_CHILD):
                    bad.append(f"{stem}.json still lists child {d1}")
                if d2 not in values(data, P_CHILD):
                    bad.append(f"{stem}.json missing child {d2}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print("Verified: both rings opened, both second Dakshas attached on both sides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
