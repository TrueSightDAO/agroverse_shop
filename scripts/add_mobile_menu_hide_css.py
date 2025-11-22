#!/usr/bin/env python3
"""
Add CSS to hide mobile menu on desktop for all blog posts.
"""

from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"


def add_mobile_menu_hide_css(post_path):
    """Add CSS to hide mobile menu on desktop."""
    print(f"\nProcessing: {post_path.name}")
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    style_tag = soup.find('style')
    if not style_tag:
        print(f"  ⚠️  No style tag found")
        return False
    
    style_content = style_tag.string or ""
    
    # Check if rule already exists
    if '.nav-links.mobile-menu' in style_content and 'display: none' in style_content:
        # Check if it's in the right place (not just in media query)
        before_media = style_content.split('@media')[0] if '@media' in style_content else style_content
        if '.nav-links.mobile-menu' in before_media and 'display: none' in before_media:
            print(f"  ℹ️  CSS already exists")
            return False
    
    # Find insertion point - after .nav-links rule
    if '.nav-links {' in style_content:
        # Find the end of .nav-links rule
        nav_links_start = style_content.find('.nav-links {')
        nav_links_end = style_content.find('}', nav_links_start) + 1
        
        # Insert the mobile menu hide rule
        mobile_hide_css = """
        
        /* Hide mobile menu on desktop */
        .nav-links.mobile-menu {
            display: none;
        }
        """
        
        style_tag.string = style_content[:nav_links_end] + mobile_hide_css + style_content[nav_links_end:]
        
        try:
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"  ✅ Added CSS to hide mobile menu on desktop")
            return True
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
            return False
    
    print(f"  ⚠️  Could not find .nav-links rule")
    return False


def main():
    """Main function."""
    print("=" * 60)
    print("Adding mobile menu hide CSS to blog posts")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if add_mobile_menu_hide_css(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


