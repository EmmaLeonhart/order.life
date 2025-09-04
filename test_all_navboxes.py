#!/usr/bin/env python3
"""
Test that ALL page types have the {{Gaian calendar}} navbox at the end
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_page, build_month_page, build_year_page

def test_all_navboxes():
    """Test that day, month, and year pages all have {{Gaian calendar}} at the end."""
    
    print("Testing Day Page Navbox (Sagittarius 15):")
    print("-" * 50)
    title, content = build_page(1, 15)  # Sagittarius 15
    lines = content.split('\n')
    for line in lines[-5:]:  # Last 5 lines
        print(line)
    print()
    
    print("Testing Month Page Navbox (Aquarius):")
    print("-" * 50)
    title, content = build_month_page(3)  # Aquarius
    lines = content.split('\n')
    for line in lines[-3:]:  # Last 3 lines
        print(line)
    print()
    
    print("Testing Year Page Navbox (12025):")
    print("-" * 50)
    title, content = build_year_page(12025)
    lines = content.split('\n')
    for line in lines[-3:]:  # Last 3 lines
        print(line)

if __name__ == "__main__":
    test_all_navboxes()