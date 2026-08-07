"""Sunitha's father is Mrityu, not Yama. Opens the Puranic ring in both copies.

    python wiki-scripts/apply_sunita_mrityu.py           # dry run
    python wiki-scripts/apply_sunita_mrityu.py --write   # apply

THE RING, and why Daksha was the wrong place to cut it

    Daksha -> Aditi -> Surya -> Yama -> Sunita -> Vena -> Prithu
           -> Vijitashva -> Havirdhana -> Prachinbarhi -> Prachetas -> Daksha

The 2026-08-07 split of Daksha broke this ring by taking Aditi and her 59 sisters off the
son of the Prachetas and giving them to a first-birth Daksha. That is backwards.
Wikipedia's Daksha article is explicit that it is the *reincarnated* Daksha -- "a son of
Prachetas and Marisha" -- who married Asikni and fathered the sixty daughters: the 13
married to Kashyapa (Aditi, Diti, Danu, Kadru), the 27 nakshatras married to Chandra, and
the 10 married to Dharmadeva. The first Daksha, Brahma's son, married Prasuti and fathered
Sati. The dump's 63 children are unmistakably the second set, so they belong exactly where
the dump already had them, and the split has been reverted.

Which means the ring never needed Daksha touched at all. cycle_policy.md predicted this:
if a loop can only be opened by cutting something that belongs, the defect is elsewhere.

THE DEFECT

`Q153444` "SUNITA Anga" -- Sunitha, wife of Anga, mother of Vena -- is recorded with
`Q2035` "Yama Dharma King of Death" as her father. Wikipedia's Prithu article states it
plainly: **"Vena's mother was Sunitha, the daughter of Mrityu."**

Mrityu and Yama are two different figures, endlessly conflated because both are death.
Yama Dharmaraja is the son of Surya and judge of the dead; Mrityu is Death personified,
a figure of the Adharma line, and Wikidata carries him separately as Q12735987 ("Demon or
god from Vedic mythology"). This is the same shape as the Lepidus record: two distinct
figures collapsed into one because the names point at the same idea.

The structure agrees. Prithu's line descends from Svayambhuva Manu through Dhruva; the
solar line descends from Vaivasvata. They are separate descents, and `Yama -> Sunita` is
the ONLY edge joining them. It is a conflation, not a join -- so cutting it severs no
cross-tradition line, and everything else in the ring stays exactly as the Puranas have it.

THE REPAIR

Create Mrityu -- a canonical Puranic figure, not an invention -- and move Sunitha's
parentage onto him, in both imported copies. Mrityu is left without parents: his own
descent runs through Adharma, Himsa, Nikriti and Bhaya, none of which exist in this dump,
and inventing that chain is not needed to open the ring.

Shadow-aware and idempotent; verifies from disk, and re-walks the ring afterwards to prove
it is open rather than asserting it.
"""

import csv
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_CHILD, P_FATHER, P_MOTHER, P_SEX, P_WIKIDATA = "P20", "P47", "P48", "P55", "P61"
MALE = "Q153718"

REPAIRS = [
    {
        "copy": "Q153xxx/Q19xx block",
        "sunita": "Q153444",   # SUNITA Anga
        "yama": "Q2035",       # Yama Dharma King of Death
        "shyamala": "Q50072",  # Shyamala, Yama's wife -- the other half of the conflation
        "mrityu": "Q200020",
        # the ring, for the post-write walk
        "ring": ["Q153390", "Q153381", "Q1991", "Q2035", "Q153444", "Q153438",
                 "Q2001", "Q1989", "Q1978", "Q1968", "Q1955"],
    },
    {
        "copy": "Q160xxx block",
        "sunita": "Q160640",   # SUNITA Anga
        "yama": "Q160673",     # YAMA Dharma
        "shyamala": "Q160674", # SHYAMALA
        "mrityu": "Q200021",
        "ring": ["Q160489", "Q160460", "Q160580", "Q160673", "Q160640", "Q160615",
                 "Q160596", "Q160576", "Q160560", "Q160539", "Q160512"],
    },
]

MRITYU_LABEL = "Mrityu"
MRITYU_ALIASES = ["Mrtyu", "Death", "Mrityu, father of Sunitha"]
MRITYU_DESC = (
    "Death personified; father of Sunitha, wife of Anga and mother of Vena. Created "
    "2026-08-07 to separate him from Yama, who had been carrying Sunitha's parentage. "
    "His own descent (Adharma, Himsa, Nikriti, Bhaya) is not in this dump."
)
MRITYU_WIKIDATA = "Q12735987"


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


def entity_claim(pid, qid):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": {"entity-type": "item", "id": qid,
                                                 "numeric-id": int(qid[1:])},
                                       "type": "wikibase-entityid"}},
            "type": "statement", "rank": "normal"}


def string_claim(pid, text):
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": {"value": text, "type": "string"}},
            "type": "statement", "rank": "normal"}


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


def add_claim(data, pid, qid):
    if qid in values(data, pid):
        return 0
    data.setdefault("claims", {}).setdefault(pid, []).append(entity_claim(pid, qid))
    return 1


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


def parents_of(qid, sib):
    """Union of P47/P48 across every file claiming the qid -- the graph's own view."""
    out = set()
    for stem in family_of(qid, sib):
        data = load(stem)
        out |= set(values(data, P_FATHER)) | set(values(data, P_MOTHER))
    return out


def walk_ring(ring, sib):
    """Follow parents up from ring[0] and report whether it returns to itself."""
    start = ring[0]
    seen, frontier, depth = {start}, {start}, 0
    while frontier and depth < 60:
        nxt = set()
        for node in frontier:
            for p in parents_of(node, sib):
                if p == start:
                    return f"CLOSED -- {start} is still its own ancestor (depth {depth+1})"
                if p not in seen:
                    seen.add(p)
                    nxt.add(p)
        frontier = nxt
        depth += 1
    return f"OPEN -- {start} reaches {len(seen)-1} ancestors, none of them itself"


def main():
    write = "--write" in sys.argv
    sib = siblings()
    edits, log = [], []

    for spec in REPAIRS:
        sunita, yama, mrityu = spec["sunita"], spec["yama"], spec["mrityu"]
        log.append(f"\n=== {spec['copy']}: {sunita} father {yama} -> {mrityu} ===")

        fam_s = family_of(sunita, sib)
        if not fam_s:
            sys.exit(f"ABORT: no file claims {sunita}")
        if not any(yama in values(load(s), P_FATHER) for s in fam_s):
            log.append(f"  {sunita}: father {yama} not present -- already repaired")
            continue

        # Mrityu, created once per copy.
        if load(mrityu) is None:
            new = {"type": "item", "id": mrityu,
                   "labels": {"en": {"language": "en", "value": MRITYU_LABEL}},
                   "aliases": {"en": [{"language": "en", "value": a}
                                      for a in MRITYU_ALIASES]},
                   "descriptions": {"en": {"language": "en", "value": MRITYU_DESC}},
                   "claims": {}}
            add_claim(new, P_SEX, MALE)
            new["claims"][P_WIKIDATA] = [string_claim(P_WIKIDATA, MRITYU_WIKIDATA)]
            add_claim(new, P_CHILD, sunita)
            edits.append((mrityu, new))
            log.append(f"  {mrityu}: CREATE '{MRITYU_LABEL}' (wd {MRITYU_WIKIDATA}), "
                       f"child {sunita}")

        # Sunitha's father moves, and her mother goes with him. Shyamala is *Yama's*
        # wife, so she was Sunitha's mother only by way of the same conflation; the
        # Puranas name Mrityu as the father and no mother at all. She has no parents of
        # her own, so nothing upward is lost, and she keeps her place beside Yama.
        shyamala = spec["shyamala"]
        log.append(f"  {sunita}: {len(fam_s)} file(s) claim it -> {fam_s}")
        for stem in fam_s:
            data = load(stem)
            removed = drop_claim(data, P_FATHER, yama)
            added = add_claim(data, P_FATHER, mrityu)
            dropped_m = drop_claim(data, P_MOTHER, shyamala)
            log.append(f"    {stem}.json: father {yama} removed x{removed}, "
                       f"{mrityu} added x{added}; mother {shyamala} removed x{dropped_m}")
            edits.append((stem, data))

        for stem in family_of(shyamala, sib):
            data = load(stem)
            removed = drop_claim(data, P_CHILD, sunita)
            log.append(f"  {shyamala} ({stem}.json): child {sunita} removed x{removed}; "
                       f"children left: {len(values(data, P_CHILD))}")
            edits.append((stem, data))

        # Yama loses the child, on his side of the edge too.
        fam_y = family_of(yama, sib)
        log.append(f"  {yama}: {len(fam_y)} file(s) claim it -> {fam_y}")
        for stem in fam_y:
            data = load(stem)
            removed = drop_claim(data, P_CHILD, sunita)
            log.append(f"    {stem}.json: child {sunita} removed x{removed}; "
                       f"children left: {len(values(data, P_CHILD))}")
            edits.append((stem, data))

    print("\n".join(log))
    dupes = [s for s, n in collections.Counter(s for s, _ in edits).items() if n > 1]
    if dupes:
        sys.exit(f"ABORT: {dupes} staged twice")

    print(f"\n{len(edits)} file(s) to write.")
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for stem, data in edits:
        save(stem, data)
    print(f"Wrote {len(edits)} file(s).")

    bad = []
    for spec in REPAIRS:
        for stem in family_of(spec["sunita"], sib):
            fathers = values(load(stem), P_FATHER)
            if spec["yama"] in fathers:
                bad.append(f"{stem}.json still has father {spec['yama']}")
            if spec["mrityu"] not in fathers:
                bad.append(f"{stem}.json missing father {spec['mrityu']}")
        for stem in family_of(spec["yama"], sib):
            if spec["sunita"] in values(load(stem), P_CHILD):
                bad.append(f"{stem}.json still lists child {spec['sunita']}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1

    print("\nRing walk (follows parents up from the Daksha of each copy):")
    closed = False
    for spec in REPAIRS:
        result = walk_ring(spec["ring"], sib)
        print(f"  {spec['copy']}: {result}")
        closed |= result.startswith("CLOSED")
    if closed:
        print("\nA ring is still closed -- the repair did not do what it claims.")
        return 1
    print("\nBoth rings open. Daksha keeps his parentage and all sixty daughters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
