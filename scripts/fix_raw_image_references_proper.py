#!/usr/bin/env python3
"""
Fix image references from assets/raw folders properly.
Only handles actual assets/raw references, not legitimate image paths.
Moves images to appropriate locations and updates references.
"""

import os
import re
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "assets" / "raw"
IMAGES_DIR = BASE_DIR / "assets" / "images"

def fix_raw_image_references(file_path):
    """Fix all assets/raw image references in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    if 'assets/raw' not in content and 'assets\\raw' not in content:
        return False  # No raw references
    
    original_content = content
    soup = BeautifulSoup(content, 'html.parser')
    changed = False
    
    # Determine context for where to put images
    if 'post' in str(file_path):
        context = 'blog-posts'
        target_dir = IMAGES_DIR / 'blog-posts'
    elif 'event' in str(file_path):
        context = 'events'
        target_dir = IMAGES_DIR / 'events'
    elif 'shipment' in str(file_path):
        context = 'shipments'
        target_dir = IMAGES_DIR / 'shipments'
    else:
        context = 'general'
        target_dir = IMAGES_DIR
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Fix img tags with assets/raw
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if 'assets/raw' in src or 'assets\\raw' in src:
            # Extract the path part after assets/raw
            match = re.search(r'assets[/\\]raw[/\\](.+)', src.replace('\\', '/'))
            if match:
                raw_path = match.group(1)
                # Find the actual file
                raw_file = RAW_DIR / raw_path.replace('/', os.sep)
                
                if raw_file.exists():
                    # Copy to target directory
                    filename = raw_file.name
                    dest_file = target_dir / filename
                    
                    # Handle duplicates
                    counter = 1
                    while dest_file.exists() and dest_file.stat().st_size != raw_file.stat().st_size:
                        stem = raw_file.stem
                        suffix = raw_file.suffix
                        dest_file = target_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    if not dest_file.exists():
                        try:
                            shutil.copy2(raw_file, dest_file)
                            print(f"    ✅ Copied: {raw_path} -> assets/images/{context}/{dest_file.name}")
                        except Exception as e:
                            print(f"    ⚠️  Error copying {raw_file}: {e}")
                            continue
                    
                    # Calculate relative path from HTML file
                    html_dir = file_path.parent
                    try:
                        relative_path = os.path.relpath(dest_file, html_dir)
                        relative_path = relative_path.replace('\\', '/')
                        img['src'] = relative_path
                        changed = True
                        print(f"    ✅ Updated: {src} -> {relative_path}")
                    except Exception as e:
                        print(f"    ⚠️  Error calculating path: {e}")
                else:
                    print(f"    ⚠️  File not found: {raw_file}")
    
    # Fix background images in style attributes
    for tag in soup.find_all(style=True):
        style = tag.get('style', '')
        if 'assets/raw' in style or 'assets\\raw' in style:
            def replace_url(match):
                url = match.group(1).strip("'\"")
                if 'assets/raw' in url or 'assets\\raw' in url:
                    # Extract path
                    path_match = re.search(r'assets[/\\]raw[/\\](.+)', url.replace('\\', '/'))
                    if path_match:
                        raw_path = path_match.group(1)
                        raw_file = RAW_DIR / raw_path.replace('/', os.sep)
                        
                        if raw_file.exists():
                            # Copy to target
                            filename = raw_file.name
                            dest_file = target_dir / filename
                            
                            # Handle duplicates
                            counter = 1
                            while dest_file.exists() and dest_file.stat().st_size != raw_file.stat().st_size:
                                stem = raw_file.stem
                                suffix = raw_file.suffix
                                dest_file = target_dir / f"{stem}_{counter}{suffix}"
                                counter += 1
                            
                            if not dest_file.exists():
                                try:
                                    shutil.copy2(raw_file, dest_file)
                                    print(f"    ✅ Copied background image: {raw_path} -> assets/images/{context}/{dest_file.name}")
                                except Exception as e:
                                    print(f"    ⚠️  Error copying {raw_file}: {e}")
                                    return match.group(0)
                            
                            # Calculate relative path
                            html_dir = file_path.parent
                            try:
                                relative_path = os.path.relpath(dest_file, html_dir)
                                relative_path = relative_path.replace('\\', '/')
                                return f'url("{relative_path}")'
                            except Exception as e:
                                print(f"    ⚠️  Error calculating path: {e}")
                                return match.group(0)
                
                return match.group(0)
            
            new_style = re.sub(r'url\(["\']?([^"\')]+)["\']?\)', replace_url, style)
            if new_style != style:
                tag['style'] = new_style
                changed = True
    
    # Fix video poster attributes
    for video in soup.find_all('video'):
        poster = video.get('poster', '')
        if 'assets/raw' in poster or 'assets\\raw' in poster:
            match = re.search(r'assets[/\\]raw[/\\](.+)', poster.replace('\\', '/'))
            if match:
                raw_path = match.group(1)
                raw_file = RAW_DIR / raw_path.replace('/', os.sep)
                
                if raw_file.exists():
                    filename = raw_file.name
                    dest_file = target_dir / filename
                    
                    # Handle duplicates
                    counter = 1
                    while dest_file.exists() and dest_file.stat().st_size != raw_file.stat().st_size:
                        stem = raw_file.stem
                        suffix = raw_file.suffix
                        dest_file = target_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    if not dest_file.exists():
                        try:
                            shutil.copy2(raw_file, dest_file)
                            print(f"    ✅ Copied video poster: {raw_path} -> assets/images/{context}/{dest_file.name}")
                        except Exception as e:
                            print(f"    ⚠️  Error copying {raw_file}: {e}")
                            continue
                    
                    # Calculate relative path
                    html_dir = file_path.parent
                    try:
                        relative_path = os.path.relpath(dest_file, html_dir)
                        relative_path = relative_path.replace('\\', '/')
                        video['poster'] = relative_path
                        changed = True
                        print(f"    ✅ Updated video poster: {poster} -> {relative_path}")
                    except Exception as e:
                        print(f"    ⚠️  Error calculating path: {e}")
    
    # Fix onerror fallback images
    for tag in soup.find_all(onerror=True):
        onerror = tag.get('onerror', '')
        if 'assets/raw' in onerror or 'assets\\raw' in onerror:
            match = re.search(r'this\.src\s*=\s*["\']([^"\']+)["\']', onerror)
            if match:
                src = match.group(1)
                if 'assets/raw' in src or 'assets\\raw' in src:
                    path_match = re.search(r'assets[/\\]raw[/\\](.+)', src.replace('\\', '/'))
                    if path_match:
                        raw_path = path_match.group(1)
                        raw_file = RAW_DIR / raw_path.replace('/', os.sep)
                        
                        if raw_file.exists():
                            filename = raw_file.name
                            dest_file = target_dir / filename
                            
                            # Handle duplicates
                            counter = 1
                            while dest_file.exists() and dest_file.stat().st_size != raw_file.stat().st_size:
                                stem = raw_file.stem
                                suffix = raw_file.suffix
                                dest_file = target_dir / f"{stem}_{counter}{suffix}"
                                counter += 1
                            
                            if not dest_file.exists():
                                try:
                                    shutil.copy2(raw_file, dest_file)
                                    print(f"    ✅ Copied onerror image: {raw_path} -> assets/images/{context}/{dest_file.name}")
                                except Exception as e:
                                    print(f"    ⚠️  Error copying {raw_file}: {e}")
                                    continue
                            
                            # Calculate relative path
                            html_dir = file_path.parent
                            try:
                                relative_path = os.path.relpath(dest_file, html_dir)
                                relative_path = relative_path.replace('\\', '/')
                                new_onerror = onerror.replace(src, relative_path)
                                tag['onerror'] = new_onerror
                                changed = True
                                print(f"    ✅ Updated onerror: {src} -> {relative_path}")
                            except Exception as e:
                                print(f"    ⚠️  Error calculating path: {e}")
    
    if changed:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            return True
        except Exception as e:
            print(f"    ❌ Error writing {file_path}: {e}")
            return False
    
    return False

def main():
    """Fix all assets/raw image references."""
    print("Scanning for assets/raw image references...")
    print("=" * 60)
    
    # Find all HTML files
    html_files = []
    
    # Check all HTML files in the repo
    for html_file in BASE_DIR.rglob("*.html"):
        if 'node_modules' not in str(html_file) and '.git' not in str(html_file):
            html_files.append(html_file)
    
    # Filter to only files with assets/raw references
    files_with_raw = []
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                if 'assets/raw' in f.read() or 'assets\\raw' in f.read():
                    files_with_raw.append(html_file)
        except:
            pass
    
    print(f"Found {len(files_with_raw)} files with assets/raw references")
    print("=" * 60)
    
    fixed = 0
    skipped = 0
    
    for file_path in files_with_raw:
        print(f"\nProcessing: {file_path.relative_to(BASE_DIR)}")
        
        if fix_raw_image_references(file_path):
            fixed += 1
        else:
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Fixed: {fixed}")
    print(f"  ℹ️  Skipped/No changes: {skipped}")

if __name__ == "__main__":
    main()


