#!/usr/bin/env python3
"""
Optimize mobile responsiveness across all pages.
Ensures proper hamburger menu functionality and mobile-optimized layouts.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def optimize_mobile_responsive(file_path):
    """Optimize mobile responsiveness in an HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False
    
    original_content = content
    changed = False
    
    # Check if file has navigation
    if '<nav' not in content:
        return False
    
    # Ensure mobile menu CSS includes hiding regular nav-links
    if '@media (max-width: 768px)' in content and '.mobile-menu-toggle' in content:
        # Check if we need to add the hide rule for regular nav-links
        if '.nav-links:not(.mobile-menu)' not in content.split('@media (max-width: 768px)')[1]:
            # Find the @media section and add hide rule
            media_pattern = r'(@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.mobile-menu-toggle[^}]*display:\s*flex[^}]*\})'
            
            def add_hide_nav(match):
                return match.group(1) + '\n            .nav-links:not(.mobile-menu) {\n                display: none !important;\n            }'
            
            new_content = re.sub(media_pattern, add_hide_nav, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                changed = True
    
    # Add general mobile optimizations
    if '@media (max-width: 768px)' in content:
        # Ensure viewport meta tag
        if 'viewport' not in content:
            # Add viewport meta tag
            content = re.sub(
                r'(<head[^>]*>)',
                r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                content
            )
            changed = True
        
        # Add mobile optimizations to existing media query
        if 'max-width: 768px' in content and 'overflow-x: hidden' not in content.split('@media')[1]:
            # Add overflow-x hidden to body for mobile
            body_mobile_rule = r'(@media\s*\(max-width:\s*768px\)\s*\{[^}]*)'
            
            def add_body_overflow(match):
                existing = match.group(1)
                if 'body {' not in existing.split('}')[0] if '}' in existing else existing:
                    return existing + '\n        body {\n            overflow-x: hidden;\n        }\n        '
                return existing
            
            new_content = re.sub(body_mobile_rule, add_body_overflow, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                changed = True
    
    # Fix any remaining class_ attributes
    if 'class_=' in content:
        content = re.sub(r'class_=', 'class=', content)
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
    """Optimize mobile responsiveness on all HTML pages."""
    print("Optimizing mobile responsiveness...")
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
        if optimize_mobile_responsive(file_path):
            fixed += 1
            print(f"  ✅ Optimized: {file_path.relative_to(BASE_DIR)}")
        else:
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Optimized: {fixed}")
    print(f"  ℹ️  Skipped: {skipped}")

if __name__ == "__main__":
    main()

