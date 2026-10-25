# Footnotes in the Gaiad

Emma, 2026-10-24: "If you really want, put a goddamn footnote at the end ... Footnotes are completely fine. The Bible
has like a gazillion footnotes. Footnotes make it better. Footnotes make it more like the Bible." The verses state the
Gaiad's claims flatly; anything that explains them (who a name is, what a line refers to, how the telling differs
from other histories) goes in a footnote, never in the verse.

## The syntax

A footnote is `{{fn|plain prose}}` at the end of a verse line:

    {{c|Flavius Theodoricus}} ruled the {{p|West}}{{fn|Theodoric the Great, called Dietrich von Bern in the German legends.}}

- **A verse is a single line.** A footnote belongs to the line it ends.
- **Usually at most one per line.** More are allowed; they are numbered in order.
- **Plain prose.** No `{{c|}}`/`{{p|}}`/`{{x|}}` tags and no braces inside a footnote. Footnotes are unstructured, unlike
  the tags (`TAGS.md`), which are data for the genealogy.
- **Translations** carry footnotes in their own language, and each translation may add or drop footnotes freely: they
  are not object references.

## Where they show

- **The site** (`build.py`, `link_stanza`): a numbered marker after the line, and the notes listed under the chapter,
  each linked both ways.
- **The PDF and EPUB** (`scripts/build_book.py`): pandoc inline notes (`^[...]`), so they become real footnotes.
- **The compiled files** (`scripts/compile_gaiad.py`): kept as markup in `compiled/<month>.md`, as `^[...]` in
  `compiled/<month>_readable.md`.
- **Left out** of everything that reads the verse as verse: the plain chapter text, the RSS and Discord readings, the
  genealogy's stanza citations (`wiki-scripts/build_gaiad_ged.py`), and the rhyme checker (`tools/validate_meter.py`).
