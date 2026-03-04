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

The bot polls this feed every 30 minutes and creates a new forum thread for
each unseen chapter in the configured Discord forum channels.

## Target Discord Servers

| Server ID              | Forum Channel ID        | Notes         |
|------------------------|------------------------|---------------|
| `1473062005509193838`  | `1478856506500976690`  | Server 1      |
| `1472675405059064083`  | `1477872761807437824`  | Server 2      |

## What the Bot Does

1. **Polls the RSS feed** (`https://order.life/feed.xml`) every 30 minutes
2. **Tracks posted GUIDs** in `posted_guids.json` so chapters are never
   double-posted
3. **Creates a forum thread** in both forum channels for each new entry:
   - Thread title: the RSS `<title>` (truncated to 100 chars)
   - Thread body: chapter text + link to the web version
4. **Logs everything** to stdout — errors, posts, connection status
5. **Saves state after each post** so a crash won't cause re-posts

## Setup Checklist (What You Need To Do)

### Step 1: Create a Discord Bot Application

1. Go to **https://discord.com/developers/applications**
2. Click **"New Application"** → name it something like "Gaiad Daily Reading"
3. Go to the **Bot** tab on the left sidebar
4. Click **"Reset Token"** → copy the token and save it somewhere safe
5. Under **Privileged Gateway Intents**: no special intents are needed

### Step 2: Invite the Bot to Both Servers

Use this URL template (replace `YOUR_APP_ID` with the Application ID from the
"General Information" tab):

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&permissions=326417525760&scope=bot
```

This grants the bot:
- `Send Messages`
- `Create Public Threads` (for forum thread creation)
- `Read Message History`
- `View Channels`

**Do this for both servers.**

### Step 3: Install and Run

```bash
cd discord-bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env and paste your bot token
```

Then run:

```bash
# Linux / Mac
export $(cat .env | xargs) && python bot.py

# Windows (PowerShell)
$env:DISCORD_BOT_TOKEN="your-token-here"
python bot.py

# Windows (CMD)
set DISCORD_BOT_TOKEN=your-token-here
python bot.py
```

### Step 4: Verify

- The bot should log `Logged in as YourBot#1234` and list the servers
- Wait for the next poll cycle (or restart the bot) and check the forum
  channels for new threads
- If the feed has chapters the bot hasn't seen, they'll be posted immediately

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DISCORD_BOT_TOKEN` | (required) | Bot authentication token |
| `POLL_INTERVAL` | `1800` | Seconds between feed checks (30 min) |

## Hosting Options

The bot needs to run 24/7 to catch daily posts. Options:

- **Your own PC**: just leave a terminal running (simplest to start)
- **A VPS** (e.g. Oracle Cloud free tier, DigitalOcean $4/mo): run with
  `nohup python bot.py &` or use `systemd`
- **Railway / Render / Fly.io**: free or cheap container hosting, set
  `DISCORD_BOT_TOKEN` as an environment secret
- **Raspberry Pi**: low-power always-on option at home

## Files

```
discord-bot/
├── bot.py              ← The bot implementation
├── requirements.txt    ← Python dependencies
├── .env.example        ← Template for environment variables
├── .gitignore          ← Keeps .env and state files out of git
├── posted_guids.json   ← (created at runtime) tracks posted chapters
└── README.md           ← This file
```

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
  always present. The bot tracks which GUIDs it has already posted to avoid
  duplicates.
- Discord forum thread titles are limited to 100 characters. The RSS titles
  can be longer, so the bot truncates if needed.
- Discord message body limit is 2000 characters. Chapter texts can exceed this.
  The bot truncates with a "Read more" link to order.life.
- The bot needs to be in both servers and have forum posting permissions in
  both forum channels.
