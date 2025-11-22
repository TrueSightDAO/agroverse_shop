#!/usr/bin/env python3
"""
Fix navigation links and enhance them to show titles/names instead of generic text.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"
FARMS_DIR = BASE_DIR / "farms"
SHIPMENTS_DIR = BASE_DIR / "shipments"
BLOG_INDEX = BASE_DIR / "blog" / "index.html"


def get_title_from_page(page_path):
    """Extract title from a page (h1 or title tag)."""
    if not page_path.exists():
        return None
    
    try:
        with open(page_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
            if title and title.lower() not in ['blog', 'farm', 'shipment']:
                return title
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            # Remove site name suffix
            title = re.sub(r'\s*\|\s*Agroverse.*$', '', title, flags=re.IGNORECASE)
            if title:
                return title
        
        return None
    except:
        return None


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


def get_farm_order():
    """Get ordered list of farms."""
    if not FARMS_DIR.exists():
        return []
    return sorted([d.name for d in FARMS_DIR.iterdir() if d.is_dir()])


def get_shipment_order():
    """Get ordered list of shipments (sorted by number)."""
    if not SHIPMENTS_DIR.exists():
        return []
    
    shipments = []
    for d in SHIPMENTS_DIR.iterdir():
        if d.is_dir() and d.name.startswith('agl'):
            match = re.search(r'agl(\d+)', d.name)
            if match:
                shipments.append((int(match.group(1)), d.name))
    
    shipments.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in shipments]


def fix_blog_navigation(post_path, post_order):
    """Fix blog post navigation with titles."""
    post_slug = post_path.parent.name
    
    if post_slug not in post_order:
        return False
    
    current_index = post_order.index(post_slug)
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('class_="', 'class="')
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    # Remove existing navigation
    existing_navs = soup.find_all('nav', class_='post-navigation')
    for nav in existing_navs:
        nav.decompose()
    
    relative_path = "../"
    back_link = soup.find('a', class_='back-link')
    article = soup.find('article')
    
    if not (back_link or article):
        return False
    
    nav_section = soup.new_tag('nav')
    nav_section['class'] = 'post-navigation'
    
    # Previous post
    if current_index < len(post_order) - 1:
        prev_slug = post_order[current_index + 1]
        prev_path = post_path.parent.parent / prev_slug / 'index.html'
        prev_title = get_title_from_page(prev_path)
        prev_text = prev_title if prev_title else 'Previous Post'
        
        prev_div = soup.new_tag('div')
        prev_div['class'] = 'nav-item nav-prev'
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.append(soup.new_string('← '))
        prev_span = soup.new_tag('span', class_='nav-label')
        prev_span.string = prev_text
        prev_link.append(prev_span)
        prev_div.append(prev_link)
        nav_section.append(prev_div)
    
    # Next post
    if current_index > 0:
        next_slug = post_order[current_index - 1]
        next_path = post_path.parent.parent / next_slug / 'index.html'
        next_title = get_title_from_page(next_path)
        next_text = next_title if next_title else 'Next Post'
        
        next_div = soup.new_tag('div')
        next_div['class'] = 'nav-item nav-next'
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_span = soup.new_tag('span', class_='nav-label')
        next_span.string = next_text
        next_link.append(next_span)
        next_link.append(soup.new_string(' →'))
        next_div.append(next_link)
        nav_section.append(next_div)
    
    if len(nav_section.contents) == 0:
        return False
    
    if back_link:
        back_link.insert_before('\n')
        back_link.insert_before(nav_section)
    elif article:
        article.append('\n')
        article.append(nav_section)
    
    # Add CSS for nav-label if not present
    style_tag = soup.find('style')
    if style_tag:
        style_content = style_tag.string or ""
        if '.nav-label' not in style_content:
            nav_css = """
        
        .nav-label {
            font-weight: 600;
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


def fix_farm_navigation(farm_path, farm_order):
    """Fix farm navigation with names."""
    farm_slug = farm_path.parent.name
    
    if farm_slug not in farm_order:
        return False
    
    current_index = farm_order.index(farm_slug)
    
    try:
        with open(farm_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('class_="', 'class="')
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    existing_navs = soup.find_all('nav', class_='post-navigation')
    for nav in existing_navs:
        nav.decompose()
    
    relative_path = "../"
    main = soup.find('main')
    footer = soup.find('footer')
    
    nav_section = soup.new_tag('nav')
    nav_section['class'] = 'post-navigation'
    
    if current_index < len(farm_order) - 1:
        prev_slug = farm_order[current_index + 1]
        prev_path = farm_path.parent.parent / prev_slug / 'index.html'
        prev_title = get_title_from_page(prev_path)
        prev_text = prev_title if prev_title else prev_slug.replace('-', ' ').title()
        
        prev_div = soup.new_tag('div')
        prev_div['class'] = 'nav-item nav-prev'
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.append(soup.new_string('← '))
        prev_span = soup.new_tag('span', class_='nav-label')
        prev_span.string = prev_text
        prev_link.append(prev_span)
        prev_div.append(prev_link)
        nav_section.append(prev_div)
    
    if current_index > 0:
        next_slug = farm_order[current_index - 1]
        next_path = farm_path.parent.parent / next_slug / 'index.html'
        next_title = get_title_from_page(next_path)
        next_text = next_title if next_title else next_slug.replace('-', ' ').title()
        
        next_div = soup.new_tag('div')
        next_div['class'] = 'nav-item nav-next'
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_span = soup.new_tag('span', class_='nav-label')
        next_span.string = next_text
        next_link.append(next_span)
        next_link.append(soup.new_string(' →'))
        next_div.append(next_link)
        nav_section.append(next_div)
    
    if len(nav_section.contents) == 0:
        return False
    
    if footer:
        footer.insert_before('\n')
        footer.insert_before(nav_section)
    elif main:
        main.append('\n')
        main.append(nav_section)
    
    style_tag = soup.find('style')
    if style_tag:
        style_content = style_tag.string or ""
        if '.nav-label' not in style_content:
            nav_css = """
        
        .nav-label {
            font-weight: 600;
        }
        """
            style_tag.string += nav_css
    
    try:
        with open(farm_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def fix_shipment_navigation(shipment_path, shipment_order):
    """Fix shipment navigation with titles."""
    shipment_slug = shipment_path.parent.name
    
    if shipment_slug not in shipment_order:
        return False
    
    current_index = shipment_order.index(shipment_slug)
    
    try:
        with open(shipment_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('class_="', 'class="')
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    existing_navs = soup.find_all('nav', class_='post-navigation')
    for nav in existing_navs:
        nav.decompose()
    
    relative_path = "../"
    main = soup.find('main')
    footer = soup.find('footer')
    
    nav_section = soup.new_tag('nav')
    nav_section['class'] = 'post-navigation'
    
    if current_index < len(shipment_order) - 1:
        prev_slug = shipment_order[current_index + 1]
        prev_path = shipment_path.parent.parent / prev_slug / 'index.html'
        prev_title = get_title_from_page(prev_path)
        prev_text = prev_title if prev_title else prev_slug.upper()
        
        prev_div = soup.new_tag('div')
        prev_div['class'] = 'nav-item nav-prev'
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.append(soup.new_string('← '))
        prev_span = soup.new_tag('span', class_='nav-label')
        prev_span.string = prev_text
        prev_link.append(prev_span)
        prev_div.append(prev_link)
        nav_section.append(prev_div)
    
    if current_index > 0:
        next_slug = shipment_order[current_index - 1]
        next_path = shipment_path.parent.parent / next_slug / 'index.html'
        next_title = get_title_from_page(next_path)
        next_text = next_title if next_title else next_slug.upper()
        
        next_div = soup.new_tag('div')
        next_div['class'] = 'nav-item nav-next'
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_span = soup.new_tag('span', class_='nav-label')
        next_span.string = next_text
        next_link.append(next_span)
        next_link.append(soup.new_string(' →'))
        next_div.append(next_link)
        nav_section.append(next_div)
    
    if len(nav_section.contents) == 0:
        return False
    
    if footer:
        footer.insert_before('\n')
        footer.insert_before(nav_section)
    elif main:
        main.append('\n')
        main.append(nav_section)
    
    style_tag = soup.find('style')
    if style_tag:
        style_content = style_tag.string or ""
        if '.nav-label' not in style_content:
            nav_css = """
        
        .nav-label {
            font-weight: 600;
        }
        """
            style_tag.string += nav_css
    
    try:
        with open(shipment_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Fixing navigation with titles for blogs, farms, and shipments")
    print("=" * 60)
    
    blog_order = get_blog_post_order()
    farm_order = get_farm_order()
    shipment_order = get_shipment_order()
    
    print(f"\n📝 Blog posts: {len(blog_order)}")
    print(f"🌾 Farms: {len(farm_order)}")
    print(f"📦 Shipments: {len(shipment_order)}")
    
    # Fix blogs
    print("\n" + "=" * 60)
    print("Processing Blog Posts")
    print("=" * 60)
    blog_count = 0
    if POSTS_DIR.exists():
        for post_dir in sorted(POSTS_DIR.iterdir()):
            if post_dir.is_dir():
                post_file = post_dir / "index.html"
                if post_file.exists():
                    print(f"\nProcessing: {post_dir.name}")
                    if fix_blog_navigation(post_file, blog_order):
                        blog_count += 1
                        print(f"  ✅ Fixed navigation with titles")
    
    # Fix farms
    print("\n" + "=" * 60)
    print("Processing Farms")
    print("=" * 60)
    farm_count = 0
    if FARMS_DIR.exists():
        for farm_dir in sorted(FARMS_DIR.iterdir()):
            if farm_dir.is_dir():
                farm_file = farm_dir / "index.html"
                if farm_file.exists():
                    print(f"\nProcessing: {farm_dir.name}")
                    if fix_farm_navigation(farm_file, farm_order):
                        farm_count += 1
                        print(f"  ✅ Fixed navigation with titles")
    
    # Fix shipments
    print("\n" + "=" * 60)
    print("Processing Shipments")
    print("=" * 60)
    shipment_count = 0
    if SHIPMENTS_DIR.exists():
        for shipment_dir in sorted(SHIPMENTS_DIR.iterdir()):
            if shipment_dir.is_dir():
                shipment_file = shipment_dir / "index.html"
                if shipment_file.exists():
                    print(f"\nProcessing: {shipment_dir.name}")
                    if fix_shipment_navigation(shipment_file, shipment_order):
                        shipment_count += 1
                        print(f"  ✅ Fixed navigation with titles")
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed navigation with titles:")
    print(f"   - {blog_count} blog posts")
    print(f"   - {farm_count} farms")
    print(f"   - {shipment_count} shipments")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

