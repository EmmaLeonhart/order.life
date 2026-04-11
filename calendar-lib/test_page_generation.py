#!/usr/bin/env python3
"""
Test script to verify month and year page generation without connecting to the wiki.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_month_page, build_year_page

def test_month_pages():
    """Test generation of all month pages."""
    print("Testing month page generation...")
    
    for m_idx in range(1, 15):  # 1-14 inclusive
        title, content = build_month_page(m_idx)
        print(f"Month {m_idx:2d}: {title}")
        print(f"Content length: {len(content)} characters")
        
        # Check that content contains expected elements
        if "[[Gaiad calendar]]" in content:
            print("OK Contains Gaiad calendar link")
        else:
            print("FAIL Missing Gaiad calendar link")
            
        if "Category:Gaiad calendar months" in content:
            print("OK Contains month category")
        else:
            print("FAIL Missing month category")
            
        # Check for Overview section
        if "== Overview ==" in content:
            print("OK Contains Overview section")
        else:
            print("FAIL Missing Overview section")
            
        # Check for date ranges section
        if "Gregorian date ranges" in content:
            print("OK Contains date ranges section")
        else:
            print("FAIL Missing date ranges section")
            
        print("-" * 50)

def test_year_pages():
    """Test generation of sample year pages."""
    print("Testing year page generation...")
    
    # Test a few sample years including edge cases
    test_years = [1, 100, 1000, 10000, 12024, 12025, 12100]
    
    for year in test_years:
        title, content = build_year_page(year)
        print(f"Year {year}: {title}")
        print(f"Content length: {len(content)} characters")
        
        # Check that content contains expected elements
        if "[[Gaiad calendar]]" in content:
            print("OK Contains Gaiad calendar link")
        else:
            print("FAIL Missing Gaiad calendar link")
            
        if "Category:Gaiad calendar years" in content:
            print("OK Contains year category")
        else:
            print("FAIL Missing year category")
            
        # Check ISO year conversion
        iso_year = year - 10000
        if f"ISO week-year {iso_year}" in content:
            print(f"OK Contains correct ISO year conversion ({iso_year})")
        else:
            print(f"FAIL Missing or incorrect ISO year conversion")
        
        # Check for date range
        if "goes from" in content and "to" in content:
            print("OK Contains date range")
        else:
            print("FAIL Missing date range")
            
        # Check for Overview section
        if "== Overview ==" in content:
            print("OK Contains Overview section")
        else:
            print("FAIL Missing Overview section")
            
        # Check for Gregorian year overlap information
        if "corresponds" in content and ("entirely" in content or "mostly" in content):
            print("OK Contains Gregorian year overlap info")
        else:
            print("FAIL Missing Gregorian year overlap info")
            
        print("-" * 50)

if __name__ == "__main__":
    test_month_pages()
    print("\n" + "=" * 70 + "\n")
    test_year_pages()