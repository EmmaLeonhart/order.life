#!/usr/bin/env python3
"""Meter check for the Gaiad, run by CI (.github/workflows/gaiad-meter.yml).

The verse form (order.life CLAUDE.md, "Gaiad verse form"; Emma, 2026-11-03 and 2026-11-06): every chapter is in
quatrains, ten syllables a line, rhymed ABAB. There is no stress requirement (Gaian stanzas, not iambic pentameter).

It checks; it rewrites nothing.

Pronunciation is General American English from the CMU Pronouncing Dictionary (the `cmudict` package, or a
cmudict.dict file named by the GAIAD_CMUDICT environment variable). Where CMUdict gives several pronunciations of a
word, any of them is accepted, so a line passes if some reading of it has ten syllables. Words CMUdict lacks (names
and the like) are looked up in our own dictionary, Gaiad/pronunciation.tsv (`word<TAB>ARPAbet`); words in neither
are counted by a spelling guess and listed in the report as unknown, so they can be added there.

It also builds a corpus of the Gaiad: word frequencies from most to least common, the hapax legomena, and the
unknown words, written to the output directory with the per-chapter report.

Usage:
  python Gaiad/epic/tools/validate_meter.py                 all chapters, report to stdout
  python Gaiad/epic/tools/validate_meter.py chapter_001.md  one chapter
  python Gaiad/epic/tools/validate_meter.py --out DIR       also write report.md, chapters.tsv, corpus files
  --report-only                                             exit 0 even when chapters fail
"""

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

EPIC = Path(__file__).resolve().parent.parent
GAIAD = EPIC.parent
OWN_DICT = GAIAD / "pronunciation.tsv"

TAG = re.compile(r"\{\{(?:c|p|x)\|(?:[^{}|]*\|)*([^{}|]*)\}\}")
FOOTNOTE = re.compile(r"[ \t]*\{\{fn\|[^{}]*\}\}")
WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ɏ0-9]+(?:['’][A-Za-zÀ-ÖØ-öø-ɏ]+)*")
VOWEL_PHONE = re.compile(r"\d$")


def load_dictionaries():
    prons = {}
    try:
        import cmudict  # pip install cmudict
        for w, ps in cmudict.dict().items():
            prons[w] = [p for p in ps]
    except ImportError:
        path = os.environ.get("GAIAD_CMUDICT")
        if not path:
            sys.exit("No pronunciation dictionary: pip install cmudict, or set GAIAD_CMUDICT to a cmudict.dict file.")
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip() or line.startswith(";;;"):
                    continue
                line = line.split("#", 1)[0].strip()
                head, *phones = line.split()
                w = re.sub(r"\(\d+\)$", "", head).lower()
                prons.setdefault(w, []).append(phones)
    if OWN_DICT.exists():
        with open(OWN_DICT, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if not line or "\t" not in line:
                    continue
                w, phones = line.split("\t", 1)
                prons.setdefault(w.strip().lower(), []).insert(0, phones.split())
    return prons


def guess_syllables(word):
    """Spelling guess, only for words in no dictionary (they are reported as unknown)."""
    w = word.lower()
    if w.isdigit():
        return max(1, len(w))
    groups = re.findall(r"[aeiouyàáâãäåæèéêëìíîïòóôõöøùúûüýāēīōū]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    return max(1, n)


class Lexicon:
    def __init__(self, prons):
        self.prons = prons
        self.unknown = Counter()

    def lookup(self, word):
        """Pronunciations of a word as lists of phones, or None if unknown."""
        w = word.lower().replace("’", "'")
        if w in self.prons:
            return self.prons[w]
        if w.endswith("'s") and w[:-2] in self.prons:
            out = []
            for p in self.prons[w[:-2]]:
                last = re.sub(r"\d", "", p[-1]) if p else ""
                out.append(p + (["IH0", "Z"] if last in ("S", "Z", "SH", "ZH", "CH", "JH") else ["Z"]))
            return out
        if w.endswith("s'") and w[:-1] in self.prons:
            return self.prons[w[:-1]]
        # a compound of two dictionary words (catgirl = cat + girl), each part at least three letters
        for i in range(3, len(w) - 2):
            a, b = w[:i], w[i:]
            if a in self.prons and b in self.prons:
                return [pa + pb for pa in self.prons[a][:2] for pb in self.prons[b][:2]]
        return None

    def syllable_options(self, word):
        ps = self.lookup(word)
        if ps is None:
            self.unknown[word.lower()] += 1
            return {guess_syllables(word)}, False
        return {sum(1 for ph in p if VOWEL_PHONE.search(ph)) for p in ps}, True

    def rhyme_parts(self, word):
        """Phones from the last stressed vowel to the end, stress marks dropped."""
        ps = self.lookup(word)
        if ps is None:
            return {"~" + word.lower()[-3:]}, False
        parts = set()
        for p in ps:
            idx = [i for i, ph in enumerate(p) if ph[-1:] in "12"]
            if not idx:
                idx = [i for i, ph in enumerate(p) if VOWEL_PHONE.search(ph)]
            start = idx[-1] if idx else 0
            parts.add(" ".join(re.sub(r"\d", "", ph) for ph in p[start:]))
        return parts, True


def clean(line):
    line = FOOTNOTE.sub("", line)
    return TAG.sub(r"\1", line)


def words_of(line):
    out = []
    for w in WORD.findall(clean(line)):
        out.extend(part for part in re.split(r"-", w) if part)
    return out


def stanzas_of(path):
    """Blank-line-separated groups of verse lines; headings skipped. Each line is (line number, text)."""
    stanzas, cur = [], []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = raw.strip()
        if s.startswith("#"):
            continue
        if not s:
            if cur:
                stanzas.append(cur)
                cur = []
            continue
        cur.append((n, s))
    if cur:
        stanzas.append(cur)
    return stanzas


def line_syllables(lex, text):
    totals = {0}
    known = True
    for w in words_of(text):
        opts, k = lex.syllable_options(w)
        known &= k
        totals = {t + o for t in totals for o in opts}
    return totals, known


def check_chapter(lex, path):
    issues = []
    lines = bad_syll = bad_shape = bad_rhyme = 0
    for st in stanzas_of(path):
        if len(st) != 4:
            bad_shape += 1
            issues.append(f"line {st[0][0]}: stanza of {len(st)} lines, not a quatrain")
        for n, text in st:
            lines += 1
            totals, known = line_syllables(lex, text)
            if 10 not in totals:
                bad_syll += 1
                shown = "/".join(str(t) for t in sorted(totals)[:4])
                issues.append(f"line {n}: {shown} syllables, not 10{'' if known else ' (has unknown words)'}: {clean(text)}")
        if len(st) == 4:
            ends = []
            for n, text in st:
                ws = words_of(text)
                ends.append((n, ws[-1] if ws else ""))
            parts = [lex.rhyme_parts(w)[0] for _, w in ends]

            def r(a, b):
                return bool(parts[a] & parts[b])

            if not (r(0, 2) and r(1, 3)):
                bad_rhyme += 1
                if r(0, 1) and r(2, 3):
                    scheme = "AABB (couplets)"
                elif r(0, 3) and r(1, 2):
                    scheme = "ABBA"
                elif r(0, 2) or r(1, 3):
                    scheme = "half rhymed"
                else:
                    scheme = "unrhymed"
                shown = " / ".join(w for _, w in ends)
                issues.append(f"line {st[0][0]}: stanza is {scheme}, not ABAB: {shown}")
            for a, b in ((0, 2), (1, 3)):
                (na, wa), (nb, wb) = ends[a], ends[b]
                if wa and wa.lower() == wb.lower():
                    issues.append(f"lines {na}/{nb}: \"{wa}\" rhymed with itself (identical word; not a failure)")
    passed = lines > 0 and bad_syll == 0 and bad_shape == 0 and bad_rhyme == 0
    return {"lines": lines, "bad_syllables": bad_syll, "bad_stanzas": bad_shape, "bad_rhymes": bad_rhyme,
            "passed": passed, "issues": issues}


def chapter_files(arg):
    if arg:
        p = Path(arg)
        if not p.exists():
            p = EPIC / arg
        return [p]
    return sorted(EPIC.glob("chapter_[0-9]*.md"), key=lambda p: int(re.search(r"\d+", p.stem).group()))


def build_corpus(files):
    freq = Counter()
    for p in files:
        for st in stanzas_of(p):
            for _, text in st:
                freq.update(w.lower() for w in words_of(text))
    return freq


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapter", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    lex = Lexicon(load_dictionaries())
    files = chapter_files(args.chapter)
    results = [(p, check_chapter(lex, p)) for p in files]
    passed = [p for p, r in results if r["passed"]]

    for p, r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{status} {p.name}: {r['lines']} lines, {r['bad_syllables']} not ten syllables, "
              f"{r['bad_stanzas']} not quatrains, {r['bad_rhymes']} stanzas not ABAB")
        if args.chapter:
            for i in r["issues"]:
                print("  " + i)
    print(f"\n{len(passed)} of {len(results)} chapters pass.")

    if args.out:
        out = Path(args.out)
        (out / "chapters").mkdir(parents=True, exist_ok=True)
        with open(out / "chapters.tsv", "w", encoding="utf-8") as f:
            f.write("chapter\tpassed\tlines\tnot_ten_syllables\tnot_quatrains\tstanzas_not_abab\n")
            for p, r in results:
                f.write(f"{p.stem}\t{r['passed']}\t{r['lines']}\t{r['bad_syllables']}\t{r['bad_stanzas']}\t{r['bad_rhymes']}\n")
                (out / "chapters" / f"{p.stem}.txt").write_text("\n".join(r["issues"]) + "\n", encoding="utf-8")
        freq = build_corpus(files)
        with open(out / "word_frequencies.tsv", "w", encoding="utf-8") as f:
            f.write("word\tcount\tin_dictionary\n")
            for w, c in freq.most_common():
                f.write(f"{w}\t{c}\t{lex.lookup(w) is not None}\n")
        hapax = sorted(w for w, c in freq.items() if c == 1)
        (out / "hapax_legomena.txt").write_text("\n".join(hapax) + "\n", encoding="utf-8")
        with open(out / "unknown_words.tsv", "w", encoding="utf-8") as f:
            f.write("word\tcount\n")
            for w, c in lex.unknown.most_common():
                f.write(f"{w}\t{c}\n")
        total_lines = sum(r["lines"] for _, r in results)
        ten = total_lines - sum(r["bad_syllables"] for _, r in results)
        report = [
            "# Gaiad meter check", "",
            f"**{len(passed)} of {len(results)} chapters pass** (quatrains, ABAB rhyme, ten syllables a line).", "",
            f"- Lines: {total_lines}; ten syllables: {ten} ({100 * ten / max(1, total_lines):.1f}%)",
            f"- Corpus: {sum(freq.values())} words, {len(freq)} distinct, {len(hapax)} hapax legomena",
            f"- Words in no dictionary: {len(lex.unknown)} distinct (add them to Gaiad/pronunciation.tsv)", "",
            "| Chapter | Pass | Lines | Not 10 syllables | Not quatrains | Stanzas not ABAB |",
            "|---|---|---|---|---|---|",
        ]
        for p, r in results:
            report.append(f"| {p.stem} | {'yes' if r['passed'] else 'no'} | {r['lines']} | {r['bad_syllables']} | "
                          f"{r['bad_stanzas']} | {r['bad_rhymes']} |")
        (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    if not args.report_only and len(passed) < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
