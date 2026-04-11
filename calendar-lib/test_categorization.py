#!/usr/bin/env python3
"""
Test the improved categorization system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_month_page, build_year_page, get_century_category, get_decade_category

def test_month_categories():
    """Test month categorization with sort keys."""
    print("Testing Month Categories:")
    print("=" * 50)
    
    # Test a few months
    test_months = [1, 3, 13, 14]  # Sagittarius, Aquarius, Ophiuchus, Horus
    
    for m_idx in test_months:
        title, content = build_month_page(m_idx)
        print(f"Month {m_idx} ({title}):")
        
        # Extract categories
        lines = content.split('\n')
        for line in lines:
            if line.startswith('[[Category:'):
                print(f"  {line}")
        print()

def test_year_categories():
    """Test year categorization with century, decade, and DEFAULTSORT."""
    print("Testing Year Categories:")
    print("=" * 50)
    
    # Test various years to show different centuries and decades
    test_years = [0, 9, 25, 100, 1522, 12025, 12100]
    
    for year in test_years:
        title, content = build_year_page(year)
        
        print(f"Year {year}:")
        print(f"  Century: {get_century_category(year)}")
        print(f"  Decade: {get_decade_category(year)}")
        
        # Extract categories and DEFAULTSORT from actual content
        lines = content.split('\n')
        for line in lines:
            if line.startswith('[[Category:') or line.startswith('{{DEFAULTSORT:'):
                print(f"  {line}")
        print()

if __name__ == "__main__":
    test_month_categories()
    print("\n" + "=" * 70 + "\n")
    test_year_categories()