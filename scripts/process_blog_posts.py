#!/usr/bin/env python3
"""
Process blog posts from raw HTML files and create clean blog post pages.

This script:
1. Reads raw blog post HTML files from assets/raw/blogs/
2. Extracts title, content, images, and metadata
3. Generates clean blog post HTML files matching the site template
4. Saves them in the /post/ directory structure matching the original URLs
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

# Base directory
BASE_DIR = Path(__file__).parent.parent
RAW_BLOGS_DIR = BASE_DIR / "assets" / "raw" / "blogs"
POSTS_DIR = BASE_DIR / "post"

# URL to slug mapping based on user's URLs
URL_TO_SLUG = {
    "the-heart-of-brazilian-cacao-bahia-and-amazon-origins": "The Heart of Brazilian Cacao_ Bahia and Amazon Origins",
    "unveiling-cacao-bean-flavor-profiles-insights-from-global-tasting-tools-and-brazilian-expertise": "Unveiling Cacao Bean Flavor Profiles_ Insights from Global Tasting Tools and Brazilian Expertise",
    "okanogan-regenerative-cacao-journey": "Okanogan Regenerative Cacao Journey",
    "vote-for-the-artwork-on-the-first-series-of-our-2024-limited-edition-paulo-s-farm-cacao-collection": "Vote for the Artwork on the First Series of Our 2024 Limited-Edition Paulo's Farm Cacao Collection",
    "ceremonial-cacao-and-the-art-of-being-from-biohacking-to-presence": "Ceremonial Cacao and the Art of Being_ From Biohacking to Presence",
    "the-connection-between-wildfires-and-climate-change-a-growing-global-crisis": "The Connection Between Wildfires and Climate Change_ A Growing Global Crisis",
    "agroverse-and-the-center-sf-a-partnership-rooted-in-regeneration-and-community": "Agroverse and the Center SF_ A Partnership Rooted in Regeneration and Community",
    "trends-driving-deforestation-in-the-amazon-rainforest-and-how-agroforestry-can-reverse-them": "Trends Driving Deforestation in the Amazon Rainforest and How Agroforestry Can Reverse Them",
    "agroverse-partners-with-green-gulch-zen-monastery-to-offer-regenerative-cacao-nibs-to-marin-county-c": "Agroverse Partners with Green Gulch Zen Monastery to Offer Regenerative Amazonian Cacao Nibs to Marin County Community",
    "how-stem-cells-regenerate-with-regular-cacao-consumption": "How Stem Cells Regenerate with Regular Cacao Consumption",
    "agroverse-partners-with-mestre-bico-duro-to-bring-capoeira-fitness-and-cacao-circle-gatherings-to-th": "Agroverse Partners with Mestre Bico Duro to Bring Capoeira Fitness and Cacao Circle Gatherings to the",
    "the-joy-of-cacao-circles-connections-and-community": "The Joy of Cacao Circles_ Connections and Community",
    "understanding-cabruca-a-traditional-agroforestry-practice-for-amazonian-rainforest-conservation": "Understanding Cabruca_ A Traditional Agroforestry Practice for Amazonian Rainforest Conservation"
}

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_blog_content(html_file_path):
    """Extract blog post content from raw HTML file."""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"Error reading {html_file_path}: {e}")
        return None
    
    # Extract title
    title = None
    if soup.title:
        title = soup.title.string.strip()
        # Remove " | Agroverse" suffix if present
        title = re.sub(r'\s*\|\s*Agroverse\s*$', '', title)
    
    # Try to find h1 as title
    h1 = soup.find('h1')
    if h1 and not title:
        title = h1.get_text().strip()
    
    # Extract meta description
    meta_desc = None
    meta_desc_tag = soup.find('meta', property='og:description') or soup.find('meta', {'name': 'description'})
    if meta_desc_tag:
        meta_desc = meta_desc_tag.get('content', '')
    
    # Extract published date
    published_date = None
    pub_date_tag = soup.find('meta', property='article:published_time')
    if pub_date_tag:
        pub_date_str = pub_date_tag.get('content', '')
        try:
            published_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # Extract author
    author = None
    author_tag = soup.find('meta', property='article:author')
    if author_tag:
        author = author_tag.get('content', '')
    
    # Extract main content - look for article, main, or rich-text content
    content_html = None
    
    # Try various selectors for blog content
    content_selectors = [
        'article',
        'main',
        '[class*="rich-text"]',
        '[class*="blog-post"]',
        '[class*="post-content"]',
        '[data-testid*="richText"]'
    ]
    
    for selector in content_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            content_html = str(content_elem)
            break
    
    # If no specific content found, try to get body content excluding scripts/nav
    if not content_html:
        body = soup.find('body')
        if body:
            # Remove scripts, styles, nav elements
            for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            content_html = str(body)
    
    # Extract images
    images = []
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src', '') or img.get('data-src', '')
        if src and not any(skip in src.lower() for skip in ['logo', 'icon', 'avatar']):
            # Check if it's a local file reference
            if src.startswith('./') or not src.startswith('http'):
                # Try to find corresponding file in _files directory
                img_file = html_file_path.parent / html_file_path.stem.replace('.html', '_files') / Path(src).name
                if not img_file.exists() and '_files' in str(src):
                    # Try extracting from _files path
                    match = re.search(r'([^/]+_files/[^/]+)', src)
                    if match:
                        img_file = html_file_path.parent / match.group(1)
                
                if img_file.exists():
                    images.append(str(img_file.relative_to(BASE_DIR)))
            else:
                images.append(src)
    
    return {
        'title': title or 'Untitled Blog Post',
        'description': meta_desc or '',
        'content': content_html or '',
        'published_date': published_date,
        'author': author,
        'images': images[:10]  # Limit to 10 images
    }

def generate_blog_post_html(blog_data, url_slug):
    """Generate clean HTML for a blog post using the site template."""
    title = blog_data['title']
    description = blog_data['description'] or f"Read about {title} on Agroverse."
    content = blog_data['content']
    published_date = blog_data['published_date']
    author = blog_data['author'] or 'Agroverse Team'
    
    # Format date
    date_str = ''
    if published_date:
        date_str = published_date.strftime('%B %d, %Y')
    
    # Calculate relative path for assets (from /post/slug/ to root)
    relative_path = '../../'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    
    <!-- SEO Meta Tags -->
    <title>{title} | Agroverse</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="https://www.agroverse.shop/post/{url_slug}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://www.agroverse.shop/post/{url_slug}">
    <meta property="og:title" content="{title} | Agroverse">
    <meta property="og:description" content="{description}">
    <meta property="article:author" content="{author}">
    {f'<meta property="article:published_time" content="{published_date.isoformat()}">' if published_date else ''}
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://www.agroverse.shop/post/{url_slug}">
    <meta property="twitter:title" content="{title} | Agroverse">
    <meta property="twitter:description" content="{description}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/jpeg" href="{relative_path}assets/images/logo/agroverse-logo.jpeg">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Open+Sans:wght@400;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --color-primary: #3b3333;
            --color-secondary: #4d4d4d;
            --color-accent: #fefc8f;
            --color-text: #3b3333;
            --color-text-light: #756F63;
            --color-bg: #ffffff;
            --color-bg-light: #f7f7f7;
            --font-heading: 'Playfair Display', serif;
            --font-body: 'Open Sans', sans-serif;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--font-body);
            color: var(--color-text);
            line-height: 1.6;
            background-color: var(--color-bg);
        }}
        
        /* Header */
        header {{
            background-color: var(--color-bg);
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        nav {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo img {{
            height: 61px;
            width: auto;
        }}
        
        .nav-links {{
            display: flex;
            gap: 2rem;
            list-style: none;
        }}
        
        .nav-links a {{
            color: var(--color-text);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }}
        
        .nav-links a:hover {{
            color: var(--color-secondary);
        }}
        
        /* Blog Post */
        .blog-container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}
        
        .blog-header {{
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 2px solid var(--color-bg-light);
        }}
        
        .blog-title {{
            font-family: var(--font-heading);
            font-size: 2.5rem;
            color: var(--color-primary);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}
        
        .blog-meta {{
            color: var(--color-text-light);
            font-size: 0.95rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .blog-content {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--color-text);
        }}
        
        .blog-content h1,
        .blog-content h2,
        .blog-content h3 {{
            font-family: var(--font-heading);
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: var(--color-primary);
        }}
        
        .blog-content h1 {{
            font-size: 2rem;
        }}
        
        .blog-content h2 {{
            font-size: 1.75rem;
        }}
        
        .blog-content h3 {{
            font-size: 1.5rem;
        }}
        
        .blog-content p {{
            margin-bottom: 1.5rem;
        }}
        
        .blog-content img {{
            max-width: 100%;
            height: auto;
            margin: 2rem 0;
            border-radius: 8px;
        }}
        
        .blog-content a {{
            color: var(--color-secondary);
            text-decoration: underline;
        }}
        
        .blog-content a:hover {{
            color: var(--color-primary);
        }}
        
        .blog-content ul,
        .blog-content ol {{
            margin-left: 2rem;
            margin-bottom: 1.5rem;
        }}
        
        .blog-content li {{
            margin-bottom: 0.5rem;
        }}
        
        .back-link {{
            display: inline-block;
            margin-top: 3rem;
            color: var(--color-secondary);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .back-link:hover {{
            color: var(--color-primary);
        }}
        
        @media (max-width: 768px) {{
            .blog-title {{
                font-size: 2rem;
            }}
            
            .blog-container {{
                padding: 2rem 1rem;
            }}
            
            .nav-links {{
                gap: 1rem;
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">
                <a href="{relative_path}index.html">
                    <img src="{relative_path}assets/images/logo/agroverse-logo.jpeg" alt="Agroverse Logo">
                </a>
            </div>
            <ul class="nav-links">
                <li><a href="{relative_path}index.html">Home</a></li>
                <li><a href="{relative_path}index.html#mission">Mission</a></li>
                <li><a href="{relative_path}category/retail-packs/index.html">Products</a></li>
                <li><a href="{relative_path}farms/oscar-bahia/index.html">Farms</a></li>
                <li><a href="{relative_path}shipments/agl8/index.html">Shipments</a></li>
                <li><a href="{relative_path}index.html#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="blog-container">
        <article class="blog-post">
            <header class="blog-header">
                <h1 class="blog-title">{title}</h1>
                <div class="blog-meta">
                    {f'<span>Published: {date_str}</span>' if date_str else ''}
                    <span>By {author}</span>
                </div>
            </header>
            
            <div class="blog-content">
                {content}
            </div>
            
            <a href="{relative_path}index.html" class="back-link">← Back to Home</a>
        </article>
    </main>
</body>
</html>"""
    
    return html

def find_blog_file(filename_pattern):
    """Find blog post file matching pattern."""
    if not RAW_BLOGS_DIR.exists():
        return None
    
    # Exact match first
    exact_file = RAW_BLOGS_DIR / f"{filename_pattern}.html"
    if exact_file.exists():
        return exact_file
    
    # Try case-insensitive match
    for file in RAW_BLOGS_DIR.glob("*.html"):
        if file.stem.lower() == filename_pattern.lower():
            return file
    
    return None

def main():
    """Process all blog posts."""
    # Create posts directory
    POSTS_DIR.mkdir(exist_ok=True)
    
    processed = 0
    skipped = 0
    errors = []
    
    print("Processing blog posts...")
    print("=" * 60)
    
    for url_slug, filename_pattern in URL_TO_SLUG.items():
        print(f"\nProcessing: {url_slug}")
        
        # Find the blog file
        blog_file = find_blog_file(filename_pattern)
        if not blog_file:
            print(f"  ⚠️  File not found: {filename_pattern}.html")
            skipped += 1
            continue
        
        print(f"  Found: {blog_file.name}")
        
        # Extract content
        blog_data = extract_blog_content(blog_file)
        if not blog_data:
            print(f"  ⚠️  Failed to extract content")
            skipped += 1
            errors.append(url_slug)
            continue
        
        print(f"  Title: {blog_data['title']}")
        
        # Create directory for this post
        post_dir = POSTS_DIR / url_slug
        post_dir.mkdir(exist_ok=True)
        
        # Generate HTML
        html_content = generate_blog_post_html(blog_data, url_slug)
        
        # Save HTML file
        output_file = post_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ Created: {output_file.relative_to(BASE_DIR)}")
        processed += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✅ Processed: {processed}")
    print(f"  ⚠️  Skipped: {skipped}")
    if errors:
        print(f"  ❌ Errors: {', '.join(errors)}")

if __name__ == "__main__":
    main()


