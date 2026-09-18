import urllib.request
import urllib.parse
import re
import sys

def search_digital_commonwealth(query):
    print(f"Searching Digital Commonwealth for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.digitalcommonwealth.org/search?utf8=%E2%9C%93&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            if "No results found" in html or "did not return any results" in html:
                return results
                
            # Find item links like /search/commonwealth:xxxxxxxxx
            matches = list(set(re.findall(r'href="(/search/commonwealth:[a-zA-Z0-9]+)"', html)))
            for m in matches:
                # Extract title from html if possible or use a default
                title_match = re.search(fr'href="{m}"[^>]*>(.*?)</a>', html, re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Digital Commonwealth Item"
                title = re.sub(r'<[^>]+>', ' ', title).strip()
                
                # The ID is the commonwealth:xxxx part
                item_id = m.split(':')[-1]
                manifest_url = f"https://www.digitalcommonwealth.org/search/commonwealth:{item_id}/manifest"
                
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'Digital Commonwealth',
                    'metadata': f"ID: {item_id}"
                })
    except Exception as e:
        print(f"Error searching Digital Commonwealth: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_digital_commonwealth(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
