#!/usr/bin/env python3
"""
Generate a clean summary for ChatGPT based on actual notes files and proper structure.
Each chapter shows its zodiac position, date correspondence, and whether it has content.
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Zodiac sign mapping
ZODIAC_MAPPING = [
    ("SAGITTARIUS", 1, 28),
    ("CAPRICORN", 29, 56),
    ("AQUARIUS", 57, 84),
    ("PISCES", 85, 112),
    ("ARIES", 113, 140),
    ("TAURUS", 141, 168),
    ("GEMINI", 169, 196),
    ("CANCER", 197, 224),
    ("LEO", 225, 252),
    ("VIRGO", 253, 280),
    ("LIBRA", 281, 308),
    ("SCORPIO", 309, 336),
    ("OPHIUCHUS", 337, 364)
]

def get_zodiac_info(chapter_num):
    """Get zodiac sign and position for a chapter number."""
    for sign, start, end in ZODIAC_MAPPING:
        if start <= chapter_num <= end:
            position = chapter_num - start + 1
            return sign, position
    return "Unknown", 0

def get_date_info(chapter_num):
    """Get approximate date/period for a chapter based on anchor points."""
    # Key anchor points provided by user
    if 1 <= chapter_num <= 28:  # Sagittarius
        return "Cosmic creation, early universe"
    elif 29 <= chapter_num <= 56:  # Capricorn
        return "Early life, oceanic development"
    elif 57 <= chapter_num <= 84:  # Aquarius
        return "Life on land to Permian-Triassic extinction (~252 MYA)"
    elif 85 <= chapter_num <= 112:  # Pisces
        return "Mesozoic Era (~252-66 MYA)"
    elif chapter_num == 113:  # Aries 1
        return "Start of Cenozoic (~66 MYA, post-dinosaur extinction)"
    elif 113 <= chapter_num <= 224:  # Aries through Cancer
        return "Cenozoic to European conquest (~66 MYA to ~1511/1520 CE)"
    elif chapter_num == 224:  # Cancer 28
        return "European conquest of Cuba (~1511/1520 CE)"
    elif 225 <= chapter_num <= 252:  # Leo
        return "Indigenous Americas perspective (1492-1830 CE)"
    elif chapter_num == 253:  # Virgo 1
        return "Protestant Reformation start (~1517 CE)"
    elif 253 <= chapter_num <= 329:  # Virgo through Scorpio 21
        return "Protestant Reformation to WWII end (1517-1945 CE)"
    elif chapter_num == 329:  # Scorpio 21
        return "Japanese surrender, end of WWII (1945 CE)"
    elif 330 <= chapter_num <= 361:  # Scorpio 22 through Ophiuchus 25
        return "Contemporary history (1945-2026 CE)"
    elif chapter_num == 362:  # Ophiuchus 26
        return "End of year 2026 CE"
    elif 362 <= chapter_num <= 364:  # Final chapters
        return "Near future/speculative (2026+ CE)"
    else:
        return "Unknown period"

def check_notes_file(chapter_num, base_path):
    """Check if a notes file exists and get its title/content."""
    notes_path = Path(base_path) / "epic" / "notes" / f"chapter_{chapter_num:03d}_notes.md"

    if not notes_path.exists():
        return False, "No title", ""

    try:
        with open(notes_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from first few lines
        lines = content.split('\n')
        title = "Unknown Title"

        for line in lines[:5]:
            if line.startswith('#'):
                # Extract title after chapter number
                title_match = re.search(r'# Chapter \d+[:\s]*(.+?)(?:\s*-\s*Notes)?$', line)
                if title_match:
                    title = title_match.group(1).strip()
                    break

        return True, title, content

    except Exception as e:
        return False, f"Error: {e}", ""

def generate_chatgpt_summary(base_path):
    """Generate the complete summary for ChatGPT."""
    summary = []

    # Header
    summary.append("# Gaiad Epic - Complete Chapter Guide for ChatGPT")
    summary.append("")
    summary.append("364-chapter epic organized by zodiac calendar (13 signs × 28 chapters each).")
    summary.append("Each chapter shows: zodiac position, historical period, and content status.")
    summary.append("")

    # Legend
    summary.append("## Legend")
    summary.append("- ✅ **Has Content**: Chapter has detailed notes")
    summary.append("- ❌ **Empty**: Chapter planned but no content yet")
    summary.append("- 🔮 **Zodiac**: Astrological position (e.g., Sagittarius 15)")
    summary.append("- 📅 **Period**: Historical time/date correspondence")
    summary.append("")

    # Quick overview by section
    summary.append("## Section Overview")
    summary.append("")

    section_status = {
        "SAGITTARIUS (1-28)": "✅ Complete - Cosmic creation",
        "CAPRICORN (29-56)": "✅ Complete - Ocean life development",
        "AQUARIUS (57-84)": "🔄 Partial - Land life to Permian extinction",
        "PISCES (85-112)": "✅ Complete - Mesozoic Era",
        "ARIES-CANCER (113-224)": "❌ Empty - Cenozoic to 1520 CE",
        "LEO (225-252)": "✅ Complete - Indigenous Americas 1492-1830",
        "VIRGO-SCORPIO21 (253-329)": "❌ Empty - Reformation to WWII (1517-1945)",
        "SCORPIO22-OPHIUCHUS25 (330-361)": "❌ Empty - Contemporary (1945-2026)",
        "OPHIUCHUS26-28 (362-364)": "✅ Complete - Future/speculative"
    }

    for section, status in section_status.items():
        summary.append(f"- **{section}**: {status}")

    summary.append("")
    summary.append("---")
    summary.append("")

    # Process all chapters
    current_sign = ""

    for chapter_num in range(1, 365):
        sign, position = get_zodiac_info(chapter_num)
        date_info = get_date_info(chapter_num)
        has_content, title, content = check_notes_file(chapter_num, base_path)

        # Add section header when sign changes
        if sign != current_sign:
            current_sign = sign
            summary.append(f"# {sign}")
            summary.append("")

        # Chapter header
        status_icon = "✅" if has_content else "❌"
        zodiac_pos = f"{sign} {position}"

        summary.append(f"## {status_icon} Chapter {chapter_num}: {title} | **{zodiac_pos}**")
        summary.append("")
        summary.append(f"**🔮 Zodiac Position:** {zodiac_pos}")
        summary.append(f"**📅 Historical Period:** {date_info}")
        summary.append("")

        if has_content:
            summary.append("### 📝 Content Available:")
            summary.append("")
            # Add the full content
            for line in content.split('\n'):
                summary.append(line)
            summary.append("")
        else:
            summary.append("*No content available - chapter planned but not yet written*")
            summary.append("")

        summary.append("---")
        summary.append("")

    # Final statistics
    total_with_content = sum(1 for i in range(1, 365) if check_notes_file(i, base_path)[0])

    summary.append("# Summary Statistics")
    summary.append("")
    summary.append(f"- **Total Chapters**: 364")
    summary.append(f"- **Chapters with Content**: {total_with_content}")
    summary.append(f"- **Empty Chapters**: {364 - total_with_content}")
    summary.append(f"- **Completion Rate**: {total_with_content/364*100:.1f}%")

    return '\n'.join(summary)

if __name__ == "__main__":
    base_path = "C:/Users/Immanuelle/Documents/Github/Gaiad"
    summary = generate_chatgpt_summary(base_path)

    # Write the summary
    output_path = Path(base_path) / "CHATGPT_CHAPTER_GUIDE.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"ChatGPT guide generated: {output_path}")
    print(f"Total length: {len(summary)} characters")
    print(f"File size: {len(summary.encode('utf-8'))} bytes")