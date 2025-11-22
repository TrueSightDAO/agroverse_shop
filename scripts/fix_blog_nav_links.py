#!/usr/bin/env python3
"""
Fix blog post navigation - remove duplicates, fix class_, and correct paths.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"
BLOG_INDEX = BASE_DIR / "blog" / "index.html"


def get_blog_post_order():
    """Extract the order of blog posts from blog index page."""
    if not BLOG_INDEX.exists():
        return []
    
    try:
        with open(BLOG_INDEX, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        blog_cards = soup.find_all('article', class_='blog-card')
        post_order = []
        
        for card in blog_cards:
            link = card.find('a', class_='blog-card-link')
            if link:
                href = link.get('href', '')
                match = re.search(r'\.\./post/([^/]+)/', href)
                if match:
                    post_order.append(match.group(1))
        
        return post_order
    except Exception as e:
        print(f"Error reading blog index: {e}")
        return []


def fix_blog_navigation(post_path, post_order):
    """Fix blog post navigation - remove duplicates and fix paths."""
    post_slug = post_path.parent.name
    
    if post_slug not in post_order:
        return False
    
    current_index = post_order.index(post_slug)
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Fix class_ to class first
            content = content.replace('class_="', 'class="')
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    changes_made = False
    
    # Remove all existing navigation
    existing_navs = soup.find_all('nav', class_='post-navigation')
    for nav in existing_navs:
        nav.decompose()
        changes_made = True
    
    # Calculate correct relative path - from post/slug/ to post/other-slug/
    # Only need one ../ because we're in post/slug/ and going to post/other-slug/
    relative_path = "../"
    
    # Find insertion point
    back_link = soup.find('a', class_='back-link')
    article = soup.find('article')
    
    if not (back_link or article):
        return False
    
    # Create new navigation
    nav_section = soup.new_tag('nav', class_='post-navigation')
    
    # Previous post (older - higher index in list)
    if current_index < len(post_order) - 1:
        prev_slug = post_order[current_index + 1]
        prev_div = soup.new_tag('div', class_='nav-item nav-prev')
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.string = '← Previous Post'
        prev_div.append(prev_link)
        nav_section.append(prev_div)
    
    # Next post (newer - lower index in list)
    if current_index > 0:
        next_slug = post_order[current_index - 1]
        next_div = soup.new_tag('div', class_='nav-item nav-next')
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_link.string = 'Next Post →'
        next_div.append(next_link)
        nav_section.append(next_div)
    
    if len(nav_section.contents) == 0:
        if changes_made:
            # Still save to remove duplicates
            pass
        else:
            return False
    
    # Insert navigation before back-link
    if back_link:
        back_link.insert_before('\n')
        back_link.insert_before(nav_section)
        changes_made = True
    elif article:
        article.append('\n')
        article.append(nav_section)
        changes_made = True
    
    # Verify paths exist
    if nav_section:
        links = nav_section.find_all('a', class_='nav-link')
        for link in links:
            href = link.get('href', '')
            if href:
                # Check if target exists
                target_path = post_path.parent.parent / href.replace('../', '')
                target_file = target_path / 'index.html' if target_path.is_dir() else target_path
                if not target_file.exists():
                    print(f"    ⚠️  Link target not found: {href} -> {target_file}")
    
    if changes_made or nav_section:
        try:
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"  ✅ Fixed navigation")
            return True
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
            return False
    
    return False


def main():
    """Main function."""
    print("=" * 60)
    print("Fixing blog post navigation links")
    print("=" * 60)
    
    blog_order = get_blog_post_order()
    print(f"\nFound {len(blog_order)} blog posts in order")
    
    fixed_count = 0
    if POSTS_DIR.exists():
        for post_dir in sorted(POSTS_DIR.iterdir()):
            if post_dir.is_dir():
                post_file = post_dir / "index.html"
                if post_file.exists():
                    print(f"\nProcessing: {post_dir.name}")
                    if fix_blog_navigation(post_file, blog_order):
                        fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


