# chats/

Claude Code web-UI chats and Claude.ai web chats, saved as HTML by the
user (File → Save Page As) and extracted to markdown with
`scripts/extract_chat.py`.

These are unstructured thinking conversations — design sketches, plan
drafts, concept explorations. They are cheaper than repo-local Claude
Code sessions but the content is valuable and lives in the repo so it
can be referenced from planning docs, `STATUS.md`, and future sessions.

## Workflow

- User saves a chat as HTML into this directory.
- Run `python scripts/extract_chat.py`. It scans for `.html` files
  without a matching `.md` sibling and writes `<title-slug>.md`.
- Commit both `.md` and `.html`. The HTML is the source of truth; the
  `.md` is the working copy.

The extractor supports two export formats:

- Claude.ai web chats (`font-user-message` / `font-claude-response`).
- Claude Code web UI (`bg-bg-200 rounded-lg` / `text-sm text-text-100`)
  — used as a fallback when the claude.ai markers are absent.

## Lifecycle

Chats are **triage inputs**, not permanent artifacts. Once a chat's
content has been:

- implemented in code / planning docs, or
- recorded in `STATUS.md`, `todo.md`, or `planning/`, or
- consciously decided as not-pursuing,

the extracted `.md` (and its `.html` + `_files/` sidecar) can be
deleted. The commit message should say which of the three paths
applied. Each chat gets its own commit so the reasoning stays
auditable.

This README exists so the directory survives when all chats are cleared.
