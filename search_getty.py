import urllib.request
import urllib.parse
import json
import re
import sys

def search_getty(query):
    print(f"Searching J. Paul Getty Trust for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.getty.edu/gateway/search?q={encoded_query}&cat=highlight&rows=20"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            # Look for item links or records
            # Find any href containing digital/api/ or look for titles
            titles = re.findall(r'class="title"[^>]*>(.*?)</a>', html, re.DOTALL)
            hrefs = re.findall(r'href="([^"]*)"', html)
            
            for idx, title in enumerate(titles[:10]):
                clean_title = re.sub(r'<[^>]+>', ' ', title).strip()
                item_url = hrefs[idx] if idx < len(hrefs) else ""
                
                # Check for manifest
                manifest_url = ""
                # For Getty, IIIF manifests are often at: https://media.getty.edu/iiif/manifest/{id}
                # Let's try to extract an ID from the URL
                id_match = re.search(r'id=([0-9a-zA-Z\-]+)', item_url)
                if id_match:
                    item_id = id_match.group(1)
                    manifest_url = f"https://media.getty.edu/iiif/manifest/{item_id}"
                
                results.append({
                    'title': clean_title,
                    'manifest': manifest_url,
                    'collection': 'J. Paul Getty Trust',
                    'metadata': f"Item URL: {item_url}"
                })
    except Exception as e:
        print(f"Error querying Getty: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_getty(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
