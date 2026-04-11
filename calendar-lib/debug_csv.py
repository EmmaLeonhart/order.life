#!/usr/bin/env python3
"""Debug CSV parsing for year 4."""

import csv
import os

csv_path = os.path.join('GaianDateRangeGenerator', 'gaian_minimal.csv')
year = 4

if os.path.exists(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['GaianYear']) == year:
                print(f"Found year {year}:")
                print(f"  All keys: {list(row.keys())}")
                print(f"  All values: {list(row.values())}")
                for k, v in row.items():
                    print(f"    '{k}': '{v}'")
                break
