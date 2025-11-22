#!/usr/bin/env python3
"""
Fix Previous/Next navigation in farm pages - ensure paths are correct.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
FARMS_DIR = BASE_DIR / "farms"


def get_farm_order():
    """Get ordered list of farms (alphabetical by directory name)."""
    if not FARMS_DIR.exists():
        return []
    
    farms = sorted([d.name for d in FARMS_DIR.iterdir() if d.is_dir()])
    return farms


def fix_farm_navigation(farm_path, farm_order):
    """Fix farm page navigation."""
    farm_slug = farm_path.parent.name
    
    if farm_slug not in farm_order:
        return False
    
    current_index = farm_order.index(farm_slug)
    
    try:
        with open(farm_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Fix class_ to class
            content = content.replace('class_="', 'class="')
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False
    
    # Remove all existing navigation
    existing_navs = soup.find_all('nav', class_='post-navigation')
    for nav in existing_navs:
        nav.decompose()
    
    # Calculate correct relative path - from farms/slug/ to farms/other-slug/
    relative_path = "../"
    
    # Find insertion point
    main = soup.find('main')
    footer = soup.find('footer')
    
    # Create new navigation
    nav_section = soup.new_tag('nav')
    nav_section['class'] = 'post-navigation'
    
    # Previous farm (alphabetically before)
    if current_index < len(farm_order) - 1:
        prev_slug = farm_order[current_index + 1]
        prev_div = soup.new_tag('div')
        prev_div['class'] = 'nav-item nav-prev'
        prev_link = soup.new_tag('a', href=f"{relative_path}{prev_slug}/")
        prev_link['class'] = 'nav-link'
        prev_link.string = '← Previous Farm'
        prev_div.append(prev_link)
        nav_section.append(prev_div)
    
    # Next farm (alphabetically after)
    if current_index > 0:
        next_slug = farm_order[current_index - 1]
        next_div = soup.new_tag('div')
        next_div['class'] = 'nav-item nav-next'
        next_link = soup.new_tag('a', href=f"{relative_path}{next_slug}/")
        next_link['class'] = 'nav-link'
        next_link.string = 'Next Farm →'
        next_div.append(next_link)
        nav_section.append(next_div)
    
    if len(nav_section.contents) == 0:
        # Still save to fix class_ issues
        try:
            with open(farm_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            return True
        except:
            return False
    
    # Insert navigation
    if footer:
        footer.insert_before('\n')
        footer.insert_before(nav_section)
    elif main:
        main.append('\n')
        main.append(nav_section)
    else:
        return False
    
    # Add CSS if not present
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
        with open(farm_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"  ❌ Error saving: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Fixing farm navigation links")
    print("=" * 60)
    
    farm_order = get_farm_order()
    print(f"\nFound {len(farm_order)} farms: {', '.join(farm_order)}")
    
    fixed_count = 0
    if FARMS_DIR.exists():
        for farm_dir in sorted(FARMS_DIR.iterdir()):
            if farm_dir.is_dir():
                farm_file = farm_dir / "index.html"
                if farm_file.exists():
                    print(f"\nProcessing: {farm_dir.name}")
                    if fix_farm_navigation(farm_file, farm_order):
                        fixed_count += 1
                        print(f"  ✅ Fixed navigation")
                    
                    # Verify links
                    try:
                        with open(farm_file, 'r', encoding='utf-8') as f:
                            soup = BeautifulSoup(f.read(), 'html.parser')
                        nav = soup.find('nav', class_='post-navigation')
                        if nav:
                            links = nav.find_all('a', class_='nav-link')
                            for link in links:
                                href = link.get('href', '')
                                if href:
                                    target_slug = href.replace('../', '').rstrip('/')
                                    target_path = farm_file.parent.parent / target_slug / 'index.html'
                                    exists = target_path.exists()
                                    status = "✅" if exists else "❌"
                                    print(f"    {link.get_text(strip=True)}: {href} {status}")
                    except:
                        pass
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed {fixed_count} farms")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()


