import urllib.request
import urllib.parse
import json
import sys

def search_rumsey(query):
    print(f"Searching David Rumsey Map Collection for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.davidrumsey.com/luna/servlet/as/search?os=0&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('results', [])
            for res in items:
                title = "No Title"
                for field in res.get('fieldValues', []):
                    if 'Short Title' in field:
                        title = field['Short Title'][0]
                        break
                    elif 'Full Title' in field:
                        title = field['Full Title'][0]
                        break
                
                manifest = res.get('iiifManifest')
                results.append({
                    'title': title,
                    'manifest': manifest,
                    'collection': 'David Rumsey Map Collection',
                    'metadata': f"LUNA ID: {res.get('id')}"
                })
    except Exception as e:
        print(f"Error querying David Rumsey: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_rumsey(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
