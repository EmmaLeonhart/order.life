#!/usr/bin/env python
"""
order.life FastSite Builder
Generates static HTML for all languages and pages of the Lifeism website.
Uses Jinja2 templates, outputs to site/{lang}/ directories.
"""

import csv
import datetime
import io
import math
import os
import re
import sys
import json
import shutil
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date

# Fix Windows console encoding issues.
# Some environments default to cp1252 and will crash when printing non-Latin text.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="backslashreplace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="backslashreplace"
        )

SCRIPT_DIR = Path(__file__).parent
SITE_DIR = SCRIPT_DIR / "site"
SITE_TMP_DIR = SCRIPT_DIR / "site_tmp"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
CONTENT_DIR = SCRIPT_DIR / "content"
EPIC_DIR = SCRIPT_DIR / "Gaiad" / "epic"
DEFAULT_LANG = "en"  # English pages live at site root (no /en/ prefix)

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("ERROR: jinja2 not found. Install with: pip install jinja2")
    sys.exit(1)

try:
    import markdown as md
except ImportError:
    md = None

from markupsafe import Markup, escape

# ── Calendar Data ──────────────────────────────────────────────────────────

MONTHS = [
    {"num": 1,  "id": "sagittarius", "symbol": "\u2650", "element": "fire"},
    {"num": 2,  "id": "capricorn",   "symbol": "\u2651", "element": "earth"},
    {"num": 3,  "id": "aquarius",    "symbol": "\u2652", "element": "air"},
    {"num": 4,  "id": "pisces",      "symbol": "\u2653", "element": "water"},
    {"num": 5,  "id": "aries",       "symbol": "\u2648", "element": "fire"},
    {"num": 6,  "id": "taurus",      "symbol": "\u2649", "element": "earth"},
    {"num": 7,  "id": "gemini",      "symbol": "\u264a", "element": "air"},
    {"num": 8,  "id": "cancer",      "symbol": "\u264b", "element": "water"},
    {"num": 9,  "id": "leo",         "symbol": "\u264c", "element": "fire"},
    {"num": 10, "id": "virgo",       "symbol": "\u264d", "element": "earth"},
    {"num": 11, "id": "libra",       "symbol": "\u264e", "element": "air"},
    {"num": 12, "id": "scorpius",    "symbol": "\u264f", "element": "water"},
    {"num": 13, "id": "ophiuchus",   "symbol": "\u26ce", "element": "healing"},
    {"num": 14, "id": "horus",       "symbol": "𓅃", "element": "intercalary"},
]

# Map wiki month names to our IDs (wiki uses "Scorpio" not "Scorpius")
WIKI_MONTH_TO_ID = {
    "Sagittarius": "sagittarius", "Capricorn": "capricorn", "Aquarius": "aquarius",
    "Pisces": "pisces", "Aries": "aries", "Taurus": "taurus", "Gemini": "gemini",
    "Cancer": "cancer", "Leo": "leo", "Virgo": "virgo", "Libra": "libra",
    "Scorpio": "scorpius", "Scorpius": "scorpius", "Ophiuchus": "ophiuchus",
    "Horus": "horus",
}

MONTH_ID_TO_WIKI = {v: k for k, v in WIKI_MONTH_TO_ID.items()}
# Fix: scorpius maps to "Scorpio" in wiki
MONTH_ID_TO_WIKI["scorpius"] = "Scorpio"

ELEMENT_THEMES = {
    "fire": {"color": "#ff6b35", "desc_key": "element_fire"},
    "earth": {"color": "#4a7c59", "desc_key": "element_earth"},
    "air": {"color": "#5b9bd5", "desc_key": "element_air"},
    "water": {"color": "#2e86ab", "desc_key": "element_water"},
    "healing": {"color": "#9b59b6", "desc_key": "element_healing"},
    "intercalary": {"color": "#8a2be2", "desc_key": "element_intercalary"},
}

MONTH_THEMES = {
    "sagittarius": (
        "Creation of the Universe",
        "The Gaiad opens with the creation of the universe — the Big Bang, the formation of stars and galaxies, "
        "the birth of Earth, and the first stirrings of life. Days 1–28 span the deepest cosmic and geological "
        "time, from the first moments of existence through the Hadean and Archean eons."
    ),
    "capricorn": (
        "The Cambrian Explosion",
        "Days 29–56 cover the sudden proliferation of complex animal life — the Cambrian explosion — "
        "when the seas filled with the ancestors of every major animal body plan alive today: "
        "trilobites, the strange creatures of the Burgess Shale, and the first nervous systems."
    ),
    "aquarius": (
        "Life Comes Ashore",
        "Days 57–84 follow life's conquest of the land — the first forests, the first four-limbed "
        "vertebrates hauling themselves out of the water, insects taking to the air, and the rise "
        "of the great coal swamps that would later power industrial civilization."
    ),
    "pisces": (
        "The Age of Dinosaurs — The Easter Month",
        "Days 85–112 cover the Triassic, Jurassic, and Cretaceous periods — the age of the dinosaurs — "
        "and the great extinction that ended them. Pisces is the Easter month: all five possible dates "
        "of Easter fall across Aquarius 28, Pisces 7, Pisces 14, Pisces 21, and Pisces 28. "
        "Pisces 14 is the historical day of the crucifixion. We celebrate with dinosaur Easter eggs, "
        "honouring the living dinosaurs — birds — and the deep time of the scripture."
    ),
    "aries": (
        "The Rise of Mammals and Early Humanity",
        "Days 113–140 trace the rise of mammals after the great extinction, the emergence of primates, "
        "and the long evolutionary journey toward modern humans: bipedalism, tool use, and the first "
        "cultures. Pentecost/Shavuot falls across five possible days spanning Aries and Taurus — "
        "Aries 21, Aries 28, Taurus 7 (canonical), Taurus 14, and Taurus 21."
    ),
    "taurus": (
        "The Dawn of Civilization",
        "Days 141–168 cover early human civilizations — the first cities, agriculture, writing, "
        "the great river cultures of Mesopotamia, Egypt, and the Indus Valley, and the Bronze Age. "
        "Taurus 7 is the canonical Pentecost/Shavuot."
    ),
    "gemini": (
        "The Ancient World",
        "Days 169–196 journey through the classical world — Greece, Rome, the Han dynasty, "
        "the spread of the world religions, and the empires that shaped the first millennium CE."
    ),
    "cancer": (
        "The Medieval World and the Americas",
        "Days 197–224 cover the medieval period and the age of exploration, culminating on "
        "Cancer 28 — the day Columbus made landfall in the Americas, linking the Old World and the New."
    ),
    "leo": (
        "The Book of Lehi — Indigenous Peoples of the Americas",
        "Days 225–252 tell the story of the indigenous peoples of the Americas, from the first "
        "crossing of Beringia through the great civilizations — Olmec, Maya, Aztec, Inca — to the "
        "early 1830s. This is the Book of Lehi, one of the most sacred narratives in the Gaiad."
    ),
    "virgo": (
        "The Modern Era — Season of Repentance",
        "Days 253–280 enter the modern era: colonialism, revolution, and the reckoning with history. "
        "Virgo is the season of repentance, echoing the Jewish High Holy Days: Virgo 7 (Rosh Hashanah), "
        "Virgo 15 (Yom Kippur), Virgo 19 (Sukkot), Virgo 26 (end of Sukkot). The narrative of "
        "colonialism and repentance follows its own arc rather than being spread across all days as Easter is."
    ),
    "libra": (
        "The Modern World",
        "Days 281–308 continue through the modern world — the Industrial Revolution, the beginnings "
        "of the World Wars, and the geopolitical landscape of the 20th century taking shape."
    ),
    "scorpius": (
        "The 20th Century",
        "Days 309–336 bring the great conflicts and turning points of the modern age to their "
        "resolution. Scorpio 21 marks the end of World War II — V-J Day and the formal surrender "
        "aboard the USS Missouri."
    ),
    "ophiuchus": (
        "Recent History and the Vision",
        "Days 337–364 cover the most recent history — the Cold War, the digital revolution, "
        "and the founding of the Order of Life itself. The final chapters of the Gaiad turn to "
        "prophecy and offer a vision of the world to come."
    ),
    "horus": (
        "The Intercalary Days",
        "Horus carries no Gaiad scripture — it stands apart as an intercalary period of 5–7 days "
        "modelled on the Ancient Egyptian epagomenal days. Each day honours a divine birth: "
        "Day 1 Osiris, Day 2 Horus, Day 3 Set, Day 4 Isis, Day 5 Nephthys (a Friday Sabbath). "
        "In 53-week years, Day 6 is the Saturday Sabbath and Day 7 is Sunday — New Year's Eve "
        "before Sagittarius 1 begins the cycle anew."
    ),
}

WEEKDAYS = [
    {"num": 1, "id": "monday",    "planet": "Moon",    "symbol": "\u263D"},
    {"num": 2, "id": "tuesday",   "planet": "Mars",    "symbol": "\u2642"},
    {"num": 3, "id": "wednesday", "planet": "Mercury", "symbol": "\u263F"},
    {"num": 4, "id": "thursday",  "planet": "Jupiter", "symbol": "\u2643"},
    {"num": 5, "id": "friday",    "planet": "Venus",   "symbol": "\u2640"},
    {"num": 6, "id": "saturday",  "planet": "Saturn",  "symbol": "\u2644"},
    {"num": 7, "id": "sunday",    "planet": "Sun",     "symbol": "\u2609"},
]

# Localized Gregorian month names + date formatting (avoid relying on system locales)
GREGORIAN_MONTHS = {
    "en": ["January","February","March","April","May","June","July","August","September","October","November","December"],
    "fr": ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"],
    "es": ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"],
    "ru": ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"],
    "uk": ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"],
    "ar": ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],
    "hi": ["जनवरी","फ़रवरी","मार्च","अप्रैल","मई","जून","जुलाई","अगस्त","सितंबर","अक्टूबर","नवंबर","दिसंबर"],
    "ja": ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"],
    "zh": ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"],
}

GREGORIAN_DATE_FMT = {
    "en": "{month} {day:02d}, {year}",
    "fr": "{day:02d} {month} {year}",
    "es": "{day:02d} {month} {year}",
    "ru": "{day:02d} {month} {year}",
    "uk": "{day:02d} {month} {year}",
    "ar": "{day} {month} {year}",
    "hi": "{day} {month} {year}",
    "ja": "{year}年{month}{day}日",
    "zh": "{year}年{month}{day}日",
}


def format_gregorian(d: date, lang: str) -> str:
    months = GREGORIAN_MONTHS.get(lang) or GREGORIAN_MONTHS["en"]
    fmt = GREGORIAN_DATE_FMT.get(lang) or GREGORIAN_DATE_FMT["en"]
    month = months[d.month - 1]
    return fmt.format(year=d.year, month=month, day=d.day)


RU_MONTH_GEN = {
    "sagittarius": "Стрельца",
    "capricorn": "Козерога",
    "aquarius": "Водолея",
    "pisces": "Рыб",
    "aries": "Овна",
    "taurus": "Тельца",
    "gemini": "Близнецов",
    "cancer": "Рака",
    "leo": "Льва",
    "virgo": "Девы",
    "libra": "Весов",
    "scorpius": "Скорпиона",
    "ophiuchus": "Змееносца",
    "horus": "Хоруса",
}

UK_MONTH_GEN = {
    "sagittarius": "Стрільця",
    "capricorn": "Козорога",
    "aquarius": "Водолія",
    "pisces": "Риб",
    "aries": "Овна",
    "taurus": "Тельця",
    "gemini": "Близнюків",
    "cancer": "Рака",
    "leo": "Лева",
    "virgo": "Діви",
    "libra": "Терезів",
    "scorpius": "Скорпіона",
    "ophiuchus": "Змієносця",
    "horus": "Горуса",
}


def lang_base(lang: str) -> str:
    """Return the URL base path for a language: '' for English, '/ja' for Japanese, etc."""
    return "" if lang == DEFAULT_LANG else f"/{lang}"


def build_gaian_date_html(lang: str, t: dict, gaian_today: dict, iso_weekday: int, preferred_weekday_names: list[str]) -> str:
    """Return localized HTML for today's Gaian date (with links) in a language-shaped order."""
    weekday = preferred_weekday_names[iso_weekday - 1]
    ge = t.get("gaian_era_abbrev", "GE")
    month_id = gaian_today["month_data"]["id"]
    month_num_str = f"{gaian_today['month']:02d}"
    month_symbol = gaian_today["month_data"]["symbol"]
    weekday_symbol = WEEKDAYS[iso_weekday - 1]["symbol"]
    day = gaian_today["day"]
    year = gaian_today["year"]
    b = lang_base(lang)

    # Display month (may need genitive)
    month_nom = (t.get("months", {}) or {}).get(month_id, month_id.title())
    if lang == "ru":
        month_disp = RU_MONTH_GEN.get(month_id, month_nom)
        return (
            f"{weekday_symbol}{month_symbol} "
            f"<a href='{b}/calendar/week/{iso_weekday}/'>{weekday}</a>, "
            f"{day}-й день <a href='{b}/calendar/{month_num_str}/'>{month_disp}</a>, "
            f"<a href='{b}/calendar/12026/'>{year}</a> года "
            f"<a href='{b}/calendar/gaian-era/'>{ge}</a>"
        )
    if lang == "uk":
        month_disp = UK_MONTH_GEN.get(month_id, month_nom)
        return (
            f"{weekday_symbol}{month_symbol} "
            f"<a href='{b}/calendar/week/{iso_weekday}/'>{weekday}</a>, "
            f"{day}-й день <a href='{b}/calendar/{month_num_str}/'>{month_disp}</a>, "
            f"<a href='{b}/calendar/12026/'>{year}</a> року "
            f"<a href='{b}/calendar/gaian-era/'>{ge}</a>"
        )
    if lang == "ja":
        month_disp = month_nom
        return (
            f"{weekday_symbol}{month_symbol} "
            f"<a href='{b}/calendar/12026/'>{year}</a>"
            f"<a href='{b}/calendar/gaian-era/'>{ge}</a> "
            f"<a href='{b}/calendar/{month_num_str}/'>{month_disp}</a>"
            f"<a href='{b}/calendar/{month_num_str}/{day:02d}/'>{day}</a>日（"
            f"<a href='{b}/calendar/week/{iso_weekday}/'>{weekday}</a>）"
        )
    if lang == "zh":
        month_disp = month_nom
        return (
            f"{weekday_symbol}{month_symbol} "
            f"<a href='{b}/calendar/12026/'>{year}</a>"
            f"<a href='{b}/calendar/gaian-era/'>{ge}</a> "
            f"<a href='{b}/calendar/{month_num_str}/'>{month_disp}</a>"
            f"<a href='{b}/calendar/{month_num_str}/{day:02d}/'>{day}</a>日（"
            f"<a href='{b}/calendar/week/{iso_weekday}/'>{weekday}</a>）"
        )
    if lang == "ar":
        month_disp = month_nom
        return (
            f"{weekday_symbol}{month_symbol} "
            f"<a href='{b}/calendar/week/{iso_weekday}/'>{weekday}</a>، "
            f"<a href='{b}/calendar/{month_num_str}/{day:02d}/'>{day}</a> "
            f"<a href='{b}/calendar/{month_num_str}/'>{month_disp}</a>، "
            f"<a href='{b}/calendar/12026/'>{year}</a> "
            f"<a href='{b}/calendar/gaian-era/'>{ge}</a>"
        )

    # Default (en/es/fr/hi etc): weekday, Month day, year GE
    month_disp = month_nom
    return (
        f"{weekday_symbol}{month_symbol} "
        f"<a href='{b}/calendar/week/{iso_weekday}/'>{weekday}</a>, "
        f"<a href='{b}/calendar/{month_num_str}/'>{month_disp}</a> "
        f"<a href='{b}/calendar/{month_num_str}/{day:02d}/'>{day}</a>, "
        f"<a href='{b}/calendar/12026/'>{year}</a> "
        f"<a href='{b}/calendar/gaian-era/'>{ge}</a>"
    )


# ── Data Loading ─────────────────────────────────────────────────────────-

def load_translations():
    """Load all translation files from content/i18n/"""
    translations = {}
    i18n_dir = CONTENT_DIR / "i18n"
    for lang_file in i18n_dir.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)
    return translations


def load_glossary():
    """Load localized proper-noun equivalents from content/glossary.json."""
    glossary_file = CONTENT_DIR / "glossary.json"
    if not glossary_file.exists():
        return {}
    with open(glossary_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_weekday_names():
    """Load weekday names map from content/weekday-names.json."""
    fpath = CONTENT_DIR / "weekday-names.json"
    if not fpath.exists():
        return {}
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_chapters():
    """Load Gaiad epic chapters from epic/ directory."""
    chapters = {}
    for i in range(1, 365):
        chapter_file = EPIC_DIR / f"chapter_{i:03d}.md"
        if chapter_file.exists():
            with open(chapter_file, "r", encoding="utf-8") as f:
                raw = f.read()
                clean = re.sub(r'\{\{c\|([^}]*)\}\}', r'\1', raw)
                chapters[i] = clean
    return chapters


def load_wiki_pages():
    """Load wiki page content from XML export. Returns dict of title -> wikitext."""
    wiki_pages = {}
    xml_file = SCRIPT_DIR / "lifeism+Wiki-20260209181520.xml"
    if not xml_file.exists():
        print("  Warning: Wiki XML not found, skipping wiki content")
        return wiki_pages

    tree = ET.parse(str(xml_file))
    root = tree.getroot()
    ns = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}

    for page in root.findall('.//mw:page', ns):
        title = page.find('mw:title', ns).text
        rev = page.find('.//mw:revision/mw:text', ns)
        if rev is not None and rev.text:
            wiki_pages[title] = rev.text

    return wiki_pages


# ── Fudoki Data ──────────────────────────────────────────────────────────

def load_fudoki_data():
    """Load realms JSON for the Hallowings (Fudoki) pages.

    Returns a list of dicts with keys: name, qid, and enrichment fields.
    Also loads per-realm markdown content from realms/content/{QID}.md.
    """
    json_file = SCRIPT_DIR / "realms" / "realms.json"
    if not json_file.exists():
        print("  Warning: realms/realms.json not found, skipping")
        return []
    with open(json_file, "r", encoding="utf-8") as f:
        realms = json.load(f)
    content_dir = SCRIPT_DIR / "realms" / "content"
    for realm in realms:
        realm["good_fudoki"] = realm.get("good_fudoki") is True
        md_file = content_dir / f"{realm.get('slug') or realm['qid']}.md"
        if md_file.exists():
            realm["content_md"] = md_file.read_text(encoding="utf-8").strip()
        else:
            realm["content_md"] = ""
    return realms



def load_shrine_data():
    """Load Shinto shrine coordinates from realms/shrines.csv.

    Returns a compact list of [lat, lon, label, qid] for shrines with coordinates.
    """
    csv_file = SCRIPT_DIR / "realms" / "shrines.csv"
    if not csv_file.exists():
        print("  Warning: realms/shrines.csv not found, skipping shrines")
        return []
    shrines = []
    with open(csv_file, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["lat"] and row["lon"]:
                try:
                    shrines.append([
                        round(float(row["lat"]), 5),
                        round(float(row["lon"]), 5),
                        row["label"],
                        row["qid"],
                    ])
                except ValueError:
                    pass
    return shrines


def extract_wiki_overview(wikitext):
    """Extract the == Overview == section from wikitext and do basic cleanup."""
    lines = wikitext.split('\n')
    in_overview = False
    overview_lines = []
    for line in lines:
        if line.strip().startswith('== Overview =='):
            in_overview = True
            continue
        if in_overview:
            # Stop at next level-2 heading
            if line.strip().startswith('== ') and not line.strip().startswith('=== '):
                break
            overview_lines.append(line)

    text = '\n'.join(overview_lines).strip()
    if not text:
        return None
    return wiki_to_html(text)


def extract_wiki_intro(wikitext):
    """Extract the intro paragraph (before first ==) from wikitext."""
    lines = wikitext.split('\n')
    intro_lines = []
    for line in lines:
        if line.strip().startswith('=='):
            break
        # Skip templates and categories
        if line.strip().startswith('{{') or line.strip().startswith('[[Category:'):
            continue
        if line.strip().startswith('{{DEFAULTSORT'):
            continue
        if line.strip():
            intro_lines.append(line)
    text = '\n'.join(intro_lines).strip()
    if not text:
        return None
    return wiki_to_html(text)


def wiki_to_html(text):
    """Very basic wikitext to HTML conversion."""
    # Remove templates like {{q|Q123}}
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    # Convert [[link|display]] and [[link]]
    text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    # Bold
    text = re.sub(r"'''(.*?)'''", r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r"''(.*?)''", r'<em>\1</em>', text)
    # H3
    text = re.sub(r'^===\s*(.+?)\s*===$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    # Wiki tables -> simplified HTML
    text = re.sub(r'\{\|[^\n]*\n', '<table class="wiki-table">\n', text)
    text = text.replace('|}', '</table>')
    text = re.sub(r'^\!\s*(.+)$', r'<th>\1</th>', text, flags=re.MULTILINE)
    text = re.sub(r'^\|\-\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r"^\|\s*(.+)$", r'<td>\1</td>', text, flags=re.MULTILINE)
    # Wrap consecutive th/td in tr
    lines = text.split('\n')
    result = []
    in_row = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<th>') or stripped.startswith('<td>'):
            if not in_row:
                result.append('<tr>')
                in_row = True
            result.append(line)
        else:
            if in_row:
                result.append('</tr>')
                in_row = False
            result.append(line)
    if in_row:
        result.append('</tr>')
    text = '\n'.join(result)
    # Paragraphs: double newlines
    text = re.sub(r'\n\n+', '</p><p>', text)
    if not text.startswith('<'):
        text = '<p>' + text + '</p>'
    # Clean up empty paragraphs
    text = re.sub(r'<p>\s*</p>', '', text)
    return text


# ── Gaian Date Computation ─────────────────────────────────────────────────

def iso_week_info(d):
    iso_cal = d.isocalendar()
    return iso_cal[0], iso_cal[1], iso_cal[2]


def gregorian_to_gaian(d):
    iso_year, week, day_of_week = iso_week_info(d)
    month_index = (week - 1) // 4
    week_in_month = (week - 1) % 4
    month = month_index + 1
    day = week_in_month * 7 + day_of_week
    return {
        "year": iso_year + 10000,
        "month": month,
        "day": day,
        "month_data": MONTHS[month - 1] if month <= 14 else MONTHS[0],
    }


def day_of_year(month_num, day_in_month):
    if month_num <= 13:
        return (month_num - 1) * 28 + day_in_month
    else:
        return 364 + day_in_month


# ── iCal Generation ───────────────────────────────────────────────────────

def _easter_gregorian(year):
    """Easter Sunday via Meeus-Jones-Butcher anonymous Gregorian algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)


def _gaian_day_to_greg(gaian_year, month_num, day_num):
    """Convert a Gaian year/month/day to a Gregorian datetime.date."""
    iso_year = gaian_year - 10000
    jan4 = datetime.date(iso_year, 1, 4)
    week1_start = jan4 - datetime.timedelta(days=jan4.isoweekday() - 1)
    offset = ((month_num - 1) * 28 + day_num - 1) if month_num <= 13 \
             else (364 + day_num - 1)
    return week1_start + datetime.timedelta(days=offset)


def _is_gaian_leap(gaian_year):
    """True if the Gaian year has 53 ISO weeks (includes Horus month)."""
    iso_year = gaian_year - 10000
    dec28 = datetime.date(iso_year, 12, 28)
    dow = dec28.isoweekday()
    thu = dec28 + datetime.timedelta(days=4 - dow)
    jan1 = datetime.date(thu.year, 1, 1)
    return ((thu - jan1).days + 7) // 7 == 53


def _ical_fold(line):
    """Fold an iCal line at 75 octets with CRLF + space continuation."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line + "\r\n"
    chunks, pos, first = [], 0, True
    while pos < len(encoded):
        limit = 75 if first else 74
        chunks.append(encoded[pos:pos + limit].decode("utf-8", errors="replace"))
        pos += limit
        first = False
    return "\r\n ".join(chunks) + "\r\n"


def _vevent(dtstart, summary, description, uid):
    """Return a complete VEVENT block string (CRLF line endings)."""
    dtend = dtstart + datetime.timedelta(days=1)
    desc_esc = description.replace("\\", "\\\\").replace(",", "\\,").replace("\n", "\\n")
    lines = [
        "BEGIN:VEVENT",
        f"DTSTART;VALUE=DATE:{dtstart:%Y%m%d}",
        f"DTEND;VALUE=DATE:{dtend:%Y%m%d}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc_esc}",
        f"UID:{uid}",
        "END:VEVENT",
    ]
    return "".join(_ical_fold(l) for l in lines)


# (month_num, day_num, summary, url-slug)
_ICAL_FIXED = [
    (1,  1,  "New Year's Day (Aster Day)",                 "new-years-day"),
    (1,  8,  "Coming of Age Day",                          "coming-of-age"),
    (2,  7,  "Groundhog Day",                              "groundhog-day"),
    (2,  14, "Valentine's Day · Lupercalia",               "valentines-day"),
    (2,  21, "Kinen-sai",                                  "kinen-sai"),
    (2,  28, "Lantern Festival",                           "lantern-festival"),
    (3,  7,  "Hinamatsuri",                                "hinamatsuri"),
    (3,  21, "Korei-sai · Ides of March · St Patrick's Day", "korei-sai"),
    (5,  14, "Cinco de Mayo",                              "cinco-de-mayo"),
    (7,  14, "Nagoshi no Oharai",                          "nagoshi"),
    (7,  21, "Tanabata",                                   "tanabata"),
    (7,  28, "Bastille Day",                               "bastille-day"),
    (8,  28, "Qixi",                                       "qixi"),
    (9,  14, "Alolalia",                                   "alolalia"),
    (10, 12, "Mid-Autumn Festival",                        "mid-autumn"),
    (10, 14, "Shindensai",                                 "shindensai"),
    (11, 1,  "Japan Sports Day",                           "sports-day"),
    (13, 21, "Christmas Day · Dongzhi Festival",           "christmas"),
]

_ICAL_HORUS = [
    (1, "Birth of Osiris"),
    (2, "Birth of Horus"),
    (3, "Birth of Set"),
    (4, "Birth of Isis"),
    (5, "Birth of Nephthys · Sabbath"),
    (7, "New Year's Eve"),
]

_ICAL_CHRISTIAN_OFFSETS = [
    (-46, "Ash Wednesday",     "ash-wednesday"),
    (-7,  "Palm Sunday",       "palm-sunday"),
    (-2,  "Good Friday",       "good-friday"),
    (-1,  "Holy Saturday",     "holy-saturday"),
    (0,   "Easter Sunday",     "easter"),
    (39,  "Ascension Thursday","ascension"),
    (49,  "Pentecost",         "pentecost"),
]


def _vevent_span(dtstart, dtend_excl, summary, description, uid):
    """Multi-day all-day spanning event (e.g. Lent, Eastertide)."""
    desc_esc = description.replace("\\", "\\\\").replace(",", "\\,").replace("\n", "\\n")
    lines = [
        "BEGIN:VEVENT",
        f"DTSTART;VALUE=DATE:{dtstart:%Y%m%d}",
        f"DTEND;VALUE=DATE:{dtend_excl:%Y%m%d}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc_esc}",
        f"UID:{uid}",
        "END:VEVENT",
    ]
    return "".join(_ical_fold(l) for l in lines)


def _fmt_greg(d):
    """Format date as '5 April 2026' (no leading zero)."""
    return f"{d.day} {d.strftime('%B %Y')}"


def _ordinal(n):
    """Return '1st', '2nd', '3rd', '4th', etc."""
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _ramadan_start(g_year):
    """Return approximate 1 Ramadan as datetime.date for a Gregorian year.

    Uses the tabular Hijri calendar (same algorithm as build_festival_data).
    May differ by ±1–2 days from announced dates.
    """
    h_approx = int((g_year - 622) * 1.030685)
    for h in range(h_approx - 1, h_approx + 2):
        if h < 1:
            continue
        # Tabular Hijri 1 Ramadan (month 9, day 1) → JDN
        jdn = (1
               + math.ceil(29.5 * 8)      # 8 full months before Ramadan
               + (h - 1) * 354
               + (11 * h + 3) // 30
               + 1948438)
        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        mm = (5 * e + 2) // 153
        day   = e - (153 * mm + 2) // 5 + 1
        month = mm + 3 - 12 * (mm // 10)
        year  = 100 * b + d - 4800 + mm // 10
        try:
            gd = datetime.date(year, month, day)
            if gd.year == g_year:
                return gd
        except Exception:
            continue
    return None


def gaian_day_description(gaian_year, month_num, day_num):
    """Return a Markdown description for a Gaian calendar day.

    Format:
      {Month} {day}, {year} GE is the {ordinal} day of {year} GE.
      [It is an auspicious combination of X, Y, and Z.]
      [On this day we read [chapter N](https://order.life/en/gaiad/NNN/).]
    """
    m = MONTHS[month_num - 1]
    month_disp = m["id"].capitalize()

    # Weekday: Gaian calendar is perpetual — (day_num - 1) % 7 gives 0=Mon … 6=Sun
    # TODO: replace with GaianCalendar library when available
    _WD_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_name = _WD_NAMES[(day_num - 1) % 7]

    try:
        gd = _gaian_day_to_greg(gaian_year, month_num, day_num)
    except Exception:
        return ""

    iso_year = gaian_year - 10000

    # Sentence 1: Day identification
    if month_num <= 13:
        chapter = (month_num - 1) * 28 + day_num
        intro = (f"{month_disp} {day_num}, {gaian_year} GE is the "
                 f"{_ordinal(chapter)} day of {gaian_year} GE, a {weekday_name}.")
    else:
        chapter = None
        intro = (f"Horus {day_num}, {gaian_year} GE is an intercalary {weekday_name} "
                 f"of {gaian_year} GE.")

    # Collect notable events/seasons on this day
    notable = []

    # Fixed holidays
    for (mn, dn, summary, _slug) in _ICAL_FIXED:
        if mn == month_num and dn == day_num:
            notable.append(summary)

    # Horus days
    if month_num == 14:
        for (dn, summary) in _ICAL_HORUS:
            if dn == day_num:
                notable.append(summary)

    # Christian season
    try:
        easter   = _easter_gregorian(iso_year)
        ash_wed  = easter - datetime.timedelta(days=46)
        pentecost = easter + datetime.timedelta(days=49)

        for (offset, summary, _slug) in _ICAL_CHRISTIAN_OFFSETS:
            if gd == easter + datetime.timedelta(days=offset):
                notable.append(summary)

        # Season context (if not already a specific feast day)
        specific_christian = {easter + datetime.timedelta(days=o)
                              for (o, _, _) in _ICAL_CHRISTIAN_OFFSETS}
        if ash_wed <= gd < easter and gd not in specific_christian:
            notable.append("the Season of Lent")
        elif easter < gd <= pentecost and gd not in specific_christian:
            notable.append("Eastertide")
    except Exception:
        pass

    # Ramadan
    try:
        ram_start = _ramadan_start(iso_year)
        if ram_start:
            ram_end = ram_start + datetime.timedelta(days=29)
            if gd == ram_start:
                notable.append("the beginning of Ramadan")
            elif ram_start < gd <= ram_end:
                notable.append("Ramadan")
    except Exception:
        pass

    # Sentence 2: Auspicious combination
    if notable:
        if len(notable) == 1:
            auspicious = f"It marks {notable[0]}."
        elif len(notable) == 2:
            auspicious = f"It is an auspicious combination of {notable[0]} and {notable[1]}."
        else:
            listed = ", ".join(notable[:-1]) + ", and " + notable[-1]
            auspicious = f"It is an auspicious combination of {listed}."
    else:
        auspicious = ""

    # Sentence 3: Gaiad reading
    if chapter and chapter <= 364:
        reading = (f"On this day we read "
                   f"[chapter {chapter}](https://order.life/en/gaiad/{chapter:03d}/).")
    else:
        reading = ""

    return " ".join(p for p in [intro, auspicious, reading] if p)


def _ical_year_holidays(gy, month_display):
    """Return list of (date, vevent_str) for all holiday events in a Gaian year."""
    events = []
    is_leap = _is_gaian_leap(gy)
    iso_year = gy - 10000

    for (mn, dn, summary, slug) in _ICAL_FIXED:
        try:
            gd = _gaian_day_to_greg(gy, mn, dn)
        except Exception:
            continue
        desc = f"Gaian date: {month_display[mn]} {dn}, {gy} GE"
        uid  = f"gaian-{gy}-{mn:02d}-{dn:02d}-{slug}@order.life"
        events.append((gd, _vevent(gd, summary, desc, uid)))

    if is_leap:
        for (dn, summary) in _ICAL_HORUS:
            try:
                gd = _gaian_day_to_greg(gy, 14, dn)
            except Exception:
                continue
            desc = f"Gaian date: Horus {dn}, {gy} GE (intercalary)"
            uid  = f"gaian-{gy}-14-{dn:02d}-horus@order.life"
            events.append((gd, _vevent(gd, summary, desc, uid)))

    try:
        easter = _easter_gregorian(iso_year)
        for (offset, summary, slug) in _ICAL_CHRISTIAN_OFFSETS:
            gd = easter + datetime.timedelta(days=offset)
            gaian = gregorian_to_gaian(gd)
            mname = month_display.get(gaian["month"], f"Month{gaian['month']}")
            desc = (f"{summary}, {_fmt_greg(gd)}. "
                    f"Gaian date: {mname} {gaian['day']}, {gy} GE")
            uid  = f"gaian-{gy}-christian-{slug}@order.life"
            events.append((gd, _vevent(gd, summary, desc, uid)))
    except Exception:
        pass

    return events


def _ical_year_daily(gy, month_display):
    """Return list of (date, vevent_str) for every day of a Gaian year."""
    events = []
    is_leap = _is_gaian_leap(gy)
    num_months = 14 if is_leap else 13

    for mn in range(1, num_months + 1):
        days_in_m = 7 if mn == 14 else 28
        m = MONTHS[mn - 1]
        for dn in range(1, days_in_m + 1):
            try:
                gd = _gaian_day_to_greg(gy, mn, dn)
            except Exception:
                continue
            summary = f"{m['symbol']} {m['id'].capitalize()} {dn}, {gy} GE"
            desc    = gaian_day_description(gy, mn, dn)
            uid     = f"gaian-{gy}-{mn:02d}-{dn:02d}-daily@order.life"
            events.append((gd, _vevent(gd, summary, desc, uid)))

    return events


def _ical_year_seasons(gy):
    """Return list of (date, vevent_str) for Lent and Eastertide season spans."""
    events = []
    iso_year = gy - 10000
    try:
        easter    = _easter_gregorian(iso_year)
        ash_wed   = easter - datetime.timedelta(days=46)
        pentecost = easter + datetime.timedelta(days=49)

        lent_desc = (f"Season of Lent: {_fmt_greg(ash_wed)} to {_fmt_greg(easter)}. "
                     f"40 days of fasting and reflection before Easter.")
        events.append((ash_wed, _vevent_span(
            ash_wed, easter + datetime.timedelta(days=1),
            "Season of Lent", lent_desc,
            f"gaian-{gy}-lent-season@order.life"
        )))

        tide_desc = (f"Eastertide: {_fmt_greg(easter)} to {_fmt_greg(pentecost)}. "
                     f"49 days from Easter to Pentecost.")
        events.append((easter, _vevent_span(
            easter, pentecost + datetime.timedelta(days=1),
            "Eastertide", tide_desc,
            f"gaian-{gy}-eastertide@order.life"
        )))
    except Exception:
        pass
    return events


def generate_ical_files(site_dir):
    """Generate Gaian Calendar .ics files into site/calendar/ical/."""
    ical_dir = site_dir / "calendar" / "ical"
    ical_dir.mkdir(parents=True, exist_ok=True)

    today      = datetime.date.today()
    current_ge = today.isocalendar()[0] + 10000

    # month_display: num → display name (capitalize id, "scorpius" → "Scorpius")
    month_display = {m["num"]: m["id"].capitalize() for m in MONTHS}

    files = {
        "current.ics": {
            "years":    range(current_ge - 2, current_ge + 3),
            "calname":  "Gaian Calendar (Current)",
            "caldesc":  "Gaian perpetual calendar: daily events, holidays, Lent and Eastertide",
            "daily":    True,
            "seasons":  True,
        },
        "gaian-holidays-extended.ics": {
            "years":    range(12000, 12041),
            "calname":  "Gaian Calendar Holidays 12000-12040",
            "caldesc":  "Gaian perpetual calendar holidays and Christian season, 2000-2040",
            "daily":    False,
            "seasons":  False,
        },
    }

    for filename, cfg in files.items():
        events = []
        for gy in cfg["years"]:
            if gy - 10000 < 1:
                continue
            events += _ical_year_holidays(gy, month_display)
            if cfg["daily"]:
                events += _ical_year_daily(gy, month_display)
            if cfg["seasons"]:
                events += _ical_year_seasons(gy)

        events.sort(key=lambda x: x[0])

        header = (
            "BEGIN:VCALENDAR\r\n"
            "VERSION:2.0\r\n"
            "PRODID:-//Order of Life//Gaian Calendar//EN\r\n"
            f"X-WR-CALNAME:{cfg['calname']}\r\n"
            f"X-WR-CALDESC:{cfg['caldesc']}\r\n"
            "CALSCALE:GREGORIAN\r\n"
            "METHOD:PUBLISH\r\n"
        )
        content = header + "".join(ev for _, ev in events) + "END:VCALENDAR\r\n"
        (ical_dir / filename).write_bytes(content.encode("utf-8"))
        print(f"  iCal {filename}: {len(events)} events")


# ── Wiki Redirect Generator ───────────────────────────────────────────────

def generate_wiki_redirects(wiki_pages, languages):
    """Generate static redirect pages for /{lang}/wiki/* and /wiki/*.

    Note: English uses unprefixed pages (no `en:`). Other languages use the
    MediaWiki interwiki-style `lang:Title` prefix (e.g. `hi:Main_Page`).
    """

    redirect_template = """<!DOCTYPE html>
<html><head><meta charset=\"UTF-8\">
<title>Redirecting...</title>
<meta http-equiv=\"refresh\" content=\"0; url={target}\">
<script>window.location.href='{target}';</script>
</head><body style=\"background:#0f0f1a;color:#e0e0e0;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;\">
<p>Redirecting to <a href=\"{target}\" style=\"color:#ffd700;\">Wiki: {title}</a>...</p>
</body></html>"""

    def target_for_lang(lang: str, title: str) -> str:
        safe_title = title.replace(" ", "_")
        if lang and lang != "en":
            return f"https://wiki.order.life/{lang}:{safe_title}"
        return f"https://wiki.order.life/{safe_title}"

    def write_wiki_tree(wiki_dir: Path, js_prefix_regex: str, lang: str | None):
        wiki_dir.mkdir(parents=True, exist_ok=True)

        # Main_Page redirect
        main_page_dir = wiki_dir / "Main_Page"
        main_page_dir.mkdir(exist_ok=True)
        (main_page_dir / "index.html").write_text(
            redirect_template.format(title="Main Page", target=target_for_lang(lang or "en", "Main_Page")),
            encoding="utf-8",
        )

        # Known wiki pages (from XML export)
        for title in wiki_pages:
            safe_title = title.replace(" ", "_")
            page_dir = wiki_dir / safe_title
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_text(
                redirect_template.format(title=title, target=target_for_lang(lang or "en", title)),
                encoding="utf-8",
            )

        # Site-mapped wiki titles (so every site page can have a corresponding wiki page)
        site_titles = [
            # Sections
            "evolution",
            "longevity",
            "shrines",
            "philosophy",
            "mythology",
            "scripture",
            # Calendar overview pages
            "Gaian_calendar",
            "Gaian_Era",
            "Gaian_calendar_datepicker",
            # Week navigation (nested paths)
            "week",
            *[f"week/{n}" for n in range(1, 8)],
            # Scripture index
            "Gaiad",
        ]
        for title in site_titles:
            safe_title = title.replace(" ", "_")
            page_dir = wiki_dir / safe_title  # may include slashes -> nested dirs
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_text(
                redirect_template.format(title=title, target=target_for_lang(lang or "en", title)),
                encoding="utf-8",
            )

        # Fallback index with JS redirect for unknown pages
        main_target = target_for_lang(lang or "en", "Main_Page")
        effective_lang = lang or "en"
        lang_prefix_js = f"{effective_lang}:" if effective_lang != "en" else ""
        (wiki_dir / "index.html").write_text(
            f"""<!DOCTYPE html>
<html><head><meta charset=\"UTF-8\"><title>Redirecting to Wiki...</title>
<script>
var path = window.location.pathname.replace({js_prefix_regex}, '').replace(/\\/$/, '');
if (!path) path = 'Main_Page';
var target = 'https://wiki.order.life/{lang_prefix_js}' + path;
window.location.href = target;
</script>
<noscript><meta http-equiv=\"refresh\" content=\"0; url={main_target}\"></noscript>
</head><body style=\"background:#0f0f1a;color:#e0e0e0;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;\">
<p>Redirecting to <a href=\"{main_target}\" style=\"color:#ffd700;\">lifeism Wiki</a>...</p>
</body></html>""",
            encoding="utf-8",
        )

    # Per-language wiki paths: /{lang}/wiki/... (English at /wiki/)
    for lang in languages:
        if lang == DEFAULT_LANG:
            wiki_dir = SITE_DIR / "wiki"
            js_regex = r"/^\\/wiki\\/?/"
        else:
            wiki_dir = SITE_DIR / lang / "wiki"
            js_regex = rf"/^\\/{lang}\\/wiki\\/?/"
        write_wiki_tree(wiki_dir, js_prefix_regex=js_regex, lang=lang)

    # Per-language /w paths: /{lang}/w/... (English at /w/)
    # Redirects to lifeism.miraheze.org/w/*
    for lang in languages:
        if lang == DEFAULT_LANG:
            w_dir = SITE_DIR / "w"
            js_regex = r"/^\\/w\\/?/"
        else:
            w_dir = SITE_DIR / lang / "w"
            js_regex = rf"/^\\/{lang}\\/w\\/?/"

        w_dir.mkdir(parents=True, exist_ok=True)
        main_root_target = "https://lifeism.miraheze.org/w"
        main_page_target = "https://lifeism.miraheze.org/w/Main_Page"

        # Main /w/ and /w/Main_Page/
        (w_dir / "index.html").write_text(
            f"""<!DOCTYPE html>
<html><head><meta charset=\"UTF-8\"><title>Redirecting to Wiki...</title>
<script>
var path = window.location.pathname.replace({js_regex}, '').replace(/\\/$/, '');
if (!path) {{
  window.location.href = {json.dumps(main_root_target)};
}} else {{
  window.location.href = 'https://lifeism.miraheze.org/w/' + path;
}}
</script>
<noscript><meta http-equiv=\"refresh\" content=\"0; url={main_root_target}\"></noscript>
</head><body style=\"background:#0f0f1a;color:#e0e0e0;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;\">
<p>Redirecting to <a href=\"{main_root_target}\" style=\"color:#ffd700;\">lifeism Wiki</a>...</p>
</body></html>""",
            encoding="utf-8",
        )
        main_page_dir = w_dir / "Main_Page"
        main_page_dir.mkdir(parents=True, exist_ok=True)
        (main_page_dir / "index.html").write_text(
            redirect_template.format(title="Main Page", target=main_page_target),
            encoding="utf-8",
        )


# ── Festival Data Generator ──────────────────────────────────────────────────

def generate_festival_data_js(static_dst):
    """Generate static/js/festival-data.js with Hebrew and Islamic calendar data.

    Hebrew dates (Passover, Hanukkah) via pyluach — covers 1 CE to 2150 CE
    (pyluach cannot represent BCE Gregorian dates).
    Islamic dates (Ramadan, Eid al-Fitr, Eid al-Adha) via hijridate (Umm
    al-Qura) where supported, tabular fallback otherwise; covers 1930–2150 CE.
    """
    import math
    from pyluach import dates as heb_dates

    HEBREW_YEAR_START = 1
    ISLAMIC_YEAR_START = 1930
    YEAR_END = 2150

    # ── Hebrew calendar ───────────────────────────────────────────────────────
    # Jewish days begin at nightfall, so "Passover" in the sense of the seder
    # night falls on the *evening* of the day before 15 Nisan in the Gregorian
    # calendar.  We subtract 1 day from pyluach's Gregorian date to match the
    # conventional display (the candle-lighting / celebration evening).

    def passover_evening(g_year):
        """Return (month_0indexed, day) for the Passover seder evening, or None."""
        try:
            h = heb_dates.HebrewDate(g_year + 3760, 1, 15)  # 15 Nisan
            g = h.to_greg()
            d = datetime.date(g.year, g.month, g.day) - datetime.timedelta(days=1)
            return d.month - 1, d.day
        except Exception:
            return None

    def hanukkah_evening(g_year):
        """Return (month_0indexed, day) for the first Hanukkah candle, or None."""
        try:
            h = heb_dates.HebrewDate(g_year + 3761, 9, 25)  # 25 Kislev
            g = h.to_greg()
            d = datetime.date(g.year, g.month, g.day) - datetime.timedelta(days=1)
            return d.month - 1, d.day
        except Exception:
            return None

    # ── Islamic calendar ──────────────────────────────────────────────────────
    # Primary: hijridate (Umm al-Qura calendar, Saudi Arabia official calendar).
    #   Supported range: Hijri 1343–1500 AH ≈ Gregorian 1924–2077 CE.
    # Fallback: pure tabular algorithm for years outside hijridate's range.
    # Either way, dates are approximate (±1–2 days from regional moon sighting).

    from hijridate import Hijri as HijriDate

    def tabular_to_date(y, m, d):
        """Tabular Islamic calendar (astronomical epoch) → datetime.date."""
        jdn = (d
               + math.ceil(29.5 * (m - 1))
               + (y - 1) * 354
               + (11 * y + 3) // 30
               + 1948438)
        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
        dd = (4 * c + 3) // 1461
        e = c - (1461 * dd) // 4
        mm = (5 * e + 2) // 153
        day_ = e - (153 * mm + 2) // 5 + 1
        month_ = mm + 3 - 12 * (mm // 10)
        year_ = 100 * b + dd - 4800 + mm // 10
        return datetime.date(year_, month_, day_)

    # hijridate's supported Hijri range
    HIJRIDATE_H_MIN = 1343
    HIJRIDATE_H_MAX = 1500

    def hijri_event(h, hijri_month, hijri_day):
        """Convert a Hijri date to datetime.date, using hijridate or tabular."""
        if HIJRIDATE_H_MIN <= h <= HIJRIDATE_H_MAX:
            g = HijriDate(h, hijri_month, hijri_day).to_gregorian()
            return datetime.date(g.year, g.month, g.day)
        return tabular_to_date(h, hijri_month, hijri_day)

    def islamic_events_for_year(g_year):
        """Return (ram, fitr, adha) as datetime.date objects for g_year, or Nones."""
        h_approx = int((g_year - 622) * 1.030685)
        for h in range(h_approx - 1, h_approx + 2):
            if h < 1:
                continue
            ram = hijri_event(h, 9, 1)
            if ram.year == g_year:
                fitr = hijri_event(h, 10, 1)
                adha = hijri_event(h, 12, 10)
                return ram, fitr, adha
        return None, None, None

    # ── Build JS table strings ────────────────────────────────────────────────

    def fmt_md(d):
        """Format a date as JS [year, month0, day] array literal."""
        return f"[{d.year},{d.month - 1},{d.day}]"

    passover_rows, hanukkah_rows, islamic_rows = [], [], []

    for g_year in range(HEBREW_YEAR_START, YEAR_END + 1):
        p = passover_evening(g_year)
        if p:
            passover_rows.append(f"  {g_year}:[{p[0]},{p[1]}]")

        h = hanukkah_evening(g_year)
        if h:
            hanukkah_rows.append(f"  {g_year}:[{h[0]},{h[1]}]")

    for g_year in range(ISLAMIC_YEAR_START, YEAR_END + 1):
        ram, fitr, adha = islamic_events_for_year(g_year)
        if ram:
            islamic_rows.append(
                f"  {g_year}:{{ram:{fmt_md(ram)},fitr:{fmt_md(fitr)},adha:{fmt_md(adha)}}}"
            )

    js_lines = [
        "// festival-data.js — generated by build.py. Do not edit manually.",
        f"// Hebrew: pyluach, {HEBREW_YEAR_START} CE – {YEAR_END} CE.",
        f"// Islamic: hijridate (Umm al-Qura, 1924–2077 CE) with tabular fallback;",
        f"// covers {ISLAMIC_YEAR_START}–{YEAR_END} CE. Dates are approximate (±1–2 days).",
        "// Hebrew sunset convention: date shown is when the holiday begins",
        "// at nightfall (one day before the Hebrew calendar date).",
        "",
        "// Passover seder evening (15 Nisan). Format: [month_0indexed, day].",
        "const PASSOVER_GY = {",
        ",\n".join(passover_rows),
        "};",
        "",
        "// Hanukkah first candle (25 Kislev). Format: [month_0indexed, day].",
        "const HANUKKAH_GY = {",
        ",\n".join(hanukkah_rows),
        "};",
        "",
        "// Islamic events keyed by Gregorian year of 1 Ramadan.",
        "// Each field stores [absolute_year, month_0indexed, day] so dates that",
        "// spill into the next Gregorian year are represented correctly.",
        "const ISLAMIC_GY = {",
        ",\n".join(islamic_rows),
        "};",
        "",
    ]
    js = "\n".join(js_lines)

    js_path = static_dst / "js" / "festival-data.js"
    js_path.parent.mkdir(parents=True, exist_ok=True)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)

    print(f"  {len(passover_rows)} Passovers ({HEBREW_YEAR_START}–{YEAR_END}),"
          f" {len(hanukkah_rows)} Hanukkah, {len(islamic_rows)} Islamic years"
          f" ({ISLAMIC_YEAR_START}–{YEAR_END})")


# ── Build Functions ────────────────────────────────────────────────────────

def build_site():
    """Main build function."""
    translations = load_translations()
    glossary = load_glossary()
    chapters = load_chapters()
    weekday_names = load_weekday_names()
    wiki_pages = load_wiki_pages()
    fudoki_divisions = load_fudoki_data()
    today = date.today()
    gaian_today = gregorian_to_gaian(today)
    iso_weekday = today.isoweekday()  # Mon=1..Sun=7
    gaian_today_doy = day_of_year(gaian_today["month"], gaian_today["day"])
    daily_reading_chapter = gaian_today_doy if gaian_today_doy <= 364 else None

    print(f"Loaded {len(chapters)} Gaiad chapters, {len(wiki_pages)} wiki pages")

    # Pre-extract wiki content for day pages
    day_wiki_content = {}  # key: (month_id, day_num) -> {"intro": ..., "overview": ...}
    month_wiki_content = {}  # key: month_id -> {"intro": ..., "overview": ...}

    for title, wikitext in wiki_pages.items():
        # Day pages: "Sagittarius 1", "Capricorn 15", etc.
        day_match = re.match(r'^(\w+)\s+(\d+)$', title)
        if day_match:
            wiki_month = day_match.group(1)
            wiki_day = int(day_match.group(2))
            month_id = WIKI_MONTH_TO_ID.get(wiki_month)
            if month_id:
                day_wiki_content[(month_id, wiki_day)] = {
                    "intro": extract_wiki_intro(wikitext),
                    "overview": extract_wiki_overview(wikitext),
                }
            continue
        # Month pages: "Sagittarius", "Capricorn", etc.
        if title in WIKI_MONTH_TO_ID:
            month_id = WIKI_MONTH_TO_ID[title]
            month_wiki_content[month_id] = {
                "intro": extract_wiki_intro(wikitext),
                "overview": extract_wiki_overview(wikitext),
            }

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    # Custom Jinja2 filters for Hallowings pages
    def format_number(value):
        """Format integer with comma separators, or em-dash for None."""
        if value is None:
            return "\u2014"
        return f"{int(value):,}"

    def format_area(value):
        """Format area with comma separators + km², or em-dash for None."""
        if value is None:
            return "\u2014"
        return f"{value:,.0f} km\u00b2"

    def wikimedia_thumb(filename, width=300):
        """Return Wikimedia Commons thumbnail URL for a filename."""
        if not filename:
            return ""
        encoded = urllib.parse.quote(filename.replace(" ", "_"), safe="/:+")
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width={width}"

    if md is None:
        print(
            "WARNING: markdown package not found; using plain paragraph fallback for simple_md. "
            "Install with: pip install markdown"
        )

    def simple_md(text):
        """Convert markdown text to HTML, with a safe plain-text fallback."""
        if not text:
            return ""
        if md is not None:
            return Markup(md.markdown(text, extensions=["tables"]))

        def fmt_inline(s):
            s = escape(s)
            s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
            s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
            s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
            return s

        html = []
        in_list = False
        paragraph = []

        def flush_paragraph():
            nonlocal paragraph
            if paragraph:
                html.append(f"<p>{' '.join(paragraph)}</p>")
                paragraph = []

        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                flush_paragraph()
                if in_list:
                    html.append("</ul>")
                    in_list = False
                continue

            heading = re.match(r"^(#{1,6})\s+(.*)$", line)
            if heading:
                flush_paragraph()
                if in_list:
                    html.append("</ul>")
                    in_list = False
                level = len(heading.group(1))
                html.append(f"<h{level}>{fmt_inline(heading.group(2))}</h{level}>")
                continue

            bullet = re.match(r"^[-*]\s+(.*)$", line)
            if bullet:
                flush_paragraph()
                if not in_list:
                    html.append("<ul>")
                    in_list = True
                html.append(f"<li>{fmt_inline(bullet.group(1))}</li>")
                continue

            paragraph.append(fmt_inline(line))

        flush_paragraph()
        if in_list:
            html.append("</ul>")

        return Markup("".join(html))

    env.filters["simple_md"] = simple_md
    env.filters["format_number"] = format_number
    env.filters["format_area"] = format_area
    env.filters["wikimedia_thumb"] = wikimedia_thumb

    # Clean output (build into a temp dir, then swap in)
    if SITE_TMP_DIR.exists():
        shutil.rmtree(SITE_TMP_DIR, ignore_errors=True)
    SITE_TMP_DIR.mkdir(parents=True, exist_ok=True)

    # Copy static assets
    static_src = SCRIPT_DIR / "static"
    static_dst = SITE_TMP_DIR / "static"
    if static_src.exists():
        shutil.copytree(static_src, static_dst)
    else:
        static_dst.mkdir(parents=True, exist_ok=True)

    # Generate computed festival data (Hebrew + Islamic) into static/js/
    print("Generating festival-data.js...")
    generate_festival_data_js(static_dst)

    # Write shrine data as static JSON for the map
    print("Writing shrines.json...")
    shrine_data = load_shrine_data()
    print(f"  {len(shrine_data)} shrines with coordinates")
    with open(static_dst / "shrines.json", "w", encoding="utf-8") as f:
        json.dump(shrine_data, f, ensure_ascii=False, separators=(",", ":"))

    # Write compact realm index for the "Your Sacred Land" location widget
    if fudoki_divisions:
        print("Writing realms-index.json...")
        realms_index = [
            {
                "qid": r["qid"],
                "realm_name": r.get("realm_name", r.get("name", "")),
                "country": r.get("country", ""),
                "geoshape": r.get("geoshape", ""),
                "slug": r.get("slug") or r["qid"],
                "good_fudoki": bool(r.get("good_fudoki")),
                "names": r.get("names", {}),
                "realm_names": r.get("realm_names", {}),
            }
            for r in fudoki_divisions
            if r.get("geoshape")
        ]
        with open(static_dst / "realms-index.json", "w", encoding="utf-8") as f:
            json.dump(realms_index, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  {len(realms_index)} realms with geoshapes indexed")

    # Pre-compute base paths for language switcher
    lang_bases = {l: lang_base(l) for l in translations}

    # Build for each language
    for lang, t in translations.items():
        print(f"Building {lang}...")
        # English pages live at root; other languages get a subdirectory
        if lang == DEFAULT_LANG:
            lang_dir = SITE_TMP_DIR
        else:
            lang_dir = SITE_TMP_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        # Preferred weekday display names (ritual/restored forms) per language.
        preferred_weekday_names = []
        for wd in WEEKDAYS:
            entry = (weekday_names.get(wd["id"], {}) or {}).get(lang, {})
            name = entry.get("preferred") or entry.get("common")
            # fallback to translation file if weekday-names is incomplete
            if not name:
                try:
                    name = t.get("weekdays", [])[wd["num"] - 1]
                except Exception:
                    name = wd["id"].title()
            preferred_weekday_names.append(name)

        gaian_today_html = build_gaian_date_html(lang, t, gaian_today, iso_weekday, preferred_weekday_names)

        base = lang_base(lang)
        ctx = {
            "lang": lang,
            "base": base,
            "lang_bases": lang_bases,
            "t": t,
            "g": glossary.get(lang, {}),
            "months": MONTHS,
            "elements": ELEMENT_THEMES,
            "weekdays_data": WEEKDAYS,
            "preferred_weekday_names": preferred_weekday_names,
            "gaian_today": gaian_today,
            "gaian_today_html": gaian_today_html,
            "iso_weekday": iso_weekday,
            "daily_reading_chapter": daily_reading_chapter,
            "today_gregorian": format_gregorian(today, lang),
            "rtl": lang in ("ar", "he"),
            "languages": list(translations.keys()),
            "is_cjk": lang in ("ja", "zh"),
        }

        # ── Homepage ──
        render_page(env, "index.html", lang_dir / "index.html", ctx)

        # ── Calendar section ──
        cal_dir = lang_dir / "calendar"
        cal_dir.mkdir(parents=True, exist_ok=True)
        render_page(env, "calendar/index.html", cal_dir / "index.html", ctx)

        # Datepicker as directory with index.html
        dp_dir = cal_dir / "datepicker"
        dp_dir.mkdir(parents=True, exist_ok=True)
        render_page(env, "calendar/datepicker.html", dp_dir / "index.html", ctx)

        # Gaian Era as directory with index.html
        ge_dir = cal_dir / "gaian-era"
        ge_dir.mkdir(parents=True, exist_ok=True)
        render_page(env, "calendar/gaian-era.html", ge_dir / "index.html", ctx)

        # Year pages — canonical URL: /calendar/year/{gaian_year}/
        # Pre-generate current Gaian year ±10; all other years are served
        # dynamically via the 404.html client-side router.
        _today      = datetime.date.today()
        _iso_year   = _today.isocalendar()[0]  # ISO week-year
        _cur_gaian  = _iso_year + 10000
        YEAR_RANGE  = range(_cur_gaian - 10, _cur_gaian + 11)
        year_dir_root = cal_dir / "year"
        year_dir_root.mkdir(parents=True, exist_ok=True)
        for gaian_year in YEAR_RANGE:
            ydir = year_dir_root / str(gaian_year)
            ydir.mkdir(parents=True, exist_ok=True)
            render_page(env, "calendar/year.html", ydir / "index.html",
                        {**ctx, "display_year": gaian_year})
            fdir = ydir / "festivals"
            fdir.mkdir(parents=True, exist_ok=True)
            render_page(env, "calendar/year-festivals.html", fdir / "index.html",
                        {**ctx, "display_year": gaian_year})
            # Redirect old URL /{lang}/calendar/{year}/ → new canonical
            old_dir = cal_dir / str(gaian_year)
            old_dir.mkdir(parents=True, exist_ok=True)
            target = f"{base}/calendar/year/{gaian_year}/"
            (old_dir / "index.html").write_text(
                f'<!DOCTYPE html><html><head><meta charset="UTF-8">'
                f'<meta http-equiv="refresh" content="0; url={target}">'
                f'<script>window.location.replace({target!r});</script>'
                f'</head><body></body></html>', encoding="utf-8")

            # ── Year/month and year/day pages ──
            iso_year = gaian_year - 10000
            _dec28 = datetime.date(iso_year, 12, 28)
            _dow   = _dec28.isoweekday()
            _thu   = _dec28 + datetime.timedelta(days=4 - _dow)
            _jan1  = datetime.date(_thu.year, 1, 1)
            _wks   = ((_thu - _jan1).days + 7) // 7
            has_horus_ym = (_wks == 53)

            for m in MONTHS:
                if m["num"] == 14 and not has_horus_ym:
                    continue
                days_in_m = 7 if m["num"] == 14 else 28
                mdir = ydir / f"{m['num']:02d}"
                mdir.mkdir(parents=True, exist_ok=True)
                render_page(env, "calendar/year-month.html", mdir / "index.html",
                            {**ctx, "display_year": gaian_year,
                             "month_num": m["num"], "month_info": m,
                             "days_in_month_ym": days_in_m})
                for d in range(1, days_in_m + 1):
                    ddir = mdir / f"{d:02d}"
                    ddir.mkdir(parents=True, exist_ok=True)
                    render_page(env, "calendar/year-day.html", ddir / "index.html",
                                {**ctx, "display_year": gaian_year,
                                 "month_num": m["num"], "day_num": d,
                                 "month_info": m})

        # ── Weekday pages ──
        def week_redirect(target: str) -> str:
            return (f'<!DOCTYPE html><html><head><meta charset="UTF-8">'
                    f'<meta http-equiv="refresh" content="0; url={target}">'
                    f'<script>window.location.replace({target!r});</script>'
                    f'</head><body></body></html>')
        week_dir = cal_dir / "week"
        week_dir.mkdir(parents=True, exist_ok=True)
        render_page(env, "calendar/week-index.html", week_dir / "index.html", {**ctx})
        for wd in WEEKDAYS:
            # Canonical: /calendar/week/<num>/
            num_dir = week_dir / str(wd["num"])
            num_dir.mkdir(parents=True, exist_ok=True)
            render_page(env, "calendar/weekday.html", num_dir / "index.html", {**ctx, "weekday": wd})
            # Slug alias: /calendar/week/<id>/ → /calendar/week/<num>/
            wd_dir = week_dir / wd["id"]
            wd_dir.mkdir(parents=True, exist_ok=True)
            (wd_dir / "index.html").write_text(week_redirect(f"{base}/calendar/week/{wd['num']}/"), encoding="utf-8")

        # Shorthand /week/* redirects → /calendar/week/<num>/
        week_short_dir = lang_dir / "week"
        week_short_dir.mkdir(parents=True, exist_ok=True)
        (week_short_dir / "index.html").write_text(week_redirect(f"{base}/calendar/week/"), encoding="utf-8")
        for wd in WEEKDAYS:
            # /week/<num>/ → /calendar/week/<num>/
            num_dir = week_short_dir / str(wd["num"])
            num_dir.mkdir(parents=True, exist_ok=True)
            (num_dir / "index.html").write_text(week_redirect(f"{base}/calendar/week/{wd['num']}/"), encoding="utf-8")
            # /week/<id>/ → /calendar/week/<num>/
            wd_short_dir = week_short_dir / wd["id"]
            wd_short_dir.mkdir(parents=True, exist_ok=True)
            (wd_short_dir / "index.html").write_text(week_redirect(f"{base}/calendar/week/{wd['num']}/"), encoding="utf-8")

        # Helper for simple meta-refresh redirects
        def cal_redirect(target: str) -> str:
            return (
                f'<!DOCTYPE html><html><head><meta charset="UTF-8">'
                f'<meta http-equiv="refresh" content="0; url={target}">'
                f'<script>window.location.replace({target!r});</script>'
                f'</head><body></body></html>'
            )

        # ── Month pages ──
        # Canonical URL: /calendar/{MM}/   e.g. /calendar/02/
        # Redirect from: /calendar/{name}/ e.g. /calendar/capricorn/
        for m in MONTHS:
            month_num_str = f"{m['num']:02d}"
            month_dir = cal_dir / month_num_str   # canonical numeric directory
            month_dir.mkdir(parents=True, exist_ok=True)
            days_in_month = 7 if m["num"] == 14 else 28
            wiki_month = month_wiki_content.get(m["id"], {})
            theme = MONTH_THEMES.get(m["id"])
            month_ctx = {
                **ctx,
                "month": m,
                "month_display_name": t["months"].get(m["id"], m["id"].title()),
                "days_in_month": days_in_month,
                "element": ELEMENT_THEMES[m["element"]],
                "wiki_intro": wiki_month.get("intro"),
                "wiki_overview": wiki_month.get("overview"),
                "month_theme_title": theme[0] if theme else None,
                "month_theme_desc": theme[1] if theme else None,
            }
            render_page(env, "calendar/month.html", month_dir / "index.html", month_ctx)

            # Name-based redirect: /calendar/{name}/ → /calendar/{MM}/
            name_month_dir = cal_dir / m["id"]
            name_month_dir.mkdir(parents=True, exist_ok=True)
            (name_month_dir / "index.html").write_text(
                cal_redirect(f"{base}/calendar/{month_num_str}/"), encoding="utf-8")

            # Day pages
            for d in range(1, days_in_month + 1):
                day_dir = month_dir / f"{d:02d}"
                day_dir.mkdir(parents=True, exist_ok=True)
                doy = day_of_year(m["num"], d)
                wiki_day = day_wiki_content.get((m["id"], d), {})
                day_ctx = {
                    **month_ctx,
                    "day_num": d,
                    "day_of_year": doy,
                    "chapter_num": doy if doy <= 364 else None,
                    "has_chapter": doy in chapters if doy <= 364 else False,
                    "weekday_num": ((d - 1) % 7) + 1,
                    "weekday_data": WEEKDAYS[((d - 1) % 7)],
                    "wiki_day_intro": wiki_day.get("intro"),
                    "wiki_day_overview": wiki_day.get("overview"),
                }
                render_page(env, "calendar/day.html", day_dir / "index.html", day_ctx)

                # Name-based day redirect: /calendar/{name}/{dd}/ → /calendar/{MM}/{dd}/
                name_day_dir = name_month_dir / f"{d:02d}"
                name_day_dir.mkdir(parents=True, exist_ok=True)
                (name_day_dir / "index.html").write_text(
                    cal_redirect(f"{base}/calendar/{month_num_str}/{d:02d}/"), encoding="utf-8")

        # ── Gaiad Scripture ──
        gaiad_dir = lang_dir / "gaiad"
        gaiad_dir.mkdir(parents=True, exist_ok=True)
        render_page(env, "gaiad/index.html", gaiad_dir / "index.html",
                    {**ctx, "chapters": chapters})

        for ch_num in range(1, 365):
            ch_dir = gaiad_dir / f"{ch_num:03d}"
            ch_dir.mkdir(parents=True, exist_ok=True)
            ch_month = ((ch_num - 1) // 28) + 1
            ch_day = ((ch_num - 1) % 28) + 1
            ch_ctx = {
                **ctx,
                "chapter_num": ch_num,
                "chapter_text": chapters.get(ch_num, None),
                "chapter_month": MONTHS[ch_month - 1] if ch_month <= 14 else None,
                "chapter_day": ch_day,
                "prev_chapter": ch_num - 1 if ch_num > 1 else None,
                "next_chapter": ch_num + 1 if ch_num < 364 else None,
            }
            render_page(env, "gaiad/chapter.html", ch_dir / "index.html", ch_ctx)

        # ── Section pages ──
        for section in ["scripture", "mythology", "philosophy", "shrines", "longevity", "evolution"]:
            sec_dir = lang_dir / section
            sec_dir.mkdir(parents=True, exist_ok=True)
            render_page(env, f"sections/{section}.html", sec_dir / "index.html", ctx)

        # ── Fudoki / Hallowings pages (English only for now) ──
        if lang == "en" and fudoki_divisions:
            fudoki_dir = lang_dir / "fudoki"
            fudoki_dir.mkdir(parents=True, exist_ok=True)
            good_fudoki_realms = [r for r in fudoki_divisions if r.get("good_fudoki")]
            render_page(env, "sections/fudoki.html", fudoki_dir / "index.html",
                        {**ctx, "realms": good_fudoki_realms})

            root_map_dir = lang_dir / "map"
            root_map_dir.mkdir(parents=True, exist_ok=True)
            render_page(env, "sections/fudoki-map.html", root_map_dir / "index.html",
                        {**ctx, "realms": fudoki_divisions})

            map_dir = fudoki_dir / "map"
            map_dir.mkdir(parents=True, exist_ok=True)
            # Keep legacy URL working, but make /map/ canonical.
            (map_dir / "index.html").write_text(
                "<!doctype html><html><head>"
                "<meta charset='utf-8'>"
                "<meta http-equiv='refresh' content='0; url=/map/'>"
                "<script>window.location.replace('/map/');</script>"
                "</head><body>Redirecting to <a href='/map/'>/map/</a>...</body></html>",
                encoding="utf-8",
            )
            for realm in fudoki_divisions:
                realm_dir = fudoki_dir / (realm.get("slug") or realm["qid"])
                realm_dir.mkdir(parents=True, exist_ok=True)
                render_page(env, "sections/fudoki-detail.html", realm_dir / "index.html",
                            {**ctx, "realm": realm})

    # English homepage is the site root (no separate language selector page needed).

    # ── Wiki Redirects ──
    print("Generating wiki redirects...")
    # Note: generate_wiki_redirects writes into SITE_DIR; temporarily point it at temp.
    global SITE_DIR
    original_site_dir = SITE_DIR
    SITE_DIR = SITE_TMP_DIR
    try:
        generate_wiki_redirects(wiki_pages, list(translations.keys()))
    finally:
        SITE_DIR = original_site_dir

    # Generate iCal files (language-agnostic, root-level)
    print("\nGenerating iCal files...")
    generate_ical_files(SITE_TMP_DIR)

    # Write CNAME for GitHub Pages custom domain
    (SITE_TMP_DIR / "CNAME").write_text("order.life\n")

    # Write custom 404 page for GitHub Pages
    shutil.copy(TEMPLATES_DIR / "404.html", SITE_TMP_DIR / "404.html")

    # Swap temp build into place
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR, ignore_errors=True)
    shutil.move(str(SITE_TMP_DIR), str(SITE_DIR))

    print(f"\nBuild complete! Output in {SITE_DIR}")
    total = sum(1 for _ in SITE_DIR.rglob("*.html"))
    print(f"Total HTML pages generated: {total}")


def render_page(env, template_name, output_path, context):
    """Render a Jinja2 template to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if "lang" in context and "path_suffix" not in context:
            # Compute language-switcher path suffix from the output path.
            # NOTE: we build into SITE_TMP_DIR and later swap to SITE_DIR, so the
            # output may not live under SITE_DIR at render time.
            lang = context["lang"]
            if lang == DEFAULT_LANG:
                lang_root_candidates = [SITE_DIR, SITE_TMP_DIR]
            else:
                lang_root_candidates = [
                    SITE_DIR / lang,
                    SITE_TMP_DIR / lang,
                ]
            for lang_root in lang_root_candidates:
                try:
                    rel = output_path.relative_to(lang_root)
                except ValueError:
                    continue

                if rel.name == "index.html":
                    parent = rel.parent.as_posix()
                    if parent == ".":
                        path_suffix = "/"
                    else:
                        path_suffix = "/" + parent.strip("/") + "/"
                else:
                    path_suffix = "/" + rel.as_posix()

                context = {**context, "path_suffix": path_suffix}
                break
        template = env.get_template(template_name)
        html = template.render(**context)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"  ERROR rendering {template_name}: {e}")


if __name__ == "__main__":
    build_site()
