"""
Write each person's Gaiad legacy number into their {{c|...}} tags: {{c|Alpha}} becomes {{c|4|Alpha}}, the ID form of
Gaiad/TAGS.md. Emma, 2026-10-29: "The idea is that we mass apply the existing numbers into the templates so that they
become stable".

A tag's number is the legacy number of the record its name makes in gaiad.ged (the UID build_gaiad_ged.py gives that
name, looked up in wikibase/analysis/gaiad_legacy_numbers.tsv): its own number, always. Merges are applied after, in
the GEDCOM generation (wikibase/analysis/gaiad_legacy_merges.tsv). Emma, 2026-10-29: "Aster is 1 and Alpha is 4. The
fact that 1 and 4 get merged after is the point". A name new since the freeze gets the next free number, added to the table.
Tags that already carry an ID are left as they are. Run again after new names are tagged.

    python Gaiad/scripts/stamp_legacy_ids.py
"""
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC = ROOT / "Gaiad" / "epic"
TABLE = ROOT / "wikibase" / "analysis" / "gaiad_legacy_numbers.tsv"
NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://order.life/gaiad/individual/")   # as build_gaiad_ged.py
BARE = re.compile(r"\{\{c\|([^}|]+)\}\}")


def main():
    lines = TABLE.read_text(encoding="utf-8").rstrip("\n").split("\n")
    rows = [r.split("\t") for r in lines[1:]]
    by_uid = {r[3]: int(r[0]) for r in rows if r[1] == "text" and r[3]}
    top = max(int(r[0]) for r in rows)
    new_rows, stamped, files = [], 0, 0

    def number(name):
        nonlocal top
        uid = str(uuid.uuid5(NS, name))
        if uid not in by_uid:
            top += 1
            by_uid[uid] = top
            new_rows.append(f"{top}\ttext\t{' '.join(name.split())}\t{uid}\t{top}\t")
        return by_uid[uid]

    for n in range(1, 365):
        f = EPIC / f"chapter_{n:03d}.md"
        if not f.exists():
            continue
        raw = f.read_bytes().decode("utf-8")   # line endings kept as they are

        def stamp(m):
            nonlocal stamped
            name = m.group(1).replace("\r", "").strip()   # the builder's name, so the builder's UID
            if not name:
                return m.group(0)
            stamped += 1
            return f"{{{{c|{number(name)}|{m.group(1)}}}}}"

        out = BARE.sub(stamp, raw)
        if out != raw:
            f.write_text(out, encoding="utf-8", newline="")
            files += 1
    if new_rows:
        with open(TABLE, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(new_rows) + "\n")
    print(f"{stamped} tags stamped in {files} chapters; {len(new_rows)} names new since the freeze given numbers")


if __name__ == "__main__":
    main()
