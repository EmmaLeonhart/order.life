"""Dedupe a named cluster of parallel-import duplicates.

This is the generalised form of apply_cato_cluster_merge.py, which was written for one
cluster and is left in place as the record of what ran on 2026-07-31. Everything learned
there is encoded here as rules the tool enforces rather than as prose someone has to
remember.

    python wiki-scripts/merge_cluster.py porcia           # dry run, prints the plan
    python wiki-scripts/merge_cluster.py porcia --write   # apply
    python wiki-scripts/merge_cluster.py --list

THE TWO RULES THIS ENFORCES

1. **No file may still claim the loser's qid afterwards.** 39,527 qids in this dump are
   claimed by more than one file and extract_genealogy.py keeps only the numerically-lowest.
   Merging B into A rewrites B.json to id=A, which VACATES qid B -- and if any file still
   claims B, it wins the vacancy and injects its own claims. That is how the phantom
   Q148133 <-> Q73167 2-cycle appeared out of a graph that never contained the edge.

   This was first written as an input-side refusal -- "the loser must have no shadows" --
   which was the wrong guard twice over. It is a proxy for the real invariant, and a
   redundant one, because the tool already rewrites every shadow of the loser in the same
   pass. It also forbade safe merges outright: Q72434/Q72514 (Marcus Aemilius Lepidus, both
   carrying wd Q435329) have shadows on BOTH sides and could not be merged in either
   direction. Replaced 2026-07-31 with the outcome-side assertion below, which is strictly
   stronger: after the merge, no file anywhere may still resolve to the loser's qid. A
   loser shadow that cannot be rewritten is still a hard abort, but now it is checked
   against what actually happened rather than guessed from the inputs.

2. **Rewrite every file claiming either qid, not just the canonical one.** An edit to the
   canonical file alone is silently reverted the moment it stops being the lowest
   claimant. check_staged_shadows.py gates this at commit time; the tool does it up front.

MECHANISM, and it is non-destructive: union the loser's genealogical claims into the
survivor, rewriting any reference that points at a record being merged away, then rewrite
the loser's file and every shadow of both sides as a copy of the survivor. Nothing is
deleted and git reverts it cleanly.

WHAT IT DOES NOT DO: third-party records that cite a loser qid are left alone, because
extract_genealogy.py canonicalises every edge through the redirect map. This matches
apply_dup_merge.py. It means item files keep stale-looking references -- Q72624 "Livia"
still lists Q141517 and Q141438 as spouse and child after the Cato merge -- which is
harmless for the graph but surprising to read.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

GEN_PROPS = ("P20", "P42", "P47", "P48", "P61")  # child, spouse, father, mother, wikidata

CLUSTERS = {
    # queue.md item 1 (2026-07-31): the residue the Porcii Catones dedupe deliberately
    # left standing. Cato the Younger came out of that merge with six children because
    # the two import branches contributed overlapping daughters. Resolved here.
    #
    # Q78063 "Porcia Catonis" and Q144042 "Porcia" are the same woman:
    #   - Q144042 carries wd Q255448, whose own Wikidata name is "Porcia Catonis" --
    #     letter for letter Q78063's label.
    #   - both are daughters of Cato the Younger by an Atilia record.
    #   - both are spouses of THE SAME record, Q78066 Marcus Calpurnius Bibulus
    #     (wd Q316775), which already lists both of them as wives -- the duplicate
    #     signature, stated by the dump itself.
    #   - both are the mother of a son of Q78066.
    #
    # That forces the two records above her, or the survivor ends up with two duplicate
    # mothers and Cato the Younger with two duplicate wives:
    #   - Q72493 / Q144102 "Atilia", both wives of Cato the Younger and mothers of the
    #     Porcia pair; Q144102 carries wd Q2334126 ("Atilia").
    #   - Q72681 "Gaius Atilius" / Q144174 "Atilius Serranus", both the father of an
    #     Atilia who married Cato the Younger; Q144174 carries wd Q12275873, whose
    #     Wikidata name is "G. Atilius Serranus" -- the same man Q72681 is named for.
    #
    # Deliberately NOT merged: Q141439 (wd Q18280006) and Q141441 (wd Q94959905) are also
    # Porcia daughters of Cato the Younger, but by Marcia (Q139581), a different wife, and
    # they carry two distinct Wikidata items. They are not this Porcia and not obviously
    # each other. Likewise Q77899 (wd Q3655959, Lucius Calpurnius Bibulus) and Q141508
    # (wd Q104224002, "Calpurnius Bibulus") are both sons of Q78066 who land on the merged
    # Porcia; they are plausibly one man but carry different Wikidata items, so merging
    # them would be a guess.
    # queue.md item 1 (2026-07-31). qa_tangle_repairs.md ranked this the top DEDUPE:
    # Q72434 and Q72514 both carry wd Q435329 (Marcus Aemilius Lepidus, cos. 78 BC), share
    # the spouse Q72517 Appuleia, and share four of their children outright. Q72434 also
    # holds Q72251 and the birth/death dates -120/-77, which match the consul of 78.
    #
    # This is the pair that exposed the old input-side guard as wrong: BOTH sides have
    # shadow files (Q72434 -> Q87226, Q185444; Q72514 -> Q87280), so no direction was
    # permitted, even though repointing makes either direction safe. Survivor is the lower
    # QID, which also carries strictly more claims.
    #
    # NOT a cascade like the Cato cluster: Q72514's apparently-extra child Q141448 is
    # already a shadow file of Q73893, so it canonicalises to a child Q72434 already has.
    # The survivor gains nothing and simply absorbs a duplicate node.
    # queue.md item 1 (2026-07-31), found while looking for the real defect in the Scipio
    # loop. Q72801 Cornelia has THREE fathers -- Q72957 Scipio Nasica Serapio, Q73425 and
    # Q73017 -- and two of the three are the same man:
    #
    #   Q73425  "Pacuvius Calavius"            sp=[Q73428]         ch=[Q72801]
    #   Q73017  "Pacuvius Calavius  Calavius"  sp=[Q73014,Q73428]  ch=[Q72870,Q72801,Q78746]
    #
    # Same name with the cognomen doubled -- the exact artefact cycle_policy.md names
    # ("Diogo Afonso Afonso de Aguiar, a doubled name") -- married to the same woman
    # Q73428 Claudia Pulcher, and both recorded as the father of the same daughter. Neither
    # carries a Wikidata id, so this is decided on position and name, the same standard used
    # for the Licinia and Salonia pairs in the Porcii Catones cluster.
    #
    # Survivor is Q73017: lower QID, and it holds three children and a second spouse that
    # Q73425 does not. Its label carries the doubled cognomen and is corrected separately
    # after the merge, with the doubled form kept as an alias.
    #
    # This does NOT break the Scipio loop and is not meant to -- the loop runs through
    # Q72957 -> Q72801, not through Calavius. It removes one of Cornelia's three fathers,
    # leaving the sharp question: Scipio Nasica Serapio or Pacuvius Calavius. That one is
    # Emma's.
    "calavius": [
        ("Q73017", "Q73425", "Pacuvius Calavius -- same name with the cognomen doubled, "
                             "same wife Q73428, same daughter Q72801"),
    ],
    "lepidi": [
        ("Q72434", "Q72514", "Marcus Aemilius Lepidus cos. 78 BC -- both carry wd Q435329, "
                             "both married to Q72517 Appuleia, four shared children"),
    ],
    # queue.md item 2 (2026-07-31). The generation directly above the "lepidi" merge above,
    # and it only became legible once that one landed.
    #
    #   Q72615  "Quintus Aemilius Lepidus"  f=[Q72786]           m=Q72789  sp=Q72618  ch=[Q72434]
    #   Q72693  "Quintus Aemilius Lepidus"  f=[Q72786, Q144279]                       ch=[Q72514]
    #
    # Q72514 canonicalises to Q72434, so both men are the father of ONE man -- and Q72434
    # lists both of them as its fathers, which is the dump stating the duplication about
    # itself, the same signature that decided the Porcia pair (Q78066 listing both women as
    # wives). A man has one father, so these two records are one man. They also share their
    # offices (P39 Q153801/Q153802), sex, and the same P94 arms filename.
    #
    # Q72693 carries wd Q11944252 and Q72615 carries none: a gap, not a conflict. Survivor
    # is Q72615 by the lower-QID convention; it also holds the mother and the spouse.
    #
    # WHAT THIS DOES NOT SETTLE, and deliberately does not guess at. Q72693 has TWO fathers,
    # both labelled "Marcus Aemilius Lepidus" -- Q72786 and Q144279 -- so the survivor
    # inherits both. That conflict is not created here, it is pre-existing on Q72693 and both
    # edges are already in edges.tsv; the merge only moves it onto one record where it is
    # visible. It cannot be settled without deciding queue item 1, because Q144279's other
    # child is Q73011, which is one of the three fathers Q72786 claims. Merging Q72786 and
    # Q144279 would therefore close a 2-cycle. Which of those two records is real is Roman
    # prosopography and Emma's call.
    #
    # The merge is correct under EITHER resolution: whichever father record survives, the
    # two sons are still one man. Net effect on multi-parent: Q72434 drops from two fathers
    # to one. Checked before applying -- Q144279 is not a descendant of Q72615 (whose only
    # child is Q72434, and Q144279 is not below that), so the new Q144279 -> Q72615 edge
    # introduces no cycle.
    "quintus-lepidus": [
        ("Q72615", "Q72693", "Quintus Aemilius Lepidus -- both sons of Q72786 and both "
                             "fathers of Q72434, which lists both of them as its fathers"),
    ],
    # queue.md item 2 (2026-07-31). The first cluster found by the NEW label-plus-
    # corroboration detector rather than by hand -- propose_tangle_repairs.py flagged it
    # DEDUPE because Q153390 names two identically-labelled fathers. Neither side of either
    # pair carries a Wikidata id, so the old shared-id detector could never have seen it.
    #
    # It is a two-level cascade and MUST be merged as one, or the survivor ends up with two
    # duplicate fathers -- the same trap the Porcii Catones cluster documented:
    #
    #   Q1968   "Prachinbarhi"          f=Q1978 m=Q49767              ch=[Q1955]
    #   Q49707  "Prachinbarhi"          f=Q1978 m=Q49767  sp=Q49703   ch=[Q49634]
    #   Q1955   "Prachetas (10 sons)"   f=Q1968                       ch=[Q153390]
    #   Q49634  "Prachetas (10 sons)"   f=Q49707 m=Q49703 sp=Q49638   ch=[Q153390]
    #
    # The upper pair is decided on more than a shared label: they share BOTH parents BY
    # IDENTITY (Q1978 Havirdhana, Q49767 Havirdhani), not merely by name, and each fathers a
    # record labelled "Prachetas (10 sons)". The lower pair is the decisive shared-child
    # signature -- Q153390 Daksha lists both of them as its fathers, and a man has one
    # father.
    #
    # Survivors are the lower QIDs by convention; the higher ones hold the spouse and mother
    # claims, which the union carries over. Q49703 Shatadruti is spouse of the Prachinbarhi
    # survivor and mother of the Prachetas survivor, which is consistent and stays.
    "prachetas": [
        ("Q1968", "Q49707", "Prachinbarhi -- same father Q1978 and same mother Q49767 by "
                            "identity, each the father of a 'Prachetas (10 sons)'"),
        ("Q1955", "Q49634", "Prachetas (10 sons) -- Q153390 Daksha lists both as its "
                            "fathers"),
    ],
    # queue.md item 2 (2026-07-31), also from the new detector. Same shape as the
    # Q72615/Q72693 pair merged earlier today, and missed for the same reason: only one
    # side carries a Wikidata id.
    #
    #   Q72984   "Quintus Caecilius Metellus"  f=Q73146  ch=[Q72834, Q72858]  wd=none
    #   Q144060  "Quintus Caecilius Metellus"  f=Q73146  ch=[Q72858]          wd=Q929498
    #
    # Same label, SAME father Q73146 by identity, and both are recorded as the father of
    # Q72858. Survivor is Q72984 (lower QID, and it holds the extra child Q72834); the union
    # carries Q144060's Wikidata id and its P56/P57 birth and death dates onto it, which is
    # exactly the property loss the 2026-07-31 backfill was written to prevent.
    "metellus": [
        ("Q72984", "Q144060", "Quintus Caecilius Metellus -- same father Q73146, both "
                              "recorded as father of Q72858; Q144060 carries wd Q929498"),
    ],
    # M3 from wikibase/analysis/adnan_merge_proposed.md. DECIDED BY EMMA 2026-07-31:
    # "You merge them lol" -- i.e. merge all three Adnan records rather than pick a
    # survivor and drop the other two. The report itself recommended choosing one, and
    # asked for the R1 decision first; R1 was decided 2026-07-30 (the Emesene route is
    # intentional and the splice stays), and Emma's answer supersedes the choose-one
    # framing entirely.
    #
    #   Q65555   "Adnaan Bin Imaam 'Udd"  3 parents, 9 children, 10 anc, 8,527 desc
    #   Q86433   "Adnan Banu Ismail"      1 parent,  1 child,  434 anc, 32,976 desc
    #   Q111364  "Adnan"                  no parents, 2 children, wd Q22338875
    #
    # Each was the right answer by a different measure -- identifier, ancestry, posterity --
    # which is exactly why the report could not choose. Merging keeps all three measures.
    # Survivor Q65555 by the lower-QID convention; it is also the record Muhammad's line
    # actually reaches.
    #
    # TWO CORRECTIONS TO THE REPORT, found while checking rather than assumed from it:
    #   - it says Q65555 "reaches nothing upward". It has three parents and 10 ancestors.
    #   - it says Q111364 has "no parents, two children"; that part holds.
    #
    # CYCLE RISK CHECKED BEFORE APPLYING, because Q86433 routes UP into the Emesene
    # material while Q65555 runs DOWN to Muhammad: no ancestor set of any of the three
    # intersects any other's descendant set, so the merge closes no loop. Verified against
    # edges.tsv, not reasoned from the prose.
    #
    # RESIDUE, not fixed here and not hidden: the survivor ends with FOUR parents
    # (Q66382, Q66385, Q66394, Q86503). Q66385 "Imaam 'Udd" and Q66394 "Udd son of Umaisi"
    # look like the same man, which the report's own "'Udd/Humaisi tangle" note flags as
    # untraced. That is a separate dedupe and is left standing deliberately -- it does not
    # increase the count of records with >2 parents, since Q65555 already had three.
    "adnan": [
        ("Q65555", "Q86433", "Adnan -- Banu Ismail branch; contributes the parent edge and "
                             "the 434-ancestor route toward Abraham"),
        ("Q65555", "Q111364", "Adnan -- carries wd Q22338875, the only identifier of the "
                              "three"),
    ],
    # queue.md item 2 (2026-08-01). The defect inside the 72-record Constantius tangle --
    # the largest in the dump -- found by cheapest_cycle_break.py rather than by guessing.
    #
    #   Q64582   "Domitia Lucilla Minor"      f=Q65519 m=Q65552  wd=none        3 children
    #   Q139826  "Calvisia Domitia Lucilla"   f=Q65519 m=Q65552  wd=Q1815905    2 children
    #
    # Both are recorded as the MOTHER of Q63780 Marcus Aurelius, and both have the SAME
    # father and SAME mother BY IDENTITY. Two women with identical parents cannot both be
    # one man's mother -- that is the dump stating the duplication about itself, the same
    # signature that decided Q72615/Q72693 and the Porcia pair. Q139826's wd Q1815905 is
    # "Domitia Lucilla", which is letter-for-letter what Q64582 is labelled.
    #
    # Survivor Q64582 by the lower-QID convention; the union carries Q139826's Wikidata id.
    #
    # NEITHER EXISTING DETECTOR COULD SEE THIS. The shared-Wikidata-id signal needs both
    # sides to carry an id and only one does. The label signals require the labels to
    # match, and "Domitia Lucilla Minor" does not normalise to "Calvisia Domitia Lucilla".
    # What identifies it is purely structural: a same-ROLE parent collision (two P48
    # mothers of one child) plus identical parentage. That signal is written up as the next
    # queue item.
    #
    # WHY THIS AND NOT A CUT: cheapest_cycle_break.py costed all 29 edges of the cycle.
    # Every chronologically-suspect edge in the Licinius stretch costs 19,700 records their
    # ancestry (worst -358); this edge costs ZERO, because the duplicate provides a
    # parallel path. Cheap AND wrong is the combination that makes a repair safe.
    "domitia-lucilla": [
        ("Q64582", "Q139826", "Domitia Lucilla Minor -- same father Q65519 and same mother "
                              "Q65552 by identity, and both are recorded as the mother of "
                              "Q63780 Marcus Aurelius; Q139826 carries wd Q1815905"),
    ],
    # queue.md item 2 (2026-08-01). The six PHANTOM-PARENT hits from the same-role signal.
    #
    # Each loser is an empty SHELL: no label, no description, and exactly one claim type
    # (P39, with the same two values and byte-identical hashes across all six). They carry
    # no genealogical claim of their own -- they appear in edges.tsv only because other
    # records name them in P20, which is the one-sided-edge defect of item 4. Every one of
    # them sits in a tangle and is recorded in the SAME parental role as a real person for
    # the same child.
    #
    # VERIFIED BEFORE MERGING, and the first test I wrote was wrong. "Parents identical"
    # failed on three of the six. The right test is SUBSET: each shell's parents and
    # children are wholly contained in its real counterpart's, so merging adds no edge and
    # only removes a duplicate node. All six pass that, and the extra parents the real
    # records carry turn out to be OTHER SHELLS -- one import made shells, a second made
    # real records, and the real ones picked up shell-parents on the way.
    #
    # Q52709 is the one with positive identification rather than mere structure: it carries
    # no label but its ALIASES are "kay manush Raja Iran" / "kay uyarsh Raja Iran", and
    # "kay uyarsh Raja Iran" is exactly the label of Q29144. Same person, named.
    #
    # NOT FIXED HERE, and not caused by this: Q29144 and Q29148 are recorded as EACH
    # OTHER'S parent -- a genuine mutual-parenthood 2-cycle among the real Persian records,
    # independent of the shells. wiki-scripts/fix_mutual_parent_pairs.py exists for that
    # shape. Merging the shells does not touch it and does not break it.
    "phantom-shells": [
        ("Q73131", "Q99368", "empty shell in the same mother-role as Cornelia Africana "
                             "Major for Q72957"),
        ("Q73293", "Q99386", "empty shell in the same father-role as Publius Cornelius "
                             "Scipio Nasica for Q73128"),
        ("Q4626", "Q60222", "empty shell in the same mother-role as Zebudah for Q135406"),
        ("Q29144", "Q52709", "shell whose aliases include 'kay uyarsh Raja Iran', which is "
                             "Q29144's label exactly"),
        ("Q29148", "Q52713", "empty shell in the same father-role as kay pisan Raja Iran "
                             "for Q29144"),
        ("Q72798", "Q73284", "empty shell in the same father-role as Marcus Livius Drusus "
                             "for Q72624"),
    ],
    # queue.md item 3 (2026-08-01). The first batch out of qa_same_role_parents.tsv, the
    # graph-wide same-role scan. All three are identical-label pairs with corroboration,
    # each hand-checked against the item files, each outside the areas the queue blocks.
    #
    # DELIBERATELY EXCLUDED from this batch, though they rank as high or higher:
    #   Q2627/Q29967 "Prasusruta, King of Kosala" and the other Ikshvaku pairs -- that IS
    #     the Kosala dedup, which queue.md holds for Emma and which gates the Indian line.
    #   Q64471/Q94808 "Abd Shams ibn Abd Manaf", Q65861/Q94403 "Al-Harith" and the other
    #     Quraysh pairs -- same caution as the 'Udd/Adnan parentage: R1 established this
    #     ancestry as deliberate, and variant source-chains look exactly like duplicates.
    #   Q1683/Q48279 "Gayatri Rajapatni" -- a THREE-level parallel import (Gayatri,
    #     Kertanegara under his regnal title Q48307, and Wisnuwardana Q1699/Q48347). It
    #     needs its own cascade cluster; merging the bottom level alone would leave the
    #     survivor with two fathers.
    #
    # (a) Q336 / Q337 "Maratton". Q337 is a LABELLED SHELL -- its only claims are P39 and
    #     P94, no parents, no children, no spouse. It reaches the graph solely through
    #     Q345 Maratidus naming it as a father, alongside Q336. Merging is purely additive:
    #     the shell contributes nothing and stops being a second father.
    #
    # (b) Q31601 / Q92268 "Isabel de Polanco". SAME father Q92264 and SAME mother Q90177 by
    #     identity, and two children shared by identity (Q32949, Q32953). Q31601 also holds
    #     husbands de Tardajos and de Barrera and children surnamed for each; Q92268 holds
    #     husband Q92710 Francisco de Baeza, and the shared children are the two surnamed
    #     "de Baeza". Successive marriages, one woman, recorded twice.
    #
    # (c) Q50050 / Q167291 "Anna Xylaloe". Same spouse Q46167 Manuel I of Trebizond and
    #     same child Q46179 Andronikos II, both by identity. Q50050 carries wd Q4767629 and
    #     Q167291 carries none -- a gap, not a conflict.
    "same-role-batch-1": [
        ("Q336", "Q337", "Maratton -- Q337 is a labelled shell with no genealogical claim, "
                         "present only as a second father of Q345"),
        ("Q31601", "Q92268", "Isabel de Polanco -- same father Q92264 and mother Q90177 by "
                             "identity, two children shared by identity"),
        ("Q50050", "Q167291", "Anna Xylaloe -- same spouse Q46167 and same child Q46179 by "
                              "identity; Q50050 carries wd Q4767629"),
    ],
    # queue.md item 3 (2026-08-01), batch 2. Seven pairs, each hand-checked and each
    # collapse-checked (no pair is one-way ancestral to the other).
    #
    # (a) THE SEVERAN SUBTREE, imported twice. The Q166xxx block duplicates the
    #     Q4680/Q148xxx/Q151xxx block, and the two converge on the same real children:
    #     Q148329 Julia Soaemias has TWO fathers and TWO mothers, one from each copy, and
    #     Q148331 Severus Alexander is shared by both Julia Avita Mamaeas.
    #
    #       Q4680  / Q166165  Julia Maesa           same father Q64615 Julius Bassianus,
    #                                               same child Q148329, by identity
    #       Q4681  / Q166205  Julia Avita Mamaea    both mothers of Q148331 Severus
    #                                               Alexander, by identity
    #       Q4682  / Q166216  Julius Aurelius Zenobius of Parthia
    #       Q151866/ Q166249  Marcus Julius Gessius Bassianus   (Q151866 wd Q15982235)
    #       Q151865/ Q166250  Theoclia                          (Q151865 wd Q15982251)
    #
    #     The last three share NO relative by identity -- their parents are themselves the
    #     duplicated pair above. That is the parallel-subtree signature: nothing is shared
    #     below, because the whole branch was copied. They are merged in the SAME cluster
    #     so canon() resolves their parents through the Mamaea merge; splitting the cluster
    #     would leave each survivor with two mothers.
    #
    #     RESIDUE, not fixed here: the husbands stay separate and the survivors keep two
    #     fathers each. That is deliberate -- Q4682's two fathers are Q144407 ELAGABALUS
    #     and Q166170 MALCHUS II OF PALMYRA, who are plainly different men, so that is a
    #     wrong-parent-edge and not a duplicate. Q151898/Q166247 share a label and may well
    #     be a pair; Q151864 "Julius Avitus" / Q166158 "Julius Calpurnius Piso" do not.
    #     None of them is decided by structure alone.
    #
    # (b) Q57183 / Q87549 "Ji" -- same father Q87569 and same child Q87535 by identity.
    #     Q87549 additionally holds a mother and a spouse, which the union carries.
    # (c) Q58128 / Q87466 "of Cheng" -- same father Q87474 Chien Kung and same child
    #     Q87460 Marquis Cheng of Cai, by identity. Chinese royal records whose labels are
    #     fragmentary, so the identification rests on the structure, not the name.
    # APPLIED AND REVERTED, then narrowed. The five Severan pairs are all correct
    # duplicates and merging them still FAILED check_invariants: I4 multi-parent children
    # increased 1207 -> 1210, because each survivor inherits BOTH copies' fathers and
    # crosses the >2 threshold:
    #
    #   Q4681  Julia Avita Mamaea  fathers Q151864 "Julius Avitus" + Q166158 "Julius
    #                              Calpurnius Piso" -- different names, undecidable
    #   Q4682  Zenobius            fathers Q144407 ELAGABALUS + Q166170 MALCHUS II OF
    #                              PALMYRA -- plainly different men, so one edge is false
    #   Q151866, Q151865           fathers Q151898 + Q166247, both "Marcus Julius Gessius
    #                              Ma..." -- these two ARE a likely pair and merging them
    #                              would fix both children
    #
    # The merges do not CREATE the contradiction; they reveal one that was hidden by being
    # split across two copies of the subtree. But the gate cannot tell those apart, and
    # resolving Elagabalus-versus-Malchus is Palmyrene prosopography I do not have. The
    # subtree waits on the husband pairs; see queue.md.
    "same-role-batch-2": [
        ("Q4680", "Q166165", "Julia Maesa -- same father Q64615 and same child Q148329 "
                             "Julia Soaemias, by identity. Union gives ONE father, so no "
                             "multi-parent increase"),
        ("Q57183", "Q87549", "Ji -- same father Q87569 and same child Q87535, by identity"),
        ("Q58128", "Q87466", "of Cheng -- same father Q87474 and same child Q87460, by "
                             "identity"),
    ],
    # BLOCKED, and kept here deliberately so the tool can demonstrate that it refuses it.
    # These four are the Severan pairs dropped from same-role-batch-2 after the applied
    # seven failed I4 (multi-parent children 1207 -> 1210). Each is a correct duplicate;
    # each survivor would inherit BOTH copies' fathers and cross the >2-parent threshold.
    #
    #   Q4681  Mamaea    fathers "Julius Avitus" Q151864 + "Julius Calpurnius Piso" Q166158
    #   Q4682  Zenobius  fathers ELAGABALUS Q144407 + MALCHUS II OF PALMYRA Q166170 --
    #                    plainly different men, so one edge is false; undecidable here
    #   Q151866, Q151865 fathers Q151898 + Q166247, both "Marcus Julius Gessius Ma..." --
    #                    those two are probably a pair; merging them FIRST unblocks both
    #
    # Running this cluster prints the I4 warning and --write aborts. That is the intended
    # behaviour and it is what validates the pre-check: the narrowed batch passes, this
    # one is refused.
    "severan-blocked": [
        ("Q4681", "Q166205", "Julia Avita Mamaea -- both mothers of Q148331 Severus "
                             "Alexander; BLOCKED, survivor would have two fathers"),
        ("Q4682", "Q166216", "Julius Aurelius Zenobius -- BLOCKED, fathers Elagabalus and "
                             "Malchus II of Palmyra are different men"),
        ("Q151866", "Q166249", "Marcus Julius Gessius Bassianus -- BLOCKED pending the "
                               "Q151898/Q166247 husband merge"),
        ("Q151865", "Q166250", "Theoclia -- BLOCKED pending the Q151898/Q166247 husband "
                               "merge"),
    ],
    "porcia": [
        ("Q72681", "Q144174", "Gaius Atilius Serranus -- wd Q12275873 is named "
                              "'G. Atilius Serranus'; both are the father of Cato the "
                              "Younger's wife Atilia"),
        ("Q72493", "Q144102", "Atilia -- both wives of Cato the Younger and mothers of "
                              "the Porcia pair below; Q144102 carries wd Q2334126"),
        ("Q78063", "Q144042", "Porcia Catonis -- wd Q255448 is named 'Porcia Catonis'; "
                              "both are spouses of the same record Q78066, which lists "
                              "both as wives"),
    ],
}


def load(q):
    p = ITEMS / f"{q}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(q, d):
    (ITEMS / f"{q}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def vals(d, pid):
    out = []
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        out.append(v.get("id") if isinstance(v, dict) else v)
    return out


def claim_id(c):
    v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) else None


def shadows():
    out = collections.defaultdict(list)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                out[r["to_qid"]].append(r["from_qid"])
    return out


def redirect_map():
    """from_qid -> to_qid for every file whose internal id differs from its filename.

    This must be folded into canonicalisation or a merge re-imports references to records
    an EARLIER merge already retired. Caught in dry run on the porcia cluster: Q144102 and
    Q144042 both cite Q141438, which the Porcii Catones merge had already redirected to
    Q72496, so the naive union would have given the merged Porcia two fathers that are the
    same man. The graph would still have canonicalised them to one edge, hiding it.
    """
    out = {}
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                out[r["from_qid"]] = r["to_qid"]
    return out


def label(q):
    d = load(q)
    if not d:
        return "?"
    v = (d.get("labels") or {}).get("en")
    return (v.get("value") if isinstance(v, dict) else v) or "(no label)"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv

    if "--list" in sys.argv or not args:
        print("clusters:")
        for name, pairs in CLUSTERS.items():
            print(f"  {name:10s} {len(pairs)} pair(s)")
        return 0
    name = args[0]
    if name not in CLUSTERS:
        print(f"unknown cluster {name!r}; try --list")
        return 1
    merges = CLUSTERS[name]
    shad = shadows()

    # Rule 1 precondition: every file that claims the loser must exist and be rewritable,
    # so that after the pass nothing is left claiming the vacated qid. The check that it
    # actually worked is in the verify step, which is the guard that matters.
    problems = []
    for surv, loser, _ in merges:
        for q in (surv, loser):
            if load(q) is None:
                problems.append(f"{q}: no item file")
        for s in shad.get(loser, ()):
            if not (ITEMS / f"{s}.json").exists():
                problems.append(
                    f"{loser} has shadow {s} with no file on disk -- it cannot be "
                    f"repointed, so qid {loser} would be left claimable. Aborting.")
    if problems:
        print("ABORT -- preconditions failed:")
        for p in problems:
            print("  " + p)
        return 1

    alias = {}
    for surv, loser, _ in merges:
        alias[loser] = surv
        for s in list(shad.get(loser, ())) + list(shad.get(surv, ())):
            alias[s] = surv

    redirects = redirect_map()

    def canon(q):
        """Resolve through earlier merges' redirects first, then this cluster's."""
        for _ in range(8):
            nxt = alias.get(q, redirects.get(q, q))
            if nxt == q:
                return q
            q = nxt
        return q

    print(f"cluster {name!r}: {len(merges)} merge(s)\n")
    for surv, loser, why in merges:
        ds, dl = load(surv), load(loser)
        print(f"  {loser} -> {surv}   {label(surv)[:44]}")
        print(f"        {why}")
        for p in GEN_PROPS:
            gained = sorted({canon(v) for v in vals(dl, p)
                             if canon(v) not in set(vals(ds, p)) and canon(v) != surv})
            if gained:
                print(f"        survivor gains {p}: {gained}")
        # Preview the NON-genealogical carry too. The apply path has done this since the
        # 38-dropped-properties fix, but the dry run only ever showed GEN_PROPS -- so a
        # reader checking the plan could not see that birth/death dates and external ids
        # were about to move. That mismatch between what the preview shows and what the
        # tool does is the same shape as the "strictly additive" claim that was false of
        # the records while true of the graph. Show both, and show the conflicts.
        will_carry = sorted(p for p in (dl.get("claims") or {})
                            if p not in GEN_PROPS and p not in (ds.get("claims") or {}))
        if will_carry:
            print(f"        survivor also gains, from the loser only: {', '.join(will_carry)}")
        differing = []
        for p, _cl in sorted((dl.get("claims") or {}).items()):
            if p in GEN_PROPS or p not in (ds.get("claims") or {}):
                continue
            a = sorted(str(v) for v in vals(ds, p))
            b = sorted(str(v) for v in vals(dl, p))
            if a != b:
                differing.append(p)
        if differing:
            print(f"        BOTH SIDES DIFFER on {', '.join(differing)} -- survivor's value "
                  f"stands and the difference is reported, not merged")
        print(f"        {1 + len(shad.get(surv, ())) + len(shad.get(loser, ()))} "
              f"file(s) rewritten (loser + shadows of both sides)")

    # I4 PRE-CHECK. check_invariants forbids the count of children with >2 parents from
    # increasing, and a merge raises it whenever a survivor inherits both sides' parents
    # and crosses three. That is not hypothetical: on 2026-08-01 a seven-pair Severan batch
    # was applied, failed I4 at 1207 -> 1210, and had to be reverted and narrowed -- about
    # 45 minutes of 164k-file sweeps to learn something computable in a second from the
    # inputs. Collapse risk and depth were checked beforehand; this was not.
    #
    # Counts the survivors only. A merge cannot raise anyone else's parent count: third
    # parties keep citing the loser's qid and extract_genealogy canonicalises it to the
    # survivor, which can merge two of a child's parents into one but never split one into
    # two.
    #
    # IT OVER-WARNS, DELIBERATELY. It counts survivors crossing upward and does not model
    # the offsetting DECREASES a merge produces elsewhere -- collapsing two of a child's
    # parents into one drops that child's count, and may drop it back under the threshold.
    # On the Severan batch this predicts 4 crossings where the observed net was +3, because
    # merging the two Julia Maesas took Julia Soaemias from two mothers to one. Erring
    # toward warning is the right bias for a guard that fronts a 45-minute round trip, but
    # a warning is a reason to look, not proof the cluster is unusable.
    over = []
    for surv, loser, _ in merges:
        ds, dl = load(surv), load(loser)
        if ds is None or dl is None:
            continue
        before_n = len({canon(v) for p in ("P47", "P48") for v in vals(ds, p)}
                       - {surv})
        after = {canon(v) for p in ("P47", "P48") for v in vals(ds, p)}
        after |= {canon(v) for p in ("P47", "P48") for v in vals(dl, p)}
        after -= {surv, loser}
        if len(after) > 2 and len(after) > before_n:
            over.append((surv, loser, before_n, len(after), sorted(after, key=lambda q: (0, int(q[1:])) if q[1:].isdigit() else (1, q))))
    if over:
        print("\n  ** I4 WARNING: these survivors would cross the >2-parent threshold **")
        for surv, loser, b, a, ps in over:
            print(f"     {surv} <- {loser}: {b} parent(s) -> {a}  ({', '.join(ps)})")
        print("     check_invariants will FAIL. Resolve the parent conflict first, or drop")
        print("     these pairs from the cluster. Do not re-baseline to make it pass.")
    else:
        print("\n  I4 pre-check: no survivor crosses the >2-parent threshold.")

    if not write:
        print("\nDRY RUN. Re-run with --write to apply.")
        return 0
    if over and "--force-i4" not in sys.argv:
        print("\nABORT: refusing to apply a cluster that would fail I4. Narrow the cluster,")
        print("or pass --force-i4 if the increase is genuinely intended and explained.")
        return 1

    print("\napplying...")
    carried, conflicts, claimed_by = {}, {}, {}
    for surv, loser, _ in merges:
        ds, dl = load(surv), load(loser)
        before = {p: len(vals(ds, p)) for p in GEN_PROPS}
        for p in GEN_PROPS:
            have = set(vals(ds, p))
            for c in (dl.get("claims") or {}).get(p, []):
                key = claim_id(c)
                if key is not None:
                    key = canon(key)
                    if key in have or key == surv:
                        continue
                    c = json.loads(json.dumps(c))
                    c["mainsnak"]["datavalue"]["value"]["id"] = key
                    if ("numeric-id" in c["mainsnak"]["datavalue"]["value"]
                            and key[1:].isdigit()):
                        c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(key[1:])
                else:
                    key = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                    if key in have:
                        continue
                ds.setdefault("claims", {}).setdefault(p, []).append(c)
                have.add(key)

        # Carry over everything else the survivor does not have at all. GEN_PROPS alone is
        # not enough: the loser's file becomes a copy of the survivor, so any property only
        # it held is gone from the dump. The first ten merges of 2026-07-31 dropped 38
        # properties this way -- external ids (P1185 Rodovid, P1819 Geni, P4159, P6821,
        # P9495) and, worse, P56/P57 birth and death dates on six records. Those merges
        # were described as "strictly additive"; that was true of the genealogy and not of
        # the records. Where BOTH sides hold a property, the survivor's value stands and
        # the difference is reported rather than guessed at.
        for p, cl in (dl.get("claims") or {}).items():
            if p in GEN_PROPS:
                continue
            if p not in (ds.get("claims") or {}):
                ds.setdefault("claims", {})[p] = json.loads(json.dumps(cl))
                carried.setdefault(surv, []).append(p)
            else:
                a = sorted(str(v) for v in vals(ds, p))
                b = sorted(str(v) for v in vals(dl, p))
                if a != b:
                    conflicts.setdefault(surv, []).append((p, a, b))

        for p in GEN_PROPS:
            kept, seen = [], set()
            for c in (ds.get("claims") or {}).get(p, []):
                key = claim_id(c)
                if key is None:
                    kept.append(c)
                    continue
                key = canon(key)
                if key == surv or key in seen:
                    continue
                seen.add(key)
                c["mainsnak"]["datavalue"]["value"]["id"] = key
                if "numeric-id" in c["mainsnak"]["datavalue"]["value"] and key[1:].isdigit():
                    c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(key[1:])
                kept.append(c)
            if p in (ds.get("claims") or {}):
                ds["claims"][p] = kept
        save(surv, ds)
        after = {p: len(vals(load(surv), p)) for p in GEN_PROPS}

        merged = load(surv)
        n = 0
        for f in [loser] + list(shad.get(loser, ())) + list(shad.get(surv, ())):
            if (ITEMS / f"{f}.json").exists():
                save(f, merged)
                n += 1
        # A file that BECAME a claimant of this survivor during an earlier merge in the
        # same cluster is not in `shad`, which was computed once from the pre-merge state.
        # Track them so the reconciliation pass below can find them without another sweep.
        claimed_by.setdefault(surv, set()).update(
            [loser] + list(shad.get(loser, ())) + list(shad.get(surv, ())))
        print(f"  {loser} -> {surv}: {before} -> {after}  ({n} file(s) rewritten)")

    # RECONCILIATION -- required whenever a cluster merges TWO records into ONE survivor.
    #
    # `shad` is built once, before any merge. Merge 1 rewrites the loser and its shadows as
    # copies of the survivor, which makes every one of those files a NEW claimant of the
    # survivor's qid. Merge 2 then updates the survivor and the shadows it knew about at
    # the start -- but not those new claimants, which are left frozen at the merge-1 state.
    #
    # Caught 2026-07-31 by .githooks/pre-commit on the `adnan` cluster, the first cluster
    # with two merges into one survivor: Q86433.json and Q98118.json held 10 children while
    # Q65555.json and the rest held 12. The earlier multi-merge clusters (porcia,
    # prachetas) each merged into DIFFERENT survivors, so the shape never arose.
    for surv, fs in claimed_by.items():
        final = load(surv)
        restale = [f for f in sorted(fs)
                   if (ITEMS / f"{f}.json").exists() and load(f) != final]
        for f in restale:
            save(f, final)
        if restale:
            print(f"\n  reconciled {len(restale)} file(s) left stale by an earlier merge "
                  f"into {surv}: {', '.join(restale)}")

    if carried:
        print("\nnon-genealogical properties carried over from the loser:")
        for q, ps in sorted(carried.items()):
            print(f"  {q}: {', '.join(sorted(ps))}")
    if conflicts:
        print("\nboth sides held these and DIFFER -- survivor's value kept, not merged:")
        for q, cs in sorted(conflicts.items()):
            for p, a, b in cs:
                print(f"  {q} {p}: survivor {a} vs loser {b}")

    print("\nverifying...")
    ok = True
    # THE load-bearing check: sweep every item file and assert that nothing anywhere still
    # resolves to a merged-away qid. This is what the old input-side refusal was standing
    # in for, and unlike that refusal it catches a claimant the redirect map did not know
    # about. It reads all 164k filenames but only opens the ones that could matter.
    losers = {loser for _, loser, _ in merges}
    stragglers, unreadable = [], 0
    for path in ITEMS.glob("Q*.json"):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            unreadable += 1
            continue
        # Some files in this dump hold valid JSON that is not an object (extract_
        # genealogy.py skips them the same way). They cannot claim a qid, so they cannot
        # be a straggler, but they are counted so the sweep does not look complete when
        # part of the directory was silently skipped.
        if not isinstance(d, dict):
            unreadable += 1
            continue
        if (d.get("id") or path.stem) in losers:
            stragglers.append(path.stem)
    if unreadable:
        print(f"  note: {unreadable} file(s) were not readable as a JSON object and were "
              f"not checked")
    if stragglers:
        print(f"  FAIL: {len(stragglers)} file(s) still claim a merged-away qid: "
              f"{', '.join(sorted(stragglers)[:10])}")
        ok = False
    else:
        print(f"  no file claims any of the {len(losers)} vacated qid(s)")

    # Compare CONTENT, not just the id field. The old check asked only whether each file's
    # internal id equalled the survivor's, which every stale copy also satisfies -- a file
    # frozen at merge-1 state still says id=Q65555. That is why this verify reported "all
    # files agree with their survivor" on the adnan cluster while .githooks/pre-commit
    # correctly blocked the commit. It also swept only the pre-merge `shad` set, so it
    # could not have looked at the files that went stale. Both are fixed: the set is the
    # union of the pre-merge shadows and everything rewritten during the run, and the test
    # is equality of the whole record.
    for surv, loser, _ in merges:
        final = load(surv)
        checkset = ({surv, loser} | set(shad.get(loser, ())) | set(shad.get(surv, ()))
                    | set(claimed_by.get(surv, ())))
        for f in sorted(checkset):
            d = load(f)
            if d is None:
                continue
            if d.get("id") != surv:
                print(f"  FAIL {f}: internal id is {d.get('id')}, expected {surv}")
                ok = False
            elif d != final:
                print(f"  FAIL {f}: claims {surv} but its content differs from the "
                      f"survivor -- a stale copy left by an earlier merge")
                ok = False
        d = load(surv)
        for p in ("P20", "P42", "P47", "P48"):
            if surv in vals(d, p):
                print(f"  FAIL {surv}: is its own {p}")
                ok = False
            stale = [v for v in vals(d, p) if v in alias]
            if stale:
                print(f"  FAIL {surv}: {p} still cites merged-away {stale}")
                ok = False
    print("all files agree with their survivor" if ok else "PROBLEMS ABOVE")
    print("\nNow re-run extract_genealogy.py, dump_qa_errors.py, check_invariants.py.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
