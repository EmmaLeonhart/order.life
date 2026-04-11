#!/usr/bin/env python3
"""
Show the full page for year 1522 as requested
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def show_1522():
    """Show what year 1522 looks like."""
    title, content = build_year_page(1522)
    print(f"Title: {title}")
    print("=" * 60)
    print(content)

if __name__ == "__main__":
    show_1522()