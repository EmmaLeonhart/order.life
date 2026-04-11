#!/usr/bin/env python3
"""
Show a sample month page to verify the format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_month_page

def show_sample_month():
    """Show what Aquarius looks like."""
    title, content = build_month_page(3)  # Aquarius is month 3
    print(f"Title: {title}")
    print("=" * 60)
    # Show first 1000 characters to avoid too much output
    print(content[:1000] + "..." if len(content) > 1000 else content)

if __name__ == "__main__":
    show_sample_month()