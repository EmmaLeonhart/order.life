#!/usr/bin/env python3
"""
Test the Indian calendar correspondence integration for Diwali.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from zodiac_wiki_pages import (
    gregorian_to_gaian_date,
    indian_overlap_table,
    indian_event_matches_gregorian,
    INDIAN_EVENTS,
    build_holiday_dates_for_year
)
from datetime import date

def test_diwali_detection():
    """Test if Diwali dates are correctly detected."""
    print("=== Testing Diwali Detection ===")

    # Test some known Diwali dates
    test_dates = [
        (2024, 11, 1),  # Diwali 2024
        (2023, 11, 12), # Diwali 2023
        (2022, 10, 24), # Diwali 2022
        (2024, 11, 2),  # Day after Diwali 2024 (should not match)
    ]

    diwali_event = None
    for event in INDIAN_EVENTS:
        if event["name"] == "Diwali":
            diwali_event = event
            break

    if not diwali_event:
        print("ERROR: Diwali event not found in INDIAN_EVENTS")
        return

    for year, month, day in test_dates:
        test_date = date(year, month, day)
        matches = indian_event_matches_gregorian(test_date, diwali_event)
        gaian_month, gaian_day, gaian_month_name = gregorian_to_gaian_date(test_date)

        print(f"{test_date} -> {gaian_month_name} {gaian_day}: Diwali = {matches}")

def test_gaian_libra_overlaps():
    """Test which Indian festivals overlap with Libra dates."""
    print("\n=== Testing Libra Date Overlaps ===")

    # Test Libra 26 (where Diwali 2024 falls) and Libra 18 (common Diwali date)
    libra_month = 11  # Libra is the 11th month

    for libra_day in [18, 26]:
        print(f"\nTesting overlaps for Libra {libra_day}...")

        # Manual check for debugging
        diwali_event = None
        for event in INDIAN_EVENTS:
            if event["name"] == "Diwali":
                diwali_event = event
                break

        if diwali_event:
            matches = 0
            total_years = 2030 - 2020 + 1
            print(f"Checking {total_years} years from 2020 to 2030...")

            for year in range(2020, 2031):
                # Check all valid dates in the year for this event
                for month in range(1, 13):
                    # Get days in this month
                    if month in [1, 3, 5, 7, 8, 10, 12]:
                        days_in_month = 31
                    elif month in [4, 6, 9, 11]:
                        days_in_month = 30
                    elif month == 2:
                        # Check for leap year
                        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                            days_in_month = 29
                        else:
                            days_in_month = 28

                    for day in range(1, days_in_month + 1):
                        try:
                            test_date = date(year, month, day)
                            if indian_event_matches_gregorian(test_date, diwali_event):
                                g_m, g_d, g_name = gregorian_to_gaian_date(test_date)
                                if g_m == libra_month and g_d == libra_day:
                                    matches += 1
                                    print(f"  Found match: {test_date} -> {g_name} {g_d}")
                                    break
                        except (ValueError, AttributeError):
                            continue

            print(f"Total matches for Libra {libra_day}: {matches} out of {total_years} years")

        # Now test the function
        overlap_result = indian_overlap_table(libra_month, libra_day, 2020, 2030)
        print(overlap_result)

def test_holiday_dates_2024():
    """Test the holiday dates block for 2024."""
    print("\n=== Testing Holiday Dates for 2024 ===")

    try:
        holidays_2024 = build_holiday_dates_for_year(12024)  # 2024 in Gaian calendar
        # Remove special characters that cause encoding issues
        cleaned_output = holidays_2024.replace('\u014d', 'o').replace('\u2013', '-').replace('\u2014', '-')
        print(cleaned_output)
    except UnicodeError as e:
        print(f"Unicode error: {e}")
        print("Skipping holiday dates output due to encoding issues")

if __name__ == "__main__":
    try:
        test_diwali_detection()
        test_gaian_libra_overlaps()
        test_holiday_dates_2024()

        print("\n" + "="*50)
        print("INTEGRATION TEST COMPLETE")
        print("="*50)

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()