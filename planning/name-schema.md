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

## GEDCOM

"Gedcom does not really support ... proper display names. It has the weird thing with the slashes."
Experiments to run in `export_gedcom7.py`: a surname absent from the name line; the display name as the
first NAME and the schema pieces as typed NAME records (`TYPE` with `PHRASE`), checked with
`check_gedcom_roundtrip.py` against Gramps.

## Order of work

The steps are in the parent repo's `queue.md`. Names come first because they are text and can be
built from the graph; arms and portraits come after, because each needs its generator.
