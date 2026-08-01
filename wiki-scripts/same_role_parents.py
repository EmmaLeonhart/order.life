"""Every child with two parents in the SAME role, graph-wide, classified.

    python wiki-scripts/same_role_parents.py

Read-only. Writes wikibase/analysis/qa_same_role_parents.tsv and a summary to stdout.

WHY THIS EXISTS

One child has one father and one mother. Two records in the same parental role for one
child is therefore always a defect -- either they are one person recorded twice, or one of
the two edges is false. It is the strongest structural duplicate signal in this dump
because it uses NO label: it caught Q64582/Q139826 "Domitia Lucilla Minor" / "Calvisia
Domitia Lucilla", both mothers of Marcus Aurelius, which every label-and-id signal missed.

But propose_tangle_repairs.py only looks INSIDE tangles -- 283 records out of 102,000 --
so it sees under 1% of the class. It found six. There are hundreds. Adnan Q65555 has two
fathers, Q66385 and Q66394, both married to the same woman Q66382; that is invisible to
the tangle-scoped detector because Adnan is in no tangle at all.

WHAT THE VERDICTS MEAN, and the order matters -- each was learned by getting it wrong:

  COLLAPSE   one of the pair is an ancestor of the other. NOT a duplicate: merging would
             fuse two generations. Checked first, because it disqualifies everything else.
             Note that MUTUAL reachability is uninformative -- inside a tangle every pair
             reaches every other -- so only a STRICTLY one-way relation counts.
  DISTINCT   both carry Wikidata ids and they differ, or the recorded sexes differ. Two
             different people, so one of the two edges is false. A CUT, not a merge, and
             which edge is wrong needs evidence this tool does not have.
  ABSENT     one side has no item file, or is a shell with no label, alias or genealogy.
             Not a person to merge with; belongs with the one-sided-edge work.
  DEDUPE     nothing distinguishes them and neither is above the other. The Domitia
             Lucilla shape. Corroboration is reported, not assumed: whether they share a
             parent, and whether they share a spouse.

DEDUPE IS A CANDIDATE, NOT A VERDICT. Every merge this session that looked obvious from a
signal and was checked by hand turned out to need the check. Read the row, open the
records.
"""

import collections
import csv
import json
import os
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
A = ROOT / "wikibase" / "analysis"
OUT = A / "qa_same_role_parents.tsv"

FATHER, MOTHER = "P47", "P48"


def qnum(q):
    return (0, int(q[1:])) if q[1:].isdigit() else (1, q)


def read_tsv(name, **kw):
    p = A / name
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    persons = {r["qid"]: r for r in read_tsv("persons.tsv")}
    red = {r["from_qid"]: r["to_qid"] for r in read_tsv("redirects.tsv")}

    def canon(q):
        for _ in range(8):
            nxt = red.get(q, q)
            if nxt == q:
                return q
            q = nxt
        return q

    par = collections.defaultdict(set)
    for r in read_tsv("edges.tsv"):
        p, c = r["parent"], r["child"]
        if p and c and p != c:
            par[c].add(p)

    spouse = collections.defaultdict(set)
    for r in read_tsv("spouses.tsv"):
        a, b = r.get("a"), r.get("b")
        if a and b and a != b:
            spouse[a].add(b)
            spouse[b].add(a)

    _anc = {}

    def ancestors(q):
        if q not in _anc:
            seen, dq = set(), deque([q])
            while dq:
                x = dq.popleft()
                for p in par.get(x, ()):
                    if p not in seen:
                        seen.add(p)
                        dq.append(p)
            _anc[q] = seen
        return _anc[q]

    # Scan once, collecting roles and substance together.
    roles = {}          # qid -> (fathers, mothers), canonicalised
    substantive = {}
    n = bad = 0
    t0 = time.time()
    with os.scandir(ITEMS) as it:
        for e in it:
            if not e.name.endswith(".json"):
                continue
            try:
                with open(e.path, "rb") as fh:
                    d = json.loads(fh.read())
            except Exception:
                bad += 1
                continue
            if not isinstance(d, dict):
                bad += 1
                continue
            q = canon(d.get("id") or e.name[:-5])
            claims = d.get("claims") or {}

            def ids(pid):
                out = []
                for c in claims.get(pid, ()):
                    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                    if isinstance(v, dict) and v.get("id"):
                        cv = canon(v["id"])
                        if cv != q and cv not in out:
                            out.append(cv)
                return out

            f, m = ids(FATHER), ids(MOTHER)
            if f or m:
                pf, pm = roles.get(q, ([], []))
                roles[q] = (sorted(set(pf) | set(f), key=qnum),
                            sorted(set(pm) | set(m), key=qnum))
            has_label = bool(((d.get("labels") or {}).get("en") or {}).get(
                "value", "").strip())
            has_alias = any(a.get("value", "").strip()
                            for a in (d.get("aliases") or {}).get("en", []))
            has_geneal = any(claims.get(p) for p in (FATHER, MOTHER, "P20", "P42"))
            substantive[q] = (substantive.get(q, False)
                              or has_label or has_alias or has_geneal)
            n += 1
            if n % 40000 == 0:
                print(f"  ...{n} items, {time.time() - t0:.0f}s", flush=True)

    def lab(q):
        return (persons.get(q, {}).get("label") or "").strip()

    def wd(q):
        return (persons.get(q, {}).get("wikidata_qid") or "").strip()

    def sex(q):
        return (persons.get(q, {}).get("sex") or "").strip()

    rows = []
    for child, (fathers, mothers) in roles.items():
        for role, lst in (("father", fathers), ("mother", mothers)):
            if len(lst) < 2:
                continue
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    a, b = lst[i], lst[j]
                    b_above_a = b in ancestors(a)
                    a_above_b = a in ancestors(b)
                    one_way = (b_above_a != a_above_b)

                    sa = ("real" if substantive.get(a) else
                          "phantom" if a in substantive else "missing")
                    sb = ("real" if substantive.get(b) else
                          "phantom" if b in substantive else "missing")
                    wa, wb = wd(a), wd(b)
                    xa, xb = sex(a), sex(b)

                    if one_way:
                        verdict = "COLLAPSE"
                    elif sa != "real" or sb != "real":
                        verdict = "ABSENT"
                    elif (wa and wb and wa != wb) or (xa and xb and xa != xb):
                        verdict = "DISTINCT"
                    else:
                        verdict = "DEDUPE"

                    shared_par = sorted(par.get(a, set()) & par.get(b, set()), key=qnum)
                    shared_sp = sorted(spouse.get(a, set()) & spouse.get(b, set()),
                                       key=qnum)
                    rows.append({
                        "verdict": verdict, "role": role, "child": child,
                        "child_label": lab(child), "a": a, "a_label": lab(a),
                        "b": b, "b_label": lab(b),
                        "a_wd": wa, "b_wd": wb, "a_kind": sa, "b_kind": sb,
                        "shared_parents": ",".join(shared_par),
                        "shared_spouses": ",".join(shared_sp),
                    })

    rows.sort(key=lambda r: (r["verdict"], qnum(r["child"])))
    fields = ["verdict", "role", "child", "child_label", "a", "a_label", "b", "b_label",
              "a_wd", "b_wd", "a_kind", "b_kind", "shared_parents", "shared_spouses"]
    # Written with plain formatting, not csv.writer, to match every other TSV in
    # wikibase/analysis. csv with QUOTE_NONE refuses a field containing '"' unless an
    # escapechar is set, and setting one would produce a file the QUOTE_NONE readers
    # cannot parse back. The dump's labels contain unescaped double quotes -- that is the
    # whole reason the readers needed fixing today -- so the only consistent choice is to
    # strip the delimiters and write the field raw.
    def cell(v):
        return str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ")

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(fields) + "\n")
        for r in rows:
            f.write("\t".join(cell(r[k]) for k in fields) + "\n")

    counts = collections.Counter(r["verdict"] for r in rows)
    kids = len({r["child"] for r in rows})
    print(f"\nitems scanned {n:,} (unreadable {bad}) in {time.time() - t0:.0f}s")
    print(f"children with two same-role parents: {kids:,}")
    print(f"colliding pairs: {len(rows):,}")
    for v in ("DEDUPE", "DISTINCT", "COLLAPSE", "ABSENT"):
        print(f"  {v:<9} {counts[v]:>6,}")
    strong = [r for r in rows
              if r["verdict"] == "DEDUPE" and (r["shared_parents"] or r["shared_spouses"])]
    print(f"\nDEDUPE with corroboration (shared parent or shared spouse): {len(strong):,}")
    print(f"written -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
