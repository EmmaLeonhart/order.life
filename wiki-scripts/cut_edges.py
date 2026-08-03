"""Remove specific parent -> child edges, from both sides and every shadow file.

    python wiki-scripts/cut_edges.py scipio           # dry run, prints the plan
    python wiki-scripts/cut_edges.py scipio --write   # apply
    python wiki-scripts/cut_edges.py --list

CUT is step 3 of the repair order in cycle_policy.md and the tool of last resort: it is
only correct when UNMERGE and DEDUPE do not apply -- when the records are genuinely
distinct people and one relationship between them is simply false. **Never cut an edge
that is the only link between two traditions.** Every entry below has to say why the
gentler repairs were ruled out.

AN EDGE LIVES IN TWO PLACES. `Father(C) = P` and `Child(P) = C` are the same edge, and
extract_genealogy.py builds the graph from the UNION, so removing one direction leaves it
alive. This bit the Tros unmerge. This tool always removes both, and rewrites every file
claiming either qid, because editing the canonical file alone is undone the moment it stops
being the numerically-lowest claimant.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

P_FATHER, P_MOTHER, P_CHILD = "P47", "P48", "P20"

CUTS = {
    # queue.md item 2 (2026-08-01). Two of the six mutual-parent pairs that
    # fix_mutual_parent_pairs.py declines to touch. It reports both as "two records of one
    # person that need a MERGE"; hand-checking says neither is, and each is a different
    # defect. That script edits the dump, so its misdiagnoses are written up in queue.md.
    #
    # (a) Q90982 <-> Q88454, THE TWO ESTHERS: **NOT CUT. I claimed the patronymics decided
    #     the direction; they do not, and I retracted it before committing.**
    #
    #       Q88454  "Esther bat Sahlan ben Abraham"          father Q91024 Sahlan
    #       Q90982  "Esther bat Yosef ben 'Amram haDayyan"   father Q88316 Yosef
    #
    #     Both readings are naming-consistent, which is the whole problem:
    #       A: Esther bat Sahlan married Yosef  -> their daughter is "Esther bat Yosef"
    #       B: Esther bat Yosef married Sahlan  -> their daughter is "Esther bat Sahlan"
    #     Under EITHER, each woman is correctly named for her own father and each recorded
    #     father-claim is right. The patronymics confirm both fathers and settle nothing
    #     about who descends from whom -- which is exactly why fix_mutual_parent_pairs.py
    #     reports spouse-coparent evidence on BOTH sides.
    #
    #     I cut it under reading A, and the depth gate then failed: Q88454 fell from 318
    #     levels to 1, because all 3,525 of her ancestors reached her through Q90982. That
    #     is not proof either way -- under reading A the inheritance was spurious and the
    #     loss is correct, under reading B it is real ancestry and the cut is an amputation.
    #     The gate cannot tell those apart, and neither can I. Reverted; needs a source.
    #
    # (b) Q78719 <-> Q78402, BOTH directions. Cleopatra III lists Q78402 as her mother AND
    #     as her child, and Q78402 DOES NOT EXIST -- no file, no shadow claiming the qid,
    #     absent from persons.tsv. It is one of the 138 dangling endpoints. A record that
    #     does not exist cannot be anyone's mother, so both claims are removable with no
    #     judgement call at all. Cleopatra keeps her real mother Q73194 Cleopatra II.
    #     Why not UNMERGE/DEDUPE: there is nothing on the other side to merge with.
    "mutual-parent-residue": [
        ("Q78402", "Q78719", "Q78402 does not exist -- dangling mother claim on "
                             "Cleopatra III"),
        ("Q78719", "Q78402", "Q78402 does not exist -- dangling child claim on "
                             "Cleopatra III"),
    ],
    # 2026-08-01. Tangles 30 and 34 of cycles_review.md -- two 2-record tangles, each a
    # mutual-parent pair, each settled by going and reading the people rather than the
    # dump. Both are the same shape: a real parent->child edge plus its reverse. Neither
    # is a merge (distinct Wikidata ids on both sides, and in the Entenca case different
    # recorded sexes), so UNMERGE and DEDUPE do not apply and CUT is correct.
    #
    # BOTH false edges also exist ON WIKIDATA, which is presumably where they came from,
    # and in both cases Wikidata contradicts itself rather than supporting the edge.
    # "Wikidata is the reference, not gospel" cuts this way too: it can be wrong in a way
    # its own other statements expose.
    #
    # (a) Q18066 -> Q32705, THE NAGANO PAIR. Q32705 is Nagano Hisanari (long ye shang ye,
    #     written both  and , wd Q106814279); Q18066 is his son Nagano Norinari
    #     (wd Q11654206, d. 1530-11-26 in the dump and on Wikidata).
    #
    #     ja.wikipedia's article on Norinari states the descent twice over: he is "the son
    #     of Nagano Hisanari and the elder brother of Nagano Masanari", and "in Bunki 3
    #     (1503) the previous head Hisanari died and he succeeded to the headship". A man
    #     who died in 1530 and inherited the house in 1503 from Hisanari cannot be
    #     Hisanari's father. The generation below agrees: Norinari's son is Nagano Narimasa
    #     (b. 1491, d. 1561), the famous lord of Minowa, so the line runs
    #     Hisanari -> Norinari -> Narimasa.
    #
    #     Wikidata's Q106814279 carries father = [Q11654206 Norinari, Q17229468 Masanari],
    #     and BOTH of those items record Q106814279 as *their* father. Those two P22
    #     statements are its two sons entered upside down; ja.wikipedia has Masanari as
    #     Hisanari's son and Norinari's younger brother.
    #
    #     Keeps the true edge Q32705 -> Q18066, which is already declared on both sides.
    #     Q32705 is left parentless; the dump does not record Hisanari's father and
    #     inventing one is not this tool's business.
    #
    # (b) Q124343 -> Q119481, THE ENTENCA PAIR. Q119481 is Pons Hug d'Entenca
    #     (wd Q21001415, male); Q124343 is his daughter Jussiana d'Entenca (wd Q14083227,
    #     female, d. 1300). The dump records her as both his child and his mother, and
    #     queue.md item 2 already had this pair right as far as "NOT a merge" -- two
    #     Wikidata ids, two sexes -- without a direction.
    #
    #     The direction is decided by the surrounding family, which is consistent three
    #     ways and only inconsistent on the one claim: Jussiana's mother is Q62118141
    #     Sibil.la, Sibil.la's spouse is Pons Hug and her only child is Jussiana. So
    #     Pons Hug + Sibil.la -> Jussiana. Chronology says the same: Pons Hug's father is
    #     Hug III d'Empuries, who died in 1173, and Jussiana died in 1300 having married a
    #     man born in 1150. A woman who died in 1300 is not the mother of a man whose
    #     father died in 1173.
    #
    #     Wikidata's Q21001415 states mother = Q14083227 AND child = Q14083227 on one
    #     record; his father's spouse there is a different woman entirely (Q11927499).
    #
    #     Keeps the true edge Q119481 -> Q124343. Pons Hug keeps his father Q115934, so
    #     his line upward is untouched.
    #
    # Neither cut is a tradition join -- Nagano is Japanese on both sides, Entenca
    # Catalan on both sides.
    #
    # Depth measured before applying, over edges.tsv with exactly these two edges removed.
    # 9 records can be affected at all (the four plus their descendants); total ancestry
    # over them goes 15,777 -> 15,769. Worst: Q119481 5,098 -> 5,095, losing his daughter,
    # her mother and himself -- the cycle counting itself -- while keeping all 5,095 real
    # ancestors through Hug III. Q32705 goes 2 -> 0 as described. No gateway anywhere near
    # this.
    # 2026-08-01. The removal half of the Deimachus UNMERGE. Run
    # `add_bridge_edges.py deimachus-son-of-neleus` FIRST -- that creates Q200002 and gives
    # it Neleus as a father; this then takes the son-of-Neleus parentage off Q75123, which
    # keeps the father-of-Enarete identity (Cleon, Idaea, Glaucia, and both copies of
    # Enarete). Full reasoning in the bridge's comment.
    #
    # Not a CUT in the repair-order sense despite living in this file: no relationship is
    # being denied, both are being attached to the right man. Q133062 Chloris never listed
    # Q75123 among her children anyway, so that edge was one-sided.
    #
    # Measured: 0 records lose their route to Aster, the tangle dissolves, and the 47
    # ancestors Q75123 sheds move to Q200002 rather than leaving the graph.
    "deimachus-unmerge": [
        ("Q131902", "Q75123", "Neleus is the father of the OTHER Deimachus (wd Q1183222), "
                              "now Q200002 -- this record is wd Q1183226, the father of "
                              "Enarete, whose father is Q75162 Cleon"),
        ("Q133062", "Q75123", "Chloris is that same son-of-Neleus's mother, not this "
                              "record's; she never listed Q75123 as her child"),
    ],
    # 2026-08-02. The removal half of the Pedaiah UNMERGE. Run
    # `add_bridge_edges.py pedaiah-of-chronicles` FIRST. Full reasoning there.
    #
    # Not a CUT in the repair-order sense: no relationship is denied. Jeconiah keeps his
    # son Pedaiah, who is now Q200003; Q4617 keeps the Rumah identity its own alias and
    # Wikidata id already carry, and Wikidata gives that man no parent at all.
    "pedaiah-unmerge": [
        ("Q135539", "Q4617", "Jeconiah is the father of the OTHER Pedaiah, wd Q116923358, "
                             "now Q200003 -- this record is wd Q20101444, Pedaiah of "
                             "Rumah, whose only recorded relation is his daughter Zebudah"),
    ],
    # 2026-08-02. THE BIG ONE. Tangle 1 -- 71 records, the largest in the dump -- and the
    # reason it exists is a name collision on "Licinius" spanning six centuries.
    #
    # Q73308 is labelled "Licinius **Varus**", alias `Licinius /Varus/` -- GEDCOM surname
    # slashes, **no Wikidata id**. The dump records it as a child of Q136506 **Flavia Julia
    # Constantia** (wd Q238023, d. 330, Constantine's sister) and Q73455 **Licinius** (wd
    # Q184549, the emperor). Below it hangs the entire Republican block:
    #
    #   Q73308 -> Q73140 Gaius Licinius Varus -> Q72966 Licinia Varus
    #     -> Q72807 Publius Mucius Scaevola (b. 300 BC) -> the Mucii Scaevolae, the Licinii
    #        Crassi, Pompey the Great, Sextus Pompey, Asinius Pollio
    #
    # WIKIDATA SETTLES THE PARENTAGE OUTRIGHT: Q238023 has exactly ONE child, Q166731
    # Licinius II -- and the dump already holds him, correctly, as Q136818 (b. 315, d. 326),
    # same father and mother. So Q73308 as a *second* son of that couple is the collision,
    # and removing it loses nothing: her real son is already recorded.
    #
    # WHY THE CUT IS AT THIS EDGE AND NOT THE ONE BELOW IT. Q73308 could in principle have
    # been Licinius II with a false child instead of the Republican with false parents. It
    # is not: its label and alias are the Republican name, it carries no Wikidata id, and
    # Constantia's real son is separately present. So the parents are the false side.
    #
    # WHAT "LOSES ITS ROUTE TO ASTER" MEANS HERE, since the number sounds worse than it is.
    # Traced: Aster -> ... -> Abraham -> ... -> the Emesene priest-kings -> Julia Domna ->
    # Constantius Chlorus -> Constantia -> **Q73308** -> the Scaevolae -> Mucia Tertia ->
    # Pompey the Great. 206 generations, and the last stretch runs BACKWARDS six hundred
    # years. The Republic is attached to Aster by descending from a family that lived three
    # centuries after it. That is the route being removed.
    #
    # AND THE DUMP ALREADY HAS THE RIGHT ROMAN ROUTE, unused by these records: Q90257
    # **Aeneas the Dardanian** reaches Aster and has 29,153 descendants; Q74644 **Iulus gens
    # Julia** 28,812; Q74518 **Romulus** 28,671. **None of the 103 records that lose Aster
    # here are among their descendants.** So Rome in this dump is two populations -- 28,812
    # attached through Troy properly, and 103 attached through this collision.
    #
    # THE 103 HANG FROM EXACTLY ONE RECORD, Q73308 itself. Reattaching them is therefore a
    # SINGLE edge, not 103 decisions -- give Q73308 a father in the Trojan line and the
    # whole block comes with it. That is Gaiad content and it is Emma's; queue.md item 2.
    #
    # Why not UNMERGE: Q73308 holds one identity, the Republican one; the imperial half is
    # already a separate record. Why not DEDUPE: nothing here is duplicated.
    # Not a tradition join -- or rather, it is a FALSE one: the real Roman join to the
    # synoptic descent is Troy, and it exists.
    #
    # Measured: tangles 14 -> 13, records in a tangle 173 -> 102, largest tangle 71 -> 15,
    # and 103 records lose the route described above.
    "licinius-varus-collision": [
        ("Q136506", "Q73308", "Flavia Julia Constantia (d. 330) recorded as the mother of "
                              "the Republican Licinius Varus -- Wikidata gives her exactly "
                              "one child, Licinius II, and the dump already holds him as "
                              "Q136818"),
        ("Q73455", "Q73308", "and the emperor Licinius as his father, the other half of "
                             "the same collision on the name Licinius"),
    ],
    # 2026-08-02. Tangle 15 of cycles_review.md, Marcus Flaccus / Cassus Curvus -- a Roman
    # mutual-parent 2-cycle, and **both directions go**, not one.
    #
    # This is the pattern apply_roman_unmerge.py was written for and names in its own
    # docstring: "Roman tria nomina repeat father-to-son, so a name-matching import linked
    # father and son in BOTH directions. The result is a 2-cycle." Here the import had four
    # Fulvii to choose from and linked the wrong two.
    #
    # THE REAL STEMMA IS ALREADY IN THE DUMP, complete and declared on both sides:
    #
    #   Q99418 Lucius Fulvius, I -> Q73958 Lucius Fulvius, II -> Q73872 Lucius Fulvius
    #   Curvus -> { Q73530 **Marcus Flaccus**, Q99414 **Marcus Curvus** }
    #   and Q99414 Marcus Curvus -> Q73653 **Cassus Curvus**
    #
    # So Marcus Flaccus and Marcus Curvus are **brothers**, and Cassus Curvus is Flaccus's
    # **nephew**. Neither of the pair is the other's father in either direction, and each
    # already carries its correct father with the edge declared from both ends --
    # Q73872 lists Q73530 among its children, Q99414 lists Q73653.
    #
    # WHY BOTH DIRECTIONS AND NOT ONE. Cutting either single edge opens the ring, and the
    # cheap habit would be to stop there. But that leaves the *other* false claim standing
    # -- a man recorded as his own nephew's son, or his own uncle's father -- purely because
    # no cycle happens to run through it any more. The queue's Scipio note makes the same
    # point about Q99342: an equally impossible claim is not less impossible for being
    # acyclic.
    #
    # Why not UNMERGE: neither record holds two identities; both are single Fulvii with one
    # name each. Why not DEDUPE: "Marcus Flaccus" and "Cassus Curvus" are different men in
    # the same family, three of whose relatives are separately recorded.
    # Not a tradition join: Roman on both sides.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster**, the
    # tangle dissolves, and the distinct ancestors lost anywhere number **three** -- the two
    # ring members and Q99414 Marcus Curvus, who was only reachable from Flaccus's line
    # through the false edge. Afterwards Q73530 has exactly Q73872 as its parent and Q73653
    # exactly Q99414, which is the stemma above.
    "fulvii-mutual-parents": [
        ("Q73653", "Q73530", "Cassus Curvus recorded as the father of Marcus Flaccus, who "
                             "is his uncle -- Flaccus's real father Q73872 Lucius Fulvius "
                             "Curvus is already declared on both sides"),
        ("Q73530", "Q73653", "and the mirror claim, Flaccus as Cassus Curvus's father. "
                             "Cutting only one opens the ring but leaves the other equally "
                             "impossible claim standing; Curvus keeps Q99414 Marcus "
                             "Curvus, declared on both sides"),
    ],
    # 2026-08-02. Tangles 15 and 16 of cycles_review.md -- two more sewn tails, both
    # Roman, both settled by the same asymmetry: the ring's head has parents OUTSIDE the
    # ring, the rest have only their predecessor, and the tail is stitched onto the head.
    #
    # (a) Q73518 -> Q73383, THE JUNII BRUTI.
    #       Q73383 "Lucius Junius Brutus", **aliases include "C. Junius Brutus"**
    #       Q73644 "C. Junius Brutus"                <- the same name
    #       Q73518 "C. Junius **Junius Brutus** Brutus"  <- a doubled, composite name
    #     The ring is Q73383 -> Q73644 -> Q73518 -> Q73383, and the recurring cognomen is
    #     exactly what lets a name-matching import join the ends. Only Q73383 has a parent
    #     outside the ring: Q73863 "Junius Brutus", which has a father of its own (Q73952)
    #     and lists Q73383 as its child. So Q73383 is the head with real parentage, and
    #     Q73518, the tail, is the extra claim.
    #     After the cut Q73383 keeps Q73863 and the chain reads 803/804/805.
    #
    # (b) Q76933 -> Q76693, THE SERGII OCTAVII.
    #       Q76693 "Sergius Octavius **Pontianus Laenes** Octavius **Pontainus**"
    #       Q77155 "Sergius Ovtavius **Laenes**"
    #       Q76933 "Sergius Octavius **Pontainus**"
    #     **Q76693's label is a concatenation of the other two.** That is a merge artefact
    #     on its face, and it carries five parents where the others carry two and one.
    #     Four of those five sit outside the ring -- Q76930 "Lucius Octavius Laenus",
    #     Q76936 "Octavius Laenas", Q76945 "Lucius Octavius Laenas" and Q76939 "Pontia" --
    #     so again the head has real parentage and the tail Q76933 is the extra.
    #     After the cut Q76693 keeps all four and the chain reads 3186/3188/3189.
    #
    # Why not UNMERGE, even though Q76693's label looks composite: splitting it needs a
    # decision about which of its five parents and three children go to which half, and
    # nothing in the dump or on Wikidata decides that -- none of these six records carries a
    # Wikidata id. The loop closes on one edge and that edge is identifiable without the
    # split. Why not DEDUPE: in each ring the members are consecutive generations, not
    # copies; merging would fuse generations.
    # Not a tradition join: Roman throughout both.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster** in
    # either, both tangles dissolve, and the distinct ancestors lost are **three** (the
    # Brutus ring) and **four** (the Sergius ring plus Q77395 Paullus, Q77155's mother) --
    # every one inside its own ring.
    "roman-sewn-tails": [
        ("Q73518", "Q73383", "the tail of a three-deep Junii Bruti chain recorded as the "
                             "father of its head, whose real father Q73863 sits outside "
                             "the ring -- the shared cognomen 'C. Junius Brutus' is what "
                             "let the ends be joined"),
        ("Q76933", "Q76693", "the tail of a three-deep Sergii Octavii chain recorded as "
                             "one of five fathers of its head, whose label is a "
                             "concatenation of the other two members' names and which "
                             "keeps four parents outside the ring"),
    ],
    # 2026-08-02. Tangle 16 of cycles_review.md, the Malacca line -- a fourth sewn tail,
    # and settled on structure rather than on adjudicating the Sejarah Melayu.
    #
    #   Q161658 Maharaja Parameswara / Raja Iskandar Shah
    #     -> Q161777 Dewa Amas Sang Aji Kala
    #     -> Q161966 Demang Lebar Daun Mangkabumi (Bendahara I)
    #     -> Q162275 Wan Sendari (Radin Ratna Cenderapuri)
    #     -> Q161658                                         <-- closes the ring
    #
    # THE ARGUMENT IS THE ASYMMETRY, not the chronicle. Three of the four have **exactly one
    # parent**, their predecessor in the chain. Q161658 has **three**: Q160051 "Maharaja
    # Malayu II - Tribhuwanaraja (**1286-1316**)", Q171395 Puti Reno Mandi Sari Lawik, and
    # Q162275, the chain's own tail. Both of the first two are recorded spouses of each
    # other's partner -- Q160051's spouse list contains Q171395 -- so the head has a
    # coherent, dated parentage outside the ring and one extra claim that closes it. Same
    # shape as the Shaodian generation-counter and the Jatavallabha acaryas below.
    #
    # WHAT I DELIBERATELY DID NOT RELY ON. The Sejarah Melayu has a Demang Lebar Daun who is
    # the Palembang ruler and father-in-law of Sang Sapurba, generations BEFORE Parameswara;
    # this record is labelled "**Bendahara I**", which instead suggests the first Bendahara
    # of Malacca, generations AFTER him. Those two readings put the chain in opposite
    # directions, and I could not settle which is meant. **The cut does not depend on it**:
    # under either reading Wan Sendari cannot be both Parameswara's mother and his
    # great-granddaughter, and the head's dated external parentage identifies which end is
    # the head.
    #
    # Why not UNMERGE or DEDUPE: no record here holds two identities and none duplicates
    # another. Not a tradition join: one Malay royal line throughout.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster** (the
    # component does not reach it), the tangle dissolves, and the distinct ancestors lost
    # anywhere number **four** -- exactly the ring. Afterwards the chain reads as a ladder,
    # 26/27/28/29 from head to tail, and Parameswara keeps Tribhuwanaraja and Puti Reno.
    "malacca-sewn-tail": [
        ("Q162275", "Q161658", "Wan Sendari, the tail of a four-deep chain descending from "
                               "Parameswara, recorded as his third parent -- he keeps his "
                               "dated father Tribhuwanaraja (1286-1316) and his mother "
                               "Puti Reno Mandi Sari Lawik"),
    ],
    # 2026-08-02. Tangle 15 of cycles_review.md, Brahma and the eleven Rudras. Puranic,
    # so it was checked FIRST against the Daksha case in queue.md -- where the ring turned
    # out to be doctrine and must not be cut. **This one is not that.**
    #
    #   Q160928 Swammbhu Brambha (Svayambhu Brahma)
    #     -> Q160981 (unnamed, "Person Q160981")      <- the Marichi slot
    #     -> Q160965 Kasayap Muni (Kashyapa)
    #     -> Q160946 "11 Rudras"
    #     -> Q160928 Brahma                            <-- closes the ring
    #
    # The first three edges are canonical: Brahma's mind-born son Marichi fathers Kashyapa,
    # and the eleven Rudras are Kashyapa's offspring by Surabhi -- confirmed inside the dump
    # itself, since Q160946's mother is Q160966 **Surbhi**. So the Rudras here are the
    # Kashyapa-and-Surabhi set of the Vishnu Purana, and they are Brahma's DESCENDANTS by
    # the dump's own chain.
    #
    # WHY THIS IS NOT THE DAKSHA CASE, stated because the resemblance is close enough to
    # matter. There, `Q153390`'s label spells out the doctrine -- "DAKSHA (**reborn as
    # DAKSHA**) Prachetas" -- and the record carries two fathers, one per birth, because the
    # Puranas assert the rebirth. Here there is no annotation, no rebirth, and no doctrine
    # making the eleven Kashyapa-born Rudras the parents of Brahma.
    #
    # ONE READING I CHECKED AND REJECTED, so it is on the record: in Shaiva cosmology Shiva
    # does generate Brahma, and a Shaiva/Vaishnava synthesis would be exactly the kind of
    # cross-tradition join this project exists to make. But `Q160946` is the **eleven
    # Rudras**, a group with a named father and mother in this dump, not Rudra-Shiva the
    # creator. If the intent was the Shaiva reading, this cut is wrong and is one revert --
    # flagged in queue.md rather than assumed away.
    #
    # Brahma is NOT left parentless: he keeps `Q160947` **Gobardhan Vishnu** and `Q160948`,
    # which is his canonical birth from Vishnu.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster** (the
    # component does not reach it), the tangle dissolves, and the distinct ancestors lost
    # anywhere number **six** -- the four ring members plus Brahma's consort Q160929 and
    # Kashyapa's wife Q160966 Surbhi, all inside the ring. Afterwards the chain reads as a
    # ladder, 2/4/5/7 from Brahma down to the Rudras.
    "brahma-rudras": [
        ("Q160946", "Q160928", "the eleven Rudras, Kashyapa's sons by Surabhi and so "
                               "Brahma's own descendants in this chain, recorded as his "
                               "father -- he keeps Gobardhan Vishnu, which is his "
                               "canonical parentage"),
    ],
    # 2026-08-02. Tangle 10 of cycles_review.md, the Jatavallabha acaryas -- a seven-
    # generation guru lineage with its last generation sewn back onto its first. Same shape
    # as the Shaodian chain below, and settled the same way: by what the records carry
    # rather than by any external source.
    #
    #   Q171493 Venkatacharyar   -> Q171595 Rangacharya   -> Q171604 Venkatacharya
    #     -> Q171614 Srinivasacharya -> Q171622 Srinivasacharyar -> Q171636 Venkatacharya
    #     -> Q171648 Rangacharya -> Q171493                       <-- closes the ring
    #
    # **Six of the seven have exactly one father: their predecessor in the chain. Q171493
    # has two** -- Q171648, the chain's last generation, and Q171378 "**Govindacharyar**
    # Jatavallabha", which sits outside the ring, has a father of its own (Q171309), and
    # lists Q171493 as its **only** child. So the chain has a proper head with a proper
    # parent, and the tail has been joined to it.
    #
    # Why the ends could be joined at all: the names recur. Q171595 and Q171648 are both
    # "Rangacharya Jatavallabha", Q171604 and Q171636 both "Venkatacharya Jatavallabha" --
    # normal in a Sri Vaishnava guru-parampara, where a descendant takes a forebear's name,
    # and exactly the condition a name-matching import needs to close a loop. Govindacharyar
    # is the one name in the neighbourhood that does NOT recur, which is why the head is
    # identifiable.
    #
    # Why not DEDUPE the two Rangacharyas or the two Venkatacharyas: they are three
    # generations apart in a chain each link of which is declared on both sides, and merging
    # either pair would fuse generations rather than open the ring.
    # Why not UNMERGE: no record here holds two identities.
    # Not a tradition join: one South Indian acarya lineage throughout.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster** (the
    # component does not reach it), the tangle dissolves, and the distinct ancestors lost
    # anywhere number **seven** -- precisely the seven ring members. Afterwards the chain
    # reads as a clean ladder, 46/47/48/49/50/51/52 ancestors from head to tail, which is
    # what a seven-generation line with no loop in it should look like.
    "jatavallabha-sewn-tail": [
        ("Q171648", "Q171493", "the last generation of a seven-deep acarya chain recorded "
                               "as the father of its first -- Q171493's real father is "
                               "Q171378 Govindacharyar, outside the ring, whose only child "
                               "he is"),
    ],
    # 2026-08-02. Tangle 6 of cycles_review.md, Shaodian -- a generation-counter chain
    # with its tail sewn to its own head. The dump's own labels settle this one; no
    # external source is needed.
    #
    # Q6421 Shaodian (b. 2697 BC, wd Q4302144) is the father of the Yellow Emperor. Hanging
    # below him is a chain of placeholders, and they are LABELLED WITH THEIR DEPTH:
    #
    #   Q6421   Shaodian            -> Q87856 "Generation 2"
    #   Q87856  "Generation 2"      -> Q87854 "Generation 3"
    #   Q87854  "Generation 3"      -> Q87852 "Generation 4"
    #   Q87852  "Generation 4"      -> Q87850 "Generation 5"
    #   Q87850  "Generation 5"      -> Q87848 -> Q87846 -> Q87844 -> Q87842 -> Q87840
    #   Q87840  (unlabelled)        -> Q6421 Shaodian          <-- closes the ring
    #
    # The counter runs DOWNWARD from Shaodian -- he is generation 1 and "Generation 2" is
    # his child -- so the tail of that chain cannot also be his father. Four more unlabelled
    # placeholders continue past "Generation 5" and the last of them is the one sewn back on.
    #
    # Shaodian is NOT left parentless. He has five recorded fathers and keeps four:
    # Q6433 Fuxi, Q6435 Nuwa, and Q51954 + Q87862, which are two copies of You Xiong (both
    # with father Q54433 and both with Q6421 as their only child -- logged as a duplicate in
    # queue.md, not merged here).
    #
    # Why not UNMERGE: nothing holds two identities. Why not DEDUPE: the ten chain records
    # are distinct placeholder generations, not copies of one another.
    # Not a tradition join: Chinese on both sides, and the cross-tradition link into this
    # material is Q54433 -> You Xiong, which is untouched.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster**, the
    # tangle dissolves, and the distinct ancestors lost anywhere number **eleven** -- the
    # ten ring members plus Q87860, "Generation 2"'s mother. Every one is inside the ring.
    # Shaodian goes 274 -> 263.
    "shaodian-generation-chain": [
        ("Q87840", "Q6421", "the tail of a chain whose own labels count generations "
                            "DOWNWARD from Shaodian -- Generation 2, 3, 4, 5 and four "
                            "unlabelled more -- recorded as Shaodian's father; he keeps "
                            "Fuxi, Nuwa and both You Xiong records"),
    ],
    # 2026-08-02. Tangle 2 of cycles_review.md, the Anicii/Petronii -- 18 records, the
    # second-largest tangle, and one woman recorded as the mother of her own
    # great-great-grandparents.
    #
    # Q75603 is **Anicia Demetrias**, wd Q3625008, and the dump has her placed correctly:
    # father Q75516 Anicius Hermogenianus Olybrius, mother Q113011 Anicia Juliana, both
    # matching Wikidata. What it also gives her is two children, Q75558 Clodia Celsina and
    # Q75576 Clodius Celsinus Adelphius -- and those two are her ANCESTORS, five
    # generations up, by the dump's own chain:
    #
    #   Q75576 Clodius Celsinus Adelphius (wd Q1147586)
    #     -> Q75540 Quintus Clodius Hermogenianus Olybrius (wd Q1148526, 335-380)
    #     -> Q75522 Anicia Faltonia Proba (wd Q1154373)
    #     -> Q75516 Anicius Hermogenianus Olybrius (wd Q1372249, cos. 395)
    #     -> Q75603 Demetrias
    # every link of which Wikidata states on both sides.
    #
    # **Wikidata records no children for Q3625008 at all** -- no child, no spouse. (She is
    # the Anicia Demetrias who took the veil in 413 and to whom Jerome, Augustine and
    # Pelagius wrote; that is context rather than the argument. The argument is that her
    # two recorded children are her own ancestors.)
    #
    # ONLY THE MOTHER-CLAIMS GO. The father-claim on both children is **correct and stays**:
    # Q75606 "Clodius Celsinus" carries wd Q110915987, which is exactly the father Wikidata
    # gives for Q1147586. So Clodia Celsina and Clodius Celsinus Adelphius keep their real
    # father and his line -- they land at 1,544 ancestors rather than 0.
    #
    # BOTH are needed. Cutting only Q75603 -> Q75558, the edge in the shortest loop, leaves
    # a five-record ring closed through the other child: Q75603 -> Q75576 -> Q75540 ->
    # Q75522 -> Q75516 -> Q75603. Measured, not assumed. With both, the tangle dissolves.
    #
    # Why not UNMERGE: Q75603 holds one identity and one Wikidata id. Why not DEDUPE:
    # nothing here is duplicated. Not a tradition join: late-Roman on every side.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster.**
    # Clodia Celsina and Adelphius go 4,258 -> 1,544, Petronius Probus 4,258 -> 3,583,
    # Demetrias herself 4,258 -> 4,257. The 2,714 distinct ancestors shed are the Anicii and
    # Petronii flowing backwards into their own forebears through the false maternity.
    "demetrias-reversed-maternity": [
        ("Q75603", "Q75558", "Anicia Demetrias recorded as the mother of Clodia Celsina, "
                             "who is her great-great-grandmother -- Wikidata gives "
                             "Q3625008 no children at all, and the real father Q75606 "
                             "(wd Q110915987) stays"),
        ("Q75603", "Q75576", "the same for Clodius Celsinus Adelphius, her "
                             "great-great-grandfather; without this one a five-record ring "
                             "survives through him"),
    ],
    # 2026-08-02. Tangle 14 of cycles_review.md, Cabrera/Urgell -- a duplicated countess
    # hung under a man who died ninety years after her husband.
    #
    # The loop's other four edges are the real Catalan descent, each confirmed on Wikidata:
    #   Q107162 Ermengol VII d'Urgell (wd Q949224, d. 1184)
    #     -> Q123407 Marquesa d'Urgell (wd Q21126997, 1150-1209), his daughter
    #     -> Q124325 Guerau IV de Cabrera (wd Q4894186, d. 1228), her son
    #     -> Q124326 Guerau V de Cabrera (wd Q19291067, d. 1242), his son
    # and the fifth, Q104371 -> Q107162, is Arsenda as Ermengol VII's mother, which is also
    # right. What closes the ring is Q124326 -> Q104371: Guerau V, dead in 1242, recorded
    # as the father of the woman who married Ermengol VI, dead in **1154**.
    #
    # THE WOMAN IS IN THE DUMP TWICE, and the good copy is untouched by this:
    #   Q118293 "Arsenda de Cabrera"  wd Q21126905, parents Q123444 + Q123448,
    #                                 spouse Q107158 Ermengol VI, child Q107162
    #   Q104371 "Arsende de Cabrera"  NO wd id, father Q124326 Guerau V, mother Q104369,
    #                                 spouse Q107158 Ermengol VI, child Q107162
    # Same husband, same son. Wikidata's Q21126905 is "comtessa consort d'Urgell", spouse
    # Q2862207 Ermengol VI, child Q949224 Ermengol VII -- and Guerau V's four recorded
    # children there do not include her.
    #
    # Why CUT and not DEDUPE, although the duplicate is real and is logged in queue.md:
    # merging them does not break the ring. The survivor would inherit Q104371's
    # father-claim on Q124326 and still be its own descendant's ancestor -- the same reason
    # the Shila pair was cut rather than merged.
    # Why not UNMERGE: neither record holds two identities.
    # Not a tradition join: Catalan on both sides.
    #
    # Measured over edges.tsv before applying: **one record loses its route to Aster, and
    # it is the duplicate itself** -- Q104371, 6,563 ancestors -> 1. That is the correct
    # answer rather than a casualty, because the real Arsenda keeps everything: Q118293
    # stays at **5,020 ancestors and still reaches Aster**, and her son Ermengol VII keeps
    # 5,573 and his route, through her. Only 15 records lose any ancestry at all.
    "cabrera-arsende-guerau": [
        ("Q124326", "Q104371", "Guerau V de Cabrera (d. 1242) recorded as the father of "
                               "Arsenda, wife of Ermengol VI (d. 1154) -- and this Arsende "
                               "is a second copy of Q118293, which carries her real "
                               "parents and her Wikidata id"),
    ],
    # 2026-08-02. Tangle 13 of cycles_review.md, the Claudii -- five records, and a branch
    # of the family hung above its own root.
    #
    # Wikidata gives a clean three-generation descent, each link stated on both sides:
    #   Q283141   Appius Claudius Crassus                  = dump Q151743, b.400 d.350
    #     -> Q657609  Appius Claudius Crassus Inregillensis, cos. 349   = dump Q73970
    #     -> Q5759141 Gaius Claudius Crassus, dictator 337            = dump Q73887
    #     -> Q297783  Appius Claudius Caecus, censor 312              = dump Q73782
    # and **Q657609 has exactly one father there, Q283141** -- which the dump already
    # holds, as one of Q73970's three recorded fathers.
    #
    # Below Caecus the dump continues into the Claudii Nerones, correctly: Caecus's son
    # Q78812 Tiberius Claudius Nero, then Q78752 Publius Claudius-Nero. The ring closes
    # because Q78752 is then recorded as the father of Q73970 -- so a man two generations
    # BELOW Caecus fathers Caecus's own great-grandfather.
    #
    # Chronology says the same using the dump's own figures read as BC magnitudes:
    #   Q151743 400/350 -> Q73970 350/349 -> Q73887 370/337 -> Q73782 341/300
    #   -> Q78812 -> Q78752 -> back to Q73970, dead in 349.
    # Caecus died in 300; his grandson cannot father a man who died fifty years earlier.
    #
    # Why not UNMERGE: each record here holds one identity, and the three with Wikidata ids
    # hold one id each. Why not DEDUPE: the Nerones are a real branch, not a copy of the
    # Crassi. Not a tradition join: Roman throughout.
    #
    # Q73970 is NOT left parentless -- he keeps Q151743, which is the father Wikidata gives
    # him, and Q74091. (That he has three fathers at all is a separate multi-parent defect;
    # Q74091 looks like a duplicate of Q151743 and is logged in queue.md, not merged here.)
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster** --
    # the component does not reach it -- the tangle dissolves, and the distinct ancestors
    # lost anywhere number **seven**: the five ring members plus the two wives Q73785 and
    # Q73890. Every one of them is inside the ring. 28,993 records below shed those seven
    # and nothing else.
    "claudii-nero-inversion": [
        ("Q78752", "Q73970", "Publius Claudius-Nero, two generations below Appius Claudius "
                             "Caecus, recorded as the father of Caecus's great-grandfather "
                             "-- Wikidata gives Q657609 one father, Q283141, and the dump "
                             "already holds it as Q151743"),
    ],
    # 2026-08-02. Tangle 7 of cycles_review.md, Meurig ab Ynyr Gwent -- 11 records, and a
    # THIRD Ynyr that should not exist.
    #
    # Every edge in the ring is corroborated on both sides and by a spouse pairing, so
    # there is no single reversed claim to find. What there is instead is one couple with
    # two sons of the same name:
    #
    #   Q136957 "Meurig **ab Ynyr** Gwent"  b.1030, father Q137382, mother Q137383 Nest,
    #                                       spouse Q136958 Elen, children Q137384 + Q136608
    #   Q137382 "**Ynyr Gwent**"            b.1000, spouse Q137383 Nest, child Q136957
    #   Q136608 "**Ynyr Fychan** ap Meurig ab Ynyr Gwent"  b.1070, father Q136957,
    #                                                      mother Q136958
    #   Q137384 "Ynyr, lord of Gwent"       father Q136957, mother Q136958, child Q137899
    #
    # Meurig's father is Ynyr, which his own name says and Q137382 supplies from both
    # sides. His son named after that grandfather is Q136608 -- **Fychan** is the Welsh
    # marker for exactly that, "the Younger". So Q137384, a *second* son of the same couple
    # with the same name and no "Fychan", is the artefact. Its real identity is the earlier
    # Ynyr, several generations ABOVE Meurig, and that is where the ring comes from.
    #
    # Chronology settles it independently. Q137384's line runs Ynyr -> Q137899 Morfudd
    # ferch Ynir -> Q137320 Gwerystan ap Gwaithfoed -> **Q137900 Cynfyn ap Gwerstan,
    # b. 990 d. 1023** -- the historical prince of Powys. Meurig is born 1030. A man born in
    # 1030 is not the great-great-grandfather of a man born in 990; Ynyr lord of Gwent
    # belongs around 900.
    #
    # BOTH parent claims go, not just the father. Q136958 Elen is in the tangle in her own
    # right (her father Q137385 Ednyfed is too), so cutting only Q136957 leaves the ring
    # closed through her -- measured: seven records still in a cycle. With both, it
    # dissolves.
    #
    # Why not UNMERGE: Q137384 holds one identity with one Wikidata id; the duplication is
    # of a NAME across generations, not of a record. Why not DEDUPE: Q137384 and Q136608
    # are two different men, grandfather and grandson.
    # Not a tradition join: Welsh on both sides.
    #
    # Measured over edges.tsv before applying: **0 records lose their route to Aster** --
    # the component does not reach it. Q137384 goes to 0 ancestors, which is honest: the
    # dump does not record the earlier Ynyr's parentage and inventing it is not this tool's
    # business. Meurig goes 184 -> 134, losing only the stretch where he was his own
    # ancestor. 3,480 records below lose ancestry and every one of the 184 distinct records
    # lost is inside the ring.
    "gwent-third-ynyr": [
        ("Q136957", "Q137384", "Meurig ab Ynyr Gwent (b.1030) recorded as the father of "
                               "Ynyr lord of Gwent, whose great-grandson Cynfyn was born "
                               "in 990 -- Meurig's real Ynyr-named son is Q136608 Ynyr "
                               "Fychan and his real father is Q137382 Ynyr Gwent"),
        ("Q136958", "Q137384", "Elen, Meurig's wife, carries the same false parentage; "
                               "she is in the tangle herself, so the ring stays closed "
                               "through her if only the father-claim is cut"),
    ],
    # 2026-08-01. Tangle 11 of cycles_review.md, the Theban kings of the Second
    # Intermediate Period. **This cut does NOT dissolve the tangle and is not meant to.**
    # It removes one edge that is positively refuted by an external attestation; the
    # component has two interlocking rings and the second one needs a source I do not have.
    # The remaining ring is written up in queue.md rather than guessed at.
    #
    # None of the seven records carries a Wikidata id, so they had to be matched by name:
    #
    #   dump Q85498 "Sekhemre Sementawi Djehuti"   = wd Q889883  Djehuti
    #   dump Q85500 "Mentuhotep, Queen of Egypt"   = wd Q536310  Mentuhotep, queen consort
    #   dump Q85514 "Senebhenaf, Vizier of Egypt"  = wd Q2270828 Senebhenaf, vizier
    #   dump Q85478 "Sekhemre Sankhtawy Neferhotep III" = wd Q888037 Neferhotep III
    #
    # THE ATTESTATION, and it is positive rather than an absence:
    #   Q2270828 Senebhenaf  -- child   Q536310
    #   Q536310  Mentuhotep  -- father  Q2270828, spouse Q889883, described on Wikidata as
    #                                   "Gemahlin des Pharaos Djehuti" / "queen consort"
    #
    # So the vizier Senebhenaf's child is **Queen Mentuhotep**, and Djehuti is her
    # **husband**. The dump has Senebhenaf fathering both of them (Q85514 -> Q85498 and
    # Q85514 -> Q85500), which makes Djehuti his own wife's brother and closes a ring.
    # Q85514 -> Q85500 is correct and stays. Q85514 -> Q85498 is the son-in-law recorded as
    # a son, and goes.
    #
    # Why not DEDUPE or UNMERGE: seven distinct kings and officials, no shared identity.
    # Not a tradition join: Egyptian on both sides.
    #
    # Measured: **0 records lose their route to Aster**, one record loses ancestry -- Q85498
    # Djehuti himself, 12 ancestors, which is his wife's family reached through the false
    # edge. The tangle drops from 7 records to 6.
    #
    # WHAT IS LEFT, EXPLICITLY. The surviving ring is
    #   Q85500 Mentuhotep -> Q85578 Mentuhotep VI -> Q85554 Sebekemsaf -> Q85528 Yauyebi
    #   -> Q85514 Senebhenaf -> Q85500
    # Senebhenaf -> Mentuhotep is the attested edge above and must not be cut. The false
    # one is among the other three, and I could not settle which: Wikidata records no
    # parents for Sobekemsaf I (Q563693) and has **no record at all for "Yauyebi"**, and
    # its date for Senebhenaf (-1500) is later than its date for his own daughter (-1650),
    # so its chronology here decides nothing either. That needs the Turin King List and
    # Ryholt's reconstruction, not another pass over the dump.
    "theban-senebhenaf": [
        ("Q85514", "Q85498", "the vizier Senebhenaf is Djehuti's father-in-law, not his "
                             "father -- Wikidata has Senebhenaf's child as Q536310 Queen "
                             "Mentuhotep, whose spouse is Djehuti. Does not dissolve the "
                             "tangle; see the note above for the ring that survives"),
    ],
    # 2026-08-01. Tangle 19 of cycles_review.md, the Pinarii -- a two-generation family
    # stretched into four by duplication, then rolled into a ring.
    #
    # WHAT WIKIDATA HAS, and it is short:
    #   Q93953755 "Pinarius", described as **the brother-in-law of Julius Caesar**, spouse
    #             Q2743448 Julia Major, one child, NO FATHER
    #   Q382127   labelled BOTH "Lucius Pinarius Scarpus" AND "Lucius Pinarius",
    #             "nephew of Caesar", father Q93953755, mother Q2743448, NO CHILDREN
    # Two generations. That is the whole family.
    #
    # WHAT THE DUMP HAS -- the same two men, wearing four records and two wives:
    #   Q77782  "Pinarius"                 wd Q93953755   spouse Q137708 Julia Major
    #   Q78264  "Lucius Pinarius"          wd Q382127     spouse Q78267  Julia Caesaris Major
    #   Q78108  "Lucius Pinarius Scarpus"  no wd          child  Q77955
    #   Q77955  "Lucius Pinarius Scarpus"  no wd          child  Q77782  <-- closes the ring
    #
    # Q382127 carries both labels, so Q78108 and Q77955 -- same label, no Wikidata id --
    # are copies of Q78264. And Q78267 "Julia Caesaris Major" has the SAME PARENTS as
    # Q137708 "Julia Major" (Q73029 and Q73026), so the dump has married Lucius Pinarius to
    # a second copy of his own mother.
    #
    # Under any reading of that, Q77955 -> Q77782 makes a man the father of his own father.
    # It is the only edge in the loop that is false on both the dump's own chain and on
    # Wikidata, which gives Pinarius no father at all.
    #
    # Why not DEDUPE, although the duplicates are real and are logged in queue.md: merging
    # Q78264/Q78108/Q77955 does not break the ring. The survivor keeps Q77955's child claim
    # on Q77782 while remaining Q77782's son, so a 4-cycle becomes a 2-cycle. The false
    # parent-claim has to go either way, and it is the smaller and better-evidenced edit.
    # Why not UNMERGE: nothing here holds two identities; the problem is the opposite,
    # one identity spread over three records.
    # Not a tradition join: Roman on both sides.
    #
    # Measured over edges.tsv before applying: **exactly one record loses its route to
    # Aster, Q77782 Pinarius himself, 998 ancestors -> 0.** That is the correct answer and
    # not a casualty -- he is the brother-in-law, related to the Julii by marriage and not
    # by blood, and Wikidata records no father for him. All **19,374 records below him keep
    # their route**, because they descend through Julia Major, who is a Julia in her own
    # right; his sons Q77566 and Q78264 move 998 -> 994.
    "pinarii-scarpus": [
        ("Q77955", "Q77782", "Lucius Pinarius Scarpus recorded as the father of Pinarius, "
                             "who is his own father -- Wikidata gives Pinarius, Caesar's "
                             "brother-in-law, no father at all, and Q77955 is a duplicate "
                             "of his son Q78264"),
    ],
    # 2026-08-01. Tangle 7 of cycles_review.md, the Caecilii Metelli -- 13 records, and
    # every one of them carries a Wikidata id, so the whole stemma can be read off.
    #
    # The loop is
    #   Q72834 -> Q141414 -> Q139559 -> Q139560 -> Q73458 -> Q73311 -> Q73146 -> Q72984
    #   -> Q72834
    # and seven of those eight edges are the real Metelli descent, confirmed record by
    # record against Wikidata:
    #
    #   Q73458  Gaius Caecilius                       wd Q107101893   b. 400 BC
    #   Q73311  L. Caecilius Metellus Denter          wd Q521498      320 - 283 BC
    #   Q73146  L. Caecilius Metellus, cos. 251       wd Q359810      d. 221 BC
    #   Q72984  Q. Caecilius Metellus, cos. 206       wd Q929498      245 - 175 BC
    #   Q72834  L. Caecilius Metellus Calvus, cos.142 wd Q703354      b. 200 BC
    #   Q141414 Caecilia Metella, his daughter        wd Q461531      200 - 160 BC
    #   Q139559 Lucullus, her son                     wd Q242819      117 - 56 BC
    #   Q139560 Licinia, his daughter                 wd Q113376428
    #
    # Read as BC magnitudes that runs cleanly downward, 400 -> 320 -> 221 -> 245/175 ->
    # 200 -> 160 -> 117, and each link is stated on both sides on Wikidata.
    #
    # The eighth edge closes the loop by running the whole chain backwards in one step:
    # Q139560 -> Q73458 makes **Licinia the parent of Gaius Caecilius**, a man born some
    # three hundred years before her father. Wikidata gives her exactly two relations,
    # father Lucullus and mother Clodia, and **no children at all** -- her description
    # there is simply "daughter of Lucullus and Clodia". cycles_review.md already flagged
    # this one edge as contradicted.
    #
    # Why not UNMERGE: every record holds one identity with its own Wikidata id.
    # Why not DEDUPE: Q138399 and Q141414 do share the label "Caecilia Metella", but they
    # are two different women on Wikidata (Q6454825, 150-70 BC, and Q461531, 200-160 BC,
    # the mother of Lucullus) and merging them would not touch this edge anyway.
    # Not a tradition join: Roman on both sides.
    #
    # Measured over edges.tsv before applying: **zero records lose their route to Q1** --
    # the component does not reach Aster at all. Q73458 goes 52 -> 1 and keeps his real
    # father Q73581; the 51 he loses are the loop itself plus Licinia's line, which is to
    # say his own descendants, which is what the false edge was feeding him. The one
    # record left without a child is Q139560 Licinia, and that is Wikidata's position too.
    "metelli-licinia": [
        ("Q139560", "Q73458", "Licinia, daughter of Lucullus (b. 117 BC), recorded as the "
                              "parent of Gaius Caecilius (b. 400 BC) -- she is the bottom "
                              "of this descent, not the top, and Wikidata gives her no "
                              "children"),
    ],
    # 2026-08-01. Tangle 28 of cycles_review.md, "Acha Ish Kfar Temarta" -- three records,
    # and the dump states the answer about itself twice.
    #
    #     Q86617  "Shila Ish Kfar Temarta"                        father Q91134, child Q86607
    #     Q91224  "Shila Ish Kfar Temarta"                        NO father,     child Q86607
    #     Q86607  "Acha Ish Kfar Temarta"                         fathers Q86617 AND Q91224
    #     Q91134  "Abba 'Abbahu' bar Acha bar Sallah al-Kafri"    father Q86607
    #
    # (a) THE NAME IS THE GENEALOGY. Q91134 is "Abba **bar Acha bar Sallah**" -- Abba son
    #     of Acha son of Sallah. So the descent is Sallah -> Acha -> Abba, and Sallah is
    #     Abba's grandfather. Shila and Sallah are the same name; both Shila records and
    #     Acha all carry the same locality, "Ish Kfar Temarta". Q86607's other children
    #     say it again: Q91182 is "Chiya **son of Shila**".
    #
    # (b) THE PARALLEL IMPORT SAYS IT TOO. Shila is in the dump twice, Q86617 and Q91224,
    #     same label, both recorded as Acha's father. The clean copy Q91224 has **no
    #     father at all**. The father-claim that closes the loop exists on exactly one of
    #     the two copies, which is what an import artefact looks like and not what a
    #     shared source looks like.
    #
    # So Q91134 -> Q86617 makes Abba the father of his own grandfather. It goes.
    #
    # Why not DEDUPE, even though Q86617/Q91224 plainly ARE one man recorded twice: merging
    # them does not break the loop. The survivor would still carry Q86617's father-claim on
    # Q91134 and Acha would still be his own great-grandfather. The duplicate is real and is
    # written up in queue.md, but it is a separate repair and the queue's scope this session
    # is loops, not deduplication.
    # Why not UNMERGE: no record here holds two identities; none carries a Wikidata id at all.
    # Not a tradition join: the whole component is one Babylonian rabbinic family.
    #
    # Measured over edges.tsv before applying: **zero records lose their route to Q1** --
    # the component does not reach Aster in the first place. Q86617 goes to 0 ancestors,
    # which is right: the dump does not record Sallah's father. Everyone else in the
    # component moves by 0 to 2, the cycle no longer counting itself.
    "acha-kfar-temarta": [
        ("Q91134", "Q86617", "Abba bar Acha bar Sallah recorded as the father of Shila, "
                             "who is the Sallah of his own patronymic -- and the parallel "
                             "copy of Shila, Q91224, carries no father"),
    ],
    # 2026-08-01. Tangles 27 and 31 of cycles_review.md. Same method as nagano-entenca:
    # read the people, find the edge that cannot be, remove it from both sides.
    #
    # (a) Q73925 -> Q73824, THE ALCIMACHUS LOOP. Three records, three generations, and one
    #     edge that folds the youngest back onto the oldest:
    #
    #         Q73824  Agathocles of Pella          wd Q4691548
    #         Q135467 Alcimachus of Apollonia      wd Q24254
    #         Q73925  Alcimachus                   wd Q4713126
    #
    #     Wikidata is clean and consistent across all three: Q4691548's children are
    #     Q24254, Q32133, Q23938, Q176912 -- Alcimachus of Apollonia and Lysimachus and
    #     his brothers -- and the dump agrees, giving Q73824 exactly four children.
    #     Q24254's father is Q4691548 and its children are Q4713126 and Q7183087. Q4713126's
    #     father is Q24254 and its only child is Q6710240, which is not Agathocles.
    #     So the line runs Agathocles -> Alcimachus of Apollonia -> Alcimachus, and the
    #     dump has the first two edges right. The third, Q73925 -> Q73824, makes a man his
    #     own grandfather's father. Wikidata records no link in that direction at all, and
    #     Agathocles of Pella has no recorded father anywhere -- which is the state
    #     Q73824 is left in, and the correct one.
    #
    #     Why not UNMERGE: each of the three holds one identity with its own Wikidata id.
    #     Why not DEDUPE: Q73925 and Q135467 share the name Alcimachus and are NOT the same
    #     man -- Q4713126's own description is "son of Alcimachus of Apollonia", and
    #     Q24254 lists Q4713126 as its child. Merging them would fuse father and son.
    #     Not a tradition join: Macedonian on all three sides.
    #
    #     Measured: the three form a CLOSED loop with nothing above it. Q73824's entire
    #     ancestor set is {Q73824, Q135467, Q73925} -- the cycle itself -- and the review
    #     already records the component as not reaching Aster. After the cut Q73824 has 0
    #     ancestors, Q135467 has 1 and Q73925 has 2, all real. Every one of the 29,424
    #     records below loses at most those three phantom ancestors and no chain upward,
    #     because there is no chain upward to lose.
    #
    # (b) Q29144 -> Q29148, THE KAYANID LOOP, decided by the Bundahishn, chapter XXXI.
    #     Q29144 is labelled "kay uyarsh Raja Iran" with the alias "kay manush Raja Iran",
    #     and that conflation is the whole defect. The text names two different men:
    #
    #       XXXI.25  "By Kavad was Kay Apiveh begotten; by Kay Apiveh were Kay Arsh,
    #                 Kay Vyarsh, Kay Pisan, and Kay Kaus begotten"      -- four BROTHERS
    #       XXXI.28  "Lohrasp was son of Auzav, son of Manush, son of Kay Pisin, son of
    #                 Kay Apiveh, son of Kay Kobad"                      -- a DESCENT
    #
    #     Manush is Kay Pisin's son. Vyarsh is Kay Pisan's brother. The import merged them
    #     into one record, so the same pair of qids carries a parent edge in each
    #     direction and the loop closes. The dump does the identical thing one row over:
    #     Q29140 is "kay kaus" with the alias "kay auzav", merging Kay Kaus (XXXI.25) with
    #     Auzav son of Manush (XXXI.28).
    #
    #     The text refutes exactly one of the two edges. Q29148 -> Q29144 is XXXI.28's
    #     "Manush, son of Kay Pisin" and stays. Q29144 -> Q29148 is refuted twice over --
    #     XXXI.25 makes them brothers, XXXI.28 makes Pisin the elder -- and goes.
    #
    #     Why not DEDUPE: Pisan and Manush are two men in the source. Why not UNMERGE:
    #     unmerging Q29144 into Vyarsh and Manush is the *right* full repair and is
    #     written up for Emma in queue.md; it needs a name, a new record and a decision
    #     about Q29140's identical conflation, none of which this loop cut requires.
    #     Not a tradition join: Iranian on both sides.
    #
    #     THE CUT ALONE WOULD AMPUTATE, so it is not applied alone. Q29148's only parent
    #     claim is the false edge, so cutting takes Kay Pisan from 341 ancestors to 0 and
    #     detaches him from Aster. XXXI.25 gives his real father in the same sentence that
    #     refutes the edge -- Kay Apiveh, already in the dump as Q29156 with 335 ancestors
    #     reaching Q1 -- so add_bridge_edges.py's "kayanid-pisan" declares Q29156 ->
    #     Q29148 and Pisan lands at 336. Measured over edges.tsv before applying:
    #         Q29148  341 -> 0 (cut alone)  -> 336 (cut + reattach)
    #         Q29144  341 -> 340            Q29156, Q29140, Q29152 unchanged
    #     Run the bridge in the same batch as this cut, never this cut on its own.
    "agathocles-kayanid": [
        ("Q73925", "Q73824", "Alcimachus recorded as the father of Agathocles of Pella, "
                             "who is his grandfather -- the two true edges of that "
                             "descent are already present and stay"),
        ("Q29144", "Q29148", "Manush recorded as the father of Kay Pisan, who is his "
                             "father in Bundahishn XXXI.28 and his brother in XXXI.25 -- "
                             "apply with the kayanid-pisan bridge, never alone"),
    ],
    "nagano-entenca": [
        ("Q18066", "Q32705", "Norinari (d. 1530) recorded as father of Hisanari, who "
                             "died in 1503 and whose headship he inherited -- the true "
                             "edge is the other way and is already present"),
        ("Q124343", "Q119481", "Jussiana (d. 1300) recorded as mother of her own father, "
                               "whose father died in 1173 -- her mother is Sibil.la "
                               "Q124763, and the true edge Q119481 -> Q124343 is already "
                               "present"),
    ],
    # queue.md item 1 (2026-07-31). The edge that closes the 18-record Roman tangle:
    #   Q72434 -> Q73893 -> Q73794 -> Q73692 -> ... -> Q72957 -> Q72801 -> Q72786 -> Q72434
    #
    # Q73893 is Lucius Cornelius Scipio Asiaticus Aemilianus (wd Q7234050), consul 83 BC,
    # an Aemilius by birth -- which is why he is CORRECTLY a child of the Lepidus record.
    # The dump dates him b. 200 / d. 77, stored unsigned; d. 77 BC is right for him.
    #
    # He is recorded as the father of Q73794 Gnaeus Cornelius Scipio, whose son Q73692 is
    # Scipio Barbatus, consul 298 BC, dated 400/300 in the dump. Read the dates as the BC
    # magnitudes they are -- and they must be, since Q72957 and Q72434 in the same chain
    # are stored SIGNED negative, and Q73443's +0211 is exactly Scipio Calvus's death in
    # 211 BC -- and the descent below Q73794 runs cleanly forward:
    #     Q73692 400/300 -> Q73569 306/250 -> Q73443 256/211 -> Q73293 230/171
    #     -> Q73128 205/141 -> Q72957 -182/-132
    # while Q73893 sits at 200/77. His grandson is born some 140-200 years before him.
    #
    # This is the trap the queue item warned about: under a naive AD reading the edge
    # looks fine (200 then 400), which is presumably how it survived. Under the correct
    # BC reading it is impossible. The repeating-cognomen collision -- the ancient
    # Scipiones hung under a 1st-century Scipio because both are "Cornelius Scipio".
    #
    # Why not UNMERGE: Q73893 holds ONE identity, not two. Its parents are the Lepidi, its
    # Wikidata id is the 1st-century Aemilianus, and its other child Q72248 (Cornelius
    # Scipio Salvito, wd Q1269233, Caesar's associate at Thapsus in 46 BC) is 1st-century
    # too. Only the Q73794 attachment is out of place. Q73794 likewise carries no second
    # identity -- its only claims are this false parentage and its son.
    # Why not DEDUPE: Q73794's wd Q128598522 is unique here; it duplicates nothing.
    # Not a tradition join: both sides are Roman.
    #
    # BOTH parents are cut, not just the one that closes the loop. Q99342 Aemilia Paula is
    # Q73893's wife and Q73794's recorded mother, and her only other child is the
    # 1st-century Salvito. There is no reading where she mothers a 4th-century man.
    # Cutting only the father -- which alone would break the tangle, since Q99342 is not in
    # it -- would leave an equally impossible claim standing just because no cycle ran
    # through it.
    #
    # Q73794 is left parentless, which is honest: the dump does not record Barbatus's
    # grandfather, and inventing one is not this tool's business. His descent below is
    # untouched.
    # REVERTED 2026-07-31, same day, by Emma's question: "no risk of load bearing ancestor
    # gateways being lost?" There was, and I had not checked.
    #
    # The chronology above is still correct -- that edge cannot be right. But it was the
    # SOLE upward gateway for the entire Scipio line. Measured after the fact:
    #
    #     Q73794 Gnaeus Cornelius Scipio   263 ancestors deep  ->  0
    #     Q73692 Scipio Barbatus           264                 ->  1
    #     Q73299 Scipio Africanus          267                 ->  4
    #     Q72957 Nasica Serapio            269                 ->  12
    #
    # and the 263-link chain ran all the way up to Q1 Aster, the root of the genealogy.
    # Cutting it made Scipio Africanus, Barbatus, the Nasicae and Cornelia a rootless
    # island. cycle_policy.md is explicit about this exact situation: "If a cycle can only
    # be broken by cutting such a join, that is a signal the real defect is elsewhere in
    # the loop -- go find it." I broke the cycle instead of finding the defect.
    #
    # What I got wrong methodologically: I verified with compare_tangles.py, which measures
    # WIDTH -- how many records sit in a tangle. It reported 18 records freed and 0 tangles
    # introduced, which looked like a clean win. Load-bearing here means DEPTH, upward, and
    # nothing I ran measured that. A repair can be green on every existing gate and still
    # amputate 263 generations.
    #
    # Kept, disabled, as the record. The real work is queue item 1: find which edge in
    # Q73794 -> ... -> Q72957 -> Q72801 -> Q72786 -> Q72615 -> Q72434 -> Q73893 is the
    # false one, so the loop opens without detaching the Scipiones from Aster.
    "scipio-REVERTED-do-not-apply": [],

    # ================================================================================
    # THE INVERSION CLASS. queue.md item 5. Emma ruled on 2026-08-02, asked directly:
    # "may these records lose their route to Aster?" -- YES, cut all five.
    #
    # THE SHAPE, identical in all five: the head of a lineage is recorded as the CHILD of
    # one of its own descendants. That false edge is also the head's only route upward, so
    # the thousands of ancestors it shows are its own descendant's ancestors flowing
    # backwards. Breaking the loop necessarily returns the head to its true, shallow
    # ancestry and drops it off Q1 Aster. That consequence is the whole of what needed a
    # ruling -- the chronology was never in doubt in any of the five.
    #
    # This is NOT the case cycle_policy.md warns about, and the distinction matters. There
    # the rule is: if a loop can only be broken by cutting a gateway, the defect is
    # elsewhere -- go find it. Here we went and found it, in all five, and the gateway IS
    # the defect. The ancestry being lost was never real; it was inherited upward through an
    # edge that cannot be true. No reattachment exists in any of the five: Wikidata
    # dead-ends too (Carloman b. 550 has no father, Q1306266 consul 302 BC has no father).
    #
    # Each edge below was checked against Wikidata one record at a time, and in every case
    # the OTHER edges of the loop are the correct descent -- Pepin of Landen -> Begga ->
    # Pepin of Herstal -> Charles Martel is the Carolingian pedigree itself. There is no
    # other edge to blame.
    "inversion-class": [
        # Tangle 9. Martel b. 688; Pepin of Landen d. 640. Wikidata lists nine children for
        # Charles Martel and Pepin of Landen is not among them -- he is Martel's
        # great-grandfather, through Begga and Pepin of Herstal, which the loop's other
        # three edges record correctly.
        ("Q113081", "Q111318",
         "Charles Martel b. 688 cannot be the father of Pepin of Landen d. 640 -- he is "
         "Pepin's great-grandson via Begga and Pepin of Herstal, which the rest of the "
         "loop records correctly"),
        # Tangle 10. Gandalf b. 705; Olaf's mother Alfhild b. 780 is herself Gandalf's
        # great-granddaughter. And the man's own patronymic settles it: Gandalf
        # ALFGEIRSSON's father is Alfgeir, not Olaf.
        ("Q118732", "Q136091",
         "Olaf cannot be the father of Gandalf b. 705 -- Olaf's own mother Alfhild b. 780 "
         "is Gandalf's great-granddaughter, and the patronymic Alfgeirsson names his "
         "father as Alfgeir"),
        # Tangle 11. The Welsh patronymics ARE the pedigree, and the loop's other three
        # edges are spelled out by them, making Dyddgu Morfudd's great-grandmother. The
        # mother-claim inverts three generations. Dyddgu's real father Cadwgan Fottwm (wd
        # Q112531567) was absent from the dump and was created by
        # `add_bridge_edges.py welsh-cadwgan-fottwm` on 2026-08-01, so she now has a real
        # 453-deep Welsh line where the false claim was previously her only route upward.
        ("Q144542", "Q148522",
         "Morfudd cannot be Dyddgu's mother -- the loop's other three edges are spelled "
         "out by the patronymics and make Dyddgu Morfudd's great-grandmother; Dyddgu's "
         "real father Cadwgan Fottwm was added by add_bridge_edges.py"),
        # Tangle 8. A Cotys/Rhescuporis name collision between two dynasties: Wikidata's own
        # description makes Q2713411 "Sapean King of Thrace, 48-41 BC" while his recorded
        # father Q2711623 is a "1st century AD Bosporan king" -- the son predates the
        # father by a century.
        ("Q138365", "Q148022",
         "Tiberius Julius Cotys I, a 1st-century AD Bosporan king, cannot be the father of "
         "Rhescuporis I, Sapean king of Thrace 48-41 BC -- a Cotys/Rhescuporis name "
         "collision between two dynasties"),
        # Tangle 12, AND THIS ONE IS AN UNMERGE, not a plain cut -- it differs in kind from
        # the other four and both removals are the two halves of one split.
        #
        # Q73119 carries TWO Wikidata ids and is two men four generations apart:
        #   Q433463    M. Livius Drusus the Younger, tribune 91 BC
        #   Q20005554  M. Livius Drusus Aemilianus, "father of the general Gaius Livius
        #              Drusus", sons of Q703448 Salinator
        # That is why the loop closes: the tribune is his own great-grandfather's father,
        # because one record is playing both parts.
        #
        # The other half ALREADY EXISTS and needs no naming: Q148206 is an empty shell
        # already declared a father of Q72951 Gaius (from Gaius's side only, which is why
        # it never got its own claims). So the unmerge is exactly two removals and Gaius
        # keeps a father -- verified before applying: Q72951 P47 = [Q73119, Q148206].
        ("Q73119", "Q72951",
         "UNMERGE half 1 of 2: Q73119 is a merge of the tribune (wd Q433463) and Drusus "
         "Aemilianus (wd Q20005554); the child-claim on Gaius belongs to Aemilianus, whose "
         "slot Q148206 already exists and is already Gaius's other recorded father"),
        ("Q151476", "Q73119",
         "UNMERGE half 2 of 2: the father-claim from Salinator belongs to Aemilianus "
         "(Q148206), not to the tribune; the tribune keeps his real 920-deep ancestry "
         "through his mother Q72801 Cornelia"),
    ],
}


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def vals(d, pid):
    # Tolerates a missing record. A qid with no file lists nothing, so the empty answer is
    # the correct one rather than a crash. Guarding at each call site instead was the
    # wrong shape: on 2026-08-01 this cut set hit the same NoneType three separate times
    # -- plan, apply, then verify -- and the second crash landed AFTER the first edge had
    # already been written to disk. One guard at the root beats three at the edges.
    if d is None:
        return []
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.append(v["id"])
    return out


def label(q):
    d = load(q)
    if not d:
        return "?"
    v = (d.get("labels") or {}).get("en")
    return (v.get("value") if isinstance(v, dict) else v) or "(no label)"


def claimants():
    out = collections.defaultdict(set)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                out[r["to_qid"]].add(r["from_qid"])
    return out


def aliases():
    # from_qid -> to_qid. A file whose "id" differs from its filename is a silent redirect,
    # and extract_genealogy.py canonicalizes BOTH ENDPOINTS of every edge through this map
    # before writing edges.tsv. So a claim citing an alias builds exactly the same edge as
    # one citing the canonical qid.
    out = {}
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                out[r["from_qid"]] = r["to_qid"]
    return out


ALIAS = {}


def canon(q):
    return ALIAS.get(q, q)


def cvals(d, pid):
    # vals() through the alias map. THE ONE THAT MATTERS FOR CUTS: matching cited qids
    # literally is how `theban-senebhenaf` reported success on 2026-08-01 while leaving its
    # edge alive for a day. Q85514 listed BOTH Q85498 and Q85518 as children; Q85518 is a
    # silent redirect to Q85498, i.e. the same person under a duplicate qid. Removing the
    # literal Q85498 left Q85518 behind, the extractor canonicalized it straight back to
    # Q85514 -> Q85498, and the tool's own verify pass -- also literal -- said the edge was
    # gone from both sides. Compare canonically or the check cannot see the edge it built.
    return [canon(v) for v in vals(d, pid)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    if "--list" in sys.argv or not args:
        print("cut sets:")
        for k, v in CUTS.items():
            print(f"  {k:10s} {len(v)} edge(s)")
        return 0
    name = args[0]
    if name == "selfloops":
        # Data-driven, from what the extractor recorded rather than a hand-kept list.
        #
        # A record that is its own parent is an error under any reading -- there is no
        # tradition in which someone fathers himself -- so this needs no adjudication, and
        # unlike every other cut it carries NO risk of severing a join: a self-edge links a
        # node to itself, so it can never be the only link between two traditions.
        # extract_genealogy.py already excludes self-edges from the graph, so removing them
        # cannot change edges.tsv at all. This only makes the item files agree with the
        # graph that was always computed from them, and lets invariant I2 go green
        # honestly instead of vacuously.
        path = ROOT / "wikibase" / "analysis" / "qa_self_edges.tsv"
        if not path.exists():
            print("qa_self_edges.tsv missing -- run extract_genealogy.py first")
            return 1
        with open(path, encoding="utf-8") as f:
            todo = [r["qid"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if r.get("qid")]
        cuts = [(q, q, "record lists itself as its own parent/child") for q in todo]
    elif name == "orphan-refs":
        # Data-driven, from edge_symmetry.py's classification (queue.md item 4).
        #
        # Every edge here has an endpoint with no item file, no shadow claiming the qid
        # and no persons.tsv row, AND edges in only one direction -- so nothing is
        # connected through it and cutting can sever no chain. That last condition is the
        # whole of the safety argument and it is not optional; see the ORPHAN-vs-GAP note
        # below.
        #
        # The classification is only trustworthy because the endpoints are canonicalised
        # through redirects.tsv first. Without that step it reported 897 of these, and
        # spot-checking found the "missing" records were ordinary shadow files whose
        # internal id differs from their filename -- Q107385 is "Fatima bint Amr
        # al-Makhzumi", not a hole in the graph. The canonical figure is 233 edges over 13
        # genuinely absent endpoints. Re-run edge_symmetry.py if the dump has moved.
        path = ROOT / "wikibase" / "analysis" / "edge_symmetry_classified.tsv"
        if not path.exists():
            print("edge_symmetry_classified.tsv missing -- run edge_symmetry.py first")
            return 1
        cuts = []
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                # ORPHAN only. A GAP endpoint has no file but IS referenced from both
                # directions -- a real person whose item file is absent, with the family
                # recorded around them. Cutting those severs a real chain: on 2026-08-01
                # this set was run treating GAP and ORPHAN alike, 219 of the 233 edges ran
                # through a gap, and compare_depth failed at -10 levels with Melaneus and
                # Aeneus cut off from the Titan line. Reverted. The repair for a GAP is to
                # CREATE the record, not to delete its edges.
                if r.get("verdict") != "ORPHAN":
                    continue
                gone = [q for q, k in ((r["parent"], r["parent_kind"]),
                                       (r["child"], r["child_kind"])) if k == "missing"]
                cuts.append((r["parent"], r["child"],
                             f"{', '.join(gone)} does not exist -- {r['side']} edge "
                             f"pointing at nothing"))
    elif name not in CUTS:
        print(f"unknown cut set {name!r}; try --list")
        return 1
    else:
        cuts = CUTS[name]
    fam = claimants()
    ALIAS.update(aliases())

    plan = []
    for parent, child, why in cuts:
        dp, dc = load(parent), load(child)
        # A DANGLING endpoint has no file on either side of the edge. Refusing the whole
        # cut because one side does not exist was the wrong guard: the claim still sits on
        # the side that DOES exist, pointing at nothing, and that claim is exactly what
        # needs removing. Cleopatra III (Q78719) lists Q78402 as both her mother and her
        # child, and Q78402 has no file, no shadow claiming the qid, and no persons.tsv
        # row -- one of the 138 dangling endpoints. Abort only if NEITHER side exists,
        # which would leave nothing to edit.
        if dp is None and dc is None:
            print(f"ABORT: neither {parent} nor {child} has an item file -- nothing to edit")
            return 1
        if dp is None or dc is None:
            missing = parent if dp is None else child
            print(f"  note: {missing} has no item file (dangling endpoint) -- removing the "
                  f"claim from the side that exists")
        on_parent = dp is not None and canon(child) in cvals(dp, P_CHILD)
        on_child = ([p for p in (P_FATHER, P_MOTHER) if canon(parent) in cvals(dc, p)]
                    if dc is not None else [])
        if not on_parent and not on_child:
            print(f"  {parent} -> {child}: already absent on both sides, nothing to do")
            continue
        plan.append((parent, child, why, on_parent, on_child))

    print(f"cut set {name!r}: {len(plan)} edge(s)\n")
    for parent, child, why, on_parent, on_child in plan:
        print(f"  {parent} ({label(parent)[:34]}) -> {child} ({label(child)[:34]})")
        print(f"        {why}")
        print(f"        declared on parent {P_CHILD}: {on_parent}; "
              f"on child: {on_child or 'no'}")
        n = len({parent} | fam.get(parent, set())) + len({child} | fam.get(child, set()))
        print(f"        {n} file(s) will be rewritten")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0

    print("\napplying...")
    removed = 0
    dirty = set()
    # Both sides are skipped when their file does not exist. The plan phase already
    # allows a dangling endpoint through -- guarding only there and not here is what made
    # this crash mid-run on 2026-08-01, after it had already written the first cut.
    for parent, child, _, _, _ in plan:
        dp = load(parent)
        if dp is not None:
            cl = (dp.get("claims") or {})
            if P_CHILD in cl:
                keep = [c for c in cl[P_CHILD]
                        if canon(((c.get("mainsnak") or {}).get("datavalue") or {})
                                 .get("value", {}).get("id")) != canon(child)]
                removed += len(cl[P_CHILD]) - len(keep)
                if keep:
                    cl[P_CHILD] = keep
                else:
                    del cl[P_CHILD]
            write_family(parent, dp, fam)
            dirty.add(parent)

        dc = load(child)
        if dc is not None:
            cl = (dc.get("claims") or {})
            for p in (P_FATHER, P_MOTHER):
                if p in cl:
                    keep = [c for c in cl[p]
                            if canon(((c.get("mainsnak") or {}).get("datavalue") or {})
                                     .get("value", {}).get("id")) != canon(parent)]
                    removed += len(cl[p]) - len(keep)
                    if keep:
                        cl[p] = keep
                    else:
                        del cl[p]
            write_family(child, dc, fam)
            dirty.add(child)

    print(f"removed {removed} claim(s) across {len(dirty)} record(s)")

    print("\nverifying...")
    ok = True
    for parent, child, _, _, _ in plan:
        dp, dc = load(parent), load(child)
        if canon(child) in cvals(dp, P_CHILD):
            print(f"  FAIL {parent} still lists {child} as a child")
            ok = False
        for p in (P_FATHER, P_MOTHER):
            if canon(parent) in cvals(dc, p):
                print(f"  FAIL {child} still lists {parent} as {p}")
                ok = False
    # The alias endpoints themselves. Cutting P -> C removes the claim from C's file, but
    # C's duplicate qids are separate FILES with their own claims, and an alias of C citing
    # P as its father rebuilds the identical edge after canonicalization.
    for parent, child, _, _, _ in plan:
        for side, other in ((child, parent), (parent, child)):
            for alt in sorted({a for a, t in ALIAS.items() if t == canon(side)}):
                d = load(alt)
                if d is None or (d.get("id") or alt) == side:
                    continue
                for p in (P_FATHER, P_MOTHER, P_CHILD):
                    if canon(other) in cvals(d, p):
                        print(f"  FAIL alias {alt} of {side} still lists {other} in {p}")
                        ok = False
    for q in sorted(dirty):
        ref = None
        for f in sorted({q} | fam.get(q, set())):
            d = load(f)
            if d is None or (d.get("id") or f) != q:
                continue
            cur = {p: sorted(vals(d, p)) for p in (P_FATHER, P_MOTHER, P_CHILD)}
            if ref is None:
                ref = cur
            elif cur != ref:
                print(f"  FAIL {q}: shadow {f} disagrees after the cut")
                ok = False
    print("edges gone from both sides, all claimants agree" if ok else "PROBLEMS ABOVE")
    print("\nRe-run extract_genealogy.py, dump_qa_errors.py, compare_tangles.py.")
    return 0 if ok else 1


def write_family(q, data, fam):
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for f in sorted({q} | fam.get(q, set())):
        fp = ITEMS / f"{f}.json"
        if fp.exists():
            fp.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
