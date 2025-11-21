#!/usr/bin/env python3
"""
Add mobile-responsive hamburger menu to all HTML pages.
Replaces the current navigation with a hamburger menu on mobile devices.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent

def add_hamburger_menu(file_path):
    """Add hamburger menu to an HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    original_content = str(soup)
    
    # Check if hamburger menu already exists
    if 'hamburger' in content.lower() or 'mobile-menu-toggle' in content:
        return False  # Already has hamburger menu
    
    # Find the nav element
    nav = soup.find('nav')
    if not nav:
        return False  # No nav found
    
    # Create hamburger button
    hamburger = soup.new_tag('button', **{
        'class': 'mobile-menu-toggle',
        'aria-label': 'Toggle navigation menu',
        'aria-expanded': 'false'
    })
    hamburger.append(soup.new_tag('span', class_='hamburger-line'))
    hamburger.append(soup.new_tag('span', class_='hamburger-line'))
    hamburger.append(soup.new_tag('span', class_='hamburger-line'))
    
    # Insert hamburger button before nav-links
    nav_links = nav.find(class_='nav-links') or nav.find('ul')
    if nav_links:
        # Insert before nav_links
        nav_links.insert_before(hamburger)
    
    # Add class to nav-links for mobile menu
    if nav_links:
        existing_classes = nav_links.get('class', [])
        if not isinstance(existing_classes, list):
            existing_classes = [existing_classes]
        existing_classes.append('mobile-menu')
        nav_links['class'] = existing_classes
    
    # Add CSS for hamburger menu in style tag
    style_tag = soup.find('style')
    if style_tag:
        style_content = style_tag.string or ''
        
        # Check if hamburger styles already exist
        if 'mobile-menu-toggle' not in style_content:
            hamburger_css = """
        
        /* Mobile Hamburger Menu */
        .mobile-menu-toggle {
            display: none;
            flex-direction: column;
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            z-index: 1001;
        }
        
        .hamburger-line {
            width: 25px;
            height: 3px;
            background-color: var(--color-text);
            margin: 3px 0;
            transition: 0.3s;
            border-radius: 2px;
        }
        
        .mobile-menu-toggle[aria-expanded="true"] .hamburger-line:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .mobile-menu-toggle[aria-expanded="true"] .hamburger-line:nth-child(2) {
            opacity: 0;
        }
        
        .mobile-menu-toggle[aria-expanded="true"] .hamburger-line:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
        
        @media (max-width: 768px) {
            .mobile-menu-toggle {
                display: flex;
            }
            
            .nav-links.mobile-menu {
                position: fixed;
                top: 0;
                right: -100%;
                height: 100vh;
                width: 80%;
                max-width: 300px;
                background-color: var(--color-bg);
                flex-direction: column;
                align-items: flex-start;
                padding: 5rem 2rem 2rem;
                box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
                transition: right 0.3s ease;
                z-index: 1000;
                gap: 1.5rem;
                overflow-y: auto;
            }
            
            .nav-links.mobile-menu.active {
                right: 0;
            }
            
            .nav-links.mobile-menu li {
                width: 100%;
                border-bottom: 1px solid var(--color-bg-light);
                padding-bottom: 1rem;
            }
            
            .nav-links.mobile-menu a {
                font-size: 1.1rem;
                width: 100%;
                display: block;
            }
            
            .mobile-menu-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 999;
            }
            
            .mobile-menu-overlay.active {
                display: block;
            }
            
            header {
                padding: 1rem 1.5rem;
            }
            
            .logo img {
                height: 48px;
            }
            
            nav {
                position: relative;
            }
        }
        
        @media (max-width: 480px) {
            header {
                padding: 0.75rem 1rem;
            }
            
            .logo img {
                height: 40px;
            }
        }"""
            
            # Insert before the last closing brace of style tag or append
            if style_content.strip():
                style_tag.string = style_content + hamburger_css
            else:
                style_tag.string = hamburger_css
    
    # Add overlay div before closing body
    body = soup.find('body')
    if body:
        overlay = soup.new_tag('div', class_='mobile-menu-overlay')
        body.append(overlay)
    
    # Add JavaScript for hamburger menu functionality
    script = soup.new_tag('script')
    script.string = """
    document.addEventListener('DOMContentLoaded', function() {
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        const overlay = document.querySelector('.mobile-menu-overlay');
        
        if (menuToggle && mobileMenu) {
            menuToggle.addEventListener('click', function() {
                const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
                
                menuToggle.setAttribute('aria-expanded', !isExpanded);
                mobileMenu.classList.toggle('active');
                
                if (overlay) {
                    overlay.classList.toggle('active');
                }
                
                // Prevent body scroll when menu is open
                if (!isExpanded) {
                    document.body.style.overflow = 'hidden';
                } else {
                    document.body.style.overflow = '';
                }
            });
            
            // Close menu when clicking overlay
            if (overlay) {
                overlay.addEventListener('click', function() {
                    menuToggle.setAttribute('aria-expanded', 'false');
                    mobileMenu.classList.remove('active');
                    overlay.classList.remove('active');
                    document.body.style.overflow = '';
                });
            }
            
            // Close menu when clicking a link
            const menuLinks = mobileMenu.querySelectorAll('a');
            menuLinks.forEach(function(link) {
                link.addEventListener('click', function() {
                    menuToggle.setAttribute('aria-expanded', 'false');
                    mobileMenu.classList.remove('active');
                    if (overlay) {
                        overlay.classList.remove('active');
                    }
                    document.body.style.overflow = '';
                });
            });
            
            // Close menu on window resize if it becomes desktop view
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    menuToggle.setAttribute('aria-expanded', 'false');
                    mobileMenu.classList.remove('active');
                    if (overlay) {
                        overlay.classList.remove('active');
                    }
                    document.body.style.overflow = '';
                }
            });
        }
    });
    """
    
    # Insert script before closing body tag
    if body:
        body.append(script)
    
    # Write updated content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def main():
    """Add hamburger menu to all HTML pages."""
    print("Adding mobile hamburger menu to all pages...")
    print("=" * 60)
    
    # Find all HTML files
    html_files = []
    
    # Find HTML files in website directories (exclude assets/raw)
    directories_to_check = [
        BASE_DIR,
        BASE_DIR / 'post',
        BASE_DIR / 'event-details-registration',
        BASE_DIR / 'category',
        BASE_DIR / 'product-page',
        BASE_DIR / 'farms',
        BASE_DIR / 'shipments',
        BASE_DIR / 'partners',
    ]
    
    for directory in directories_to_check:
        if directory.exists():
            html_files.extend(list(directory.rglob('*.html')))
    
    # Remove duplicates and filter out node_modules, .git, assets/raw, etc.
    html_files = list(set(html_files))
    html_files = [f for f in html_files 
                  if 'node_modules' not in str(f) 
                  and '.git' not in str(f)
                  and 'assets/raw' not in str(f)
                  and f.is_file()]
    
    print(f"Found {len(html_files)} HTML files")
    print("=" * 60)
    
    fixed = 0
    skipped = 0
    errors = []
    
    for file_path in sorted(html_files):
        print(f"\nProcessing: {file_path.relative_to(BASE_DIR)}")
        
        if add_hamburger_menu(file_path):
            fixed += 1
            print(f"  ✅ Added hamburger menu")
        else:
            skipped += 1
            print(f"  ℹ️  Skipped (already has menu or no nav found)")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Updated: {fixed}")
    print(f"  ℹ️  Skipped: {skipped}")
    if errors:
        print(f"  ❌ Errors: {len(errors)}")

if __name__ == "__main__":
    main()

