#!/usr/bin/env python3
"""Quick test to debug BC year parsing."""

import sys
sys.path.append('.')

from zodiac_wiki_pages import build_year_page

# Test with year 10 (leap year from CSV)
title, content = build_year_page(10)

print(f"TITLE: {title}")
print("\nCONTENT:")
print("=" * 80)
print(content)