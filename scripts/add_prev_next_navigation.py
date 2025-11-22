#!/usr/bin/env python3
"""
Add Previous/Next navigation to blog posts, farms, and shipments.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"
FARMS_DIR = BASE_DIR / "farms"
SHIPMENTS_DIR = BASE_DIR / "shipments"
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


def get_farm_order():
    """Get ordered list of farms (alphabetical by directory name)."""
    if not FARMS_DIR.exists():
        return []
    
    farms = sorted([d.name for d in FARMS_DIR.iterdir() if d.is_dir()])
    return farms


def get_shipment_order():
    """Get ordered list of shipments (sorted by number in aglN format)."""
    if not SHIPMENTS_DIR.exists():
        return []
    
    shipments = []
    for d in SHIPMENTS_DIR.iterdir():
        if d.is_dir() and d.name.startswith('agl'):
            # Extract number from aglN
            match = re.search(r'agl(\d+)', d.name)
            if match:
                shipments.append((int(match.group(1)), d.name))
    
    # Sort by number (newest first - higher numbers first)
    shipments.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in shipments]


def add_blog_navigation(post_path, post_order):
    """Add Previous/Next navigation to a blog post."""
    # Extract slug from path
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
    
    # Calculate relative path
    depth = len(post_path.parent.relative_to(BASE_DIR).parts)
    relative_path = "../" * depth if depth > 0 else ""
    
    # Find the main/article or back-link to insert before
    back_link = soup.find('a', class_='back-link')
    main = soup.find('main')
    
    # Create navigation section
    nav_section = soup.new_tag('nav', class_='post-navigation')
    
    # Previous post
    if current_index < len(post_order) - 1:
        prev_slug = post_order[current_index + 1]
        prev_li = soup.new_tag('div', class_='nav-item nav-prev')
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.append(soup.new_string('← Previous Post'))
        prev_li.append(prev_link)
        nav_section.append(prev_li)
    
    # Next post
    if current_index > 0:
        next_slug = post_order[current_index - 1]
        next_li = soup.new_tag('div', class_='nav-item nav-next')
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_link.append(soup.new_string('Next Post →'))
        next_li.append(next_link)
        nav_section.append(next_li)
    
    if len(nav_section.contents) == 0:
        return False  # No navigation to add
    
    # Insert navigation before back-link or at end of main
    if back_link:
        back_link.insert_before(nav_section)
        back_link.insert_before(soup.new_string('\n'))
    elif main:
        main.append(nav_section)
    else:
        return False
    
    # Add CSS for navigation
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


def add_farm_navigation(farm_path, farm_order):
    """Add Previous/Next navigation to a farm page."""
    farm_slug = farm_path.parent.name
    
    if farm_slug not in farm_order:
        return False
    
    current_index = farm_order.index(farm_slug)
    
    try:
        with open(farm_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    depth = len(farm_path.parent.relative_to(BASE_DIR).parts)
    relative_path = "../" * depth if depth > 0 else ""
    
    # Find a good insertion point (before footer or at end of main)
    main = soup.find('main')
    footer = soup.find('footer')
    
    nav_section = soup.new_tag('nav', class_='post-navigation')
    
    if current_index < len(farm_order) - 1:
        prev_slug = farm_order[current_index + 1]
        prev_li = soup.new_tag('div', class_='nav-item nav-prev')
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.append(soup.new_string('← Previous Farm'))
        prev_li.append(prev_link)
        nav_section.append(prev_li)
    
    if current_index > 0:
        next_slug = farm_order[current_index - 1]
        next_li = soup.new_tag('div', class_='nav-item nav-next')
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_link.append(soup.new_string('Next Farm →'))
        next_li.append(next_link)
        nav_section.append(next_li)
    
    if len(nav_section.contents) == 0:
        return False
    
    if footer:
        footer.insert_before(nav_section)
    elif main:
        main.append(nav_section)
    else:
        return False
    
    # Add CSS if not present
    style_tag = soup.find('style')
    if style_tag and '.post-navigation' not in (style_tag.string or ""):
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
        with open(farm_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def add_shipment_navigation(shipment_path, shipment_order):
    """Add Previous/Next navigation to a shipment page."""
    shipment_slug = shipment_path.parent.name
    
    if shipment_slug not in shipment_order:
        return False
    
    current_index = shipment_order.index(shipment_slug)
    
    try:
        with open(shipment_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    depth = len(shipment_path.parent.relative_to(BASE_DIR).parts)
    relative_path = "../" * depth if depth > 0 else ""
    
    main = soup.find('main')
    footer = soup.find('footer')
    
    nav_section = soup.new_tag('nav', class_='post-navigation')
    
    if current_index < len(shipment_order) - 1:
        prev_slug = shipment_order[current_index + 1]
        prev_li = soup.new_tag('div', class_='nav-item nav-prev')
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.append(soup.new_string('← Previous Shipment'))
        prev_li.append(prev_link)
        nav_section.append(prev_li)
    
    if current_index > 0:
        next_slug = shipment_order[current_index - 1]
        next_li = soup.new_tag('div', class_='nav-item nav-next')
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_link.append(soup.new_string('Next Shipment →'))
        next_li.append(next_link)
        nav_section.append(next_li)
    
    if len(nav_section.contents) == 0:
        return False
    
    if footer:
        footer.insert_before(nav_section)
    elif main:
        main.append(nav_section)
    else:
        return False
    
    # Add CSS if not present
    style_tag = soup.find('style')
    if style_tag and '.post-navigation' not in (style_tag.string or ""):
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
        with open(shipment_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Adding Previous/Next navigation to blog posts, farms, and shipments")
    print("=" * 60)
    
    # Get orders
    print("\n📝 Getting blog post order...")
    blog_order = get_blog_post_order()
    print(f"   Found {len(blog_order)} blog posts")
    
    print("\n🌾 Getting farm order...")
    farm_order = get_farm_order()
    print(f"   Found {len(farm_order)} farms")
    
    print("\n📦 Getting shipment order...")
    shipment_order = get_shipment_order()
    print(f"   Found {len(shipment_order)} shipments")
    
    # Process blog posts
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
                    if add_blog_navigation(post_file, blog_order):
                        blog_count += 1
                        print(f"  ✅ Added navigation")
    
    # Process farms
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
                    if add_farm_navigation(farm_file, farm_order):
                        farm_count += 1
                        print(f"  ✅ Added navigation")
    
    # Process shipments
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
                    if add_shipment_navigation(shipment_file, shipment_order):
                        shipment_count += 1
                        print(f"  ✅ Added navigation")
    
    print("\n" + "=" * 60)
    print(f"✅ Added navigation to:")
    print(f"   - {blog_count} blog posts")
    print(f"   - {farm_count} farms")
    print(f"   - {shipment_count} shipments")
    print("=" * 60)


if __name__ == "__main__":
    main()


