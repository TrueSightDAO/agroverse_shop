#!/usr/bin/env python3
"""
Add CSS to reduce spacing between headers and paragraphs in blog posts.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"

SPACING_CSS = """
        /* Reduce spacing between headers and paragraphs */
        .blog-content > div {
            margin-bottom: 0.5rem;
        }
        
        .blog-content > div > h1,
        .blog-content > div > h2,
        .blog-content > div > h3,
        .blog-content > div > h4,
        .blog-content > div > h5,
        .blog-content > div > h6 {
            margin-top: 2rem;
            margin-bottom: 0.75rem;
        }
        
        .blog-content > div > p {
            margin-top: 0;
            margin-bottom: 1rem;
        }
        
        .blog-content > div > p:first-child {
            margin-top: 0;
        }
        
"""


def add_spacing_css(post_path):
    """Add spacing CSS to a blog post."""
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
    
    # Check if spacing CSS already exists
    if '.blog-content > div' in style_content:
        print(f"  ℹ️  Spacing CSS already exists")
        return False
    
    # Find the insertion point (before @media or mobile menu styles)
    insertion_point = None
    if '@media (max-width: 768px)' in style_content:
        insertion_point = style_content.find('@media (max-width: 768px)')
    elif '/* Mobile Menu Toggle */' in style_content:
        insertion_point = style_content.find('/* Mobile Menu Toggle */')
    elif 'mobile-menu-toggle' in style_content:
        insertion_point = style_content.find('mobile-menu-toggle')
    else:
        # Insert at the end before closing </style>
        insertion_point = len(style_content)
    
    # Insert the CSS
    new_content = (
        style_content[:insertion_point] + 
        SPACING_CSS + 
        style_content[insertion_point:]
    )
    
    style_tag.string = new_content
    
    # Save
    try:
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"  ✅ Added spacing CSS")
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Adding spacing CSS to blog posts")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if add_spacing_css(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Updated {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


