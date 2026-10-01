# order.life: planning/, summaries/, chats/ digested (2026-09-25, read-only)

She asked for these three directories to be "digested today". Nothing in `order.life` was changed,
moved or deleted. This file sits beside `analysis/order-life-map.md`, which it doesn't repeat.

**Conventions.** Her words are in quotation marks. Anything marked *(mine)* is my judgement. The
verdicts are all mine:
- **KEEP**: live plan.
- **DIGEST**: her ideas are extracted here, and the file could then be archived.
- **STALE**: can go.

**Her standing instruction is not to delete anything.** "Can go" means she can archive it if she
chooses. It is not an action I have taken or queued.

**Her verdicts from today, which frame everything below:**
- The Sagittarius–Aries chapters are good.
- Taurus, Gemini and Cancer are basically placeholder.
- Leo is self-contained.
- The medieval part was "extremely well planned", but she lost steam implementing it.
- The modern part is almost absent.
- "a lot of stuff in the modern section was just kind of hallucinated".

---

## 1. The two competing modern chapter maps, identified

She said she doesn't know what the two modern chapter maps are. Both are in
`planning/gaiad-253-364/`, and **both are AI-made numbered lists. She never marked up either one.**

| | `modern-period-chapter-map.md` | `proposal-253-329.md` |
|---|---|---|
| Date | 2026-06-26, edited 08-05 | 2026-07-08 |
| Covers | ch 253–364, every slot | ch 253–329 only |
| Whose | The file says "These are MY proposed defaults so the map can exist. Override any of them." It is the model's. | Its header says "proposal for Emma's assessment … nothing here is decided until she marks it up". It was built from her 2026-07-07 perspective schema. |
| Frame | Global "parallel modernization". Three dynasty chronicles (Popes, Ottomans, Qing). Neutral global camera. | Her anchor countries, Japan and Britain (and so Shinto and Anglicanism). The world enters "as they get colonized by the Anglophone world". The no-Europe test. |
| Status against her own decisions | **Superseded.** On 2026-07-07 she rejected "parallel protagonists" ("organization is based on reactions to European colonialism"), which throws out its Ottoman/Qing chronicle defaults. | **Consistent with her schema, but unratified.** |

**The bigger point (mine, confidence high).** On 2026-04-14, in the saved Claude Code chat, she said
this about numbered chapter lists:

> "Trying to make a list of the chapters is actually the absolute worst thing that can be done …
> Trying to make a list of the chapters completely destroys any actual ability for me to make the
> chapters."

> "committing to the chapter structure is how you end up with garbage."

The folder's own README repeats this ("a numbered chapter list made in advance of writing produces
garbage"). Two months later a full numbered list was made anyway, and the 07-08 proposal is a second
one. Both are the kind of artifact she called the worst thing.

**The modern material that is hers** is:
- the three thematic axes,
- the editorial rules,
- the tail anchors,
- the perspective schema.

The slot-by-slot titles are not hers. Section 2 separates the two.

**The third "map"** is the ch 329–364 table in `Gaiad/epic/todo.md` ("Suburban Dream", "Beat
Generation", "The Singularity of Consciousness" and so on). It is older scaffolding. `todo.md` itself
already flags it as "partly hallucinated" legacy (2026-04-21).

---

## 2. planning/ (top level and gaiad-253-364): per file

Dates are from git. "Hers" means the file attributes it to her by quotation or dated directive.

### Top level

| File | What it is | Hers or AI | Hallucination risk *(mine)* | Verdict |
|---|---|---|---|---|
| `architecture.md` (02-09) | Site map, domains, 6 languages, calendar logic, 命 branding | Spec written in session; the branding (命 replaces 神, 命神宮, "extension of Shinto shrine tradition") reads as her established position | Low. The site now has 9 languages, so it is out of date | **STALE** (the build supersedes it); harvest the branding lines |
| `claude-issues-status.md`, `codex-issues-status.md` (02-09) | Checklists of site bugs from old chat logs | AI bookkeeping | None | **STALE** |
| `doctrine.md` (02-09) | Lifeism doctrine: primacy of life, agency as sacred, negative-theology polytheism, universal immortality, voluntary exit | Distilled from an earlier source; it is the text on the live site | Not applicable (doctrine, not history) | **KEEP**. It is the doctrinal source of record |
| `gaiad-tone-and-founders.md` (04-14/15) | Her tone principle, and her treatment of each founder or religion | **Hers.** I checked it against the saved chat transcript (§4b), and it matches her dictation closely | Low. It frames her positions and makes few factual claims | **KEEP**. It is the most faithful record of her design voice in the directory. Its "sibling doc" pointers are dead (the files were moved into `gaiad-130-220/`) |
| `lineage_bridges_proposed.md` (07-30) | Three proposed genealogy bridges (Adam→Genghis, Jimmu↔Heo, Kosala→Heo), plus five data defects | Written by the autonomous work-loop, propose-only; five decisions are left open for her | Careful: it refuses to invent generations, and it flags that one of its own calls isn't decided by the evidence | **KEEP**, but it belongs to the genealogy move, not the epic |

### gaiad-253-364/ (the modern period)

| File | What it is | Hers or AI | Verdict |
|---|---|---|---|
| `README.md` | Index. It lists the 06-26 map as live and doesn't list `proposal-253-329.md` or `perspective-schema.md` | AI | **STALE** as an index *(mine: it points at the superseded map)* |
| `chapter-allocation.md` (04-21) | Plan of record: tail anchors, "confirmed inclusions" ("Items the user has explicitly affirmed"), editorial criteria, open questions | Mixed. The anchors, inclusions and criteria are recorded as hers; the bracket budget is AI | **KEEP** (the anchors and criteria) |
| `thematic-spine.md` (04-21) | The three axes (invented tradition, suppressed syncretism, technology as double-edged) and "peoples, not ideologies" | The axes and filter are recorded as settled with her. The example lists and the Hollerith→IBM→LLM arc are AI elaboration | **KEEP** (the axes); treat the examples as suggestions |
| `ch362-handoff.md` (04-21) | Spec for ch 362 (2026 → time skip) | Structure hers (it matches `todo.md`); the craft options are AI | **KEEP** |
| `chronicle-candidates.md` (04-21) | Whether to add chronicle-form chapters beyond the Popes | AI options memo | **STALE**. Her 07-07 schema answered it: no dynasty chronicles |
| `early-modern-gunpowder-empires.md` (04-21) | Two theses (parallel modernization; unified identity as the variable of success) and a "mismatched ruling class" table | Theses recorded as hers, with quotes. The per-empire detail is AI | **DIGEST**. The theses live on in the schema; the empire-by-empire narrative is the "parallel protagonists" frame she later rejected |
| `anglican-focus.md` (07-07) | Her directive and a slate of ideas | Directive hers, verbatim; the slate is explicitly "proposals, not decisions" and parked | **DIGEST** (the directive is carried into the schema) |
| `perspective-schema.md` (07-07) | Japan and Britain as the anchor countries; the no-Europe test; gap analysis | Points 1–10 and the refinement are hers, verbatim; the gap analysis is AI | **KEEP**. It is her most recent decision about the modern section |
| `modern-period-chapter-map.md` (06-26) | See §1 | AI defaults | **STALE** (superseded by her 07-07 schema) |
| `proposal-253-329.md` (07-08) | See §1 | AI proposal, not marked up | **DIGEST**. Keep it only if she wants something to react to; otherwise it can go |

**Is the modern planning hallucinated? (mine)** The spine and schema files are opinionated but not
fabricated. Their historical examples are real and broadly standard:
- Hollerith and the census
- shinbutsu bunri
- the Zunghar genocide, 1755–58
- Kang Youwei's Confucian church

The weak spots are these:
- **Contestable claims presented as settled.** "Ottoman non-Arabization → a unified Arab superstate",
  and "Safavid Shi'ism took → durable Iranian identity". Both are stated as verdicts.
- **Filler slots with invented society-claims** in the 06-26 map, for example "Ch 263 — The Manchu
  gods" and "Ch 294 — The reactionary binary".
- **The older hallucination she recalls** most plausibly means the `todo.md` 329–364 table and
  `Gaiad/epic/notes_deprecated/` (flagged in `todo.md` as "bare-bones AND partly hallucinated"),
  rather than these files.

---

## 3. planning/gaiad-130-220/ (the medieval and ancient plan, 66 files)

**Provenance.**
- Written 2026-04-14 to 04-18. The first commits are authored "Claude"; the rest carry her name but
  are session transcription.
- The files use "Emma:" and "Emma, explicit" quotes. *(mine)* The prose around those quotes is mostly
  AI elaboration.

**Implementation.**
- **All of ch 130–220 was drafted on one day, 2026-04-18**, slot by slot from `chapter-allocation.md`.
  That day's commit message is hers: "added some chapters (I think they seriously dropped the ball)".
- **Ch 130–177 run 1,000–2,800 words.** Ch 178–220 fall to 300–1,000 words and read as placeholders.
  Ch 218 has filler rhyme-words.
- *(mine)* This fits her verdict: the plan was strong and the implementation ran thin.

**The signature medieval ideas that never reached the text:**
- Bustanai
- the Jesus and Muhammad lines via Rome
- Rāhula's descendants going east
- the Islam-in-Asia chapter (Wali Sanga, Han Kitab, Xiao'erjing)

Ch 201 argues the *opposite* of `india-stagnation.md`. Ch 210 is "The Ming Rises" rather than the
planned Renaissance.

| Cluster | Verdict *(mine)* |
|---|---|
| `mongol-block.md`, `late-medieval-sequence.md`: the eight-day Sunday-to-Sunday liturgical arc (Black Death as Good Friday, Kenmu as Holy Saturday, Renaissance as Easter; "Renaissance should FEEL like the Renaissance") | **KEEP**. The live plan for a rewrite of the thin chapters |
| `medieval-problem.md`: the section she called well planned. It works backwards from 1453; "Black Death gets its own chapter. Confirmed." | **KEEP/DIGEST**. Has errors (below) |
| `structure.md` (4.7k words): the richest record of her voice (tier list, rapid-transition hypothesis, Leo, the genealogy's purpose) | **DIGEST** (quotes in §5) |
| `gaiad-tone`-linked founder files: `buddha`, `jesus`, `muhammad`, `founder-followership-displacement`, `founder-retention-exception`, `gateway-ancestor-ubiquity`, `marozia`, `islam-syncretic`, `bustanai`, `charlemagne`, `heo-hwang-ok`, `elagabalus`, `genesis-opening`, `manu-yemo`, `moses-bac-pivot`, `bronze-age-collapse`, `lithuania-counterfactual`, `india-stagnation`, `prophetic-movement`, `scope-caveats`, `asia-arc`, `japan-emphasis`, `jimmu` | **DIGEST**. `japan-emphasis` is **KEEP** |
| `chapter-allocation.md` (the 91/91 plan that was implemented) | **STALE** as a plan; keep it as an index to the chapters |
| Standard-summary files, now implemented: `haplogroups`, the biblical spine (`abraham-jacob`, `joseph-egypt`, `pharaohs`, `israelite-kingdom`, `second-temple`, `bible`, `torah`, `david`), `ramayana`, `mahabharata`, `manu-indian`, `indus-valley`, `cucuteni-trypillia`, `mesopotamia`, `third-century-crisis`, `byzantium`, `xuanzang`, `chronology`, `must-include`, `might-include`, `europe-arc`, `southeast-asia`, the mythic-cycle notes (`aztec`, `scandinavia`, `rome`, `china`, `greece`, `mongolia`, `arabia`, `ethiopia`, `ireland`, `maori`, `other-mythic-cycles`), `README` | **STALE** once the few quotes are lifted |

**Unsupported or wrong claims found** (a spot-check, mine):
- **Mongol defeats.** "Japan the only place that did" defeat the Mongols is false (Ain Jalut, Đại
  Việt, Delhi).
- **Ögedei.** A "heart attack" as his cause of death is unsupported; drink is the usual account.
- **Kashmir Shaivism.** Dated "around the Delhi Sultanate"; it is 9th–11th c.
- **Finnish and Hungarian.** Said to be non-Indo-European "because of a different haplogroup"; that is
  wrong for Hungarians.
- **Hammurabi.** "Hammurabi is Abraham's cousin" and "Abraham descendant of Sargon via Puzur-Ashur" are
  invented genealogy.
- **Akhenaten** as "persecutor of Jewish people" is invented.
- **Heo Hwang-ok** is placed in Silla material; she is Gaya.
- **Xiao'erjing.** The claim that it gave the Hui "materially higher hanzi literacy" is unsupported.
- **Bustanai's princess** is given two different fathers in two files.
- **Hitler and Napoleon.** `must-include.md` says "No Hitler, Napoleon" haplogroup stories. That
  contradicts `structure.md` and her own chat, where she wanted them.

**Decisions stated in these files but *not* attributed to her.** Don't treat them as hers until she
owns them:
- the prophets as "basically Hamas"
- Islam as "starting borderline Baha'i"
- Baha'i as a harmful rival
- "China is mid"
- Carthage as the Lost Tribes, crossing to the Americas
- caste as the villain of Indian stagnation

---

## 4. chats/: extracted conversation text

There are two saved chats. Each has an HTML file, an already-extracted `.md` made by
`scripts/extract_chat.py`, and a `_files/` folder of JS assets (18 MB and 8.7 MB). The `.md` versions
are complete; I read her turns from them. Her own `chats/README.md` sets the lifecycle: once a chat is
captured in `planning/`, its `.md`, `.html` and `_files/` can go.

### 4a. "Islamism: Humiliation, Ideology, and Modern Harms" (Grok)

**Date and verdict.** Saved by 2026-04-15; the export carries no conversation date. Verdict **DIGEST**:
- partly captured, in `gaiad-130-220/islam-syncretic.md` (Xiao'erjing, Han Kitab) and in the modern
  "suppressed syncretism" axis;
- her political position is captured nowhere else.

The `_files/` folder is **STALE**. The Grok side is long generic analysis.

**Her positions (5 turns):**
- Islamism, not Islam, is the harm, and it runs on humiliation. "I really don't see it that badly
  historically, but I see Islamism as a more general phenomenon as being really, really, really
  harmful … a very distinct perspective of a previous humiliation that needs to be overcome".
- The model is not the old empires. "I'm not saying that I think that the Umayyads and the Mughals and
  stuff were good … these aren't actually the good examples to point to."
- Early-modern practice, not scripture:
  - "learn about how Islam was practised in China in the 1700s"
  - "when anybody reads a text that's over a thousand years old and tries to read a modern political
    message into it, they just read whatever they want"
  - early-modern history "gives a lot more of a real model for how Islam can peacefully coexist with
    other religions, compared to reading the Quran"
- Not restoration: "trying to restore the Ottoman Empire is kind of a stupid idea". What she means is
  instead "look at this stuff that happened … What stuff would you want to continue?"
- Coexistence is real but not the liberal version: "real meaningful and positive coexistence, but it
  has a lot of problems with it. It usually does not occur in a way that … a lot of liberals will
  kind of want to say".
- Why local understandings break: "people oftentimes don't value them … people don't really see these
  as being accomplishments, and that's the reason why they're fragile under stress."
- On modernisation: "Christianity more or less completely turned over a new leaf … but I think Islam
  and, I even personally say, Judaism haven't."
- A long-standing interest in alternate history: a sinicized Islam dominant in China. "I think both
  Christian China and Muslim China are both much more realistic outcomes than a lot of people give
  them credit for". She corrects herself: "sinusized, not a scientific".

### 4b. "Review chapter status and send workflows" (Claude Code, 2026-04-14)

**Verdict: DIGEST, largely done.** This session produced `gaiad-tone-and-founders.md` and the
`gaiad-130-220/` notes. I compared her turns against the tone doc and the capture is faithful. The
`_files/` folder is **STALE**.

**Her ideas and decisions (46 turns):**

**The shape of the book**
- "it isn't the Book of Genesis; this is like the Book of Genesis times a lot."
- It is carried by haplogroups "to kind of start from the beginning of man and then end at the
  beginning of man".
- Three strands at once: "Geological history · Natural history · The kind of history of peoples or
  the table of nations", "also … the technological and ideological history".
- Pivots: "The beginning of the book is very strongly emphasising creation"; "The month of Pisces,
  which is all about destruction … finally at the point where the stakes are established and now
  we're actually saying something with them"; and for humanity, "Exodus · The book of Leo · The
  modern age".

**The hard part**
- "The really hard to get to is probably more the Bronze Age collapse."
- "Once you reach 1500 or so, we reach a point where we're talking more about stuff than people, so
  it becomes easier again."
- *(mine)* She had expected the modern part to be the easier one, which sits beside her verdict today
  that she didn't know what to do with its history.

**Mythic cycles**
- The best bridges are the recent, rapid transitions: "Scandinavia and Japan are the strongest, even
  though they're the most recent, because the transition occurred rapidly". Then: "Aztec might
  actually be the strongest".
- "if a mythical cycle rather readily maps on to a historical point and historical genealogy, that's
  basically gold to us."
- "The Celtic ones really, really go in."
- Lithuania: "if Lithuania had a big body of epics … it would probably have the best transition".
- King Arthur: "We can probably make it go into King Arthur, and that would probably be a to-do thing."

**Descent from antiquity**
- "it's more of a bridge between two modes of history."
- "We're not really trying to legitimise a certain line … We're trying to incorporate people into the
  mythical narrative."
- "we go hard on the Jesus bloodline".
- She rejects *Holy Blood, Holy Grail* "because it doesn't emphasise continuity".
- "we're not necessarily trying to make it perfect; we're trying to tell a story."
- Of the merging: "difficult as fuck to do".

**The Book of Leo** is "a bit satirical on the Book of Mormon in its structure … in a weird way, more
culturally sensitive"; "I'm probably going to change the Book of Leo a decent amount."

**Coverage**
- "not every country needs to be in the Gaiad just every single country needs to be somewhat
  represented."
- "We are not treating indigenous as necessarily something that grants moral status."

**Against numbered chapter lists:** see the quotes in §1. What she asked for instead was the five
chapters on either side of the gap, with "a general chronological arrangement of the things, with no
intention of a chapter organisation at all … the lack of chapters is the fucking point." And: "we
have to know what we're doing and not just hallucinate crap."

**Tone**
- "If you have one weird historical detail, then it's this. If you have one weird offensive
  historical detail, then it's the Satanic Verses. If you have all of them, then it's the X-Files."
- "It's not like it's South Park".
- Thematically, "the absurdity of humanity and how we can strive to overcome it". She corrected the
  model's "can't" sharply.

**Founders** (all captured in the tone doc):
- Judaism: "very pro-David"; monotheism a tragedy, "Yahweh is the one who didn't kill the other gods".
- Jesus: "hesitancy about the mental health", "ultimately goes pro-Jesus anyway".
- Islam: extends Manichaeism, "ultimately behaving like a very syncretic religion".
- Muhammad: "isn't really trying to start something new … ends up forced into a position of starting
  something new".
- Confucius: "an illegitimate child … ends up saving the I Ching".
- Jimmu: "an extremely messy political coalition between multiple different ethnic groups".
- Zarathustra: "pretty much Vedic".
- Hinduism: "I don't think there really is a founder … focus on the caste system as being this more
  or less opportunistically imposed power structure".
- Sikhism: "a religion of the modern age … a way of trying to bridge the gap and protect the innocent
  … still is depicted as positive".
- Buddha: "a guy who had a failed political career … systematically denied the ability to be a
  priest … he ends up basically having a pretty happy ending"; "my depiction of the Buddha is
  probably the most actively critical, even though it comes out well".

**The working relationship:** "please please please be actually taking notes of what we're talking
about in some kind of planning directory". This is why `planning/` exists.

---

## 5. summaries/ (32 files, 5.6 MB): all STALE

**How they were made.** All 32 were added in one commit on 2026-02-24, with her message: "This is a
summary thing for usage in summarization functions". They are **not summaries.** They are raw
concatenations with `--- FILE: name ---` separators, most likely a hand-run PowerShell job (mine),
which is why the encoding is mixed.

**Nothing in them exists only here.** A script split each bundle at its separators and compared every
segment (450+) with the tracked source at the adding commit, and all of them matched exactly. Every
source is still in the repo, usually in a newer version.

| Files | Contents | Verdict |
|---|---|---|
| `scripture_01–22` | Gaiad ch 1–84 and 329, from before later edits | **STALE** |
| `capricorn_compilation`, `characters_index`, `core_content` | Copies of the epic compilation, the character CSVs, and `content/*.json` | **STALE** |
| `project_and_planning` | Old README, todo, CLAUDE.md, the three top-level planning files | **STALE** |
| `realms_content_1/_3`, `realms_summary` (2 MB) | Realm pages, `realms.json`, `shrines.csv` (`_2` was never made) | **STALE** |
| `religion_book_1/_3` | Gaiad/religion-book chapters and its ChatGPT research prompts (`_2` was never made) | **STALE** |
| `Comprehensive_Site_Guide` | A flattened render of the site from `en.json` and `gaian_days.json`, with broken template text ("the 2th day…") | **STALE**. The build regenerates it |

**The cost of keeping them (mine):** stale duplicates that any grep or LLM search of the repo will hit
alongside the live sources.

---

## 6. What is live, in one place (mine)

1. **Doctrine and tone:**
   - `doctrine.md`
   - `gaiad-tone-and-founders.md`
2. **The modern section, her decisions only:**
   - tail anchors 253 / 362 / 363 / 364, with 329 soft
   - the three axes
   - "every chapter must say something special about society"
   - "peoples, not ideologies"
   - the Japan + Britain anchor schema and the no-Europe test

   The modern section does **not** have a chapter list she has ratified. Her own April rule argues
   against making one ahead of writing.
3. **The medieval rewrite:** the Mongol and late-medieval liturgical week, and `medieval-problem.md`,
   with the errors in §3 corrected.
4. **Genealogy:** `lineage_bridges_proposed.md` goes with the genealogy move.

**Everything else** either has its ideas lifted into this file, or is a verbatim duplicate or an
implemented summary. It can be archived whenever she chooses. Nothing has been deleted.

---

**✗ CORRECTED BY HER, 2026-09-25:** *"Hammurabi as a Abraham's cousin is intentional. That's not a
hallucination."* Struck from the unsupported-claims list above; it is her creative choice. **And her
decision on the Daijōsai chapter:** the chapter is great but belongs *"closer to Yom Kippur than to
Ninamesai"*; the Niiname-sai slot will instead be *"the real Daijosai ... of uh, Emperor Heisei"*
(Akihito's, November 1990).
