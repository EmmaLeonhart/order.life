# Gaiad Daily Reading — Discord Forum Bot

Posts each new daily Gaiad chapter reading from the RSS feed as a new thread
in Discord forum channels.

## Overview

The site generates an RSS feed at `https://order.life/feed.xml` containing
daily Gaiad chapter readings. Each item includes:

- **Title**: Gaian date, any holidays, chapter number and title
  (e.g. `♓ Pisces 10, 12026 GE — Chapter 66: The Meiji Restoration`)
- **Link**: `https://order.life/gaiad/066/`
- **GUID**: `gaiad-12026-066@order.life` (unique per year + chapter)
- **Description**: Intro line + full chapter markdown text

The bot polls this feed periodically and creates a new forum thread for each
unseen chapter in the configured Discord forum channels.

## Target Discord Servers

| Server ID              | Forum Channel ID        | Notes         |
|------------------------|------------------------|---------------|
| `1473062005509193838`  | `1478856506500976690`  | Server 1      |
| `1472675405059064083`  | `1477872761807437824`  | Server 2      |

## Bot Behavior

1. **Poll RSS feed** (`https://order.life/feed.xml`) on a schedule (e.g. every
   30 minutes, or once daily shortly after midnight UTC).
2. **Track posted GUIDs** so chapters are never double-posted. Store seen GUIDs
   in a local file (`posted_guids.json`) or a lightweight database.
3. **For each new item**, create a **forum thread** in both forum channels:
   - **Thread title**: The RSS `<title>` (truncated to 100 chars if needed —
     Discord's limit)
   - **Thread body (starter message)**: The chapter intro + text from
     `<description>`, plus a link to the web version.
   - **Tags**: Optionally apply forum tags if configured (e.g. "Daily Reading").
4. **Error handling**: Log failures, retry on transient errors, skip and log
   permanent failures.

## Implementation Plan

### Option A: discord.py Bot (Recommended)

A Python bot using `discord.py` and `feedparser`.

#### Dependencies

```
discord.py>=2.3
feedparser>=6.0
```

#### Skeleton

```python
import discord
import feedparser
import json
import asyncio
from pathlib import Path

FEED_URL = "https://order.life/feed.xml"
POSTED_GUIDS_FILE = Path("posted_guids.json")

# Forum channels to post to (server_id: forum_channel_id)
TARGETS = [
    {"server": 1473062005509193838, "forum": 1478856506500976690},
    {"server": 1472675405059064083, "forum": 1477872761807437824},
]

POLL_INTERVAL = 1800  # 30 minutes

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def load_posted():
    if POSTED_GUIDS_FILE.exists():
        return set(json.loads(POSTED_GUIDS_FILE.read_text()))
    return set()


def save_posted(guids):
    POSTED_GUIDS_FILE.write_text(json.dumps(sorted(guids)))


async def check_feed():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            feed = feedparser.parse(FEED_URL)
            posted = load_posted()

            for entry in reversed(feed.entries):  # oldest first
                guid = entry.get("id", entry.get("link"))
                if guid in posted:
                    continue

                title = entry.get("title", "Daily Reading")[:100]
                description = entry.get("description", "")
                link = entry.get("link", "")

                # Build the message (Discord max 2000 chars per message)
                body = description
                if len(body) > 1900:
                    body = body[:1900] + "..."
                body += f"\n\n[Read on order.life]({link})"

                for target in TARGETS:
                    try:
                        forum = client.get_channel(target["forum"])
                        if forum is None:
                            print(f"Forum channel {target['forum']} not found")
                            continue
                        await forum.create_thread(
                            name=title,
                            content=body,
                        )
                        print(f"Posted: {title} → {target['forum']}")
                    except Exception as e:
                        print(f"Error posting to {target['forum']}: {e}")

                posted.add(guid)

            save_posted(posted)

        except Exception as e:
            print(f"Feed check error: {e}")

        await asyncio.sleep(POLL_INTERVAL)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


client.loop.create_task(check_feed())
client.run("YOUR_BOT_TOKEN")
```

#### Running

```bash
pip install discord.py feedparser
export DISCORD_BOT_TOKEN="your-token-here"
python bot.py
```

### Option B: GitHub Actions + Discord Webhook

If you don't want to host a persistent bot, use a GitHub Actions workflow
that runs daily after the site build, parses the feed, and posts via Discord
webhook. Webhooks can't create forum threads natively though — you'd need the
bot API for forum thread creation.

### Option C: Third-party RSS-to-Discord services

Services like MonitoRSS or IFTTT can forward RSS items to Discord channels,
but most don't support **forum thread creation** — they post as regular messages.

## Setup Checklist

1. [ ] Create a Discord Application at https://discord.com/developers/applications
2. [ ] Create a Bot user and copy the token
3. [ ] Enable these **Privileged Gateway Intents** (if needed): none required
       for basic forum posting
4. [ ] Invite the bot to both servers with these permissions:
   - `Send Messages`
   - `Create Public Threads` (for forum thread creation)
   - `Read Message History`
   - `View Channels`
   - OAuth2 URL scopes: `bot`, `applications.commands`
   - Permission integer: `326417525760` (covers the above)
   - Invite URL template:
     ```
     https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&permissions=326417525760&scope=bot
     ```
5. [ ] Set the bot token as an environment variable or in a `.env` file
       (never commit the token!)
6. [ ] Run the bot: `python bot.py`
7. [ ] Verify: check that new chapters appear as forum threads

## RSS Feed Details

- **URL**: `https://order.life/feed.xml`
- **Format**: RSS 2.0 with Atom self-link
- **Update frequency**: Rebuilt on every site deploy (GitHub Actions on push
  to master)
- **Items**: One per day of the current Gaian year, up to today
- **Item GUID pattern**: `gaiad-{gaian_year}-{chapter_number:03d}@order.life`
- **Newest items first** in the feed (most recent chapter at top)

## Notes

- The RSS feed is rebuilt on every deploy, so all chapters up to today are
  always present. The bot must track which GUIDs it has already posted to avoid
  duplicates.
- Discord forum thread titles are limited to 100 characters. The RSS titles
  can be longer, so truncate if needed.
- Discord message body limit is 2000 characters. Chapter texts can exceed this.
  Either truncate with a "Read more" link, or split into multiple messages in
  the thread.
- The bot needs to be in both servers and have forum posting permissions in
  both forum channels.
