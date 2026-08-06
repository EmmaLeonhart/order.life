"""Add the lineage-bridge edges from planning/lineage_bridges_proposed.md.

    python wiki-scripts/add_bridge_edges.py adam-genghis           # dry run
    python wiki-scripts/add_bridge_edges.py adam-genghis --write   # apply

Data-driven and shadow-aware, like merge_cluster.py. Everything it does is additive:
it creates records that do not exist and appends parent/child claims. It never removes a
claim, so `git checkout -- wikibase/items` reverts it completely.

WHY A SCRIPT AND NOT A HAND EDIT

An edge lives in TWO places -- the child's P47/P48 and the parent's P20 -- and
extract_genealogy.py builds edges.tsv from the union, so a half-declared edge still reads
as real while any one-sided repair silently fails. That is what made the Tros fix look
done while two cycles were still closed. This writes both directions and asserts both
afterwards.

And a record's claims must be propagated to every file claiming its qid, or the edit
reverts the moment that file stops being the numerically-lowest claimant. None of the
records touched by the adam-genghis bridge currently has a shadow, but that is a fact
about today's dump and not a property to rely on, so the propagation runs regardless.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
ANALYSIS = ROOT / "wikibase" / "analysis"

# A bridge is: records to create, then parent -> child edges to declare.
BRIDGES = {
    # planning/lineage_bridges_proposed.md, Bridge A. DECIDED BY EMMA 2026-07-31: "Both?"
    # -- take A1 AND A2, not one or the other. The report anticipated this: "A1 and A2 are
    # not exclusive; A2 could carry the descent and A1 could still be repaired as a
    # separate correctness fix."
    #
    # Khaidu Q53399 is the root of the Borjigin line: 401 descendants including Genghis
    # Khan (Q37401), and ZERO ancestors. Neither edge below can create a cycle -- checked
    # against edges.tsv before writing: neither Q153230 nor Q1164 is a descendant of
    # Khaidu, and both reach Aster Q1.
    "adam-genghis": {
        "create": [
            # A2. Haplogroup C (Q1164) exists, is Adam-descended, and has no children.
            # C2-M217 is a real clade with a real position under C, and is the
            # best-attested fact about Genghis Khan's genetics -- so this invents no
            # person. It mirrors Q54433 "Sinitic O2a2b1a2 (F114)", which sits between the
            # Yellow Emperor's line and Adam in exactly this way.
            {
                "qid": "Q200000",
                "label": "C2 (M217)",
                "aliases": ["Haplogroup C2", "C-M217"],
                "note": "haplogroup bridge node, created 2026-07-31 for Bridge A2",
            },
        ],
        "edges": [
            # A2: Haplogroup C -> C2 (M217) -> Khaidu
            ("Q1164", "Q200000", "A2: C2-M217 is a clade under Haplogroup C"),
            ("Q200000", "Q53399", "A2: Khaidu attaches beneath the C2-M217 node, as "
                                  "Youxiong attaches beneath Q54433"),
            # A1: the Borjigin chain itself. Rashid al-Din's descent is
            # Bodonchar -> Buqa -> Dutum Menen -> Qaidu, which puts Khaidu under Q153230.
            # THE REPORT FLAGS THIS AS A JUDGEMENT CALL AND SO DOES THIS COMMENT: the
            # Secret History has Bodonchar -> Habich Baatar -> Menen Tudun -> Qachi Kulug
            # -> Qaidu, which would attach Khaidu one generation lower, at Q153225. Both
            # placeholders are unlabelled and carry no date and no wikidata_qid, so
            # nothing in the dump distinguishes them. Moving the edge down one node is the
            # whole correction if Emma prefers the Secret History reading.
            ("Q153230", "Q53399", "A1: Rashid al-Din -- Khaidu is the son of Dutum Menen"),
        ],
    },
    # 2026-08-02. Tangle 15 of cycles_review.md, Pedaiah -- an UNMERGE of two biblical
    # figures who share a name. The matching removal is cut_edges.py's "pedaiah-unmerge";
    # run this bridge FIRST.
    #
    # The Hebrew Bible has two Pedaiahs three generations apart, and Wikidata holds them
    # as two items:
    #   Q20101444  Pedaiah **of Rumah** -- 2 Kings 23:36, "his mother's name was Zebidah
    #              the daughter of Pedaiah of Rumah". Its ONLY claim is child Q30527376
    #              Zebudah. **No father, no mother.**
    #   Q116923358 Pedaiah -- described there as "biblical figure in **1 Chronicles 3:18,
    #              father of Zerubbabel**", and listed among Q319049 Jeconiah's children.
    #
    # The dump's Q4617 is both at once, which is exactly why the ring closes:
    #   father  Q135539 Jeconiah      -> the 1 Chronicles man
    #   children Q4626 + Q60222 Zebudah -> the Rumah man
    # and the loop runs Pedaiah -> Zebudah -> Jehoiakim -> Jeconiah -> Pedaiah. Q4617's own
    # alias is "**Pediah of Rumah**" and its wd id is Q20101444, so the record keeps the
    # Rumah identity and the Chronicles one moves out. (Both its children are Zebudah --
    # Q60222 duplicates Q4626, same wd id, same two sons. That duplicate is logged in
    # queue.md; it sits on the same side of the split either way.)
    #
    # Measured before applying: the tangle dissolves and **nothing leaves the graph** --
    # the 510 ancestors Q4617 sheds move to Q200003, the man they belong to. Jehoiakim
    # keeps 499 and his route to Aster through his father Josiah, which is the Davidic line
    # and the one that matters.
    #
    # TWO RECORDS END OFF-ASTER: Q4617 Pedaiah of Rumah and his daughter Q4626 Zebudah.
    # That is the sources' own position rather than a loss -- **Wikidata records no parent
    # of any kind for Q20101444**, and Zebudah is a king's mother by marriage, not a
    # Davidic descendant. This is the test that separates it from the six cases parked on
    # Emma's ruling in queue.md: there, the record left rootless HAS a recorded parent that
    # the dump simply cannot route to Aster; here there is no parent to record.
    #
    # This tool cannot write P61, so Q200003 does not carry wd Q116923358 and Q4617 keeps
    # Q20101444 (correctly, as the Rumah man). Logged with the Deimachus residue.
    "pedaiah-of-chronicles": {
        "create": [
            {
                "qid": "Q200003",
                "label": "Pedaiah",
                "aliases": ["Pedaiah son of Jeconiah", "Pedaiah (1 Chronicles 3:18)"],
                "note": "created 2026-08-02 by the Pedaiah unmerge; wd Q116923358, the son "
                        "of Jeconiah and father of Zerubbabel, split off from Q4617 which "
                        "is wd Q20101444, Pedaiah of Rumah",
            },
        ],
        "edges": [
            ("Q135539", "Q200003", "1 Chronicles 3:17-18 lists Pedaiah among the sons of "
                                   "Jeconiah; Wikidata has Q116923358 among Q319049's "
                                   "children"),
        ],
    },
    # 2026-08-01. Tangle 15 of cycles_review.md, Deimachus -- an UNMERGE, repair-order
    # step 1, and the half of it that ADDS. The matching removals are cut_edges.py's
    # "deimachus-unmerge". Run this bridge FIRST, then that cut.
    #
    # Q75123 carries **two Wikidata ids**, and Wikidata holds them as two separate people:
    #
    #   Q1183222  "Deimachos, **son of Neleus**"   father Q637955 Neleus,
    #                                              mother Q28122362 Chloris, NO children
    #   Q1183226  "Deimachos, **Vater der Enarete**"  child Q48665 Enarete, NO parents
    #
    # One record is playing both, which is exactly why the loop closes. Every other edge in
    # it is genuine Greek myth and none of them should move:
    #   Enarete -> Salmoneus   (Apollodorus 1.7.3: Aeolus married Enarete, daughter of
    #                           Deimachus; Salmoneus is their son)
    #   Salmoneus -> Tyro      Tyro is Salmoneus's daughter
    #   Tyro -> Neleus         Neleus is Tyro's son by Poseidon
    #   Neleus -> Deimachus    Apollodorus 1.9.9 lists Deimachus among Neleus's twelve sons
    # The loop exists because the Deimachus who is Neleus's SON and the Deimachus who is
    # Enarete's FATHER -- separated by four generations -- are one record. Split them and
    # every edge above survives untouched. Nothing is cut but the merge itself.
    #
    # The split is fully determined by the dump's own claims:
    #   son-of-Neleus half   -> father Q131902 Neleus, mother Q133062 Chloris (= wd
    #                           Q28122362, confirmed), no children
    #   father-of-Enarete    -> father Q75162 Cleon, mother Q75165 Idaea, spouse Q75120
    #     half (stays on       Glaucia, children Q132251 Enarete and Q75087 "Enarete,
    #     Q75123)              Aenarete, Enareta, Aegiale" -- which is a second copy of
    #                          Enarete, and sits on the same side of the split either way
    #
    # Measured before applying: **0 records lose their route to Aster** and the tangle
    # dissolves. The 47 ancestors Q75123 sheds are not destroyed -- they move to Q200002,
    # which lands at 190. That is what an unmerge is supposed to look like.
    #
    # TWO THINGS THIS TOOL CANNOT DO, named rather than left to be discovered:
    #   * it writes P47 only, so **Q200002 gets its father Neleus but not its mother
    #     Chloris**. That true claim is unrecorded until something can write P48.
    #   * it cannot write P61, so **Q75123 still carries BOTH wd ids** and Q200002 carries
    #     none. That is the very signal that found this defect, so leaving it is a
    #     re-merge hazard. Both are logged in queue.md.
    "deimachus-son-of-neleus": {
        "create": [
            {
                "qid": "Q200002",
                "label": "Deimachus",
                "aliases": ["Deimachus son of Neleus"],
                "note": "created 2026-08-01 by the Deimachus unmerge; wd Q1183222, the "
                        "son of Neleus, split off from Q75123 which was also holding "
                        "wd Q1183226, the father of Enarete",
            },
        ],
        "edges": [
            ("Q131902", "Q200002", "Apollodorus 1.9.9 lists Deimachus among the twelve "
                                   "sons of Neleus; wd Q1183222's father is wd Q637955"),
        ],
    },
    # 2026-08-01. Tangle 22 of cycles_review.md, the Welsh Cynwrig/Tudur pedigree. This is
    # PURELY ADDITIVE and removes NO loop on its own -- it fills the hole that makes the
    # loop's false edge look load-bearing. The cut itself needs Emma's ruling; see queue.md.
    #
    # THE HOLE. Welsh names are the pedigree, and three of the four edges in that tangle are
    # spelled out by them:
    #   Q148521 "Tudur Fongam **ap Cynwrig Fychan** ap Cynwrig ap Llywarch" -> father Q146349
    #   Q144542 "Morfudd **ferch Tudur Fongam** ap Cynwrig Fychan ap Cynwrig" -> father Q148521
    #   Q146349 "Cynwrig Fychan **ap Cynwrig**" -> father Q143115 "Cynwrig"
    # The fourth, Q144542 -> Q148522, says Morfudd is the mother of Dyddgu. Dyddgu's own
    # name is "Dyddgu **ferch Cadwgan Fottwm** ab Ednyfed ap Cadwgan Ddu", so her father is
    # Cadwgan Fottwm -- and the other three edges make Dyddgu Morfudd's GREAT-GRANDMOTHER.
    # The mother-claim inverts three generations. Wikidata carries the same loop, so it
    # arbitrates nothing here; the names do.
    #
    # In the dump Q148522 Dyddgu has **no father at all**, because Cadwgan Fottwm is not in
    # it -- wd Q112531567, absent. That absence is the whole reason the false edge looks
    # load-bearing: it is her only parent claim.
    #
    # BOTH NEIGHBOURS ARE PRESENT AND THE NAME IS NOT A JUDGEMENT CALL:
    #   wd Q112531567 "Cadwgan Fottwm ab Ednyfed ap Cadwgan Ddu ap Llywarch Gochh"
    #                 father wd Q112531573, child wd Q110636576 Dyddgu
    #   dump Q148767  "Ednyfed ap Cadwgan Ddu ap Llywarch Gochh", **wd Q112531573**, and it
    #                 has NO children recorded
    #   dump Q148522  "Dyddgu ferch Cadwgan Fottwm ...", **wd Q110636576**, no father
    # So the missing generation sits exactly between a childless father and a fatherless
    # daughter, and Wikidata supplies the label verbatim. queue.md's rule for a GAP is to
    # CREATE the record rather than delete its edges; this does that.
    #
    # Cannot close a cycle: checked against edges.tsv before writing -- Q148767 is not a
    # descendant of Q148522. Adding a second parent to Dyddgu while the false mother-claim
    # still stands is harmless; she simply has both until the cut is ruled on.
    #
    # WHAT THIS DOES NOT FIX, stated plainly: Q148767 has 452 ancestors and **does not reach
    # Aster**. So this gives Dyddgu a real 453-deep Welsh line where she had none, but it
    # does NOT preserve the Aster route, which for that cluster runs backwards through
    # Morfudd's mother Gwenllian Fechan. Cutting Q144542 -> Q148522 still costs 18 records
    # their route to Q1. That is the open ruling, not something this bridge resolves.
    "welsh-cadwgan-fottwm": {
        "create": [
            {
                "qid": "Q200001",
                "label": "Cadwgan Fottwm ab Ednyfed ap Cadwgan Ddu ap Llywarch Gochh",
                "aliases": ["Cadwgan Fottwm"],
                "note": "created 2026-08-01; wd Q112531567, the generation missing between "
                        "Q148767 Ednyfed (childless here) and Q148522 Dyddgu (fatherless "
                        "here), named verbatim in Dyddgu's own patronymic",
            },
        ],
        "edges": [
            ("Q148767", "Q200001", "wd Q112531567's father is wd Q112531573, which is "
                                   "Q148767 -- and Q148767 had no children recorded"),
            ("Q200001", "Q148522", "Dyddgu is 'ferch Cadwgan Fottwm'; wd Q112531567 lists "
                                   "wd Q110636576 as its child"),
        ],
    },
    # 2026-08-01. The other half of cut_edges.py's "agathocles-kayanid" cut (b), and it is
    # not optional -- run them as one batch.
    #
    # Cutting the false edge Q29144 -> Q29148 leaves Q29148 Kay Pisan with no parent claim
    # at all, because the false edge was his only one: 341 ancestors to 0, detached from
    # Aster. That is the amputation shape cycle_policy.md is about, and here the source
    # hands back the true edge in the same sentence that refutes the false one:
    #
    #   Bundahishn XXXI.25 -- "By Kavad was Kay Apiveh begotten; by Kay Apiveh were
    #                          Kay Arsh, Kay Vyarsh, Kay Pisan, and Kay Kaus begotten"
    #
    # Kay Apiveh is already in the dump as Q29156, with 335 ancestors reaching Q1 Aster,
    # and already carries three of the four brothers as children. This adds the fourth.
    # It invents nothing and creates no record.
    #
    # Cannot close a cycle: checked against edges.tsv before writing -- Q29156 is not a
    # descendant of Q29148. Measured after: Q29148 lands at 336 ancestors, the five lost
    # against the original 341 being the cycle counting itself.
    "kayanid-pisan": {
        "create": [],
        "edges": [
            ("Q29156", "Q29148", "Bundahishn XXXI.25 -- Kay Pisan is a son of Kay "
                                 "Apiveh, alongside Kay Arsh, Kay Vyarsh and Kay Kaus"),
        ],
    },
    # 2026-08-05. queue.md item 0, GAP A -- the Yamato no Fuhito descent, and the thing
    # that has to exist before ANY of the Korean work means anything.
    #
    # WHAT THIS IS FOR. Emma's plan, 2026-08-05: "My plan was that the Korean lines mixed
    # at some point earlier before Kammu's descent," and "Japan ought to have two
    # ancestries." Both depend on Emperor Kanmu actually inheriting through his mother.
    # Today he does not: Q7508 Kanmu has 23 ancestors and reaches nothing, because
    # Q7687 Yamato no Ototsugu -- his mother's father -- has NO PARENTS in the dump, and
    # Q9935 Prince Junda has NO CHILDREN. The two ends of the line are both present and
    # the middle is missing.
    #
    # THIS IS RESEARCH, NOT INVENTION. Takano no Niigasa's clan, the Yamato no Fuhito,
    # descends from Prince Junda son of King Muryeong of Baekje -- Shoku Nihongi, and the
    # descent Emperor Akihito cited publicly in 2001. Wikidata carries every intervening
    # generation as its own record, checked live 2026-08-05:
    #
    #   Q497878  Muryeong of Baekje      (already dump Q10437)
    #   Q15113421 Prince Junda           (already dump Q9935)   -> child Q26248560
    #   Q26248560 Hoshikimi              father Q15113421
    #   Q26248561 Osoriki no Kimi        father Q26248560
    #   Q26248562 Waunara                father Q26248561
    #   Q26248563 Waguri no Masaru       father Q26248562
    #   Q26248564 Wajosoku               father Q26248563
    #   Q26248566 Wamusuke               father Q26248564       -> child Q26248568
    #   Q26248568 Yamato no Ototsugu     (already dump Q7687)
    #   Q7677188  Takano no Niigasa      (already dump Q7502)
    #   Q314846   Emperor Kanmu          (already dump Q7508)
    #
    # All six middle records are ABSENT from the dump -- checked by wikidata id against
    # persons.tsv, none present. So this creates six people who are attested on Wikidata
    # and wires an unbroken father-to-son chain. Every link is father->son, which is
    # exactly what this tool writes (P47 + P20); no mother claim is needed anywhere in it,
    # so the tool's P48 limitation costs nothing here.
    #
    # CANNOT CREATE A CYCLE. Q9935 Junda's ancestry is the Baekje royal line up to
    # Dongmyeong of Goguryeo and Hae Mo-su of Buyeo -- 25 records, none of them Japanese --
    # and Q7687 Ototsugu currently has no ancestors at all. The two sets are disjoint, so
    # joining them adds no loop. Verify with verify_repair.py regardless.
    #
    # WHAT IT DOES NOT DO. It does not give Japan its Indian ancestry -- that needs the
    # Gaya mother for Junda (item 0, part B, one woman whose NAME IS EMMA'S), and it does
    # not reconnect Kanmu to Jimmu, which is item 0c. It closes the channel those two
    # then flow through.
    "junda-yamato-fuhito": {
        "create": [
            {
                "qid": "Q200004",
                "label": "Hoshikimi",
                "aliases": ["Hoshikimi", "Hoshi no Kimi"],
                "note": "created 2026-08-05 for queue.md item 0 gap A; wd Q26248560, son "
                        "of Prince Junda of Baekje, first Japanese generation of the "
                        "Yamato no Fuhito line",
            },
            {
                "qid": "Q200005",
                "label": "Osoriki no Kimi",
                "aliases": ["Osoriki no Kimi"],
                "note": "created 2026-08-05 for queue.md item 0 gap A; wd Q26248561",
            },
            {
                "qid": "Q200006",
                "label": "Waunara",
                "aliases": ["Waunara"],
                "note": "created 2026-08-05 for queue.md item 0 gap A; wd Q26248562",
            },
            {
                "qid": "Q200007",
                "label": "Waguri no Masaru",
                "aliases": ["Waguri no Masaru"],
                "note": "created 2026-08-05 for queue.md item 0 gap A; wd Q26248563",
            },
            {
                "qid": "Q200008",
                "label": "Wajosoku",
                "aliases": ["Wajosoku"],
                "note": "created 2026-08-05 for queue.md item 0 gap A; wd Q26248564",
            },
            {
                "qid": "Q200009",
                "label": "Wamusuke",
                "aliases": ["Wamusuke"],
                "note": "created 2026-08-05 for queue.md item 0 gap A; wd Q26248566, "
                        "father of Yamato no Ototsugu",
            },
        ],
        "edges": [
            ("Q9935", "Q200004", "Shoku Nihongi: the Yamato no Fuhito descend from Prince "
                                 "Junda; wd Q15113421's only recorded child is Q26248560"),
            ("Q200004", "Q200005", "wd Q26248561's father is Q26248560"),
            ("Q200005", "Q200006", "wd Q26248562's father is Q26248561"),
            ("Q200006", "Q200007", "wd Q26248563's father is Q26248562"),
            ("Q200007", "Q200008", "wd Q26248564's father is Q26248563"),
            ("Q200008", "Q200009", "wd Q26248566's father is Q26248564"),
            ("Q200009", "Q7687", "wd Q26248568 Yamato no Ototsugu's father is Q26248566; "
                                 "this is the join that lets Kanmu inherit through his "
                                 "mother Takano no Niigasa"),
        ],
    },
}

FATHER, CHILD = "P47", "P20"


def load(qid):
    p = ITEMS / f"{qid}.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return d if isinstance(d, dict) else None


def save(qid, data):
    (ITEMS / f"{qid}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def claim_ids(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def make_claim(pid, target):
    num = int(target[1:]) if target[1:].isdigit() else None
    value = {"entity-type": "item", "id": target}
    if num is not None:
        value["numeric-id"] = num
    return {
        "mainsnak": {
            "snaktype": "value",
            "property": pid,
            "datavalue": {"value": value, "type": "wikibase-entityid"},
        },
        "type": "statement",
        "rank": "normal",
    }


def shadows_of(qid):
    """Every file whose internal id is qid but whose filename is not."""
    out = []
    path = ANALYSIS / "redirects.tsv"
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            i_from, i_to = header.index("from_qid"), header.index("to_qid")
        except ValueError:
            return out
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > max(i_from, i_to) and parts[i_to] == qid:
                out.append(parts[i_from])
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv[1:]
    if not args or args[0] not in BRIDGES:
        print(__doc__)
        print("bridges: " + ", ".join(sorted(BRIDGES)))
        return 1
    name = args[0]
    spec = BRIDGES[name]

    print(f"bridge {name!r}\n")

    problems = []
    for rec in spec["create"]:
        if load(rec["qid"]) is not None:
            problems.append(f"{rec['qid']} already exists -- refusing to overwrite it")
    for parent, child, _why in spec["edges"]:
        for q in (parent, child):
            if load(q) is None and not any(r["qid"] == q for r in spec["create"]):
                problems.append(f"{q} does not exist and is not being created")
    if problems:
        print("ABORT -- preconditions failed:")
        for p in problems:
            print("  " + p)
        return 1

    for rec in spec["create"]:
        print(f"  CREATE {rec['qid']}  {rec['label']!r}")
        print(f"         {rec['note']}")
    for parent, child, why in spec["edges"]:
        pd, cd = load(parent), load(child)
        have_down = pd is not None and child in claim_ids(pd, CHILD)
        have_up = cd is not None and parent in claim_ids(cd, FATHER)
        state = ("already both directions" if (have_down and have_up)
                 else "parent side only" if have_down
                 else "child side only" if have_up else "new")
        print(f"  EDGE   {parent} -> {child}   ({state})")
        print(f"         {why}")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    for rec in spec["create"]:
        d = {
            "type": "item",
            "id": rec["qid"],
            "labels": {"en": {"language": "en", "value": rec["label"]}},
            "aliases": {"en": [{"language": "en", "value": a}
                               for a in rec.get("aliases", [])]},
            "descriptions": {},
            "claims": {},
        }
        save(rec["qid"], d)
        print(f"  created {rec['qid']}")

    touched = set()
    for parent, child, _why in spec["edges"]:
        pd = load(parent)
        if child not in claim_ids(pd, CHILD):
            pd.setdefault("claims", {}).setdefault(CHILD, []).append(
                make_claim(CHILD, child))
            save(parent, pd)
        cd = load(child)
        if parent not in claim_ids(cd, FATHER):
            cd.setdefault("claims", {}).setdefault(FATHER, []).append(
                make_claim(FATHER, parent))
            save(child, cd)
        touched.update((parent, child))
        print(f"  declared {parent} -> {child} on both sides")

    # Propagate to every file claiming a touched qid. None of these records has a shadow
    # today; that is a fact about the current dump, not a guarantee, so this runs anyway.
    n = 0
    for q in sorted(touched):
        final = load(q)
        for s in shadows_of(q):
            if (ITEMS / f"{s}.json").exists():
                save(s, final)
                n += 1
    print(f"  propagated to {n} shadow file(s)")

    print("\nverifying, from the files rather than from the plan...")
    ok = True
    for parent, child, _why in spec["edges"]:
        pd, cd = load(parent), load(child)
        down = child in claim_ids(pd, CHILD)
        up = parent in claim_ids(cd, FATHER)
        if not (down and up):
            print(f"  FAIL {parent} -> {child}: parent-side={down} child-side={up}")
            ok = False
    for q in sorted(touched):
        final = load(q)
        for s in shadows_of(q):
            if (ITEMS / f"{s}.json").exists() and load(s) != final:
                print(f"  FAIL shadow {s} disagrees with {q}")
                ok = False
    if ok:
        print("  every edge is declared on BOTH sides; all shadows agree")
    print("\nNow run: python wiki-scripts/verify_repair.py")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
