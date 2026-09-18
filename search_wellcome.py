import urllib.request
import urllib.parse
import json
import sys

def search_wellcome(query):
    print(f"Searching Wellcome Collection for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.wellcomecollection.org/catalogue/v2/works?query={encoded_query}&include=items"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('results', [])
            for item in items:
                title = item.get('title')
                work_id = item.get('id')
                
                # Check for IIIF manifest URLs in item locations
                manifest_url = ""
                for it in item.get('items', []):
                    for loc in it.get('locations', []):
                        if 'url' in loc and ('iiif' in loc['url'] or 'manifest' in loc['url']):
                            manifest_url = loc['url']
                            break
                    if manifest_url:
                        break
                        
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'Wellcome Collection',
                    'metadata': f"Work ID: {work_id}"
                })
    except Exception as e:
        print(f"Error querying Wellcome: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_wellcome(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
