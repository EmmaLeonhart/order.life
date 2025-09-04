#!/usr/bin/env python3
"""
Test Ophiuchus month page specifically
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import build_month_page

def show_ophiuchus():
    """Show what Ophiuchus (month 13) looks like."""
    title, content = build_month_page(13)  # Ophiuchus is month 13
    print(f"Title: {title}")
    print("=" * 60)
    # Show first 500 characters to see the template
    print(content[:500] + "..." if len(content) > 500 else content)

if __name__ == "__main__":
    show_ophiuchus()