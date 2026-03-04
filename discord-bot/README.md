# Gaiad Daily Reading — Discord Forum Post

A GitHub Actions workflow that posts today's Gaiad chapter as a new forum
thread in Discord every day at 00:05 UTC. No bot hosting required.

## How It Works

1. GitHub Actions runs `discord-bot/post_daily.py` daily via cron
2. The script calculates today's Gaian calendar date
3. It loads the corresponding chapter from `epic/chapter_NNN.md`
4. It posts a new forum thread to each Discord forum channel via webhook

**Thread title**: Just the Gaian date (e.g. `♓ Pisces 10, 12026 GE`)
**Thread body**: Chapter number, title, full text, and link to order.life

## Setup (What You Need To Do)

### Step 1: Create Webhooks in Discord (2 min)

For **each** forum channel:

1. Open the forum channel settings (gear icon)
2. Go to **Integrations** → **Webhooks**
3. Click **"New Webhook"**
4. Name it something like "Gaiad Daily Reading"
5. **Copy the webhook URL**

You need webhook URLs for both forum channels:
- Server 1, forum `1478856506500976690`
- Server 2, forum `1477872761807437824`

### Step 2: Add the Secret to GitHub (1 min)

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `DISCORD_WEBHOOKS`
4. Value: both webhook URLs separated by a comma:
   ```
   https://discord.com/api/webhooks/xxx/yyy,https://discord.com/api/webhooks/aaa/bbb
   ```
5. Click **"Add secret"**

### Step 3: Test It

Go to **Actions** → **Daily Gaiad Discord Post** → **Run workflow** → click
the green button. Check your Discord forum channels for the new thread.

That's it. It will now run automatically every day.

## Files

```
discord-bot/
├── post_daily.py     ← Script: calculates Gaian date, loads chapter, posts to Discord
├── .gitignore
└── README.md         ← This file

.github/workflows/
└── discord-daily.yml ← Cron job: runs post_daily.py daily at 00:05 UTC
```

## Manual Testing

```bash
DISCORD_WEBHOOKS="https://discord.com/api/webhooks/xxx/yyy" python discord-bot/post_daily.py
```

## Notes

- No external Python dependencies needed (uses only stdlib)
- The script reads chapters directly from `epic/chapter_NNN.md` in the repo
- Discord message body limit is 2000 chars; longer chapters are truncated
  with a link to the full page on order.life
- The workflow also supports `workflow_dispatch` so you can trigger it manually
