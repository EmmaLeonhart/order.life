#!/usr/bin/env python3
"""
Script to add character IDs to epic chapters.
"""

import re
import glob
from pathlib import Path

# Character ID mapping
character_ids = {
    "Aster": 1,
    "Andromeda": 2,
    "Juno": 3,
    "Brunhilda": 4,
    "Ruby": 5,
    "Chrystella": 6,
    "Celestella": 7,
    "Gigastella": 8,
    # More characters will be added as we encounter them
}

def add_character_tags(text, characters_dict):
    """Add {{c|ID|Name}} tags to character mentions."""
    result = text

    for name, char_id in sorted(characters_dict.items(), key=lambda x: len(x[0]), reverse=True):
        # Match the name when it appears as a standalone word
        # Avoid matching if already tagged
        pattern = rf'(?<!\|)(?<!\{{c\|\d\|)\b({re.escape(name)})\b(?!}})'
        replacement = rf'{{{{c|{char_id}|{name}}}}}'
        result = re.sub(pattern, replacement, result)

    return result

def process_chapter(file_path, characters_dict):
    """Process a single chapter file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_content = add_character_tags(content, characters_dict)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Processed: {file_path.name}")

def main():
    epic_dir = Path("/home/user/Gaiad-and-Literature-work/epic")

    # Get chapters 001-062
    chapter_files = sorted(epic_dir.glob("chapter_0[0-5][0-9].md")) + sorted(epic_dir.glob("chapter_06[0-2].md"))

    print(f"Found {len(chapter_files)} chapters to process")
    print(f"Processing first 3 chapters with current character list...")

    # Process just the first few to test
    for chapter_file in chapter_files[:3]:
        process_chapter(chapter_file, character_ids)

    print("\nDone! Check the results.")

if __name__ == "__main__":
    main()
