#!/usr/bin/env python3
"""
update_git_revisions.py
=======================
Generates a wiki table of all git commits from the order.life repository
and publishes it to [[Git revisions]] on lifeism.miraheze.org.

Usage:
    python update_git_revisions.py              # dry-run (prints table)
    python update_git_revisions.py --apply      # publishes to wiki
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from utils import connect, safe_save

WIKI_PAGE = "Git revisions"
REPO_URL = "https://github.com/Emma-Leonhart/order.life"


def get_git_log():
    """Run git log and return list of (date, short_sha, full_sha, author, message)."""
    # Run from the repo root (parent of wiki-scripts/)
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    result = subprocess.run(
        ["git", "log", "--format=%aI\t%h\t%H\t%an\t%s"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"git log failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    commits = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t", 4)
        if len(parts) == 5:
            date_iso, short_sha, full_sha, author, message = parts
            # Extract just the date portion (YYYY-MM-DD)
            date_str = date_iso[:10]
            commits.append((date_str, short_sha, full_sha, author, message))
    return commits


def build_wiki_table(commits):
    """Build a MediaWiki table from the commit list (newest first)."""
    lines = [
        "This page is automatically maintained by [[User:EmmaBot]].",
        "",
        f"Total commits: '''{len(commits)}'''",
        "",
        '{| class="wikitable sortable" style="width:100%"',
        "! Date !! SHA !! Message !! Author",
    ]

    for date_str, short_sha, full_sha, author, message in commits:
        # Escape pipe characters in message
        safe_message = message.replace("|", "{{!}}")
        sha_link = f"[{REPO_URL}/commit/{full_sha} {short_sha}]"
        lines.append("|-")
        lines.append(f"| {date_str} || <code>{sha_link}</code> || {safe_message} || {author}")

    lines.append("|}")
    lines.append("")
    lines.append("[[Category:Bot maintained pages]]")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Update [[Git revisions]] wiki page")
    parser.add_argument("--apply", action="store_true",
                        help="Actually publish to wiki (default is dry-run)")
    parser.add_argument("--run-tag", default="",
                        help="Wiki-formatted run tag for edit summaries")
    args = parser.parse_args()

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""

    print("Reading git log...", flush=True)
    commits = get_git_log()
    print(f"Found {len(commits)} commits.", flush=True)

    if not commits:
        print("No commits found. Nothing to do.")
        return

    table = build_wiki_table(commits)

    if not args.apply:
        print("\n--- DRY RUN (pass --apply to publish) ---")
        # Print first 30 lines as preview
        preview_lines = table.splitlines()[:30]
        for line in preview_lines:
            print(line)
        if len(table.splitlines()) > 30:
            print(f"  ... ({len(table.splitlines()) - 30} more lines)")
        return

    site = connect()
    page = site.pages[WIKI_PAGE]
    saved = safe_save(page, table,
                      summary=f"Bot: update git revisions ({len(commits)} commits){run_tag_suffix}")
    if saved:
        print(f"Updated [[{WIKI_PAGE}]] with {len(commits)} commits.")
    else:
        print(f"[[{WIKI_PAGE}]] already up to date.")


if __name__ == "__main__":
    main()
