import urllib.request
import urllib.parse
import json
import sys

def search_bodleian(query):
    print(f"Searching Digital Bodleian for: {query}")
    encoded_query = urllib.parse.quote(query)
    # Note: we use the trailing slash to avoid 301 redirects
    url = f"https://digital.bodleian.ox.ac.uk/search/?q={encoded_query}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/ld+json'
    })
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            members = data.get('member', [])
            for item in members:
                display_fields = item.get('displayFields', {})
                title = display_fields.get('title', ['No Title'])[0]
                manifest = item.get('manifest')
                shelfmark = item.get('shelfmark')
                
                results.append({
                    'title': title,
                    'manifest': manifest,
                    'collection': 'University of Oxford (Digital Bodleian)',
                    'metadata': f"Shelfmark: {shelfmark}"
                })
    except Exception as e:
        print(f"Error querying Digital Bodleian: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_bodleian(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
