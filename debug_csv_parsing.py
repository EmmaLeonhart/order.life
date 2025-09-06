#!/usr/bin/env python3
"""Debug CSV parsing for year 10."""

import csv
import os

csv_path = os.path.join('GaianDateRangeGenerator', 'gaian_minimal.csv')
year = 10

if os.path.exists(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['GaianYear']) == year:
                print(f"Found year {year}:")
                for key, value in row.items():
                    print(f"  '{key}': '{value}'")
                
                # Test the parsing logic
                is_leap_year = row.get('GaianLeapYear', 'False').lower() == 'true'
                days_in_year = int(row.get('DaysInYear', 364))
                print(f"\nParsed results:")
                print(f"  is_leap_year: {is_leap_year}")
                print(f"  days_in_year: {days_in_year}")
                break
