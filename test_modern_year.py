#!/usr/bin/env python3
"""
Show a modern year with overlap information
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def show_modern_year():
    """Show what year 12026 looks like with overlap info."""
    title, content = build_year_page(12026)
    print(f"Title: {title}")
    print("=" * 60)
    # Show first part with overlap info
    lines = content.split('\n')
    for i, line in enumerate(lines):
        print(line)
        if i > 10:  # Show first several lines
            break

if __name__ == "__main__":
    show_modern_year()