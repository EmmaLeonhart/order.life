# The Licinii Vari: the line is Geni-sourced and stands. A withdrawn finding.

Research for `queue.md` item 2, done 2026-08-15 against Wikidata — **and then largely
withdrawn the same day.** This file is kept because the lookups are worth having and
because the mistake is worth not repeating.

## The conclusion, corrected

**Nothing is wrong with the Licinii Vari line. Do not repair it.**

The dump records:

    Q73308  "Licinius  Varus"          geni 6000000030478073233, no wd
      -> Q73140  "Gaius Lincinius  Varus"   geni 6000000030478360865, no wd   = cos. 236 BC
           -> Q72966  "Lincinia  Varus"     geni 6000000002188289192, no wd
                married Q72963 Q. Mucius Scaevola (pr. 215, wd Q939045)
                mother of Q72807 P. Mucius Scaevola (cos. 175, wd Q2066659)
                   -> the Mucii Scaevolae, Licinii Crassi, Pompey, Asinius Pollio ...

So the Republic descends into the synoptic line through a Licinius Varus daughter marrying
into the Mucii Scaevolae. **That chain is Geni-sourced, carries no Wikidata ids, and that
is fine** — Emma, 2026-08-15: *"My guess is whatever it is right now is something that was
found on Geni at some point but is not on Wikidata, and that's fine."*

## What the Wikidata lookups actually showed

These stand. They simply do not support the conclusion first drawn from them.

| | |
|---|---|
| `Q1338451` Gaius Licinius Varus, **cos. 236 BC** | child `Q26110551` P. Licinius Varus (pr. 208). **No father recorded.** |
| `Q2066659` P. Mucius Scaevola, **cos. 175 BC** | father `Q939045`/`Q6095299` Q. Mucius Scaevola. **No mother recorded.** spouse `Q12284962` Licinia |
| `Q12284962` Licinia | *"wife of Publius Mucius Scaevola"*; children `Q261441` (cos. 133), `Q715499` Mucianus |
| `Q715499` P. Licinius Crassus Dives Mucianus | father `Q2066659` **and** `Q746582` P. Licinius Crassus; mother `Q12284962` |

The Mucianus entry is a clean instance of **CLAUDE.md case 2** — adoptive plus biological,
both correct, neither a defect. He was born a Mucius Scaevola and adopted into the Licinii
Crassi, which is why the cognomen records the birth family.

## THE WITHDRAWN FINDING, and why it was wrong

**What was claimed:** that `Q72966` "Lincinia Varus" and `Q72810` Licinia (wd `Q12284962`)
are the same woman imported twice a generation apart — one correctly as the cos. 175's
wife, one wrongly as his mother — and that the Republic therefore reached Aster through a
link no source records, which `narrative_spine.md` calls the wrong-story case.

**Why it does not hold:**

1. **They are two distinct Geni profiles.** `...2188289159` and `...2188289192` are
   different people on Geni, not one record imported twice. The proximity of the ids says
   they came from the same part of one family tree, which is exactly what you would expect
   of a mother-in-law and a daughter-in-law — not evidence of duplication.
2. **Two Licinias marrying into the Mucii Scaevolae in successive generations is ordinary
   Roman prosopography**, not an anomaly. Republican families intermarried repeatedly and
   *Licinia* is among the commonest names available.
3. **Wikidata's silence was treated as refutation.** `queue.md` states the rule directly —
   *"Wikidata records no link between them" is an absence of evidence, not a refutation* —
   and `Q2066659` having no recorded mother does not mean he had none. Most Republican
   women are unrecorded.

**The evidence offered was: both named Licinia, both married a Mucius Scaevola, adjacent
Geni ids.** That is suggestive. It was written into a queue item, a devlog entry, a commit
message and this file as though it were established, with a three-option decision built on
top of it. Applying nothing and asking first is the only reason it cost a write-up rather
than the line itself.

**The mechanism is worth naming**, because it is not carelessness and will recur: this came
after six consecutive ticks of finding real defects of exactly this shape — duplicate
imports, displaced generations, GEDCOM artifacts with no Wikidata id. Being freshly primed
by genuine finds made the false positive **more** likely, not less. A record that matches
the silhouette of the last six defects deserves *more* scepticism than a random one, not
less.

## What survives, and it is small

**`Q72972` carries a Wikidata id that cannot be right.** The record is the father of
`Q72810` Licinia, the cos. 175's wife, and it is aliased "Gaius Licinius Varus
/Licinius-Crassus/" and "Publius Licinius Varus Licinius Crassus Dives". Its `P61` is
**`Q29518656` = P. Licinius Crassus Dives, who is Mucianus's son** — that is roughly two
generations *below* the cos. 175, while the record stands as father of the cos. 175's wife.

Either the wd id is attached to the wrong record, or `Q72972` merges two men. **This is a
separate defect from anything above and does not touch the Vari attachment.** Filed on its
own; do not bundle it back into the Licinii Vari question, which is closed.
