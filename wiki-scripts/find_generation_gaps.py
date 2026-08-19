"""Find the `Q200022` shape: two runs already in the dump, one generation apart.

queue.md item 0c. The Haji repair on 2026-08-18 closed a gap worth more than the item
that found it: `Q14866` Haji no Otori had **no father**, `Q15732` Haji no Mukuro had **no
child**, and *both already carried the `P61`* that says wd `Q97613635` sits between them.
One created record joined two runs that had been sitting apart in the same dump.

**Nothing looks for that shape**, and it is cheap to look for, because the test is
arithmetic on ids the dump already holds:

    take every record with NO father and a P61          -> the "bottom" of an upper run
    take every record with NO child  and a P61           -> the "top" of a lower run
    ask Wikidata whether the fatherless one's P22 chain
      reaches the childless one within a few steps

Every step of that chain is a person the dump is missing, and the endpoints are people it
already has.

WHAT THIS DOES NOT DO, DELIBERATELY

**It creates nothing and proposes no edge.** Its output is a list of gaps with the
records that would fill them, for reading one at a time. The Haji pass found Wikidata
*wrong* about one filiation — it recorded Izumo no Furune as his brother Iiirine's father,
when the Nihon Shoki has them as brothers and Furune as Iiirine's killer — so a gap that
looks arithmetically clean can still be built on a bad claim.

It is also **not a general defect sweep**: it only ever reports pairs where both endpoints
are already in the dump and already carry a Wikidata id, which is a few thousand records
out of 107,000, not the whole graph.

    python wiki-scripts/find_generation_gaps.py [--max-steps 4] [--limit 40]

Reads the analysis TSVs and Wikidata. Writes wikibase/analysis/generation_gaps.md.
"""

import collections
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "wikibase" / "analysis"
PERSONS = ANALYSIS / "persons.tsv"
EDGES = ANALYSIS / "edges.tsv"
OUT = ANALYSIS / "generation_gaps.md"

#: Wikimedia asks for a descriptive agent with a contact; without one the API returns 403.
UA = {"User-Agent": "order.life-genealogy-qa/1.0 (emma@topazcomputing.com)"}
API = "https://www.wikidata.org/w/api.php"


def read_tsvs():
    """Records, their Wikidata ids, and who has a father or a child.

    `quoting=csv.QUOTE_NONE` per CLAUDE.md: these files never quote, and the default
    reader silently drops rows whose label contains a double quote.
    """
    label, wd = {}, {}
    with open(PERSONS, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            label[r["qid"]] = r["label"]
            if r.get("wikidata_qid"):
                wd[r["qid"]] = r["wikidata_qid"]
    has_parent, has_child = set(), set()
    with open(EDGES, encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(rd)
        for parent, child in rd:
            has_child.add(parent)
            has_parent.add(child)
    return label, wd, has_parent, has_child


def fetch(ids):
    """P22/P25 and the English label for a batch of Wikidata items."""
    out = {}
    ids = [i for i in ids if i]
    for i in range(0, len(ids), 45):
        url = (f"{API}?action=wbgetentities&ids={'|'.join(ids[i:i + 45])}"
               "&props=claims|labels&languages=en&format=json")
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as fh:
                ents = json.load(fh)["entities"]
        except Exception as e:                                   # noqa: BLE001
            print(f"  fetch failed for a batch: {e}", file=sys.stderr)
            continue
        for q, e in ents.items():
            parents = []
            for pid in ("P22", "P25"):
                for c in (e.get("claims") or {}).get(pid, []):
                    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                    if isinstance(v, dict) and v.get("id"):
                        parents.append(v["id"])
            out[q] = (((e.get("labels") or {}).get("en") or {}).get("value"), parents)
        time.sleep(0.15)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    max_steps = 4
    limit = 40
    if "--max-steps" in sys.argv:
        max_steps = int(sys.argv[sys.argv.index("--max-steps") + 1])
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    label, wd, has_parent, has_child = read_tsvs()
    fatherless = [q for q in wd if q not in has_parent]
    childless = [q for q in wd if q not in has_child]
    target = {wd[q]: q for q in childless}          # wikidata id -> our qid

    print(f"records carrying a Wikidata id : {len(wd):,}")
    print(f"  ...with no parent in our graph: {len(fatherless):,}  (the bottoms of upper runs)")
    print(f"  ...with no child  in our graph: {len(childless):,}  (the tops of lower runs)")
    print(f"walking up to {max_steps} step(s) from each fatherless record\n")

    # walk up from every fatherless record, level by level, all of them at once
    frontier = {wd[q]: (q, []) for q in fatherless}          # wd id -> (our start qid, chain)
    seen = set(frontier)
    gaps = []
    for step in range(1, max_steps + 1):
        info = fetch(sorted(frontier))
        nxt = {}
        for wid, (start, chain) in frontier.items():
            name, parents = info.get(wid, (None, []))
            for p in parents:
                if p in target and target[p] != start:
                    gaps.append((step, start, target[p], chain + [p]))
                elif p not in seen:
                    seen.add(p)
                    nxt[p] = (start, chain + [p])
        print(f"  step {step}: {len(frontier):,} item(s) queried, "
              f"{len(nxt):,} new ancestor(s), {len(gaps):,} gap(s) so far", flush=True)
        frontier = nxt
        if not frontier:
            break

    gaps.sort()
    lines = ["# Generation gaps: two runs one link apart, both already in the dump", "",
             "Generated by `wiki-scripts/find_generation_gaps.py`. **Proposes nothing.**",
             "",
             f"- records carrying a Wikidata id: **{len(wd):,}**",
             f"- of those, no parent here: **{len(fatherless):,}**; no child here: "
             f"**{len(childless):,}**",
             f"- gaps found within {max_steps} step(s): **{len(gaps):,}**", "",
             "`steps` is how many people are missing between the two, so **1 means they "
             "are parent and child and the dump simply does not say so**.", "",
             "| steps | fatherless record | its Wikidata chain upward | reaches | which is |",
             "| ---: | --- | --- | --- | --- |"]
    for step, lower, upper, chain in gaps[:limit]:
        lines.append(f"| {step} | `{lower}` {label.get(lower, '')} | "
                     f"{' → '.join(chain)} | `{wd[upper]}` | `{upper}` {label.get(upper, '')} |")
    if len(gaps) > limit:
        lines.append("")
        lines.append(f"*{len(gaps) - limit} further gap(s) not listed; raise `--limit`.*")
    lines += ["", "## Before filling any of these",
              "",
              "**Read the case.** The Haji pass found Wikidata wrong about one filiation — "
              "it recorded Izumo no Furune as the father of his brother Iiirine, whom the "
              "Nihon Shoki says he killed. A gap that is arithmetically clean can still "
              "rest on a bad claim.",
              "",
              "**A `steps` of 1 is not a missing record at all** — it means both people are "
              "already here and the edge between them is simply absent. That is an "
              "`add_bridge_edges.py` edge, not a created person."]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}  ({len(gaps):,} gap(s))")
    for step, lower, upper, chain in gaps[:12]:
        print(f"  {step} step(s): {lower} {label.get(lower, '')[:26]:26} -> "
              f"{upper} {label.get(upper, '')[:26]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
