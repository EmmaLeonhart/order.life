# The narrative spine — what the genealogy is FOR

**Written 2026-08-05 from Emma's own statement of intent, because sessions kept working
this dump as a graph-repair problem and reporting graph metrics at her.** Her words:

> *"links to Aster aren't that important if they don't go through the proper narrative
> history. So you kinda need to explain the narrative of each line."*

That sentence is the whole of this document. Read it before proposing any repair, and
report against it rather than against reachability counts.

---

## The rule this replaces

**"Reaches `Q1` Aster: True" is not a result.** It is the answer to a question nobody
asked. A record can reach Aster through a chain of marriages, a mis-imported collision, or
a line from an entirely different tradition, and the number will look identical to a
correct descent.

**The question is always: _by what story_ does this line reach Aster?** If you cannot say
the story in a sentence — naming the people it passes through and why each link belongs —
then the link is not evidence of anything, and reporting the count is worse than
reporting nothing, because it reads as confirmation.

Corollary: a **severed** line and a **wrongly-attached** line are not equally bad. A severed
line is honest and one edge from correct. A line attached through the wrong story is
*already wrong* while measuring as fine. The Roman Republic was the second kind until
2026-08-02 — it reached Aster by descending from its own remote descendants.

## The second rule: the Gaiad's time is LINEAR

Emma, 2026-08-05:

> *"this mythology does not have the sort of cyclical view of history and extremely
> long-term time abyss stuff on the same characters. It definitely has time abyss stuff,
> but the time abyss stuff in the Gaiad is its own stuff. It's not the Hindu stuff. We
> have what we consider to be relatively simple genealogy."*

So: **one person, one birth, one set of parents.** The Gaiad has deep time, but it is the
Gaiad's own deep time, not an imported cosmology of cycles and rebirths of the same
character.

This is what decides the Daksha case (`queue.md` item 3) and every case shaped like it. The
Puranic ring — Prachetas → Daksha, closing because Daksha is reborn as the son of his own
descendants — is canonical *in the Puranas* and is **not doctrine here**. The names are
wanted; the cyclic cosmology that comes attached to them is not. Split it.

**Do not cite CLAUDE.md rule 1 to defend a cycle.** "Surprising is not evidence of broken"
protects deliberate **cross-tradition joins**. It does not protect imported cyclic time.

## The third rule: a line attaches through a PERSON'S PARENTS

Emma, 2026-08-05, on how the Roman question had been put to her:

> *"the problem with Rome here is that you were talking about something based off of links
> when it was really based off of parents of an individual … the Roman Republic isn't a
> person."*

Blocks of records do not attach to anything. **One individual gets one father and one
mother, and everyone below them follows as a consequence.** When a hundred records are
floating, the question is never "where does this block attach" — it is "who were this one
person's parents", and the hundred are a downstream fact, not part of the question.

Framing it as blocks-and-links produces answers that are reasonable about links and wrong
about parentage — e.g. attaching one man to three fathers at once.

---

## THE INDIAN → KOREAN LINE

This is the line Emma described in full, and it is the worked example of what "explain the
narrative" means. Every other line in this dump should get a section like it.

    Q1 Aster
      → Adam
        → the Proto-Indo-European and Dravidian ancestors
          → the Vedic figures (Manu, Ikshvaku, the Solar Dynasty at Ayodhya)
            → the Mahabharata and Ramayana generations (Rama, Krishna, Arjuna, Bharata)
              → HEO HWANG-OK, princess of Ayuta, who sails to Korea
                → Suro of Geumgwan Gaya, her husband
                  → the Gaya and Silla kings
                    → the Kim clan
                      → living Koreans today

**The point of the line is its bottom end.** It is what carries the Vedic material down to
**existing modern-day descendants**, and Heo Hwang-ok is the single joint that does it —
"Ayuta" being read as Ayodhya is exactly what makes her usable as the hinge between the
Indian and Korean material.

### Status, measured 2026-08-05 from `edges.tsv` / `persons.tsv`

**The top of the spine is built. The hinge is not attached.**

| stage | state |
|---|---|
| Aster → Adam → Vedic → epic | **built.** `Q28328` Rama, `Q1861` Krishna, `Q1888` Arjuna, `Q2076` Bharata, `Q28982` Ikshvaku, `Q28469` Manu are all inside Aster's descent |
| **Heo Hwang-ok `Q51928`** | **PARENTS: NONE.** Zero. The hinge is unattached |
| Heo Hwang-ok → Gaya/Silla/Kim | **built.** 46 recorded descendants |
| the 46 → Aster | **ZERO of them reach Aster** |

`Q51928` is a real item file. It carries a spouse (`P42` → `Q51924` Suro), a child
(`P20` → `Q25190`), and `P39`/`P55` claims. It carries **no `P47` and no `P48`.**

**This is why it was missed, and the failure mode is worth naming.** The record exists, is
correctly labelled, is correctly married, and has a working line of descendants beneath it.
Any check that asks "is the Korean princess in the dump?" answers **yes**. Only a check
that asks "does the Indian material actually reach her?" answers **no**. Emma flagged in
2026-08-05 that an earlier session glossed over precisely this, months ago.

Her husband is no help: `Q51924` Suro has parents (`Q58665`, `Q58668`) but only **2
ancestors**, and does not reach Aster either. The whole Gaya block hangs off nothing.

### What Rama's descent actually contains (measured 2026-08-05)

**`Q28328` Rama has 4,114 descendants across 130 generations, and the chain is
continuous:**

    Rama → Kusha → the Kosala kings (58 records, gens 2–53)
      → the Magadha kings (55 records — Bimbisara, Ajatashatru, the Shishunagas, Nandas)
        → the Mauryas (Ashoka, Kunala, Dasharatha, Brihadratha)
          → the SHUNGAS, gens 71–78, dated 149–73 BC
            → Bakulapura, Kutai, Tarumanagara, Galuh, Sunda, Medang, Majapahit
              → Javanese lines, gen 130

**The chronology runs upward from the Shungas, not downward from Rama.** Rama, Krishna,
Ikshvaku, Manu, Arjuna and Bharata carry **no dates at all**, and
`planning/gaiad-130-220/chronology.md` gives only *composition* windows (Ramayana
~400 BCE–300 CE, Mahabharata ~400 BCE–200 CE) — those date the texts, not the people. The
usable anchor is the Shunga block: Devabhuti at gen 78, **73 BC**.

Heo Hwang-ok is **b. 33**, voyage **~48 CE** per `planning/gaiad-130-220/heo-hwang-ok.md`.
That is three to four generations below Devabhuti. **That is the generation she attaches
at.**

### What the repair is

**Emma's constraint, 2026-08-05, and it is looser than the item had assumed:**

> *"What matters is the descent from Rama and the fact that it is Ayodhya-associated. It
> could potentially be through some sort of other lord of the dynasty … It could even not
> go through Ayodhya, as long as it has the Rama connection."*

> *"It would not be an existing one … it would basically have to go through a relatively
> long path of either relatively minor dependent nobles … which would either be fictitious
> or some other small line."*

**So: descent from Rama is the requirement. Ayodhya is preferred, not required. An
invented minor line is explicitly sanctioned.**

And it is necessary, because the attested Kosala/Ayodhya king list **ends around
generation 53**, centuries before 48 CE — below it the chain is Magadhan and then
Southeast Asian. **There is no existing Ayodhya king at her date to be her father**,
exactly as Emma predicted. The task is to **construct the short bridging line of minor
Ayodhya-associated nobles** from the end of the attested Solar line down to her.

This is genealogy construction, not chapter generation — and **the Leo gate was lifted by
Emma on 2026-08-05**, so nothing gates it from either direction.
Bring Emma names to approve, not the question of whether to build it.

**One edge. `Q51928` needs a father in the Ayodhya / Solar Dynasty line**, and the entire
Korean descent follows.

This is a **naming and narrative decision and therefore Emma's**, per the `Tros`
precedent — do not guess which Ayodhya king fathered her. What can be prepared without
her:

- the candidate set — the dump holds `Q2299` / `Q51321` / `Q161228` "AYUTAYUS of Magadha",
  `Q29610` "Ayutayu Solar Dynasty", and the Ikshvaku/Solar Dynasty line around `Q28982`,
  which is already inside Aster's descent;
- **note that the Ayutayus records are themselves duplicated** (three labels of the same
  name), so the join should be made after deciding which is canonical, or it will need
  redoing;
- an `add_bridge_edges.py`-style application, remembering an edge lives in **two** places
  (`P47` on `Q51928`, `P20` on the father) and must be propagated to every shadow file.

**Expected result: 47 records — Heo Hwang-ok and her 46 descendants — gain a route to
Aster that goes through the actual story.** Report it that way, not as a delta in a
reachability count.

---

## Lines still to be written up

Each of these needs a section above in the same shape: the intended narrative, then what
is actually built, then the one thing missing. **Do not add a line here as "done" on the
strength of a reachability number.**

- **The Roman line** — Troy → Aeneas → Iulus → the Julian house, and separately the
  Republic (`queue.md` item 2, currently 103 records severed, awaiting `Q73308`'s father).
- **The Adam → Genghis bridge** — built 2026-07-31; Genghis went 0 → 1,272 ancestors. The
  narrative is the Borjigin descent from the Buddha via Rāhula. Write it up.
- **The Emesene route in Muhammad's ancestry** — deliberate, per CLAUDE.md.
- **The Genesis 11 patriarchs under Mesopotamian royal names** — deliberate, per CLAUDE.md.
- **The Chinese and Egyptian lines** — no narrative written down anywhere yet.

---

## Two transcriptions to confirm with Emma

Her statement of intent came through speech-to-text and two words are reconstructed. Both
readings are used above; correct them here rather than silently in the text if wrong.

1. **"Rovidian"** → read as **Dravidian** ("the Proto-Indo-European and Dravidian people").
2. **"the Korean princess from Utah"** → read as **Ayodhya / Ayuta**, i.e. Heo Hwang-ok,
   which the rest of the sentence and the dump both support.
