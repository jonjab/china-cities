import urllib.request
import urllib.parse
import re
import sys

def search_bsb(query):
    print(f"Searching BSB for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.digitale-sammlungen.de/en/search?query={encoded_query}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            if "No results found" in html or "no results" in html.lower():
                return results
            
            # Extract item bsb IDs and titles
            # Detail links are typically like /en/details/bsb00116812 or /details/bsb00116812
            bsb_ids = set(re.findall(r'/details/(bsb[0-9a-zA-Z]+)', html))
            
            for bsb_id in bsb_ids:
                # Get the title for this item if possible from HTML, or use a placeholder
                # Let's see if we can find a title near the bsb_id
                # Or we can just inspect the HTML for title blocks
                title_match = re.search(fr'href="[^"]*details/{bsb_id}"[^>]*>(.*?)</a>', html, re.DOTALL)
                title = title_match.group(1).strip() if title_match else f"BSB Map {bsb_id}"
                # Clean up HTML tags from title
                title = re.sub(r'<[^>]+>', '', title).strip()
                manifest_url = f"https://api.digitale-sammlungen.de/iiif/presentation/v2/{bsb_id}/manifest"
                
                # Check if it's a map (for BSB we can check if 'karte' or 'map' is associated or assume yes if title has map/karte)
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'Bavarian State Library (BSB)',
                    'metadata': f"BSB ID: {bsb_id}"
                })
    except Exception as e:
        print(f"Error searching BSB: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_bsb(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
