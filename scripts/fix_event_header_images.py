#!/usr/bin/env python3
"""
Fix header images on event pages to show the full image without cutting it off.
Updates all event pages in event-details-registration directory.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
EVENT_DIR = BASE_DIR / "event-details-registration"

def fix_event_header_image(file_path):
    """Fix the header image CSS in an event page."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    # Pattern to match the event-hero CSS section
    # Look for background-size: cover and update it
    old_pattern = r'(\.event-hero\s*\{[^}]*background-size:\s*)cover([^;]*;)'
    
    # Replace with better sizing that shows full image
    # Using 'contain' ensures the full image is visible, or we can use a larger height approach
    replacement = r'\1contain\2'
    
    # Also update background-position to be more flexible
    if 'background-position: center center;' in content:
        # Change to center top for better visibility
        content = content.replace(
            'background-position: center center;',
            'background-position: center top;'
        )
    
    # Increase min-height to give more space for the image
    height_pattern = r'(\.event-hero[^}]*min-height:\s*)(\d+)vh([^;]*;)'
    
    def increase_height(match):
        current_height = int(match.group(2))
        # Increase to at least 70vh or more if currently 60vh
        new_height = max(70, current_height + 10)
        return f"{match.group(1)}{new_height}vh{match.group(3)}"
    
    content = re.sub(height_pattern, increase_height, content)
    
    # If cover exists, replace it with contain
    if 'background-size: cover;' in content:
        content = content.replace('background-size: cover;', 'background-size: contain;')
        # Also add background-repeat: no-repeat to ensure clean display
        if 'background-repeat' not in content.split('.event-hero')[1].split('}')[0]:
            content = re.sub(
                r'(\.event-hero\s*\{[^}]*background-blend-mode:[^;]*;)',
                r'\1\n            background-repeat: no-repeat;',
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
    print("=" * 60)
    
    fixed = 0
    errors = []
    
    for file_path in event_files:
        print(f"\nProcessing: {file_path.relative_to(BASE_DIR)}")
        
        if fix_event_header_image(file_path):
            print("  ✅ Fixed header image styling")
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


