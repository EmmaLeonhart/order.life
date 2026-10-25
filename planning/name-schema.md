# The name schema: every person's names as puzzle pieces

From Emma's words of 2026-10-13, about 00:05 to 01:00 (her session notes,
`psilocybin-management-2/research/session-2026-10-12.md`, "The name schema" and "Neo-kun'yomi and
Chinese names"). Quoted lines are hers. Written 2026-10-15; the decisions marked as Claude's were made
on her instruction to make the call on stuck items, and are hers to change.

> "We treat the names much more like puzzle pieces that you put together."
> "It sounds like eclecticism. I would argue it's almost the opposite." It is "a combinatorics thing on
> what should be representing a person. And a desire for a sort of universal compatibility."

## What every person carries

| Slot | Who gets it | Rule |
|---|---|---|
| Display name | everyone | the name the site and the GEDCOM show first |
| Native name | everyone | in the person's own script and language |
| English, Chinese, Japanese, Korean | everyone | "Chinese, Japanese, Korean, English are the primary ones"; every other language that appears on any label is "aspirational" for everyone |
| Western name | everyone | the given name, as the old "Christian name" was, for everyone not Chinese, Japanese or Korean (see Decisions for them) |
| Patronymic or matronymic | everyone | set by the person's **canonical line to Aster and Andromeda**, not by default to the father: "my canonical line goes through my mother". Stacked as in Welsh where wanted. Rendered per language ("Emma Helen's daughter into Arabic would be Emma Bint Helen"). A historical patronymic that differs goes in the notes, with both ("I don't think this is going to be very common") |
| Chinese name | everyone | independent of the transliteration; unique where possible and phonetically related. The surname can come from the clan, not the given name: for Muhammad "something Quraysh-derived ... something like Ha" (哈, Hashim) |
| Neo-kun'yomi | everyone with an Abrahamic name | one standard kanji form per name root: "all versions of John are the same, all versions of David are the same". One Japanese representation among others, not the primary one |
| Temple name and Horus name | every monarch | "Every monarch ever ... needs to have a temple name and a Horus name" |
| Christian or Muslim name | Chinese emperors | given one |
| Restored names | pharaohs | lost name parts restored; Hellenized names standardized |
| Coat of arms | everyone | a unique SVG |
| Portrait | everyone | AI-generated, released under Creative Commons, "kind of similar to ... Crusader Kings" |

Why: "trying really hard to basically make almost any sort of ancestral rites possible with any
ancestor", pre-human organisms included. "It feels superficially extremely individualistic and weird
... but in a sense, it's almost the most collectivistic thing you can do."

## Primary names (Emma, 2026-10-17)

"We are introducing a system where people have a so called "primary name" which can be anglicized, sinified, etc."
Each person has one **primary name per language or script**: the anglicized, sinified, Koreanized (and so on) form
that is shown first in that language. Older or other forms in that language stay as **aliases**, not dropped. On
order.life the primary name is the item's label in that language and the older forms are its aliases there; in
gaiad.ged it is a `TRAN` with `LANG` under the person's primary `NAME`, and the aliases are `NAME` with `TYPE AKA`.

Applied so far to Emma only: "change Emma Leonhart's name to 이명월 in Korean. This is the primary name and the old one
still stays as an alias". Q2's ko label is 이명월, and in gaiad.ged I2's primary NAME carries `TRAN 이명월` / `LANG ko`
(`PRIMARY_TRAN` in `wiki-scripts/build_gaiad_ged.py`). No earlier Hangul form of her name was on record anywhere in
the repo; her earlier name for Korean use was the hanja 李命玥 (of which 이명월 is the Korean reading), so that is
her ko alias on Q2 and stays her `NAME Emma 李命玥` / `TYPE AKA` in gaiad.ged. Not yet applied to anyone else.

## Decisions (Claude, 2026-10-15)

1. **The Western-name slot for Chinese, Japanese and Korean people:** a recorded baptismal or Western
   name where the person has one (Paul Xu Guangqi, Thomas Ahn Jung-geun's baptismal name); otherwise the
   native given name romanized (Hepburn for Japanese, pinyin for Chinese, Revised Romanization for
   Korean). Reason: she named the slot after the old "Christian name", and a given name is what fills it
   for everyone else; inventing a Western name for millions would be the invention she warns against
   elsewhere. She was "not sure what the exact method is going to be".
2. **Presidents get no temple names.** Monarchs only, following her lean: monarchs exemplify "something
   that's a bit different from modern day heads of state ... but I'm not sure about that."
3. **The canonical line** is computed, not chosen per person: the shortest descent path from the person
   to Aster (Q1) or Andromeda (Q3) in the order.life graph decides whether the first link is a father
   (patronymic) or a mother (matronymic). Ties keep the parent on the line already used by that
   person's children, so a family stays consistent. Emma's own (Q2) goes through her mother, as she said.
   *As built (2026-10-15, `wiki-scripts/canonical_line.py` → `wikibase/analysis/canonical_line.tsv`):* ties
   between two equally near parents go to the one nearer both roots, then to the mother (3,488 ties).
   People with no route to either root fall back to the parent with the larger known ancestry ("load-bearing"
   means depth upward, `CLAUDE.md`), then the mother. Emma's line is an override from her words, because
   her parents here are placeholders. Result over 106,761 records: 34,392 by father and 13,074 by mother on
   a real line to Aster or Andromeda; 35,567 father and 6,261 mother by fallback; 16,924 with no parent.
   A line reaching Aster is not a narrative line (`CLAUDE.md`, "Reaches Q1 Aster: True is not a result"):
   this decides a name piece, not a story.

## GEDCOM

"Gedcom does not really support ... proper display names. It has the weird thing with the slashes."
Experiments to run in `export_gedcom7.py`: a surname absent from the name line; the display name as the
first NAME and the schema pieces as typed NAME records (`TYPE` with `PHRASE`), checked with
`check_gedcom_roundtrip.py` against Gramps.

**Built 2026-10-15 (step 2):** `export_gedcom7.py` writes each person's patronymic or matronymic as two
typed NAME records (`TYPE OTHER`, `PHRASE patronymic, English form` / `... Arabic form`): "Margarida Rui's
daughter", "Wael ibn Nizar". Only where both given names are clean (the given part of the gedcom name, or a
one-word label) and in Latin script: 32,582 names on 16,291 people. Full labels were skipped because they
made names like "Gwyn ap Peredur ab Ednowain ... 's son". Gramps 6 keeps all of them but drops the PHRASE.
Russian-style and Welsh-style stacking, and the forms in other scripts, are later work.

**Experiments run 2026-10-15** (eight one-person variants through Gramps 6.0.8 import and GEDCOM export; the
test file is in the parent repo's gitignored `scratch/names-exp/`):

| Variant | Written | Gramps kept |
|---|---|---|
| A | `Emma /Leonhart/` | as written, GIVN Emma, SURN Leonhart |
| B | `Emma Leonhart` (no slashes) | the whole as a given name, `Emma Leonhart //` |
| C | `Emma Leonhart` + `SURN Bure` | rewritten to `Emma /Bure/`: the SURN wins and "Leonhart" is lost |
| D | `Emma //` + `SURN Bure` | `Emma /Bure/` |
| E | typed display name first, slashed name second | both, in order; the first stays primary, the second becomes "aka"; PHRASE dropped |
| F | `Gwyn /ap Peredur/` | as written, "ap Peredur" as the surname |
| G | `/Leonhart/ Emma` (surname first) | turned round to `Emma /Leonhart/`: the order is lost |
| H | `平蓮娘` with `TRAN Helensdotter` | the kanji name; the TRAN dropped |

So: a surname absent from the name line does not survive (Gramps rebuilds the line from SURN); surname-first order
does not survive; the order of NAME records and the first one's primacy do, which is why the exporter puts the
display form first and writes every other form as its own NAME rather than as TRAN or SURN tricks.

**The same eight through webtrees 2.2.4, 2026-10-25** (CLI `tree-import` and `tree-export` on a SQLite install in the
parent repo's gitignored `scratch/dl/wt/`). webtrees stores each record's raw GEDCOM, so its export gives back every
line of all eight as written (header relabelled `GEDC VERS 5.5.1`). What differs is how it reads them, from its name
index:

| Variant | webtrees shows | Sorted and searched under |
|---|---|---|
| A | Emma Leonhart | surname Leonhart, given Emma |
| B | Emma Leonhart | no surname, given "Emma Leonhart" |
| C | Emma Leonhart (the line wins for display) | surname Bure (SURN wins for the index) |
| D | Emma @N.N. (unknown surname shown) | surname Bure |
| E | both names, the typed display name first and primary | the first: no surname; the second: Leonhart |
| F | Gwyn ap Peredur | surname "Peredur": the particle "ap" is stripped for sorting |
| G | Leonhart Emma (the written order kept) | surname Leonhart, given Emma |
| H | 平蓮娘 | the kanji only; TRAN is not read as a name (only 5.5.1 ROMN, FONE and `_` tags are) |

So webtrees is the gentler program: it keeps the line as written (C and G, which Gramps rewrites), and only its
index follows SURN. It agrees with Gramps on the point the exporter relies on: the first NAME is primary and every
other NAME is kept and shown. The zh, ja and ko labels the exporter writes as TRAN are kept but not shown or searched
(the 2026-10-10 test in `research/gedcom7-programs.md` saw them flagged "Unrecognized GEDCOM code").

**The whole file through webtrees, 2026-10-25.** Two GEDCOM files went in and back out: the standalone
`export_gedcom7.py` file (131,710 people, 70,691 families) and the live `/gaiad.ged` from `build_gaiad_ged.py` (90,830
people, 35,462 families). Every person and family came back; `check_gedcom_roundtrip.py` matched 107,317 of 107,317
order.life ids in the first, with all five carriers and all 128,174 parent links, and gave the live file the same
result as the file checked against itself. The only text webtrees rewrote: long NOTE and PHRASE lines split with
CONC (invalid in 7.0, as already known), DATE keywords and months upper-cased ("about 1700" to "ABOUT 1700", "02 Feb
1866" to "02 FEB 1866"), each "@@" halved, and every negative year lost its sign. Three fixes came out of it:

- **BC years.** The live file carried 1,621 DATE lines with years like "-500" and "ABT -44" from the ancestry file.
  GEDCOM 7 has no negative years, and webtrees read each one as AD. `build_gaiad_ged.py` now writes them "500 BCE",
  and they come back from webtrees unchanged.
- **"@" in names.** The GEDCOM 7 exporter took its name helpers from the 5.5.1 one, which doubles every @. Malay names
  use @ for "alias" ("Tun Abu Saban@ishak"), so 74 lines said "@@", two literal @s to a 7.0 reader. GEDCOM 7 doubles
  only a leading @; `export_gedcom7.py` now halves what the 5.5.1 helper doubled. One label is itself damaged
  ("Pendekar Ralip @@ Deralip", Q65171) and goes with the damaged-labels work.
- **The checker.** `check_gedcom_roundtrip.py` read the Wikidata QID in a `SOUR @WIKIDATA@` PAGE as an order.life id,
  which made 74 live records look as if they matched two people; it now skips wikidata.org pages. The 39 that still
  match more than one person carry two order.life ids in the live file itself (text individuals that the entity
  resolution joined), and are the same before and after webtrees.

webtrees' own CLI importer has two bugs that the web upload does not: it does not strip a byte-order mark (the file's
HEAD is rejected), and it counts bytes read wrongly and stops early (the first try loaded 14,915 of 70,691 families
and reported success). The runs above stripped the mark and fixed the loop in the scratch copy; the per-record import
is the same code the web upload uses. RootsMagic and MyHeritage remain: they need Emma's app and account.

**Readings are not names (Emma, 2026-10-15):** "there's the transliteration of somebody's name, and then there's also,
like, their Chinese name"; "this is not the same as somebody's Chinese name." So a person can carry three separate
things, none overriding another: their real labels (zh, ja, ko from the wikibase); their **Chinese name**, the schema
name (`chinese_names.py`, typed "Chinese name (generated)"); and their **readings**, the name transcribed into ja, zh
and ko word by word from the genealogy repo's curated token table (typed "zh reading (transcription, not a Chinese
name)"), added only where no real label exists in that language.

## Order of work

The steps are in the parent repo's `queue.md`. Names come first because they are text and can be
built from the graph; arms and portraits come after, because each needs its generator.

**Built 2026-10-25 (stacking and scripts):** Welsh stacking now also where the canonical parent's label is
Welsh-styled (2,487 stacked forms over the current data); Arabic nasab stacked two generations up for records
written with ibn/bin/bint (26, Latin script only, placeholders and run-together parts refused); Devanagari
Y-putra X / Y-putrī X from real Hindi labels on both (183). Hebrew (ben/bat) and Georgian (ძე/ასული) forms are
written where both have labels in those languages, which the local labels table does not carry yet. Chinese,
Japanese and Korean phrases (Y之子X and the like) were built and taken back out: they use whole labels, and
damaged labels on parents (Darwin's father labelled with a Dutch metropolitan area) would go into some 40,000
of them. They wait on the damaged-labels work. **Put back 2026-10-25 15:40:** only from labels that match the Wikidata item the record carries
(`wiki-scripts/verify_cjk_labels.py` writes `wikibase/analysis/cjk_labels_verified.tsv`: 55,871 of 60,446 zh/ja/ko
labels; the rest are copied labels such as アーネム＝ナイメーヘン都市圏 on Iberian nobles, or records with no Wikidata
id), and only labels with no spaces, brackets or Latin letters. Forms: 鯀の子禹, 武三思之子武崇訓, 崔鳳舉之女崔氏,
Y의 아들 X. Over the standalone export: 18,284 Chinese, 15,669 Japanese and 1,401 Korean.
