#!/usr/bin/env python3
"""
Extract the earliest and latest possible Diwali dates from our analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, date, timedelta
from collections import defaultdict, Counter

def gregorian_to_gaian_simple(year, month, day):
    """Simple conversion from Gregorian to Gaian calendar."""
    try:
        dt = datetime(year, month, day)
        iso_year, iso_week, iso_weekday = dt.isocalendar()
        gaian_year = iso_year + 10000
        gaian_month = ((iso_week - 1) // 4) + 1
        week_in_month = ((iso_week - 1) % 4) + 1
        gaian_day = ((week_in_month - 1) * 7) + iso_weekday

        if gaian_month > 13:
            gaian_month = 14
            gaian_day = ((iso_week - 53) * 7) + iso_weekday + 7

        return gaian_year, gaian_month, gaian_day
    except Exception as e:
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

def analyze_diwali_date_range():
    """Analyze the range of Diwali dates from known historical data."""

    # Known historical Diwali dates
    known_dates = {
        2000: (10, 26), 2001: (11, 14), 2002: (11, 4), 2003: (10, 25), 2004: (11, 11),
        2005: (11, 1), 2006: (10, 21), 2007: (11, 9), 2008: (10, 28), 2009: (10, 17),
        2010: (11, 5), 2011: (10, 26), 2012: (11, 13), 2013: (11, 3), 2014: (10, 23),
        2015: (11, 11), 2016: (10, 30), 2017: (10, 19), 2018: (11, 7), 2019: (10, 27),
        2020: (11, 14), 2021: (11, 4), 2022: (10, 24), 2023: (11, 12), 2024: (11, 1),
        2025: (10, 20), 2026: (11, 8), 2027: (10, 29), 2028: (10, 17), 2029: (11, 5),
        2030: (10, 26)
    }

    print("=== Diwali Date Range Analysis ===\n")

    # Convert to day of year for easy comparison
    gregorian_dates = []
    gaian_dates = []

    for year, (month, day) in known_dates.items():
        # Gregorian analysis
        diwali_date = date(year, month, day)
        day_of_year = diwali_date.timetuple().tm_yday
        gregorian_dates.append((diwali_date, day_of_year, f"{month:02d}-{day:02d}"))

        # Gaian analysis
        gaian_year, gaian_month, gaian_day = gregorian_to_gaian_simple(year, month, day)
        if gaian_year is not None:
            gaian_month_name = get_gaian_month_name(gaian_month)
            gaian_dates.append((diwali_date, gaian_month, gaian_day, gaian_month_name))

    # Find extremes in Gregorian calendar
    earliest_greg = min(gregorian_dates, key=lambda x: x[1])
    latest_greg = max(gregorian_dates, key=lambda x: x[1])

    print("GREGORIAN CALENDAR RANGE:")
    print(f"Earliest: {earliest_greg[0]} (Day {earliest_greg[1]} of year)")
    print(f"Latest:   {latest_greg[0]} (Day {latest_greg[1]} of year)")
    print(f"Range:    {latest_greg[1] - earliest_greg[1]} days")

    # Find extremes in Gaian calendar
    # Sort by month first, then by day
    gaian_sorted = sorted(gaian_dates, key=lambda x: (x[1], x[2]))
    earliest_gaian = gaian_sorted[0]
    latest_gaian = gaian_sorted[-1]

    print(f"\nGAIAN CALENDAR RANGE:")
    print(f"Earliest: {earliest_gaian[3]} {earliest_gaian[2]} ({earliest_gaian[0]})")
    print(f"Latest:   {latest_gaian[3]} {latest_gaian[2]} ({latest_gaian[0]})")

    # Calculate all unique Gaian dates and their frequencies
    gaian_date_counter = Counter()
    for _, gaian_month, gaian_day, gaian_month_name in gaian_dates:
        gaian_date_counter[(gaian_month, gaian_day, gaian_month_name)] += 1

    print(f"\nUNIQUE GAIAN DATES ({len(gaian_date_counter)} total):")
    for (month, day, month_name), count in sorted(gaian_date_counter.items()):
        print(f"  {month_name} {day}: {count} time(s)")

    # Extended range analysis (theoretical limits)
    print(f"\n=== THEORETICAL DIWALI RANGE ===")
    print("Based on astronomical patterns, Diwali can theoretically occur:")

    # Diwali window is typically Oct 13 - Nov 14 (about 32 days)
    theoretical_earliest = date(2024, 10, 13)  # Using 2024 as reference year
    theoretical_latest = date(2024, 11, 14)

    # Convert to Gaian
    earliest_gaian_th = gregorian_to_gaian_simple(2024, 10, 13)
    latest_gaian_th = gregorian_to_gaian_simple(2024, 11, 14)

    if earliest_gaian_th[0] is not None and latest_gaian_th[0] is not None:
        earliest_name = get_gaian_month_name(earliest_gaian_th[1])
        latest_name = get_gaian_month_name(latest_gaian_th[1])

        print(f"Theoretical earliest: {earliest_name} {earliest_gaian_th[2]} (Oct 13)")
        print(f"Theoretical latest:   {latest_name} {latest_gaian_th[2]} (Nov 14)")
        print(f"Theoretical span:     ~32 Gregorian days")

    # Observed vs theoretical comparison
    print(f"\n=== OBSERVED VS THEORETICAL ===")
    observed_earliest_greg = earliest_greg[0]
    observed_latest_greg = latest_greg[0]

    print(f"Observed range:    {observed_earliest_greg.strftime('%b %d')} - {observed_latest_greg.strftime('%b %d')}")
    print(f"Theoretical range: Oct 13 - Nov 14")
    print(f"Range utilization: {(observed_latest_greg - observed_earliest_greg).days + 1} of ~32 possible days")

    # Show all observed dates chronologically within a year
    print(f"\n=== ALL OBSERVED DIWALI DATES (sorted by calendar date) ===")

    # Create a list of (month, day) tuples and sort them
    month_day_pairs = [(month, day) for year, (month, day) in known_dates.items()]
    unique_month_days = sorted(set(month_day_pairs))

    print("Gregorian Date -> Gaian Date:")
    for month, day in unique_month_days:
        # Use 2024 as reference year for conversion
        gaian_year, gaian_month, gaian_day = gregorian_to_gaian_simple(2024, month, day)
        if gaian_year is not None:
            gaian_month_name = get_gaian_month_name(gaian_month)
            # Count how many times this date occurred
            count = month_day_pairs.count((month, day))
            print(f"  {month:2d}-{day:02d} -> {gaian_month_name} {gaian_day} ({count} time(s))")

if __name__ == "__main__":
    analyze_diwali_date_range()