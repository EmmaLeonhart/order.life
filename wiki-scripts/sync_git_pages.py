#!/usr/bin/env python3
"""
sync_git_pages.py
=================
Bidirectional sync of pages in [[Category:Git synced pages]] between
the Lifeism wiki and the local ``wiki-pages/`` directory.

Direction of sync:
  --pull   : wiki  -> local files  (fetch latest from wiki)
  --push   : local files -> wiki   (upload changed files to wiki)
  --sync   : pull then push        (default)

Pages are editable on both sides: edit on the wiki and the next pull
brings it into the repo; edit locally and the next push updates the wiki.

File layout::

    wiki-pages/
      _sync_state.json        # title <-> filename + revid metadata
      Some_Page.wiki          # page wikitext
      ...

Usage::

    python wiki-scripts/sync_git_pages.py --pull
    python wiki-scripts/sync_git_pages.py --push --apply
    python wiki-scripts/sync_git_pages.py --sync --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import THROTTLE
from utils import connect, safe_save

PAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "wiki-pages")
STATE_FILE = os.path.join(PAGES_DIR, "_sync_state.json")
SYNC_CATEGORY = "Git synced pages"


# ---------------------------------------------------------------------------
# Filename <-> title mapping
# ---------------------------------------------------------------------------

def title_to_filename(title: str) -> str:
    """Convert a wiki page title to a safe local filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', title)
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name).strip('_')
    return name + ".wiki"


def filename_to_title(filename: str, state: dict) -> str | None:
    """Look up the original page title from the state metadata."""
    for title, meta in state.items():
        if meta.get("file") == filename:
            return title
    return None


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    """Load sync state (title -> {file, revid})."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    """Persist sync state."""
    os.makedirs(PAGES_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Propagate: tag subcategory members with [[Category:Git synced pages]]
# ---------------------------------------------------------------------------

CAT_TAG = "[[Category:Git synced pages]]"

def propagate(site, apply: bool = False, run_tag: str = "",
              verbose: bool = True) -> int:
    """Find subcategories of Category:Git synced pages and tag their
    direct members with [[Category:Git synced pages]].

    Non-recursive on purpose — runs once per CI invocation, so deeper
    nesting propagates naturally over successive runs.

    Returns number of pages tagged.
    """
    cat = site.categories[SYNC_CATEGORY]
    tagged = 0
    run_tag_suffix = f" ({run_tag})" if run_tag else ""

    # Collect direct subcategories only
    subcats = []
    for member in cat.members():
        if member.namespace == 14:
            subcats.append(member.name.replace("Category:", "", 1))

    if not subcats:
        print("Propagate: no subcategories found.")
        return 0

    for subcat_name in subcats:
        if verbose:
            print(f"  subcategory: Category:{subcat_name}")
        subcat = site.categories[subcat_name]
        for member in subcat.members():
            title = member.name
            page = site.pages[title]
            if not page.exists:
                continue

            text = page.text()
            if not text:
                continue

            # Already tagged — skip
            if "[[Category:Git synced pages]]" in text:
                if verbose:
                    print(f"    already tagged: {title}")
                continue

            if apply:
                new_text = text.rstrip() + "\n" + CAT_TAG + "\n"
                summary = f"Bot: propagate git-sync category from Category:{subcat_name}{run_tag_suffix}"
                try:
                    saved = safe_save(page, new_text, summary)
                except Exception as exc:
                    print(f"    ERROR tagging {title}: {exc}")
                    continue
                if saved:
                    tagged += 1
                    print(f"    tagged: {title}")
                else:
                    print(f"    FAILED to tag: {title}")
            else:
                print(f"    would tag: {title}")
                tagged += 1

    action = "tagged" if apply else "would tag"
    print(f"Propagate complete: {tagged} pages {action}.")
    return tagged


# ---------------------------------------------------------------------------
# Pull: wiki -> local
# ---------------------------------------------------------------------------

def pull(site, state: dict, verbose: bool = True) -> int:
    """Pull pages from Category:Git synced pages into local files.

    Returns number of files updated.
    """
    os.makedirs(PAGES_DIR, exist_ok=True)

    cat = site.categories[SYNC_CATEGORY]
    updated = 0
    titles_seen = set()

    for member in cat.members():
        title = member.name
        ns = member.namespace

        # Skip category pages — they're handled by propagate, not synced as files
        if ns == 14:
            continue

        if title in titles_seen:
            continue
        titles_seen.add(title)

        page = site.pages[title]
        if not page.exists:
            continue

        text = page.text()
        if not text or not text.strip():
            continue

        revid = page.revision
        filename = title_to_filename(title)
        filepath = os.path.join(PAGES_DIR, filename)

        # Check if content changed since last sync
        old_meta = state.get(title, {})
        if old_meta.get("revid") == revid and os.path.exists(filepath):
            if verbose:
                print(f"  unchanged: {title}")
            state[title] = {"file": filename, "revid": revid}
            continue

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        state[title] = {"file": filename, "revid": revid}
        updated += 1
        print(f"  pulled: {title} -> {filename}")
        time.sleep(THROTTLE)

    # Clean up state entries for pages no longer in category
    removed = [t for t in state if t not in titles_seen]
    for t in removed:
        old_file = os.path.join(PAGES_DIR, state[t].get("file", ""))
        if os.path.exists(old_file):
            os.remove(old_file)
            print(f"  removed: {t} (no longer in category)")
        del state[t]

    print(f"Pull complete: {updated} files updated, {len(titles_seen)} total pages.")
    return updated


# ---------------------------------------------------------------------------
# Push: local -> wiki
# ---------------------------------------------------------------------------

def push(site, state: dict, apply: bool = False, run_tag: str = "",
         verbose: bool = True) -> int:
    """Push local wiki-page files back to the wiki.

    Only pushes files that differ from the wiki's current content.
    Returns number of pages updated.
    """
    if not os.path.isdir(PAGES_DIR):
        print("No wiki-pages/ directory found. Run --pull first.")
        return 0

    updated = 0
    run_tag_suffix = f" ({run_tag})" if run_tag else ""

    for filename in sorted(os.listdir(PAGES_DIR)):
        if not filename.endswith(".wiki"):
            continue

        filepath = os.path.join(PAGES_DIR, filename)
        title = filename_to_title(filename, state)
        if title is None:
            # New file not in state — derive title from filename
            title = filename.replace(".wiki", "").replace("_", " ")
            print(f"  new file (no state): {filename} -> {title}")

        with open(filepath, "r", encoding="utf-8") as f:
            local_text = f.read()

        page = site.pages[title]
        try:
            wiki_text = page.text() if page.exists else ""
        except Exception:
            wiki_text = ""

        if local_text.rstrip() == wiki_text.rstrip():
            if verbose:
                print(f"  unchanged: {title}")
            continue

        if apply:
            summary = f"Bot: sync page from repo{run_tag_suffix}"
            saved = safe_save(page, local_text, summary)
            if saved:
                page = site.pages[title]  # re-fetch for new revid
                state[title] = {"file": filename, "revid": page.revision}
                updated += 1
                print(f"  pushed: {title}")
            else:
                print(f"  FAILED to push: {title}")
        else:
            print(f"  would push: {title}")
            updated += 1

    action = "pushed" if apply else "would push"
    print(f"Push complete: {updated} pages {action}.")
    return updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Sync [[Category:Git synced pages]] between wiki and repo."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pull", action="store_true", help="Pull wiki pages to local files.")
    group.add_argument("--push", action="store_true", help="Push local files to wiki.")
    group.add_argument("--sync", action="store_true", help="Pull then push (default).")
    parser.add_argument("--apply", action="store_true", help="Actually write to wiki (push/sync only).")
    parser.add_argument("--run-tag", default="", help="Run tag for edit summaries.")
    parser.add_argument("--quiet", action="store_true", help="Only print changes.")
    args = parser.parse_args()

    # Default to sync if nothing specified
    do_pull = args.pull or args.sync or (not args.pull and not args.push)
    do_push = args.push or args.sync or (not args.pull and not args.push)

    site = connect()
    state = load_state()

    # Propagate first: tag direct members of subcategories so they
    # appear in the main category for pull. One level per run —
    # deeper nesting propagates over successive CI runs.
    print("=== PROPAGATE: tag subcategory members ===")
    propagate(site, apply=args.apply, run_tag=args.run_tag,
              verbose=not args.quiet)

    if do_pull:
        print("=== PULL: wiki -> local ===")
        pull(site, state, verbose=not args.quiet)
        save_state(state)

    if do_push:
        print("=== PUSH: local -> wiki ===")
        push(site, state, apply=args.apply, run_tag=args.run_tag,
             verbose=not args.quiet)
        save_state(state)


if __name__ == "__main__":
    main()
