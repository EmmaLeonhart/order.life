#!/usr/bin/env python
"""Check every ancestry-cycle edge against Wikidata. READ-ONLY, fetches nothing local.

    python wiki-scripts/check_cycles_against_wikidata.py

56% of the dump's people carry a `wikidata_qid`, so for most cycle edges the parentage
can simply be looked up instead of guessed at from names. Writes
`wikibase/analysis/qa_cycles_vs_wikidata.tsv` and prints a summary.

The point of the check is to sort the cycles into three very different problems:

  INHERITED   Wikidata asserts the same contradiction. Pons Hug d'Entença (Q21001415)
              lists Jussiana (Q14083227) as BOTH his mother and his child, and the dump
              copied that faithfully. Nothing local caused it and no local cleverness
              fixes it — the repair belongs upstream.
  CONTRADICTED Wikidata records a different, consistent parentage. These are import
              errors and Wikidata decides them outright.
  UNKNOWN     One or both endpoints have no Wikidata ID, or Wikidata records no
              parent/child link either way. Local evidence is all there is.

Wikidata is the reference here, not gospel — it is also user-edited and demonstrably
holds impossible loops. An INHERITED verdict means "both copies agree", which is a
statement about provenance, not about truth.
"""

import csv
import io
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "wikibase" / "analysis"
OUT = ANALYSIS / "qa_cycles_vs_wikidata.tsv"
CACHE = ANALYSIS / ".wikidata_cache.json"

API = "https://www.wikidata.org/w/api.php"
UA = "order.life-genealogy-qa/1.0 (emma@topazcomputing.com)"
BATCH = 50

P_FATHER, P_MOTHER, P_CHILD = "P22", "P25", "P40"

csv.field_size_limit(10_000_000)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def rows(name):
    with open(ANALYSIS / name, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def claim_ids(entity, prop):
    out = []
    for c in entity.get("claims", {}).get(prop, []):
        snak = c.get("mainsnak", {})
        if snak.get("snaktype") != "value":
            continue
        v = snak.get("datavalue", {}).get("value", {})
        if isinstance(v, dict) and "id" in v:
            out.append(v["id"])
    return out


def fetch(wd_ids):
    """wikidata qid -> {father:[], mother:[], child:[], label:str}, cached on disk."""
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = sorted(set(wd_ids) - set(cache))
    if todo:
        sys.stderr.write("fetching %d Wikidata items (%d cached)...\n"
                         % (len(todo), len(cache)))
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        r = requests.get(API, params={
            "action": "wbgetentities", "ids": "|".join(chunk), "format": "json",
            "props": "claims|labels", "languages": "en",
        }, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        ents = r.json().get("entities", {})
        for qid in chunk:
            e = ents.get(qid) or {}
            if "missing" in e:
                cache[qid] = None
                continue
            cache[qid] = {
                "label": e.get("labels", {}).get("en", {}).get("value", ""),
                "father": claim_ids(e, P_FATHER),
                "mother": claim_ids(e, P_MOTHER),
                "child": claim_ids(e, P_CHILD),
            }
        sys.stderr.write("  %d/%d\n" % (min(i + BATCH, len(todo)), len(todo)))
        time.sleep(0.4)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return cache


def main():
    persons = {r["qid"]: r for r in rows("persons.tsv")}

    cycles = []
    for r in rows("qa_cycles.tsv"):
        chain = r["chain_qids"].split(" -> ")
        cycles.append({"len": int(r["cycle_len"]), "chain": chain,
                       "edges": [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]})

    wd_of = {q: (persons.get(q, {}).get("wikidata_qid") or "").strip()
             for cy in cycles for q in cy["chain"]}
    wd = fetch([v for v in wd_of.values() if v])

    def lab(q):
        return " ".join((persons.get(q, {}).get("label") or "").split()) or q

    def verdict(p, c):
        """Classify one cycle edge p->c against Wikidata."""
        wp, wc = wd_of.get(p), wd_of.get(c)
        if not wp or not wc:
            missing = " and ".join(x for x, ok in ((lab(p), wp), (lab(c), wc)) if not ok)
            return "unknown", "no Wikidata ID for %s" % missing
        ep, ec = wd.get(wp), wd.get(wc)
        if ep is None or ec is None:
            return "unknown", "Wikidata item deleted or missing"

        p_is_parent = wp in ec["father"] + ec["mother"] or wc in ep["child"]
        c_is_parent = wc in ep["father"] + ep["mother"] or wp in ec["child"]

        if p_is_parent and c_is_parent:
            return "inherited", ("Wikidata itself has %s (%s) as BOTH parent and child "
                                 "of %s (%s) — the contradiction is upstream"
                                 % (lab(p), wp, lab(c), wc))
        if p_is_parent:
            return "confirmed", "Wikidata agrees %s is a parent of %s" % (lab(p), lab(c))
        if c_is_parent:
            return "contradicted", ("Wikidata has the link the other way round: %s is a "
                                    "parent of %s" % (lab(c), lab(p)))
        real = [wd[x]["label"] or x for x in ec["father"] + ec["mother"] if x in wd]
        return "contradicted", ("Wikidata records no link between them%s"
                                % ("; it gives %s's parents as %s"
                                   % (lab(c), ", ".join(real)) if real else ""))

    out_rows = []
    per_cycle = []
    for cy in cycles:
        vs = [(p, c) + verdict(p, c) for p, c in cy["edges"]]
        kinds = {v[2] for v in vs}
        if "inherited" in kinds:
            cls = "inherited from Wikidata"
        elif "contradicted" in kinds:
            cls = "Wikidata decides it"
        elif kinds == {"confirmed"}:
            cls = "Wikidata agrees with every edge"
        else:
            cls = "not in Wikidata"
        per_cycle.append(cls)
        for p, c, kind, why in vs:
            out_rows.append({
                "cycle_len": cy["len"], "cycle_head": cy["chain"][0],
                "parent": "%s (%s)" % (p, lab(p)), "child": "%s (%s)" % (c, lab(c)),
                "wd_parent": wd_of.get(p, ""), "wd_child": wd_of.get(c, ""),
                "verdict": kind, "detail": why,
            })

    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n",
                           fieldnames=["cycle_len", "cycle_head", "parent", "child",
                                       "wd_parent", "wd_child", "verdict", "detail"])
        w.writeheader()
        w.writerows(out_rows)

    from collections import Counter
    ec = Counter(r["verdict"] for r in out_rows)
    cc = Counter(per_cycle)
    total_edges = len(out_rows)
    print("wrote %s" % OUT)
    print("\ncycle edges checked: %d" % total_edges)
    for k in ("confirmed", "inherited", "contradicted", "unknown"):
        if ec[k]:
            print("  %-13s %4d  (%4.1f%%)" % (k, ec[k], 100.0 * ec[k] / total_edges))
    print("\ncycles by what Wikidata says: %d total" % len(cycles))
    for k, n in cc.most_common():
        print("  %-32s %d" % (k, n))

    both = [q for q, e in wd.items() if e and set(e["child"]) & set(e["father"] + e["mother"])]
    print("\nWikidata items that list the same person as both a parent and a child "
          "of themselves: %d" % len(both))
    for q in both[:12]:
        print("  %s  %s" % (q, wd[q]["label"] or "(no en label)"))


if __name__ == "__main__":
    main()
