#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Running wiki bot loop from: $ROOT_DIR"

RUN_ID="${GITHUB_RUN_ID:-}"
REPO="${GITHUB_REPOSITORY:-Emma-Leonhart/order.life}"
EVENT_NAME="${GITHUB_EVENT_NAME:-local}"

if [ -z "${RUN_ID}" ]; then
  echo "GITHUB_RUN_ID is required to build run-tag; refusing to run."
  exit 1
fi

RUN_PATH="${REPO}/actions/runs/${RUN_ID}"
CAUSE_TEXT="pipeline run"
case "${EVENT_NAME}" in
  push)
    CAUSE_TEXT="commit triggered pipeline"
    ;;
  schedule)
    CAUSE_TEXT="time triggered pipeline"
    ;;
  workflow_dispatch)
    CAUSE_TEXT="manual triggered pipeline"
    ;;
esac

RUN_TAG="[[github:${RUN_PATH}|${CAUSE_TEXT}]]"
echo "Run tag: ${RUN_TAG}"

# 1. Update bot status page
python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}"

# 2. Create wanted categories
python wiki-scripts/create_wanted_categories.py --apply --run-tag "${RUN_TAG}"

# 3. Create wanted pages
python wiki-scripts/create_wanted_pages.py --apply --run-tag "${RUN_TAG}"

# 4. Update git revisions page
python wiki-scripts/update_git_revisions.py --apply --run-tag "${RUN_TAG}"

# 5. Sync git-synced pages (bidirectional: pull from wiki, push local edits)
python wiki-scripts/sync_git_pages.py --sync --apply --run-tag "${RUN_TAG}"

# Commit any pages pulled from wiki
if ! git diff --quiet -- wiki-pages/ 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard -- wiki-pages/)" ]; then
  git add wiki-pages/
  git commit -m "chore(state): sync wiki pages [skip ci]"
  git pull --rebase origin master
  git push origin HEAD:master
fi
