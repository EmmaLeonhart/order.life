"""Compile Gaiad chapter_NNN.md files into per-month and full-book markdown.

Outputs:
  Gaiad/epic/compiled/{slug}.md           — month compilation (raw, with {{c|...}} tags)
  Gaiad/epic/compiled/{slug}_readable.md  — month compilation (tags stripped)
  gaiad_full.md                           — all 13 months concatenated (raw)
  gaiad_full_readable.md                  — all 13 months concatenated (readable)

Convenience artifact for anyone who wants to read the whole epic in one place.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPIC = ROOT / "Gaiad" / "epic"
OUT_DIR = EPIC / "compiled"

MONTHS = [
    ("sagittarius", "Sagittarius", 1, 1, 28),
    ("capricorn",   "Capricorn",   2, 29, 56),
    ("aquarius",    "Aquarius",    3, 57, 84),
    ("pisces",      "Pisces",      4, 85, 112),
    ("aries",       "Aries",       5, 113, 140),
    ("taurus",      "Taurus",      6, 141, 168),
    ("gemini",      "Gemini",      7, 169, 196),
    ("cancer",      "Cancer",      8, 197, 224),
    ("leo",         "Leo",         9, 225, 252),
    ("virgo",       "Virgo",      10, 253, 280),
    ("libra",       "Libra",      11, 281, 308),
    ("scorpius",    "Scorpius",   12, 309, 336),
    ("ophiuchus",   "Ophiuchus",  13, 337, 364),
]

CHAR_TAG = re.compile(r"\{\{c\|([^}]+)\}\}")


def strip_char_tags(text: str) -> str:
    return CHAR_TAG.sub(r"\1", text)


def read_chapter(n: int) -> str | None:
    p = EPIC / f"chapter_{n:03d}.md"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip()


def compile_month(name: str, idx: int, start: int, end: int) -> tuple[str, int, int]:
    parts = [f"# {name} ({idx}\u5bae) - Days {start}-{end}\n"]
    written = 0
    missing = 0
    for n in range(start, end + 1):
        body = read_chapter(n)
        if body is None:
            parts.append(f"\n*Chapter {n} not yet written.*\n")
            missing += 1
            continue
        parts.append("\n" + body + "\n")
        written += 1
    return "\n".join(parts).rstrip() + "\n", written, missing


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_parts = ["# The Gaiad\n\n*A complete compilation of all written chapters.*\n"]
    total_written = 0
    total_missing = 0

    for slug, name, idx, start, end in MONTHS:
        raw, w, m = compile_month(name, idx, start, end)
        readable = strip_char_tags(raw)
        (OUT_DIR / f"{slug}.md").write_text(raw, encoding="utf-8")
        (OUT_DIR / f"{slug}_readable.md").write_text(readable, encoding="utf-8")
        all_parts.append(raw)
        total_written += w
        total_missing += m
        print(f"  {slug:12s} {w:3d} written, {m:3d} missing")

    full_raw = "\n---\n\n".join(all_parts).rstrip() + "\n"
    full_readable = strip_char_tags(full_raw)
    (ROOT / "gaiad_full.md").write_text(full_raw, encoding="utf-8")
    (ROOT / "gaiad_full_readable.md").write_text(full_readable, encoding="utf-8")

    print(f"\nTotal: {total_written} written, {total_missing} missing (of 364)")
    print(f"Wrote {len(MONTHS) * 2} month files to {OUT_DIR.relative_to(ROOT)}/")
    print("Wrote gaiad_full.md and gaiad_full_readable.md at repo root")
    return 0


if __name__ == "__main__":
    sys.exit(main())
