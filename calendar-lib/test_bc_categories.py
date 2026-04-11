#!/usr/bin/env python3
"""
Test BC year categorization to show the limitation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def test_bc_categories():
    """Test BC year categorization limitation."""
    # Test some BC years
    test_years = [1, 1522, 5000, 9999]  # These will be BC years
    
    for year in test_years:
        title, content = build_year_page(year)
        iso_year = year - 10000
        
        print(f"Year {year} (ISO {iso_year} = {abs(iso_year-1)} BC):")
        print("-" * 50)
        
        # Show categories
        lines = content.split('\n')
        for line in lines:
            if line.startswith('[[Category:'):
                print(f"Category: {line}")
        
        # Note the limitation
        if iso_year <= 0:
            print("NOTE: BC years are always categorized as common years")
            print("      due to Python date limitations with historical dates.")
        
        print()

if __name__ == "__main__":
    test_bc_categories()