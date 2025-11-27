#!/usr/bin/env python3
"""
Script to find partner addresses using Google Places API and Nominatim (OpenStreetMap) as fallback
"""
import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Google API key from .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEy") or os.getenv("GOOGLE_API_KEY")

# Partners to search for - with multiple query attempts
PARTNERS = [
    {"name": "Block71 Silicon Valley", "location": "Silicon Valley, California", "queries": ["Block71 co-working San Mateo", "Block71 Stanford Research Park", "Block71 Silicon Valley San Mateo"]},
    {"name": "Edge and Node House of Web3", "location": "San Francisco, California", "queries": ["Edge and Node San Francisco", "The Graph Edge and Node San Francisco", "House of Web3 San Francisco"]},
    {"name": "Green Gulch Farm Zen Center", "location": "Marin County, California", "queries": ["1601 Shoreline Highway Muir Beach", "Green Gulch Farm 1601 Shoreline Highway California", "1601 Shoreline Highway California 94965"]},
    {"name": "Miss Tomato", "location": "Daly City, California", "queries": ["Miss Tomato restaurant Daly City", "Miss Tomato Daly City California"]},
    {"name": "The Enchanted Forest Boutique", "location": "Chico, California", "queries": ["Enchanted Forest Boutique Chico", "Enchanted Forest Chico California"]},
    {"name": "Peace on Fifth", "location": "Dayton, Ohio", "queries": ["Peace on Fifth Dayton Ohio", "Peace on Fifth Dayton"]},
    {"name": "Soulfulness Breathe", "location": "Denver, Colorado", "queries": ["Soulfulness Breathe Denver", "Soulfulness Breathe Denver Colorado"]},
    {"name": "The Ponderosa Slab City", "location": "Slab City, California", "queries": ["Ponderosa Slab City", "Ponderosa Niland California", "Slab City Ponderosa"]},
    {"name": "Founderhaus", "location": "Brazil", "queries": ["Founderhaus São Paulo", "Founderhaus Brazil"]},
    {"name": "Heierling Ski", "location": "Switzerland", "queries": ["Heierling Ski shop Switzerland", "Heierling Ski"]},
]

def find_place_google(query):
    """Find a place using Google Places API Text Search"""
    if not GOOGLE_API_KEY:
        return {"error": "No Google API key found"}
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        "query": query,
        "key": GOOGLE_API_KEY,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            place = data["results"][0]
            return {
                "name": place.get("name"),
                "formatted_address": place.get("formatted_address"),
                "place_id": place.get("place_id"),
            }
        else:
            return {"error": data.get("status"), "message": data.get("error_message", "No results found")}
    except Exception as e:
        return {"error": str(e)}

def geocode_nominatim(query):
    """Geocode an address using Nominatim (OpenStreetMap) - free and no API key needed"""
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    
    headers = {
        "User-Agent": "Agroverse Partner Address Finder"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            address = result.get("display_name", "")
            
            # Try to format address nicely
            address_parts = result.get("address", {})
            formatted_parts = []
            
            if address_parts.get("house_number") and address_parts.get("road"):
                formatted_parts.append(f"{address_parts['house_number']} {address_parts['road']}")
            elif address_parts.get("road"):
                formatted_parts.append(address_parts["road"])
            
            if address_parts.get("city"):
                formatted_parts.append(address_parts["city"])
            elif address_parts.get("town"):
                formatted_parts.append(address_parts["town"])
            elif address_parts.get("village"):
                formatted_parts.append(address_parts["village"])
            
            if address_parts.get("state"):
                formatted_parts.append(address_parts["state"])
            
            if address_parts.get("postcode"):
                formatted_parts.append(address_parts["postcode"])
            
            if address_parts.get("country"):
                formatted_parts.append(address_parts["country"])
            
            formatted_address = ", ".join(formatted_parts) if formatted_parts else address
            
            return {
                "formatted_address": formatted_address,
                "display_name": address,
                "lat": result.get("lat"),
                "lon": result.get("lon"),
            }
        else:
            return {"error": "No results found"}
    except Exception as e:
        return {"error": str(e)}

def get_place_details(place_id):
    """Get detailed information about a place using place_id"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "fields": "formatted_address,formatted_phone_number,website,opening_hours",
        "key": API_KEY,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK":
            return data.get("result", {})
        else:
            return {"error": data.get("status")}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("Searching for partner addresses using Google Places API (with Nominatim fallback)...\n")
    
    if GOOGLE_API_KEY:
        print(f"✓ Using Google API key: {GOOGLE_API_KEY[:20]}...\n")
    else:
        print("⚠ No Google API key found, using Nominatim only\n")
    
    results = {}
    
    for i, partner in enumerate(PARTNERS):
        name = partner["name"]
        queries = partner.get("queries", [f"{name} {partner['location']}"])
        
        print(f"[{i+1}/{len(PARTNERS)}] Searching for: {name}")
        
        found = False
        for query in queries:
            print(f"  Trying: {query}")
            
            # Try Google Places API first
            if GOOGLE_API_KEY:
                result = find_place_google(query)
                if "error" not in result:
                    print(f"  ✓ Found (Google): {result['formatted_address']}")
                    results[name] = result["formatted_address"]
                    found = True
                    break
                elif result.get("error") != "REQUEST_DENIED":
                    print(f"  Google API: {result.get('error', 'Unknown error')}")
            
            # Fallback to Nominatim
            result = geocode_nominatim(query)
            if "error" not in result:
                # Check if the result seems relevant (contains location keywords)
                address_lower = result['formatted_address'].lower()
                location_lower = partner['location'].lower()
                
                # Basic relevance check
                if any(keyword in address_lower for keyword in location_lower.split()):
                    print(f"  ✓ Found (Nominatim): {result['formatted_address']}")
                    results[name] = result["formatted_address"]
                    found = True
                    break
                else:
                    print(f"  ? Found but may not be relevant: {result['formatted_address']}")
        
        if not found:
            print(f"  ✗ Not found with any query")
            results[name] = None
        
        # Rate limiting - Nominatim requires max 1 request per second
        # Google API has its own rate limits
        if i < len(PARTNERS) - 1:
            time.sleep(0.5)  # Reduced delay since we're using Google API
        
        print()
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, address in results.items():
        if address:
            print(f"{name}:")
            print(f"  {address}\n")
        else:
            print(f"{name}: NOT FOUND\n")
    
    # Save to JSON file
    with open("/Users/garyjob/Applications/agroverse_shop/scripts/partner_addresses.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to partner_addresses.json")

if __name__ == "__main__":
    main()

