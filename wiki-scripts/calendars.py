"""
A date in the Gaian, Hebrew, Islamic and solar Hijri calendars, for the notes on every dated event in gaiad.ged.

Emma, 2026-10-13: the dates "will all have notes giving their Gaian calendar dates too", and "notes that are
basically like all of the different calendars ... the date in Hebrew, ... Islamic, solar Hijri. Etc."

Arithmetic from Reingold and Dershowitz, *Calendrical Calculations* (fixed day numbers, R.D. 1 = Monday,
1 January 1 CE, proleptic Gregorian). The Islamic date is the arithmetic (tabular) calendar and the solar Hijri
the arithmetic 2820-year form; both can differ by a day from a calendar fixed by observation, so the notes say
"arithmetic". Years before each era (before 622 CE for Islamic and solar Hijri) are left out. Stdlib only.
"""
from math import ceil, floor

GAIAN_MONTHS = ["Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer",
                "Leo", "Virgo", "Libra", "Scorpius", "Ophiuchus", "Horus"]
HEBREW_MONTHS = ["Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishri", "Heshvan", "Kislev", "Tevet",
                 "Shevat", "Adar", "Adar II"]
ISLAMIC_MONTHS = ["Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani", "Jumada al-Ula", "Jumada al-Akhira",
                  "Rajab", "Shaban", "Ramadan", "Shawwal", "Dhu al-Qada", "Dhu al-Hijja"]
PERSIAN_MONTHS = ["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar", "Mehr", "Aban",
                  "Azar", "Dey", "Bahman", "Esfand"]


def gregorian_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def fixed_from_gregorian(y, m, d):
    """y is an astronomical year (1 BCE = 0)."""
    return (365 * (y - 1) + floor((y - 1) / 4) - floor((y - 1) / 100) + floor((y - 1) / 400)
            + floor((367 * m - 362) / 12) + (0 if m <= 2 else (-1 if gregorian_leap(y) else -2)) + d)


# ── Gaian: ISO week-year + 10,000; 13 months of four weeks, Horus for week 53 ──

def iso_week1_start(y):
    jan4 = fixed_from_gregorian(y, 1, 4)
    return jan4 - ((jan4 - 1) % 7)          # back to Monday (R.D. 1 is a Monday)


def gaian_from_fixed(rd):
    y = floor((rd - 1) / 365.2425) + 1
    while iso_week1_start(y + 1) <= rd:
        y += 1
    while iso_week1_start(y) > rd:
        y -= 1
    days = rd - iso_week1_start(y)
    week, weekday = days // 7 + 1, days % 7 + 1
    month = (week - 1) // 4 + 1
    day = ((week - 1) % 4) * 7 + weekday if month <= 13 else weekday
    return y + 10000, month, day


# ── Hebrew ──

HEBREW_EPOCH = -1373427   # fixed_from_julian(-3761, October, 7)


def hebrew_leap(y):
    return (7 * y + 1) % 19 < 7


def _elapsed(y):
    months = floor((235 * y - 234) / 19)
    parts = 12084 + 13753 * months
    days = 29 * months + floor(parts / 25920)
    return days + 1 if (3 * (days + 1)) % 7 < 3 else days


def _correction(y):
    ny0, ny1, ny2 = _elapsed(y - 1), _elapsed(y), _elapsed(y + 1)
    if ny2 - ny1 == 356:
        return 2
    if ny1 - ny0 == 382:
        return 1
    return 0


def hebrew_new_year(y):
    return HEBREW_EPOCH + _elapsed(y) + _correction(y)


def _year_days(y):
    return hebrew_new_year(y + 1) - hebrew_new_year(y)


def _last_day(m, y):
    if m in (2, 4, 6, 10, 13) or (m == 12 and not hebrew_leap(y)):
        return 29
    if m == 8 and _year_days(y) not in (355, 385):
        return 29
    if m == 9 and _year_days(y) in (353, 383):
        return 29
    return 30


def _last_month(y):
    return 13 if hebrew_leap(y) else 12


def fixed_from_hebrew(y, m, d):
    rd = hebrew_new_year(y) + d - 1
    if m < 7:
        rd += sum(_last_day(mm, y) for mm in range(7, _last_month(y) + 1))
        rd += sum(_last_day(mm, y) for mm in range(1, m))
    else:
        rd += sum(_last_day(mm, y) for mm in range(7, m))
    return rd


def hebrew_from_fixed(rd):
    approx = floor((rd - HEBREW_EPOCH) / (35975351 / 98496)) + 1
    y = approx - 1 if hebrew_new_year(approx) > rd else approx
    if hebrew_new_year(y + 1) <= rd:
        y += 1
    start = 7 if rd < fixed_from_hebrew(y, 1, 1) else 1
    m = start
    while rd > fixed_from_hebrew(y, m, _last_day(m, y)):
        m += 1
    return y, m, rd - fixed_from_hebrew(y, m, 1) + 1


def hebrew_month_name(m, y):
    if m == 12 and hebrew_leap(y):
        return "Adar I"
    return HEBREW_MONTHS[m - 1]


# ── Islamic (arithmetic) ──

ISLAMIC_EPOCH = 227015    # fixed_from_julian(622, July, 16)


def fixed_from_islamic(y, m, d):
    return d + 29 * (m - 1) + floor((6 * m - 1) / 11) + (y - 1) * 354 + floor((3 + 11 * y) / 30) + ISLAMIC_EPOCH - 1


def islamic_from_fixed(rd):
    y = floor((30 * (rd - ISLAMIC_EPOCH) + 10646) / 10631)
    m = floor((11 * (rd - fixed_from_islamic(y, 1, 1)) + 330) / 325)
    return y, m, rd - fixed_from_islamic(y, m, 1) + 1


# ── Solar Hijri (arithmetic) ──

PERSIAN_EPOCH = 226896    # fixed_from_julian(622, March, 19)


def fixed_from_persian(y, m, d):
    y0 = y - 474 if y > 0 else y - 473
    y1 = y0 % 2820 + 474
    return (PERSIAN_EPOCH - 1 + 1029983 * floor(y0 / 2820) + 365 * (y1 - 1) + floor((31 * y1 - 5) / 128)
            + (31 * (m - 1) if m <= 7 else 30 * (m - 1) + 6) + d)


def persian_from_fixed(rd):
    d0 = rd - fixed_from_persian(475, 1, 1)
    n2820, d1 = floor(d0 / 1029983), d0 % 1029983
    y2820 = 2820 if d1 == 1029982 else floor((128 * d1 + 46878) / 46751)
    y = 474 + 2820 * n2820 + y2820
    if y <= 0:
        y -= 1
    doy = 1 + rd - fixed_from_persian(y, 1, 1)
    m = ceil(doy / 31) if doy <= 186 else ceil((doy - 6) / 30)
    return y, m, rd - fixed_from_persian(y, m, 1) + 1


def calendar_note(year, month, day):
    """The note for one exact date (year astronomical: 1 BCE = 0)."""
    rd = fixed_from_gregorian(year, month, day)
    gy, gm, gd = gaian_from_fixed(rd)
    parts = [f"Gaian: {GAIAN_MONTHS[gm - 1]} {gd}, {gy} GE"]
    hy, hm, hd = hebrew_from_fixed(rd)
    parts.append(f"Hebrew: {hd} {hebrew_month_name(hm, hy)} {hy}")
    if rd >= ISLAMIC_EPOCH:
        iy, im, idd = islamic_from_fixed(rd)
        parts.append(f"Islamic (arithmetic): {idd} {ISLAMIC_MONTHS[im - 1]} {iy} AH")
    if rd >= PERSIAN_EPOCH:
        py, pm, pd = persian_from_fixed(rd)
        parts.append(f"Solar Hijri (arithmetic): {pd} {PERSIAN_MONTHS[pm - 1]} {py} SH")
    return "; ".join(parts)


if __name__ == "__main__":
    for d in [(2026, 10, 15), (2026, 9, 12), (2025, 12, 29), (2026, 3, 21), (1996, 2, 26), (622, 7, 16)]:
        print(d, calendar_note(*d))
