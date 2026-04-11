#!/usr/bin/env python3
"""
Test a full year page with the date conversion table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_year_page

def show_year_with_table():
    """Show a year with the conversion table (truncated for readability)."""
    title, content = build_year_page(12025)
    
    print(f"Title: {title}")
    print("=" * 60)
    
    # Show content up to the table
    lines = content.split('\n')
    in_table = False
    table_line_count = 0
    
    for line in lines:
        if "== Gregorian correspondence" in line:
            in_table = True
            print(line)
        elif in_table and line.startswith('|}'):
            print("... (table continues with all 364 days)")
            print(line)
            in_table = False
        elif in_table:
            table_line_count += 1
            if table_line_count <= 10:  # Show first 10 table lines
                print(line)
            elif table_line_count == 11:
                print("... (showing only first few rows)")
        else:
            print(line)

if __name__ == "__main__":
    show_year_with_table()