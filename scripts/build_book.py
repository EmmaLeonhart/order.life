"""
Assemble the English Gaiad as one Markdown book, the source of /gaiad.pdf and /gaiad.epub.

Emma, 2026-10-14: the PDF is "just the English version", and it "should also be generated as an
EPUB and all these other formats through the CI/CD". deploy.yml runs this after build.py and
turns its output into site/gaiad.epub (pandoc) and site/gaiad.pdf (pandoc with Typst).

Months are top-level headings and chapters sit under them, so the EPUB's table of contents
follows the calendar. Tags ({{c|Name}}, {{c|453|Name}}, {{p|..}}, {{x|..}}) become plain names.
Line breaks inside a stanza are kept (pandoc reads it with +hard_line_breaks).

    python scripts/build_book.py OUT.md
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPIC = ROOT / "Gaiad" / "epic"
MONTHS = ["Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini",
          "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Ophiuchus"]
# Each month is a book, with its book name as the subheading (Emma, 2026-10-20: "The book of Lehi is the book of Leo.
# All the other ones often have other meanings associated with it, or just make them ... up"). The names of 10-20 came
# from first-chapter titles and hid each book's theme; all 13 were renamed by theme with Emma on 2026-11-09, and she
# made them final the same night ("Yes, now I say all of this is final. I think it's good."):
# Sagittarius the Yarn (the mythopoetic, occult book of branching genealogies); Capricorn Kingdoms (the kingdoms of
# life as kingdoms); Aquarius Janus (it opens "This book tells of the generations blessed / Of Janus' lines"); Pisces
# Pascha (its Paschal cycle; "Easter, not Passover", and the pun kept); Aries Stone, Taurus Bronze, Gemini Iron; Cancer
# Romans ("actively putting the book of Romans as being after the Roman Empire for clever reasons"); Leo Lehi; Virgo
# Confluence (Dara Shikoh's Confluence of the Two Seas); Libra Enlightenment; Scorpio Hours (standard time, the
# appointed hour, the Y2K clocks, and the prayer-book genre); Ophiuchus Omega.
BOOKS = {"Sagittarius": "The Book of the Yarn", "Capricorn": "The Book of Kingdoms", "Aquarius": "The Book of Janus",
         "Pisces": "The Book of Pascha", "Aries": "The Book of Stone", "Taurus": "The Book of Bronze",
         "Gemini": "The Book of Iron", "Cancer": "The Book of Romans", "Leo": "The Book of Lehi",
         "Virgo": "The Book of Confluence", "Libra": "The Book of Enlightenment", "Scorpio": "The Book of Hours",
         "Ophiuchus": "The Book of Omega"}
TAG = re.compile(r"\{\{[cpx]\|(?:[^}|]*\|)?([^}|]+)\}\}")
# A footnote {{fn|...}} (Gaiad/FOOTNOTES.md) becomes a pandoc inline note, ^[...], so the EPUB and the PDF
# carry it as a real footnote (Emma, 2026-10-24: visible "in the PDF, but processed differently").
FN = re.compile(r"[ \t]*\{\{fn\|([^{}]*)\}\}")


def note(m):
    return "^[" + m.group(1).strip().replace("[", "\\[").replace("]", "\\]") + "]"


def chapter(n):
    f = EPIC / f"chapter_{n:03d}.md"
    if not f.exists():
        return None, None
    text = FN.sub(note, TAG.sub(r"\1", f.read_text(encoding="utf-8"))).replace("\r", "")
    lines = text.strip().split("\n")
    title = f"Chapter {n}"
    if lines and lines[0].startswith("#"):
        title = lines[0].lstrip("#").strip()
        lines = lines[1:]
    # Inner headings would break the month > chapter outline: keep them as bold lines.
    body = "\n".join(("**" + l.lstrip("#").strip() + "**") if l.startswith("#") else l for l in lines)
    return title, body.strip()


def main(out):
    parts = ["---",
             "title: The Gaiad",
             "subtitle: A Daily Meditation on the History of Life",
             "author: Emma Leonhart",
             "lang: en",
             "rights: https://order.life/",
             "---", ""]
    n_ch = 0
    for m, name in enumerate(MONTHS):
        parts.append(f"# {name}: {BOOKS[name]}\n")
        for d in range(1, 29):
            n = m * 28 + d
            title, body = chapter(n)
            if title is None:
                continue
            n_ch += 1
            parts.append(f"## {title}\n")
            parts.append(f"*{name} {d}, day {n} of the Gaian year*\n")
            parts.append(body + "\n")
    Path(out).write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out}: {n_ch} chapters")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "gaiad_book.md")
