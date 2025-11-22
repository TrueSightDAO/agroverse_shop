#!/usr/bin/env python3
"""
Clean up duplicate menu elements in blog posts.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"


def clean_duplicates(post_path):
    """Remove duplicate menu elements."""
    print(f"\nCleaning: {post_path.name}")
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    # Fix class_ to class in the HTML
    content = content.replace('class_="', 'class="')
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove duplicate buttons
    buttons = soup.find_all('button', class_='mobile-menu-toggle')
    if len(buttons) > 1:
        for btn in buttons[1:]:
            btn.decompose()
        print(f"  ✅ Removed {len(buttons) - 1} duplicate buttons")
    
    # Remove duplicate mobile menus
    mobile_menus = soup.find_all('ul', class_='mobile-menu')
    if len(mobile_menus) > 1:
        for menu in mobile_menus[1:]:
            menu.decompose()
        print(f"  ✅ Removed {len(mobile_menus) - 1} duplicate mobile menus")
    
    # Remove duplicate overlays
    overlays = soup.find_all('div', class_='mobile-menu-overlay')
    if len(overlays) > 1:
        for overlay in overlays[1:]:
            overlay.decompose()
        print(f"  ✅ Removed {len(overlays) - 1} duplicate overlays")
    
    # Save
    try:
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"  ✅ Saved")
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Cleaning duplicate menu elements")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if clean_duplicates(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Cleaned {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


