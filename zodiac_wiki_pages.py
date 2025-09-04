# zodiac_push_all.py
# Hard-coded bot that creates/overwrites ALL 13×28 pages on shinto.miraheze.org

import time
from datetime import date, datetime, timedelta

# if your script makes HTTP calls (it does, for MediaWiki):
import requests

# optional, only if you’re using type hints in the file
from typing import Dict, List, Tuple, Optional




import sys
import argparse

API_URL     = "https://evolutionism.miraheze.org/w/api.php"
USER_AGENT  = "ZodiacWikiBot/0.2 (User:Immanuelle; contact: you@example.com)"
SUMMARY     = "Create/update zodiac date page"
THROTTLE    = 0.6      # seconds between edits (be polite to the wiki)
TITLE_PREFIX = ""      # e.g., "Calendar:" if you want them in a namespace
LONGRUN_START = 2001   # per your spec
LONGRUN_END   = 2399

CHINESE_DIST_START = 1900
CHINESE_DIST_END   = 2100




# ---- Calendar libs ----
import os, sys, importlib

# Hebrew via convertdate (works on your install)
try:
    H = importlib.import_module("convertdate.hebrew")
    HAVE_HEBREW = True
except Exception as e:
    H = None
    HAVE_HEBREW = False
    print("hebrew: disabled ->", e)

# Chinese via lunardate (not part of convertdate)
try:
    LunarDate = importlib.import_module("lunardate").LunarDate
    HAVE_CHINESE = True
except Exception as e:
    LunarDate = None
    HAVE_CHINESE = False
    print("chinese: disabled ->", e)




# --- Your event lists (as you provided) ---
CHINESE_EVENTS = [
    {"name": "Chinese New Year", "type": "lunar", "month": 1, "day": 1},
    {"name": "Chinese New Year's Eve", "type": "relative",
     "anchor": {"type": "lunar", "month": 1, "day": 1}, "offset_days": -1},
    {"name": "Lantern Festival", "type": "lunar", "month": 1, "day": 15},
    {"name": "Qingming", "type": "solar_term", "term": "Qingming"},      # Sun λ=15° (requires astro)
    {"name": "Dragon Boat Festival", "type": "lunar", "month": 5, "day": 5},
    {"name": "Qixi", "type": "lunar", "month": 7, "day": 7},
    {"name": "Ghost Festival", "type": "lunar", "month": 7, "day": 15},
    {"name": "Mid-Autumn Festival", "type": "lunar", "month": 8, "day": 15},
    {"name": "Double Ninth", "type": "lunar", "month": 9, "day": 9},
    {"name": "Dongzhi", "type": "solar_term", "term": "Dongzhi"}          # Solstice (requires astro)
]

HEBREW_EVENTS = [
    {"name": "Rosh Hashanah (Day 1)", "type": "hebrew", "month": "Tishrei", "day": 1},
    {"name": "Rosh Hashanah (Day 2)", "type": "hebrew", "month": "Tishrei", "day": 2},

    {"name": "Yom Kippur", "type": "hebrew", "month": "Tishrei", "day": 10},
    {"name": "Sukkot (First Day)", "type": "hebrew", "month": "Tishrei", "day": 15},
    {"name": "Sukkot (Second Day)", "type": "hebrew", "month": "Tishrei", "day": 16},
    {"name": "Sukkot (Third Day)", "type": "hebrew", "month": "Tishrei", "day": 17},
    {"name": "Sukkot (Fourth Day)", "type": "hebrew", "month": "Tishrei", "day": 18},
    {"name": "Sukkot (Fifth Day)", "type": "hebrew", "month": "Tishrei", "day": 19},
    {"name": "Sukkot (Sixth Day)", "type": "hebrew", "month": "Tishrei", "day": 20},
    {"name": "Sukkot (Seventh Day / Hoshana Rabbah)", "type": "hebrew", "month": "Tishrei", "day": 21},

    {"name": "Shemini Atzeret", "type": "hebrew", "month": "Tishrei", "day": 22},
    {"name": "Simchat Torah (Diaspora)", "type": "hebrew", "month": "Tishrei", "day": 23, "optional": True},
    {"name": "Hanukkah (Day 1)", "type": "hebrew", "month": "Kislev", "day": 25},
    {"name": "Hanukkah (Day 2)", "type": "hebrew", "month": "Kislev", "day": 26},
    {"name": "Hanukkah (Day 3)", "type": "hebrew", "month": "Kislev", "day": 27},
    {"name": "Hanukkah (Day 4)", "type": "hebrew", "month": "Kislev", "day": 28},
    {"name": "Hanukkah (Day 5)", "type": "hebrew", "month": "Kislev", "day": 29},
    {"name": "Hanukkah (sometimes Day 6)", "type": "hebrew", "month": "Kislev", "day": 30},
    {"name": "Hanukkah (Day 6 or 7)", "type": "hebrew", "month": "Tevet", "day": 1},
    {"name": "Hanukkah (Day 7 or 8)", "type": "hebrew", "month": "Tevet", "day": 2},
    {"name": "Hanukkah (sometimes Day 8)", "type": "hebrew", "month": "Tevet", "day": 3},

    {"name": "Tu BiShvat", "type": "hebrew", "month": "Shevat", "day": 15},
    {"name": "Purim", "type": "hebrew", "month": "Adar", "day": 14, "rule": "AdarII_in_leap_year"},
    {"name": "Pesach (First Day)", "type": "hebrew", "month": "Nisan", "day": 15},
    {"name": "Pesach (2nd Day)", "type": "hebrew", "month": "Nisan", "day": 16},
    {"name": "Pesach (3rd Day)", "type": "hebrew", "month": "Nisan", "day": 17},
    {"name": "Pesach (4th Day)", "type": "hebrew", "month": "Nisan", "day": 18},
    {"name": "Pesach (5th Day)", "type": "hebrew", "month": "Nisan", "day": 19},
    {"name": "Pesach (6th Day)", "type": "hebrew", "month": "Nisan", "day": 20},
    {"name": "Pesach (7th Day)", "type": "hebrew", "month": "Nisan", "day": 21},
    {"name": "Pesach (8th Day)", "type": "hebrew", "month": "Nisan", "day": 22},
    {"name": "Lag BaOmer", "type": "hebrew", "month": "Iyar", "day": 18},
    {"name": "Shavuot", "type": "hebrew", "month": "Sivan", "day": 6},
    {"name": "Tisha B'Av", "type": "hebrew", "month": "Av", "day": 9, "rule": "postpone_if_shabbat"}
]

# Hebrew month indices expected by convertdate (ECCLESIASTICAL numbering: Nisan=1… Adar=12/13)
HEBREW_MONTH_INDEX = {
    "nisan": 1, "iyyar": 2, "iyar": 2, "sivan": 3, "tammuz": 4, "av": 5, "elul": 6,
    "tishrei": 7, "tishri": 7, "cheshvan": 8, "marcheshvan": 8, "marheshvan": 8,
    "kislev": 9, "tevet": 10, "shevat": 11, "shvat": 11,
    # Adar handling depends on leap year; see helper below
}

# After: from lunardate import LunarDate  (and HAVE_CHINESE = True)
if HAVE_CHINESE:
    class _CShim:
        @staticmethod
        def from_gregorian(y, m, d):
            ld = LunarDate.fromSolarDate(y, m, d)
            leap = getattr(ld, "isLeapMonth", getattr(ld, "leap", False))
            # convertdate.chinese.from_gregorian returns (cycle, year, month, leap, day)
            return (None, ld.year, ld.month, bool(leap), ld.day)

        @staticmethod
        def to_gregorian(cycle, year, month, leap, day):
            g = LunarDate(year, month, day, leap).toSolarDate()
            # convertdate.chinese.to_gregorian returns (Y, M, D)
            return (g.year, g.month, g.day)

    C = _CShim


def _cn_from_greg(g: date):
    """Return (lyear, lmonth, lday, leap_flag) using lunardate."""
    ld = LunarDate.fromSolarDate(g.year, g.month, g.day)
    # some versions use .isLeapMonth, some .leap
    leap = getattr(ld, "isLeapMonth", getattr(ld, "leap", False))
    return ld.year, ld.month, ld.day, bool(leap)

def _cn_to_greg(lyear: int, lmonth: int, lday: int, is_leap: bool = False) -> date:
    return LunarDate(lyear, lmonth, lday, is_leap).toSolarDate()

def chinese_event_matches_gregorian(g: date, ev: dict):
    """True/False/None; None for unsupported (e.g., solar terms)."""
    t = ev["type"]
    if t == "lunar":
        lyear, lmonth, lday, leap = _cn_from_greg(g)
        want_m, want_d = ev["month"], ev["day"]
        if ev.get("leap") is not None:
            return (lmonth == want_m) and (lday == want_d) and (leap == bool(ev["leap"]))
        # default: only match non-leap months (public festivals are non-leap)
        return (lmonth == want_m) and (lday == want_d) and (not leap)

    if t == "relative":
        anch = ev["anchor"]
        if anch.get("type") != "lunar":
            return None
        lyear, _, _, _ = _cn_from_greg(g)              # same Chinese year as g
        anchor_g = _cn_to_greg(lyear, anch["month"], anch["day"], bool(anch.get("leap", False)))
        target_g = anchor_g + timedelta(days=int(ev.get("offset_days", 0)))
        return g == target_g

    if t == "solar_term":
        # Not implemented here (needs astronomical solar longitude).
        return None

    return None


def hebrew_month_number(name: str, hy: int, rule: str | None) -> int:
    """Return convertdate's month number for this Hebrew year hy."""
    n = name.strip().lower()
    if n.startswith("adar"):  # Adar / Adar I / Adar II
        if rule == "AdarII_in_leap_year" and H.leap(hy):
            return 13  # Adar II
        # Non-leap: Adar = 12; Leap: 'Adar' often means Adar II, but rule above catches Purim
        return 12
    return HEBREW_MONTH_INDEX[n]


# ---------- CHINESE MATCHERS ----------
def chinese_lunar_tuple(g: date):
    # (cycle, year, month, is_leap, day)
    return C.from_gregorian(g.year, g.month, g.day)

def chinese_new_year_gregorian_for_cy(cyc: int, y: int) -> date:
    # m=1, leap=False, d=1
    y1, m1, d1 = C.to_gregorian(cyc, y, 1, False, 1)
    return date(y1, m1, d1)

def chinese_event_matches_gregorian(g: date, ev: dict) -> bool | None:
    """Return True if matches, False if not, None if event type not supported."""
    if ev["type"] == "lunar":
        cyc, yy, m, leap, d = chinese_lunar_tuple(g)
        want_m = ev["month"]; want_d = ev["day"]
        # Most public festivals are in non-leap months; don't match leap months unless specified.
        if ev.get("leap") is not None:
            return (m == want_m) and (d == want_d) and (leap is bool(ev["leap"]))
        else:
            return (m == want_m) and (d == want_d) and (not leap)
    elif ev["type"] == "relative":
        # Only anchor supported here: another lunar date in the SAME Chinese year
        cyc, yy, _, _, _ = chinese_lunar_tuple(g)
        anch = ev["anchor"]
        if anch["type"] != "lunar":
            return None
        ay, am, ad = C.to_gregorian(cyc, yy, anch["month"], bool(anch.get("leap", False)), anch["day"])
        anchor_g = date(ay, am, ad)
        target = anchor_g + timedelta(days=int(ev.get("offset_days", 0)))
        return g == target
    elif ev["type"] == "solar_term":
        # Requires astro calc (sun ecliptic longitude). Left unimplemented to avoid heavy deps.
        return None
    return None


# ---- Hebrew month labels with leap handling ----
HEB_NAMES = {
    1:"Nisan", 2:"Iyar", 3:"Sivan", 4:"Tammuz", 5:"Av", 6:"Elul",
    7:"Tishrei", 8:"Cheshvan", 9:"Kislev", 10:"Tevet", 11:"Shevat",
    # 12/13 depend on leap year
}

def hebrew_label_and_index(hy: int, hm: int) -> tuple[str, int]:
    """
    Return (display_label, sort_index) for the given Hebrew year+month.
    In leap years: 12=Adar I, 13=Adar II; otherwise 12=Adar.
    sort_index is ecclesiastical order: Nisan=1 ... Adar I/Adar=12 ... Adar II=13
    """
    if hm == 12:
        if H.leap(hy):
            return "Adar I", 12
        else:
            return "Adar", 12
    if hm == 13:
        return "Adar II", 13
    return HEB_NAMES[hm], hm

def hebrew_distribution_block(m_idx: int, d_m: int,
                              start_iso_year: int = LONGRUN_START,
                              end_iso_year: int   = LONGRUN_END) -> str:
    if not HAVE_HEBREW:
        return "<!-- Hebrew distribution skipped: convertdate.hebrew not available -->"

    from collections import Counter
    counts: Counter[tuple[int, str, int]] = Counter()  # (sort_idx, label, day)

    for y in range(start_iso_year, end_iso_year + 1):
        try:
            gdate = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            # Year doesn't have week 53, skip intercalary days
            continue
        try:
            hy, hm, hd = H.from_gregorian(gdate.year, gdate.month, gdate.day)
        except Exception:
            continue

        # label + stable sort index (Nisan=1 … Adar/Adar I=12 … Adar II=13)
        if hm == 12:
            label, idx = ("Adar I", 12) if H.leap(hy) else ("Adar", 12)
        elif hm == 13:
            label, idx = ("Adar II", 13)
        else:
            label, idx = (HEB_NAMES[hm], hm)

        if 1 <= hd <= 30:
            counts[(idx, label, hd)] += 1

    total = sum(counts.values()) or 1  # denom = actually counted years

    lines = [
        '{| class="wikitable sortable"',
        f'! Hebrew month-day !! Count !! Probability'
    ]
    for (idx, label, hday) in sorted(counts.keys()):
        c = counts[(idx, label, hday)]
        lines.append(f"|-\n| {label} {hday} || {c} || {c/total:.2%}")
    lines.append("|}")
    lines.append(f"<small>Years tested: {total}</small>")
    return "\n".join(lines)



def chinese_distribution_block(m_idx: int, d_m: int,
                               start_year: int = CHINESE_DIST_START,
                               end_year: int   = CHINESE_DIST_END) -> str:
    """
    Returns a wikitable showing how often this zodiac day maps to each Chinese lunar (month, day),
    over a *fixed* range (default 1900–2100). We do not “probe” outside that range.
    Denominator = number of ISO years in that range where this zodiac day actually exists.
    """
    if not HAVE_CHINESE:
        return "<!-- Chinese calendar section skipped: lunardate not available -->"

    # Clamp to supported window explicitly; no out-of-range probing.
    sy = max(start_year, CHINESE_DIST_START)
    ey = min(end_year, CHINESE_DIST_END)

    from collections import Counter
    counts = Counter()
    years_considered = 0

    for y in range(sy, ey + 1):
        # Compute the Gregorian date for this zodiac day in ISO year y.
        try:
            g = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            # e.g., Horus day in a year without ISO week 53 -> this zodiac day does not occur in ISO year y.
            continue

        # Convert to Chinese lunar using lunardate
        l = LunarDate.fromSolarDate(g.year, g.month, g.day)
        # Different lunardate versions expose the leap flag slightly differently; cover both.
        leap = bool(getattr(l, "leap", getattr(l, "isLeapMonth", False)))
        counts[(leap, l.month, l.day)] += 1
        years_considered += 1

    if years_considered == 0:
        return f"== Chinese lunar date distribution ({sy}–{ey}) ==\n" \
               f"<!-- No occurrence of this zodiac day in the chosen range. -->"

    def label(leap_m_d: tuple[bool, int, int]) -> str:
        leap, m, d = leap_m_d
        return f"{'Leap ' if leap else ''}Month {m} {d}"

    lines = [f"== Chinese lunar date distribution ({sy}–{ey}) ==",
             '{| class="wikitable sortable"',
             '! Chinese lunar month-day !! Count !! Probability']
    for key in sorted(counts.keys(), key=lambda t: (t[0], t[1], t[2])):
        c = counts[key]
        lines.append(f"|-\n| {label(key)} || {c} || {c/years_considered:.2%}")
    lines.append("|}")
    lines.append(f"<small>Years considered: {years_considered} (out of {ey - sy + 1} in range; "
                 f"years where this zodiac day does not occur are excluded).</small>")
    return "\n".join(lines)




# --- helper: append a category tag inline with the label when there’s a hit ---
def label_with_category(name: str, hit_count: int) -> str:
    return f"{name} [[Category:Days that {name} falls on]]" if hit_count > 0 else name

def chinese_overlap_table(m_idx: int, d_m: int,
                          start_iso_year: int = LONGRUN_START, end_iso_year: int = LONGRUN_END) -> str:
    if not HAVE_CHINESE:
        return "<!-- Chinese calendar section skipped: lunardate not available -->"

    total = end_iso_year - start_iso_year + 1
    rows = []
    for ev in CHINESE_EVENTS:
        matches = 0
        supported = True
        for y in range(start_iso_year, end_iso_year + 1):
            try:
                g = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
            except ValueError:
                continue  # Year doesn't have week 53, skip intercalary days
            res = chinese_event_matches_gregorian(g, ev)
            if res is None:
                supported = False
                break
            if res:
                matches += 1
        prob = (matches / total) if supported else 0.0
        name = ev["name"] + ("" if supported else " (requires solar-term calc)")
        name_cell = label_with_category(name, matches) if supported else name
        rows.append((name_cell, matches if supported else 0, total if supported else total, prob))

    lines = ['{| class="wikitable sortable"', '! Event !! Matches !! Years !! Probability']
    for name_cell, c, t, p in rows:
        lines.append(f"|-\n| {name_cell} || {c} || {t} || {p:.2%}")
    lines.append("|}")
    return "\n".join(lines)



# ---------- HEBREW MATCHERS ----------

def hebrew_event_matches_gregorian(g: date, ev: dict) -> bool:
    hy, hm, hd = H.from_gregorian(g.year, g.month, g.day)
    # compute the *observed* Gregorian date of the event in this Hebrew year
    tgt_month = hebrew_month_number(ev["month"], hy, ev.get("rule"))
    # base day (e.g., 9 Av)
    ty, tm, td = H.to_gregorian(hy, tgt_month, ev["day"])
    observed = date(ty, tm, td)
    # special rule: postpone Tisha B'Av if Shabbat
    if ev.get("rule") == "postpone_if_shabbat":
        if observed.weekday() == 5:  # Sat=5 in Python (Mon=0)
            observed = observed + timedelta(days=1)
    return g == observed

def hebrew_overlap_table(m_idx: int, d_m: int,
                         start_iso_year: int = LONGRUN_START, end_iso_year: int = LONGRUN_END) -> str:
    if not HAVE_HEBREW:
        return ("''Hebrew calendar section requires `convertdate`. "
                "Install with `pip install convertdate`.''")

    total = end_iso_year - start_iso_year + 1
    rows = []
    for ev in HEBREW_EVENTS:
        matches = 0
        for y in range(start_iso_year, end_iso_year + 1):
            try:
                g = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
            except ValueError:
                continue  # Year doesn't have week 53, skip intercalary days
            if hebrew_event_matches_gregorian(g, ev):     # your existing matcher
                matches += 1
        name_cell = label_with_category(ev["name"], matches)
        rows.append((name_cell, matches, total, matches/total))

    lines = ['{| class="wikitable sortable"', '! Event !! Matches !! Years !! Probability']
    for name_cell, c, t, p in rows:
        lines.append(f"|-\n| {name_cell} || {c} || {t} || {p:.2%}")
    lines.append("|}")
    return "\n".join(lines)




# ------------- Page generator (minimal but complete) -------------

MONTHS = [
    "Sagittarius","Capricorn","Aquarius","Pisces","Aries","Taurus",
    "Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Ophiuchus","Horus"
]
MONTH_NAMES = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
WD_ABBR = {1:"Mon",2:"Tue",3:"Wed",4:"Thu",5:"Fri",6:"Sat",7:"Sun"}

def zodiac_to_iso(m_idx: int, d_m: int):
    # Handle regular months (1-13)
    if 1 <= m_idx <= 13 and 1 <= d_m <= 28:
        iso_week  = (m_idx - 1) * 4 + ((d_m - 1) // 7) + 1      # 1..52
        iso_wday  = ((d_m - 1) % 7) + 1                         # 1..7 (Mon..Sun)
        return iso_week, iso_wday
    # Handle Horus intercalary days (month 14, days 1-7)
    elif m_idx == 14 and 1 <= d_m <= 7:
        iso_week = 53  # Symbolic week for intercalary days
        iso_wday = d_m  # Day 1-7 maps to Mon-Sun
        return iso_week, iso_wday
    else:
        raise ValueError("month_index 1..14 (1-13 regular, 14=Horus), day_of_month 1..28 (1-7 for Horus)")

def ordinal_in_year(m_idx: int, d_m: int) -> int:
    if m_idx == 14:  # Horus intercalary days
        return 364 + d_m  # Days 365-371
    w, wd = zodiac_to_iso(m_idx, d_m)
    return (w - 1) * 7 + wd  # 1..364

def zodiac_gregorian_for_iso_year(m_idx: int, d_m: int, iso_year: int) -> date:
    w, wd = zodiac_to_iso(m_idx, d_m)
    
    # For intercalary days (Horus), only return date for 53-week years
    if m_idx == 14:  # Horus intercalary days
        try:
            return date.fromisocalendar(iso_year, w, wd)
        except ValueError:
            # This year doesn't have week 53, so no intercalary days
            raise ValueError(f"Year {iso_year} has no week 53 (no intercalary days)")
    
    return date.fromisocalendar(iso_year, w, wd)

def gregorian_to_gaian_date(gregorian_date: date) -> tuple[int, int, str]:
    """
    Convert a Gregorian date to Gaian calendar format.
    Returns (month_idx, day_of_month, month_name)
    """
    iso_year, iso_week, iso_weekday = gregorian_date.isocalendar()
    
    # Handle intercalary week (week 53)
    if iso_week == 53:
        return (14, iso_weekday, "Horus")
    
    # Calculate Gaian month and day for regular weeks (1-52)
    month_idx = ((iso_week - 1) // 4) + 1  # Weeks 1-4=month 1, 5-8=month 2, etc.
    week_in_month = ((iso_week - 1) % 4) + 1  # Which week within the month (1-4)
    day_of_month = ((week_in_month - 1) * 7) + iso_weekday  # Day within the month (1-28)
    
    return (month_idx, day_of_month, MONTHS[month_idx-1])

def reading_for_ordinal(ord1: int) -> str:
    return f"Chapter {ord1} of the Gaiad"

def nth_weekday_of_month(year: int, month: int, weekday_mon0: int, n: int) -> date:
    """weekday_mon0: 0=Mon .. 6=Sun; n>=1"""
    d = date(year, month, 1)
    delta = (weekday_mon0 - d.weekday()) % 7
    first = d + timedelta(days=delta)
    return first + timedelta(weeks=n-1)

def last_weekday_of_month(year: int, month: int, weekday_mon0: int) -> date:
    """weekday_mon0: 0=Mon .. 6=Sun"""
    if month == 12:
        d = date(year, 12, 31)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)
    delta = (d.weekday() - weekday_mon0) % 7
    return d - timedelta(days=delta)

def nth_weekday_holidays_for_year(year: int):
    """
    Returns {label: gregorian_date} for Nth-weekday style holidays.
    Labels are explicit about country; US/CA Thanksgiving are separate.
    """
    rules = {}

    # --- United States (federal) ---
    rules["US Martin Luther King Jr. Day (3rd Mon Jan)"] = nth_weekday_of_month(year, 1, 0, 3)
    rules["US Presidents Day (Washington’s Birthday, 3rd Mon Feb)"] = nth_weekday_of_month(year, 2, 0, 3)
    rules["US Memorial Day (last Mon May)"] = last_weekday_of_month(year, 5, 0)
    rules["US Labor Day (1st Mon Sep)"] = nth_weekday_of_month(year, 9, 0, 1)
    rules["US Columbus Day / Indigenous Peoples’ Day (2nd Mon Oct)"] = nth_weekday_of_month(year, 10, 0, 2)
    us_thanks = nth_weekday_of_month(year, 11, 3, 4)  # Thu=3
    rules["US Thanksgiving (4th Thu Nov)"] = us_thanks
    us_elect = nth_weekday_of_month(year, 11, 1, 1)  # Thu=3
    rules["US Election Monday (1st Monday of November)"] = us_elect
    rules["US Election Day (The Tuesday after the first Monday of November)"] = us_elect + timedelta(days=1)

    # Black Friday = day after US Thanksgiving
    rules["US Black Friday (Fri after US Thanksgiving)"] = us_thanks + timedelta(days=1)

    # --- United States (common observances) ---
    rules["US Mother’s Day (2nd Sun May)"] = nth_weekday_of_month(year, 5, 6, 2)  # Sun=6
    rules["US Father’s Day (3rd Sun Jun)"] = nth_weekday_of_month(year, 6, 6, 3)

    # --- Canada (national/federal) ---
    rules["Canada Labour Day (1st Mon Sep)"] = nth_weekday_of_month(year, 9, 0, 1)
    rules["Canada Thanksgiving (2nd Mon Oct)"] = nth_weekday_of_month(year, 10, 0, 2)

    # --- Canada (provincial examples) ---
    rules["Canada Family Day (most prov., 3rd Mon Feb)"] = nth_weekday_of_month(year, 2, 0, 3)
    rules["Canada Civic Holiday (1st Mon Aug)"] = nth_weekday_of_month(year, 8, 0, 1)
    rules["Yukon Discovery Day (3rd Mon Aug)"] = nth_weekday_of_month(year, 8, 0, 3)

    # --- Japan (national holidays via Happy Monday rules) ---
    rules["Japan Coming of Age Day (2nd Mon Jan)"] = nth_weekday_of_month(year, 1, 0, 2)
    rules["Japan Marine Day (3rd Mon Jul)"] = nth_weekday_of_month(year, 7, 0, 3)
    rules["Japan Respect for the Aged Day (3rd Mon Sep)"] = nth_weekday_of_month(year, 9, 0, 3)
    rules["Japan Sports Day (2nd Mon Oct)"] = nth_weekday_of_month(year, 10, 0, 2)

        # CANADA – fixed-date general election day (subject to early dissolution)
    # Canada Elections Act: third Monday in October. :contentReference[oaicite:0]{index=0}
    rules["Canada Federal Election Day (fixed-date, 3rd Mon Oct)"] = nth_weekday_of_month(year, 10, 0, 3)

    # MEXICO – federal elections are held the FIRST SUNDAY IN JUNE
    # (Presidential every 6 years; deputies every 3. We encode the weekday rule here.) :contentReference[oaicite:1]{index=1}
    rules["Mexico Federal Election Day (1st Sun Jun)"] = nth_weekday_of_month(year, 6, 6, 1)

    # BRAZIL – 1st round: FIRST SUNDAY IN OCTOBER; 2nd round (if needed): LAST SUNDAY IN OCTOBER
    # (Applies to presidential/gubernatorial when needed). :contentReference[oaicite:2]{index=2}
    rules["Brazil General Elections – 1st round (1st Sun Oct)"] = nth_weekday_of_month(year, 10, 6, 1)
    rules["Brazil General Elections – 2nd round (last Sun Oct, if needed)"] = last_weekday_of_month(year, 10, 6)

    # ARGENTINA – general elections: FOURTH SUNDAY IN OCTOBER (runoff typically in November)
    # Encodes the weekday rule used in recent cycles. :contentReference[oaicite:3]{index=3}
    rules["Argentina General Election (4th Sun Oct)"] = nth_weekday_of_month(year, 10, 6, 4)

    # SWEDEN – general election: SECOND SUNDAY IN SEPTEMBER, every 4 years
    # We add the date only in election years (years % 4 == 2: e.g., 2018, 2022, 2026). :contentReference[oaicite:4]{index=4}
    if year % 4 == 2:
        rules["Sweden General Election (2nd Sun Sep)"] = nth_weekday_of_month(year, 9, 6, 2)

    # NORWAY – parliamentary election: MONDAY IN SEPTEMBER, every 4 years
    # Official practice is a Monday in September; next is 8 Sep 2025. Use 2nd Monday as the standard rule. :contentReference[oaicite:5]{index=5}
    if year % 4 == 1:  # 2025, 2029, ...
        rules["Norway Parliamentary Election (2nd Mon Sep)"] = nth_weekday_of_month(year, 9, 0, 2)

    # RUSSIA – presidential election: SECOND SUNDAY IN MARCH, every 6 years (unless shifted);
    # Duma elections: often THIRD SUNDAY IN SEPTEMBER (5-year cycle; may be moved or multi-day).
    # Encode the base weekday rules. :contentReference[oaicite:6]{index=6}
    if (year - 2018) % 6 == 0:
        rules["Russia Presidential Election (2nd Sun Mar)"] = nth_weekday_of_month(year, 3, 6, 2)
    if (year - 2021) % 5 == 0:
        rules["Russia State Duma Election (3rd Sun Sep)"] = nth_weekday_of_month(year, 9, 6, 3)

    # NETHERLANDS – municipal/provincial elections are on a WEDNESDAY in March; 
    # municipalities are the THIRD WEDNESDAY in March (every 4 years). (General elections are usually Wed but not formula-fixed.)
    # If you want municipal elections:
    # rules["Netherlands Municipal Elections (3rd Wed Mar)"] = nth_weekday_of_month(year, 3, 2, 3)


    return rules

def easter_sunday_gregorian(year: int) -> date:
    a = year % 19; b = year // 100; c = year % 100
    d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i = c // 4; k = c % 4
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day = ((h + l - 7*m + 114) % 31) + 1
    return date(year, month, day)

EASTER_OFFSET_LABELS = {
    -63: "Septuagesima Sunday",
    -56: "Sexagesima Sunday",
    -49: "Quinquagesima Sunday",
    -47: "Mardi Gras/Carnival",
    -46: "Ash Wednesday",
    -35: "2nd Sunday in Lent",
    -28: "3rd Sunday in Lent",
    -21: "Laetare Sunday",
    -14: "Passion Sunday (Fifth Sunday of Lent)",
    -7 : "Palm Sunday",
    -6: "Holy Monday",
    -5: "Holy Tuesday",
    -4: "Spy Wednesday",
    -3 : "Maundy Thursday",
    -2 : "Good Friday",
    -1 : "Holy Saturday",
     0 : "Easter Sunday",
    +1:  "Easter Monday",
    +2:  "Easter Tuesday",
    +3:  "Easter Wednesday",
    +4:  "Easter Thursday",
    +5:  "Easter Friday",
    +6:  "Easter Saturday",
    +7:  "Second Sunday of Easter (Divine Mercy Sunday)",
    +14: "Third Sunday of Easter",
    +21: "Fourth Sunday of Easter",
    +28: "Fifth Sunday of Easter",
    +35: "Sixth Sunday of Easter",
    +39: "Ascension Thursday",
    +42: "Seventh Sunday of Easter",
    +49: "Pentecost Sunday",
    +56: "Trinity Sunday",
    +60: "Corpus Christi (Latin/Thu)",
}

def recent_block(m_idx: int, d_m: int, span: int = 5) -> str:
    # For intercalary days (Horus), use a larger span since they're rarer
    if m_idx == 14:
        span = 25  # Use ±25 years for intercalary days
    
    iso_year = datetime.now().date().isocalendar()[0]
    y0, y1 = iso_year - span, iso_year + span
    w, wd = zodiac_to_iso(m_idx, d_m)
    lines = ['{| class="wikitable"', '! ISO year !! Gregorian date (weekday) !! ISO triple']
    for y in range(y0, y1+1):
        try:
            g = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            continue  # Year doesn't have week 53, skip intercalary days
        lines.append(f"|-\n| {y} || {g.isoformat()} ({WD_ABBR[g.isoweekday()]}) || {y}-W{w}-{wd}")
    lines.append("|}")
    return "\n".join(lines)

def gregorian_distribution_block(m_idx: int, d_m: int,
                                 start_iso_year: int = LONGRUN_START,
                                 end_iso_year: int   = LONGRUN_END) -> str:
    from collections import Counter
    counts = Counter()
    years_counted = 0

    for y in range(start_iso_year, end_iso_year + 1):
        try:
            g = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            # e.g., Horus day in a year without ISO week 53
            continue
        counts[(g.month, g.day)] += 1
        years_counted += 1

    total = sum(counts.values()) or 1  # denom = only years where this zodiac day exists

    lines = ['{| class="wikitable sortable"', '! Month-day !! Count !! Probability !! Fixed-date holidays']
    for (m, d) in sorted(counts.keys()):
        c = counts[(m, d)]
        fixed_col = "—"  # <--- If you have your own fixed-holiday label logic, use it here.
        lines.append(f"|-\n| {MONTH_NAMES[m-1]} {d} || {c} || {c/total:.2%} || {fixed_col}")
    lines.append("|}")
    lines.append(f"<small>Years counted in range {start_iso_year}–{end_iso_year}: {years_counted}</small>")
    return "\n".join(lines)



def nth_weekday_overlap_block(m_idx: int, d_m: int,
                              start_iso_year: int = LONGRUN_START,
                              end_iso_year: int   = LONGRUN_END) -> str:
    # Build map only for years where this zodiac day exists
    zd = {}
    for y in range(start_iso_year, end_iso_year + 1):
        try:
            zd[y] = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            continue  # skip non-occurrence years (e.g., no ISO week 53)

    denom_years = len(zd) or 1

    rules: set[str] = set()
    hits: dict[str, int] = {}

    for y in range(start_iso_year, end_iso_year + 1):
        if y not in zd:
            continue
        hol = nth_weekday_holidays_for_year(y)
        rules |= set(hol.keys())
        zy = zd[y]
        for name, d in hol.items():
            if d == zy:
                hits[name] = hits.get(name, 0) + 1

    lines = ['{| class="wikitable sortable"', '! Holiday (rule) !! Matches !! Years considered !! Probability']
    for name in sorted(rules):
        c = hits.get(name, 0)
        lines.append(f"|-\n| {name} || {c} || {denom_years} || {c/denom_years:.2%}")
    lines.append("|}")
    lines.append(f"<small>Years considered are only those where this zodiac day exists: "
                 f"{denom_years} of {end_iso_year - start_iso_year + 1}.</small>")
    return "\n".join(lines)




def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20: suf = "th"
    else: suf = {1:"st", 2:"nd", 3:"rd"}.get(n % 10, "th")
    return f"{n}{suf}"

def weekday_name_from_iso(wd: int) -> str:
    # ISO weekday: 1=Mon … 7=Sun
    return ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][wd-1]

def build_description_block(m_idx: int, d_m: int, qid_mapping: dict = None) -> str:
    """Returns the short description block you want, with categories + DEFAULTSORT."""
    month_name = MONTHS[m_idx-1]
    iso_week, iso_wd = zodiac_to_iso(m_idx, d_m)          # 1..52, 1..7 (53 for intercalary)
    ord_year = ordinal_in_year(m_idx, d_m)                # 1..364 (365-371 for intercalary)
    weekday_name = weekday_name_from_iso(iso_wd)

    lines = []

    # ALWAYS include the month template first — no f-strings, no format()
    # If your 14th month is named "Horus" in templates but "Cetus" in MONTHS, map it here.
    TEMPLATE_NAME_MAP = {
        # "Cetus": "Horus",   # uncomment if MONTHS uses "Cetus" but your template is {{Horus}}
        # otherwise leave this dict empty
    }
    tpl = TEMPLATE_NAME_MAP.get(month_name, month_name)
    lines.append("{{" + tpl + "}}")

    if m_idx == 14:  # intercalary block (rename in text if you use Cetus/Horus differently)
        jp_informal = f"14宮{d_m}日"
        lines.append(
            f"{month_name} {d_m} is the {ordinal(ord_year)} day of the year in the [[Gaian calendar]]. "
            f"It is an intercalary day, the {ordinal(d_m)} of the 7 days of {month_name}. "
            f"It falls on a {weekday_name} in intercalary week {iso_week}."
        )
    else:
        jp_informal = f"{m_idx}宮{d_m}日"
        lines.append(
            f"{month_name} {d_m} is the {ordinal(ord_year)} day of the year in the [[Gaian calendar]]. "
            f"It is the {ordinal(d_m)} day of {month_name}, and it is a {weekday_name}. "
            f"It corresponds to ISO week {iso_week}, weekday {iso_wd}."
        )

    lines.append("")
    lines.append(f"Its informal Japanese name is {jp_informal}.")
    lines.append("")
    lines.append(f"On this day, [[Gaiad chapter {ord_year}|Chapter {ord_year}]] of the [[Gaiad]] is read.")
    
    # Add QID link if available
    page_title = f"{month_name} {d_m}"
    if qid_mapping and page_title in qid_mapping:
        qid = qid_mapping[page_title]
        lines.append("")
        lines.append(f"To see structured data on this date see {{{{q|{qid}}}}}.")
    
    lines.append("")
    lines.append(f"[[Category:Days with weekday {weekday_name}]]")
    lines.append(f"[[Category:Days {d_m} of the Gaian calendar]]")
    lines.append(f"[[Category:Days of {month_name}]]")
    
    # Fixed DEFAULTSORT with zero-padding
    jp_formatted = f"{m_idx:02d}宮{d_m:02d}日"
    lines.append(f"{{{{DEFAULTSORT:{jp_formatted}}}}}")

    return "\n".join(lines)



def easter_offsets_block(m_idx: int, d_m: int,
                         start_iso_year: int = LONGRUN_START, end_iso_year: int = LONGRUN_END) -> str:
    # Intercalary days (Horus) will only appear in 53-week years within the date range
    
    counts = {}; total = end_iso_year - start_iso_year + 1
    for y in range(start_iso_year, end_iso_year+1):
        try:
            z = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            continue  # Year doesn't have week 53, skip intercalary days
        e = easter_sunday_gregorian(y)
        off = (z - e).days
        counts[off] = counts.get(off, 0) + 1
    lines = ['{| class="wikitable sortable"', '! Offset (days vs Easter) !! Label !! Count !! Probability']
    for off in sorted(counts.keys()):
        label = EASTER_OFFSET_LABELS.get(off, "")
        c = counts[off]
        lines.append(f"|-\n| {off:+d} || {label} || {c} || {c/total:.2%}")
    lines.append("|}")
    return "\n".join(lines)

# ---- FIXED-DATE EVENTS YOU CARE ABOUT ----
# name -> (month, day)
FIXED_DATE_EVENTS = {
    # Shinto / Japan (fixed)
    "Kinen-sai": (2, 17),
    "Nagoshi no Ōharai": (6, 30),                     # 大祓（夏越の祓）
    "Niiname-sai (新嘗祭)": (11, 23),
    "Kōrei-sai (皇霊祭)": (3, 21),
    "Shindensai (神殿祭)": (9, 21),
    # Golden Week (7-day run you specified)
    "Shōwa Day (Golden Week 1)": (4, 29),
    "Golden Week 2": (4, 30),
    "Golden Week 3 (May Day)": (5, 1),
    "Golden Week 4": (5, 2),
    "Constitution Memorial Day (Golden Week 5)": (5, 3),
    "Greenery Day (Golden Week 6)": (5, 4),
    "Children’s Day (Golden Week 7)": (5, 5),
    # Other JP fixed
    "Tanabata": (7, 7),
    "Shichi-Go-San": (11, 15),
    "Hinamatsuri": (3, 3),

    # North America (fixed)
    "Ides of March": (3, 15),
    "Bastille Day": (7, 14),
    "Guy Fawkes Night": (11, 5),
    "New Year’s Eve": (12, 31),
    "Valentine’s Day": (2, 14),
    "Groundhog Day": (2, 2),
    "St. Patrick’s Day": (3, 17),
    "Halloween": (10, 31),
    "Cinco de Mayo": (5, 5),
    "Remembrance Day": (11, 11),
    "Christmas Day": (12, 25),
    "Boxing Day": (12, 26),
    "Yuri's Night": (4, 12),
    #Wiccan

    "Yule (Winter Solstice)": (12, 21),
    "Imbolc": (2, 1),
    "Ostara (Spring Equinox)": (3, 20),
    "Beltane": (5, 1),
    "Litha (Summer Solstice)": (6, 21),
    "Lughnasadh / Lammas": (8, 1),
    "Mabon (Autumn Equinox)": (9, 22),
    "Samhain": (10, 31),

    #Chinese

    "Qingming Festival": (4, 5),   # Tomb-Sweeping Day
    "Dongzhi Festival": (12, 22)  # Winter Solstice

}

def zodiac_possible_monthdays(m_idx: int, d_m: int,
                              start_iso_year: int = LONGRUN_START,
                              end_iso_year: int   = LONGRUN_END):
    """All Gregorian (month,day) this zodiac date can land on across the window."""
    # Intercalary days (Horus) will only appear in 53-week years within the date range
    
    s = set()
    for y in range(start_iso_year, end_iso_year+1):
        try:
            g = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            continue  # Year doesn't have week 53, skip intercalary days
        s.add((g.month, g.day))
    return s

def categories_for_fixed_dates(m_idx: int, d_m: int) -> list[str]:
    poss = zodiac_possible_monthdays(m_idx, d_m)
    cats = []
    for name, (m, d) in FIXED_DATE_EVENTS.items():
        if (m, d) in poss:
            cats.append(f"[[Category:Days that {name} falls on]]")
    return cats

def categories_for_nth_weekday(m_idx: int, d_m: int,
                               start_iso_year: int = LONGRUN_START,
                               end_iso_year: int   = LONGRUN_END) -> list[str]:
    """Add a category for each weekday-rule holiday that ever coincides."""
    # Intercalary days (Horus) will only appear in 53-week years within the date range
    
    # Your script already defines nth_weekday_holidays_for_year(year)
    hits = set()
    for y in range(start_iso_year, end_iso_year+1):
        try:
            z = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            continue  # Year doesn't have week 53, skip intercalary days
        for label, d in nth_weekday_holidays_for_year(y).items():
            if d == z:
                hits.add(label)
    return [f"[[Category:Days that {label} falls on]]" for label in sorted(hits)]

def categories_for_easter_offsets(m_idx: int, d_m: int,
                                  start_iso_year: int = LONGRUN_START,
                                  end_iso_year: int   = LONGRUN_END) -> list[str]:
    """Add a category for each named feast (in EASTER_OFFSET_LABELS) that ever coincides."""
    # Intercalary days (Horus) will only appear in 53-week years within the date range
    
    cats = []
    # build offset counts once (you already have a function, keeping it inline)
    seen_offsets = set()
    for y in range(start_iso_year, end_iso_year+1):
        try:
            z = zodiac_gregorian_for_iso_year(m_idx, d_m, y)
        except ValueError:
            continue  # Year doesn't have week 53, skip intercalary days
        e = easter_sunday_gregorian(y)
        off = (z - e).days
        seen_offsets.add(off)
    for off in sorted(seen_offsets):
        label = EASTER_OFFSET_LABELS.get(off)
        if label:
            cats.append(f"[[Category:Days that {label} falls on]]")
    return cats


def load_year_qids() -> dict:
    """Load QID mappings from year_qids.txt file."""
    qid_mapping = {}
    try:
        with open('year_qids.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '(' in line and ')' in line:
                    # Parse line like "Sagittarius 1 (Q152000) (← links)"
                    parts = line.split(' (')
                    if len(parts) >= 2:
                        page_name = parts[0].strip()
                        qid_part = parts[1].split(')')[0].strip()
                        if qid_part.startswith('Q') and qid_part[1:].isdigit():
                            qid_mapping[page_name] = qid_part
    except FileNotFoundError:
        print("Warning: year_qids.txt not found, QID links will be skipped")
    except Exception as e:
        print(f"Error loading year_qids.txt: {e}")
    
    return qid_mapping

def extract_overview_section(page_content: str) -> str:
    """Extract the Overview section from existing page content."""
    if not page_content:
        return ""
    
    lines = page_content.split('\n')
    overview_content = []
    in_overview = False
    
    for line in lines:
        if line.strip() == "== Overview ==":
            in_overview = True
            continue
        elif line.startswith("== ") and in_overview:
            # Found another section, stop extracting
            break
        elif in_overview:
            overview_content.append(line)
    
    # Clean up the content - remove leading/trailing empty lines
    while overview_content and not overview_content[0].strip():
        overview_content.pop(0)
    while overview_content and not overview_content[-1].strip():
        overview_content.pop()
    
    return '\n'.join(overview_content)

def build_page(m_idx: int, d_m: int, wiki: 'Wiki' = None) -> (str, str):
    base = f"{MONTHS[m_idx-1]} {d_m}"
    title = f"{TITLE_PREFIX}{base}" if TITLE_PREFIX else base
    w, wd = zodiac_to_iso(m_idx, d_m)
    ord1 = ordinal_in_year(m_idx, d_m)
    reading = reading_for_ordinal(ord1)

    # neighbors - handle intercalary month (Horus) specially
    if m_idx == 14:  # Horus intercalary month
        if d_m > 1:
            pm, pd = (14, d_m-1)
        else:
            pm, pd = (13, 28)  # Last day of Ophiuchus
        
        if d_m < 7:
            nm, nd = (14, d_m+1)
        else:
            nm, nd = (1, 1)  # First day of next year's Sagittarius
    else:
        # Regular month navigation
        pm, pd = (m_idx, d_m-1) if d_m>1 else ((13 if m_idx==1 else m_idx-1), 28)
        if m_idx == 13:  # Ophiuchus
            if d_m < 28:
                nm, nd = (m_idx, d_m+1)
            else:
                # Check if next year has intercalary days (week 53)
                # For simplicity, assume regular transition to next year
                nm, nd = (1, 1)
        else:
            nm, nd = (m_idx, d_m+1) if d_m<28 else ((m_idx+1 if m_idx<13 else 1), 1)
    prev_title = f"{MONTHS[pm-1]} {pd}"
    next_title = f"{MONTHS[nm-1]} {nd}"

    # Get existing page content to preserve Overview section
    overview_content = ""
    if wiki:
        existing_content = wiki.get_page_content(title)
        overview_content = extract_overview_section(existing_content)

    # Load QID mappings for structured data links
    qid_mapping = load_year_qids()

    parts = []
    parts.append(build_description_block(m_idx, d_m, qid_mapping))
    
    # Add Overview section
    if overview_content:
        parts.append("\n== Overview ==")
        parts.append(overview_content)
    else:
        parts.append("\n== Overview ==")
        parts.append("<!-- Add custom content about this day here -->")
    
    parts.append("\n== Calculations ==")

    parts.append("\n=== Recent (±10 ISO years) ===")
    parts.append(recent_block(m_idx, d_m, span=10))

    parts.append(f"\n=== Long-run Gregorian distribution ({LONGRUN_START}–{LONGRUN_END}) ===")
    parts.append(gregorian_distribution_block(m_idx, d_m, LONGRUN_START, LONGRUN_END))

    parts.append("\n=== Nth-weekday holidays (overlap probabilities) ===")
    parts.append(nth_weekday_overlap_block(m_idx, d_m, LONGRUN_START, LONGRUN_END))

    parts.append("\n=== Easter-relative distribution ===")
    parts.append(easter_offsets_block(m_idx, d_m, LONGRUN_START, LONGRUN_END))

    parts.append("\n=== Chinese calendar overlaps ===")
    parts.append(chinese_overlap_table(m_idx, d_m, LONGRUN_START, LONGRUN_END))

    #parts.append(f"\n== Chinese lunar date distribution ({LONGRUN_START}–{LONGRUN_END}) ==")
    parts.append(chinese_distribution_block(m_idx, d_m, LONGRUN_START, LONGRUN_END))

    parts.append("\n=== Hebrew calendar overlaps ===")
    parts.append(hebrew_overlap_table(m_idx, d_m, LONGRUN_START, LONGRUN_END))

    parts.append(f"\n=== Hebrew date distribution ({LONGRUN_START}–{LONGRUN_END}) ===")
    parts.append(hebrew_distribution_block(m_idx, d_m, LONGRUN_START, LONGRUN_END))



    parts.append("\n== See also ==")
    parts.append(f"* [[{prev_title}]]")
    parts.append(f"* [[{next_title}]]")
    parts.append("\n== References ==")
    parts.append("{{reflist}}")
    
    # --- Auto-categories based on overlaps across the long-run window ---
    category_lines = []
    category_lines += categories_for_fixed_dates(m_idx, d_m)
    category_lines += categories_for_nth_weekday(m_idx, d_m)
    category_lines += categories_for_easter_offsets(m_idx, d_m)

    if category_lines:
        parts.append("\n".join(category_lines))
    parts.append("\n[[Category:Gaian calendar days]]\n")
    
    # Add Gaian calendar navbox
    parts.append("{{Gaian calendar}}")
    
    parts.append("\n<!-- Generated by zodiac_wiki_pages.py -->\n")
    return title, "\n".join(parts)

# ------------- Minimal MediaWiki client -------------

class Wiki:
    def __init__(self, api_url: str):
        self.api = api_url
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": USER_AGENT})
        self.csrf = None

    def _check(self, r):
        try:
            r.raise_for_status()
        except requests.HTTPError:
            print("HTTP", r.status_code, r.url)
            print("Body:", r.text[:1000])
            raise

    def get(self, **params):
        params.setdefault("format", "json")
        r = self.s.get(self.api, params=params, timeout=60)
        self._check(r)
        return r.json()

    def post(self, **data):
        data.setdefault("format", "json")
        r = self.s.post(self.api, data=data, timeout=90)
        self._check(r)
        return r.json()

    def login_bot(self, username: str, password: str):
        t = self.get(action="query", meta="tokens", type="login")["query"]["tokens"]["logintoken"]
        j = self.post(action="login", lgname=username, lgpassword=password, lgtoken=t)
        if j.get("login", {}).get("result") != "Success":
            raise RuntimeError(f"Login failed: {j}")
        self.csrf = self.get(action="query", meta="tokens", type="csrf")["query"]["tokens"]["csrftoken"]

    def get_page_content(self, title: str) -> str:
        """Get the raw wikitext content of a page."""
        try:
            j = self.get(action="query", titles=title, prop="revisions", rvprop="content", rvslots="main")
            pages = j.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":  # Page doesn't exist
                    return ""
                revisions = page_data.get("revisions", [])
                if revisions:
                    return revisions[0].get("slots", {}).get("main", {}).get("*", "")
        except Exception as e:
            print(f"Error fetching page content for {title}: {e}")
        return ""

    def edit(self, title: str, text: str, summary: str):
        if not self.csrf:
            raise RuntimeError("Not logged in")
        j = self.post(
            action="edit",
            title=title,
            text=text,               # replaces content (create or overwrite)
            token=self.csrf,
            summary=summary,
            bot="1",
            minor="1",
        )
        if "error" in j:
            raise RuntimeError(f"Edit failed for {title}: {j['error']}")
        return j.get("edit", {}).get("result", "OK")

# ------------- Run all pages -------------

def get_month_date_ranges(m_idx: int, span: int = 10) -> str:
    """Get the Gregorian date ranges for a month across ±span years."""
    from collections import defaultdict
    from datetime import datetime
    
    current_iso_year = datetime.now().date().isocalendar()[0]
    year_ranges = defaultdict(list)
    
    # For intercalary months (Horus), use a larger span since they're rarer
    if m_idx == 14:
        span = 25
    
    for year_offset in range(-span, span + 1):
        iso_year = current_iso_year + year_offset
        gaian_year = iso_year + 10000
        
        # For intercalary month, only include 53-week years
        if m_idx == 14:
            try:
                date.fromisocalendar(iso_year, 53, 1)
            except ValueError:
                continue  # Skip non-53-week years
        
        # Get first and last day of the month
        try:
            if m_idx == 14:
                # Horus: week 53, days 1-7
                first_day = date.fromisocalendar(iso_year, 53, 1)
                last_day = date.fromisocalendar(iso_year, 53, 7)
            else:
                # Regular month: calculate weeks
                start_week = (m_idx - 1) * 4 + 1
                end_week = m_idx * 4
                first_day = date.fromisocalendar(iso_year, start_week, 1)
                last_day = date.fromisocalendar(iso_year, end_week, 7)
            
            year_ranges[gaian_year] = [first_day, last_day]
        except ValueError:
            continue
    
    # Format the output
    lines = ['{| class="wikitable sortable"']
    lines.append('! Gaian Year !! Start Date !! End Date !! Gregorian Years')
    
    for gaian_year in sorted(year_ranges.keys()):
        start_date, end_date = year_ranges[gaian_year]
        
        # Get Gregorian years overlapped - simply check start and end dates
        greg_years = set()
        greg_years.add(start_date.year)
        greg_years.add(end_date.year)
        
        greg_years_list = sorted(list(greg_years))
        greg_years_str = ", ".join(str(y) for y in greg_years_list)
        
        lines.append(f"|-\n| {gaian_year} || {start_date.isoformat()} || {end_date.isoformat()} || {greg_years_str}")
    
    lines.append('|}')
    return '\n'.join(lines)

def build_month_page(m_idx: int, wiki: 'Wiki' = None) -> (str, str):
    """Build a page for a Gaian calendar month."""
    month_name = MONTHS[m_idx-1]
    title = f"{TITLE_PREFIX}{month_name}" if TITLE_PREFIX else month_name
    
    # Get existing page content to preserve Overview section
    existing_overview = ""
    if wiki:
        existing_content = wiki.get_page_content(title)
        existing_overview = extract_overview_section(existing_content)
    
    # Basic month information
    if m_idx == 14:  # Horus intercalary month
        days_in_month = 7
        weeks_in_month = 1
        description = f"{month_name} is the intercalary month of the [[Gaian calendar]]. It contains {days_in_month} days (one intercalary week) and occurs only in years with 53 ISO weeks."
        iso_weeks = "53"
    else:
        days_in_month = 28
        weeks_in_month = 4
        start_week = (m_idx - 1) * 4 + 1
        end_week = m_idx * 4
        description = f"{month_name} is the {ordinal(m_idx)} month of the [[Gaian calendar]]. It contains {days_in_month} days ({weeks_in_month} weeks) and corresponds to ISO weeks {start_week}–{end_week}."
        iso_weeks = f"{start_week}–{end_week}"
    
    # Navigation
    if m_idx == 1:
        prev_month = "Horus"
    else:
        prev_month = MONTHS[m_idx-2]
    
    if m_idx == 14:
        next_month = MONTHS[0]  # Sagittarius
    elif m_idx == 13:
        next_month = "Horus"
    else:
        next_month = MONTHS[m_idx]
    
    parts = []
    # Use the actual month template (e.g., {{Sagittarius}}, {{Ophiuchus}}, etc.)
    parts.append("{{" + month_name + "}}")
    
    parts.append(f"\n{description}")
    
    # Add Overview section
    parts.append("\n== Overview ==")
    if existing_overview:
        parts.append(existing_overview)
    else:
        parts.append("<!-- Add custom content about this month here -->")
    
    # Date ranges
    span_years = 25 if m_idx == 14 else 10
    parts.append(f"\n== Gregorian date ranges (±{span_years} years) ==")
    parts.append(get_month_date_ranges(m_idx, span_years))
    
    # Days in this month
    parts.append(f"\n== Days in {month_name} ==")
    
    # Format as a table for better presentation
    parts.append('{| class="wikitable"')
    parts.append('! Day !! Link')
    for d in range(1, days_in_month + 1):
        parts.append(f"|-\n| {d} || [[{month_name} {d}]]")
    parts.append('|}')
    
    # Navigation
    parts.append(f"\n== See also ==")
    parts.append(f"* [[{prev_month}]] (previous month)")
    parts.append(f"* [[{next_month}]] (next month)")
    parts.append(f"* [[Gaian calendar]]")
    
    # Categories
    parts.append(f"\n[[Category:Gaian calendar months|{m_idx:02d}]]")
    if m_idx == 14:
        parts.append(f"[[Category:Intercalary months]]")
    
    # Add Gaian calendar navbox
    parts.append(f"\n{{{{Gaian calendar}}}}")
    
    return title, "\n".join(parts)

def get_year_date_range(year: int) -> tuple:
    """Get the Gregorian date range for a Gaian year."""
    iso_year = year - 10000
    
    # First day of the year: Sagittarius 1 = Week 1, Day 1
    try:
        start_date = date.fromisocalendar(iso_year, 1, 1)
    except ValueError:
        # Handle years outside valid range
        return None, None
    
    # Last day of the year
    try:
        # Try week 53 first (intercalary years)
        end_date = date.fromisocalendar(iso_year, 53, 7)
    except ValueError:
        # Regular year: Week 52, Day 7
        end_date = date.fromisocalendar(iso_year, 52, 7)
    
    return start_date, end_date

def get_gregorian_year_overlaps(year: int) -> list:
    """Get the Gregorian years that this Gaian year overlaps with."""
    start_date, end_date = get_year_date_range(year)
    if start_date is None:
        return []
    
    years = []
    for greg_year in range(start_date.year, end_date.year + 1):
        years.append(greg_year)
    
    return years

def get_century_category(year: int) -> str:
    """Get the century category for a Gaian year."""
    if year == 0:
        return "[[Category:1st century]]"  # Year 0 is in the 1st century
    
    century_num = ((year - 1) // 100) + 1
    
    # Convert to ordinal
    if century_num % 100 in [11, 12, 13]:  # Special cases: 11th, 12th, 13th
        suffix = "th"
    elif century_num % 10 == 1:
        suffix = "st"
    elif century_num % 10 == 2:
        suffix = "nd"
    elif century_num % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    
    return f"[[Category:{century_num}{suffix} century]]"

def get_decade_category(year: int) -> str:
    """Get the decade category for a Gaian year."""
    if year < 10:
        return f"[[Category:{year}s]]"  # 0s, 1s, 2s, etc.
    
    decade_start = (year // 10) * 10
    return f"[[Category:{decade_start}s]]"

def build_holiday_dates_for_year(year: int) -> str:
    """Build a comprehensive holiday dates table for the given Gaian year."""
    iso_year = year - 10000
    
    # Check if dates can be calculated for this year
    try:
        test_date = date.fromisocalendar(iso_year, 1, 1)
    except ValueError:
        return f"<!-- Holiday dates not available for year {year} GE (outside supported date range) -->"
    
    holidays = []
    
    # 1. Fixed date holidays
    for name, (month, day) in FIXED_DATE_EVENTS.items():
        try:
            gregorian_date = date(iso_year, month, day)
            m_idx, d_m, month_name = gregorian_to_gaian_date(gregorian_date)
            holidays.append((name, f"[[{month_name} {d_m}]]", gregorian_date, "Fixed"))
        except ValueError:
            continue  # Skip if date doesn't exist (e.g., Feb 29 in non-leap year)
    
    # 2. Nth weekday holidays (only major US ones to avoid clutter)
    if iso_year >= 1900:  # Only for reasonable date range
        try:
            # Calculate specific holidays manually for better control
            
            # US Thanksgiving (4th Thursday in November)
            thanksgiving = nth_weekday_of_month(iso_year, 11, 3, 4)  # 4th Thu (3=Thu)
            m_idx, d_m, month_name = gregorian_to_gaian_date(thanksgiving)
            holidays.append(("US Thanksgiving", f"[[{month_name} {d_m}]]", thanksgiving, "Weekday"))
            
            # Black Friday (day after Thanksgiving)
            black_friday = thanksgiving + timedelta(days=1)
            m_idx, d_m, month_name = gregorian_to_gaian_date(black_friday)
            holidays.append(("Black Friday", f"[[{month_name} {d_m}]]", black_friday, "Weekday"))
            
            # US Memorial Day (last Monday in May)
            memorial_day = last_weekday_of_month(iso_year, 5, 0)  # last Mon (0=Mon)
            m_idx, d_m, month_name = gregorian_to_gaian_date(memorial_day)
            holidays.append(("US Memorial Day", f"[[{month_name} {d_m}]]", memorial_day, "Weekday"))
            
            # US Labor Day (1st Monday in September)
            labor_day = nth_weekday_of_month(iso_year, 9, 0, 1)  # 1st Mon (0=Mon)
            m_idx, d_m, month_name = gregorian_to_gaian_date(labor_day)
            holidays.append(("US Labor Day", f"[[{month_name} {d_m}]]", labor_day, "Weekday"))
            
            # Mother's Day (2nd Sunday in May)
            mothers_day = nth_weekday_of_month(iso_year, 5, 6, 2)  # 2nd Sun (6=Sun)
            m_idx, d_m, month_name = gregorian_to_gaian_date(mothers_day)
            holidays.append(("Mother's Day", f"[[{month_name} {d_m}]]", mothers_day, "Weekday"))
            
            # Father's Day (3rd Sunday in June)  
            fathers_day = nth_weekday_of_month(iso_year, 6, 6, 3)  # 3rd Sun (6=Sun)
            m_idx, d_m, month_name = gregorian_to_gaian_date(fathers_day)
            holidays.append(("Father's Day", f"[[{month_name} {d_m}]]", fathers_day, "Weekday"))
            
        except Exception:
            pass  # Skip if calculation fails
    
    # 3. Easter-related holidays (only major ones)
    try:
        easter_date = easter_sunday_gregorian(iso_year)
        major_easter_holidays = {
            -63: "Septuagesima Sunday",
            -56: "Sexagesima Sunday", 
            -49: "Quinquagesima Sunday",
            -47: "Mardi Gras/Carnival",
            -46: "Ash Wednesday",
            -35: "2nd Sunday in Lent",
            -28: "3rd Sunday in Lent", 
            -21: "Laetare Sunday (4th Sunday in Lent)",
            -14: "Passion Sunday (5th Sunday in Lent)",
            -7: "Palm Sunday",
            -3: "Maundy Thursday",
            -2: "Good Friday",
            -1: "Holy Saturday",
            0: "Easter Sunday",
            +1: "Easter Monday",
            +7: "Second Sunday of Easter (Divine Mercy Sunday)",
            +39: "Ascension Thursday",
            +49: "Pentecost Sunday",
            +56: "Trinity Sunday",
            +60: "Corpus Christi"
        }
        for offset_days, label in major_easter_holidays.items():
            holiday_date = easter_date + timedelta(days=offset_days)
            # Only include if the holiday date is in the same ISO year
            if holiday_date.isocalendar()[0] == iso_year:
                m_idx, d_m, month_name = gregorian_to_gaian_date(holiday_date)
                holidays.append((label, f"[[{month_name} {d_m}]]", holiday_date, "Easter"))
    except Exception:
        pass  # Skip if Easter calculation fails
    
    # 4. Chinese holidays (if available)
    if HAVE_CHINESE and 1900 <= iso_year <= 2100:
        try:
            for event in CHINESE_EVENTS:
                if event["type"] == "lunar":
                    # Try to find this lunar date in the given ISO year
                    for test_date in [date(iso_year, m, d) for m in range(1, 13) for d in range(1, 32)]:
                        try:
                            if chinese_event_matches_gregorian(test_date, event):
                                m_idx, d_m, month_name = gregorian_to_gaian_date(test_date)
                                holidays.append((event["name"], f"[[{month_name} {d_m}]]", test_date, "Chinese"))
                                break
                        except (ValueError, AttributeError):
                            continue
        except Exception:
            pass
    
    # 5. Hebrew holidays (if available)
    if HAVE_HEBREW:
        try:
            for event in HEBREW_EVENTS:
                if event.get("optional"):
                    continue  # Skip optional events to reduce clutter
                # Try to find dates within the ISO year
                for test_date in [date(iso_year, m, d) for m in range(1, 13) for d in range(1, 32)]:
                    try:
                        if hebrew_event_matches_gregorian(test_date, event):
                            m_idx, d_m, month_name = gregorian_to_gaian_date(test_date)
                            holidays.append((event["name"], f"[[{month_name} {d_m}]]", test_date, "Hebrew"))
                            break
                    except (ValueError, AttributeError):
                        continue
        except Exception:
            pass
    
    if not holidays:
        return f"== Holiday dates in {year} GE ==\nNo major holidays calculated for this year."
    
    # Sort holidays by gregorian date
    holidays.sort(key=lambda x: x[2])
    
    # Build the table
    lines = [f"== Holiday dates in {year} GE =="]
    lines.append('{| class="wikitable sortable"')
    lines.append('! Holiday !! Gaian Date !! Gregorian Date !! Type')
    
    for name, gaian_date, gregorian_date, holiday_type in holidays:
        greg_str = gregorian_date.strftime("%B %d").replace(" 0", " ")
        lines.append(f"|-\n| {name} || {gaian_date} || {greg_str} || {holiday_type}")
    
    lines.append('|}')
    lines.append(f"<small>Calculated holidays for Gaian year {year} GE (ISO year {iso_year}).</small>")
    
    return '\n'.join(lines)

def build_gregorian_correspondence_table(year: int) -> str:
    """Build a comprehensive date conversion table for the year."""
    iso_year = year - 10000
    
    # Check if dates can be calculated for this year
    try:
        from datetime import date
        test_date = date.fromisocalendar(iso_year, 1, 1)
    except ValueError:
        return f"<!-- Gregorian correspondence table not available for year {year} (outside supported date range) -->"
    
    # Check if this is a leap year (has 53 weeks)
    has_intercalary = False
    try:
        date.fromisocalendar(iso_year, 53, 1)
        has_intercalary = True
    except ValueError:
        has_intercalary = False
    
    lines = [f"== Gregorian correspondence in {iso_year} =="]
    lines.append('{| class="wikitable"')
    lines.append('! Month !! Day !! Gregorian Date')
    
    # Process each month
    for m_idx in range(1, 14):  # Regular months 1-13
        month_name = MONTHS[m_idx-1]
        
        for day in range(1, 29):  # Days 1-28 for each month
            try:
                gaian_date = zodiac_gregorian_for_iso_year(m_idx, day, iso_year)
                gregorian_str = gaian_date.strftime("%B %d").replace(" 0", " ").strip()
                
                # Format the row
                if day == 1:
                    lines.append(f"|-\n| rowspan=\"28\" | [[{month_name}]]")
                else:
                    lines.append("|-")
                
                lines.append(f"| [[{month_name} {day}|{day}]] || {gregorian_str}")
                
            except ValueError:
                continue
    
    # Add Horus intercalary days if this is a leap year
    if has_intercalary:
        for day in range(1, 8):  # Horus days 1-7
            try:
                gaian_date = zodiac_gregorian_for_iso_year(14, day, iso_year)  # Month 14 = Horus
                gregorian_str = gaian_date.strftime("%B %d").replace(" 0", " ").strip()
                
                if day == 1:
                    lines.append(f"|-\n| rowspan=\"7\" | [[Horus]]")
                else:
                    lines.append("|-")
                
                lines.append(f"| [[Horus {day}|{day}]] || {gregorian_str}")
                
            except ValueError:
                continue
    
    lines.append("|}") 
    return '\n'.join(lines)

def build_year_page(year: int, wiki: 'Wiki' = None) -> (str, str):
    """Build a page for a Gaian calendar year."""
    title = f"{TITLE_PREFIX}{year} GE" if TITLE_PREFIX else f"{year} GE"
    
    # Get existing page content to preserve Overview section
    existing_overview = ""
    if wiki:
        existing_content = wiki.get_page_content(title)
        existing_overview = extract_overview_section(existing_content)
    
    # Convert to ISO year (subtract 10,000)
    iso_year = year - 10000
    
    # Check if this is a leap year (has 53 weeks)
    has_intercalary = False
    try:
        from datetime import date
        # Try to create week 53, day 1
        date.fromisocalendar(iso_year, 53, 1)
        has_intercalary = True
    except ValueError:
        has_intercalary = False
    
    total_days = 371 if has_intercalary else 364
    
    # Get date range
    start_date, end_date = get_year_date_range(year)
    
    # Get Gregorian year overlaps
    gregorian_years = get_gregorian_year_overlaps(year)
    
    def format_year_reference(greg_year):
        """Format a Gregorian year with proper BC/AD and Wikipedia link."""
        if greg_year <= 0:
            bc_year = abs(greg_year - 1)  # Convert to BC (0 = 1 BC, -1 = 2 BC, etc.)
            return f"[[:en:{bc_year} BC|{bc_year} BC]][[en:{bc_year} BC]]"
        else:
            return f"[[:en:AD {greg_year}|{greg_year} AD]][[en:AD {greg_year}]]"
    
    parts = []
    # Add Year nav template at the beginning
    parts.append(f"{{{{Year nav|{year}}}}}")
    
    # Build the main description
    if iso_year <= 0:
        bc_year = abs(iso_year - 1)
        parts.append(f"\n'''{year}''' is a year in the [[Gaian calendar]], corresponding roughly to Gregorian {format_year_reference(iso_year)}.")
    else:
        parts.append(f"\n'''{year}''' is a year in the [[Gaian calendar]], corresponding roughly to Gregorian {format_year_reference(iso_year)}.")
    
    if start_date and end_date:
        parts.append(f"\n{year} goes from {start_date.isoformat()} to {end_date.isoformat()}.")
    
    if has_intercalary:
        parts.append(f"\nThis year contains {total_days} days, including the 7 intercalary days of [[Horus]].")
    else:
        parts.append(f"\nThis year contains {total_days} days across the 13 regular months.")
    
    # Gregorian year overlap information
    if gregorian_years:
        if len(gregorian_years) == 1:
            parts.append(f"\n{year} corresponds entirely to the Gregorian year {format_year_reference(gregorian_years[0])}.")
        elif len(gregorian_years) == 2:
            parts.append(f"\n{year} corresponds mostly to the Gregorian year {format_year_reference(gregorian_years[0])} but has some overlap with {format_year_reference(gregorian_years[1])}.")
        elif len(gregorian_years) == 3:
            parts.append(f"\n{year} corresponds mostly to the Gregorian year {format_year_reference(gregorian_years[1])} but has some overlap with {format_year_reference(gregorian_years[0])} and {format_year_reference(gregorian_years[2])}.")
    
    # Add Overview section
    parts.append("\n== Overview ==")
    if existing_overview:
        parts.append(existing_overview)
    else:
        parts.append("<!-- Add custom content about this year here -->")
    
    # Months in this year
    parts.append(f"\n== Months in {year} ==")
    parts.append('{| class="wikitable"')
    parts.append('! Month !! Days !! ISO Weeks')
    
    for m_idx in range(1, 14):
        month_name = MONTHS[m_idx-1]
        start_week = (m_idx - 1) * 4 + 1
        end_week = m_idx * 4
        parts.append(f"|-\n| [[{month_name}]] || 28 || {start_week}–{end_week}")
    
    if has_intercalary:
        parts.append(f"|-\n| [[Horus]] || 7 || 53")
    
    parts.append('|}')
    
    # Add holiday dates section
    parts.append(f"\n{build_holiday_dates_for_year(year)}")
    
    # Add comprehensive date conversion table
    parts.append(f"\n{build_gregorian_correspondence_table(year)}")
    
    # Navigation
    parts.append(f"\n== See also ==")
    if year > 0:
        parts.append(f"* [[{year-1} GE]] (previous year)")
    if year < 12100:
        parts.append(f"* [[{year+1} GE]] (next year)")
    parts.append(f"* [[Gaian calendar]]")
    
    # Categories
    parts.append(f"\n{get_century_category(year)}")
    parts.append(f"{get_decade_category(year)}")
    parts.append(f"[[Category:Gaian calendar years]]")
    if has_intercalary:
        parts.append(f"[[Category:Gaian leap years]]")
    else:
        parts.append(f"[[Category:Gaian common years]]")
    
    # Add DEFAULTSORT for proper year sorting
    parts.append(f"\n{{{{DEFAULTSORT:{year:05d}}}}}")
    
    # Add Gaian calendar navbox
    parts.append(f"\n{{{{Gaian calendar}}}}")
    
    return title, "\n".join(parts)

def main():
    parser = argparse.ArgumentParser(description='Generate Gaian calendar wiki pages')
    parser.add_argument('--username', required=True, help='Wiki username')
    parser.add_argument('--password', required=True, help='Wiki password')
    parser.add_argument('--days', action='store_true', help='Generate day pages (default behavior)')
    parser.add_argument('--months', action='store_true', help='Generate month pages')
    parser.add_argument('--years', action='store_true', help='Generate year pages')
    parser.add_argument('--year-start', type=int, default=0, help='Starting year for year pages (default: 1)')
    parser.add_argument('--year-end', type=int, default=12100, help='Ending year for year pages (default: 12100)')
    
    args = parser.parse_args()
    
    # If no specific type is requested, default to days
    if not (args.days or args.months or args.years):
        args.days = True
    
    wiki = Wiki(API_URL)
    wiki.login_bot(args.username, args.password)

    total_operations = 0
    successful_operations = 0
    
    if args.days:
        print("Generating day pages...")
        # Regular months: 13×28 = 364 days
        targets = [(m_idx, d) for m_idx in range(1, 14) for d in range(1, 29)]
        # Add Horus intercalary days: 7 days
        targets.extend([(14, d) for d in range(1, 8)])  # Horus 1-7
        
        total = len(targets)
        total_operations += total
        ok = 0
        for i, (m_idx, d) in enumerate(targets, 1):
            title, text = build_page(m_idx, d, wiki)
            try:
                res = wiki.edit(title, text, SUMMARY)
                ok += 1
                successful_operations += 1
                print(f"[DAY {i}/{total}] [{res}] {title}")
            except Exception as e:
                print(f"[DAY {i}/{total}] [ERROR] {title} :: {e}")
            time.sleep(THROTTLE)

        print(f"Days completed. Success {ok}/{total}. (364 regular + 7 intercalary)")
    
    if args.months:
        print("Generating month pages...")
        total = 14  # 13 regular months + 1 intercalary
        total_operations += total
        ok = 0
        for m_idx in range(1, 15):  # 1-14 inclusive
            title, text = build_month_page(m_idx, wiki)
            try:
                res = wiki.edit(title, text, "Create/update Gaian calendar month page")
                ok += 1
                successful_operations += 1
                print(f"[MONTH {m_idx}/14] [{res}] {title}")
            except Exception as e:
                print(f"[MONTH {m_idx}/14] [ERROR] {title} :: {e}")
            time.sleep(THROTTLE)
        
        print(f"Months completed. Success {ok}/{total}.")
    
    if args.years:
        print(f"Generating year pages ({args.year_start}-{args.year_end})...")
        year_range = range(args.year_start, args.year_end + 1)
        total = len(year_range)
        total_operations += total
        ok = 0
        
        for i, year in enumerate(year_range, 1):
            title, text = build_year_page(year, wiki)
            try:
                res = wiki.edit(title, text, "Create/update Gaian calendar year page")
                ok += 1
                successful_operations += 1
                print(f"[YEAR {i}/{total}] [{res}] {title}")
            except Exception as e:
                print(f"[YEAR {i}/{total}] [ERROR] {title} :: {e}")
            time.sleep(THROTTLE)
        
        print(f"Years completed. Success {ok}/{total}.")
    
    print(f"All operations completed. Total success: {successful_operations}/{total_operations}.")

if __name__ == "__main__":
    main()
