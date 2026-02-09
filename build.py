#!/usr/bin/env python
"""
order.life FastSite Builder
Generates static HTML for all languages and pages of the Lifeism website.
Uses Jinja2 templates, outputs to site/{lang}/ directories.
"""

import io
import os
import re
import sys
import json
import shutil
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

WEEKDAYS = [
    {"num": 1, "id": "monday",    "planet": "Moon",    "symbol": "\u263D"},
    {"num": 2, "id": "tuesday",   "planet": "Mars",    "symbol": "\u2642"},
    {"num": 3, "id": "wednesday", "planet": "Mercury", "symbol": "\u263F"},
    {"num": 4, "id": "thursday",  "planet": "Jupiter", "symbol": "\u2643"},
    {"num": 5, "id": "friday",    "planet": "Venus",   "symbol": "\u2640"},
    {"num": 6, "id": "saturday",  "planet": "Saturn",  "symbol": "\u2644"},
    {"num": 7, "id": "sunday",    "planet": "Sun",     "symbol": "\u2609"},
]


# ── Data Loading ──────────────────────────────────────────────────────────

def load_translations():
    """Load all translation files from content/i18n/"""
    translations = {}
    i18n_dir = CONTENT_DIR / "i18n"
    for lang_file in i18n_dir.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)
    return translations


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
    xml_file = SCRIPT_DIR / "Evolutionism+Wiki-20260209181520.xml"
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


# ── Wiki Redirect Generator ───────────────────────────────────────────────

def generate_wiki_redirects(wiki_pages, languages):
    """Generate static redirect pages for /{lang}/wiki/* and /wiki/*.

    Note: for now *all* languages redirect to the same Evolutionism Miraheze wiki
    (no lang: prefix), per project intent.
    """

    redirect_template = """<!DOCTYPE html>
<html><head><meta charset=\"UTF-8\">
<title>Redirecting...</title>
<meta http-equiv=\"refresh\" content=\"0; url={target}\">
<script>window.location.href='{target}';</script>
</head><body style=\"background:#0f0f1a;color:#e0e0e0;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;\">
<p>Redirecting to <a href=\"{target}\" style=\"color:#ffd700;\">Wiki: {title}</a>...</p>
</body></html>"""

    def target_for(title: str) -> str:
        safe_title = title.replace(" ", "_")
        return f"https://evolutionism.miraheze.org/wiki/{safe_title}"

    def write_wiki_tree(wiki_dir: Path, js_prefix_regex: str):
        wiki_dir.mkdir(parents=True, exist_ok=True)

        # Main_Page redirect
        main_page_dir = wiki_dir / "Main_Page"
        main_page_dir.mkdir(exist_ok=True)
        (main_page_dir / "index.html").write_text(
            redirect_template.format(title="Main Page", target=target_for("Main_Page")),
            encoding="utf-8",
        )

        # Known wiki pages
        for title in wiki_pages:
            safe_title = title.replace(" ", "_")
            page_dir = wiki_dir / safe_title
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_text(
                redirect_template.format(title=title, target=target_for(title)),
                encoding="utf-8",
            )

        # Fallback index with JS redirect for unknown pages
        (wiki_dir / "index.html").write_text(
            f"""<!DOCTYPE html>
<html><head><meta charset=\"UTF-8\"><title>Redirecting to Wiki...</title>
<script>
var path = window.location.pathname.replace({js_prefix_regex}, '').replace(/\\/$/, '');
if (!path) path = 'Main_Page';
var target = 'https://evolutionism.miraheze.org/wiki/' + (path);
window.location.href = target;
</script>
<noscript><meta http-equiv=\"refresh\" content=\"0; url={target_for('Main_Page')}\"></noscript>
</head><body style=\"background:#0f0f1a;color:#e0e0e0;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;\">
<p>Redirecting to <a href=\"{target_for('Main_Page')}\" style=\"color:#ffd700;\">Evolutionism Wiki</a>...</p>
</body></html>""",
            encoding="utf-8",
        )

    # Per-language wiki paths: /{lang}/wiki/...
    for lang in languages:
        write_wiki_tree(SITE_DIR / lang / "wiki", js_prefix_regex=rf"/^\\/{lang}\\/wiki\\/?/")

    # Root wiki paths: /wiki/...
    write_wiki_tree(SITE_DIR / "wiki", js_prefix_regex=r"/^\\/wiki\\/?/")


# ── Build Functions ────────────────────────────────────────────────────────

def build_site():
    """Main build function."""
    translations = load_translations()
    chapters = load_chapters()
    wiki_pages = load_wiki_pages()
    today = date.today()
    gaian_today = gregorian_to_gaian(today)

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
            "weekdays_data": WEEKDAYS,
            "gaian_today": gaian_today,
            "today_gregorian": today.strftime("%B %d, %Y"),
            "rtl": lang == "ar",
            "languages": list(translations.keys()),
            "is_cjk": lang in ("ja", "zh"),
        }

        # ── Homepage ──
        render_page(env, "index.html", lang_dir / "index.html", ctx)

        # ── Calendar section ──
        cal_dir = lang_dir / "calendar"
        cal_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/index.html", cal_dir / "index.html", ctx)

        # Datepicker as directory with index.html
        dp_dir = cal_dir / "datepicker"
        dp_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/datepicker.html", dp_dir / "index.html", ctx)

        # Gaian Era as directory with index.html
        ge_dir = cal_dir / "gaian-era"
        ge_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/gaian-era.html", ge_dir / "index.html", ctx)

        # Year page
        year_dir = cal_dir / "12026"
        year_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/year.html", year_dir / "index.html",
                    {**ctx, "display_year": 12026})

        # ── Weekday pages ──
        week_dir = cal_dir / "week"
        week_dir.mkdir(exist_ok=True)
        render_page(env, "calendar/week-index.html", week_dir / "index.html",
                    {**ctx})
        for wd in WEEKDAYS:
            wd_dir = week_dir / wd["id"]
            wd_dir.mkdir(exist_ok=True)
            render_page(env, "calendar/weekday.html", wd_dir / "index.html",
                        {**ctx, "weekday": wd})

        # ── Month pages ──
        for m in MONTHS:
            month_dir = cal_dir / m["id"]
            month_dir.mkdir(exist_ok=True)
            days_in_month = 7 if m["num"] == 14 else 28
            wiki_month = month_wiki_content.get(m["id"], {})
            month_ctx = {
                **ctx,
                "month": m,
                "month_display_name": t["months"].get(m["id"], m["id"].title()),
                "days_in_month": days_in_month,
                "element": ELEMENT_THEMES[m["element"]],
                "wiki_intro": wiki_month.get("intro"),
                "wiki_overview": wiki_month.get("overview"),
            }
            render_page(env, "calendar/month.html", month_dir / "index.html", month_ctx)

            # Day pages
            for d in range(1, days_in_month + 1):
                day_dir = month_dir / f"{d:02d}"
                day_dir.mkdir(exist_ok=True)
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

        # ── Gaiad Scripture ──
        gaiad_dir = lang_dir / "gaiad"
        gaiad_dir.mkdir(exist_ok=True)
        render_page(env, "gaiad/index.html", gaiad_dir / "index.html",
                    {**ctx, "chapters": chapters})

        for ch_num in range(1, 365):
            ch_dir = gaiad_dir / f"{ch_num:03d}"
            ch_dir.mkdir(exist_ok=True)
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

    # ── Wiki Redirects ──
    print("Generating wiki redirects...")
    generate_wiki_redirects(wiki_pages, list(translations.keys()))

    print(f"\nBuild complete! Output in {SITE_DIR}")
    total = sum(1 for _ in SITE_DIR.rglob("*.html"))
    print(f"Total HTML pages generated: {total}")


def render_page(env, template_name, output_path, context):
    """Render a Jinja2 template to a file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if "lang" in context and "path_suffix" not in context:
            try:
                rel = output_path.relative_to(SITE_DIR / context["lang"])
                if rel.name == "index.html":
                    parent = rel.parent.as_posix()
                    if parent == ".":
                        path_suffix = "/"
                    else:
                        path_suffix = "/" + parent.strip("/") + "/"
                else:
                    path_suffix = "/" + rel.as_posix()
                context = {**context, "path_suffix": path_suffix}
            except ValueError:
                pass
        template = env.get_template(template_name)
        html = template.render(**context)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"  ERROR rendering {template_name}: {e}")


if __name__ == "__main__":
    build_site()
