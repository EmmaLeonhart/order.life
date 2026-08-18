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

import csv
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
    # 2026-08-05. queue.md item 0c -- the severed Japanese imperial line. Emma ruled
    # "create Ojin and reconnect" when asked.
    #
    # THE BREAK. The dump already holds an unbroken chain from Jimmu down eleven
    # generations: Q6432 Jimmu -> Q6456 Suizei -> Q6481 Annei -> Q6538 Itoku ->
    # Q153775 Kosho -> Q153778 Koan -> Q153777 Korei -> Q153776 Kogen -> Q6742 Kaika ->
    # Q6792 Sujin -> Q6832 Suinin. Then it stops, and three later records sit fatherless
    # because the four men who should be their fathers are simply ABSENT from the dump:
    #
    #   Q6804 Yamato Takeru      has ONLY a mother (Q6748)   -- his father is Keiko
    #   Q6950 Nintoku            has ONLY a mother (Q6945)   -- his father is Ojin
    #   Q7038 Ichinobe-no Oshiwa has NO parents at all       -- his father is Richu
    #
    # So Ojin was never "lost"; he was never entered. Same for Keiko, Chuai and Richu.
    # Checked by wikidata id against persons.tsv: wd Q329723 Keiko, Q179971 Chuai,
    # Q317997 Ojin and Q329704 Richu are all absent, while every other emperor in the
    # succession is present.
    #
    # STANDARD KOJIKI / NIHON SHOKI SUCCESSION, verified live on Wikidata 2026-08-05 by
    # walking P22 upward from Richu and landing exactly on Jimmu:
    #   Richu Q329704 <- Nintoku Q313119 <- Ojin Q317997 <- Chuai Q179971 <-
    #   Yamato Takeru Q461258 <- Keiko Q329723 <- Suinin Q314850 <- ... <- Jimmu Q200188
    # (dump Q6432 Jimmu carries wd Q200188, confirmed.) Nothing here is invented.
    #
    # WHAT IT IS WORTH. Q7038 Ichinobe-no Oshiwa has **1,282 descendants**, and that is
    # the whole floating Kanmu block -- Kanmu is among them, Jimmu is not. Wiring Ichinobe
    # up to Richu therefore hands all 1,282 the Wu-Taibo descent that Jimmu's line already
    # carries: -> Ji Yangchang King of Yayoi -> the Kings of Wu -> Zhou -> the Yellow
    # Emperor -> Adam -> Q1 Aster. Combined with the junda-yamato-fuhito bridge above,
    # Kanmu then holds BOTH ancestries at once -- Chinese paternally, Korean through his
    # mother -- which is the cross-cutting design (CLAUDE.md).
    #
    # CANNOT CREATE A CYCLE, checked before writing rather than after: none of Suinin,
    # Yamato Takeru, Nintoku or Jimmu is among Ichinobe's 1,282 descendants. Kanmu is,
    # correctly.
    #
    # Every link is father->son, so writing P47 only costs nothing. The mothers Q6748 and
    # Q6945 already sit on their sons and are untouched.
    "ojin-imperial-reconnection": {
        "create": [
            {
                "qid": "Q200010",
                "label": "Keikō",
                "aliases": ["Emperor Keiko", "Otarashihiko-oshirowake"],
                "note": "created 2026-08-05 for queue.md item 0c; wd Q329723, son of "
                        "Suinin and father of Yamato Takeru",
            },
            {
                "qid": "Q200011",
                "label": "Chūai",
                "aliases": ["Emperor Chuai", "Tarashinakatsuhiko"],
                "note": "created 2026-08-05 for queue.md item 0c; wd Q179971, son of "
                        "Yamato Takeru and father of Ojin",
            },
            {
                "qid": "Q200012",
                "label": "Ōjin",
                "aliases": ["Emperor Ojin", "Homutawake", "Hachiman"],
                "note": "created 2026-08-05 for queue.md item 0c; wd Q317997, son of "
                        "Chuai and father of Nintoku -- the emperor Emma named, absent "
                        "from the dump entirely until now",
            },
            {
                "qid": "Q200013",
                "label": "Richū",
                "aliases": ["Emperor Richu", "Izahowake"],
                "note": "created 2026-08-05 for queue.md item 0c; wd Q329704, son of "
                        "Nintoku and father of Ichinobe-no Oshiwa",
            },
        ],
        "edges": [
            ("Q6832", "Q200010", "wd Q329723 Keiko's father is Q314850 Suinin"),
            ("Q200010", "Q6804", "wd Q461258 Yamato Takeru's father is Q329723 Keiko; the "
                                 "dump had only his mother Q6748"),
            ("Q6804", "Q200011", "wd Q179971 Chuai's father is Q461258 Yamato Takeru"),
            ("Q200011", "Q200012", "wd Q317997 Ojin's father is Q179971 Chuai"),
            ("Q200012", "Q6950", "wd Q313119 Nintoku's father is Q317997 Ojin; the dump "
                                 "had only his mother Q6945"),
            ("Q6950", "Q200013", "wd Q329704 Richu's father is Q313119 Nintoku"),
            ("Q200013", "Q7038", "wd Q2297842 Ichinobe-no Oshiwa's father is Q329704 "
                                 "Richu; this is the join that reconnects the whole "
                                 "1,282-record Kanmu block to Jimmu"),
        ],
    },
    # 2026-08-06. queue.md item 0, PART B -- the mix itself. One woman, two edges, and it
    # is the join the whole Korean/Japanese half of item 0 was built toward.
    #
    # WHAT EMMA ASKED FOR, 2026-08-05: "My plan was that the Korean lines mixed at some
    # point earlier before Kammu's descent," and "Japan ought to have two ancestries."
    # Part A (junda-yamato-fuhito) opened the channel -- Kanmu now descends from Muryeong
    # of Baekje through his mother Takano no Niigasa. This adds the SECOND Korean house:
    # Q9935 Prince Junda has a father (Q10437 Muryeong) and NO MOTHER. Give him a Gaya
    # mother descended from Heo Hwang-ok and Kanmu inherits Baekje and Gaya at once.
    #
    # THE CHRONOLOGY PICKS THE RECORD. Junda is b. +0480 (corrected 2026-08-06 from a
    # century-precision import artifact) and d. 513, so his mother is born around 460.
    # Q15720 Jilji of Geumgwan Gaya d. 492 is exactly that generation and IS a descendant
    # of Q51928 Heo Hwang-ok -- verified by walking edges.tsv, she is among Heo Hwang-ok's
    # 46. Her father Q16457 Chwihui d. 451 and her son Q15253 Gyeomji reads b. 401 d. 521,
    # a 120-year life, which is why Jilji is preferred over Gyeomji as queue.md says.
    #
    # THE NAME IS INVENTED AND EMMA AUTHORISED IT, 2026-08-06: "just make one please no
    # need for a specific name. as long as it comes off as korean at the time." Modeok
    # (모덕) follows the attested register of Geumgwan Gaya queens in the Samguk Yusa --
    # Mojeong, Hogu, Aji, Jeongsin, Boksu, Indeok, Bangwon, Gyehwa -- two syllables,
    # hanja-legible, and not colliding with any of them. She is a Gaiad construction, not
    # an attested person; there is no Wikidata id and there should not be one.
    #
    # NO DATES, DELIBERATELY. ~460 is what the surrounding records imply, not what any
    # source states, and writing it at year precision would be the exact mistake that put
    # Junda's birth at 450 -- an inferred number wearing the costume of an attested one.
    # The reasoning is recorded here and in the devlog, where it can be read.
    #
    # CANNOT CREATE A CYCLE, checked before writing: Q15720 is not among Q9935's 1,221
    # descendants, and neither is any other Gaya record. The two sets are disjoint.
    "junda-gaya-mother": {
        "create": [
            {
                "qid": "Q200014",
                "label": "Modeok of Geumgwan Gaya",
                "aliases": ["Modeok", "Lady Modeok"],
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153719"]},
                "note": "created 2026-08-06 for queue.md item 0 part B; an INVENTED "
                        "daughter of Q15720 Jilji of Geumgwan Gaya, authorised by Emma "
                        "2026-08-06, married to Muryeong of Baekje and mother of Prince "
                        "Junda -- the node where the Gaya line of Heo Hwang-ok mixes into "
                        "the Baekje line that Kanmu inherits. No wikidata id: she is not "
                        "an attested person",
            },
        ],
        "edges": [
            ("Q15720", "Q200014", "P47", "Modeok is a daughter of Jilji of Geumgwan Gaya "
                                         "(d. 492), the Gaya king of the right generation "
                                         "and a descendant of Q51928 Heo Hwang-ok"),
            ("Q200014", "Q9935", "P48", "Junda (b. 480, d. 513) had a father and no mother; "
                                        "this is the Gaya mother that gives Kanmu his "
                                        "second Korean ancestry"),
        ],
        "spouses": [
            ("Q200014", "Q10437", "Modeok is the wife of Muryeong of Baekje, which is what "
                                  "makes her Junda's mother rather than a bare edge"),
        ],
    },
    # 2026-08-06. queue.md item 0, THE HEADLINE -- the Indian line reaching living Koreans.
    # Emma, 2026-08-06: "connect Heo Hwang-ok into the line with generated minor noble
    # lineage connecting with our established people up to Rama ... like Rama's known
    # descendants at one point continue the generations to Heo Hwang-ok."
    #
    # THE STORY THE LINE TELLS, which is the only thing that makes it a result:
    #
    #   Aster -> Adam -> ... -> Ikshvaku -> Rama of Ayodhya -> Kusha -> the Kosala kings
    #   -> the Magadha kings -> the Mauryas -> the Shungas -> GHOSHA (Shunga VII, r. 119
    #   BCE) -> a cadet branch that stays in Kosala and rules from Ayodhya -> HEO HWANG-OK,
    #   princess of Ayuta -> Suro of Geumgwan Gaya -> the Gaya and Silla kings -> the Kim
    #   and Heo clans of Gimhae -> living Koreans; and through Q200014 Modeok -> Prince
    #   Junda -> the Yamato no Fuhito -> Takano no Niigasa -> Emperor Kanmu -> Japan.
    #
    # Every record above Ghosha already exists and is already connected. Ghosha has 1,408
    # ancestors and reaches Rama, Ikshvaku and Q1 Aster -- verified from edges.tsv, not
    # assumed. The whole gap is the five records below.
    #
    # THE FIVE ARE NOT INVENTED FROM NOTHING, and this is the part worth knowing. Heo
    # Hwang-ok's own tradition (Samguk Yusa) makes her a princess of **Ayuta**, the name
    # Korean tradition identifies with **Ayodhya** -- that identification is the entire
    # basis of the Gimhae Kim and Heo clans' claimed Indian origin. And Ayodhya really did
    # have a dynasty in exactly her century: P. L. Gupta counts **fifteen kings ruling from
    # Ayodhya between 130 BCE and 158 CE** whose coins survive, ten of them named --
    # Muladeva, Vayudeva, Vishakhadeva, Dhanadeva, Ajavarman, Sanghamitra, Vijayamitra,
    # Satyamitra, Devamitra, Aryamitra. Heo Hwang-ok's birth in 33 CE falls inside that
    # window. So the NAMES are attested and the FILIATIONS are the Gaiad's construction:
    # the coins give a king list, never a genealogy, so chaining them father-to-son
    # contradicts no source. Nothing here overwrites an attested parentage.
    #
    # WHY GHOSHA IS THE ATTACHMENT POINT. The Ayodhya Inscription of Dhana calls its king
    # "Dhana(deva), Lord of Kosala, son of Kausiki, **the sixth of the Senapati
    # Pushyamitra**, who had performed the Ashvamedha twice". Counting six down the dump's
    # own Shunga chain from the Pushyamitra slot -- Q2181 -> Q2175 Agnimitra -> Q2165
    # Vasumitra -> Q2150 Bhadraka -> Q2134 Pulindaka -> Q2117 Ghosha -> [sixth] -- lands
    # exactly on a son of Ghosha. So the inscription picks the attachment point for us, and
    # the literal "sixth" reading dates Dhana to the early 1st century BCE, which is where
    # a son of Ghosha (r. 119 BCE) sits. It is a cadet branch: the Shunga main line runs on
    # to Bhagabhadra and Devabhuti and is untouched.
    #
    # STATED PLAINLY RATHER THAN GLOSSED: the dump's Shunga chain is a chain of REIGNS
    # recorded as father-to-son, so its nine "generations" cover 185-73 BCE at about twelve
    # years each, which is not how generations work. The count above is therefore a count
    # of dump records, not of biological generations, and it agrees with the inscription
    # only because both are counting successions. D. C. Sircar's palaeographic dating puts
    # Dhana in the 1st century CE instead, which would make him a descendant rather than
    # the sixth in line. Either reading leaves him a Shunga-descended king of Kosala; the
    # earlier one is used here because it is the one the dump's own structure supports.
    #
    # WHICH COPY. The Maurya/Shunga block is imported THREE times -- Q2xxx, Q50xxx and
    # Q160xxx are the same men (queue.md item 0 records two of the three; the Q50xxx copy
    # is a third and is now logged). This attaches to the **Q2xxx** copy, which is the one
    # carrying Wikidata ids and dates (Q2175 = wd Q24395, Q2074 = wd Q3878846), i.e. the
    # copy queue.md already names as the survivor when the dedupe happens. The edge
    # therefore survives that dedupe instead of being redone after it.
    #
    # NO P56/P57 DATES, DELIBERATELY. Every generation here is BCE, and this dump stores
    # BCE with a POSITIVE sign (queue.md item 0b: 11,833 records carry one positive date
    # and are invisible to the death<birth detector). Writing "+0110" for 110 BCE would add
    # five more records to that pile and read as 110 CE to every numeric comparison in the
    # toolchain. The chronology goes in the item descriptions, where it is readable and
    # cannot be silently mis-compared.
    #
    # CANNOT CREATE A CYCLE, checked before writing: Heo Hwang-ok's descendant set is 1,269
    # records (the Gaya/Kim block plus, since Modeok, the whole Kanmu block) and contains
    # no Indian record at all -- not Ghosha, not Devabhuti, not Rama.
    # queue.md item 0c (2026-08-18). The Haji clan is in the dump TWICE, as two fragments
    # that do not touch, and one missing generation is the whole break:
    #
    #   fragment A   Q14866 Haji no Otori (NO father) -> Q14463 Haji no Kuiko
    #   fragment B   Q19453 Nomi no Sukune -> Q17793 Adakatsu -> Q16508 Iwabi ->
    #                Q15732 Haji no Mukuro (NO child)
    #
    # Wikidata puts exactly one man between them: Q97613635 "Haji no Osoba"
    # (土師意富祖婆), whose father is Q97613639 = Q15732 Mukuro and whose child is
    # Q97613634 = Q14866 Otori. Both dump records already carry the matching P61, so the
    # identification is the dump's own, not a label match. This invents nobody -- it
    # imports one attested record that the original import skipped.
    #
    # THE STORY, which is the part that matters: the Haji (土師氏) are the clan of Nomi no
    # Sukune, who is descended from Ame no Hohi (Q6615, in the dump), the son Amaterasu and
    # Susanoo produced in the ukehi -- the standard Izumo descent. Closing this gap puts
    # Kuiko and Otori back on that line as far as Nomi no Sukune.
    #
    # Cannot close a cycle: checked against edges.tsv -- Q14866 has no ancestors at all,
    # and Q15732's ancestors are Iwabi, Adakatsu and Nomi no Sukune, none of which is a
    # descendant of Q14866.
    #
    # NOT DONE HERE, and it is the rest of item 0c: Nomi no Sukune (Q19453) is himself
    # rootless, and eleven attested Izumo records stand between him and Q6715
    # Takehiratori. Q7915 Haji no Hodo is rootless for the same reason -- his father
    # Q136929945 and three more above him are absent. Five of those sixteen records have
    # NO English label on Wikidata (土師土徳, 土師兎, 土師首, 可美乾飯根命, 伊佐我命) and
    # naming them is Emma's call, not research; see queue.md.
    "haji-osoba": {
        "create": [
            {
                "qid": "Q200022",
                "label": "Haji no Ōsoba",
                "aliases": ["Haji no Osoba", "Haji no Oosoba", "土師意富祖婆"],
                "desc": "Haji clan, son of Haji no Mukuro and father of Haji no Otori",
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153718"]},
                "note": "created 2026-08-18 for queue.md item 0c; wd Q97613635, the "
                        "generation missing between Q15732 Mukuro (childless here) and "
                        "Q14866 Otori (fatherless here). This tool cannot write P61, so "
                        "the record does not carry wd Q97613635",
            },
        ],
        "edges": [
            ("Q15732", "Q200022", "wd Q97613635's father is wd Q97613639, which is Q15732 "
                                  "by its own P61 -- and Q15732 had no child recorded"),
            ("Q200022", "Q14866", "wd Q97613635's child is wd Q97613634, which is Q14866 "
                                  "by its own P61 -- and Q14866 had no father recorded"),
        ],
    },
    "heo-hwang-ok-ayodhya": {
        "create": [
            {
                "qid": "Q200015",
                "label": "Dhanadeva, Lord of Kosala",
                "aliases": ["Dhanadeva", "Dhana", "Dhanadeva of Ayodhya"],
                "desc": "king of Ayodhya, c. 110-55 BCE; the Ayodhya inscription's "
                        "'sixth of the Senapati Pushyamitra', who performed the "
                        "Ashvamedha twice",
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153718"]},
                "note": "created 2026-08-06 for queue.md item 0; attested by coins and by "
                        "the Ayodhya Inscription of Dhana, wd Q48724349 (the inscription, "
                        "not the man -- he has no Wikidata item). Cadet Shunga branch "
                        "ruling Kosala from Ayodhya",
            },
            {
                "qid": "Q200016",
                "label": "Ajavarman of Ayodhya",
                "aliases": ["Ajavarman"],
                "desc": "king of Ayodhya, c. 85-30 BCE",
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153718"]},
                "note": "created 2026-08-06 for queue.md item 0; name attested on Ayodhya "
                        "coinage (P. L. Gupta's fifteen kings, 130 BCE - 158 CE); the "
                        "filiation is the Gaiad's",
            },
            {
                "qid": "Q200017",
                "label": "Sanghamitra of Ayodhya",
                "aliases": ["Sanghamitra", "Samghamitra"],
                "desc": "king of Ayodhya, c. 60-5 BCE",
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153718"]},
                "note": "created 2026-08-06 for queue.md item 0; name attested on Ayodhya "
                        "coinage. NOT Ashoka's daughter Sanghamitta -- the Ayodhya coin "
                        "king of this name is a different, male figure two centuries later",
            },
            {
                "qid": "Q200018",
                "label": "Vijayamitra of Ayodhya",
                "aliases": ["Vijayamitra"],
                "desc": "king of Ayodhya, c. 35 BCE - 20 CE",
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153718"]},
                "note": "created 2026-08-06 for queue.md item 0; name attested on Ayodhya "
                        "coinage; the filiation is the Gaiad's",
            },
            {
                "qid": "Q200019",
                "label": "Satyamitra of Ayodhya",
                "aliases": ["Satyamitra"],
                "desc": "king of Ayodhya, c. 5 BCE - 50 CE; father of Heo Hwang-ok, "
                        "princess of Ayuta",
                "props": {"P39": ["Q153801", "Q153802"], "P55": ["Q153718"]},
                "note": "created 2026-08-06 for queue.md item 0; name attested on Ayodhya "
                        "coinage. He is the joint itself -- the last Indian generation "
                        "before the voyage to Gaya in c. 48 CE",
            },
        ],
        "edges": [
            ("Q2117", "Q200015", "P47", "the Ayodhya inscription makes Dhana 'the sixth of "
                                        "the Senapati Pushyamitra'; six down the dump's "
                                        "own Shunga chain from the Pushyamitra slot Q2181 "
                                        "is a son of Q2117 Ghosha"),
            ("Q200015", "Q200016", "P47", "Ayodhya king list order, P. L. Gupta"),
            ("Q200016", "Q200017", "P47", "Ayodhya king list order, P. L. Gupta"),
            ("Q200017", "Q200018", "P47", "Ayodhya king list order, P. L. Gupta"),
            ("Q200018", "Q200019", "P47", "Ayodhya king list order, P. L. Gupta"),
            ("Q200019", "Q51928", "P47", "Heo Hwang-ok is a princess of Ayuta = Ayodhya in "
                                         "the Samguk Yusa; this is the joint that carries "
                                         "the Vedic and epic material into Korea and Japan"),
        ],
    },
}

FATHER, MOTHER, CHILD, SPOUSE = "P47", "P48", "P20", "P42"


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


_ALIASES = None


def resolve(qid):
    """Map a qid through redirects.tsv, the way extract_genealogy.py does.

    Added 2026-08-15. Without this, an edge already present under a merged-away qid reads
    as "new" and gets written a second time: graph-neutral, because the extractor resolves
    both spellings to the same edge, but it leaves the record claiming a vacated qid --
    which is the residue queue.md item 1c is about, and the merge rule forbids.

    The sharper version of the same bug cost eight days on apply_lepidus_cut.py, which
    compared raw qids to DROP an edge, matched nothing, and then confirmed its own no-op
    with a verify block written from the same premise. This tool is additive so it cannot
    fail that way -- but it can still be wrong about what is already there.
    """
    global _ALIASES
    if _ALIASES is None:
        _ALIASES = {}
        path = ANALYSIS / "redirects.tsv"
        if path.exists():
            with path.open(encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                    _ALIASES[r["from_qid"]] = r["to_qid"]
    seen = set()
    while qid in _ALIASES and qid not in seen:
        seen.add(qid)
        qid = _ALIASES[qid]
    return qid


def claim_ids(d, pid):
    """Claim targets as the graph sees them -- resolved, so an alias cannot read as absent."""
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(resolve(v["id"]))
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


def edges_of(spec):
    """Normalise both edge shapes to (parent, child, role, why).

    The original bridges wrote father-son chains only and are 3-tuples; the role slot was
    added 2026-08-06 for the Gaya mother, where the downward claim on the child must be
    P48 and not P47. Writing P47 there would record a woman as her son's father, which
    extract_genealogy.py would happily turn into a correct-looking edge.
    """
    for e in spec["edges"]:
        if len(e) == 4:
            yield e
        else:
            parent, child, why = e
            yield parent, child, FATHER, why


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
    for parent, child, _role, _why in edges_of(spec):
        for q in (parent, child):
            if load(q) is None and not any(r["qid"] == q for r in spec["create"]):
                problems.append(f"{q} does not exist and is not being created")
    for a, b, _why in spec.get("spouses", []):
        for q in (a, b):
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
    for parent, child, role, why in edges_of(spec):
        pd, cd = load(parent), load(child)
        # Resolve both sides: claim_ids returns resolved targets, so a raw probe qid that
        # is itself an alias would compare unequal against its own canonical form.
        have_down = pd is not None and resolve(child) in claim_ids(pd, CHILD)
        have_up = cd is not None and resolve(parent) in claim_ids(cd, role)
        state = ("already both directions" if (have_down and have_up)
                 else "parent side only" if have_down
                 else "child side only" if have_up else "new")
        kind = "father" if role == FATHER else "mother"
        print(f"  EDGE   {parent} -> {child}   ({kind}, {state})")
        print(f"         {why}")
    for a, b, why in spec.get("spouses", []):
        ad, bd = load(a), load(b)
        have = (ad is not None and resolve(b) in claim_ids(ad, SPOUSE)
                and bd is not None and resolve(a) in claim_ids(bd, SPOUSE))
        print(f"  SPOUSE {a} <-> {b}   ({'already both directions' if have else 'new'})")
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
            "descriptions": ({"en": {"language": "en", "value": rec["desc"]}}
                             if rec.get("desc") else {}),
            "claims": {},
        }
        # Non-genealogical item claims the surrounding records all carry -- P39 Person /
        # Gaiad character, P55 Male or Female. The six records created 2026-08-05 got none
        # of these and read as bare nodes next to their neighbours.
        for pid, targets in (rec.get("props") or {}).items():
            d["claims"][pid] = [make_claim(pid, t) for t in targets]
        save(rec["qid"], d)
        print(f"  created {rec['qid']}")

    touched = set()
    for parent, child, role, _why in edges_of(spec):
        pd = load(parent)
        if resolve(child) not in claim_ids(pd, CHILD):
            pd.setdefault("claims", {}).setdefault(CHILD, []).append(
                make_claim(CHILD, child))
            save(parent, pd)
        cd = load(child)
        if resolve(parent) not in claim_ids(cd, role):
            cd.setdefault("claims", {}).setdefault(role, []).append(
                make_claim(role, parent))
            save(child, cd)
        touched.update((parent, child))
        print(f"  declared {parent} -> {child} on both sides ({role} + {CHILD})")

    for a, b, _why in spec.get("spouses", []):
        for x, y in ((a, b), (b, a)):
            xd = load(x)
            if resolve(y) not in claim_ids(xd, SPOUSE):
                xd.setdefault("claims", {}).setdefault(SPOUSE, []).append(
                    make_claim(SPOUSE, y))
                save(x, xd)
        touched.update((a, b))
        print(f"  declared {a} <-> {b} spouse on both sides")

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
    for parent, child, role, _why in edges_of(spec):
        pd, cd = load(parent), load(child)
        down = resolve(child) in claim_ids(pd, CHILD)
        up = resolve(parent) in claim_ids(cd, role)
        if not (down and up):
            print(f"  FAIL {parent} -> {child}: parent-side={down} child-side={up}")
            ok = False
    for a, b, _why in spec.get("spouses", []):
        if (resolve(a) not in claim_ids(load(b), SPOUSE)
                or resolve(b) not in claim_ids(load(a), SPOUSE)):
            print(f"  FAIL spouse {a} <-> {b} is one-sided")
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
