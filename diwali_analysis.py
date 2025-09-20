#!/usr/bin/env python3
"""
Analyze Diwali date patterns and their frequency in the Gaian calendar system.

Diwali occurs on the new moon (Amavasya) of the Hindu month Kartik,
typically falling between mid-October and mid-November.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'GaianNodaTimeWrappers'))

from datetime import datetime, date
from collections import defaultdict, Counter
import traceback

# Historical Diwali dates (Gregorian calendar)
# Source: Various Hindu calendar sources and astronomical calculations
DIWALI_DATES = {
    2000: (2000, 10, 26),
    2001: (2001, 11, 14),
    2002: (2002, 11, 4),
    2003: (2003, 10, 25),
    2004: (2004, 11, 11),
    2005: (2005, 11, 1),
    2006: (2006, 10, 21),
    2007: (2007, 11, 9),
    2008: (2008, 10, 28),
    2009: (2009, 10, 17),
    2010: (2010, 11, 5),
    2011: (2011, 10, 26),
    2012: (2012, 11, 13),
    2013: (2013, 11, 3),
    2014: (2014, 10, 23),
    2015: (2015, 11, 11),
    2016: (2016, 10, 30),
    2017: (2017, 10, 19),
    2018: (2018, 11, 7),
    2019: (2019, 10, 27),
    2020: (2020, 11, 14),
    2021: (2021, 11, 4),
    2022: (2022, 10, 24),
    2023: (2023, 11, 12),
    2024: (2024, 11, 1),
    2025: (2025, 10, 20),
    2026: (2026, 11, 8),
    2027: (2027, 10, 29),
    2028: (2028, 10, 17),
    2029: (2029, 11, 5),
    2030: (2030, 10, 26),
}

def gregorian_to_gaian_simple(year, month, day):
    """
    Simple conversion from Gregorian to Gaian calendar using the logic from GaianTools.
    This is a simplified version without importing the full .NET library.
    """
    try:
        # Create a date object
        dt = datetime(year, month, day)

        # Get ISO week year and week number
        # Python's isocalendar() returns (ISO year, ISO week, ISO weekday)
        iso_year, iso_week, iso_weekday = dt.isocalendar()

        # Convert to Gaian year
        gaian_year = iso_year + 10000

        # Convert week to month and day
        # Gaian months have 4 weeks each (weeks 1-4 = month 1, weeks 5-8 = month 2, etc.)
        gaian_month = ((iso_week - 1) // 4) + 1
        week_in_month = ((iso_week - 1) % 4) + 1

        # Day within the month: (week_in_month - 1) * 7 + weekday
        gaian_day = ((week_in_month - 1) * 7) + iso_weekday

        # Handle intercalary month (Horus - month 14)
        if gaian_month > 13:
            gaian_month = 14
            gaian_day = ((iso_week - 53) * 7) + iso_weekday + 7  # Adjust for Horus

        return gaian_year, gaian_month, gaian_day

    except Exception as e:
        print(f"Error converting {year}-{month:02d}-{day:02d}: {e}")
        return None, None, None

def get_gaian_month_name(month):
    """Get the Gaian month name."""
    month_names = [
        "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus",
        "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Ophiuchus", "Horus"
    ]
    if 1 <= month <= 14:
        return month_names[month - 1]
    return f"Month{month}"

def analyze_diwali_patterns():
    """Analyze when Diwali occurs in the Gaian calendar."""
    print("=== Diwali in the Gaian Calendar ===\n")

    gaian_dates = []
    gaian_month_counts = Counter()
    gaian_day_counts = Counter()
    gaian_month_day_counts = Counter()

    print("Diwali dates conversion (Gregorian -> Gaian):")
    print(f"{'Year':<6} {'Gregorian':<12} {'Gaian Year':<11} {'Gaian Date':<25}")
    print("-" * 70)

    for year in sorted(DIWALI_DATES.keys()):
        greg_year, greg_month, greg_day = DIWALI_DATES[year]
        gaian_year, gaian_month, gaian_day = gregorian_to_gaian_simple(greg_year, greg_month, greg_day)

        if gaian_year is not None:
            gaian_dates.append((gaian_year, gaian_month, gaian_day))
            gaian_month_counts[gaian_month] += 1
            gaian_day_counts[gaian_day] += 1
            gaian_month_day_counts[(gaian_month, gaian_day)] += 1

            greg_str = f"{greg_year}-{greg_month:02d}-{greg_day:02d}"
            gaian_month_name = get_gaian_month_name(gaian_month)
            gaian_str = f"{gaian_month_name} {gaian_day}, {gaian_year}"

            print(f"{year:<6} {greg_str:<12} {gaian_year:<11} {gaian_str:<25}")

    print(f"\n=== Analysis of {len(gaian_dates)} Diwali dates ===")

    # Month frequency analysis
    print("\nGaian Month Frequency:")
    print(f"{'Month':<12} {'Count':<6} {'Percentage':<10}")
    print("-" * 30)
    total = len(gaian_dates)
    for month in sorted(gaian_month_counts.keys()):
        count = gaian_month_counts[month]
        percentage = (count / total) * 100
        month_name = get_gaian_month_name(month)
        print(f"{month_name:<12} {count:<6} {percentage:>7.1f}%")

    # Day frequency analysis
    print(f"\nMost Common Gaian Days:")
    print(f"{'Day':<4} {'Count':<6} {'Percentage':<10}")
    print("-" * 22)
    for day, count in gaian_day_counts.most_common(10):
        percentage = (count / total) * 100
        print(f"{day:<4} {count:<6} {percentage:>7.1f}%")

    # Month-Day combination frequency
    print(f"\nMost Common Gaian Month-Day Combinations:")
    print(f"{'Month-Day':<20} {'Count':<6} {'Percentage':<10}")
    print("-" * 38)
    for (month, day), count in gaian_month_day_counts.most_common(10):
        percentage = (count / total) * 100
        month_name = get_gaian_month_name(month)
        combo = f"{month_name} {day}"
        print(f"{combo:<20} {count:<6} {percentage:>7.1f}%")

    # Year span analysis
    if gaian_dates:
        gaian_years = [gy for gy, gm, gd in gaian_dates]
        print(f"\nGaian Year Range: {min(gaian_years)} to {max(gaian_years)}")
        print(f"Gregorian Year Range: {min(DIWALI_DATES.keys())} to {max(DIWALI_DATES.keys())}")

    return gaian_dates, gaian_month_counts, gaian_day_counts, gaian_month_day_counts

def generate_extended_diwali_dates(start_year=1950, end_year=2050):
    """
    Generate more Diwali dates using the astronomical pattern.
    Diwali follows a ~19-year Metonic cycle with some variation.
    """
    print(f"\n=== Extended Diwali Analysis ({start_year}-{end_year}) ===")

    # Use the known pattern: Diwali typically occurs between Oct 13 - Nov 14
    # and follows lunar cycles, approximately every 354 days (lunar year)
    # with adjustments for the solar year difference

    base_dates = []

    # Extend backwards and forwards from known dates
    known_years = sorted(DIWALI_DATES.keys())

    # For years before our known range
    for year in range(start_year, min(known_years)):
        # Estimate based on lunar cycle offset (~11 days earlier each year)
        # with periodic adjustments
        offset_years = min(known_years) - year
        base_date = datetime(DIWALI_DATES[min(known_years)][0],
                           DIWALI_DATES[min(known_years)][1],
                           DIWALI_DATES[min(known_years)][2])

        # Rough approximation: ~11 days earlier per year, with cycle adjustments
        estimated_day_offset = -(offset_years * 11) % 365

        # This is a very rough approximation - real calculation would need
        # proper astronomical/calendar libraries
        continue  # Skip for now due to complexity

    print("Note: Extended date calculation requires proper Hindu calendar libraries")
    print("Current analysis is based on historical data from 2000-2030")

    return base_dates

if __name__ == "__main__":
    try:
        gaian_dates, month_counts, day_counts, month_day_counts = analyze_diwali_patterns()

        print("\n" + "="*60)
        print("KEY FINDINGS:")

        # Find most common month
        if month_counts:
            most_common_month = max(month_counts.items(), key=lambda x: x[1])
            month_name = get_gaian_month_name(most_common_month[0])
            month_pct = (most_common_month[1] / len(gaian_dates)) * 100
            print(f"• Diwali most often occurs in {month_name} ({month_pct:.1f}% of the time)")

        # Find most common day range
        if day_counts:
            common_days = [day for day, count in day_counts.most_common(5)]
            print(f"• Most common Gaian days: {', '.join(map(str, common_days))}")

        # Find most common combination
        if month_day_counts:
            most_common_combo = max(month_day_counts.items(), key=lambda x: x[1])
            (month, day), count = most_common_combo
            month_name = get_gaian_month_name(month)
            combo_pct = (count / len(gaian_dates)) * 100
            print(f"• Most frequent date: {month_name} {day} ({combo_pct:.1f}% of years)")

        print("="*60)

    except Exception as e:
        print(f"Error during analysis: {e}")
        traceback.print_exc()