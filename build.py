#!/usr/bin/env python
"""
order.life FastSite Builder
Generates static HTML for all languages and pages of the Lifeism website.
Uses Jinja2 templates, outputs to site/{lang}/ directories.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import date

# Use the correct Python with packages
SCRIPT_DIR = Path(__file__).parent
SITE_DIR = SCRIPT_DIR / "site"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
CONTENT_DIR = SCRIPT_DIR / "content"
EPIC_DIR = SCRIPT_DIR / "epic"

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("ERROR: jinja2 not found. Install with: pip install jinja2")
    sys.exit(1)

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
    {"num": 14, "id": "horus",       "symbol": "\U00013143", "element": "intercalary"},
]

ELEMENT_THEMES = {
    "fire": {"color": "#ff6b35", "desc_key": "element_fire"},
    "earth": {"color": "#4a7c59", "desc_key": "element_earth"},
    "air": {"color": "#5b9bd5", "desc_key": "element_air"},
    "water": {"color": "#2e86ab", "desc_key": "element_water"},
    "healing": {"color": "#9b59b6", "desc_key": "element_healing"},
    "intercalary": {"color": "#8a2be2", "desc_key": "element_intercalary"},
}

# ── Translation Data ───────────────────────────────────────────────────────

def load_translations():
    """Load all translation files from content/i18n/"""
    translations = {}
    i18n_dir = CONTENT_DIR / "i18n"
    for lang_file in i18n_dir.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)
    return translations


# ── Chapter Loading ────────────────────────────────────────────────────────

def load_chapters():
    """Load Gaiad epic chapters from epic/ directory."""
    chapters = {}
    for i in range(1, 365):
        chapter_file = EPIC_DIR / f"chapter_{i:03d}.md"
        if chapter_file.exists():
            with open(chapter_file, "r", encoding="utf-8") as f:
                raw = f.read()
                # Strip {{c|...}} wiki markup to just the text inside
                import re
                clean = re.sub(r'\{\{c\|([^}]*)\}\}', r'\1', raw)
                chapters[i] = clean
    return chapters


# ── Gaian Date Computation ─────────────────────────────────────────────────

def iso_week_info(d):
    """Get ISO year and week number for a date."""
    iso_cal = d.isocalendar()
    return iso_cal[0], iso_cal[1], iso_cal[2]  # year, week, weekday(1=Mon)


def gregorian_to_gaian(d):
    """Convert a Gregorian date to Gaian calendar date."""
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
    """Get the day-of-year number (1-371) from month and day."""
    if month_num <= 13:
        return (month_num - 1) * 28 + day_in_month
    else:  # Horus
        return 364 + day_in_month


# ── Build Functions ────────────────────────────────────────────────────────

def build_site():
    """Main build function."""
    translations = load_translations()
    chapters = load_chapters()
    today = date.today()
    gaian_today = gregorian_to_gaian(today)

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    # Clean output
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # Copy static assets
    static_src = SCRIPT_DIR / "static"
    static_dst = SITE_DIR / "static"
    if static_src.exists():
        shutil.copytree(static_src, static_dst)

    # Build for each language
    for lang, t in translations.items():
        print(f"Building {lang}...")
        lang_dir = SITE_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        ctx = {
            "lang": lang,
            "t": t,
            "months": MONTHS,
            "elements": ELEMENT_THEMES,
            "gaian_today": gaian_today,
            "today_gregorian": today.strftime("%B %d, %Y"),
            "rtl": lang == "ar",
            "languages": list(translations.keys()),
            "month_name": lambda m, tr=t: tr["months"].get(MONTHS[m-1]["id"], MONTHS[m-1]["id"].title()),
        }

        # ── Homepage ──
        render_page(env, "index.html", lang_dir / "index.html", ctx)

        # ── Calendar section ──
        cal_dir = lang_dir / "calendar"
        cal_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/index.html", cal_dir / "index.html", ctx)
        render_page(env, "calendar/datepicker.html", cal_dir / "datepicker.html", ctx)
        render_page(env, "calendar/gaian-era.html", cal_dir / "gaian-era.html", ctx)

        # Year page (just 12026 for now)
        year_dir = cal_dir / "12026"
        year_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/year.html", year_dir / "index.html",
                    {**ctx, "display_year": 12026})

        # Month pages
        for m in MONTHS:
            month_dir = cal_dir / m["id"]
            month_dir.mkdir(exist_ok=True)
            days_in_month = 7 if m["num"] == 14 else 28
            month_ctx = {
                **ctx,
                "month": m,
                "month_display_name": t["months"].get(m["id"], m["id"].title()),
                "days_in_month": days_in_month,
                "element": ELEMENT_THEMES[m["element"]],
            }
            render_page(env, "calendar/month.html", month_dir / "index.html", month_ctx)

            # Day pages
            for d in range(1, days_in_month + 1):
                day_dir = month_dir / f"{d:02d}"
                day_dir.mkdir(exist_ok=True)
                doy = day_of_year(m["num"], d)
                chapter_text = chapters.get(doy, None)
                day_ctx = {
                    **month_ctx,
                    "day_num": d,
                    "day_of_year": doy,
                    "chapter_num": doy if doy <= 364 else None,
                    "chapter_text": chapter_text,
                    "weekday_num": ((d - 1) % 7) + 1,
                }
                render_page(env, "calendar/day.html", day_dir / "index.html", day_ctx)

        # ── Gaiad Scripture ──
        gaiad_dir = lang_dir / "gaiad"
        gaiad_dir.mkdir(exist_ok=True)
        render_page(env, "gaiad/index.html", gaiad_dir / "index.html",
                    {**ctx, "chapters": chapters})

        for ch_num in range(1, 365):
            ch_dir = gaiad_dir / f"{ch_num:03d}"
            ch_dir.mkdir(exist_ok=True)
            # Find which month/day this chapter corresponds to
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
            sec_dir.mkdir(exist_ok=True)
            render_page(env, f"sections/{section}.html", sec_dir / "index.html", ctx)

    # ── Root index (language selector) ──
    render_page(env, "root.html", SITE_DIR / "index.html",
                {"languages": list(translations.keys()), "translations": translations})

    # ── Redirects ──
    # /wiki/* -> lifeism.miraheze.org
    render_page(env, "wiki-redirect.html", SITE_DIR / "wiki" / "index.html", {})

    print(f"\nBuild complete! Output in {SITE_DIR}")
    total = sum(1 for _ in SITE_DIR.rglob("*.html"))
    print(f"Total HTML pages generated: {total}")


def render_page(env, template_name, output_path, context):
    """Render a Jinja2 template to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        template = env.get_template(template_name)
        html = template.render(**context)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"  ERROR rendering {template_name}: {e}")


if __name__ == "__main__":
    build_site()
