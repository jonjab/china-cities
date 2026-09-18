import urllib.request
import urllib.parse
import json
import sys

def search_huntington(query):
    print(f"Searching Huntington Digital Library for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://hdl.huntington.org/digital/api/search/collection/all/searchterm/{encoded_query}/field/all/mode/all/conn/and/order/nosort/ad/asc/row/20/start/1/format/json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('results', [])
            for item in items:
                title = item.get('title')
                pointer = item.get('pointer')
                coll = item.get('collection', '').strip('/')
                manifest = f"https://hdl.huntington.org/iiif/info/{coll}/{pointer}/manifest.json"
                results.append({
                    'title': title,
                    'manifest': manifest,
                    'collection': 'Huntington Digital Library',
                    'metadata': f"Collection: {coll}, Pointer: {pointer}"
                })
    except Exception as e:
        print(f"Error querying Huntington: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_huntington(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
