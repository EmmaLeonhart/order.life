#!/usr/bin/env python3
"""
Test the Year nav template at the beginning of year pages
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def test_year_nav():
    """Test that Year nav template appears at the beginning of year pages."""
    test_years = [0, 1522, 12025, 12100]
    
    for year in test_years:
        title, content = build_year_page(year)
        
        print(f"Year {year} ({title}):")
        print("-" * 40)
        
        # Show first few lines to see the Year nav template
        lines = content.split('\n')
        for i, line in enumerate(lines[:6]):  # First 6 lines
            print(line)
        
        print("... (rest of content)")
        print()

if __name__ == "__main__":
    test_year_nav()