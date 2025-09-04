#!/usr/bin/env python3
"""
Show a complete leap year page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def show_leap_year():
    """Show what a leap year (12026) looks like completely."""
    title, content = build_year_page(12026)
    print(f"Title: {title}")
    print("=" * 60)
    print(content)

if __name__ == "__main__":
    show_leap_year()