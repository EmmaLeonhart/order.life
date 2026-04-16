"""
Extract the genealogy graph from dumped wikibase items.

Produces compact TSVs under wikibase/analysis/:
- persons.tsv    one row per item with label, sex, dates, external IDs
- edges.tsv      directed parent -> child edges (from P47/P48/P20)
- spouses.tsv    undirected spouse pairs (from P42; deduped canonical form)

Parent/child source of truth (which P-IDs carry genealogical meaning):
  P47 = Father, P48 = Mother, P20 = Child, P42 = Spouse, P55 = Sex,
  P56 = Date of Birth, P57 = Date of Death.

Edges are deduped so an A--B link present as both Father(A)->Child(B)
and Child(A)->Parent(B) counts once.
"""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
ITEMS = REPO / "wikibase" / "items"
OUT = REPO / "wikibase" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

P_FATHER = "P47"
P_MOTHER = "P48"
P_CHILD = "P20"
P_SPOUSE = "P42"
P_SEX = "P55"
P_BIRTH = "P56"
P_DEATH = "P57"
P_GEDCOM = "P5"
P_GIVEN = "P3"
P_SURNAME = "P4"
P_WIKIDATA = "P61"
P_GENI = "P62"


def get_entity_id(claim):
    try:
        mw = claim["mainsnak"]
        if mw.get("snaktype") != "value":
            return None
        return mw["datavalue"]["value"]["id"]
    except (KeyError, TypeError):
        return None


def get_string(claim):
    try:
        mw = claim["mainsnak"]
        if mw.get("snaktype") != "value":
            return None
        v = mw["datavalue"]["value"]
        return v if isinstance(v, str) else v.get("text")
    except (KeyError, TypeError):
        return None


def get_time(claim):
    try:
        mw = claim["mainsnak"]
        if mw.get("snaktype") != "value":
            return None
        v = mw["datavalue"]["value"]
        if isinstance(v, dict):
            return v.get("time")
        if isinstance(v, str):
            return v
        return None
    except (KeyError, TypeError):
        return None


def first(values):
    for v in values:
        if v:
            return v
    return ""


def tsv_escape(s):
    if s is None:
        return ""
    return str(s).replace("\t", " ").replace("\n", " ").replace("\r", " ")


def main():
    files = sorted(ITEMS.glob("Q*.json"), key=lambda p: int(p.stem[1:]))
    total = len(files)
    print(f"Scanning {total} items...", flush=True)

    persons_f = open(OUT / "persons.tsv", "w", encoding="utf-8", newline="\n")
    persons_f.write("qid\tlabel\tsex\tbirth\tdeath\tgedcom\twikidata_qid\tgeni_id\n")

    parent_edges = set()  # (parent_qid, child_qid)
    spouse_pairs = set()  # canonicalized frozenset
    redirects = {}        # filename_qid -> target entity id (for items with mismatched id)
    seen_ids = set()      # canonical entity ids already written

    persons_with_claims = 0
    for i, p in enumerate(files):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        file_qid = p.stem
        qid = data.get("id") or file_qid
        if qid != file_qid:
            redirects[file_qid] = qid
        if qid in seen_ids:
            continue  # dedupe: file was a redirect to an entity we've already processed
        seen_ids.add(qid)
        labels = data.get("labels") or {}
        label = ""
        for code in ("en", "mul", "ja"):
            v = labels.get(code)
            if v and v.get("value"):
                label = v["value"]
                break
        if not label:
            # fall back to any language label
            for v in labels.values():
                if v.get("value"):
                    label = v["value"]
                    break

        claims = data.get("claims") or {}
        if not claims:
            persons_f.write(f"{qid}\t{tsv_escape(label)}\t\t\t\t\t\t\n")
            continue
        persons_with_claims += 1

        sex = first(get_entity_id(c) for c in claims.get(P_SEX, []))
        birth = first(get_time(c) for c in claims.get(P_BIRTH, []))
        death = first(get_time(c) for c in claims.get(P_DEATH, []))
        gedcom = first(get_string(c) for c in claims.get(P_GEDCOM, []))
        wikidata = first(get_string(c) for c in claims.get(P_WIKIDATA, []))
        geni = first(get_string(c) for c in claims.get(P_GENI, []))

        persons_f.write(
            f"{qid}\t{tsv_escape(label)}\t{sex}\t{tsv_escape(birth)}\t"
            f"{tsv_escape(death)}\t{tsv_escape(gedcom)}\t"
            f"{tsv_escape(wikidata)}\t{tsv_escape(geni)}\n"
        )

        # Parent edges: Father(X) of qid  =>  X -> qid
        for c in claims.get(P_FATHER, []):
            parent = get_entity_id(c)
            if parent:
                parent_edges.add((parent, qid))
        for c in claims.get(P_MOTHER, []):
            parent = get_entity_id(c)
            if parent:
                parent_edges.add((parent, qid))
        # Child(X) of qid  =>  qid -> X
        for c in claims.get(P_CHILD, []):
            child = get_entity_id(c)
            if child:
                parent_edges.add((qid, child))

        # Spouse edges: undirected
        for c in claims.get(P_SPOUSE, []):
            other = get_entity_id(c)
            if other and other != qid:
                spouse_pairs.add(frozenset((qid, other)))

        if (i + 1) % 20000 == 0:
            print(f"  {i+1}/{total}  parent_edges={len(parent_edges):,}  "
                  f"spouses={len(spouse_pairs):,}", flush=True)

    persons_f.close()

    # Canonicalize edges: rewrite any QID that is a known redirect source
    # to its target. Edges collected from claims may still cite the redirect
    # source (e.g. Father = Q136398 where Q136398 -> Q115039).
    def canon(q):
        return redirects.get(q, q)

    canon_parent = {(canon(a), canon(b)) for a, b in parent_edges
                    if canon(a) != canon(b)}
    canon_spouses = set()
    for pair in spouse_pairs:
        a, b = tuple(pair)
        ca, cb = canon(a), canon(b)
        if ca != cb:
            canon_spouses.add(frozenset((ca, cb)))

    with open(OUT / "edges.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("parent\tchild\n")
        for a, b in sorted(canon_parent):
            f.write(f"{a}\t{b}\n")

    with open(OUT / "spouses.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("a\tb\n")
        for pair in sorted(tuple(sorted(pair)) for pair in canon_spouses):
            f.write(f"{pair[0]}\t{pair[1]}\n")

    with open(OUT / "redirects.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("from_qid\tto_qid\n")
        for src, dst in sorted(redirects.items(), key=lambda kv: int(kv[0][1:])):
            f.write(f"{src}\t{dst}\n")

    print(f"\nDone.")
    print(f"  files scanned:  {total:,}")
    print(f"  canonical persons: {len(seen_ids):,}  ({persons_with_claims:,} with claims)")
    print(f"  silent redirects: {len(redirects):,}")
    print(f"  parent edges (raw):       {len(parent_edges):,}")
    print(f"  parent edges (canonical): {len(canon_parent):,}")
    print(f"  spouse pairs (raw):       {len(spouse_pairs):,}")
    print(f"  spouse pairs (canonical): {len(canon_spouses):,}")
    print(f"  output dir:     {OUT}")


if __name__ == "__main__":
    main()
