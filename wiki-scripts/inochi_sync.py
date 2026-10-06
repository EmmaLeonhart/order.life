#!/usr/bin/env python3
"""
inochi_sync.py
==============
Two-way sync of the pages on inochi.miraheze.org with the repo's
``inochi-pages/`` directory — the same scheme ``sync_git_pages.py`` ran for
the lifeism wiki.

Every page on inochi is git synced (Emma, 2026-10-03: "all of the pages on
the wiki right now are supposed to be git synced"). A page is synced when it
is in [[Category:Git synced pages]], or, for pages whose content model cannot
hold a category (Lua modules, JS/CSS, Wikibase items and properties), when its
title is listed in ``inochi-pages/_extra_pages.txt``.

  --pull     : wiki -> local files
  --push     : local files -> wiki (only files whose text differs)
  --sync     : pull then push (default)
  --tag-all  : first, put every page on the wiki that is not yet synced into
               the sync: wikitext pages get [[Category:Git synced pages]]
               (inside <noinclude> on templates), other content models are
               added to _extra_pages.txt

Pull reads only synced pages, and push writes only files that changed,
throttled, so a run touches as few pages as possible. Wikibase items and
properties are pulled only: their JSON cannot be saved back through
action=edit. Writes need --apply. Runs from Emma's machine (Miraheze
bot-checks GitHub runners); credentials come from INOCHI_USERNAME /
INOCHI_PASSWORD.

File layout::

    inochi-pages/
      _sync_state.json   # title -> {file, revid, model}
      _extra_pages.txt   # synced titles that cannot carry the category
      Some_Page.wiki
"""
from __future__ import annotations

import argparse
import csv
import hashlib
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
EXTRA_FILE = os.path.join(PAGES_DIR, "_extra_pages.txt")
# Redirects are never synced (Emma, 2026-10-05): they stay on the wiki, and this registry of each one and
# its target is the authority. Any redirect the sync meets is added here instead of pulled.
REDIRECTS_FILE = os.path.join(PAGES_DIR, "_redirects.csv")
REDIRECT = re.compile(r"\s*#redirect\s*:?\s*\[\[([^\]|]+)", re.I)
SYNC_CATEGORY = "Category:Git synced pages"
CATEGORY_TAG = "[[" + SYNC_CATEGORY + "]]"
THROTTLE = 1.5
PULL_ONLY_MODELS = {"wikibase-item", "wikibase-property", "wikibase-lexeme"}


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


def load_redirects() -> dict[str, str]:
    if not os.path.exists(REDIRECTS_FILE):
        return {}
    with open(REDIRECTS_FILE, encoding="utf-8", newline="") as f:
        return {row["title"]: row["target"] for row in csv.DictReader(f)}


def save_redirects(reg: dict[str, str]) -> None:
    with open(REDIRECTS_FILE, "w", encoding="utf-8", newline="") as f:
        out = csv.writer(f, lineterminator="\n")
        out.writerow(["title", "target"])
        for t in sorted(reg):
            out.writerow([t, reg[t]])


def redirect_target(text: str) -> str | None:
    m = REDIRECT.match(text)
    return m.group(1).strip() if m else None


def load_extra() -> list[str]:
    if not os.path.exists(EXTRA_FILE):
        return []
    with open(EXTRA_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def save_extra(titles: list[str]) -> None:
    with open(EXTRA_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Synced pages whose content model cannot hold [[Category:Git synced pages]].\n")
        for t in sorted(set(titles)):
            f.write(t + "\n")


def _paged(s: requests.Session, params: dict, key: str) -> list[dict]:
    out, cont = [], {}
    while True:
        r = _json(s.get(API, params={**params, **cont, "format": "json"}))
        out += r["query"][key]
        if "continue" not in r:
            return out
        cont = r["continue"]


def all_pages(s: requests.Session) -> list[str]:
    ns = _json(s.get(API, params={"action": "query", "meta": "siteinfo",
                                  "siprop": "namespaces", "format": "json"}))
    titles = []
    for k in ns["query"]["namespaces"]:
        if int(k) < 0:
            continue
        titles += [p["title"] for p in _paged(s, {"action": "query", "list": "allpages",
                                                   "apnamespace": k, "aplimit": 500}, "allpages")]
    return titles


def category_members(s: requests.Session) -> list[str]:
    return [m["title"] for m in _paged(s, {"action": "query", "list": "categorymembers",
                                           "cmtitle": SYNC_CATEGORY, "cmlimit": 500},
                                       "categorymembers")]


def fetch(s: requests.Session, title: str) -> tuple[str, int, str] | None:
    # Miraheze answers the odd 502 over thousands of reads; retry rather than lose the whole run.
    for attempt in range(5):
        try:
            r = _json(s.get(API, params={"action": "query", "titles": title,
                                         "prop": "revisions", "rvprop": "content|ids|contentmodel",
                                         "rvslots": "main", "format": "json"}, timeout=120))
            break
        except (RuntimeError, requests.RequestException):
            if attempt == 4:
                raise
            time.sleep(15 * (attempt + 1))
    page = next(iter(r["query"]["pages"].values()))
    if "missing" in page:
        return None
    rev = page["revisions"][0]
    slot = rev["slots"]["main"]
    return slot["*"], rev["revid"], slot.get("contentmodel", "wikitext")


def tagged(text: str, title: str) -> str:
    if title.startswith("Template:"):
        return text.rstrip() + "\n<noinclude>" + CATEGORY_TAG + "</noinclude>\n"
    return text.rstrip() + "\n\n" + CATEGORY_TAG + "\n"


class Writer:
    def __init__(self, s: requests.Session):
        self.s, self.logged_in = s, False

    def edit(self, title: str, text: str, summary: str) -> int | None:
        if not self.logged_in:
            print(f"Logged in as {login(self.s, os.getenv('INOCHI_USERNAME', 'Immanuelle'), os.environ['INOCHI_PASSWORD'])}")
            self.logged_in = True
        csrf = _json(self.s.get(API, params={"action": "query", "meta": "tokens",
                                             "format": "json"}))["query"]["tokens"]["csrftoken"]
        r = _json(self.s.post(API, data={"action": "edit", "title": title, "text": text,
                                         "summary": summary, "token": csrf, "format": "json"}))
        time.sleep(THROTTLE)
        if r.get("edit", {}).get("result") != "Success":
            print(f"  FAILED to edit {title}: {r}", file=sys.stderr)
            return None
        return r["edit"].get("newrevid", r["edit"].get("oldrevid"))


def tag_all(s: requests.Session, w: Writer, apply: bool) -> None:
    extra = load_extra()
    reg = load_redirects()
    synced = set(category_members(s)) | set(extra)
    for title in all_pages(s):
        if title in synced or title in reg:
            continue
        got = fetch(s, title)
        if got is None:
            continue
        text, _, model = got
        if model == "wikitext" and redirect_target(text):
            reg[title] = redirect_target(text)
            print(f"  redirect, registered not tagged: {title}")
            continue
        if model != "wikitext":
            extra.append(title)
            print(f"  listed ({model}): {title}")
            continue
        if CATEGORY_TAG in text:
            # Written but not registered, e.g. after an unclosed <!-- (Category:Cyberspace collected six
            # copies, one an hour). Appending another changes nothing; the page needs fixing by hand.
            print(f"  tag present but not registered, not re-tagged: {title}")
            continue
        if not apply:
            print(f"  would tag: {title}")
            continue
        if w.edit(title, tagged(text, title), "Add to Git synced pages (every inochi page is git synced)"):
            print(f"  tagged: {title}")
    save_extra(extra)
    save_redirects(reg)


def _sha(text: str) -> str:
    return hashlib.sha1((text.rstrip() + "\n").encode("utf-8")).hexdigest()


def latest_revids(s: requests.Session, titles: list[str]) -> dict[str, int]:
    """Current revision id of each title, 50 titles a request, so a run reads only pages that changed."""
    out = {}
    for i in range(0, len(titles), 50):
        for attempt in range(5):
            try:
                r = _json(s.get(API, params={"action": "query", "titles": "|".join(titles[i:i + 50]),
                                             "prop": "revisions", "rvprop": "ids", "format": "json",
                                             "formatversion": 2}, timeout=120))
                break
            except (RuntimeError, requests.RequestException):
                if attempt == 4:
                    raise
                time.sleep(15 * (attempt + 1))
        for page in r["query"]["pages"]:
            if not page.get("missing") and page.get("revisions"):
                out[page["title"]] = page["revisions"][0]["revid"]
    return out


def pull(s: requests.Session, state: dict) -> None:
    reg = load_redirects()
    titles = [t for t in dict.fromkeys(category_members(s) + load_extra()) if t not in reg]
    current = latest_revids(s, titles)
    # Windows file names ignore case, so "Patriarchal Priesthood" and "Patriarchal priesthood" would share
    # one file and push would write one page's text over the other (it did, 2026-10-05). A title whose
    # file name is already held by a different title gets a hash suffix instead.
    claimed = {meta["file"].lower(): t for t, meta in state.items()}
    for title in titles:
        if title not in current:
            continue
        filename = state.get(title, {}).get("file") or title_to_filename(title)
        if claimed.get(filename.lower(), title) != title:
            filename = filename[:-5] + "__" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:8] + ".wiki"
        claimed[filename.lower()] = title
        path = os.path.join(PAGES_DIR, filename)
        if state.get(title, {}).get("revid") == current[title] and os.path.exists(path):
            continue
        got = fetch(s, title)
        if got is None:
            continue
        text, revid, model = got
        if model == "wikitext" and redirect_target(text):
            reg[title] = redirect_target(text)
            state.pop(title, None)
            print(f"  redirect, registered not pulled: {title}")
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.rstrip() + "\n")
        state[title] = {"file": filename, "revid": revid, "model": model, "sha": _sha(text)}
        print(f"  pulled: {title} -> {filename}")
        time.sleep(THROTTLE)
    for title in [t for t in state if t not in titles]:
        print(f"  no longer synced (file kept): {title}")
        del state[title]
    save_redirects(reg)
    print(f"Pull complete: {len(titles)} synced pages.")


def push(s: requests.Session, w: Writer, state: dict, apply: bool) -> None:
    # Keyed by lower case: Windows may hand back a file name in a different case from the one recorded,
    # and an exact match then guessed the title from the name and nearly pushed the case twin's text.
    by_file = {meta["file"].lower(): t for t, meta in state.items()}
    reg = load_redirects()
    shared = {}
    for t, meta in state.items():
        shared.setdefault(meta["file"].lower(), []).append(t)
    for filename in sorted(os.listdir(PAGES_DIR)):
        if not filename.endswith(".wiki"):
            continue
        if len(shared.get(filename.lower(), [])) > 1:
            print(f"  NOT pushed, file shared by {shared[filename.lower()]}: {filename}", file=sys.stderr)
            continue
        title = by_file.get(filename.lower()) or filename[:-5].replace("_", " ")
        if title in reg:
            continue
        meta = state.get(title, {})
        if meta.get("model") in PULL_ONLY_MODELS:
            continue
        with open(os.path.join(PAGES_DIR, filename), encoding="utf-8") as f:
            local = f.read()
        # A file whose text is what was last pulled has nothing to push; only changed or new files are
        # read back from the wiki. Entries from before hashes were kept take the file as their baseline.
        if meta and "sha" not in meta:
            meta["sha"] = _sha(local)
        if meta and meta["sha"] == _sha(local):
            continue
        got = fetch(s, title)
        if got and got[0].rstrip() == local.rstrip():
            if meta:
                meta["sha"] = _sha(local)
            continue
        if not apply:
            print(f"  would push: {title}")
            continue
        revid = w.edit(title, local, "Sync page from order.life repo")
        if revid:
            state[title] = {"file": filename, "revid": revid,
                            "model": got[2] if got else "wikitext", "sha": _sha(local)}
            print(f"  pushed: {title}")


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pull", action="store_true")
    g.add_argument("--push", action="store_true")
    g.add_argument("--sync", action="store_true")
    ap.add_argument("--tag-all", action="store_true",
                    help="first put every unsynced page on the wiki into the sync")
    ap.add_argument("--apply", action="store_true", help="actually write to the wiki")
    args = ap.parse_args()
    do_pull = not args.push
    do_push = not args.pull

    s = requests.Session()
    s.headers["User-Agent"] = UA
    w = Writer(s)
    state = load_state()
    if args.tag_all:
        print("=== TAG: every page on the wiki into the sync ===")
        tag_all(s, w, args.apply)
    if do_pull:
        print("=== PULL: wiki -> local ===")
        pull(s, state)
        save_state(state)
    if do_push:
        print("=== PUSH: local -> wiki ===")
        push(s, w, state, args.apply)
        save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
