#!/usr/bin/env python3
"""
Test the comprehensive date conversion table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_gregorian_correspondence_table, build_year_page

def test_date_table():
    """Test the date conversion table for a regular and leap year."""
    print("Testing Regular Year (12025):")
    print("=" * 50)
    table = build_gregorian_correspondence_table(12025)
    # Show first few lines to verify format
    lines = table.split('\n')
    for i, line in enumerate(lines[:15]):  # First 15 lines
        print(line)
    print("... (truncated)")
    print()
    
    print("Testing Leap Year (12026):")
    print("=" * 50)
    table = build_gregorian_correspondence_table(12026)
    lines = table.split('\n')
    # Show the last part with Horus days
    for line in lines[-15:]:  # Last 15 lines to see Horus
        print(line)
    print()
    
    print("Testing BC Year (1522 - should show limitation):")
    print("=" * 50)
    table = build_gregorian_correspondence_table(1522)
    print(table)

if __name__ == "__main__":
    test_date_table()