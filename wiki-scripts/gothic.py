"""Latin-script names in the Gothic alphabet (Wulfila's script, Unicode U+10330-U+1034F), for gaiad.ged.

Ported 2026-10-25 from the ostrogoth-gf repository (scripts/gothic_transliterate.py), on Emma's word: "applying
Gothic as a standard label thing". Letter for letter where Gothic has the letter, digraphs first; v and y as w
(Wulfila wrote Greek upsilon so); a/ae as ai, o-umlaut and o-slash as e, a-ring as o; accents dropped; Roman numerals
kept; German "von" as fon. Historical Goths with reconstructed names are overridden (Theodoric, *Thiudareiks).
A transliteration, not a Gothic name: the GEDCOM marks it so. Name fields only, not titles.
"""
import re
import unicodedata

LETTERS = {
    'a': '𐌰', 'b': '𐌱', 'c': '𐌺', 'd': '𐌳', 'e': '𐌴', 'f': '𐍆', 'g': '𐌲',
    'h': '𐌷', 'i': '𐌹', 'j': '𐌾', 'k': '𐌺', 'l': '𐌻', 'm': '𐌼', 'n': '𐌽',
    'o': '𐍉', 'p': '𐍀', 'q': '𐌵', 'r': '𐍂', 's': '𐍃', 't': '𐍄', 'u': '𐌿',
    'v': '𐍅', 'w': '𐍅', 'x': '𐌺𐍃', 'y': '𐍅', 'z': '𐌶', 'þ': '𐌸',
}
DIGRAPHS = [
    ('sch', '𐍃𐌺'), ('th', '𐌸'), ('ch', '𐍇'), ('ph', '𐍆'), ('qu', '𐌵'),
    ('ck', '𐌺'), ('ae', '𐌰𐌹'), ('oe', '𐌴'), ('hw', '𐍈'),
]
SPECIAL = {'ä': '𐌰𐌹', 'æ': '𐌰𐌹', 'ö': '𐌴', 'ø': '𐌴', 'œ': '𐌴', 'å': '𐍉', 'ü': '𐍅', 'ł': '𐌻'}
# Historical Goths with reconstructed Gothic names.
OVERRIDES = {  # whole name, by FamilySearch tree ID
    'PF4V-G53': '𐍆𐌻𐌰𐍅𐌹𐌿𐍃 𐌸𐌹𐌿𐌳𐌰𐍂𐌴𐌹𐌺𐍃',  # Flavius Theodoric (*Þiudareiks)
}
WORD_OVERRIDES = {  # single words, inside any name
    'theodoric': '𐌸𐌹𐌿𐌳𐌰𐍂𐌴𐌹𐌺𐍃',  # *Þiudareiks, reconstructed
}


def word(w):
    low = w.lower()
    if re.fullmatch(r'[IVXLC]+', w):
        return w
    if low in WORD_OVERRIDES:
        return WORD_OVERRIDES[low]
    if low == 'von':
        return '𐍆𐍉𐌽'
    out, i = [], 0
    while i < len(low):
        for dg, g in DIGRAPHS:
            if low.startswith(dg, i):
                out.append(g)
                i += len(dg)
                break
        else:
            ch = low[i]
            if ch in SPECIAL:
                out.append(SPECIAL[ch])
            else:
                base = unicodedata.normalize('NFD', ch)[0]
                out.append(LETTERS.get(base, ch))
            i += 1
    return ''.join(out)


def gothic(name, fs_id=''):
    if fs_id in OVERRIDES:
        return OVERRIDES[fs_id]
    return re.sub(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-žþÞ]+", lambda m: word(m.group(0)), name)


OVERRIDES.update({
    "Q109383": OVERRIDES["PF4V-G53"],   # Theodoric the Great, the Gaiad's record
    "S41792": OVERRIDES["PF4V-G53"],    # the same man, from her FamilySearch tree
    # Emma's own Gothic name, her choice (2026-10-25, ostrogoth-gf); 命玥 stays as it is
    "Q2": "𐌴𐌼𐌼𐌰 𐌷𐌹𐌼𐌹𐌺𐍉 𐌷𐌴𐌻𐌴𐌽𐍃𐌳𐍉𐍄𐍄𐌴𐍂 𐍆𐍉𐌽 𐌱𐌿𐍂𐌴𐌿𐍃 𐌻𐌴𐍉𐌽𐌷𐌰𐍂𐍄 命玥",
    "PFR5-LDS": "𐌴𐌼𐌼𐌰 𐌷𐌹𐌼𐌹𐌺𐍉 𐌷𐌴𐌻𐌴𐌽𐍃𐌳𐍉𐍄𐍄𐌴𐍂 𐍆𐍉𐌽 𐌱𐌿𐍂𐌴𐌿𐍃 𐌻𐌴𐍉𐌽𐌷𐌰𐍂𐍄 命玥",  # her FamilySearch id
    "@I2@": "𐌴𐌼𐌼𐌰 𐌷𐌹𐌼𐌹𐌺𐍉 𐌷𐌴𐌻𐌴𐌽𐍃𐌳𐍉𐍄𐍄𐌴𐍂 𐍆𐍉𐌽 𐌱𐌿𐍂𐌴𐌿𐍃 𐌻𐌴𐍉𐌽𐌷𐌰𐍂𐍄 命玥",  # I2 in /gaiad.ged
})


def name_part(name):
    """The name without its titles: the part before the first comma, without trailing roman-numeral dots."""
    return re.sub(r"\s+", " ", name.split(",")[0]).strip()


GOTHIC_RE = re.compile("[\U00010330-\U0001034F]")


def add_names(lines):
    """Give every INDI of a GEDCOM (a list of lines) a Gothic NAME after its first NAME and that NAME's sub-lines.
    The record's order.life id (REFN of TYPE order.life) or FamilySearch id (_FSFTID, EXID) picks an override.
    Returns (lines, count)."""
    out, rec, n = [], [], 0

    def flush():
        nonlocal n
        if not rec or not re.match(r"0 @[^@]+@ INDI", rec[0]):
            out.extend(rec)
            return
        ids = [b[7:].strip() for b, c in zip(rec, rec[1:] + [""]) if b.startswith("1 REFN ") and c.strip() == "2 TYPE order.life"]
        ids += [b.split(" ", 2)[2].split()[0] for b in rec if b.startswith(("1 _FSFTID ", "1 EXID "))]
        ids.append(rec[0].split()[1])   # the xref: I2 is Emma in /gaiad.ged
        first = next((i for i, b in enumerate(rec) if b.startswith("1 NAME ")), None)
        if first is None:
            out.extend(rec)
            return
        primary = rec[first][7:].replace("/", "").strip()
        override = next((OVERRIDES[i] for i in ids if i in OVERRIDES), None)
        got = override or gothic(name_part(primary))
        have = {b[7:].strip() for b in rec if b.startswith("1 NAME ")}
        if not GOTHIC_RE.search(got) or got in have:
            out.extend(rec)
            return
        end = first + 1
        while end < len(rec) and not rec[end].startswith(("0 ", "1 ")):
            end += 1
        phrase = "Gothic name" if override else "Gothic script (transliterated)"
        out.extend(rec[:end] + [f"1 NAME {got}", "2 TYPE OTHER", f"3 PHRASE {phrase}"] + rec[end:])
        n += 1

    for line in lines:
        if line.startswith("0 "):
            flush()
            rec = []
        rec.append(line)
    flush()
    return out, n
