#!/usr/bin/env python3
"""
Fix mobile navigation issues:
1. Fix class_ to class attribute
2. Hide regular nav-links on mobile (only show in hamburger menu)
3. Ensure proper mobile menu functionality
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def fix_mobile_nav(file_path):
    """Fix mobile navigation in an HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False
    
    original_content = content
    changed = False
    
    # Fix class_ to class
    if 'class_=' in content:
        content = re.sub(r'class_=', 'class=', content)
        changed = True
    
    # Fix nav-links to hide on mobile by default
    if '.mobile-menu-toggle' in content:
        # Find the @media (max-width: 768px) section
        media_query_pattern = r'(@media\s*\(max-width:\s*768px\)\s*\{[^}]*(?:}[^}]*)*?\.nav-links[^}]*\})'
        
        # Check if we need to hide regular nav-links
        if '.nav-links:not(.mobile-menu)' not in content:
            # Insert hide rule for regular nav-links in mobile media query
            if '@media (max-width: 768px)' in content:
                # Find where to insert - after .mobile-menu-toggle or before closing brace
                insert_pattern = r'(@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.mobile-menu-toggle[^}]+\})'
                
                def add_hide_rule(match):
                    return match.group(1) + '\n            .nav-links:not(.mobile-menu) {\n                display: none;\n            }'
                
                content = re.sub(insert_pattern, add_hide_rule, content)
                changed = True
    
    # Ensure overlay has proper class attribute
    if 'class_="mobile-menu-overlay"' in content:
        content = content.replace('class_="mobile-menu-overlay"', 'class="mobile-menu-overlay"')
        changed = True
    
    if changed and content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    return False

def main():
    """Fix mobile navigation on all HTML pages."""
    print("Fixing mobile navigation...")
    print("=" * 60)
    
    # Find HTML files (exclude assets/raw)
    html_files = []
    directories = [
        BASE_DIR,
        BASE_DIR / 'post',
        BASE_DIR / 'event-details-registration',
        BASE_DIR / 'category',
        BASE_DIR / 'product-page',
        BASE_DIR / 'farms',
        BASE_DIR / 'shipments',
        BASE_DIR / 'partners',
    ]
    
    for directory in directories:
        if directory.exists():
            html_files.extend(list(directory.rglob('*.html')))
    
    html_files = list(set(html_files))
    html_files = [f for f in html_files 
                  if 'assets/raw' not in str(f)
                  and '.git' not in str(f)
                  and f.is_file()]
    
    print(f"Found {len(html_files)} HTML files")
    print("=" * 60)
    
    fixed = 0
    skipped = 0
    
    for file_path in sorted(html_files):
        if fix_mobile_nav(file_path):
            fixed += 1
            print(f"  ✅ Fixed: {file_path.relative_to(BASE_DIR)}")
        else:
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Fixed: {fixed}")
    print(f"  ℹ️  Skipped: {skipped}")

if __name__ == "__main__":
    main()

