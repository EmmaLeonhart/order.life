"""The verification ritual for a genealogy repair, as one command.

    python wiki-scripts/verify_repair.py --snapshot     # BEFORE: freeze the current edges.tsv
    ... make the repair ...
    python wiki-scripts/verify_repair.py                # AFTER: regenerate, then run every gate

With no positional argument the AFTER run compares against the snapshot the BEFORE run
wrote. Pass one path to compare against some other snapshot instead. Pass TWO paths to
compare an arbitrary before/after pair -- which is how you can exercise the failure path
without touching the dump, and note that check_invariants.py still reads the live extracts
in that mode because it has no before/after form. Exits non-zero if any gate fails, and
says which.

WHY THIS EXISTS

Every gate this runs already existed. The failure was that running them was a ritual held
in prose -- queue.md and cycle_policy.md described the steps, and whoever was mid-repair
had to remember all of them in the right order. On 2026-07-31 a cut went in having passed
compare_tangles.py, because compare_depth.py was written to catch exactly that class of
mistake and then never wired to anything. It stripped 263 generations of ancestry off the
Scipio line and was reverted the same day. A gate nobody runs is not a gate.

So: one command, all of them, in order, with the snapshot handled for you.

WHAT IT RUNS

  1. extract_genealogy.py   regenerate the TSVs -- they go stale the moment items change,
                            and every gate below reads them, so a stale extract makes all
                            of this measure the previous state. Skip with --skip-extract
                            only if you have already regenerated since the last edit.
  2. compare_tangles.py     SCC partitions before vs after: tangles introduced, removed,
                            reshaped. Measures WIDTH. Fails if a repair introduces one.
  3. compare_depth.py       ancestral depth per record before vs after. Measures DEPTH,
                            which is what load-bearing means here. Fails if any record
                            loses more than --max-loss levels (default 5).
  4. check_invariants.py    the four standing invariants against the committed baseline.

WHAT IT DOES NOT RUN, deliberately

Shadow consistency. `.githooks/pre-commit` runs check_staged_shadows.py over exactly the
records you staged, which is both narrower and better targeted than anything this could do
from an edges.tsv pair -- it is the gate that catches an edit applied to the canonical file
alone. Install it once per checkout: `git config core.hooksPath .githooks`. This script
prints a reminder rather than duplicating it.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "wiki-scripts"
EDGES = ROOT / "wikibase" / "analysis" / "edges.tsv"
SNAPSHOT = ROOT / "wikibase" / "analysis" / ".repair_snapshot.tsv"


def run(name, args, label):
    """Run one gate. Returns its exit code; streams nothing, prints the tail."""
    print(f"\n{'=' * 72}\n  {label}\n{'=' * 72}")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    lines = out.rstrip("\n").split("\n")
    # the gates put their verdict at the end; show enough context to read it
    for line in lines[-40:] if len(lines) > 40 else lines:
        print(f"  {line}")
    if len(lines) > 40:
        print(f"  ... ({len(lines) - 40} earlier lines suppressed)")
    print(f"\n  -> exit {proc.returncode}")
    return proc.returncode


def take_snapshot():
    if not EDGES.exists():
        print(f"FAIL: {EDGES} does not exist -- run extract_genealogy.py first.")
        return 1
    shutil.copyfile(EDGES, SNAPSHOT)
    rows = sum(1 for _ in SNAPSHOT.open(encoding="utf-8")) - 1
    print(f"snapshot taken: {SNAPSHOT.relative_to(ROOT)}  ({rows:,} edges)")
    print("\nMake the repair, then run:  python wiki-scripts/verify_repair.py")
    return 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]

    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    if "--snapshot" in argv:
        return take_snapshot()

    flags = [a for a in argv if a.startswith("--")]
    positional = [a for a in argv if not a.startswith("--")]
    skip_extract = "--skip-extract" in flags
    max_loss = next((f for f in flags if f.startswith("--max-loss=")), None)

    before = Path(positional[0]) if positional else SNAPSHOT
    after = Path(positional[1]) if len(positional) > 1 else None
    if not before.exists():
        print(f"FAIL: no snapshot at {before}.")
        print("Take one BEFORE the repair with:  "
              "python wiki-scripts/verify_repair.py --snapshot")
        return 2
    if after is not None and not after.exists():
        print(f"FAIL: no such after-file: {after}")
        return 2

    print(f"comparing against snapshot: {before}")
    if after is not None:
        print(f"explicit after-file:        {after}")
        print("NOTE: check_invariants.py has no before/after form and still reads the live")
        print("      extracts, so its verdict describes the working tree, not this pair.")

    pair = [str(before)] + ([str(after)] if after is not None else [])
    results = []

    if skip_extract or after is not None:
        why = ("an explicit after-file was given, so the live extracts are not the subject"
               if after is not None else
               "you asserted the TSVs are already fresh")
        print(f"\n(skipping extract_genealogy.py -- {why})")
    else:
        results.append(("extract_genealogy", run(
            "extract_genealogy.py", [],
            "1/4  extract_genealogy.py -- regenerate the TSVs from wikibase/items/")))

    results.append(("compare_tangles", run(
        "compare_tangles.py", pair,
        "2/4  compare_tangles.py -- WIDTH: tangles introduced / removed / reshaped")))
    results.append(("compare_depth", run(
        "compare_depth.py", pair + ([max_loss] if max_loss else []),
        "3/4  compare_depth.py -- DEPTH: ancestry lost per record (the load-bearing one)")))
    results.append(("check_invariants", run(
        "check_invariants.py", [],
        "4/4  check_invariants.py -- the four standing invariants vs the baseline")))

    failed = [n for n, rc in results if rc != 0]

    print(f"\n{'=' * 72}\n  VERDICT\n{'=' * 72}")
    for name, rc in results:
        print(f"  {'PASS' if rc == 0 else 'FAIL':<6} {name}")

    if failed:
        print(f"\nFAIL: {', '.join(failed)}.")
        print("Do not commit this repair. If compare_depth failed, the edge you touched was")
        print("a gateway and the real defect is elsewhere in the loop -- cycle_policy.md.")
        return 1

    print("\nPASS: every gate green. Shadow consistency is checked at commit time by")
    print(".githooks/pre-commit (needs `git config core.hooksPath .githooks` once per")
    print("checkout); if that hook is not installed, this repair is not yet durable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
