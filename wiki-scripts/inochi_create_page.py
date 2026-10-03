#!/usr/bin/env python3
"""
inochi_create_page.py
=====================
Create ONE page on inochi.miraheze.org from a file in the repo.

Deliberately small: one page per run, create-only (an existing page is
never overwritten), started by hand from GitHub Actions. Nothing here
loops over pages or runs on a schedule, so it cannot flood the wiki.

Credentials come from the environment:
    INOCHI_USERNAME   account name (default: Immanuelle)
    INOCHI_PASSWORD   the account password (GitHub secret INOCHI_PASSWORD)

A plain account name logs in with action=clientlogin (main-account
password). A name containing '@' is treated as a Special:BotPasswords
login and uses action=login.

Usage::

    python wiki-scripts/inochi_create_page.py --title 命 --file inochi-pages/命.wiki
    python wiki-scripts/inochi_create_page.py --title 命 --file inochi-pages/命.wiki --apply
"""
from __future__ import annotations

import argparse
import os
import sys

import requests

API = "https://inochi.miraheze.org/w/api.php"
UA = "InochiBot/1.0 (User:Immanuelle; inochi.miraheze.org; order.life)"


def _json(r: requests.Response) -> dict:
    """Decode an API response, or say plainly what came back instead."""
    try:
        return r.json()
    except ValueError:
        raise RuntimeError(f"HTTP {r.status_code} from {r.url}, not JSON: "
                           f"{r.text[:300]!r}") from None


def login(s: requests.Session, username: str, password: str) -> str:
    token = _json(s.get(API, params={"action": "query", "meta": "tokens",
                               "type": "login", "format": "json"}))
    token = token["query"]["tokens"]["logintoken"]
    if "@" in username:
        r = _json(s.post(API, data={"action": "login", "lgname": username,
                              "lgpassword": password, "lgtoken": token,
                              "format": "json"}))
        if r.get("login", {}).get("result") != "Success":
            raise RuntimeError(f"login failed: {r}")
    else:
        r = _json(s.post(API, data={"action": "clientlogin", "username": username,
                              "password": password, "logintoken": token,
                              "loginreturnurl": "https://inochi.miraheze.org/",
                              "format": "json"}))
        if r.get("clientlogin", {}).get("status") != "PASS":
            raise RuntimeError(f"clientlogin failed: {r.get('clientlogin', r)}")
    who = _json(s.get(API, params={"action": "query", "meta": "userinfo",
                             "format": "json"}))
    return who["query"]["userinfo"]["name"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--summary", default="Create page from order.life")
    ap.add_argument("--overwrite", action="store_true",
                    help="allow replacing an existing page (default: create-only)")
    ap.add_argument("--apply", action="store_true",
                    help="actually create the page (default: dry run)")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        text = f.read()

    s = requests.Session()
    s.headers["User-Agent"] = UA

    exists = _json(s.get(API, params={"action": "query", "titles": args.title,
                                "format": "json"}))
    page = next(iter(exists["query"]["pages"].values()))
    if "missing" not in page and not args.overwrite:
        print(f"[[{args.title}]] already exists; not touching it.")
        return 0

    if not args.apply:
        print(f"DRY RUN: would write [[{args.title}]] ({len(text)} chars):")
        print(text)
        return 0

    username = os.getenv("INOCHI_USERNAME", "Immanuelle")
    password = os.getenv("INOCHI_PASSWORD", "")
    if not password:
        print("INOCHI_PASSWORD is not set.", file=sys.stderr)
        return 1
    print(f"Logged in as {login(s, username, password)}")

    csrf = _json(s.get(API, params={"action": "query", "meta": "tokens",
                              "format": "json"}))
    csrf = csrf["query"]["tokens"]["csrftoken"]
    r = _json(s.post(API, data={"action": "edit", "title": args.title,
                          "text": text, "summary": args.summary,
                          "token": csrf, "format": "json",
                          **({} if args.overwrite else {"createonly": 1})}))
    if r.get("edit", {}).get("result") != "Success":
        print(f"edit failed: {r}", file=sys.stderr)
        return 1
    print(f"Saved [[{args.title}]]: "
          f"https://inochi.miraheze.org/wiki/{args.title.replace(' ', '_')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
