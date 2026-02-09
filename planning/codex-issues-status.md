# Codex mistakes status (from `codex mistakes.txt`)

This file tracks the issues listed in `codex mistakes.txt` and whether they are resolved.

## Status legend
- ✅ Resolved
- ⚠️ Partially resolved / in progress
- ❌ Not resolved

## 1) High-level outcome mismatch (multilingual “meat”)
**Issue:** non-English versions contained lots of English “meat”, largely because significant prose was hardcoded in templates rather than in i18n JSON.

**Status:** ⚠️ In progress.
- i18n JSON coverage is good for the existing key set.
- We’ve begun moving hardcoded template prose into i18n (`gaian-era`, `week-index`, `wiki-redirect`).
- Remaining large blocks still to migrate/translate: `calendar/weekday.html` and `templates/sections/*.html`.

## 2) Translation coverage gaps
- **French**: `fr.json` is translated. ✅
- **RU/UK month names**: localized month names have been applied (no longer Latin). ✅
- **HI/AR**: content exists and builds; further stylistic review can be done, but no missing keys vs English. ✅

(We validate key parity with `tools/i18n_audit.py`.)

## 3) Proper-name handling (ꙮ and other names)
- **RU/UK**: site titles use the multiocular o (ꙮ). ✅
- **Localized proper nouns everywhere**: glossary introduced at `content/glossary.json` and passed into templates as `g` for consistent localized naming. ⚠️ In progress (templates still need to be updated to consume `g.*` broadly).

## 4) Encoding / mojibake
- Builder hardens stdout/stderr UTF-8 on Windows to reduce cp1252 issues. ✅
- Repo content is UTF-8 (no remaining mojibake patterns detected in en.json). ✅

## 5) Process/tooling churn
- A stable translation audit script exists (`tools/i18n_audit.py`). ✅
- We now build into `site_tmp/` and swap into `site/` to avoid partial builds during preview. ✅

## Next concrete work
- Finish migrating all remaining hardcoded English prose into i18n keys and translate across all supported languages.
- Then spot-check key pages per language (home, calendar, scripture, weekday pages).
