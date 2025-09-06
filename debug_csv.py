#!/usr/bin/env python3
"""Debug CSV parsing."""

import csv
import os

# Try to load from our new minimal CSV first
minimal_csv = "GaianDateRangeGenerator/gaian_minimal.csv"
if not os.path.exists(minimal_csv):
    minimal_csv = "gaian_bc_dates.csv"  # Fallback to old CSV

bc_info = None
if os.path.exists(minimal_csv):
    print(f"Reading from: {minimal_csv}")
    try:
        with open(minimal_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['GaianYear']) == 3:
                    bc_info = row
                    break
    except Exception as e:
        print(f"Error: {e}")

if bc_info:
    print(f"Found data for year 3:")
    for key, value in bc_info.items():
        print(f"  {key}: '{value}' (length: {len(value)})")
    
    # Apply the fix
    start_date_part = bc_info['StartDate']  # "December 30"
    year_part = bc_info['GregorianLeapYear']  # " 9998 BC"
    start_date_str = f"{start_date_part},{year_part}"  # "December 30, 9998 BC"
    
    print(f"\nFixed start date string: '{start_date_str}'")
    print(f"Repr: {repr(start_date_str)}")
    
    import re
    match = re.match(r'(\w+)\s+(\d+),\s+(\d+)\s+BC', start_date_str)
    if match:
        print(f"Match groups: {match.groups()}")
    else:
        print("No match!")
        # Try different patterns
        patterns = [
            r'(\w+)\s+(\d+)',  # Just month and day
            r'(\w+)\s+(\d+),',  # Month, day, comma
            r'(\w+)\s+(\d+),\s+(\d+)',  # Month, day, comma, year
            r'(\w+)\s+(\d+),\s+(\d+)\s+BC',  # Full pattern
        ]
        for i, pattern in enumerate(patterns):
            match = re.match(pattern, start_date_str)
            print(f"Pattern {i}: {pattern} -> {match.groups() if match else 'No match'}")
else:
    print("No data found!")