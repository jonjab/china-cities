import urllib.request
import urllib.parse
import json
import sys

def search_cultural_japan(query):
    print(f"Searching Cultural Japan for: {query}")
    params = {'keyword': query}
    url = "https://api.cultural.jp/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            hits = data.get('hits', {}).get('hits', [])
            for hit in hits:
                title_ja = hit.get('title', {}).get('ja', [''])[0] if isinstance(hit.get('title'), dict) else ''
                title_en = hit.get('title', {}).get('en', [''])[0] if isinstance(hit.get('title'), dict) else ''
                title = title_en if title_en else title_ja
                manifests = hit.get('manifest', [])
                source = hit.get('source', {}).get('en', ['Other'])[0] if isinstance(hit.get('source'), dict) else 'Other'
                
                manifest_url = manifests[0] if manifests else ""
                
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': f"Cultural Japan ({source})",
                    'metadata': f"Source: {source}"
                })
    except Exception as e:
        print(f"Error querying Cultural Japan: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_cultural_japan(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
