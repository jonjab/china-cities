import urllib.request
import urllib.parse
import json
import re
import sys

def search_loc(query):
    print(f"Searching Library of Congress for: {query}")
    params = {
        'q': query,
        'fo': 'json'
    }
    url = "https://www.loc.gov/search/?" + urllib.parse.urlencode(params)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('results', [])
            for item in items:
                title = item.get('title')
                item_url = item.get('id')
                original_format = item.get('original_format', [])
                formats = [f.lower() for f in original_format] if isinstance(original_format, list) else [str(original_format).lower()]
                types = [t.lower() for f in item.get('type', []) for t in ([f] if isinstance(f, str) else f)]
                
                is_map = 'map' in formats or 'map' in types or any('map' in f for f in formats)
                
                # Check for manifest
                # Check if it has resources or image_url that has iiif
                item_str = json.dumps(item)
                iiif_urls = re.findall(r'https?://[^"\s]*iiif[^"\s]*manifest[^"\s]*', item_str)
                manifest_urls = re.findall(r'https?://[^"\s]*/manifest\.json', item_str)
                all_manifests = list(set(iiif_urls + manifest_urls))
                
                if 'manifest' in item:
                    all_manifests.append(item['manifest'])
                
                manifest_url = all_manifests[0] if all_manifests else ""
                
                # If we don't have a manifest but it's a map on LOC, we can represent it with its item URL
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'Library of Congress',
                    'metadata': f"Item URL: {item_url}, Formats: {original_format}, Is Map: {is_map}"
                })
    except Exception as e:
        print(f"Error searching LOC: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_loc(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
