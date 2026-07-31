#!/bin/sh
# order.life — run after a reboot, or any time you want the genealogy state rebuilt
# and checked. Safe to run repeatedly; it changes no item data.
#
#   sh wiki-scripts/resume.sh          # rebuild extracts + run all gates
#   sh wiki-scripts/resume.sh --quick  # gates only, skip the 10-minute rebuild
#
# From PowerShell:  bash wiki-scripts/resume.sh
set -e
cd "$(dirname "$0")/.."

echo "== 1. install the pre-commit gate (local config, does not survive a fresh clone) =="
git config core.hooksPath .githooks
echo "   core.hooksPath = $(git config core.hooksPath)"

echo
echo "== 2. wait for any in-flight extract run =="
# Restoring the TSVs while extract_genealogy.py is mid-write leaves persons.tsv half one
# version and half the other, which shows up as tens of thousands of dangling endpoints.
# Learned the hard way on 2026-07-31.
while tasklist //FI "IMAGENAME eq python.exe" 2>/dev/null | grep -q python.exe; do
    echo "   a python process is running (possibly extract_genealogy.py); waiting 30s..."
    sleep 30
done
echo "   no python running"

echo
echo "== 3. discard any half-written extracts =="
# A killed regeneration leaves persons.tsv truncated. These files are DERIVED from
# wikibase/items/, so restoring them from git is always safe -- nothing authored is lost.
for f in persons edges spouses redirects; do
    git checkout -- "wikibase/analysis/$f.tsv" 2>/dev/null || true
done
echo "   persons.tsv: $(wc -l < wikibase/analysis/persons.tsv) lines (expect ~107,052)"

if [ "$1" != "--quick" ]; then
    echo
    echo "== 4. rebuild the extracts from the item files (~10 minutes) =="
    python wiki-scripts/extract_genealogy.py
    python wiki-scripts/dump_qa_errors.py
fi

echo
echo "== 5. gates =="
python wiki-scripts/check_invariants.py || echo "   !! INVARIANT REGRESSED -- do not commit item changes until resolved"
python wiki-scripts/check_staged_shadows.py || true

echo
echo "== 6. state =="
git fetch -q origin || true
echo "   HEAD:      $(git log --oneline -1)"
echo "   vs origin: $(git rev-list --left-right --count origin/master...master) (behind / ahead)"
echo "   pending:   $(git status --porcelain | wc -l) file(s)"

cat <<'NOTE'

== what does NOT survive a reboot ==
The three work-loop crons (:03 work-loop, :15 auto-flush, :42 status) are
session-only -- they live in the Claude session, not on disk, and are gone.
A new session recreates them; ask it to "start the work loop", or it will do
so itself via the autonomous-loop skill.

Everything else persists: all commits are pushed, core.hooksPath is stored in
.git/config, and queue.md / devlog.md carry the state of play.
NOTE
