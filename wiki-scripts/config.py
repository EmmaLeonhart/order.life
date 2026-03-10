"""
config.py
=========
Connection settings for lifeism.miraheze.org wikibot.

Credentials are read from environment variables. Set them before running:
    set WIKI_USERNAME=EmmaBot@EmmaBot
    set WIKI_PASSWORD=your-bot-password

Or create a .env file (never commit this!) and load it manually.
"""
import os

# Wiki connection
WIKI_URL = "lifeism.miraheze.org"
WIKI_PATH = "/w/"

# Credentials from environment (set via Special:BotPasswords on the wiki)
# GitHub Actions uses WIKI_USERNAME / WIKI_PASSWORD; local uses LIFEISM_WIKI_*
USERNAME = os.getenv("WIKI_USERNAME", "") or os.getenv("LIFEISM_WIKI_USERNAME", "")
PASSWORD = os.getenv("WIKI_PASSWORD", "") or os.getenv("LIFEISM_WIKI_PASSWORD", "")

# Bot behaviour
THROTTLE = 1.5          # seconds between edits (standard for Miraheze)
BOT_UA = "LifeismBot/1.0 (User:EmmaBot; lifeism.miraheze.org)"
