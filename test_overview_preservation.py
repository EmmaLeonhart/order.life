#!/usr/bin/env python3
"""
Test script to diagnose Overview section preservation issues.
This will help determine if the problem is:
1. Wiki pages don't have Overview sections yet
2. API/authentication issues
3. Content extraction problems
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(__file__))

from zodiac_wiki_pages import Wiki, extract_overview_section, build_year_page, build_month_page

def test_wiki_connection(username, password):
    """Test basic wiki connection and page retrieval."""
    print("=== TESTING WIKI CONNECTION ===")
    
    API_URL = "https://evolutionism.miraheze.org/w/api.php"
    
    try:
        wiki = Wiki(API_URL)
        wiki.login_bot(username, password)
        print("✅ Successfully logged in to wiki")
        
        # Test retrieving a few sample pages
        test_pages = ["12025 GE", "Sagittarius", "Sagittarius 1"]
        
        for page_title in test_pages:
            print(f"\n--- Testing page: '{page_title}' ---")
            content = wiki.get_page_content(page_title)
            
            if not content:
                print(f"❌ Page '{page_title}' doesn't exist or has no content")
                continue
                
            print(f"✅ Found page content ({len(content)} chars)")
            
            # Check if it has an Overview section
            lines = content.split('\n')
            has_overview = any(line.strip() == "== Overview ==" for line in lines)
            
            if has_overview:
                print("✅ Page has Overview section")
                overview_content = extract_overview_section(content)
                if overview_content.strip():
                    print(f"✅ Overview has content ({len(overview_content)} chars): {overview_content[:100]}...")
                else:
                    print("⚠️ Overview section exists but is empty")
            else:
                print("❌ Page has no Overview section")
                
            # Show first few lines for context
            print("First 5 lines of page:")
            for i, line in enumerate(lines[:5]):
                print(f"  {i+1}: {line}")
                
        return wiki
        
    except Exception as e:
        print(f"❌ Error connecting to wiki: {e}")
        return None

def test_overview_preservation(wiki, test_pages):
    """Test if Overview sections are preserved when regenerating pages."""
    print("\n=== TESTING OVERVIEW PRESERVATION ===")
    
    for page_info in test_pages:
        page_type, page_arg = page_info
        print(f"\n--- Testing {page_type}: {page_arg} ---")
        
        if page_type == "year":
            title, new_content = build_year_page(page_arg, wiki)
        elif page_type == "month":
            title, new_content = build_month_page(page_arg, wiki)
        else:
            continue
            
        print(f"Generated title: '{title}'")
        
        # Check if new content preserved Overview
        lines = new_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == "== Overview ==":
                print(f"✅ Found Overview section at line {i+1}")
                # Show next few lines
                for j in range(1, 4):
                    if i+j < len(lines) and lines[i+j].strip():
                        content_line = lines[i+j]
                        if "Add custom content" in content_line:
                            print(f"❌ Line {i+j+1}: {content_line} (placeholder - not preserved!)")
                        else:
                            print(f"✅ Line {i+j+1}: {content_line} (preserved content)")
                        break
                break
        else:
            print("❌ No Overview section found in generated content")

def main():
    parser = argparse.ArgumentParser(description='Test Overview section preservation')
    parser.add_argument('--username', required=True, help='Wiki username')
    parser.add_argument('--password', required=True, help='Wiki password')
    
    args = parser.parse_args()
    
    # Test wiki connection first
    wiki = test_wiki_connection(args.username, args.password)
    if not wiki:
        return
        
    # Test Overview preservation for a few sample pages
    test_pages = [
        ("year", 12025),
        ("month", 1),  # Sagittarius
        ("year", 12024),
    ]
    
    test_overview_preservation(wiki, test_pages)
    
    print("\n=== DIAGNOSIS COMPLETE ===")
    print("If Overview sections are being replaced with placeholders,")
    print("the issue is likely that the existing wiki pages don't have")
    print("Overview sections yet, or they're formatted differently.")

if __name__ == "__main__":
    main()