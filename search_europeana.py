import urllib.request
import urllib.parse
import re
import sys

def search_europeana(query):
    print(f"Searching Europeana for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.europeana.eu/en/search?query={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            if "No results" in html or "didn't return any results" in html:
                return results
                
            # Find item links
            item_links = set(re.findall(r'href="([^"]*/item/[^"]*)"', html))
            for l in list(item_links)[:5]:
                # Build the item page URL
                full_item_url = l if l.startswith('http') else f"https://www.europeana.eu{l}"
                # For Europeana, manifests are often hosted on Europeana's API, or we can use the item_url as metadata
                results.append({
                    'title': f"Europeana Item: {full_item_url.split('/')[-1]}",
                    'manifest': f"https://api.europeana.eu/iiif/presentation/v2/{full_item_url.split('/')[-1]}/manifest",
                    'collection': 'Europeana',
                    'metadata': f"Item URL: {full_item_url}"
                })
    except Exception as e:
        print(f"Error: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_europeana(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
