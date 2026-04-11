#!/usr/bin/env python3
"""
Corrected analysis of Diwali date ranges and distribution.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, date
from collections import Counter

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

def analyze_diwali_distribution():
    """Properly analyze Diwali date distribution and range."""

    # Known Diwali dates (verified historical data)
    known_dates = {
        2000: (10, 26), 2001: (11, 14), 2002: (11, 4), 2003: (10, 25), 2004: (11, 11),
        2005: (11, 1), 2006: (10, 21), 2007: (11, 9), 2008: (10, 28), 2009: (10, 17),
        2010: (11, 5), 2011: (10, 26), 2012: (11, 13), 2013: (11, 3), 2014: (10, 23),
        2015: (11, 11), 2016: (10, 30), 2017: (10, 19), 2018: (11, 7), 2019: (10, 27),
        2020: (11, 14), 2021: (11, 4), 2022: (10, 24), 2023: (11, 12), 2024: (11, 1),
        2025: (10, 20), 2026: (11, 8), 2027: (10, 29), 2028: (10, 17), 2029: (11, 5),
        2030: (10, 26)
    }

    print("=== CORRECTED DIWALI ANALYSIS ===")
    print(f"Analyzing {len(known_dates)} verified Diwali dates (2000-2030)\n")

    # Convert all dates and collect data
    all_conversions = []
    gaian_dates = []

    print("Year  Gregorian    Gaian Date")
    print("-" * 35)

    for year in sorted(known_dates.keys()):
        month, day = known_dates[year]
        gaian_year, gaian_month, gaian_day = gregorian_to_gaian_simple(year, month, day)

        if gaian_year is not None:
            gaian_month_name = get_gaian_month_name(gaian_month)
            gaian_full_date = f"{gaian_month_name} {gaian_day}"

            all_conversions.append({
                'year': year,
                'gregorian': (month, day),
                'gregorian_str': f"{month:02d}-{day:02d}",
                'gaian_month': gaian_month,
                'gaian_day': gaian_day,
                'gaian_month_name': gaian_month_name,
                'gaian_full': gaian_full_date
            })

            gaian_dates.append((gaian_month, gaian_day))
            print(f"{year}  {month:02d}-{day:02d}       {gaian_full_date}")

    print(f"\n=== RANGE ANALYSIS ===")

    # Find extremes
    earliest_greg = min(all_conversions, key=lambda x: (x['gregorian'][0], x['gregorian'][1]))
    latest_greg = max(all_conversions, key=lambda x: (x['gregorian'][0], x['gregorian'][1]))

    earliest_gaian = min(all_conversions, key=lambda x: (x['gaian_month'], x['gaian_day']))
    latest_gaian = max(all_conversions, key=lambda x: (x['gaian_month'], x['gaian_day']))

    print("EARLIEST DIWALI:")
    print(f"  Gregorian: {earliest_greg['gregorian_str']} ({earliest_greg['year']})")
    print(f"  Gaian: {earliest_gaian['gaian_full']} ({earliest_gaian['year']})")

    print("\nLATEST DIWALI:")
    print(f"  Gregorian: {latest_greg['gregorian_str']} ({latest_greg['year']})")
    print(f"  Gaian: {latest_gaian['gaian_full']} ({latest_gaian['year']})")

    # Calculate ranges
    earliest_date = date(2024, earliest_greg['gregorian'][0], earliest_greg['gregorian'][1])
    latest_date = date(2024, latest_greg['gregorian'][0], latest_greg['gregorian'][1])
    gregorian_range = (latest_date - earliest_date).days

    print(f"\nGREGORIAN RANGE: {gregorian_range + 1} days")
    print(f"GAIAN RANGE: {earliest_gaian['gaian_full']} to {latest_gaian['gaian_full']}")

    print(f"\n=== DISTRIBUTION BY GAIAN MONTH ===")

    month_counts = Counter()
    for conv in all_conversions:
        month_counts[conv['gaian_month']] += 1

    total = len(all_conversions)
    for month in sorted(month_counts.keys()):
        count = month_counts[month]
        percentage = (count / total) * 100
        month_name = get_gaian_month_name(month)
        print(f"{month_name:>12}: {count:2d} times ({percentage:5.1f}%)")

    print(f"\n=== DISTRIBUTION BY GAIAN DATE ===")

    date_counts = Counter()
    for conv in all_conversions:
        date_counts[conv['gaian_full']] += 1

    print("Date               Count  Percentage")
    print("-" * 35)
    for gaian_date, count in sorted(date_counts.items(), key=lambda x: date_counts.most_common().index((x[0], x[1]))):
        percentage = (count / total) * 100
        print(f"{gaian_date:<17} {count:2d}     {percentage:5.1f}%")

    print(f"\n=== UNIQUE DATES SUMMARY ===")
    print(f"Total years analyzed: {total}")
    print(f"Unique Gaian dates: {len(date_counts)}")
    print(f"Most frequent: {date_counts.most_common(1)[0][0]} ({date_counts.most_common(1)[0][1]} times)")

    # Show all dates that occurred more than once
    multiple_occurrences = [(date, count) for date, count in date_counts.items() if count > 1]
    if multiple_occurrences:
        print(f"\nDates occurring multiple times:")
        for gaian_date, count in sorted(multiple_occurrences, key=lambda x: x[1], reverse=True):
            print(f"  {gaian_date}: {count} times")

    return all_conversions, earliest_gaian, latest_gaian

if __name__ == "__main__":
    try:
        conversions, earliest, latest = analyze_diwali_distribution()

        print(f"\n" + "="*50)
        print("FINAL ANSWER")
        print("="*50)
        print(f"EARLIEST: {earliest['gaian_full']}")
        print(f"LATEST:   {latest['gaian_full']}")
        print(f"SPAN:     From {earliest['gaian_full']} to {latest['gaian_full']}")
        print("="*50)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()