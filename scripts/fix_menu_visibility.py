#!/usr/bin/env python3
"""
Fix menu visibility - ensure mobile menu is hidden on desktop and desktop menu is hidden on mobile.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"


def fix_menu_visibility(post_path):
    """Fix menu visibility CSS."""
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
    original_content = style_content
    
    # Check if we already have the proper CSS
    has_desktop_hide = '.nav-links.mobile-menu' in style_content and 'display: none' in style_content.split('.nav-links.mobile-menu')[0]
    has_mobile_show = '@media (max-width: 768px)' in style_content and '.nav-links.mobile-menu' in style_content
    
    if has_desktop_hide and has_mobile_show:
        print(f"  ℹ️  Menu visibility CSS already correct")
        return False
    
    # Find the .nav-links rule
    nav_links_match = re.search(r'\.nav-links\s*\{[^}]*\}', style_content)
    
    if nav_links_match:
        # Insert mobile menu hide rule after .nav-links
        insertion_point = nav_links_match.end()
        mobile_hide_css = """
        
        /* Hide mobile menu on desktop */
        .nav-links.mobile-menu {
            display: none;
        }
        """
        
        # Check if rule already exists
        if '.nav-links.mobile-menu' not in style_content[:insertion_point + 200]:
            style_content = style_content[:insertion_point] + mobile_hide_css + style_content[insertion_point:]
            print(f"  ✅ Added CSS to hide mobile menu on desktop")
    
    # Ensure mobile menu shows on mobile (in media query)
    if '@media (max-width: 768px)' in style_content:
        media_query_start = style_content.find('@media (max-width: 768px)')
        media_query_end = style_content.find('}', media_query_start + len('@media (max-width: 768px)'))
        
        # Find the end of the media query block
        brace_count = 0
        for i, char in enumerate(style_content[media_query_start:], start=media_query_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    media_query_end = i + 1
                    break
        
        media_query_content = style_content[media_query_start:media_query_end]
        
        # Check if mobile menu display rule exists in media query
        if '.nav-links.mobile-menu' in media_query_content and 'display:' not in media_query_content.split('.nav-links.mobile-menu')[1].split('}')[0]:
            # Add display rule for mobile menu in media query
            mobile_menu_match = re.search(r'\.nav-links\.mobile-menu\s*\{', media_query_content)
            if mobile_menu_match:
                # Find the closing brace of this rule
                rule_start = mobile_menu_match.end()
                rule_end = media_query_content.find('}', rule_start)
                rule_content = media_query_content[rule_start:rule_end]
                
                if 'display:' not in rule_content:
                    # Insert display: block at the start of the rule
                    display_rule = '\n                display: block;\n'
                    media_query_content = media_query_content[:rule_start] + display_rule + media_query_content[rule_start:]
                    style_content = style_content[:media_query_start] + media_query_content + style_content[media_query_end:]
                    print(f"  ✅ Added display rule for mobile menu on mobile")
    
    if style_content != original_content:
        style_tag.string = style_content
        try:
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"  ✅ Saved changes")
            return True
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
            return False
    
    return False


def main():
    """Main function."""
    print("=" * 60)
    print("Fixing menu visibility in blog posts")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if fix_menu_visibility(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


