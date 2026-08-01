"""Pre-commit gate: a record's shadows must agree with it.

39,527 qids in this dump are claimed by more than one file, and extract_genealogy.py keeps
only the numerically-lowest QID per qid. Editing the canonical file alone leaves stale
shadows: the fix looks applied, but is silently reverted the moment that file stops winning.
That happened on 2026-07-30 to ten applied repairs at once -- Q74698's shadows still carried
the Trojan children the unmerge had removed.

This checks ONLY the qids touched by the staged item files, so it runs in well under a
second. The expensive gates -- check_invariants.py (needs a regenerated extract) and
shadow_audit.py (reads all 164k files) -- are not run here; the hook prints a reminder.

    python wiki-scripts/check_staged_shadows.py            # check staged files
    python wiki-scripts/check_staged_shadows.py Q74698 ...  # check named qids instead

Exit 1 if any staged record disagrees with a file that shares its qid.
"""

import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "wikibase" / "items"
REDIRECTS = ROOT / "wikibase" / "analysis" / "redirects.tsv"

GEN = ("P20", "P47", "P48")
NAMES = {"P20": "child", "P47": "father", "P48": "mother"}


def staged_items():
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except Exception:
        return []
    return [Path(p).stem for p in out.splitlines()
            if p.startswith("wikibase/items/") and p.endswith(".json")]


def load(stem):
    p = ITEMS / f"{stem}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def vals(d, pid):
    out = set()
    for c in (d.get("claims") or {}).get(pid, []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict) and v.get("id"):
            out.add(v["id"])
    return out


def siblings_by_qid():
    """qid -> [filenames claiming it], from the committed redirect map."""
    out = collections.defaultdict(set)
    if REDIRECTS.exists():
        with open(REDIRECTS, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                out[r["to_qid"]].add(r["from_qid"])
                out[r["to_qid"]].add(r["to_qid"])
    return out


def main():
    args = [a for a in sys.argv[1:] if a.startswith("Q")]
    stems = args or staged_items()
    if not stems:
        return 0

    sib = siblings_by_qid()
    problems = []
    checked = 0
    for stem in stems:
        d = load(stem)
        if not d:
            continue
        qid = d.get("id") or stem
        family = set(sib.get(qid, set())) | {stem, qid}
        family = {f for f in family if (ITEMS / f"{f}.json").exists()}
        if len(family) < 2:
            continue
        checked += 1
        # every file claiming this qid must agree on the genealogical claims
        ref = None
        for f in sorted(family, key=lambda x: int(x[1:])):
            fd = load(f)
            if not fd or (fd.get("id") or f) != qid:
                continue          # not actually claiming this qid
            cur = {p: vals(fd, p) for p in GEN}
            if ref is None:
                ref, refname = cur, f
                continue
            for p in GEN:
                if cur[p] != ref[p]:
                    # report only the difference -- these sets run to 60+ entries and
                    # printing both in full buries the one value that actually differs
                    only_f = sorted(cur[p] - ref[p])
                    only_r = sorted(ref[p] - cur[p])
                    bits = []
                    if only_f:
                        bits.append(f"{f}.json has {only_f}")
                    if only_r:
                        bits.append(f"{refname}.json has {only_r}")
                    problems.append(
                        f"{qid} {NAMES[p]}: " + " ; ".join(bits) + " (the other does not)")

    if problems:
        sys.stderr.write("\nBLOCKED: staged records have shadow files that disagree.\n")
        sys.stderr.write("Editing the canonical file alone is not durable -- the fix reverts\n")
        sys.stderr.write("as soon as that file stops being the numerically-lowest claimant.\n\n")
        for p in problems[:20]:
            sys.stderr.write(f"  {p}\n")
        if len(problems) > 20:
            sys.stderr.write(f"  ... and {len(problems) - 20} more\n")
        sys.stderr.write("\nFix: rewrite every file claiming the qid, then re-stage.\n")
        sys.stderr.write("Bypass only if you mean it: git commit --no-verify\n\n")
        return 1

    if checked:
        print(f"shadow gate: {checked} staged record(s) with shadows, all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
