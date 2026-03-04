"""
Gaiad Daily Reading — Discord Forum Bot

Polls the order.life RSS feed and posts new daily Gaiad chapter readings
as forum threads in configured Discord servers.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

import discord
import feedparser

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FEED_URL = "https://order.life/feed.xml"
POSTED_GUIDS_FILE = Path(__file__).parent / "posted_guids.json"

# Forum channels to post to (server_id → forum_channel_id)
TARGETS = [
    {"server": 1473062005509193838, "forum": 1478856506500976690},
    {"server": 1472675405059064083, "forum": 1477872761807437824},
]

# How often to check the feed (seconds). Default: 30 minutes.
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "1800"))

# Discord limits
MAX_THREAD_TITLE = 100
MAX_MESSAGE_LENGTH = 2000

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("gaiad-bot")

# ---------------------------------------------------------------------------
# GUID persistence
# ---------------------------------------------------------------------------


def load_posted() -> set[str]:
    if POSTED_GUIDS_FILE.exists():
        try:
            return set(json.loads(POSTED_GUIDS_FILE.read_text()))
        except (json.JSONDecodeError, TypeError):
            log.warning("Corrupt posted_guids.json — starting fresh")
    return set()


def save_posted(guids: set[str]) -> None:
    POSTED_GUIDS_FILE.write_text(json.dumps(sorted(guids), indent=2))


# ---------------------------------------------------------------------------
# Feed parsing
# ---------------------------------------------------------------------------


def fetch_new_entries(posted: set[str]) -> list[dict]:
    """Return RSS entries whose GUIDs haven't been posted yet (oldest first)."""
    feed = feedparser.parse(FEED_URL)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Feed parse error: {feed.bozo_exception}")

    new = []
    for entry in reversed(feed.entries):  # oldest first
        guid = entry.get("id") or entry.get("link", "")
        if guid and guid not in posted:
            new.append(
                {
                    "guid": guid,
                    "title": (entry.get("title") or "Daily Reading")[:MAX_THREAD_TITLE],
                    "description": entry.get("description", ""),
                    "link": entry.get("link", ""),
                }
            )
    return new


# ---------------------------------------------------------------------------
# Message formatting
# ---------------------------------------------------------------------------


def format_message(entry: dict) -> str:
    """Build the forum thread starter message from an RSS entry."""
    body = entry["description"]
    link = entry["link"]
    suffix = f"\n\n**[Read on order.life]({link})**" if link else ""

    # Leave room for the suffix within Discord's limit
    max_body = MAX_MESSAGE_LENGTH - len(suffix) - 10
    if len(body) > max_body:
        body = body[:max_body] + "…"

    return body + suffix


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def post_to_forums(entry: dict) -> bool:
    """Create a forum thread for *entry* in every configured forum channel.
    Returns True if at least one post succeeded."""
    message = format_message(entry)
    any_success = False

    for target in TARGETS:
        forum = client.get_channel(target["forum"])
        if forum is None:
            log.warning("Forum channel %s not found (server %s) — skipping",
                        target["forum"], target["server"])
            continue

        try:
            thread, _ = await forum.create_thread(
                name=entry["title"],
                content=message,
            )
            log.info("Posted thread '%s' in forum %s (server %s)",
                     entry["title"], target["forum"], target["server"])
            any_success = True
        except discord.Forbidden:
            log.error("Missing permissions for forum %s (server %s)",
                      target["forum"], target["server"])
        except discord.HTTPException as exc:
            log.error("Discord API error posting to %s: %s", target["forum"], exc)

    return any_success


async def poll_feed() -> None:
    """Main loop: poll the RSS feed and post new entries."""
    await client.wait_until_ready()
    log.info("Feed polling started (interval: %ds)", POLL_INTERVAL)

    while not client.is_closed():
        try:
            posted = load_posted()
            new_entries = fetch_new_entries(posted)

            if new_entries:
                log.info("Found %d new chapter(s) to post", len(new_entries))

            for entry in new_entries:
                success = await post_to_forums(entry)
                if success:
                    posted.add(entry["guid"])
                    save_posted(posted)  # save after each to avoid re-posting on crash

            if not new_entries:
                log.debug("No new chapters")

        except Exception:
            log.exception("Error during feed poll")

        await asyncio.sleep(POLL_INTERVAL)


@client.event
async def on_ready():
    log.info("Logged in as %s (id: %s)", client.user, client.user.id)
    guilds = [g.name for g in client.guilds]
    log.info("Connected to %d server(s): %s", len(guilds), ", ".join(guilds))


async def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        log.error("DISCORD_BOT_TOKEN environment variable is not set")
        sys.exit(1)

    async with client:
        client.loop.create_task(poll_feed())
        await client.start(token)


if __name__ == "__main__":
    asyncio.run(main())
