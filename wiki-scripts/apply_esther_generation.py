"""The two Esthers: settled by the 1037 ketubba. Esther bat Sahlan holds her mother's life.

    python wiki-scripts/apply_esther_generation.py           # dry run
    python wiki-scripts/apply_esther_generation.py --write   # apply

THE SOURCE, which is what this item has been waiting on since 2026-08-01

queue.md item 12 filed this as "genuinely undecidable from the dump", and it was right to.
Both readings are naming-consistent, each woman is correctly named for her own father
under either, and a cut made under reading A on 2026-08-01 was reverted because the
patronymics do not decide the direction.

They do not. The ketubba does.

**Abu 'Amr Sahlan ben Abraham -- payṭan, alluf, head of the Iraqi congregation of Fustat
1034-1049/50 -- married Esther, the daughter of Joseph ben 'Amram, chief judge of
Sijilmasa. The marriage contract survives and is dated September 1037.** (Encyclopedia of
Jews in the Islamic World, s.v. Sahlān b. Abraham; Sahlān succeeded his father Abraham
ben Sahlān, who held the post 1016-c.1032.)

So reading B is correct: **Esther *bat Yosef* married Sahlan, and their daughter is Esther
*bat Sahlan*.** Reading A -- Esther bat Sahlan marrying Yosef -- would make her the wife of
her own maternal grandfather.

The dump corroborates it independently. `Q90982` already carries `P42` = `Q91024` Sahlan,
which is exactly the attested marriage, and both `Q91024` and `Q90982` already list
`Q88454` as their child. Everything on the mother's side is right.

WHAT IS ACTUALLY WRONG

`Q88454` "Esther bat Sahlan" has been given **her mother's life on top of her own**. She
is recorded as the wife of Yosef ben 'Amram -- her maternal grandfather -- and as the
mother of Esther bat Yosef, who is her mother. A same-name collapse across two
generations, and the papponymic naming that produced the two Esthers is what made it
possible.

`Q88380` is a parallel import of `Q90982`: same name, same father `Q88316`, and it carries
the same false mother. Deduping the two is separate work and removes no loop, so it is not
done here -- but the false claim is removed from both, or the defect just moves.

WHAT SURVIVES UNTOUCHED

Every true edge: Sahlan and Esther bat Yosef as the parents of Esther bat Sahlan, their
attested marriage, and Yosef ben 'Amram as the father of Esther bat Yosef. Esther bat
Sahlan's own husband is not recorded anywhere, and the mother of Esther bat Yosef is not
either; both are left absent rather than guessed.

Shadow-aware and idempotent; verifies from disk and re-walks the pair afterwards.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER, P_SPOUSE = "P20", "P47", "P48", "P42"

DAUGHTER = "Q88454"   # Esther bat Sahlan ben Abraham -- the younger
MOTHER = "Q90982"     # Esther bat Yosef ben 'Amram -- the elder, m. Sahlan 1037
MOTHER_DUP = "Q88380" # parallel import of the elder
GRANDFATHER = "Q88316"  # Yosef ben 'Amram, haDayyan of Sijilmasa

# (holder qid, property, value qid, why it is false)
FALSE_CLAIMS = [
    (MOTHER, P_MOTHER, DAUGHTER,
     "the elder Esther's mother cannot be her own daughter"),
    (DAUGHTER, P_CHILD, MOTHER,
     "reciprocal of the above -- the younger Esther is not her mother's mother"),
    (MOTHER_DUP, P_MOTHER, DAUGHTER,
     "same false mother on the parallel import of the elder Esther"),
    (DAUGHTER, P_CHILD, MOTHER_DUP,
     "reciprocal of the above"),
    (DAUGHTER, P_SPOUSE, GRANDFATHER,
     "the 1037 ketubba marries Yosef's DAUGHTER to Sahlan; this marries Yosef to his "
     "own granddaughter -- it is the mother's marriage, attached to the daughter"),
    (GRANDFATHER, P_SPOUSE, DAUGHTER,
     "reciprocal of the above"),
]


def load(stem):
    path = ITEMS / f"{stem}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


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


def drop_claim(data, pid, qid):
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


def siblings():
    out = collections.defaultdict(set)
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["to_qid"]].add(r["from_qid"])
            out[r["to_qid"]].add(r["to_qid"])
    return out


def family_of(qid, sib):
    out = []
    for stem in sorted(sib.get(qid, set()) | {qid}, key=lambda x: int(x[1:])):
        data = load(stem)
        if data is not None and (data.get("id") or stem) == qid:
            out.append(stem)
    return out


def main():
    write = "--write" in sys.argv
    sib = siblings()

    # Refuse to run unless the true edges the source establishes are actually present --
    # this repair only makes sense on top of them.
    required = [
        (DAUGHTER, P_FATHER, "Q91024", "Sahlan is her father"),
        (DAUGHTER, P_MOTHER, MOTHER, "the elder Esther is her mother"),
        (MOTHER, P_SPOUSE, "Q91024", "the 1037 ketubba: the elder Esther married Sahlan"),
        (MOTHER, P_FATHER, GRANDFATHER, "Yosef ben 'Amram is the elder Esther's father"),
    ]
    for qid, pid, expect, why in required:
        present = any(expect in values(load(s), pid) for s in family_of(qid, sib))
        if not present:
            sys.exit(f"ABORT: {qid} {pid} is missing {expect} ({why}); "
                     f"the dump is not in the state this repair assumes")
    print("Preconditions hold: the attested mother-side edges are all present.\n")

    edits, staged = [], {}
    for holder, pid, target, why in FALSE_CLAIMS:
        fam = family_of(holder, sib)
        if not fam:
            sys.exit(f"ABORT: no file claims {holder}")
        for stem in fam:
            data = staged.get(stem) or load(stem)
            n = drop_claim(data, pid, target)
            staged[stem] = data
            if n:
                print(f"  {stem}.json ({holder}): dropped {pid} -> {target} x{n}")
                print(f"      {why}")
    edits = list(staged.items())

    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for holder, pid, target, _ in FALSE_CLAIMS:
        for stem in family_of(holder, sib):
            if target in values(load(stem), pid):
                bad.append(f"{stem}.json still has {pid} -> {target}")
    for qid, pid, expect, why in required:
        if not any(expect in values(load(s), pid) for s in family_of(qid, sib)):
            bad.append(f"{qid} {pid} lost {expect} -- {why}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1

    # The loop was a 2-cycle, so proving it open is cheap and exact.
    daughter_parents = set()
    for s in family_of(DAUGHTER, sib):
        d = load(s)
        daughter_parents |= set(values(d, P_FATHER)) | set(values(d, P_MOTHER))
    mother_parents = set()
    for s in family_of(MOTHER, sib):
        d = load(s)
        mother_parents |= set(values(d, P_FATHER)) | set(values(d, P_MOTHER))
    print(f"\n  {DAUGHTER} parents: {sorted(daughter_parents)}")
    print(f"  {MOTHER} parents: {sorted(mother_parents)}")
    if DAUGHTER in mother_parents:
        print("Loop still closed.")
        return 1
    print("\nLoop open. The mother keeps her marriage, the daughter keeps her parents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
