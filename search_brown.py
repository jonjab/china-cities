import urllib.request
import urllib.parse
import json
import re

def search_brown(query):
    print(f"\n--- Searching Brown University Digital Repository for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    # Brown's repository search URL
    url = f"https://repository.library.brown.edu/studio/search/?q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            print(f"Status: {response.status}, Length: {len(html)}")
            
            # Check for "no results"
            if "No results found" in html or "0 results" in html:
                print("No results found.")
                return
            
            # Look for item links (usually containing /studio/item/bdr:...)
            bdr_links = set(re.findall(r'href="([^"]*/studio/item/bdr:[^"]*)"', html))
            print(f"Found {len(bdr_links)} item links:")
            for l in list(bdr_links)[:5]:
                print(f"  Item link: {l}")
                # We can request the item and check for IIIF manifest!
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_brown("jinan")
    search_brown("tsinan")
