#!/usr/bin/env python3
"""
Update navigation menus across all pages to include Blog link.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent

def calculate_relative_path(file_path):
    """Calculate relative path from file to root."""
    depth = len(file_path.parent.relative_to(BASE_DIR).parts)
    if depth == 0:
        return ""
    return "../" * depth

def update_navigation_menu(html_content, relative_path):
    """Update navigation menu to include Blog link."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all nav-links and footer-links
    nav_links = soup.find_all('ul', class_='nav-links')
    footer_links = soup.find_all('ul', class_='footer-links')
    
    blog_path = f"{relative_path}blog/" if relative_path else "blog/"
    
    # Pattern to match navigation items
    nav_patterns = [
        (r'<li><a href="[^"]*shipments[^"]*">Shipments</a></li>', 
         f'<li><a href="{blog_path}">Blog</a></li>\n<li><a href="[^"]*shipments[^"]*">Shipments</a></li>'),
        (r'<li><a href="[^"]*#shipments[^"]*">Shipments</a></li>',
         f'<li><a href="{blog_path}">Blog</a></li>\n<li><a href="#shipments">Shipments</a></li>'),
    ]
    
    updated = False
    
    # Update nav-links
    for nav in nav_links:
        nav_html = str(nav)
        # Check if Blog is already present
        if 'href="blog/' in nav_html or 'href="../blog/' in nav_html or 'href="../../blog/' in nav_html:
            continue
        
        # Find Shipments link
        shipments_link = nav.find('a', href=re.compile(r'shipments|#shipments'))
        if shipments_link:
            # Insert Blog after Shipments
            shipments_li = shipments_link.find_parent('li')
            if shipments_li:
                blog_li = soup.new_tag('li')
                blog_a = soup.new_tag('a', href=blog_path)
                blog_a.string = 'Blog'
                blog_li.append(blog_a)
                shipments_li.insert_after('\n')
                shipments_li.insert_after(blog_li)
                updated = True
    
    # Update footer-links
    for footer in footer_links:
        footer_html = str(footer)
        # Check if Blog is already present
        if 'href="blog/' in footer_html or 'href="../blog/' in footer_html or 'href="../../blog/' in footer_html:
            continue
        
        # Find Shipments link
        shipments_link = footer.find('a', href=re.compile(r'shipments|#shipments'))
        if shipments_link:
            # Insert Blog after Shipments
            shipments_li = shipments_link.find_parent('li')
            if shipments_li:
                blog_li = soup.new_tag('li')
                blog_a = soup.new_tag('a', href=blog_path)
                blog_a.string = 'Blog'
                blog_li.append(blog_a)
                shipments_li.insert_after('\n')
                shipments_li.insert_after(blog_li)
                updated = True
    
    if updated:
        return str(soup)
    return None

def process_file(file_path):
    """Process a single HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False
    
    # Skip if it's the blog listing page itself
    if 'blog/index.html' in str(file_path):
        return False
    
    relative_path = calculate_relative_path(file_path)
    updated_content = update_navigation_menu(content, relative_path)
    
    if updated_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False
    
    return False

def main():
    """Update all HTML files."""
    html_files = list(BASE_DIR.rglob('*.html'))
    
    # Exclude scripts directory
    html_files = [f for f in html_files if 'scripts' not in str(f)]
    
    updated_count = 0
    skipped_count = 0
    
    print("Updating navigation menus...")
    print("=" * 60)
    
    for file_path in sorted(html_files):
        relative = file_path.relative_to(BASE_DIR)
        
        # Skip blog/index.html (already has Blog in nav)
        if str(relative) == 'blog/index.html':
            skipped_count += 1
            continue
        
        if process_file(file_path):
            print(f"✅ Updated: {relative}")
            updated_count += 1
        else:
            skipped_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Updated: {updated_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")

if __name__ == "__main__":
    main()

