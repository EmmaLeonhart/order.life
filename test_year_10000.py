#!/usr/bin/env python3
"""Test script to verify year 10000 GE works correctly."""

import sys
import os

# Import the functions from the main zodiac script
sys.path.append(os.path.dirname(__file__))
from zodiac_wiki_pages import build_gregorian_correspondence_table, build_holiday_dates_for_year

def test_year_10000():
    """Test that year 10000 GE can be processed without errors."""
    print("Testing year 10000 GE...")
    
    # Test Gregorian correspondence table
    print("\n1. Testing Gregorian correspondence table...")
    try:
        gregorian_table = build_gregorian_correspondence_table(10000)
        if "outside supported date range" in gregorian_table:
            print("FAILED: Still getting 'outside supported date range' error")
            print(f"Result: {gregorian_table}")
            return False
        else:
            print("SUCCESS: Gregorian correspondence table generated")
            print(f"Preview: {gregorian_table[:200]}...")
    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")
        return False
    
    # Test holiday dates
    print("\n2. Testing holiday dates...")
    try:
        holiday_table = build_holiday_dates_for_year(10000)
        if "outside supported date range" in holiday_table:
            print("FAILED: Still getting 'outside supported date range' error")
            print(f"Result: {holiday_table}")
            return False
        else:
            print("SUCCESS: Holiday dates table generated")
            print(f"Preview: {holiday_table[:200]}...")
    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")
        return False
    
    print("\nAll tests passed! Year 10000 GE should now work on the wiki.")
    return True

if __name__ == "__main__":
    test_year_10000()