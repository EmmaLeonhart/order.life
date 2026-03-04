"""
Post today's Gaiad chapter to Discord forum channels via webhook.

Run daily by GitHub Actions. Each webhook URL corresponds to a forum channel.
The webhook creates a new forum thread with the Gaian date as the title
and the chapter reading as the body.

Usage:
    DISCORD_WEBHOOKS="url1,url2" python post_daily.py
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Gaian Calendar
# ---------------------------------------------------------------------------

MONTHS = [
    {"num": 1,  "id": "sagittarius", "symbol": "\u2650"},
    {"num": 2,  "id": "capricorn",   "symbol": "\u2651"},
    {"num": 3,  "id": "aquarius",    "symbol": "\u2652"},
    {"num": 4,  "id": "pisces",      "symbol": "\u2653"},
    {"num": 5,  "id": "aries",       "symbol": "\u2648"},
    {"num": 6,  "id": "taurus",      "symbol": "\u2649"},
    {"num": 7,  "id": "gemini",      "symbol": "\u264a"},
    {"num": 8,  "id": "cancer",      "symbol": "\u264b"},
    {"num": 9,  "id": "leo",         "symbol": "\u264c"},
    {"num": 10, "id": "virgo",       "symbol": "\u264d"},
    {"num": 11, "id": "libra",       "symbol": "\u264e"},
    {"num": 12, "id": "scorpius",    "symbol": "\u264f"},
    {"num": 13, "id": "ophiuchus",   "symbol": "\u26ce"},
    {"num": 14, "id": "horus",       "symbol": "\U000130C3"},
]


def gregorian_to_gaian(d: date) -> dict:
    iso_year, week, day_of_week = d.isocalendar()
    month_index = (week - 1) // 4
    week_in_month = (week - 1) % 4
    month = month_index + 1
    day = week_in_month * 7 + day_of_week
    return {
        "year": iso_year + 10000,
        "month": month,
        "day": day,
        "month_data": MONTHS[month - 1] if month <= 14 else MONTHS[0],
    }


def day_of_year(month_num: int, day_in_month: int) -> int:
    if month_num <= 13:
        return (month_num - 1) * 28 + day_in_month
    return 364 + day_in_month


def gaian_date_string(gaian: dict) -> str:
    """e.g. '♓ Pisces 10, 12026 GE'"""
    m = gaian["month_data"]
    return f'{m["symbol"]} {m["id"].capitalize()} {gaian["day"]}, {gaian["year"]} GE'


# ---------------------------------------------------------------------------
# Chapter loading
# ---------------------------------------------------------------------------

EPIC_DIR = Path(__file__).resolve().parent.parent / "epic"


def load_chapter(chapter_num: int) -> tuple[str, str]:
    """Return (title, body) for a chapter. Title from first '# ' line."""
    path = EPIC_DIR / f"chapter_{chapter_num:03d}.md"
    if not path.exists():
        return f"Chapter {chapter_num}", ""

    text = path.read_text(encoding="utf-8")
    title = f"Chapter {chapter_num}"
    lines = text.split("\n")
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, text


# ---------------------------------------------------------------------------
# Discord webhook posting (creates forum thread)
# ---------------------------------------------------------------------------

MAX_MESSAGE = 2000


def post_to_webhook(webhook_url: str, thread_name: str, content: str) -> bool:
    """Post a new forum thread via Discord webhook.

    When a webhook targets a forum channel, the `thread_name` parameter
    creates a new forum thread with that title.
    """
    if len(content) > MAX_MESSAGE:
        content = content[: MAX_MESSAGE - 20] + "\n\n*(continued...)*"

    payload = json.dumps({
        "thread_name": thread_name,
        "content": content,
    }).encode()

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  Posted to webhook (status {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  ERROR: Discord returned {e.code}: {body}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"  ERROR: Network error: {e.reason}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    webhooks_str = os.getenv("DISCORD_WEBHOOKS", "")
    if not webhooks_str:
        print("ERROR: DISCORD_WEBHOOKS environment variable is not set", file=sys.stderr)
        sys.exit(1)

    webhooks = [url.strip() for url in webhooks_str.split(",") if url.strip()]

    today = date.today()
    gaian = gregorian_to_gaian(today)
    chapter_num = day_of_year(gaian["month"], gaian["day"])
    gaian_date = gaian_date_string(gaian)

    print(f"Today: {today} = {gaian_date} (chapter {chapter_num})")

    # Thread title = just the Gaian date
    thread_title = gaian_date

    # Thread body = intro + chapter text + link
    ch_title, ch_text = load_chapter(chapter_num)
    link = f"https://order.life/gaiad/{chapter_num:03d}/"

    body = (
        f"**{gaian_date}**\n"
        f"Chapter {chapter_num}: {ch_title}\n\n"
        f"{ch_text}\n\n"
        f"**[Read on order.life]({link})**"
    )

    any_success = False
    for i, url in enumerate(webhooks, 1):
        print(f"Posting to webhook {i}/{len(webhooks)}...")
        if post_to_webhook(url, thread_title, body):
            any_success = True

    if not any_success:
        print("FAILED: Could not post to any webhook", file=sys.stderr)
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
