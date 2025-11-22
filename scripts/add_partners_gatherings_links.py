#!/usr/bin/env python3
"""
Add Partners and Gatherings links to blog post navigation menus.
"""

from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "post"


def add_partners_gatherings_links(post_path):
    """Add Partners and Gatherings links to navigation menus."""
    print(f"\nProcessing: {post_path.name}")
    
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    # Calculate relative path to root
    depth = len(post_path.parent.relative_to(BASE_DIR).parts)
    relative_path = "../" * depth if depth > 0 else ""
    
    nav = soup.find('nav')
    if not nav:
        print(f"  ⚠️  No nav found")
        return False
    
    # Find all nav-links menus (desktop and mobile)
    nav_links_menus = nav.find_all('ul', class_='nav-links')
    
    if not nav_links_menus:
        print(f"  ⚠️  No nav-links menus found")
        return False
    
    changes_made = False
    
    for menu in nav_links_menus:
        # Check if Partners link already exists
        partners_link = menu.find('a', href=lambda x: x and ('partner' in x.lower() or 'gathering' in x.lower()))
        if not partners_link:
            # Find Blog link to insert after
            blog_link = menu.find('a', href=lambda x: x and 'blog' in x.lower())
            
            if blog_link:
                blog_li = blog_link.find_parent('li')
                
                # Create Partners link
                partners_li = soup.new_tag('li')
                partners_a = soup.new_tag('a', href=f"{relative_path}partners/index.html")
                partners_a.string = 'Partners'
                partners_li.append(partners_a)
                
                # Insert Partners after Blog
                blog_li.insert_after(partners_li)
                
                # Create Gatherings link
                gatherings_li = soup.new_tag('li')
                gatherings_a = soup.new_tag('a', href=f"{relative_path}index.html#gatherings")
                gatherings_a.string = 'Gatherings'
                gatherings_li.append(gatherings_a)
                
                # Insert Gatherings after Partners
                partners_li.insert_after(gatherings_li)
                
                changes_made = True
                print(f"  ✅ Added Partners and Gatherings links")
            else:
                print(f"  ⚠️  Could not find Blog link to insert after")
    
    # Save if changes were made
    if changes_made:
        try:
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"  ✅ Saved changes")
            return True
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
            return False
    
    print(f"  ℹ️  No changes needed")
    return False


def main():
    """Main function."""
    print("=" * 60)
    print("Adding Partners and Gatherings links to blog posts")
    print("=" * 60)
    
    post_dirs = [d for d in POSTS_DIR.iterdir() if d.is_dir()]
    
    fixed_count = 0
    for post_dir in sorted(post_dirs):
        post_file = post_dir / "index.html"
        if post_file.exists():
            if add_partners_gatherings_links(post_file):
                fixed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} blog posts")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


