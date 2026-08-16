"""
Extract the genealogy graph from dumped wikibase items.

Produces compact TSVs under wikibase/analysis/:
- persons.tsv    one row per item with label, sex, dates, external IDs
- edges.tsv      directed parent -> child edges (from P47/P48/P20)
- spouses.tsv    undirected spouse pairs (from P42; deduped canonical form)
- redirects.tsv  filename qid -> internal id, for files whose id differs
- qa_self_edges.tsv  records listing themselves as their own parent
- qa_vacated_refs.tsv  claims naming a qid that redirects somewhere else

EVERY OUTPUT IS WRITTEN ATOMICALLY (tmp file, then os.replace). persons.tsv used to be
opened "w" and written row by row during the scan, so at any moment before the run
finished the file on disk was a valid-looking PREFIX of the real thing: it parsed, its
rows were well formed, and nothing downstream checked that the run completed.
verify_repair.py calls this script as its first step, so an interrupted extract left
compare_tangles, compare_depth and check_invariants all reading a half-file -- failing in
the direction that reports success. It happened for real on 2026-08-12, truncating
persons.tsv by 71,218 rows, and the run has been killed by a bounded runner twice since.
An interrupted run now leaves the previous good file untouched.

Parent/child source of truth (which P-IDs carry genealogical meaning):
  P47 = Father, P48 = Mother, P20 = Child, P42 = Spouse, P55 = Sex,
  P56 = Date of Birth, P57 = Date of Death.

Edges are deduped so an A--B link present as both Father(A)->Child(B)
and Child(A)->Parent(B) counts once.
"""
import json
import os
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
ITEMS = REPO / "wikibase" / "items"
OUT = REPO / "wikibase" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

class AtomicWrite:
    """Write to <name>.tmp, then os.replace onto <name> only if the block completes.

    os.replace is atomic on Windows and POSIX alike, so a reader either sees the whole
    previous file or the whole new one -- never a prefix of the new one. On any exception,
    and on a kill that unwinds normally, the temp file is removed and the old output
    stands. A hard kill (-9) leaves a .tmp behind, which is harmless and obvious.
    """

    def __init__(self, path, header=None):
        self.path = path
        self.tmp = path.with_suffix(path.suffix + ".tmp")
        self.header = header
        self.f = None

    def __enter__(self):
        self.f = open(self.tmp, "w", encoding="utf-8", newline="\n")
        if self.header:
            self.f.write(self.header)
        return self.f

    def __exit__(self, exc_type, exc, tb):
        self.f.close()
        if exc_type is None:
            os.replace(self.tmp, self.path)
        else:
            try:
                os.unlink(self.tmp)
            except OSError:
                pass
        return False


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

    persons_out = AtomicWrite(
        OUT / "persons.tsv",
        "qid\tlabel\tsex\tbirth\tdeath\tgedcom\twikidata_qid\tgeni_id\n")
    persons_f = persons_out.__enter__()

    parent_edges = set()  # (parent_qid, child_qid)
    spouse_pairs = set()  # canonicalized frozenset
    redirects = {}        # filename_qid -> target entity id (for items with mismatched id)
    seen_ids = set()      # canonical entity ids already written
    # (owner_qid, pid, raw_target) for every genealogical claim, kept raw. The redirect map
    # is only complete once the scan is, so the mismatches cannot be identified until
    # afterwards -- see the qa_vacated_refs.tsv block below for what this is for.
    raw_refs = []

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
                raw_refs.append((qid, P_FATHER, parent))
        for c in claims.get(P_MOTHER, []):
            parent = get_entity_id(c)
            if parent:
                parent_edges.add((parent, qid))
                raw_refs.append((qid, P_MOTHER, parent))
        # Child(X) of qid  =>  qid -> X
        for c in claims.get(P_CHILD, []):
            child = get_entity_id(c)
            if child:
                parent_edges.add((qid, child))
                raw_refs.append((qid, P_CHILD, child))

        # Spouse edges: undirected
        for c in claims.get(P_SPOUSE, []):
            other = get_entity_id(c)
            if other and other != qid:
                spouse_pairs.add(frozenset((qid, other)))
                raw_refs.append((qid, P_SPOUSE, other))

        if (i + 1) % 20000 == 0:
            print(f"  {i+1}/{total}  parent_edges={len(parent_edges):,}  "
                  f"spouses={len(spouse_pairs):,}", flush=True)

    persons_out.__exit__(None, None, None)

    # Canonicalize edges: rewrite any QID that is a known redirect source
    # to its target. Edges collected from claims may still cite the redirect
    # source (e.g. Father = Q136398 where Q136398 -> Q115039).
    def canon(q):
        return redirects.get(q, q)

    canon_parent = {(canon(a), canon(b)) for a, b in parent_edges
                    if canon(a) != canon(b)}

    # Self-edges are excluded from the graph above -- correct, since a self-loop is not a
    # usable ancestry edge and would distort the SCC work -- but excluding them silently
    # made check_invariants.py's I2 ("no record is its own parent, self_loops must always
    # be 0") VACUOUS on its default tsv source: it reads edges.tsv, which by construction
    # can never contain one. It reported 0 while Q72786 listed itself in both P47 and P20.
    # So record them separately, and let I2 read this instead.
    self_edges = sorted({canon(a) for a, b in parent_edges if canon(a) == canon(b)},
                        key=lambda q: (0, int(q[1:])) if q[1:].isdigit() else (1, q))
    with AtomicWrite(OUT / "qa_self_edges.tsv", "qid\n") as f:
        for q in self_edges:
            f.write(f"{q}\n")
    canon_spouses = set()
    for pair in spouse_pairs:
        a, b = tuple(pair)
        ca, cb = canon(a), canon(b)
        if ca != cb:
            canon_spouses.add(frozenset((ca, cb)))

    with AtomicWrite(OUT / "edges.tsv", "parent\tchild\n") as f:
        for a, b in sorted(canon_parent):
            f.write(f"{a}\t{b}\n")

    with AtomicWrite(OUT / "spouses.tsv", "a\tb\n") as f:
        for pair in sorted(tuple(sorted(pair)) for pair in canon_spouses):
            f.write(f"{pair[0]}\t{pair[1]}\n")

    with AtomicWrite(OUT / "redirects.tsv", "from_qid\tto_qid\n") as f:
        for src, dst in sorted(redirects.items(), key=lambda kv: int(kv[0][1:])):
            f.write(f"{src}\t{dst}\n")

    # qa_vacated_refs.tsv -- every genealogical claim naming a qid that redirects elsewhere.
    #
    # merge_cluster.py's standing rule is that after a merge no file may still claim the
    # loser's qid, because vacating a qid some file still claims lets that file win it and
    # inject its claims -- the phantom Cato 2-cycle came from exactly that. But its sweep
    # checks whether a file's own id is a loser (ownership) and whether the SURVIVOR cites
    # an alias. A third-party record citing the loser is never examined; Q72786, Q144279
    # and Q72434 all did, undetected, from 2026-07-31 to 2026-08-15.
    #
    # These refs are invisible in edges.tsv by construction, because canon() resolves both
    # spellings to the same edge -- which is exactly why they accumulate unseen. This
    # script is the only place that sees the raw and canonical forms together, and it was
    # discarding the raw one. Emitting it costs one list and no extra I/O; measuring it any
    # other way needs a second 15-minute pass over 164k files, which was tried and killed
    # twice, or a git grep over 57,440 patterns, which timed out past ten minutes.
    #
    # SCOPE, and it is a real limit: this counts RECORDS, not files. A shadow file whose id
    # is already in seen_ids is skipped by the scan, so a reference held only in a shadow
    # copy is not counted. Shadows must agree with their canonical file anyway
    # (shadow_audit.py at 0), and repoint_vacated_qids.py finds every FILE with git grep at
    # repair time. That split is deliberate -- but do not read this number as a file count.
    vacated = [(owner, pid, raw, canon(raw)) for owner, pid, raw in raw_refs
               if canon(raw) != raw]
    with AtomicWrite(OUT / "qa_vacated_refs.tsv",
                     "owner_qid\tpid\traw_target\tresolves_to\n") as f:
        for owner, pid, raw, to in sorted(
                vacated,
                key=lambda r: (int(r[0][1:]) if r[0][1:].isdigit() else 0, r[1], r[2])):
            f.write(f"{owner}\t{pid}\t{raw}\t{to}\n")

    # The costly shape: one person named twice in the same role on one record, once under
    # a dead spelling, so the record reads as having two parents where it has one written
    # twice. Q72434 was this until 2026-08-15.
    slots = {}
    for owner, pid, raw in raw_refs:
        slots.setdefault((owner, pid), []).append(raw)
    dup_slots = sum(1 for raws in slots.values()
                    if len(set(raws)) > len({canon(r) for r in raws}))

    print(f"\nDone.")
    print(f"  files scanned:  {total:,}")
    print(f"  canonical persons: {len(seen_ids):,}  ({persons_with_claims:,} with claims)")
    print(f"  silent redirects: {len(redirects):,}")
    print(f"  parent edges (raw):       {len(parent_edges):,}")
    print(f"  parent edges (canonical): {len(canon_parent):,}")
    print(f"  spouse pairs (raw):       {len(spouse_pairs):,}")
    print(f"  spouse pairs (canonical): {len(canon_spouses):,}")
    print(f"  claims naming a vacated qid: {len(vacated):,}  "
          f"across {len({r[0] for r in vacated}):,} record(s)")
    print(f"  ...of those, one person named TWICE in a role: {dup_slots:,} slot(s)")
    print(f"  output dir:     {OUT}")


if __name__ == "__main__":
    main()
