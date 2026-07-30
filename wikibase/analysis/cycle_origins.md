# Where the ancestry cycles come from

**2026-07-30. Scope set by Emma: cycles only, and no cycle should exist.**

Read-only. Nothing cut, nothing edited. Every figure here is reproduced by
`python wiki-scripts/cycle_origins.py`.

---

## The short answer

**Roman naming.** Roman aristocratic men repeat the full *tria nomina* generation after
generation, so father and son are literally the same string. Every genealogy tool that
matches or dedupes on name treats them as one person, and once two records that are
actually father and son are linked in both directions, the graph has a cycle.

The numbers say it plainly:

| Naming convention | share of cycle members | share of dump | enrichment |
|---|---|---|---|
| **Roman repeating names** | **18.3%** | 1.91% | **9.6×** |
| Iberian patronymic | 3.8% | 0.95% | **4.0×** |
| Welsh patronymic | 6.1% | 5.34% | 1.1× |
| Arabic patronymic | 1.5% | 2.94% | 0.5× |
| CJK | 0.3% | 6.11% | 0.0× |

Roman names are nearly ten times over-represented inside cycles. Iberian names four times.
**Welsh patronymics are not enriched at all** (1.1×) — I had assumed they would be, since
`ap`/`ferch` names embed the father's name in the child's, and that assumption was wrong.
Arabic patronymics are *depleted* (0.5×) and CJK names are effectively absent from cycles
despite being 6% of the dump.

So this is not "long names confuse matchers". It is specifically **the convention where a
son bears his father's exact name**, which is Roman, and secondarily the Iberian
`<given> <patronymic> de <place>` pattern where a few families reuse a small pool of names.

---

## The mechanism, visible in the cut set

Of the 56 edges that break all 71 cycles, these are same-name or near-same-name pairs:

```
Q73323 Titus Manlius Torquatus        -> Q73470 Titus Manlius Torquatus      identical
Q70388 Publius Aelius Marullinus      -> Q69886 Publius Aelius Marullinus    identical
Q78507 Marcus Granius                 -> Q78384 Marcus Granius               identical
Q73910 Gaius Servilius                -> Q73812 Gaius Servilius              identical
Q73958 Lucius Fulvius, II             -> Q73872 Lucius Fulvius Curvus        near
Q78501 Marcus Valerius                -> Q78615 Manius Valerius              near
Q73005 Cato the Elder                 -> Q73167 Marcus Porcius Censorius     same person, two names
Q73119 Marcus Livius Drusus           -> Q72951 Gaius Livius Drusus          same gens
Q73311 L. Caecilius Metellus Denter   -> Q73146 Lucius Caecilius Metellus    near
Q73644 C. Junius Brutus               -> Q73518 C. Junius Junius Brutus Brutus  near
Q141474 P. Licinius Crassus Dives Mucianus -> Q72972 P. Licinius Crassus Dives  near
Q76933 Sergius Octavius Pontainus     -> Q76693 Sergius Octavius Pontianus Laenes  near
```

`Publius Aelius Marullinus` is the cleanest case. The dump holds two records, **and so does
Wikidata** — `Q112865805` and `Q112865796`, adjacent identifiers, i.e. Wikidata knows there
are two men of that name. The dump copied both correctly. Then something attached a parent
edge in each direction between them, and the pair became each other's ancestor.

`Lucius Fulvius, II` is the tell that a human hit this and papered over it: someone appended
"II" to disambiguate, which means they saw the collision, and the edges stayed wrong anyway.

Per-cycle, the duplicate-name signature shows up in **36 of 71**:

| Signature | Cycles |
|---|---|
| near-identical labels in the cycle (≥0.72) | 26 |
| identical label twice in the cycle | 10 |
| 2-cycle with no name overlap | 15 |
| no duplicate signature | 20 |

And 22 of the 71 cycles are length 2 — a mutual parent-child pair, which is the minimal
form of exactly this error.

---

## Where they came in from

| Provenance field | cycle members | dump | enrichment |
|---|---|---|---|
| `gedcom` | 36.0% | 16.8% | **2.15×** |
| `geni_id` | 50.6% | 32.7% | **1.54×** |
| `wikidata_qid` | 41.0% | 56.2% | **0.73×** |

Cycle members are twice as likely to carry a GEDCOM identifier and half again as likely to
carry a Geni identifier — and **less** likely to be Wikidata-linked. The GEDCOM values on
cycle members carry the `/surname/` convention (`Publius /Claudius-Nero/`,
`Marcus Livius Salinator Drusus /Drusus Salinator/`), which is where the doubled cognomina
come from.

The direction is consistent: **cycles arrived through GEDCOM and Geni imports, and the
Wikidata-linked part of the dump is the cleanest part of it.**

---

## 71 cycles are not 71 defects

This is the part that changes the work.

- 367 distinct edges appear inside cycles.
- **87 of them appear in more than one cycle.**
- **56 edges break all 71 cycles.**

One run of twelve consecutive edges through the Portuguese **de Aguiar** family appears in
**seven cycles each**:

```
Q79510 Maria Soares -> Q79582 Diogo Rodrigues de Aguiar -> Q79663 Rui Dias de Aguiar
  -> Q79863 Joao Afonso de Aguiar -> Q80223 Diogo Afonso Afonso de Aguiar
  -> Q80606 Pedro Afonso de Aguiar -> Q81339 Antonio Ambrosio de Aguiar Coutinho
  -> Q82122 Barbara, imperatriz of Rome -> Q99597 Bárbara, Princess of Rome
  -> Q99585 Aviena -> Q99573 Proba -> Q99558 Proba Rogas of Lybia -> Q99544 Heracles
```

Seven of the eight cycles of length ≥ 20 run through that one stretch. Note `Diogo Afonso
**Afonso** de Aguiar` and the pair `Barbara, imperatriz of Rome` / `Bárbara, Princess of
Rome` — the doubled name and the accented duplicate are the same collision pattern again,
and the run ends by joining a Portuguese family to Heracles.

**So the 71-cycle count overstates the damage.** It is closer to 56 independent bad edges,
and in the Iberian block possibly two or three root errors generating most of the long
cycles between them.

---

## Cycles that are the same defect imported twice

Two pairs in the cut set are the same error appearing in two parallel copies of the same
material:

- `Q2035 YAMA Dharma King of Death -> Q153444 SUNITA Anga` **and**
  `Q160673 YAMA Dharma -> Q160640 SUNITA Anga`
- `Q88454 Esther bat Sahlan ben Abraham` has the same bad edge to **two** different
  `Esther bat Yosef ben 'Amram haDayyan` records, Q88380 and Q90982

These are the same duplicated-import problem already documented for the Kosala king list
(three parallel copies) and the Ishmael/Adnan records. **Deduplicating those imports would
remove these cycles without any edge being cut by hand.**

---

## What is not name collision

The 20 cycles with no duplicate signature need separate treatment, and two kinds stand out:

- **Placeholder generation chains.** `Q87854 Generation 3 -> Q87852 Generation 4` is in the
  cut set. These are the synthetic `Generation N` / `N-generation ancestor` filler records
  (463 of them in the dump), which have no real identity to collide and cycle for a
  different reason — probably an off-by-one when the chain was stitched to its endpoints.
- **Mythic-tier figures.** `Q90576 Belus -> Q74973 Danaus`, `Q74973 Danaus -> Q130061
  Nilus`, `Q130582 Atlas -> Q130716 Electra`. Danaus was already flagged as a fan-out
  suspect (231 children). Greek mythographers genuinely disagree about these parentages, so
  the cycle may record two incompatible traditions rather than one import error.

I raised these as possibly-authored earlier and was told no cycle should exist. Taking that
as given, they still need cutting — but they are the rows where the *choice* of which edge
to cut is a claim about which tradition wins, not a data-cleanliness question. **Flagging,
not deciding.**

---

## What I would do next

1. **Dedupe the parallel imports first** (Kosala, Ishmael/Adnan, the doubled YAMA/SUNITA and
   Esther chains). Cycles that are duplication artifacts disappear without a cut being
   chosen, which is strictly safer than choosing one.
2. **Then cut the 56-edge set**, not 71 cuts. It is smaller, and several of its edges kill
   seven cycles at once.
3. **Fold the Wikidata cross-check into the proposals.** `qa_cycles_proposed.tsv` was built
   *before* `qa_cycles_vs_wikidata.tsv` and never saw it. Of the 25 cycles it left
   unresolved, **7 contain an edge Wikidata explicitly contradicts** — those are decided
   already and nobody has noticed. Another 289 of 514 cycle edges are still `unknown`
   against Wikidata and could be resolved by fetching.
4. **Leave the mythic tier last**, since those cuts are editorial.
