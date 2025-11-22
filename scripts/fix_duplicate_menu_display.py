#!/usr/bin/env python3
"""
Fix duplicate menu display in blog posts - ensure only one menu shows at a time.
"""

from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"


def fix_menu_display(post_path):
    """Fix menu display to show only one menu at a time."""
    print(f"\nProcessing: {post_path.name}")
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    nav = soup.find('nav')
    if not nav:
        print(f"  ⚠️  No nav found")
        return False
    
    # Find all nav-links ul elements
    nav_links_list = nav.find_all('ul', class_='nav-links')
    
    if len(nav_links_list) < 2:
        print(f"  ℹ️  Menu structure looks correct (found {len(nav_links_list)} nav-links)")
        return False
    
    # Find desktop menu (without mobile-menu class)
    desktop_menu = None
    mobile_menu = None
    
    for menu in nav_links_list:
        classes = menu.get('class', [])
        if 'mobile-menu' in classes:
            mobile_menu = menu
        else:
            desktop_menu = menu
    
    if not desktop_menu or not mobile_menu:
        print(f"  ⚠️  Could not identify desktop/mobile menus")
        return False
    
    # Ensure desktop menu doesn't have mobile-menu class
    if 'mobile-menu' in desktop_menu.get('class', []):
        classes = desktop_menu.get('class', [])
        classes.remove('mobile-menu')
        desktop_menu['class'] = classes
    
    # Ensure mobile menu has both classes
    mobile_classes = mobile_menu.get('class', [])
    if 'nav-links' not in mobile_classes:
        mobile_classes.insert(0, 'nav-links')
    if 'mobile-menu' not in mobile_classes:
        mobile_classes.append('mobile-menu')
    mobile_menu['class'] = mobile_classes
    
    # Check CSS - ensure desktop menu is hidden on mobile
    style_tag = soup.find('style')
    if style_tag:
        style_content = style_tag.string or ""
        
        # Check if we have the correct media query
        if '.nav-links:not(.mobile-menu)' not in style_content:
            # Add CSS to hide desktop menu on mobile if not present
            css_addition = """
            
            .nav-links:not(.mobile-menu) {
                display: flex !important;
            }
            
            @media (max-width: 768px) {
                .nav-links:not(.mobile-menu) {
                    display: none !important;
                }
            }
            """
            
            # Insert before mobile menu styles
            if '@media (max-width: 768px)' in style_content:
                insertion_point = style_content.find('@media (max-width: 768px)')
                style_tag.string = style_content[:insertion_point] + css_addition + style_content[insertion_point:]
            else:
                style_tag.string += css_addition
    
    # Save
    try:
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"  ✅ Fixed menu display")
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Fixing duplicate menu display in blog posts")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if fix_menu_display(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


