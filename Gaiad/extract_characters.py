#!/usr/bin/env python3
"""
Extract all character names from chapters 001-062.
"""

import re
import glob
from pathlib import Path
from collections import Counter

def extract_capitalized_names(text):
    """Extract capitalized words that look like character names."""
    # Match capitalized words, but exclude common words
    exclude_words = {
        "The", "And", "But", "For", "With", "From", "Through", "When", "Where", "What",
        "This", "That", "Their", "They", "Them", "These", "Those", "Then", "Thus",
        "Here", "There", "While", "Which", "Who", "Whose", "Whom", "How", "Why",
        "All", "Each", "Every", "Some", "Many", "Few", "Most", "Several", "Both",
        "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "First", "Second", "Third", "Last", "Next", "Previous", "Another", "Other",
        "Lord", "Lady", "King", "Queen", "Prince", "Princess", "God", "Goddess",
        "Father", "Mother", "Brother", "Sister", "Son", "Daughter", "Children",
        "Day", "Night", "Dawn", "Dusk", "Morning", "Evening", "Noon", "Midnight",
        "Spring", "Summer", "Fall", "Winter", "Autumn",
        "North", "South", "East", "West",
        "Heaven", "Earth", "Sky", "Sea", "Ocean", "Land", "Water", "Fire", "Air",
        "Life", "Death", "Love", "Hope", "Faith", "Truth", "Light", "Dark", "Darkness",
        "Time", "Space", "Universe", "World", "Cosmos", "Galaxy",
        "In", "On", "At", "To", "By", "Of", "As", "Into", "Upon", "Within",
        "About", "Above", "Across", "After", "Against", "Along", "Among", "Around",
        "Before", "Behind", "Below", "Beneath", "Beside", "Between", "Beyond",
        "During", "Inside", "Near", "Over", "Past", "Since", "Under", "Until",
        "Unless", "Unlike", "Without", "Toward", "Towards",
        "Advertisement", "Chapter", "Book", "Tale", "Story", "Song", "Poem",
        "Once", "Upon", "Never", "Always", "Sometimes", "Often", "Rarely",
        "Can", "Could", "May", "Might", "Must", "Should", "Would", "Will", "Shall",
        "His", "Her", "Its", "My", "Your", "Our",
        "Not", "No", "Yes", "Yet", "Still", "Just", "Only", "Even", "Also", "Too",
        "So", "Such", "Very", "Much", "More", "Most", "Less", "Least",
        "Great", "Grand", "Mighty", "Noble", "Sacred", "Holy", "Divine", "Blessed",
        "Bright", "Beautiful", "Fair", "Pure", "True", "Wise", "Ancient", "Old", "New",
        "First", "Final", "Last", "Eternal", "Endless",
        "Though", "Although", "Because", "Since", "While", "Until", "Unless",
        "If", "Whether", "Than", "Rather", "Instead", "Otherwise",
        "Omega", "Alpha", "Point",
    }

    # Extract capitalized words
    pattern = r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)*\b'
    words = re.findall(pattern, text)

    # Filter out excluded words
    names = [word for word in words if word not in exclude_words]

    return names

def main():
    epic_dir = Path("/home/user/Gaiad-and-Literature-work/epic")

    # Get chapters 001-062
    chapter_files = sorted(epic_dir.glob("chapter_0[0-5][0-9].md")) + sorted(epic_dir.glob("chapter_06[0-2].md"))

    print(f"Extracting characters from {len(chapter_files)} chapters...\n")

    all_names = []

    for chapter_file in chapter_files:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
            names = extract_capitalized_names(content)
            all_names.extend(names)

    # Count occurrences
    name_counts = Counter(all_names)

    # Sort by frequency (descending)
    sorted_names = sorted(name_counts.items(), key=lambda x: (-x[1], x[0]))

    print("Top 100 most frequently mentioned names:\n")
    for i, (name, count) in enumerate(sorted_names[:100], 1):
        print(f"{i:3d}. {name:30s} ({count:4d} mentions)")

    print(f"\n\nTotal unique names: {len(name_counts)}")
    print(f"Total mentions: {sum(name_counts.values())}")

    # Save all unique names to a file
    output_file = epic_dir / "extracted_character_names.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Extracted Character Names (sorted by frequency)\n\n")
        for name, count in sorted_names:
            f.write(f"{name}: {count}\n")

    print(f"\n\nFull list saved to: {output_file}")

if __name__ == "__main__":
    main()
