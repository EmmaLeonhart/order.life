#!/usr/bin/env python3
"""
Test leap year categorization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def test_leap_categories():
    """Test leap year and regular year categorization."""
    # Test known leap years (53-week years) and regular years
    test_years = [12024, 12025, 12026, 12027, 12020, 12021]
    
    for year in test_years:
        title, content = build_year_page(year)
        iso_year = year - 10000
        
        print(f"Year {year} (ISO {iso_year}):")
        print("-" * 40)
        
        # Check if it has intercalary days
        if "intercalary days of [[Horus]]" in content:
            leap_status = "LEAP YEAR (has Horus month)"
        else:
            leap_status = "Regular year"
        
        print(f"Status: {leap_status}")
        
        # Show categories
        lines = content.split('\n')
        for line in lines:
            if line.startswith('[[Category:'):
                print(f"Category: {line}")
        
        print()

if __name__ == "__main__":
    test_leap_categories()