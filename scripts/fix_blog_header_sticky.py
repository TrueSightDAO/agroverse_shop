#!/usr/bin/env python3
"""
Remove or adjust sticky positioning from blog post headers to make scrolling feel more natural.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"


def fix_header_sticky(post_path):
    """Remove or adjust sticky positioning from blog post headers."""
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
    
    # Check if header has sticky positioning
    if 'position: sticky' in style_content or 'position:sticky' in style_content:
        # Find the header CSS rule
        header_match = re.search(r'header\s*\{[^}]*\}', style_content, re.DOTALL)
        
        if header_match:
            header_rule = header_match.group(0)
            
            # Remove sticky positioning, top, and z-index from header
            # But keep the z-index for mobile menu elements
            new_header_rule = header_rule
            new_header_rule = re.sub(r'position:\s*sticky;?\s*', '', new_header_rule)
            new_header_rule = re.sub(r'position:sticky;?\s*', '', new_header_rule)
            
            # Remove top: 0 only if it's directly related to sticky positioning
            # We need to be careful - only remove top if it's in the header rule
            if 'top:' in new_header_rule:
                # Remove top property from header (but keep z-index as it might be needed for mobile menu)
                # Actually, let's keep z-index but remove top
                new_header_rule = re.sub(r'top:\s*0;?\s*', '', new_header_rule)
                new_header_rule = re.sub(r'top:\s*0\s*;?\s*', '', new_header_rule)
            
            # Replace the header rule in the style content
            style_content = style_content[:header_match.start()] + new_header_rule + style_content[header_match.end():]
            
            print(f"  ✅ Removed sticky positioning from header")
    
    # Alternatively, we could change it to static or just remove the position property
    # But let's just remove sticky for now
    
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
    
    print(f"  ℹ️  No sticky positioning found")
    return False


def main():
    """Main function."""
    print("=" * 60)
    print("Removing sticky positioning from blog post headers")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if fix_header_sticky(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

