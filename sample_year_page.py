#!/usr/bin/env python3
"""
Show a sample year page to verify the format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def show_sample_year():
    """Show what year 12025 looks like."""
    title, content = build_year_page(12025)
    print(f"Title: {title}")
    print("=" * 60)
    print(content)

if __name__ == "__main__":
    show_sample_year()