#!/usr/bin/env python3
"""
Fix Previous/Next navigation in blog posts - ensure it's properly added and links work.
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
                # Extract slug from href like ../post/slug/
                match = re.search(r'\.\./post/([^/]+)/', href)
                if match:
                    post_order.append(match.group(1))
        
        return post_order
    except Exception as e:
        print(f"Error reading blog index: {e}")
        return []


def fix_blog_navigation(post_path, post_order):
    """Add or fix Previous/Next navigation to a blog post."""
    post_slug = post_path.parent.name
    
    if post_slug not in post_order:
        return False
    
    current_index = post_order.index(post_slug)
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    # Calculate relative path - from post/slug/ to root
    depth = len(post_path.parent.relative_to(BASE_DIR).parts)
    relative_path = "../" * depth if depth > 0 else ""
    
    # Remove existing navigation if present
    existing_nav = soup.find('nav', class_='post-navigation')
    if existing_nav:
        existing_nav.decompose()
    
    # Find insertion point - before back-link or at end of article/main
    back_link = soup.find('a', class_='back-link')
    article = soup.find('article')
    main = soup.find('main')
    
    # Create navigation section
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
        return False  # No navigation to add
    
    # Insert navigation
    if back_link:
        back_link.insert_before('\n')
        back_link.insert_before(nav_section)
    elif article:
        article.append('\n')
        article.append(nav_section)
    elif main:
        main.append('\n')
        main.append(nav_section)
    else:
        return False
    
    # Add CSS for navigation if not present
    style_tag = soup.find('style')
    if style_tag:
        style_content = style_tag.string or ""
        
        if '.post-navigation' not in style_content:
            nav_css = """
        
        /* Post Navigation */
        .post-navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 3rem 0 2rem;
            padding: 2rem 0;
            border-top: 2px solid var(--color-bg-light);
            border-bottom: 2px solid var(--color-bg-light);
            gap: 2rem;
        }
        
        .nav-item {
            flex: 1;
        }
        
        .nav-item.nav-next {
            text-align: right;
        }
        
        .nav-link {
            display: inline-block;
            color: var(--color-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 1rem;
            transition: color 0.3s;
            padding: 0.5rem 0;
        }
        
        .nav-link:hover {
            color: var(--color-primary);
        }
        
        @media (max-width: 768px) {
            .post-navigation {
                flex-direction: column;
                gap: 1.5rem;
            }
            
            .nav-item.nav-next {
                text-align: left;
            }
        }
        """
            style_tag.string += nav_css
    
    try:
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Fixing Previous/Next navigation in blog posts")
    print("=" * 60)
    
    print("\n📝 Getting blog post order...")
    blog_order = get_blog_post_order()
    print(f"   Found {len(blog_order)} blog posts")
    
    if len(blog_order) == 0:
        print("  ❌ No blog posts found in order")
        return
    
    print("\n" + "=" * 60)
    print("Processing Blog Posts")
    print("=" * 60)
    
    fixed_count = 0
    if POSTS_DIR.exists():
        for post_dir in sorted(POSTS_DIR.iterdir()):
            if post_dir.is_dir():
                post_file = post_dir / "index.html"
                if post_file.exists():
                    print(f"\nProcessing: {post_dir.name}")
                    if fix_blog_navigation(post_file, blog_order):
                        fixed_count += 1
                        print(f"  ✅ Added/fixed navigation")
                    
                    # Verify links
                    try:
                        with open(post_file, 'r', encoding='utf-8') as f:
                            soup = BeautifulSoup(f.read(), 'html.parser')
                        nav = soup.find('nav', class_='post-navigation')
                        if nav:
                            links = nav.find_all('a', class_='nav-link')
                            for link in links:
                                href = link.get('href', '')
                                if href:
                                    # Check if file exists
                                    target_path = post_file.parent.parent / href.replace('../', '') / 'index.html'
                                    exists = target_path.exists() if target_path else False
                                    print(f"    Link: {href} {'✅' if exists else '❌'}")
                    except:
                        pass
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed navigation in {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


