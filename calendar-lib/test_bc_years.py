#!/usr/bin/env python3
"""
Test BC year formatting
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def test_bc_years():
    """Test various BC and AD year formats."""
    test_years = [1, 1522, 5000, 9999, 10001, 12025, 12100]
    
    for year in test_years:
        title, content = build_year_page(year)
        iso_year = year - 10000
        
        print(f"Gaian Year {year} (ISO {iso_year}):")
        print("=" * 50)
        
        # Extract just the first paragraph
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('==') and not line.startswith('{|'):
                print(line.strip())
                if line.strip().endswith('.'):
                    break
        print()

if __name__ == "__main__":
    test_bc_years()