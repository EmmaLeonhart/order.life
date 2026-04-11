#!/usr/bin/env python3
"""
Test Horus intercalary month page specifically
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_month_page

def show_horus():
    """Show what Horus (month 14) looks like."""
    title, content = build_month_page(14)  # Horus is month 14
    print(f"Title: {title}")
    print("=" * 60)
    # Show first 600 characters to see the template
    print(content[:600] + "..." if len(content) > 600 else content)

if __name__ == "__main__":
    show_horus()