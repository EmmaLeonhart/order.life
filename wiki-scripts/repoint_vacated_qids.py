"""Rewrite genealogy claims that name a vacated qid so they name the survivor instead.

    python wiki-scripts/repoint_vacated_qids.py Q72693           # dry run
    python wiki-scripts/repoint_vacated_qids.py Q72693 --write   # apply

Takes one or more vacated qids. For every file holding a P47/P48/P20/P42 claim naming one,
the claim is repointed to what redirects.tsv resolves it to -- and if the survivor is
ALREADY named in the same role on that record, the duplicate is dropped rather than
repointed, because two claims naming one person is not two parents.

GRAPH-NEUTRAL BY CONSTRUCTION, and the verify step proves it rather than asserting it.
extract_genealogy.py canonicalises both endpoints of every edge through the same redirect
map before writing edges.tsv, so a claim naming Q72693 and a claim naming Q72615 build the
identical edge. Repointing changes the record and cannot change the graph. Run
verify_repair.py around it anyway; expect compare_tangles and compare_depth to report
nothing at all, and treat any movement as a bug in this script.

WHY BOTHER, IF THE GRAPH DOES NOT MOVE

merge_cluster.py's rule is that after a merge no file may still claim the loser's qid,
because vacating a qid some file still claims lets that file win it and inject its claims
-- the phantom Cato 2-cycle came from exactly that. The rule is enforced at merge time and
by nothing afterwards.

Meanwhile the residue costs three things. A record listing one person twice in a role reads
as a two-parent defect it does not have, and lands in qa_same_role_parents.tsv and
children_over_2_parents as a false positive. Any script comparing raw qids can be fooled by
the spelling in either direction -- apply_lepidus_cut.py silently dropped nothing for eight
days, add_bridge_edges.py would have silently added a duplicate. And if a vacated qid is
ever re-issued, every stale claim starts pointing at a different person.

Shadow-aware: every file claiming a touched record's qid is rewritten, or the edit reverts
the moment that file stops being the numerically-lowest claimant.
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

ROLES = {"P47": "father", "P48": "mother", "P20": "child", "P42": "spouse"}


def redirect_map():
    out = {}
    with open(REDIRECTS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            out[r["from_qid"]] = r["to_qid"]
    return out


def resolve(qid, red):
    seen = set()
    while qid in red and qid not in seen:
        seen.add(qid)
        qid = red[qid]
    return qid


def detect_indent(text, default=2):
    """The indent width this file already uses, so rewriting it does not reformat it.

    The dump's convention is indent=2 -- measured 2026-08-15 over a 400-file sample of
    tracked items: 399 at indent 2, 1 at indent 1. The odd ones out are damage. Every
    apply_*.py in this repo writes json.dumps(..., indent=1), so each repair silently
    reformats every file it touches: the six-file Q72693 repoint produced roughly 3,000
    changed lines for six semantic edits, and doing that to the 1,711 files in the
    dump-wide pass would have buried the actual change under millions of lines of noise.

    Sniffing the existing width rather than hardcoding 2 also means a genuinely mixed
    dump stays put instead of churning back and forth between passes.
    """
    for line in text.split("\n")[1:]:
        stripped = len(line) - len(line.lstrip(" "))
        if stripped > 0:
            return stripped
    return default


def write_item(path, data, indent):
    """Write an item file in place, preserving its formatting.

    newline="\\n" is explicit because Path.write_text on Windows translates \\n to \\r\\n,
    which .gitattributes normalises away at commit time but which makes every local diff
    and every `cat -A` misleading in the meantime.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=indent) + "\n")


def target_of(claim):
    v = ((claim.get("mainsnak") or {}).get("datavalue") or {}).get("value")
    return v.get("id") if isinstance(v, dict) and v.get("id") else None


def repoint(data, vacated, red):
    """Repoint or drop claims naming `vacated`. Returns [(pid, action, target)]."""
    log = []
    for pid in ROLES:
        claims = (data.get("claims") or {}).get(pid)
        if not claims:
            continue
        survivor = resolve(vacated, red)
        # What the record already names in this role, by canonical identity, excluding the
        # vacated spellings themselves -- so we can tell a duplicate from a repoint.
        already = {resolve(t, red) for c in claims
                   if (t := target_of(c)) and t != vacated}
        keep = []
        for c in claims:
            t = target_of(c)
            if t != vacated:
                keep.append(c)
                continue
            if survivor in already:
                log.append((pid, "drop-duplicate", survivor))
                continue
            c["mainsnak"]["datavalue"]["value"]["id"] = survivor
            if survivor[1:].isdigit():
                c["mainsnak"]["datavalue"]["value"]["numeric-id"] = int(survivor[1:])
            already.add(survivor)
            keep.append(c)
            log.append((pid, "repoint", survivor))
        if keep:
            data["claims"][pid] = keep
        else:
            del data["claims"][pid]
    return log


def candidate_files(targets):
    """Files mentioning any of `targets`, found with `git grep`.

    USE git grep, NOT a Python pass over wikibase/items/. Reading and parsing the 164k
    item files takes upwards of fifteen minutes and gets killed by any bounded runner
    before it finishes; `git grep -l` over the same tree answers in about twelve seconds,
    because the files are tracked and git does not have to stat them one at a time. That
    is a 70x difference on the same question, measured 2026-08-15.

    The trade is that git grep only sees TRACKED files. That is the right universe here --
    an untracked item file is not part of the dump and would not survive a clone -- but it
    is a real limit, so uncommitted new items are invisible to this and the caller is told.
    """
    pattern = "|".join(f'"{q}"' for q in sorted(targets))
    proc = subprocess.run(
        ["git", "grep", "-l", "-E", pattern, "--", "wikibase/items/*.json"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    # git grep exits 1 when there are no matches, which is not an error here.
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"git grep failed ({proc.returncode}): {proc.stderr.strip()}")
    names = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    print(f"git grep: {len(names)} tracked file(s) mention "
          f"{', '.join(sorted(targets))}")
    return [ROOT / n for n in names if (ROOT / n).exists()]


def owners_and_shadows(red):
    """qid -> every file stem whose contents claim it."""
    stems = collections.defaultdict(set)
    for to_qid in set(red.values()):
        stems[to_qid].add(to_qid)
    for frm, to in red.items():
        stems[to].add(frm)
    return stems


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    red = redirect_map()
    for q in args:
        if q not in red:
            print(f"ABORT: {q} is not in redirects.tsv -- it is not a vacated qid.")
            return 1

    targets = set(args)
    hits = candidate_files(targets)
    print(f"  {len(hits)} file(s) hold a genealogy claim naming them\n")

    edits = {}
    for path in hits:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        log = []
        for q in args:
            log += repoint(data, q, red)
        if log:
            edits[path.name] = (data, log, detect_indent(text))
            owner = data.get("id") or path.stem
            print(f"  {path.name:<18} (id {owner})")
            for pid, action, tgt in log:
                print(f"      {pid} {ROLES[pid]:<7} {action:<15} -> {tgt}")

    if not edits:
        print("nothing to do -- no genealogy claim names a vacated qid here.")
        return 0

    # Every file claiming a touched record must end up identical, or the edit reverts the
    # moment a different file becomes the numerically-lowest claimant for that qid.
    stems = owners_and_shadows(red)
    touched_owners = {d.get("id") or n[:-5] for n, (d, _, _i) in edits.items()}
    missing = []
    for owner in sorted(touched_owners):
        for stem in sorted(stems.get(owner, {owner})):
            p = ITEMS / f"{stem}.json"
            if p.exists() and p.name not in edits:
                missing.append(p)
    if missing:
        print(f"\n{len(missing)} shadow file(s) claim a touched record and will be "
              f"rewritten from it:")
        for p in missing:
            print(f"      {p.name}")

    print(f"\n{len(edits)} file(s) to write"
          + (f", {len(missing)} shadow(s) to sync." if missing else "."))
    if not write:
        print("Dry run. Re-run with --write to apply.")
        return 0

    for name, (data, _, indent) in edits.items():
        write_item(ITEMS / name, data, indent)
    for p in missing:
        text = p.read_text(encoding="utf-8")
        owner = json.loads(text).get("id") or p.stem
        src = next((d for n, (d, _, _i) in edits.items()
                    if (d.get("id") or n[:-5]) == owner), None)
        if src is not None:
            # Match the SHADOW's own formatting, not the source record's -- they are
            # separate files and each should stay as it was written.
            write_item(p, src, detect_indent(text))
    print(f"Wrote {len(edits) + len(missing)} file(s).")

    # Re-read from disk rather than from the objects held in memory -- the point is to
    # check what was written, not what was intended.
    bad = []
    for path in list(hits) + missing:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        for pid in ROLES:
            for c in (data.get("claims") or {}).get(pid, []):
                if target_of(c) in targets:
                    bad.append(f"{path.name} still has {pid} -> {target_of(c)}")
    if bad:
        print("\nVERIFY FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"Verified across {len(hits) + len(missing)} file(s): none names these qids now.")
    print("NOTE: that is every file the audit found, not an independent sweep. Re-run\n"
          "      vacated_qid_audit.py to confirm the dump-wide count went to zero.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
