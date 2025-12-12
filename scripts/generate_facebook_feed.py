#!/usr/bin/env python3
"""
Generate Facebook Product Feed XML from products.js

This script:
1. Reads products from js/products.js
2. Generates a Facebook-compatible product feed XML file
3. Outputs to facebook_product_feed.xml

Facebook Product Feed Requirements (XML format):
- id (required): Unique product identifier
- title (required): Product name
- description: Product description
- link (required): Product page URL
- image_link (required): Product image URL
- availability (required): in stock / out of stock / preorder
- condition (required): new / refurbished / used
- price (required): Price with currency (e.g., "25.00 USD")
- brand: Brand name
- google_product_category: Google product category ID
- product_type: Product category/type
"""

import re
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
PRODUCTS_JS_FILE = BASE_DIR / 'js' / 'products.js'
OUTPUT_XML_FILE = BASE_DIR / 'facebook_product_feed.xml'
BASE_URL = 'https://www.agroverse.shop'

def parse_products_js():
    """Parse products.js file and extract product data."""
    with open(PRODUCTS_JS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the PRODUCTS object using regex
    # Look for window.PRODUCTS = { ... };
    pattern = r'window\.PRODUCTS\s*=\s*({.*?});'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Could not find PRODUCTS object in products.js")
    
    products_str = match.group(1)
    
    # Use a more robust parsing approach
    products = {}
    
    # Find each product entry: 'product-id': { ... }
    # This regex handles nested objects better
    product_pattern = r"'([^']+)':\s*\{((?:[^{}]|\{[^{}]*\})*)\}"
    
    for match in re.finditer(product_pattern, products_str, re.DOTALL):
        product_id = match.group(1)
        product_data_str = match.group(2)
        
        # Extract key-value pairs, handling strings that may contain commas
        product = {}
        
        # More sophisticated field extraction
        # Handle both single and double quotes, including escaped quotes
        # Match: key: value where value can be:
        # - Single-quoted string (handling escaped quotes)
        # - Double-quoted string (handling escaped quotes)
        # - Number
        field_pattern = r"(\w+):\s*((?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|\d+\.?\d*))"
        
        for field_match in re.finditer(field_pattern, product_data_str):
            key = field_match.group(1)
            value_raw = field_match.group(2).strip()
            
            # Check if it's a quoted string
            if value_raw.startswith("'") and value_raw.endswith("'"):
                # Single-quoted string - get the inner content
                value = field_match.group(3) if field_match.group(3) is not None else value_raw[1:-1]
                # Unescape escaped quotes
                value = value.replace("\\'", "'").replace("\\\\", "\\")
            elif value_raw.startswith('"') and value_raw.endswith('"'):
                # Double-quoted string - get the inner content
                value = field_match.group(4) if field_match.group(4) is not None else value_raw[1:-1]
                # Unescape escaped quotes
                value = value.replace('\\"', '"').replace("\\\\", "\\")
            else:
                # Try to convert to number
                try:
                    value = float(value_raw) if '.' in value_raw else int(value_raw)
                except ValueError:
                    value = value_raw
            
            product[key] = value
        
        products[product_id] = product
    
    return products

def escape_xml(text):
    """Escape XML special characters."""
    if text is None:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def format_price(price):
    """Format price for Facebook feed (e.g., '25.00 USD')."""
    if price is None or price == 0:
        return None
    return f"{price:.2f} USD"

def get_product_url(product_id):
    """Generate product page URL."""
    return f"{BASE_URL}/product-page/{product_id}/"

def get_image_url(image_path):
    """Convert relative image path to absolute URL."""
    if not image_path:
        return None
    # Remove leading slash if present (we'll add it)
    image_path = image_path.lstrip('/')
    return f"{BASE_URL}/{image_path}"

def generate_description(product):
    """Generate product description from product data."""
    name = product.get('name', '')
    farm = product.get('farm', '')
    shipment = product.get('shipment', '')
    category = product.get('category', '')
    
    parts = [name]
    if farm:
        parts.append(f"From {farm}")
    if shipment:
        parts.append(f"Shipment {shipment}")
    
    description = ". ".join(parts)
    
    # Add category-specific info
    if category == 'retail':
        description += ". Available for direct purchase."
    elif category == 'wholesale':
        description += ". Contact us for wholesale pricing."
    
    return description

def generate_xml_feed(products):
    """Generate Facebook product feed in XML format."""
    # Create XML structure
    rss = ET.Element('rss', {
        'version': '2.0',
        'xmlns:g': 'http://base.google.com/ns/1.0'
    })
    
    channel = ET.SubElement(rss, 'channel')
    
    # Channel metadata
    ET.SubElement(channel, 'title').text = 'Agroverse Shop Products'
    ET.SubElement(channel, 'link').text = BASE_URL
    ET.SubElement(channel, 'description').text = 'Agroverse regenerative cacao products from Brazilian farms'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Add products
    for product_id, product in products.items():
        item = ET.SubElement(channel, 'item')
        
        # Required fields
        ET.SubElement(item, 'g:id').text = escape_xml(product_id)
        ET.SubElement(item, 'g:title').text = escape_xml(product.get('name', ''))
        
        # Link (required)
        product_url = get_product_url(product_id)
        ET.SubElement(item, 'g:link').text = product_url
        
        # Image link (required)
        image_path = product.get('image', '')
        if image_path:
            image_url = get_image_url(image_path)
            ET.SubElement(item, 'g:image_link').text = image_url
        
        # Description
        description = generate_description(product)
        ET.SubElement(item, 'g:description').text = escape_xml(description)
        
        # Availability (required)
        category = product.get('category', 'retail')
        availability = 'in stock'
        ET.SubElement(item, 'g:availability').text = availability
        
        # Price (required)
        price = product.get('price', 0)
        try:
            price_float = float(price) if price else 0.0
            if price_float > 0:
                price_str = format_price(price_float)
                ET.SubElement(item, 'g:price').text = price_str
            else:
                ET.SubElement(item, 'g:price').text = '0.00 USD'
        except (ValueError, TypeError):
            ET.SubElement(item, 'g:price').text = '0.00 USD'
        
        # Condition (required)
        ET.SubElement(item, 'g:condition').text = 'new'
        
        # Brand
        ET.SubElement(item, 'g:brand').text = 'Agroverse'
        
        # Additional fields
        if product.get('farm'):
            ET.SubElement(item, 'g:custom_label_0').text = escape_xml(product.get('farm'))
        
        if product.get('shipment'):
            ET.SubElement(item, 'g:custom_label_1').text = escape_xml(product.get('shipment'))
        
        if category:
            ET.SubElement(item, 'g:product_type').text = escape_xml(category.title())
        
        # Google product category
        ET.SubElement(item, 'g:google_product_category').text = '357'
    
    # Convert to string with pretty formatting
    xml_str = ET.tostring(rss, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    # Remove empty lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    pretty_xml = '\n'.join(lines)
    
    # Write to file
    print(f"Writing XML feed to {OUTPUT_XML_FILE}...")
    with open(OUTPUT_XML_FILE, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"✅ Generated XML feed: {OUTPUT_XML_FILE}")

def generate_facebook_feed():
    """Generate Facebook product feed in XML format."""
    print(f"Reading products from {PRODUCTS_JS_FILE}...")
    products = parse_products_js()
    
    print(f"Found {len(products)} products\n")
    
    # Generate XML feed
    generate_xml_feed(products)
    
    print(f"\n✅ Successfully generated Facebook product feed with {len(products)} products")
    print(f"📄 XML file: {OUTPUT_XML_FILE}")
    print(f"🌐 Feed URL: {BASE_URL}/facebook_product_feed.xml")
    print("\nNext steps:")
    print("1. Commit and push the XML file to GitHub")
    print("2. In Facebook Commerce Manager, add a data source")
    print("3. Use the feed URL: https://www.agroverse.shop/facebook_product_feed.xml")

if __name__ == '__main__':
    try:
        generate_facebook_feed()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

