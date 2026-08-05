# `Q72786` resolved — it is a **Mamercus**, not a Marcus

**Researched 2026-08-05 by looking the records up on Wikidata**, which is the one thing
the 2026-07-31 and 2026-08-01 sessions never did. Emma's instruction was *"do the
research. I'm pretty sure there's something easy to find that we just haven't seen yet."*
She was right, and this is it.

Nothing has been applied to `wikibase/items/` yet. This file is the finding.

## The question

`Q72786` "Marcus Aemilius Lepidus" carries **three separate father+mother couples**, each
of which lists it as their child. A record cannot have three parentages. The repair is an
unmerge; what was missing was which couple belongs to which man.

| | father | mother |
|---|---|---|
| **A** | `Q73011` M. Aemilius Lepidus (wd `Q3622705`) | `Q72801` Cornelia (wd `Q100804879`) |
| **B** | `Q73113` M. Aemilius Lepidus | `Q73110` NN wife of M. Aemilius Lepidus |
| **C** | `Q73173` M. Aemilius Lepidus, Consul | — |

Couple A's edge — `Q72801` Cornelia → `Q72786` — is what drags the Scipiones down into the
Aemilii and closes the 15-record tangle.

## What Wikidata says

Fetched live 2026-08-05 (`wbgetentities`, explicit User-Agent per CLAUDE.md):

**`Q3622705` — "Marcus Aemilius Lepidus", Roman consul 126 BC.** The dump's `Q73011`.
- father: `Q3625112` and `Q1275675` (Wikidata itself carries two candidates)
- **child: `Q721477` — and that is the ONLY one.**

**`Q100804879` — "Cornelia", described as _"wife of Drusus"_.** The dump's `Q72801`.
- children: `Q433463` Marcus Livius Drusus (124–91 BC), **`Q721477`**, `Q432100` Livia
  (200–90 BC)
- no father recorded

**`Q721477` — "Mamercus Aemilius Lepidus Livianus", b. c. 150 BC.**

## The finding

**Couple A's son is `Q721477` Mamercus Aemilius Lepidus Livianus — not a Marcus at all.**

The cognomen is the giveaway and it is self-documenting: *Livianus* marks him as born a
**Livius Drusus** and adopted into the Aemilii Lepidi. That is exactly why Cornelia is
described as "wife of Drusus" while her son carries an Aemilian name, and why her other
two children are a Livius Drusus and a Livia.

So the dump's `Q72786` is a **name collision between Marcus and Mamercus**, and the three
"parentages" are not three claims about one man — they are at least two different men
filed under one label. **This is an unmerge, step 1 of the repair order, and it costs
nothing:** split, and couple A keeps their son under his own name.

**No cross-tradition join is touched and the Scipio half is not touched.** This is the
defect `cycle_policy.md` predicted would be elsewhere in the loop.

## The fourth Lepidus falls out of the same lookup

The `Q72615`/`Q72693` merge of 2026-07-31 left a "Quintus Aemilius Lepidus" with **two
fathers**, `Q72786` and `Q144279`, both labelled "Marcus Aemilius Lepidus". That conflict
resolves here too:

**`Q3625112` — "Marcus Aemilius Lepidus", tribunus militum 190 BC, b. 210 BC d. 190 BC.**
This is the dump's `Q144279`, and the identification is certain: the dump carries
`b=+0210`, `d=+0190` and Wikidata carries `-0210`, `-0190` — the same numbers, differing
only by the sign bug documented below.
- children: `Q3622705` (the consul of 126 BC, = dump `Q73011`) **and `Q11944252` Quintus
  Aemilius Lepidus**

**So Quintus's father is `Q144279`, which the dump already records.** The competing
`Q72786` → Quintus edge is the false one. Removing it needs no judgement call — Wikidata
records the same pair the other way is not even required here; it simply assigns the son
elsewhere, and the surviving edge is already present.

This also confirms the generation collapse the queue suspected: `Q3625112` is the father
of `Q3622705`, i.e. dump `Q144279` is the father of dump `Q73011`.

## Still open, and genuinely so

- **Which men are couples B and C?** The lookup settles couple A. `Q73113`/`Q73110` and
  `Q73173` are unidentified in the dump (no Wikidata ids on any of the three). They need
  their own lookups against the Aemilii Lepidi prosopography before the unmerge can assign
  all three.
- **Cornelia's own father.** The dump gives her three (`Q72957`, `Q73425`, `Q73017`);
  **Wikidata records none.** `Q72957` is "Consul (138 BC) - Publius Cornelius Scipio
  Nasica", dated −182/−132, and it is that edge that closes the loop downward. Absence on
  Wikidata is not refutation — see the standing warning in `queue.md` — so this stays open.
- **Naming** the split records is Emma's per the `Tros` precedent. `Q721477` supplies the
  name for couple A's son; B and C do not have names yet.

## ALSO FOUND — BC dates are stored as POSITIVE years

Turned up while dating these records, and it is a general hazard, not a Lepidus one.

**Only 133 records in the entire dump carry a negative (BC) date.** Almost everything
pre-Christian is stored with a positive year:

| record | truth | stored as |
|---|---|---|
| `Q74255` Numa Pompilius (716–672 BC) | BC | `b=+0753`, `d=+0671` |
| `Q2175` Agnimitra (d. 141 BC) | BC | `d=+0141` |
| `Q2074` Devabhuti (d. 73 BC) | BC | `d=+0073` |
| `Q2086` Bhagabhadra (d. 83 BC) | BC | `d=+0083` |
| `Q72957` P. Cornelius Scipio Nasica | BC | `b=-0182`, `d=-0132` — **correct** |

So the dump is **inconsistent**, which is worse than being uniformly wrong: a script
cannot assume either convention.

**Consequence, and it needs checking rather than assuming:** every past repair justified
as *"chronologically impossible"* — above all the **inversion class** cut on 2026-08-02,
five tangles and 21 records — reasoned about dates. Where those arguments used
patronymics, dynasty membership or explicit BC/AD in the label, they stand. Where any of
them compared these date fields numerically, the comparison was between mixed conventions
and must be re-derived. **Do not revert anything on this basis; go and check which
arguments actually used the fields.** Queued as its own item.
