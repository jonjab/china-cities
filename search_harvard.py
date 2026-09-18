import urllib.request
import urllib.parse
import json
import re
import sys

def search_harvard(query):
    print(f"Searching Harvard Library Cloud for: {query}")
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.lib.harvard.edu/v2/items.json?q={encoded_query}&limit=20"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('items', {}).get('mods', [])
            if not isinstance(items, list):
                items = [items] if items else []
                
            for item in items:
                # Title Info
                title_info = item.get('titleInfo', {})
                title = ""
                if isinstance(title_info, list):
                    title = title_info[0].get('title', 'No Title') if title_info else 'No Title'
                elif isinstance(title_info, dict):
                    title = title_info.get('title', 'No Title')
                
                # Check for IIIF manifest URLs in the metadata
                # Usually under extension / standard fields or in urn links
                item_str = json.dumps(item)
                manifests = list(set(re.findall(r'https?://[^"\s]*iiif[^"\s]*manifest[^"\s]*', item_str)))
                
                # Harvard manifests can also be constructed if we have the DRS ID (digital object ID)
                # URN links are typically like: "http://nrs.harvard.edu/urn-3:FHCL:123456"
                urns = re.findall(r'http://nrs\.harvard\.edu/urn-3:[A-Z]+:[0-9]+', item_str)
                for urn in urns:
                    # Construct potential manifest URL if not found
                    # Typically Harvard manifests are: https://iiif.lib.harvard.edu/manifests/drs:123456
                    drs_id = urn.split(':')[-1]
                    manifests.append(f"https://iiif.lib.harvard.edu/manifests/drs:{drs_id}")
                
                manifest_url = manifests[0] if manifests else ""
                
                results.append({
                    'title': title,
                    'manifest': manifest_url,
                    'collection': 'Harvard University Digital Collections',
                    'metadata': f"Record ID: {item.get('recordInfo', {}).get('recordIdentifier', 'N/A')}"
                })
    except Exception as e:
        print(f"Error querying Harvard: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_harvard(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
