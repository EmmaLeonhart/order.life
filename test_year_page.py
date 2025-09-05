#!/usr/bin/env python3
"""Quick test to see what the year page output looks like."""

import sys
sys.path.append('.')

from zodiac_wiki_pages import build_year_page

# Test with year 12024 (regular year) 
title, content = build_year_page(12024)

print(f"TITLE: {title}")
print("\nCONTENT:")
print("=" * 80)
print(content)