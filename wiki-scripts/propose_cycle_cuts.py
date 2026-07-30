#!/usr/bin/env python
"""Propose one edge to cut per ancestry cycle — PROPOSE ONLY, edits nothing.

Reads the committed local dump extracts and writes a review file:
    wikibase/analysis/qa_cycles_proposed.tsv
with columns: cycle_len, chain_qids, cut_parent, cut_child, reason, confidence

Nothing in wikibase/items/*.json or the source *.tsv extracts is modified.
Where the evidence does not decide a cycle, the row is emitted with empty
cut_parent/cut_child and confidence=unresolved — that is a correct outcome.

Evidence rules, strongest first:

  R1 date_direct      Both endpoints carry an explicit birth year and the parent
                      is born at/after the child. Impossible; magnitude reported.
  R2 patronymic_rev   The parent's own name is a patronymic naming the child as
                      *its* father (Welsh "ap/ab/ferch/verch", Iberian -es/-ez).
                      The edge is pointing the wrong way.
  R3 duplicate_adj    The two endpoints of the edge are near-namesakes, i.e. the
                      data says a person is the parent of their own duplicate.
                      This is the Geni merge artifact in its clearest form and it
                      shows up inside long cycles, not only 2-node ones.
  R4 date_bounded     Birth-year bounds inferred from DATED RELATIVES WITHIN 3
                      GENERATIONS (never longer, and never through a cycle edge)
                      put the parent's earliest possible birth after the child's
                      latest possible birth. Provenance is reported per row.
  R5 duplicate_pair   A 2-node cycle whose labels are similar but below the R3
                      bar: still a merge artifact, direction chosen by sourcing.
  R6 sourcing_weakest Last resort. One edge in the cycle is uniquely worst-sourced
                      (fewest external IDs / dates across its two endpoints) while
                      every other edge carries corroboration. Low confidence.

Edges that R2/co-parent agreement positively CORROBORATE are protected from being
chosen, which is often what isolates the single bad edge in an otherwise sound chain.

Deliberately NOT used: unbounded birth-year propagation over the whole graph. The
dump's mythic tier is ~1000 generations deep, so a +12-years-per-generation walk
compounds into bounds like "born no earlier than 12372" and fires on every edge in
a chain. Bounds are therefore capped at MAX_HOPS generations from a real date.
"""

import csv
import re
import sys
from collections import defaultdict, deque
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "wikibase" / "analysis"

MALE = "Q153718"
FEMALE = "Q153719"

# Minimum plausible parent->child birth-year gap, used for bound inference only.
MIN_GAP = 12
# How many generations a date anchor may be carried. Past this the +MIN_GAP
# accumulation stops meaning anything (see module docstring).
MAX_HOPS = 3
# Label similarity at/above which two adjacent records are treated as the same
# person duplicated rather than two people.
DUP_ADJACENT = 0.72
DUP_PAIR = 0.55

csv.field_size_limit(10_000_000)


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_persons():
    persons = {}
    with open(ANALYSIS / "persons.tsv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            persons[row["qid"]] = row
    return persons


def load_edges():
    edges = []
    with open(ANALYSIS / "edges.tsv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            edges.append((row["parent"], row["child"]))
    return edges


def load_spouses():
    pairs = set()
    with open(ANALYSIS / "spouses.tsv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            pairs.add(frozenset((row["a"], row["b"])))
    return pairs


def load_cycles():
    cycles = []
    with open(ANALYSIS / "qa_cycles.tsv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            chain = row["chain_qids"].split(" -> ")
            cycles.append({
                "cycle_len": int(row["cycle_len"]),
                "chain_qids": row["chain_qids"],
                "chain_labels": row["chain_labels"],
                "nodes": chain,
                "edges": [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)],
            })
    return cycles


# --------------------------------------------------------------------------
# dates
# --------------------------------------------------------------------------

YEAR_RE = re.compile(r"^([+-])(\d+)-")


def year_of(stamp):
    """Wikibase time stamp -> int year, or None."""
    if not stamp:
        return None
    m = YEAR_RE.match(stamp)
    if not m:
        return None
    sign, digits = m.group(1), m.group(2)
    try:
        y = int(digits)
    except ValueError:
        return None
    if y == 0:
        return None
    # Deep-time geological stamps (-13000000000) are cosmology nodes, not people;
    # they are real data but useless as a person-level generation constraint.
    if y > 100_000:
        return None
    return -y if sign == "-" else y


# --------------------------------------------------------------------------
# patronymics
# --------------------------------------------------------------------------

WELSH_RE = re.compile(r"\b(?:ap|ab|ferch|verch|vch|ferch)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÑ][\w'À-ɏ]*)")

# Irregular Iberian patronymics that suffix-stripping cannot recover.
IRREGULAR = {
    "pires": "pedro", "peres": "pedro", "perez": "pedro", "pérez": "pedro",
    "pais": "paio", "paes": "paio", "pais": "paio",
    "soares": "soeiro", "suarez": "soeiro", "suárez": "soeiro",
    "dias": "diogo", "díaz": "diogo", "diaz": "diogo",
    "eanes": "joão", "anes": "joão", "joanes": "joão",
    "viegas": "egas",
    "nunes": "nuno", "núñez": "nuno", "nunez": "nuno",
    "vasques": "vasco", "vázquez": "vasco", "vazquez": "vasco",
    "lopes": "lopo", "lópez": "lopo", "lopez": "lopo",
    "garcês": "garcia", "garces": "garcia",
    "eriz": "ero",
    "ausendes": "ausindo",
    "muniz": "munio", "moniz": "munio",
    "veloso": None,
}

PATRONYMIC_SUFFIXES = ("endes", "aldes", "alves", "igues", "andes", "iques",
                       "aches", "eves", "unes", "eres", "ares", "ides",
                       "ues", "es", "ez", "iz", "az", "oz")


def strip_diacritics(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def norm(s):
    return strip_diacritics(s or "").lower().strip(" .,")


def tokens(label):
    return [t for t in re.split(r"[\s.,]+", label or "") if t]


def given_name(label):
    """First substantive token of a label, skipping honorifics."""
    skip = {"d", "dom", "don", "dona", "d.", "n.n.", "nn", "saint", "st",
            "sir", "king", "queen", "prince", "princess", "count", "sao", "são"}
    for t in tokens(label):
        n = norm(t)
        if n and n not in skip and len(n) > 1:
            return n
    return ""


def implied_father(label, sex):
    """Father's given name as asserted by this person's own name, or None.

    Welsh: 'Rhys ap Llowdden' -> llowdden.  Iberian: 'Pero Pais' -> paio.
    Returns (father_given, style) or (None, None).
    """
    if not label:
        return None, None

    m = WELSH_RE.search(label)
    if m:
        return norm(m.group(1)), "welsh"

    toks = tokens(label)
    if len(toks) >= 2:
        for t in toks[1:]:
            n = norm(t)
            if n in IRREGULAR:
                val = IRREGULAR[n]
                if val:
                    return val, "iberian"
                continue
            if len(n) < 5:
                continue
            for suf in PATRONYMIC_SUFFIXES:
                if n.endswith(suf) and len(n) - len(suf) >= 3:
                    root = n[: -len(suf)]
                    # 'Goncalves' -> 'goncalv' -> goncalo needs a vowel restore;
                    # fuzzy-match handles the tail, we only need a candidate root.
                    return root, "iberian"
    return None, None


def name_matches(candidate_root, actual_given):
    """Does a patronymic root plausibly denote this given name?"""
    if not candidate_root or not actual_given:
        return False
    a, b = norm(candidate_root), norm(actual_given)
    if a == b:
        return True
    if b.startswith(a) and len(a) >= 4:
        return True
    if a.startswith(b) and len(b) >= 4:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.82


# --------------------------------------------------------------------------
# bound propagation over the acyclic part of the graph
# --------------------------------------------------------------------------

def build_dag(edges):
    """Return (kept_edges, dropped) with all back edges removed via iterative DFS."""
    children = defaultdict(list)
    nodes = set()
    for p, c in edges:
        children[p].append(c)
        nodes.add(p)
        nodes.add(c)

    WHITE, GREY, BLACK = 0, 1, 2
    color = defaultdict(int)
    back = set()

    # Sorted iteration, not set order: this file is a committed review artifact and
    # must regenerate identically. Python randomises str hashing per process.
    for start in sorted(nodes):
        if color[start] != WHITE:
            continue
        stack = [(start, iter(children[start]))]
        color[start] = GREY
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if color[nxt] == GREY:
                    back.add((node, nxt))
                elif color[nxt] == WHITE:
                    color[nxt] = GREY
                    stack.append((nxt, iter(children[nxt])))
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()
    kept = [e for e in edges if e not in back]
    return kept, back


def own_lower(person):
    """Earliest year this person could have been born, from their own record."""
    by = year_of(person.get("birth"))
    if by is not None:
        return by
    dy = year_of(person.get("death"))
    if dy is not None:
        return dy - 120
    return None


def own_upper(person):
    """Latest year this person could have been born, from their own record."""
    by = year_of(person.get("birth"))
    if by is not None:
        return by
    dy = year_of(person.get("death"))
    if dy is not None:
        return dy
    return None


def bounded_bounds(targets, persons, parents_of, children_of, blocked):
    """Birth-year bounds for `targets`, from dated relatives <= MAX_HOPS away.

    `blocked` is the set of edges under test (every listed cycle edge); anchors are
    never carried across one, so an edge is never used as evidence about itself.
    Returns lo, hi: qid -> (year, source_qid, hops) or absent.
    """
    lo, hi = {}, {}
    for t in sorted(targets):
        own = persons.get(t, {})
        best_lo = None
        v = own_lower(own)
        if v is not None:
            best_lo = (v, t, 0)
        best_hi = None
        v = own_upper(own)
        if v is not None:
            best_hi = (v, t, 0)

        # walk up for lower bounds: ancestor born >= X  =>  t born >= X + 12*hops
        seen = {t}
        frontier = [t]
        for hop in range(1, MAX_HOPS + 1):
            nxt = []
            for n in frontier:
                for a in parents_of.get(n, ()):
                    if (a, n) in blocked or a in seen:
                        continue
                    seen.add(a)
                    nxt.append(a)
                    v = own_lower(persons.get(a, {}))
                    if v is not None:
                        cand = (v + MIN_GAP * hop, a, hop)
                        if best_lo is None or cand[0] > best_lo[0]:
                            best_lo = cand
            frontier = nxt

        # walk down for upper bounds: descendant born <= Y  =>  t born <= Y - 12*hops
        seen = {t}
        frontier = [t]
        for hop in range(1, MAX_HOPS + 1):
            nxt = []
            for n in frontier:
                for d in children_of.get(n, ()):
                    if (n, d) in blocked or d in seen:
                        continue
                    seen.add(d)
                    nxt.append(d)
                    v = own_upper(persons.get(d, {}))
                    if v is not None:
                        cand = (v - MIN_GAP * hop, d, hop)
                        if best_hi is None or cand[0] < best_hi[0]:
                            best_hi = cand
            frontier = nxt

        if best_lo:
            lo[t] = best_lo
        if best_hi:
            hi[t] = best_hi
    return lo, hi


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------

def sourcing_score(person):
    if not person:
        return 0
    s = 0
    if person.get("wikidata_qid"):
        s += 3
    if person.get("geni_id"):
        s += 1
    if person.get("gedcom"):
        s += 1
    if person.get("birth"):
        s += 2
    if person.get("death"):
        s += 2
    if person.get("sex"):
        s += 1
    return s


def label(persons, qid):
    return re.sub(r"\s+", " ", (persons.get(qid, {}).get("label") or qid)).strip()


ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
         "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13,
         "xiv": 14, "xv": 15}
YOUNGER = {"junior", "jr", "younger", "ii", "the younger", "minor", "menor", "jovem"}
ELDER = {"senior", "sr", "elder", "the elder", "maior", "major", "mayor", "velho"}


def ordinal_of(lbl):
    """(rank, label-with-ordinal-removed) for regnal/generation numbering.

    'Guerau V de Cabrera' -> (5, 'guerau de cabrera'); 'Generation 4' -> (4, 'generation').
    Returns (None, normalised label) when the label carries no ordinal.
    """
    rank = None
    rest = []
    for t in tokens(lbl):
        n = norm(t)
        if rank is None and n in ROMAN:
            rank = ROMAN[n]
            continue
        if rank is None and n.isdigit() and len(n) <= 2:
            rank = int(n)
            continue
        if rank is None and n in YOUNGER:
            rank = 2
            continue
        if rank is None and n in ELDER:
            rank = 1
            continue
        rest.append(n)
    return rank, " ".join(rest)


def ordinal_relation(plab, clab):
    """'succession' / 'reversed' / None for a same-name pair distinguished by ordinal.

    'Guerau IV -> Guerau V' is a *correct* father->son edge, not a duplicate; the
    numbering is what distinguishes two real people. The reverse direction is a
    genuine error.
    """
    pr, prest = ordinal_of(plab)
    cr, crest = ordinal_of(clab)
    if pr is None and cr is None:
        return None
    if not prest or prest != crest:
        return None
    if pr is None or cr is None:
        # Only one side is marked ('Marcus Livius Drusus' / 'Marcus Livius maior
        # Drusus'). The marker exists precisely to separate two same-named people,
        # so they are distinct — but which is elder is not reliably encoded, so
        # report the protective reading.
        return "succession"
    if pr == cr:
        return None
    return "succession" if pr < cr else "reversed"


def era_ambiguous(y):
    """True when a positive year this small is probably an unsigned BC date.

    The dump records many Roman republican figures as +0300 / +0400 where the
    source meant 300 BC / 400 BC. Any date comparison resting on such a year can
    be explained by the sign error instead of by a bad edge.
    """
    return y is not None and 0 < y < 500


def label_similarity(a, b):
    """0.0 when either label is missing or too short to carry information.

    ~2,900 records in the dump have no label at all; SequenceMatcher scores two
    empty strings as a perfect match, which would invent duplicate pairs.
    """
    na, nb = norm(a), norm(b)
    if len(na) < 4 or len(nb) < 4:
        return 0.0
    if re.fullmatch(r"q\d+", na) or re.fullmatch(r"q\d+", nb):
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def evaluate_edge(p, c, persons, lo, hi, spouses, parents_of):
    """Return list of (kind, strength, detail). Positive strength = cut evidence."""
    out = []
    pp, cc = persons.get(p, {}), persons.get(c, {})
    plab, clab = label(persons, p), label(persons, c)

    # R1 — explicit dates on both endpoints
    pb, cb = year_of(pp.get("birth")), year_of(cc.get("birth"))
    if pb is not None and cb is not None and pb >= cb:
        detail = ("recorded birth %d (%s) is not before recorded birth %d (%s)"
                  % (pb, plab, cb, clab))
        if era_ambiguous(pb) and (era_ambiguous(cb) or cb < 0):
            out.append(("date_ambiguous_era", 610, detail +
                        " — BUT the parent's year is recorded as a small positive "
                        "number, which in this dump usually means an unsigned BC "
                        "date. Read as BC the order is fine, so this may be a "
                        "mis-signed DATE rather than a bad EDGE. Check the date "
                        "first; do not cut on this alone"))
        else:
            out.append(("date_direct", 1000 + min(pb - cb, 500), detail))

    # R2 — the parent's own name calls the child its father
    pf, _ = implied_father(plab, pp.get("sex"))
    cf, _ = implied_father(clab, cc.get("sex"))
    if pf and name_matches(pf, given_name(clab)) and cc.get("sex") != FEMALE:
        out.append(("patronymic_reversal", 900,
                    "parent's own patronymic (%s) names the child as ITS father; "
                    "edge points the wrong way" % plab))

    # R3 — the two endpoints are the same person duplicated, or same-family homonyms
    sim = label_similarity(plab, clab)
    rel = ordinal_relation(plab, clab)
    if rel == "succession":
        out.append(("ordinal_support", -400,
                    "'%s' -> '%s' is a regnal/generational succession in the right "
                    "order — the numbering is what distinguishes two real people, "
                    "so this is a plausible father-son edge, not a duplicate"
                    % (plab, clab)))
    elif rel == "reversed":
        out.append(("ordinal_reversed", 750,
                    "'%s' -> '%s' runs the regnal/generational numbering BACKWARDS: "
                    "the higher-numbered namesake is listed as parent of the lower"
                    % (plab, clab)))
    elif sim >= DUP_ADJACENT:
        # Same name means the SAME name. Roman practice distinguishes father from
        # son by cognomen ('Scipio Barbatus' -> 'Scipio', 'Metellus Macedonicus' ->
        # 'Metellus Balearicus'), so a shared praenomen+nomen is not duplication.
        if sorted(norm(t) for t in tokens(plab)) == sorted(norm(t) for t in tokens(clab)):
            out.append(("duplicate_adjacent", 800 + int(sim * 100),
                        "endpoints carry the IDENTICAL name ('%s') — the data makes "
                        "a person the parent of their own duplicate. Proposed action "
                        "is a MERGE of the two records; cutting this edge is the "
                        "minimal fix" % plab))
        else:
            # A shared GIVEN name ('Barbara, imperatriz of Rome' / 'Barbara,
            # Princess of Rome') is a far better duplicate signal than raw string
            # overlap, which two same-surname relatives score just as highly on.
            same_given = given_name(plab) == given_name(clab) and given_name(plab)
            out.append(("homonym_adjacent", 500 + int(sim * 100) + (40 if same_given else 0),
                        "endpoints share part of a name but not all of it (%.0f%% "
                        "similar: '%s' / '%s'). Roman families distinguish father "
                        "from son by cognomen and Welsh ones by patronymic, so these "
                        "may well be two real people — but a same-family pair inside "
                        "a cycle is also where Geni merges collapse a generation. "
                        "VERIFY before cutting; this is the likeliest edge in the "
                        "cycle, not a proven error" % (sim * 100, plab, clab)))

    # R4 — bounds from dated relatives within MAX_HOPS
    lp, hc = lo.get(p), hi.get(c)
    if lp and hc and lp[0] > hc[0]:
        detail = ("%s born no earlier than %d (from %s b.%s, %d generation(s) up); "
                  "%s born no later than %d (from %s, %d generation(s) down)"
                  % (plab, lp[0], label(persons, lp[1]),
                     (persons.get(lp[1], {}).get("birth") or "?")[:5], lp[2],
                     clab, hc[0], label(persons, hc[1]), hc[2]))
        if era_ambiguous(lp[0]) or era_ambiguous(hc[0]) or (lp[0] > 0) != (hc[0] > 0):
            out.append(("date_bounded_ambiguous_era", 580, detail +
                        " — BUT one of these anchors is a small positive year or the "
                        "two straddle year 0, which in this dump usually means an "
                        "unsigned BC date. The bound may be an artifact of the sign, "
                        "not a real contradiction"))
        else:
            out.append(("date_bounded", 600 + min(lp[0] - hc[0], 200), detail))

    # corroboration (negative strength = protect this edge)
    if cf and name_matches(cf, given_name(plab)) and pp.get("sex") != FEMALE:
        out.append(("patronymic_support", -500,
                    "child's patronymic (%s) names this parent" % clab))
    co = [q for q in parents_of.get(c, []) if q != p
          and frozenset((q, p)) in spouses]
    if co:
        if sim >= DUP_ADJACENT:
            # Two near-identically named records sharing a spouse is what a merge
            # looks like from the inside, not independent confirmation of the edge.
            out.append(("coparent_shared_with_namesake", 60,
                        "and the two records share a spouse (%s), which is what a "
                        "duplicated person looks like rather than corroboration"
                        % label(persons, co[0])))
        else:
            out.append(("coparent_support", -300,
                        "co-parent %s is a recorded spouse" % label(persons, co[0])))
    return out


def choose_cut(cycle, persons, lo, hi, spouses, parents_of, edge_freq):
    edges = cycle["edges"]
    scored = []
    for p, c in edges:
        ev = evaluate_edge(p, c, persons, lo, hi, spouses, parents_of)
        cut_ev = [e for e in ev if e[1] > 0]
        prot_ev = [e for e in ev if e[1] < 0]
        best = max((e[1] for e in cut_ev), default=0)
        protect = sum(e[1] for e in prot_ev)
        scored.append({
            "edge": (p, c), "cut_ev": cut_ev, "prot_ev": prot_ev,
            "score": best + protect,
            "src": sourcing_score(persons.get(p)) + sourcing_score(persons.get(c)),
            "freq": edge_freq[(p, c)],
        })

    positives = [s for s in scored if s["cut_ev"] and s["score"] > 0]
    if positives:
        positives.sort(key=lambda s: (-s["score"], -s["freq"], s["src"], s["edge"]))
        top = positives[0]
        ranked = sorted(top["cut_ev"], key=lambda e: -e[1])
        kind, _, detail = ranked[0]
        for _, _, extra in ranked[1:]:          # keep corroborating evidence visible
            detail += " | " + extra
        conf = {"date_direct": "high", "patronymic_reversal": "high",
                "duplicate_adjacent": "high", "ordinal_reversed": "medium",
                "date_bounded": "medium", "homonym_adjacent": "low",
                "date_ambiguous_era": "low",
                "date_bounded_ambiguous_era": "low"}.get(kind, "medium")
        tie = [s for s in positives[1:] if s["score"] == top["score"]]
        if tie:
            conf = "low"
            detail += "; NOTE %d other edge(s) in this cycle carry equally strong " \
                      "evidence — cut chosen by cross-cycle frequency" % len(tie)
        return top["edge"], kind, detail, conf

    # R4 — 2-node cycles are merge artifacts by construction
    if len(edges) == 2:
        a, b = edges[0][0], edges[0][1]
        sim = label_similarity(label(persons, a), label(persons, b))
        # cut the direction whose endpoints are worse sourced
        scored.sort(key=lambda s: (s["src"], -s["freq"], s["edge"]))
        weak = scored[0]
        if sim >= 0.55:
            return (weak["edge"], "duplicate_pair",
                    "2-node cycle, labels %.0f%% identical (%s / %s): a merge "
                    "artifact — these are one person duplicated, not two people. "
                    "Proposed action is a MERGE; the cut edge named here is the "
                    "worse-sourced direction" % (sim * 100, label(persons, a),
                                                 label(persons, b)),
                    "medium")
        return ((None, None), "unresolved",
                "2-node cycle (%s <-> %s) — mutual parenthood is impossible, but "
                "labels are only %.0f%% similar and no date, patronymic or "
                "sourcing signal separates the two directions. Needs a human "
                "reading of the two records." % (label(persons, a),
                                                 label(persons, b), sim * 100),
                "unresolved")

    # R5 — uniquely worst-sourced edge, only if the gap is clear
    by_src = sorted(scored, key=lambda s: (s["src"], s["edge"]))
    if len(by_src) > 1 and by_src[0]["src"] + 3 <= by_src[1]["src"]:
        w = by_src[0]
        return (w["edge"], "sourcing_weakest",
                "no date, patronymic or co-parent signal contradicts any edge; this "
                "edge is the only one whose endpoints carry no external identifier "
                "(sourcing score %d vs next-worst %d)" % (w["src"], by_src[1]["src"]),
                "low")

    return ((None, None), "unresolved",
            "no evidence separates the %d edges in this cycle: none contradicted by "
            "dates, none reversed by patronymic, and sourcing is even across the "
            "chain. Cutting any edge here would be a guess." % len(edges),
            "unresolved")


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------

def count_back_edges(edges):
    _, back = build_dag(edges)
    return len(back)


def main():
    persons = load_persons()
    edges = load_edges()
    spouses = load_spouses()
    cycles = load_cycles()

    parents_of = defaultdict(list)
    children_of = defaultdict(list)
    for p, c in edges:
        parents_of[c].append(p)
        children_of[p].append(c)

    edge_freq = defaultdict(int)
    cycle_edges = set()
    cycle_nodes = set()
    for cy in cycles:
        for e in cy["edges"]:
            edge_freq[e] += 1
            cycle_edges.add(e)
        cycle_nodes.update(cy["nodes"])

    sys.stderr.write("inferring birth-year bounds for %d cycle nodes from dated "
                     "relatives within %d generations...\n" % (len(cycle_nodes), MAX_HOPS))
    lo, hi = bounded_bounds(cycle_nodes, persons, parents_of, children_of, cycle_edges)
    sys.stderr.write("  bounded: %d lower, %d upper\n" % (len(lo), len(hi)))

    rows = []
    cuts = set()
    for cy in cycles:
        (cp, cc), kind, detail, conf = choose_cut(
            cy, persons, lo, hi, spouses, parents_of, edge_freq)
        if cp:
            cuts.add((cp, cc))
        freq = edge_freq.get((cp, cc), 0) if cp else 0
        reason = detail
        if cp and freq > 1:
            reason += " [this edge appears in %d of the %d listed cycles]" % (freq, len(cycles))
        rows.append({
            "cycle_len": cy["cycle_len"],
            "chain_qids": cy["chain_qids"],
            "cut_parent": "%s (%s)" % (cp, label(persons, cp)) if cp else "",
            "cut_child": "%s (%s)" % (cc, label(persons, cc)) if cc else "",
            "reason": "%s: %s" % (kind, reason),
            "confidence": conf,
        })

    out = ANALYSIS / "qa_cycles_proposed.tsv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n",
                           fieldnames=["cycle_len", "chain_qids", "cut_parent",
                                       "cut_child", "reason", "confidence"])
        w.writeheader()
        w.writerows(rows)

    # Verification. Applies the proposals to an in-memory copy of the graph only —
    # nothing is written back to the dump.
    resolved = sum(1 for r in rows if r["confidence"] != "unresolved")
    broken = sum(1 for cy in cycles if any(e in cuts for e in cy["edges"]))
    still_intact = [cy for cy in cycles if not any(e in cuts for e in cy["edges"])]
    remaining_edges = [e for e in edges if e not in cuts]
    sys.stderr.write("verifying: re-running cycle detection with proposals applied...\n")
    before = count_back_edges(edges)
    after = count_back_edges(remaining_edges)

    from collections import Counter
    conf_counts = Counter(r["confidence"] for r in rows)
    kind_counts = Counter(r["reason"].split(":")[0] for r in rows)

    print("wrote %s" % out)
    print("cycles listed:            %d" % len(cycles))
    print("rows with a proposed cut: %d   left unresolved: %d"
          % (resolved, len(cycles) - resolved))
    print("distinct edges proposed:  %d  (cuts are shared: one edge can sit on "
          "several cycles)" % len(cuts))
    print("cycles broken by the cut set: %d  still intact: %d"
          % (broken, len(still_intact)))
    print("back edges in the whole graph: %d -> %d  (DFS-order dependent, an "
          "indicator not a cycle count)" % (before, after))
    print("confidence: %s" % dict(conf_counts))
    print("rule:       %s" % dict(kind_counts))
    if resolved and broken < resolved:
        print("WARNING: fewer cycles broken than cuts proposed — a proposed cut is "
              "not on its own cycle")


if __name__ == "__main__":
    main()
