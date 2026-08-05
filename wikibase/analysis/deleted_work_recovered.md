# The 2025-09-06 mass deletion, and what it does and does not contain

**Written 2026-08-05.** Emma: *"Jimmu ancestry is supposed to go through her to India.
Jimmu ancestry was a thing I did a lot of work on but it might be gone. Git history and
chatlogs might preserve it."*

Searched. **The Japanese work is real, recoverable, and already live in the dump. The
Jimmu → Heo Hwang-ok → India link is not in it, and was never built.**

## The commit

`57711c637`, 2025-09-06, commit message `q`. **319 files, 1,862,702 deletions.** Nothing
is lost — every file is recoverable with `git show 57711c637^:<path>`.

What it removed, relevant here:

| file | size | what it is |
|---|---:|---|
| `Gaiad/GENEALOGY_PROJECT_SUMMARY.md` | — | the project's own account of the GEDCOM imports |
| `Gaiad/japanese_gedcom_to_qid_mapping.txt` | 24,188 lines | the Japanese import mapping |
| `Gaiad/chinese_gedcom_to_qid_mapping.txt` | 8,387 lines | the Chinese import mapping |
| `Gaiad/merge_mapping.csv` | — | a duplicate-detection pass with MERGE/PENDING verdicts |
| `Gaiad/qid_correspondence.csv`, `mongodb_correspondence.csv` | — | old-wikibase QID correspondence |
| `Gaiad/gedcom_date_*.py` (6 scripts) | — | **date analysis and standardisation — likely relevant to the BC-sign problem, item 0b** |

Per `GENEALOGY_PROJECT_SUMMARY.md`, the imports were:

- **Chinese** — 8,280 parsed, 8,271 uploaded, 5,927 families, QIDs from ~Q6607.
- **Japanese** — 30,000 parsed, **24,158 uploaded**, 20,035 families, QIDs from ~Q16547.
- **Master combined** — 99,518+ individuals, marked IN PROGRESS at the time.

**So "a lot of work on Jimmu ancestry" is accurate and it survived**: the Japanese block is
the Q16547+ range and it is in the dump today.

## What the Japanese material actually connects to — measured, not assumed

`Q6432` Jimmu has **403 ancestors and reaches `Q1` Aster**. The route is not Indian:

    Jimmu → Ugayafukiaezu → Hoori → a chain of *-no-Mikoto*
      → Jī Yángchāng, KING OF YAYOI → the Kings of Wu → Zhou → the Yellow Emperor
        → the haplogroup chain → Adam → Aster

That is the **Wu-Taibo descent** — the traditional claim that the Japanese ruling line
descends from Taibo of Wu. It is a genuine cross-tradition join, it is intact, and it is
what the Japanese GEDCOM import was wired into.

## The India bridge is absent, and this was checked three ways

1. **`japanese_gedcom_to_qid_mapping.txt` — zero matches** for heo / hwang / ayodhya /
   india / gaya / suro / silla / korea. It is a standalone Japanese genealogy.
2. **`git grep` across the entire deleted tree** for hwang / ayodhya / ayuta returns only
   unrelated Korean surnames (Yi Hwang, Oh Hwang, Hwangbo Je-gong) and the Indian
   *Ayutayus* records — no Heo Hwang-ok linkage.
3. **`Q51928` Heo Hwang-ok has no parents today**, and `Q6432` Jimmu's ancestor set does
   not contain her.

**What does exist is the intent, recorded twice.** `planning/gaiad-130-220/heo-hwang-ok.md`
calls her "the one named Asian-to-Asian bridge … linking Indic, Korean, and Japanese
material", and the chatlog `chats/review-chapter-status-and-send-workflows-claude-code.md`
has *"Heo Hwang-ok as the one Asian bridge"*. **Intent, never implementation.**

## The direction problem — this needs Emma, and it is a real narrative call

**Jimmu cannot descend from Heo Hwang-ok.** Traditional Jimmu is 660 BC; she is b. 33,
voyage ~48 CE — she is roughly **700 years later than he is**. A Jimmu-descends-from-her
edge would be the exact inversion class this repo spent 2026-08-02 cutting.

Her own brief already says the other thing: *"the bridge reaches Japan through **later**
descendants."* So the buildable version is:

    Heo Hwang-ok (48 CE) → the Gaya and Silla kings → the Kim clan
      → [a Korean-to-Japanese marriage, some centuries later] → the Japanese line

which joins Japan to India **below** Jimmu, leaving his Wu-Taibo ancestry untouched. Japan
would then have two ancestries — Chinese through Jimmu, Indian through the later Korean
marriage — which is what this project is for.

**The question for Emma is which she meant**, and it is genuinely hers:

- **(a)** the later-marriage version above — additive, chronologically clean, keeps
  Wu-Taibo; or
- **(b)** she really does want Jimmu's own line rerouted to India, which means displacing
  the Wu-Taibo descent and accepting an inverted chronology; or
- **(c)** she is remembering the *intent* from the planning notes and the implementation
  never happened — which is what the evidence says.

## Recovered as directly actionable

**`merge_mapping.csv` already flagged the AYUTAYUS duplicates in 2025 and they were never
merged.** Three pairs among `Q2299` / `Q51321` / `Q70070`, all at `1.000 name_similarity`,
status **MERGE / PENDING**. That is independent confirmation of the dedupe queued as prep
for item 0.

**Caveat: those files use the OLD Miraheze wikibase QIDs and the numbering has shifted.**
`Q70070`, `Q2538` and `Q2316` ("RĀMA of Ayodhya Dasharatha") **do not exist in the current
dump**. `Q2299`, `Q51321`, `Q161228` and `Q29610` do. So treat the old CSVs as evidence of
*what was judged*, never as a source of qids to act on.

**Also worth recovering deliberately:** the six `gedcom_date_*` scripts. Item 0b is about
11,833 records whose BC dates read as AD, and a date standardiser written by the person who
did the import may document the convention rather than leave it to be re-derived.
