#!/usr/bin/env python3
"""
Update blog index page with actual images from blog posts.
Extracts the first/main image from each blog post and updates the blog index.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
BLOG_INDEX = BASE_DIR / "blog" / "index.html"
POSTS_DIR = BASE_DIR / "post"

# URL to slug mapping
URL_TO_SLUG = {
    "/post/how-stem-cells-regenerate-with-regular-cacao-consumption/": "how-stem-cells-regenerate-with-regular-cacao-consumption",
    "/post/the-joy-of-cacao-circles-connections-and-community/": "the-joy-of-cacao-circles-connections-and-community",
    "/post/vote-for-the-artwork-on-the-first-series-of-our-2024-limited-edition-paulo-s-farm-cacao-collection/": "vote-for-the-artwork-on-the-first-series-of-our-2024-limited-edition-paulo-s-farm-cacao-collection",
    "/post/the-heart-of-brazilian-cacao-bahia-and-amazon-origins/": "the-heart-of-brazilian-cacao-bahia-and-amazon-origins",
    "/post/the-connection-between-wildfires-and-climate-change-a-growing-global-crisis/": "the-connection-between-wildfires-and-climate-change-a-growing-global-crisis",
    "/post/okanogan-regenerative-cacao-journey/": "okanogan-regenerative-cacao-journey",
    "/post/unveiling-cacao-bean-flavor-profiles-insights-from-global-tasting-tools-and-brazilian-expertise/": "unveiling-cacao-bean-flavor-profiles-insights-from-global-tasting-tools-and-brazilian-expertise",
    "/post/ceremonial-cacao-and-the-art-of-being-from-biohacking-to-presence/": "ceremonial-cacao-and-the-art-of-being-from-biohacking-to-presence",
    "/post/understanding-cabruca-a-traditional-agroforestry-practice-for-amazonian-rainforest-conservation/": "understanding-cabruca-a-traditional-agroforestry-practice-for-amazonian-rainforest-conservation",
    "/post/trends-driving-deforestation-in-the-amazon-rainforest-and-how-agroforestry-can-reverse-them/": "trends-driving-deforestation-in-the-amazon-rainforest-and-how-agroforestry-can-reverse-them",
    "/post/agroverse-partners-with-mestre-bico-duro-to-bring-capoeira-fitness-and-cacao-circle-gatherings-to-th/": "agroverse-partners-with-mestre-bico-duro-to-bring-capoeira-fitness-and-cacao-circle-gatherings-to-th",
    "/post/agroverse-and-the-center-sf-a-partnership-rooted-in-regeneration-and-community/": "agroverse-and-the-center-sf-a-partnership-rooted-in-regeneration-and-community",
    "/post/agroverse-partners-with-green-gulch-zen-monastery-to-offer-regenerative-cacao-nibs-to-marin-county-c/": "agroverse-partners-with-green-gulch-zen-monastery-to-offer-regenerative-cacao-nibs-to-marin-county-c",
}

def extract_first_image(post_dir):
    """Extract the first image from a blog post."""
    post_file = post_dir / "index.html"
    if not post_file.exists():
        return None
    
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find first image in blog content (skip logos, icons)
        images = soup.select('.blog-content img')
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            # Skip logos, icons, and social media images
            if any(skip in src.lower() or skip in alt for skip in ['logo', 'icon', 'avatar', 'wix', 'facebook', 'twitter', 'instagram']):
                continue
            
            # Convert relative paths to paths relative to blog/index.html
            if src.startswith('../../'):
                # Already relative from post/slug/ to root, need to go from blog/ to root
                return src.replace('../../', '../')
            elif src.startswith('../'):
                # From post/slug/ to assets, need to adjust for blog/ location
                return src
            elif src.startswith('http'):
                # External URL - keep as is
                return src
            elif src.startswith('/'):
                # Absolute path - convert to relative
                return '..' + src
            else:
                # Relative path - assume it's relative to assets
                return f'../assets/{src}' if not src.startswith('assets/') else f'../{src}'
        
        return None
    except Exception as e:
        print(f"    ⚠️  Error extracting image from {post_dir}: {e}")
        return None

def update_blog_index():
    """Update blog index with images from blog posts."""
    if not BLOG_INDEX.exists():
        print(f"❌ Blog index not found: {BLOG_INDEX}")
        return
    
    print("Updating blog index with images from blog posts...")
    print("=" * 60)
    
    try:
        with open(BLOG_INDEX, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        print(f"❌ Error reading blog index: {e}")
        return
    
    # Find all blog card links
    blog_cards = soup.select('.blog-card-link')
    print(f"Found {len(blog_cards)} blog cards")
    
    updated_count = 0
    
    for card in blog_cards:
        # Get the href to identify which post this is
        href = card.get('href', '')
        
        # Find the slug from the href
        slug = None
        for url, url_slug in URL_TO_SLUG.items():
            if url in href or href.endswith(url_slug + '/'):
                slug = url_slug
                break
        
        # Also try to extract slug from href directly
        if not slug:
            match = re.search(r'/post/([^/]+)/', href)
            if match:
                slug = match.group(1)
        
        if not slug:
            print(f"  ⚠️  Could not find slug for: {href}")
            continue
        
        print(f"\nProcessing: {slug}")
        
        # Find the post directory
        post_dir = POSTS_DIR / slug
        if not post_dir.exists():
            print(f"  ⚠️  Post directory not found: {post_dir}")
            continue
        
        # Extract first image
        image_src = extract_first_image(post_dir)
        
        if image_src:
            # Find the image container
            image_container = card.select_one('.blog-card-image-container')
            if image_container:
                # Remove placeholder if it exists
                placeholder = image_container.find(class_='blog-card-image-placeholder')
                if placeholder:
                    placeholder.decompose()
                
                # Check if image already exists
                existing_img = image_container.find('img', class_='blog-card-image')
                if existing_img:
                    existing_img['src'] = image_src
                else:
                    # Create new image tag
                    new_img = soup.new_tag('img', src=image_src, alt=slug.replace('-', ' ').title(), class_='blog-card-image', loading='lazy')
                    image_container.insert(0, new_img)
                
                print(f"  ✅ Added image: {image_src}")
                updated_count += 1
            else:
                print(f"  ⚠️  Could not find image container")
        else:
            print(f"  ℹ️  No image found, keeping placeholder")
    
    # Save updated HTML
    try:
        with open(BLOG_INDEX, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print("\n" + "=" * 60)
        print(f"✅ Updated blog index with {updated_count} images")
    except Exception as e:
        print(f"\n❌ Error saving blog index: {e}")

if __name__ == "__main__":
    update_blog_index()

