#!/usr/bin/env python3
"""
inochi_sync.py
==============
Two-way sync of [[Category:Git synced pages]] between inochi.miraheze.org
and the repo's ``inochi-pages/`` directory — the same scheme
``sync_git_pages.py`` ran for the lifeism wiki.

  --pull : wiki -> local files
  --push : local files -> wiki (only files whose text differs)
  --sync : pull then push (default)

Pull reads only members of the category, and push writes only files that
changed, throttled, so a run touches as few pages as possible. Writes need
--apply. Runs from Emma's machine (Miraheze bot-checks GitHub runners);
credentials come from INOCHI_USERNAME / INOCHI_PASSWORD.

File layout::

    inochi-pages/
      _sync_state.json   # title -> {file, revid}
      Some_Page.wiki
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(__file__))
from inochi_create_page import API, UA, _json, login  # noqa: E402

PAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "inochi-pages")
STATE_FILE = os.path.join(PAGES_DIR, "_sync_state.json")
SYNC_CATEGORY = "Category:Git synced pages"
THROTTLE = 1.5


def title_to_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', '_', title).replace(' ', '_')
    return re.sub(r'_+', '_', name).strip('_') + ".wiki"


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def fetch(s: requests.Session, title: str) -> tuple[str, int] | None:
    r = _json(s.get(API, params={"action": "query", "titles": title,
                                 "prop": "revisions", "rvprop": "content|ids",
                                 "rvslots": "main", "format": "json"}))
    page = next(iter(r["query"]["pages"].values()))
    if "missing" in page:
        return None
    rev = page["revisions"][0]
    return rev["slots"]["main"]["*"], rev["revid"]


def pull(s: requests.Session, state: dict) -> None:
    r = _json(s.get(API, params={"action": "query", "list": "categorymembers",
                                 "cmtitle": SYNC_CATEGORY, "cmlimit": 500,
                                 "cmnamespace": 0, "format": "json"}))
    titles = [m["title"] for m in r["query"]["categorymembers"]]
    for title in titles:
        got = fetch(s, title)
        if got is None:
            continue
        text, revid = got
        filename = title_to_filename(title)
        path = os.path.join(PAGES_DIR, filename)
        if state.get(title, {}).get("revid") == revid and os.path.exists(path):
            print(f"  unchanged: {title}")
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.rstrip() + "\n")
        state[title] = {"file": filename, "revid": revid}
        print(f"  pulled: {title} -> {filename}")
        time.sleep(THROTTLE)
    for title in [t for t in state if t not in titles]:
        print(f"  no longer in category (file kept): {title}")
        del state[title]
    print(f"Pull complete: {len(titles)} pages in category.")


def push(s: requests.Session, state: dict, apply: bool) -> None:
    by_file = {meta["file"]: t for t, meta in state.items()}
    logged_in = False
    for filename in sorted(os.listdir(PAGES_DIR)):
        if not filename.endswith(".wiki"):
            continue
        title = by_file.get(filename) or filename[:-5].replace("_", " ")
        with open(os.path.join(PAGES_DIR, filename), encoding="utf-8") as f:
            local = f.read()
        got = fetch(s, title)
        if got and got[0].rstrip() == local.rstrip():
            continue
        if not apply:
            print(f"  would push: {title}")
            continue
        if not logged_in:
            print(f"Logged in as {login(s, os.getenv('INOCHI_USERNAME', 'Immanuelle'), os.environ['INOCHI_PASSWORD'])}")
            logged_in = True
        csrf = _json(s.get(API, params={"action": "query", "meta": "tokens",
                                        "format": "json"}))["query"]["tokens"]["csrftoken"]
        r = _json(s.post(API, data={"action": "edit", "title": title, "text": local,
                                    "summary": "Sync page from order.life repo",
                                    "token": csrf, "format": "json"}))
        if r.get("edit", {}).get("result") != "Success":
            print(f"  FAILED to push {title}: {r}", file=sys.stderr)
            continue
        state[title] = {"file": filename, "revid": r["edit"].get("newrevid", r["edit"].get("oldrevid"))}
        print(f"  pushed: {title}")
        time.sleep(THROTTLE)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pull", action="store_true")
    g.add_argument("--push", action="store_true")
    g.add_argument("--sync", action="store_true")
    ap.add_argument("--apply", action="store_true", help="actually write to the wiki")
    args = ap.parse_args()
    do_pull = not args.push
    do_push = not args.pull

    s = requests.Session()
    s.headers["User-Agent"] = UA
    state = load_state()
    if do_pull:
        print("=== PULL: wiki -> local ===")
        pull(s, state)
        save_state(state)
    if do_push:
        print("=== PUSH: local -> wiki ===")
        push(s, state, args.apply)
        save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
