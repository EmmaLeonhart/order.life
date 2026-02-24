#!/usr/bin/env python3
"""
Generate a corrected markdown summary based on ACTUAL chapter notes files,
not the outdated comprehensive plan.
"""

import os
import re
from pathlib import Path

# Zodiac sign mapping based on 28-chapter cycles
ZODIAC_MAPPING = {
    (1, 28): "SAGITTARIUS",
    (29, 56): "CAPRICORN",
    (57, 84): "AQUARIUS",
    (85, 112): "PISCES",
    (113, 140): "ARIES",
    (141, 168): "TAURUS",
    (169, 196): "GEMINI",
    (197, 224): "CANCER",
    (225, 252): "LEO",
    (253, 329): "VIRGO/LIBRA/PART SCORPIO",
    (330, 361): "SCORPIO/OPHIUCHUS",
    (362, 364): "END OPHIUCHUS"
}

def get_zodiac_info(chapter_num):
    """Get zodiac sign and position for a chapter number."""
    for (start, end), sign in ZODIAC_MAPPING.items():
        if start <= chapter_num <= end:
            position = chapter_num - start + 1
            return sign, position, f"{start}-{end}"
    return "Unknown", 0, "Unknown"

def parse_notes_file(notes_file):
    """Parse a notes file to extract title and content."""
    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from first line or header
        lines = content.split('\n')
        title = "Unknown Title"

        for line in lines[:5]:  # Check first few lines
            if line.startswith('#'):
                # Remove markdown header marks and extract title
                title_match = re.search(r'# Chapter \d+[:\s]*(.+?)(?:\s*-\s*Notes)?$', line)
                if title_match:
                    title = title_match.group(1).strip()
                    break

        return title, content
    except Exception as e:
        return f"Error reading file", f"Error: {e}"

def scan_notes_files(base_path):
    """Scan all actual notes files and extract their information."""
    notes_path = Path(base_path) / "epic" / "notes"
    chapters = {}

    if not notes_path.exists():
        return chapters

    for notes_file in notes_path.glob("chapter_*_notes.md"):
        match = re.match(r'chapter_(\d+)_notes\.md', notes_file.name)
        if match:
            chapter_num = int(match.group(1))
            title, content = parse_notes_file(notes_file)
            sign, position, range_str = get_zodiac_info(chapter_num)

            chapters[chapter_num] = {
                'title': title,
                'content': content,
                'sign': sign,
                'position': position,
                'range': range_str,
                'file_path': notes_file
            }

    return chapters

def generate_summary(base_path):
    """Generate summary based on actual notes files."""
    chapters = scan_notes_files(base_path)

    summary = []
    summary.append("# Gaiad Epic - Corrected Chapter Summary (Based on Actual Notes)")
    summary.append("")
    summary.append("This summary is based on ACTUAL chapter notes files, not the outdated comprehensive plan.")
    summary.append("")

    # Legend
    summary.append("## Legend")
    summary.append("- 📝 **Chapter**: Based on actual notes content")
    summary.append("- 🔮 **Astrological**: Sign and position (e.g., Aquarius 6)")
    summary.append("- 📅 **Range**: Chapter range for each zodiac sign")
    summary.append("")

    # Zodiac index with actual chapters found
    summary.append("## 🔮 Zodiac Sign Index (Actual Chapters Found)")
    summary.append("")

    sign_chapters = {}
    for chapter_num, info in chapters.items():
        sign = info['sign']
        if sign not in sign_chapters:
            sign_chapters[sign] = []
        sign_chapters[sign].append(chapter_num)

    for sign in ZODIAC_MAPPING.values():
        if sign in sign_chapters:
            chapters_list = sorted(sign_chapters[sign])
            summary.append(f"- **{sign}**: {len(chapters_list)} chapters with notes ({min(chapters_list)}-{max(chapters_list)})")
        else:
            summary.append(f"- **{sign}**: No chapters with notes found")

    summary.append("")
    summary.append("---")
    summary.append("")

    # Process chapters in numerical order
    current_sign = ""

    for chapter_num in sorted(chapters.keys()):
        chapter = chapters[chapter_num]

        # Add section header if sign changed
        if chapter['sign'] != current_sign:
            current_sign = chapter['sign']
            summary.append(f"# {current_sign}")
            summary.append("")

        # Chapter header with proper astrological notation
        astrological_notation = f"{chapter['sign'].split('/')[0]} {chapter['position']}"
        summary.append(f"## 📝 Chapter {chapter_num}: {chapter['title']} | **{astrological_notation}**")
        summary.append("")

        # Astrological info
        summary.append(f"**🔮 Astrological Position:** {astrological_notation}")
        summary.append(f"**📅 Sign Range:** Chapters {chapter['range']}")
        summary.append("")

        # Full notes content
        summary.append("### 📝 Complete Notes Content:")
        summary.append("")
        for line in chapter['content'].split('\n'):
            summary.append(line)
        summary.append("")
        summary.append("---")
        summary.append("")

    # Statistics
    total_chapters_with_notes = len(chapters)
    total_expected = 364

    summary.append("# Summary Statistics")
    summary.append("")
    summary.append(f"- **Total Expected Chapters**: {total_expected}")
    summary.append(f"- **Chapters with Actual Notes**: {total_chapters_with_notes}")
    summary.append(f"- **Completion Rate**: {total_chapters_with_notes/total_expected*100:.1f}%")
    summary.append("")

    # Show which signs have notes
    summary.append("## Notes Coverage by Zodiac Sign")
    summary.append("")
    for sign in ZODIAC_MAPPING.values():
        if sign in sign_chapters:
            count = len(sign_chapters[sign])
            # Calculate expected chapters for this sign
            for (start, end), mapped_sign in ZODIAC_MAPPING.items():
                if mapped_sign == sign:
                    expected = end - start + 1
                    percentage = count/expected*100
                    summary.append(f"- **{sign}**: {count}/{expected} chapters ({percentage:.1f}%)")
                    break
        else:
            summary.append(f"- **{sign}**: 0 chapters")

    return '\n'.join(summary)

if __name__ == "__main__":
    base_path = "C:/Users/Immanuelle/Documents/Github/Gaiad"
    summary = generate_summary(base_path)

    # Write the corrected summary
    output_path = Path(base_path) / "CORRECTED_CHAPTER_SUMMARY.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Corrected summary generated: {output_path}")
    print(f"Total length: {len(summary)} characters")