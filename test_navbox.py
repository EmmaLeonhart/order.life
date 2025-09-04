#!/usr/bin/env python3
"""
Test the navbox at the end of pages
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_month_page, build_year_page

def test_navbox():
    """Test that navbox appears at the end of pages."""
    print("Testing Month Page Navbox (Aquarius):")
    print("-" * 50)
    title, content = build_month_page(3)  # Aquarius
    
    # Show last 10 lines
    lines = content.split('\n')
    for line in lines[-10:]:
        print(line)
    print()
    
    print("Testing Year Page Navbox (12025):")
    print("-" * 50)
    title, content = build_year_page(12025)
    
    # Show last 10 lines
    lines = content.split('\n')
    for line in lines[-10:]:
        print(line)

if __name__ == "__main__":
    test_navbox()