#!/usr/bin/env python3
"""
Refine header images on event pages to show more of the image without cutting it off.
Uses a refined approach: larger height with cover and better positioning.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
EVENT_DIR = BASE_DIR / "event-details-registration"

def fix_event_header_image(file_path):
    """Fix the header image CSS in an event page with refined approach."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    # Pattern to match the entire event-hero CSS section
    hero_pattern = r'(\.event-hero\s*\{[^}]*\})'
    
    # Check if already has the improved version
    if 'background-attachment' in content or 'event-hero::before' in content:
        # Already updated, check if we need to refine further
        if 'min-height: 80vh' not in content:
            # Update height
            content = re.sub(
                r'(\.event-hero[^}]*min-height:\s*)\d+vh([^;]*;)',
                r'\180vh\2',
                content
            )
            # Ensure cover is used (not contain)
            content = re.sub(
                r'(\.event-hero[^}]*background-size:\s*)contain([^;]*;)',
                r'\1cover\2',
                content
            )
            # Ensure center center positioning
            content = re.sub(
                r'(\.event-hero[^}]*background-position:\s*)[^;]+([^;]*;)',
                r'\1center center\2',
                content
            )
    else:
        # Replace the entire hero section with improved version
        old_hero_match = re.search(hero_pattern, content, re.DOTALL)
        if old_hero_match:
            old_hero = old_hero_match.group(1)
            
            # Extract the background URL
            bg_url_match = re.search(r"url\('([^']+)'\)", old_hero)
            bg_url = bg_url_match.group(1) if bg_url_match else "''"
            
            # Create improved hero section
            new_hero = f""".event-hero {{
            background: linear-gradient(135deg, rgba(59, 51, 51, 0.6) 0%, rgba(77, 77, 77, 0.6) 100%), url('{bg_url}');
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: scroll;
            background-blend-mode: overlay;
            color: white;
            padding: 5rem 2rem;
            text-align: center;
            min-height: 80vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }}"""
            
            content = content.replace(old_hero, new_hero)
            
            # Add the ::before pseudo-element after the hero section
            hero_end = content.find('.event-hero')
            if hero_end != -1:
                # Find the closing brace of .event-hero
                next_style = content.find('.event-', hero_end + 1)
                if next_style != -1:
                    insert_pos = content.rfind('}', hero_end, next_style) + 1
                    pseudo_element = """
        
        .event-hero > * {
            position: relative;
            z-index: 1;
        }"""
                    content = content[:insert_pos] + pseudo_element + content[insert_pos:]
        else:
            # Fallback: just update key properties
            content = re.sub(
                r'(\.event-hero[^}]*background-size:\s*)[^;]+([^;]*;)',
                r'\1cover\2',
                content
            )
            content = re.sub(
                r'(\.event-hero[^}]*background-position:\s*)[^;]+([^;]*;)',
                r'\1center center\2',
                content
            )
            content = re.sub(
                r'(\.event-hero[^}]*min-height:\s*)\d+vh([^;]*;)',
                r'\180vh\2',
                content
            )
            # Add background-attachment if not present
            if 'background-attachment' not in content.split('.event-hero')[1].split('}')[0]:
                content = re.sub(
                    r'(\.event-hero\s*\{[^}]*background-repeat:[^;]*;)',
                    r'\1\n            background-attachment: scroll;',
                    content
                )
            # Add overflow hidden
            if 'overflow:' not in content.split('.event-hero')[1].split('}')[0]:
                content = re.sub(
                    r'(\.event-hero\s*\{[^}]*position:\s*relative[^;]*;)',
                    r'\1\n            overflow: hidden;',
                    content
                )
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def main():
    """Fix all event pages."""
    if not EVENT_DIR.exists():
        print(f"Event directory not found: {EVENT_DIR}")
        return
    
    event_files = list(EVENT_DIR.rglob("index.html"))
    
    if not event_files:
        print("No event files found")
        return
    
    print(f"Found {len(event_files)} event pages")
    print("Refining header image styling...")
    print("=" * 60)
    
    fixed = 0
    errors = []
    
    for file_path in event_files:
        print(f"\nProcessing: {file_path.relative_to(BASE_DIR)}")
        
        if fix_event_header_image(file_path):
            print("  ✅ Refined header image styling")
            fixed += 1
        else:
            print("  ❌ Error fixing file")
            errors.append(str(file_path))
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Fixed: {fixed}")
    print(f"  ❌ Errors: {len(errors)}")
    if errors:
        print(f"\nErrors:")
        for error in errors:
            print(f"  - {error}")

if __name__ == "__main__":
    main()


