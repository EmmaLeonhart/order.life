# Q73380 `BAD MERGE` — what it actually is

Written 2026-07-30 (queue item 3). **Describes, proposes, changes nothing.** No edit has
been made to `wikibase/items/*.json` or to any extract. Every number below comes from the
committed local dump (`persons.tsv`, `edges.tsv`, `spouses.tsv`).

The node was flagged because it carries **29,466 descendants** on the main backbone while
being literally labelled `BAD MERGE`, so it was to be understood before being touched.

## Headline

The working hypothesis in `queue.md` was right — a Spartan mythic figure conflated with a
Seleucid king — but the fix is not the one anticipated. **Q73380 does not need to be split
into two nodes, because both clean halves already exist in the dump as separate unlabelled
records.** Q73380 is a redundant third record whose edges are, with five exceptions,
duplicates of edges those two already carry.

| | record | label | evidence |
|---|---|---|---|
| Spartan half | **Q133344** | *(no label)* | parents Gorgophone + Oebalus; wives Periboea, Asterodeia, Polycaste, Dorodoche; father of Penelope — Icarius of Sparta |
| Seleucid half | **Q135914** | *(no label)* | parents Antiochus III the Great + Laodice III; wife Laodice IV — Seleucus IV Philopator |
| the merge | **Q73380** | `BAD MERGE` | holds **all** of the above at once |

Q73380's own fields agree with the Seleucid reading: birth `+0215`, death `+0164`,
`wikidata_qid` `Q3356`. Read as unsigned BC dates — the recording convention this dump
uses widely, see the era note in `GENEALOGY_QA.md` — that is 215–164 BC, which matches
Seleucus IV. Nothing on the record points to the Spartan side except the relationships.
Worth a check against Wikidata before acting: the identification of `Q3356` is stated
here from the surrounding relationships, not verified against Wikidata itself.

## The split, edge by edge

Every parent, every spouse but one, and 15 of the 20 children are already carried by
Q133344 or Q135914.

**Parents — 4 of 4 already covered**

| QID | label | also parent of |
|---|---|---|
| Q132823 | Gorgophone | Q133344 |
| Q90289 | Oebalus | Q133344 |
| Q73362 | Antiochus III the Great | Q135914 |
| Q73359 | Laodice III | Q135914 |

That a single person has both pairs is the merge in one line: two entirely unrelated
families, Spartan myth and the Seleucid dynasty.

**Spouses — 5 of 6 already covered**

Periboea, Asterodeia, Polycaste and Dorodoche are all Q133344's wives; Laodice IV is
Q135914's. Only `Q165295 N.N.` hangs on Q73380 alone, and its single child is Antiochis.

**Children — 15 of 20 already covered, and the co-parents sort them cleanly**

The Spartan children (Penelope, Thoon, Thoas, Perileos, Iphthime, Amasichus, Phalereus,
Pheremmelias, Alyzeus, Damasippus, Imeusimos, Aletes, Leucadius) all list Q133344 as a
co-parent alongside a Spartan wife. Nysa lists Q135914 alongside Laodice IV. Laodice
(Q73515) lists Q133344 alongside Asterodeia — see the warning below.

Five children attach to **Q73380 and nothing else**:

| QID | label | co-parent | descendants |
|---|---|---|---|
| Q73218 | Laodice VI | Laodice IV | 29,426 |
| Q136142 | Antiochus V | Laodice IV | 0 |
| Q136146 | Alexandros Balas | Laodice IV | 2 |
| Q165289 | Antiochus Eupator . | Laodice IV | 0 |
| Q165296 | Antiochis | N.N. | 0 |

All five are Seleucid by co-parent. They are the only edges that would be lost by
deleting Q73380 outright, and the only ones needing a decision.

## Where the 29,466 descendants actually go

Not to Sparta. The descendant mass is the **Pontic royal house**, reached through three
daughters whose descendant sets almost coincide:

| daughter | route | descendants |
|---|---|---|
| Q73515 Laodice (m. Mithridates III of Pontus) | via Q133344, the **Spartan** record | 29,438 |
| Q73377 Nysa (m. Pharnaces I of Pontus) | via Q135914, the Seleucid record | 29,431 |
| Q73218 Laodice VI (m. Mithridates V of Pontus) | via Q73380 only | 29,426 |

The sets overlap because the Pontic line marries back into itself — Laodice's son
Pharnaces I marries Nysa — so nearly everyone downstream descends through more than one
of the three. Their union is 29,438, and the whole of Q73218's 29,426 is contained in it.

**Nothing downstream depends on the two sides being joined.** Deleting Q73380 outright,
with no reassignment at all, would orphan **7 people** — and reassigning its five unique
children to Q135914 orphans **none**. The join carries no load.

## Proposed action — retire the node, do not split it

1. **Reassign the five Seleucid-only children** (Q73218, Q136142, Q136146, Q165289,
   Q165296) from Q73380 to **Q135914**, which already holds their grandparents and, for
   four of them, their mother Laodice IV.
2. **Move the spouse edge Q73380–Q165295 (N.N.)** to Q135914, so Antiochis keeps both
   parents.
3. **Delete Q73380's remaining 4 parent, 5 spouse and 15 child edges as duplicates** —
   every one is already carried by Q133344 or Q135914.
4. **Retire Q73380** and, if the dump supports redirects, point it at Q135914, since its
   own fields (dates, `Q3356`) describe the Seleucid person.
5. **Label Q133344 and Q135914.** Both are unlabelled, which is why the merged record
   looked load-bearing in the first place. On the relationships they are Icarius of Sparta
   and Seleucus IV Philopator; confirm before writing the labels in.

## The bigger problem this uncovers, which retiring Q73380 does NOT fix

**Q73515 Laodice — 29,438 descendants — is parented by Q133344 (Icarius of Sparta) and
Asterodeia.** Her husband and all five children are Pontic; her parents are Spartan myth.
That edge, not Q73380, is what currently ties the Greek mythic tier to the historical
backbone through this part of the graph, and it survives every step proposed above.

Reattaching her is a genuine genealogical decision, not a deduplication, so it is left
here rather than proposed: her recorded birth `+0250` (250 BC read as unsigned BC) sits
before Q73380's own `+0215`, so she cannot be Seleucus IV's daughter either, and the dump
offers no third candidate. Emma decides.

Also noted while reading the Seleucid side, both out of scope here: `Antiochus V`
(Q136142) and `Antiochus Eupator .` (Q165289) look like the same person recorded twice,
and Alexandros Balas was a pretender who *claimed* Seleucid descent rather than holding
it. Neither affects the proposal above — all three are childless or near-childless — but
both are worth a look if the Seleucid branch is ever cleaned properly.
