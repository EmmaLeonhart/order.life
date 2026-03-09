#!/usr/bin/env python3
"""Gaiad Daily Reading — Discord Forum Bot (one-shot).

Checks the order.life RSS feed and posts new chapters as forum threads.
Runs once and exits. Designed for daily GitHub Actions cron.
"""

import json
import os
import sys
import time
from pathlib import Path

import feedparser
import requests

FEED_URL = "https://order.life/feed.xml"
POSTED_GUIDS_FILE = Path(__file__).parent / "posted_guids.json"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DISCORD_API = "https://discord.com/api/v10"

# Forum channels to post to
TARGETS = [
    {"server": 1473062005509193838, "forum": 1478856506500976690},
    {"server": 1472675405059064083, "forum": 1477872761807437824},
]


def load_posted():
    if POSTED_GUIDS_FILE.exists():
        return set(json.loads(POSTED_GUIDS_FILE.read_text()))
    return set()


def save_posted(guids):
    POSTED_GUIDS_FILE.write_text(json.dumps(sorted(guids)))


def create_forum_thread(channel_id, title, body):
    """Create a new forum thread via Discord HTTP API."""
    url = f"{DISCORD_API}/channels/{channel_id}/threads"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": title[:100],
        "message": {
            "content": body[:2000],
        },
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set")
        sys.exit(1)

    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        print("No entries in feed")
        return

    posted = load_posted()
    first_run = len(posted) == 0

    if first_run:
        # First run: seed all existing GUIDs, only post the latest chapter
        all_guids = set()
        for entry in feed.entries:
            guid = entry.get("id", entry.get("link"))
            all_guids.add(guid)

        latest = feed.entries[0]
        guid = latest.get("id", latest.get("link"))
        title = latest.get("title", "Daily Reading")[:100]
        description = latest.get("description", "")
        link = latest.get("link", "")

        body = description
        if len(body) > 1900:
            body = body[:1900] + "..."
        body += f"\n\n[Read on order.life]({link})"

        for target in TARGETS:
            try:
                create_forum_thread(target["forum"], title, body)
                print(f"Posted: {title} -> channel {target['forum']}")
            except requests.HTTPError as e:
                print(f"Error posting to {target['forum']}: {e}")
                print(f"Response: {e.response.text}")
            time.sleep(1)

        save_posted(all_guids)
        print(f"First run: posted latest chapter, seeded {len(all_guids)} GUIDs.")
        return

    # Normal run: post any new entries
    new_count = 0
    for entry in reversed(feed.entries):  # oldest first
        guid = entry.get("id", entry.get("link"))
        if guid in posted:
            continue

        title = entry.get("title", "Daily Reading")[:100]
        description = entry.get("description", "")
        link = entry.get("link", "")

        body = description
        if len(body) > 1900:
            body = body[:1900] + "..."
        body += f"\n\n[Read on order.life]({link})"

        for target in TARGETS:
            try:
                create_forum_thread(target["forum"], title, body)
                print(f"Posted: {title} -> channel {target['forum']}")
            except requests.HTTPError as e:
                print(f"Error posting to {target['forum']}: {e}")
                print(f"Response: {e.response.text}")
            time.sleep(1)

        posted.add(guid)
        new_count += 1

    save_posted(posted)
    print(f"Done. Posted {new_count} new chapter(s).")


if __name__ == "__main__":
    main()
