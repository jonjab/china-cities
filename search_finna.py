import urllib.request
import urllib.parse
import json
import sys

def search_finna(query):
    print(f"Searching National Library of Finland (Finna.fi) for: {query}")
    url = f"https://api.finna.fi/v1/search?lookfor={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            records = data.get('records', [])
            for item in records:
                title = item.get('title')
                formats = item.get('formats', [])
                
                # Check for IIIF manifest or images
                manifest_url = ""
                # Finna often has custom IIIF services, let's look for iiif
                # If they have an image/cover, or standard presentation manifest
                # Often it can be constructed if there is a 'has_presentation_manifest' or similar
                # Let's check for onlineUrls
                urls_list = item.get('onlineUrls', [])
                for u in urls_list:
                    if 'iiif' in u or 'manifest' in u:
                        manifest_url = u
                        break
                
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'National Library of Finland (Finna.fi)',
                    'metadata': f"Formats: {formats}, Year: {item.get('year', 'N/A')}"
                })
    except Exception as e:
        print(f"Error querying Finna: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_finna(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
