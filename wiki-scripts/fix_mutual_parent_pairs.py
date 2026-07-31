#!/usr/bin/env python
"""Repair mutual parent pairs — A is B's parent AND B is A's parent.

THIS SCRIPT EDITS THE DUMP. Everything else in the QA chain proposes only; this one
applies, on Emma's explicit authorisation (2026-07-30) for this error class alone.
Run with --dry-run to see the plan without writing.

The shape, and why it is not what it first looks like
-----------------------------------------------------
The contradiction is usually stored inside a single item: Q78507 carries both
`P47 Father = Q78384` and `P20 Child = Q78384`. So this is not a duplicate person
to delete — Q78507 is a real man (Marcus Granius, husband of Oppidia Rufa) whose
record picked up one reversed claim about his own son. The repair is to delete the
claims encoding the false direction, and nothing else. No item is removed, no
relationship other than the reversed one is touched.

Direction evidence, and the rule for using it
---------------------------------------------
  S1 spouse_coparent  A's spouse is independently recorded as a parent of B, so the
                      family record reads A + spouse -> B. One-directional only: if
                      both sides have it, the pair is two records of one person and
                      needs a merge, not a direction fix.
  S2 dates            Both birth years recorded and >= MIN_GAP apart. Required to
                      hold under BOTH the AD and the BC reading of the years, since
                      this dump stores many BC dates unsigned (see GENEALOGY_QA.md).
  S3 patronymic       B's own name names A as its father (Welsh ap/ferch, Iberian
                      -es/-ez), or A's name names B as its father.
  S4 wikidata         qa_cycles_vs_wikidata.tsv records the pair with one direction
                      `confirmed` and the other not. This is the strongest signal
                      available, because it refutes a specific direction instead of
                      inferring one. Added 2026-07-31 (queue.md: fold the Wikidata
                      cross-check into the cycle proposals). Deliberately NOT fired when
                      Wikidata confirms BOTH directions — that is an INHERITED loop,
                      Wikidata holding the same contradiction, and it decides nothing.

A pair is repaired only when at least one signal fires and NO signal contradicts
another. Conflicts and undecidables are left alone and reported — Uematsu Takamasa
(b. 1705) and Iwakura Hiromasa (b. 1746) have a consistent-looking family record
pointing the opposite way to their recorded dates, and guessing between those two
is exactly the judgement this script must not make.

SHADOW FILES. Until 2026-07-31 this script wrote only ITEMS/<qid>.json, which is the
failure CLAUDE.md records as having reverted ten applied repairs at once: 39,527 qids are
claimed by more than one file and extract_genealogy.py keeps the numerically-lowest, so an
edit to the canonical file alone is undone the moment that file stops winning. It now
rewrites every file claiming an edited qid and verifies they agree afterwards.
"""

import argparse
import csv
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from propose_cycle_cuts import (  # noqa: E402
    FEMALE, era_ambiguous, given_name, implied_father, name_matches, year_of,
)

REPO = Path(__file__).resolve().parent.parent
ITEMS = REPO / "wikibase" / "items"
ANALYSIS = REPO / "wikibase" / "analysis"

P_FATHER, P_MOTHER, P_CHILD, P_SPOUSE = "P47", "P48", "P20", "P42"
MIN_GAP = 12


def load_tsv(name):
    with open(ANALYSIS / name, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def entity_id(claim):
    try:
        snak = claim["mainsnak"]
        if snak.get("snaktype") != "value":
            return None
        return snak["datavalue"]["value"]["id"]
    except (KeyError, TypeError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    persons = {r["qid"]: r for r in load_tsv("persons.tsv")}
    par, ch, sp = defaultdict(set), defaultdict(set), defaultdict(set)
    for r in load_tsv("edges.tsv"):
        par[r["child"]].add(r["parent"])
        ch[r["parent"]].add(r["child"])
    for r in load_tsv("spouses.tsv"):
        sp[r["a"]].add(r["b"])
        sp[r["b"]].add(r["a"])

    def lab(q):
        return (persons.get(q, {}).get("label") or "").strip() or "(unlabelled)"

    # S4 evidence. The cross-check writes its endpoints as "Q123 (Label)".
    wdv = {}
    try:
        for r in load_tsv("qa_cycles_vs_wikidata.tsv"):
            wdv[(r["parent"].split(" ")[0], r["child"].split(" ")[0])] = r["verdict"]
    except FileNotFoundError:
        print("note: qa_cycles_vs_wikidata.tsv absent — S4 wikidata signal unavailable")

    # Every file claiming a given qid, so an edit can be propagated to all of them.
    claimants = defaultdict(set)
    try:
        for r in load_tsv("redirects.tsv"):
            claimants[r["to_qid"]].add(r["from_qid"])
    except FileNotFoundError:
        print("note: redirects.tsv absent — shadow propagation unavailable, ABORTING")
        return

    # every mutual pair in the whole graph, not only those the cycle DFS happened to list
    pairs = sorted({tuple(sorted((c, p))) for c, ps in par.items()
                    for p in ps if c in par.get(p, ())})

    plan, skipped = [], []
    for a, b in pairs:
        votes = {}          # signal -> "a" (a is the parent) or "b"

        # S1 spouse co-parent
        a_first = [s for s in sp[a] if s in par[b] and s != a]
        b_first = [s for s in sp[b] if s in par[a] and s != b]
        if a_first and not b_first:
            votes["spouse_coparent"] = ("a", "%s's spouse %s is also recorded as a "
                                        "parent of %s" % (lab(a), lab(a_first[0]), lab(b)))
        elif b_first and not a_first:
            votes["spouse_coparent"] = ("b", "%s's spouse %s is also recorded as a "
                                        "parent of %s" % (lab(b), lab(b_first[0]), lab(a)))
        elif a_first and b_first:
            skipped.append((a, b, "both sides have spouse co-parent evidence — these "
                                  "are two records of one person and need a MERGE, "
                                  "which this script does not do"))
            continue

        # S2 dates, required to hold under both the AD and the BC reading
        ya, yb = year_of(persons.get(a, {}).get("birth")), year_of(persons.get(b, {}).get("birth"))
        if ya is not None and yb is not None:
            ad = "a" if ya + MIN_GAP <= yb else ("b" if yb + MIN_GAP <= ya else None)
            bc = "a" if (-ya) + MIN_GAP <= (-yb) else ("b" if (-yb) + MIN_GAP <= (-ya) else None)
            # The BC reading is only a live possibility for small positive years; 1705
            # and 1746 are Japanese AD dates whatever else the dump gets wrong, and
            # demanding sign-invariance there would silently discard a good signal.
            ambiguous = era_ambiguous(ya) or era_ambiguous(yb)
            if ad and (ad == bc or not ambiguous):
                votes["dates"] = (ad, "recorded births %d and %d put %s first by at "
                                  "least %d years%s"
                                  % (ya, yb, lab(a if ad == "a" else b), MIN_GAP,
                                     " under either the AD or the BC reading"
                                     if ad == bc else ""))

        # S4 wikidata, the strongest signal: a confirmed direction with the reverse
        # not confirmed. Both confirmed means Wikidata holds the loop too (INHERITED)
        # and settles nothing, so no vote is cast.
        fwd, rev = wdv.get((a, b)), wdv.get((b, a))
        if fwd == "confirmed" and rev != "confirmed":
            votes["wikidata"] = ("a", "Wikidata records %s as a parent of %s and does "
                                 "not support the reverse" % (lab(a), lab(b)))
        elif rev == "confirmed" and fwd != "confirmed":
            votes["wikidata"] = ("b", "Wikidata records %s as a parent of %s and does "
                                 "not support the reverse" % (lab(b), lab(a)))

        # S3 patronymic
        la, lb = lab(a), lab(b)
        fa, _ = implied_father(la, persons.get(a, {}).get("sex"))
        fb, _ = implied_father(lb, persons.get(b, {}).get("sex"))
        if fb and name_matches(fb, given_name(la)) and persons.get(a, {}).get("sex") != FEMALE:
            votes["patronymic"] = ("a", "%s's own name names %s as its father" % (lb, la))
        elif fa and name_matches(fa, given_name(lb)) and persons.get(b, {}).get("sex") != FEMALE:
            votes["patronymic"] = ("b", "%s's own name names %s as its father" % (la, lb))

        if not votes:
            skipped.append((a, b, "no direction evidence: no spouse co-parent, no "
                                  "usable dates, no patronymic"))
            continue
        sides = {v[0] for v in votes.values()}
        if len(sides) > 1:
            detail = "; ".join("%s says %s" % (k, lab(a if v[0] == "a" else b))
                               for k, v in sorted(votes.items()))
            skipped.append((a, b, "evidence conflicts — %s" % detail))
            continue

        keep_parent, keep_child = (a, b) if sides == {"a"} else (b, a)
        plan.append({
            "parent": keep_parent, "child": keep_child,
            "drop_parent": keep_child, "drop_child": keep_parent,
            "why": "; ".join(v[1] for _, v in sorted(votes.items())),
            "signals": sorted(votes),
        })

    print("mutual parent pairs found: %d" % len(pairs))
    print("repairable (evidence agrees): %d" % len(plan))
    print("left alone: %d\n" % len(skipped))

    for p in plan:
        print("KEEP  %s (%s) -> %s (%s)"
              % (p["parent"], lab(p["parent"]), p["child"], lab(p["child"])))
        print("  DROP the reverse claim: %s -> %s   [%s]"
              % (p["drop_parent"], p["drop_child"], ", ".join(p["signals"])))
        print("  %s" % p["why"])
    print()
    for a, b, why in skipped:
        print("SKIP  %s (%s) <-> %s (%s)\n      %s" % (a, lab(a), b, lab(b), why))

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return

    # Apply: remove claims encoding the false direction drop_parent -> drop_child.
    edits = defaultdict(list)
    for p in plan:
        bad_parent, bad_child = p["drop_parent"], p["drop_child"]
        edits[bad_child].append(("parent-of", bad_parent))
        edits[bad_parent].append(("child-of", bad_child))

    removed = 0
    touched = []
    shadow_writes = defaultdict(list)
    for qid, ops in sorted(edits.items()):
        path = ITEMS / ("%s.json" % qid)
        if not path.exists():
            print("MISSING ITEM %s — skipped" % qid)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        claims = data.get("claims", {})
        before = json.dumps(claims, sort_keys=True)

        for kind, other in ops:
            props = (P_FATHER, P_MOTHER) if kind == "parent-of" else (P_CHILD,)
            for prop in props:
                if prop not in claims:
                    continue
                kept = [c for c in claims[prop] if entity_id(c) != other]
                dropped = len(claims[prop]) - len(kept)
                if dropped:
                    removed += dropped
                    if kept:
                        claims[prop] = kept
                    else:
                        del claims[prop]

        if json.dumps(claims, sort_keys=True) != before:
            # indent=2 + sort_keys is exactly how the snapshot was serialised, so the
            # diff shows only the removed claims instead of a whole-file reformat.
            text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            # Write to EVERY file claiming this qid, not just the canonical one. See the
            # SHADOW FILES note at the top: editing the canonical file alone is silently
            # reverted the moment it stops being the numerically-lowest claimant.
            family = {qid} | claimants.get(qid, set())
            for f in sorted(family):
                fp = ITEMS / ("%s.json" % f)
                if fp.exists():
                    fp.write_text(text, encoding="utf-8")
                    shadow_writes[qid].append(f)
            touched.append(qid)

    print("\nremoved %d claims across %d items" % (removed, len(touched)))
    for qid in touched:
        extra = [f for f in shadow_writes[qid] if f != qid]
        print("  %s%s" % (qid, "  (+%d shadow file(s): %s)" % (len(extra), ", ".join(extra))
                          if extra else ""))

    # Verify the propagation actually took: every file claiming a touched qid must now
    # agree with it on the genealogical claims.
    print("\nverifying shadow propagation...")
    ok = True
    for qid in touched:
        ref = None
        for f in sorted({qid} | claimants.get(qid, set())):
            fp = ITEMS / ("%s.json" % f)
            if not fp.exists():
                continue
            d = json.loads(fp.read_text(encoding="utf-8"))
            if (d.get("id") or f) != qid:
                continue
            cur = {p: sorted(filter(None, (entity_id(c)
                                           for c in (d.get("claims") or {}).get(p, []))))
                   for p in (P_FATHER, P_MOTHER, P_CHILD)}
            if ref is None:
                ref = cur
            elif cur != ref:
                print("  FAIL %s: %s disagrees with the canonical record" % (qid, f))
                ok = False
    print("all files claiming a touched qid agree" if ok else "PROPAGATION INCOMPLETE")

    print("\nRe-run wiki-scripts/extract_genealogy.py, then dump_qa_errors.py.")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
