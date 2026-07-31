"""Dedupe the Porcii Catones parallel import -- queue.md item 1.

THE DECISION THIS ENCODES.

queue.md asked: are Q148133, Q73005 and Q73167 one man, or is Q73167 Cato's father,
or his son Licinianus? The dump answers it outright:

    Q73167 "Marcus Porcius  Censorius"   P47 father = Q73005 Cato the Elder
                                         P48 mother = Q73329 Licinia
    Q73005 "Cato the Elder"              P42 spouse = Q73329 Licinia

Q73167's mother is Cato's own wife. A man cannot have his son's wife for a mother, so
Q73167 is not Cato and is not Cato's father. He is **Cato's son by Licinia** -- which is
precisely Marcus Porcius Cato Licinianus, whose cognomen means "Licinia's son". The label
"Censorius" is import noise: P5 reads "Marcus Porcius /Censorius/", i.e. the source carried
the father's cognomen in the surname slot.

The queue's premise was therefore wrong in an instructive way. There is no third Cato. What
there is, is a **parallel import of the entire Porcii Catones family**, one branch under
Q7xxxx and an independent one under Q14xxxx/Q15xxxx:

    Q73005  Cato the Elder            = Q148133   wd Q180081     <- confirmed by shared id
    Q73002  Salonia                   = Q148134   wd Q435959     <- confirmed by shared id
    Q72855  Cato Salonianus           = Q144170   wd Q1181865    <- confirmed by shared id
    Q72684  Marcus Porcius Cato       = Q141517   wd Q1372970    <- confirmed by shared id
    Q72496  Cato the Younger          = Q141438   wd Q193506     <- confirmed by shared id
    Q73329  Licinia                   = Q151388   (position)
    Q73167  Cato Licinianus           = Q148135   (position)

Five of the seven are confirmed by a Wikidata id both sides carry -- the same evidence
standard qa_wikidata_ids.tsv already uses for "shared_id". The last two carry an id on one
side only (no conflict, just a gap) and are forced by the five: both Licinia records are
wife-of-Cato and mother-of-the-Licinianus-record, and both Licinianus records are
son-of-Cato-and-Licinia. Once the Elder merges, leaving them apart would hand the survivor
two duplicate wives and two duplicate sons.

This is repair-order step 2, DEDUPE. No edge is cut, no cross-tradition join is touched,
and both descents survive in full -- the union of the two branches is strictly larger than
either.

WHERE THIS STOPS, deliberately. Below Cato the Younger the two branches stop corresponding
one-to-one: the Q7xxxx branch gives him one child (Q78063 "Porcia Catonis", no Wikidata id)
and the Q14xxxx branch gives him five (Q141439, Q141440, Q141441, Q144043, Q144042). Q78063
is probably one of the three Porcia records, but the dump does not say which and neither
does a shared id. Guessing would invent a person. So the merged Cato the Younger keeps all
six children and the Porcia duplication is left standing, reported below and written back to
queue.md as its own item.

DIRECTION. Survivor is always the Q7xxxx side. Every Q7xxxx record here has shadow files
and no Q14xxxx/Q15xxxx record has any, so merging this way vacates only qids that nothing
can re-claim. Merging the other way would vacate Q73005 -- which is exactly the mistake that
produced the reverted 2-cycle: a vacated qid lets a shadow win and injects its claims.

MECHANISM (unchanged from apply_dup_merge.py, and non-destructive): union the loser's
genealogical claims into the survivor, then rewrite the loser's file -- and every shadow of
either side -- as a copy of the survivor's content, so its internal id becomes the survivor.
extract_genealogy.py reads a file whose id differs from its filename as a redirect and
canonicalises every edge citing it. Nothing is deleted; git reverts it cleanly.

    python wiki-scripts/apply_cato_cluster_merge.py           # dry run
    python wiki-scripts/apply_cato_cluster_merge.py --write   # apply
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

GEN_PROPS = ("P20", "P42", "P47", "P48", "P61")  # child, spouse, father, mother, wikidata

# (survivor, loser, why). Order is top-down; it does not matter for correctness because
# every reference is canonicalised by the redirect map, but it reads as the family does.
MERGES = [
    ("Q73005", "Q148133", "Cato the Elder -- both carry wd Q180081"),
    ("Q73002", "Q148134", "Salonia -- both carry wd Q435959"),
    ("Q73329", "Q151388", "Licinia -- wife of Cato, mother of the Licinianus record"),
    ("Q72855", "Q144170", "Cato Salonianus -- both carry wd Q1181865"),
    ("Q73167", "Q148135", "Cato Licinianus -- son of Cato by Licinia; 'Censorius' is import noise"),
    ("Q72684", "Q141517", "Marcus Porcius Cato -- both carry wd Q1372970"),
    ("Q72496", "Q141438", "Cato the Younger -- both carry wd Q193506"),
]

# Left standing on purpose; see the module docstring.
RESIDUE = [
    "Q78063 'Porcia Catonis' (no Wikidata id) vs Q141439 / Q141441 / Q144042 -- three "
    "Porcia records under the merged Cato the Younger. Which, if any, Q78063 equals is "
    "not decided by the dump.",
]


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(q, d):
    (ITEMS / f"{q}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def claim_id(c):
    """Entity id a claim points at, or None if the value is not an entity."""
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else None


def shadows():
    """qid -> [other files claiming it], from the extractor's own redirect map."""
    out = collections.defaultdict(list)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                out[r["to_qid"]].append(r["from_qid"])
    return out


def label(q):
    d = load(q)
    if not d:
        return "?"
    v = (d.get("labels") or {}).get("en")
    return (v.get("value") if isinstance(v, dict) else v) or "(no label)"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write = "--write" in sys.argv
    shad = shadows()

    # Everything that will end up meaning "the survivor" once this runs, so that
    # unioned claims can be rewritten to the survivor's own qid.
    alias = {}
    for surv, loser, _ in MERGES:
        alias[loser] = surv
        for s in shad.get(loser, ()):
            alias[s] = surv
        for s in shad.get(surv, ()):
            alias[s] = surv

    def canon(q):
        return alias.get(q, q)

    problems = []
    for surv, loser, _ in MERGES:
        for q in (surv, loser):
            if load(q) is None:
                problems.append(f"{q}: no item file")
    if problems:
        print("ABORT -- preconditions failed:")
        for p in problems:
            print("  " + p)
        return 1

    print(f"{len(MERGES)} merge(s) planned\n")
    for surv, loser, why in MERGES:
        ds, dl = load(surv), load(loser)
        print(f"  {loser} -> {surv}   {label(surv)[:40]}")
        print(f"        {why}")
        for p in GEN_PROPS:
            gained = [canon(v) for v in vals(dl, p)]
            gained = sorted({v for v in gained if v not in set(vals(ds, p)) and v != surv})
            if gained:
                print(f"        survivor gains {p}: {gained}")
        n = len(shad.get(surv, ())) + len(shad.get(loser, ()))
        print(f"        {n} shadow file(s) will be rewritten alongside")

    print("\nleft unmerged on purpose:")
    for r in RESIDUE:
        print("  - " + r)

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    for surv, loser, _ in MERGES:
        ds, dl = load(surv), load(loser)
        before = {p: len(vals(ds, p)) for p in GEN_PROPS}
        for p in GEN_PROPS:
            have = set(vals(ds, p))
            for c in (dl.get("claims") or {}).get(p, []):
                key = claim_id(c)
                if key is not None:
                    key = canon(key)
                    if key in have or key == surv:
                        continue
                    c = json.loads(json.dumps(c))  # don't mutate the loser's own claim
                    c["mainsnak"]["datavalue"]["value"]["id"] = key
                    num = key[1:]
                    if "numeric-id" in c["mainsnak"]["datavalue"]["value"] and num.isdigit():
                        c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(num)
                else:
                    if key in have:
                        continue
                    key = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                    if key in have:
                        continue
                ds.setdefault("claims", {}).setdefault(p, []).append(c)
                have.add(key)

        # Rewrite the survivor's OWN entity references through the alias map too, so a
        # claim it already held that points at a now-merged record follows the merge.
        for p in GEN_PROPS:
            kept, seen = [], set()
            for c in (ds.get("claims") or {}).get(p, []):
                key = claim_id(c)
                if key is None:
                    kept.append(c)
                    continue
                key = canon(key)
                if key == surv or key in seen:
                    continue  # no self-parenthood, no duplicate value
                seen.add(key)
                c["mainsnak"]["datavalue"]["value"]["id"] = key
                if "numeric-id" in c["mainsnak"]["datavalue"]["value"] and key[1:].isdigit():
                    c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(key[1:])
                kept.append(c)
            if p in (ds.get("claims") or {}):
                ds["claims"][p] = kept
        save(surv, ds)
        after = {p: len(vals(load(surv), p)) for p in GEN_PROPS}

        merged = load(surv)
        n = 0
        for f in [loser] + list(shad.get(loser, ())) + list(shad.get(surv, ())):
            if (ITEMS / f"{f}.json").exists():
                save(f, merged)
                n += 1
        print(f"  {loser} -> {surv}: {before} -> {after}  ({n} file(s) rewritten)")

    print("\nverifying...")
    ok = True
    for surv, loser, _ in MERGES:
        files = [surv, loser] + list(shad.get(loser, ())) + list(shad.get(surv, ()))
        for f in files:
            d = load(f)
            if d is None:
                continue
            if d.get("id") != surv:
                print(f"  FAIL {f}: internal id is {d.get('id')}, expected {surv}")
                ok = False
        d = load(surv)
        for p in ("P20", "P47", "P48", "P42"):
            if surv in vals(d, p):
                print(f"  FAIL {surv}: is its own {p}")
                ok = False
        for p in ("P20", "P47", "P48", "P42"):
            stale = [v for v in vals(d, p) if v in alias]
            if stale:
                print(f"  FAIL {surv}: {p} still cites merged-away {stale}")
                ok = False
    print("all files agree with their survivor" if ok else "PROBLEMS ABOVE")
    print("\nNow re-run extract_genealogy.py, shadow_audit.py and dump_qa_errors.py.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
