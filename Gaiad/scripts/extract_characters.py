#!/usr/bin/env python
"""
Extract characters from Gaiad epic chapters.
Parses {{c|Name}} markup from chapter_*.md files and generates JSON files for each character.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Directories
EPIC_DIR = Path(__file__).parent.parent / "epic"
GENEALOGY_DIR = Path(__file__).parent.parent / "genealogy"

# Create genealogy directory if it doesn't exist
GENEALOGY_DIR.mkdir(exist_ok=True)

def extract_marked_text(text):
    """Extract all {{c|...}} marked text from a string."""
    pattern = r'\{\{c\|([^}]+)\}\}'
    return re.findall(pattern, text)

def load_chapters():
    """Load all chapters and extract marked characters."""
    chapters = {}
    character_chapters = defaultdict(set)  # Use set to deduplicate

    # Find all chapter files
    chapter_files = sorted(EPIC_DIR.glob("chapter_*.md"))

    for chapter_file in chapter_files:
        # Extract chapter number from filename
        match = re.match(r"chapter_(\d+)\.md", chapter_file.name)
        if not match:
            continue

        chapter_num = int(match.group(1))

        # Read chapter content
        with open(chapter_file, "r", encoding="utf-8") as f:
            content = f.read()

        chapters[chapter_num] = content

        # Extract all marked text
        marked_texts = extract_marked_text(content)

        # Track which chapters each character appears in (deduplicated per chapter)
        for char_name in marked_texts:
            character_chapters[char_name].add(chapter_num)

    return chapters, character_chapters

def create_character_jsons(character_chapters):
    """Create JSON files for each unique character."""

    for char_name in sorted(character_chapters.keys()):
        chapters = sorted(list(character_chapters[char_name]))

        # Create character data
        char_data = {
            "name": char_name,
            "chapters_mentioned_in": chapters,
            "father": None,
            "mother": None,
            "children": [],
            "wiki_qid": None
        }

        # Create filename from character name (sanitize for filesystem)
        # Convert to snake_case and replace spaces with underscores
        filename = re.sub(r'[^a-zA-Z0-9_-]', '', char_name.replace(' ', '_')).lower()

        # Handle edge cases where filename becomes empty
        if not filename:
            filename = "unknown"

        filepath = GENEALOGY_DIR / f"{filename}.json"

        # Write JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(char_data, f, indent=2, ensure_ascii=False)

        print(f"Created: {filepath}")

    print(f"\nTotal characters created: {len(character_chapters)}")

def main():
    """Main entry point."""
    print("Extracting characters from Gaiad epic chapters...")
    print(f"Epic directory: {EPIC_DIR}")
    print(f"Output directory: {GENEALOGY_DIR}")
    print()

    chapters, character_chapters = load_chapters()
    print(f"Loaded {len(chapters)} chapters")
    print(f"Found {len(character_chapters)} unique characters/concepts")
    print()

    create_character_jsons(character_chapters)

if __name__ == "__main__":
    main()
