#!/usr/bin/env python3
"""
Generate a comprehensive markdown summary of all chapters in the Gaiad Epic
with their notes status and content.
"""

import os
import re
from pathlib import Path

def extract_chapter_info_from_plan(plan_content):
    """Extract chapter information from the comprehensive plan."""
    chapters = {}
    current_section = ""
    current_sign = ""
    current_range = ""

    lines = plan_content.split('\n')
    for line in lines:
        # Check for section headers
        if line.startswith('## CHAPTERS'):
            current_section = line.strip()
            # Extract zodiac sign and chapter range
            match = re.match(r'## CHAPTERS (\d+-\d+) \(([^)]+)\) - (.+)', line)
            if match:
                current_range = match.group(1)
                current_sign = match.group(2)
        # Check for chapter definitions
        elif line.startswith('### Chapter'):
            match = re.match(r'### Chapter (\d+): (.+)', line)
            if match:
                chapter_num = int(match.group(1))
                chapter_title = match.group(2)
                chapters[chapter_num] = {
                    'title': chapter_title,
                    'section': current_section,
                    'sign': current_sign,
                    'range': current_range,
                    'description': ""
                }
        # Add description lines
        elif line.strip() and not line.startswith('#') and chapters:
            last_chapter = max(chapters.keys())
            if chapters[last_chapter]['description']:
                chapters[last_chapter]['description'] += " "
            chapters[last_chapter]['description'] += line.strip()

    return chapters

def check_notes_files(base_path):
    """Check which chapter notes files exist."""
    notes_path = Path(base_path) / "epic" / "notes"
    existing_notes = {}

    if notes_path.exists():
        for notes_file in notes_path.glob("chapter_*_notes.md"):
            match = re.match(r'chapter_(\d+)_notes\.md', notes_file.name)
            if match:
                chapter_num = int(match.group(1))
                existing_notes[chapter_num] = notes_file

    return existing_notes

def read_notes_content(notes_file):
    """Read the content of a notes file."""
    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def generate_summary(base_path):
    """Generate the complete markdown summary."""

    # Read the comprehensive chapter plan
    plan_path = Path(base_path) / "epic" / "COMPREHENSIVE_CHAPTER_PLAN.md"
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_content = f.read()

    # Extract chapter information
    chapters = extract_chapter_info_from_plan(plan_content)

    # Check which notes files exist
    existing_notes = check_notes_files(base_path)

    # Generate the summary
    summary = []
    summary.append("# Gaiad Epic - Complete Chapter Summary")
    summary.append("")
    summary.append("A comprehensive overview of all 364 chapters with notes status and content.")
    summary.append("")
    summary.append("## Legend")
    summary.append("- ✅ **Has Notes**: Chapter has detailed notes file")
    summary.append("- ❌ **No Notes**: Chapter exists in plan but no notes file")
    summary.append("- 📝 **Notes Content**: Full content of notes when available")
    summary.append("- 🔮 **Astrological Sign**: Each chapter's zodiac correspondence")
    summary.append("")

    # Create zodiac sign index
    summary.append("## 🔮 Zodiac Sign Index")
    summary.append("")
    sign_ranges = {}
    for chapter_num, chapter in chapters.items():
        sign = chapter.get('sign', 'Unknown')
        if sign not in sign_ranges:
            sign_ranges[sign] = []
        sign_ranges[sign].append(chapter_num)

    for sign in sign_ranges:
        if sign and sign != 'Unknown':
            chapters_in_sign = sorted(sign_ranges[sign])
            min_ch = min(chapters_in_sign)
            max_ch = max(chapters_in_sign)
            summary.append(f"- **{sign}**: Chapters {min_ch}-{max_ch} ({len(chapters_in_sign)} chapters)")

    summary.append("")
    summary.append("---")
    summary.append("")

    current_section = ""

    # Process each chapter in order
    for chapter_num in sorted(chapters.keys()):
        chapter = chapters[chapter_num]

        # Add section header if changed
        if chapter['section'] != current_section:
            current_section = chapter['section']
            summary.append(f"# {current_section}")
            summary.append("")

        # Chapter header with status and zodiac sign
        has_notes = chapter_num in existing_notes
        status_icon = "✅" if has_notes else "❌"
        sign_info = f"**{chapter.get('sign', 'Unknown')}**" if chapter.get('sign') else ""

        summary.append(f"## {status_icon} Chapter {chapter_num}: {chapter['title']} | {sign_info}")
        summary.append("")

        # Add zodiac and range info prominently
        if chapter.get('sign'):
            summary.append(f"**🔮 Astrological Sign:** {chapter['sign']}")
        if chapter.get('range'):
            summary.append(f"**📚 Chapter Range:** {chapter['range']}")
        summary.append("")

        # Chapter description from plan
        if chapter['description']:
            summary.append("**Overview from Comprehensive Plan:**")
            summary.append(chapter['description'])
            summary.append("")

        # Notes content if available
        if has_notes:
            summary.append("### 📝 Notes Content:")
            summary.append("")
            notes_content = read_notes_content(existing_notes[chapter_num])
            # Add notes content with proper indentation
            for line in notes_content.split('\n'):
                summary.append(line)
            summary.append("")
        else:
            summary.append("*No notes file available*")
            summary.append("")

        summary.append("---")
        summary.append("")

    # Statistics
    total_chapters = len(chapters)
    chapters_with_notes = len(existing_notes)
    chapters_without_notes = total_chapters - chapters_with_notes

    summary.append("# Summary Statistics")
    summary.append("")
    summary.append(f"- **Total Chapters**: {total_chapters}")
    summary.append(f"- **Chapters with Notes**: {chapters_with_notes} ({chapters_with_notes/total_chapters*100:.1f}%)")
    summary.append(f"- **Chapters without Notes**: {chapters_without_notes} ({chapters_without_notes/total_chapters*100:.1f}%)")
    summary.append("")

    # List chapters without notes
    missing_chapters = [ch for ch in sorted(chapters.keys()) if ch not in existing_notes]
    if missing_chapters:
        summary.append("## Chapters Missing Notes")
        summary.append("")
        for chapter_num in missing_chapters:
            summary.append(f"- Chapter {chapter_num}: {chapters[chapter_num]['title']}")
        summary.append("")

    return '\n'.join(summary)

if __name__ == "__main__":
    base_path = "C:/Users/Immanuelle/Documents/Github/Gaiad"
    summary = generate_summary(base_path)

    # Write the summary
    output_path = Path(base_path) / "CHAPTER_SUMMARY_FOR_CHATGPT.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Summary generated: {output_path}")
    print(f"Total length: {len(summary)} characters")