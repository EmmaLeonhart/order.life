#!/usr/bin/env python3
"""Debug full year 4 leap year logic."""

import csv
import os
import sys
sys.path.append('.')

from zodiac_wiki_pages import build_year_page

# Debug the CSV parsing directly
csv_path = os.path.join('GaianDateRangeGenerator', 'gaian_minimal.csv')
year = 4

print("=== CSV Debug ===")
if os.path.exists(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['GaianYear']) == year:
                print(f"Found year {year} in CSV:")
                print(f"  DaysInYear column: '{row.get('DaysInYear', 'NOT_FOUND')}'")
                print(f"  None column: '{row.get(None, 'NOT_FOUND')}'")
                
                # Test the exact logic from the function
                is_leap_year = row.get('DaysInYear', 'False').lower() == 'true'  # Actually GaianLeapYear
                none_data = row.get(None, [])
                if isinstance(none_data, list) and none_data:
                    days_in_year = int(none_data[0])
                else:
                    days_in_year = int(str(none_data).strip("[]'"))
                
                print(f"  Parsed is_leap_year: {is_leap_year}")
                print(f"  Parsed days_in_year: {days_in_year}")
                break

print("\n=== Page Build Test ===")
title, content = build_year_page(4)

# Check for leap year indicators in content
if "371 days, including the 7 intercalary days of [[Horus]]" in content:
    print("✓ Correct leap year description found")
else:
    print("✗ Missing leap year description")
    
if "[[Category:Gaian leap years]]" in content:
    print("✓ Correct leap year category found")  
else:
    print("✗ Missing leap year category")
    
if "[[Category:Gaian common years]]" in content:
    print("✗ Incorrect common year category found")
else:
    print("✓ No common year category")
