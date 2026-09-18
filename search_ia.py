import urllib.request
import urllib.parse
import json
import sys

def search_ia(query):
    print(f"Searching Internet Archive for: {query}")
    params = {
        'q': f"({query}) AND mediatype:(image OR texts OR web)",
        'fl[]': 'identifier,title,mediatype,subject',
        'rows': '20',
        'output': 'json'
    }
    url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            for doc in docs:
                title = doc.get('title', 'No Title')
                identifier = doc.get('identifier')
                # Internet Archive IIIF manifest URL format:
                # https://iiif.archivelab.org/iiif/{identifier}/manifest.json
                manifest_url = f"https://iiif.archivelab.org/iiif/{identifier}/manifest.json"
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'Internet Archive',
                    'metadata': f"Identifier: {identifier}, Media Type: {doc.get('mediatype')}"
                })
    except Exception as e:
        print(f"Error querying Internet Archive: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_ia(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
