"""
The invented coats of arms (the coats-of-arms item; Emma's rule, 2026-10-20, "Inherit, else invent"; who bears which
arms is worked out by gedcom_arms.py in the site build).

A fixed pool of POOL blazons, drawn with the Sodacan generator (github.com/EmmaLeonhart/Sodacan-arms-svg-generator,
checked out beside this repo's parent). They use only shapes it fully parses and draws (checked on a contact sheet),
keep the rule of tincture (no colour on colour, no metal on metal), and stay to light charges so the files stay small.
A pool rather than one design per founder keeps the files to a fixed number however many founders there are.

Writes static/arms/<sha1 of the blazon>.svg and .png (128 px, a preview; the SVG is the full drawing) for each
design, and static/arms/pool.txt (the blazons in pool order, which gedcom_arms.py reads). Run here with the
generator's dependencies (the art venv).

    python wiki-scripts/make_arms.py [path to Sodacan-arms-svg-generator]
"""
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "arms"

METALS = ["Or", "Argent"]
COLOURS = ["Azure", "Gules", "Vert", "Sable", "Purpure"]
ORDINARIES = ["a fess", "a chevron", "a pale", "a cross", "a saltire", "a chief", "a bend", "a bend sinister",
              "a pall", "a bordure", "two bars", "a canton", "an inescutcheon", "a pile", "a quarter"]
LINED = ("a fess", "a chevron", "a bend", "a pale", "a chief")
LINES = ["", "", "", " wavy", " engrailed", " indented", " embattled", " nebuly", " invected"]
CHARGES = ["mullet", "crescent", "roundel", "lozenge", "annulet", "billet", "mascle"]
COUNTS = [("a", ""), ("two", "s"), ("three", "s"), ("four", "s")]
PARTITIONS = ["Per pale", "Per fess", "Per bend", "Quarterly", "Gyronny", "Barry of six", "Bendy of six",
              "Paly of six", "Chequy"]
# Invented arms are drawn from a fixed pool, so the files stay few however many founders there are; a founder's arms
# are pool[sha1(key) % POOL]. Changing the lists or POOL changes everyone's invented arms.
POOL = 2048


def invent(seed):
    """One blazon from a seed, keeping the rule of tincture: an ordinary, charges, or both on a plain field, charges
    on an ordinary, or a parted field."""
    rng = random.Random(seed)
    metal_field = rng.random() < 0.35
    field = rng.choice(METALS if metal_field else COLOURS)
    other = lambda: rng.choice(COLOURS if metal_field else METALS)  # noqa: E731
    same = lambda: rng.choice(METALS if metal_field else COLOURS)   # noqa: E731
    line = lambda o: rng.choice(LINES) if o in LINED else ""        # noqa: E731

    def charges(n=None):
        count, s = rng.choice(COUNTS) if n is None else n
        charge = rng.choice(CHARGES)
        return f"{'an' if count == 'a' and charge[0] in 'aeiou' else count} {charge}{s}"

    form = rng.random()
    if form < 0.1:
        return f"{rng.choice(PARTITIONS)} {rng.choice(COLOURS)} and {rng.choice(METALS)}"
    if form < 0.4:
        o = rng.choice(ORDINARIES)
        return f"{field}, {o}{line(o)} {other()}"
    if form < 0.55:
        return f"{field}, {charges()} {other()}"
    if form < 0.7:
        o = rng.choice(["a fess", "a chevron"])     # "a bend between three ..." draws the bend without the charges
        return f"{field}, {o}{line(o)} between {charges(('three', 's'))} {other()}"
    if form < 0.85:
        o = rng.choice(["a chief", "a fess", "a bend", "a pale"])
        return f"{field}, on {o}{line(o)} {other()} {charges(('three', 's'))} {same()}"
    if form < 0.93:
        return f"{field}, {charges(rng.choice(COUNTS[1:]))} {other()}, a chief{line('a chief')} {other()}"
    o = rng.choice(["a fess", "a chevron", "a pale", "a cross", "a saltire", "a bend"])
    return f"{field}, {o}{line(o)} {other()}, {rng.choice(['a bordure', 'a label of three points'])} {other()}"


def pool(en):
    """POOL distinct blazons the parser fully reads, in a fixed order."""
    out, seen, i = [], set(), 0
    while len(out) < POOL:
        text = invent(f"pool/{i}")
        i += 1
        if text not in seen and en.fully_parsed(en.parse(text)):
            seen.add(text)
            out.append(text)
    return out


def arms_key(blazon):
    """The file name (without extension) of an invented blazon's SVG and PNG in static/arms/."""
    return hashlib.sha1(blazon.encode()).hexdigest()[:12]


def main():
    sodacan = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent.parent / "Sodacan-arms-svg-generator"
    sys.path.insert(0, str(sodacan))
    import resvg_py
    from arms.blazon import en
    from arms.render import render

    OUT.mkdir(parents=True, exist_ok=True)
    designs = pool(en)
    keys = {arms_key(t) for t in designs}
    for f in OUT.glob("*.*"):                          # a design the pool no longer holds
        if f.stem not in keys and f.name != "pool.txt":
            f.unlink()
    written = 0
    for text in designs:
        f = OUT / f"{arms_key(text)}.svg"
        if not (f.exists() and f.with_suffix(".png").exists()):
            svg = render(en.parse(text))
            f.write_text(svg, encoding="utf-8")
            f.with_suffix(".png").write_bytes(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=128)))
            written += 1
    (OUT / "pool.txt").write_text("\n".join(designs) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(designs)} designs in the pool, {written} drawn -> {OUT}")


if __name__ == "__main__":
    main()
