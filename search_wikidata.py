import urllib.request
import urllib.parse
import json
import sys

def search_wikidata(query):
    print(f"Searching Wikidata for: {query}")
    sparql_query = f"""
    SELECT ?item ?itemLabel ?manifest WHERE {{
      ?item wdt:P6108 ?manifest .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
      FILTER(CONTAINS(LCASE(?itemLabel), "{query.lower()}"))
    }}
    LIMIT 20
    """
    url = "https://query.wikidata.org/sparql"
    params = {
        'query': sparql_query,
        'format': 'json'
    }
    encoded_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(encoded_url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/sparql-results+json'
    })
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            bindings = data.get('results', {}).get('bindings', [])
            for r in bindings:
                item_url = r.get('item', {}).get('value')
                label = r.get('itemLabel', {}).get('value')
                manifest = r.get('manifest', {}).get('value')
                results.append({
                    'title': label,
                    'manifest': manifest,
                    'collection': 'Wikidata',
                    'metadata': f"Wikidata Item: {item_url}"
                })
    except Exception as e:
        print(f"Error querying Wikidata: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_wikidata(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
