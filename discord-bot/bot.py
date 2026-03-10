#!/usr/bin/env python3
"""Gaiad Daily Reading — Discord Forum Bot (one-shot).

Checks the order.life RSS feed and posts new chapters as forum threads.
Runs once and exits. Designed for daily GitHub Actions cron.

Modes:
  (default)   Post today's new chapter from RSS feed
  --catchup   Post the next catch-up chapter directly from chapter files
              (chapters 1-70, one per day, March 9 – May 17 2026)
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path

import feedparser
import requests

FEED_URL = "https://order.life/feed.xml"
POSTED_GUIDS_FILE = Path(__file__).parent / "posted_guids.json"
CATCHUP_GUIDS_FILE = Path(__file__).parent / "catchup_posted_guids.json"
EPIC_DIR = Path(__file__).parent.parent / "Gaiad" / "epic"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DISCORD_API = "https://discord.com/api/v10"

# Forum channels to post to
TARGETS = [
    {"server": 1473062005509193838, "forum": 1478856506500976690},
    {"server": 1472675405059064083, "forum": 1477872761807437824},
]

# Catch-up: post chapters 1-70, one per day, starting March 9 2026
CATCHUP_START_DATE = datetime.date(2026, 3, 9)
CATCHUP_CHAPTERS = 70

# Gaian calendar months in order
GAIAN_MONTHS = [
    ("\u2650", "Sagittarius"),
    ("\u2651", "Capricorn"),
    ("\u2652", "Aquarius"),
    ("\u2653", "Pisces"),
    ("\u2648", "Aries"),
    ("\u2649", "Taurus"),
    ("\u264a", "Gemini"),
    ("\u264b", "Cancer"),
    ("\u264c", "Leo"),
    ("\u264d", "Virgo"),
    ("\u264e", "Libra"),
    ("\u264f", "Scorpius"),
    ("\u26ce", "Ophiuchus"),
]


def chapter_to_gaian_date(chapter_num):
    """Convert chapter number (1-364) to Gaian calendar date string."""
    month_index = (chapter_num - 1) // 28
    day = (chapter_num - 1) % 28 + 1
    if month_index < len(GAIAN_MONTHS):
        symbol, name = GAIAN_MONTHS[month_index]
        return f"{symbol} {name} {day}, 12026 GE"
    return f"Day {chapter_num}, 12026 GE"


def load_guids(path):
    if path.exists():
        return set(json.loads(path.read_text()))
    return set()


def save_guids(guids, path):
    path.write_text(json.dumps(sorted(guids)))


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


def load_chapter_file(chapter_num):
    """Load chapter text from Gaiad/epic/chapter_NNN.md."""
    chapter_file = EPIC_DIR / f"chapter_{chapter_num:03d}.md"
    if not chapter_file.exists():
        return None, None
    raw = chapter_file.read_text(encoding="utf-8")
    clean = re.sub(r'\{\{[cp]\|([^}]*)\}\}', r'\1', raw)
    title = None
    title_match = re.match(r'^#\s+(?:Chapter\s+\d+:\s*)?(.*)', clean)
    if title_match:
        title = title_match.group(1).strip()
        clean = clean[title_match.end():].lstrip('\n')
    return title, clean


def run_daily(feed):
    """Post today's chapter (the newest entry in the feed)."""
    posted = load_guids(POSTED_GUIDS_FILE)
    first_run = len(posted) == 0

    if first_run:
        # First run: seed all existing GUIDs, only post the latest chapter
        all_guids = set()
        for entry in feed.entries:
            guid = entry.get("id", entry.get("link"))
            all_guids.add(guid)

        latest = feed.entries[0]
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

        save_guids(all_guids, POSTED_GUIDS_FILE)
        print(f"First run: posted latest chapter, seeded {len(all_guids)} GUIDs.")
        return

    # Normal run: post any new entries since last run
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

    save_guids(posted, POSTED_GUIDS_FILE)
    print(f"Done. Posted {new_count} new chapter(s).")


def run_catchup():
    """Post a catch-up chapter (chapters 1-70, one per day from March 9)."""
    today = datetime.date.today()
    day_offset = (today - CATCHUP_START_DATE).days

    if day_offset < 0 or day_offset >= CATCHUP_CHAPTERS:
        print("No catch-up chapter due today (outside March 9 - May 17 window).")
        return

    chapter_num = day_offset + 1  # day 0 = chapter 1, day 1 = chapter 2, ...

    # Check if already posted today
    catchup_posted = load_guids(CATCHUP_GUIDS_FILE)
    catchup_key = f"catchup-{chapter_num:03d}"
    if catchup_key in catchup_posted:
        print(f"Catch-up chapter {chapter_num} already posted.")
        return

    # Load chapter directly from file
    chapter_title, chapter_text = load_chapter_file(chapter_num)
    if chapter_text is None:
        print(f"Chapter file chapter_{chapter_num:03d}.md not found.")
        return

    gaian_date = chapter_to_gaian_date(chapter_num)
    link = f"https://order.life/gaiad/{chapter_num:03d}/"

    if chapter_title:
        thread_title = f"[Catch-up] Chapter {chapter_num}: {chapter_title}"[:100]
    else:
        thread_title = f"[Catch-up] Chapter {chapter_num} ({gaian_date})"[:100]

    catchup_intro = (
        f"**Catch-up Reading \u2014 {gaian_date}**\n\n"
        f"This chapter would normally have been posted on {gaian_date}, "
        f"but since our daily readings began on \u2652 Aquarius 15, 12026 GE, "
        f"we are posting previous chapters in chronological order through "
        f"\u2649 Taurus 1 for the benefit of readers.\n\n"
    )

    body = catchup_intro + chapter_text
    if len(body) > 1900:
        body = body[:1900] + "..."
    body += f"\n\n[Read on order.life]({link})"

    for target in TARGETS:
        try:
            create_forum_thread(target["forum"], thread_title, body)
            print(f"Catch-up posted: {thread_title} -> channel {target['forum']}")
        except requests.HTTPError as e:
            print(f"Error posting catch-up to {target['forum']}: {e}")
            print(f"Response: {e.response.text}")
        time.sleep(1)

    catchup_posted.add(catchup_key)
    save_guids(catchup_posted, CATCHUP_GUIDS_FILE)
    print(f"Catch-up: posted chapter {chapter_num}.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catchup", action="store_true",
                        help="Post catch-up chapter instead of daily")
    args = parser.parse_args()

    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set")
        sys.exit(1)

    if args.catchup:
        run_catchup()
    else:
        feed = feedparser.parse(FEED_URL)
        if not feed.entries:
            print("No entries in feed")
            return
        run_daily(feed)


if __name__ == "__main__":
    main()
