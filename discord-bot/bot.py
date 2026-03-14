#!/usr/bin/env python3
"""Gaiad Daily Reading — Discord Forum Bot (one-shot, state-file based).

Runs on a frequent cron (every 3 hours). Uses a committed state file to
track what has already been posted, so duplicate runs are harmless no-ops.

Two posting windows per day (Pacific Time):
  - After 6 AM PT:  Post today's daily chapter (computed from Gaian calendar)
  - After 6 PM PT:  Post today's catch-up chapter (chapters 1-70, Mar 9 – May 17)
"""

import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

EPIC_DIR = Path(__file__).parent.parent / "Gaiad" / "epic"
FURTHER_READING_FILE = EPIC_DIR / "further_reading.json"
STATE_FILE = Path(__file__).parent / "state.json"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DISCORD_API = "https://discord.com/api/v10"

# Forum channels to post to
TARGETS = [
    {"server": 1473062005509193838, "forum": 1478856506500976690},
    {"server": 1472675405059064083, "forum": 1477872761807437824},
]

# Catch-up: chapters 1-70, one per day starting March 9 2026 (Pacific)
CATCHUP_START_DATE = datetime.date(2026, 3, 9)
CATCHUP_CHAPTERS = 70

PT = ZoneInfo("America/Los_Angeles")

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


def greg_to_chapter(greg_date):
    """Convert a Gregorian date to Gaiad chapter number (1-364+)."""
    iso_year, iso_week, iso_day = greg_date.isocalendar()
    return (iso_week - 1) * 7 + iso_day


def load_state():
    """Load the posting state from state.json."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_daily_date": None, "last_catchup_date": None}


def save_state(state):
    """Save posting state to state.json."""
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_further_reading():
    """Load the further reading Wikipedia links for each chapter."""
    if FURTHER_READING_FILE.exists():
        return json.loads(FURTHER_READING_FILE.read_text(encoding="utf-8"))
    return {}


def build_further_reading_message(chapter_num):
    """Build a 'Further Reading' message for a given chapter number."""
    readings = load_further_reading()
    articles = readings.get(str(chapter_num))
    if not articles:
        return None
    lines = ["\U0001f4da **Further Reading**", ""]
    for article in articles:
        lines.append(f"\u2022 [{article['title']}]({article['url']})")
    return "\n".join(lines)


def create_forum_thread(channel_id, title, body):
    """Create a new forum thread via Discord HTTP API."""
    url = f"{DISCORD_API}/channels/{channel_id}/threads"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": title[:100],
        "message": {"content": body[:2000]},
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def post_message_in_thread(thread_id, content):
    """Post a follow-up message in an existing thread."""
    url = f"{DISCORD_API}/channels/{thread_id}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"content": content[:2000]}
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


def post_to_discord(thread_title, body, chapter_num):
    """Post a chapter to all target Discord forums. Returns True if successful."""
    further_msg = build_further_reading_message(chapter_num)
    success = False
    for target in TARGETS:
        try:
            result = create_forum_thread(target["forum"], thread_title, body)
            print(f"  Posted: {thread_title} -> channel {target['forum']}")
            success = True
            if further_msg and "id" in result:
                time.sleep(0.5)
                post_message_in_thread(result["id"], further_msg)
                print(f"  Further reading posted to thread {result['id']}")
        except requests.HTTPError as e:
            print(f"  Error posting to {target['forum']}: {e}")
            print(f"  Response: {e.response.text}")
        time.sleep(1)
    return success


def try_daily(now_pt, state):
    """Post today's daily chapter if after 6 AM PT and not yet posted today."""
    today_str = now_pt.date().isoformat()

    if state.get("last_daily_date") == today_str:
        print(f"[daily] Already posted for {today_str}, skipping.")
        return False

    if now_pt.hour < 6:
        print(f"[daily] Before 6 AM PT ({now_pt.strftime('%H:%M')}), skipping.")
        return False

    chapter_num = greg_to_chapter(now_pt.date())
    if chapter_num < 1 or chapter_num > 364:
        print(f"[daily] Chapter {chapter_num} out of range (Horus intercalary?), skipping.")
        return False

    chapter_title, chapter_text = load_chapter_file(chapter_num)
    if chapter_text is None:
        print(f"[daily] Chapter file chapter_{chapter_num:03d}.md not found, skipping.")
        return False

    gaian_date = chapter_to_gaian_date(chapter_num)
    link = f"https://order.life/gaiad/{chapter_num:03d}/"

    if chapter_title:
        thread_title = f"{gaian_date} — Chapter {chapter_num}: {chapter_title}"[:100]
    else:
        thread_title = f"{gaian_date} — Chapter {chapter_num}"[:100]

    daily_intro = (
        f"Today is {gaian_date}, and here is chapter {chapter_num}, "
        f"the daily reading.\n\n"
    )

    body = daily_intro + chapter_text
    if len(body) > 1900:
        body = body[:1900] + "..."
    body += f"\n\n[Read on order.life]({link})"

    print(f"[daily] Posting chapter {chapter_num} ({gaian_date}) for {today_str}...")
    if post_to_discord(thread_title, body, chapter_num):
        state["last_daily_date"] = today_str
        return True
    return False


def try_catchup(now_pt, state):
    """Post today's catch-up chapter if after 6 PM PT and not yet posted today."""
    today_str = now_pt.date().isoformat()

    if state.get("last_catchup_date") == today_str:
        print(f"[catchup] Already posted for {today_str}, skipping.")
        return False

    if now_pt.hour < 18:
        print(f"[catchup] Before 6 PM PT ({now_pt.strftime('%H:%M')}), skipping.")
        return False

    day_offset = (now_pt.date() - CATCHUP_START_DATE).days
    if day_offset < 0 or day_offset >= CATCHUP_CHAPTERS:
        print(f"[catchup] Outside catch-up window (day offset {day_offset}), skipping.")
        return False

    chapter_num = day_offset + 1

    chapter_title, chapter_text = load_chapter_file(chapter_num)
    if chapter_text is None:
        print(f"[catchup] Chapter file chapter_{chapter_num:03d}.md not found, skipping.")
        return False

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

    print(f"[catchup] Posting chapter {chapter_num} ({gaian_date}) for {today_str}...")
    if post_to_discord(thread_title, body, chapter_num):
        state["last_catchup_date"] = today_str
        return True
    return False


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set")
        sys.exit(1)

    now_pt = datetime.datetime.now(PT)
    print(f"Bot running at {now_pt.strftime('%Y-%m-%d %H:%M %Z')}")

    state = load_state()
    changed = False

    if try_daily(now_pt, state):
        changed = True

    if try_catchup(now_pt, state):
        changed = True

    if changed:
        save_state(state)
        print(f"State updated: {json.dumps(state)}")
    else:
        print("Nothing to post this run.")


if __name__ == "__main__":
    main()
