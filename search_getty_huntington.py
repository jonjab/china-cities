import urllib.request
import urllib.parse
import json

def search_huntington(query):
    print(f"\n--- Searching Huntington Digital Library for: {query} ---")
    # Huntington is on CONTENTdm, which supports the /digital/api/search endpoint
    encoded_query = urllib.parse.quote(query)
    # Syntax for CONTENTdm query API:
    url = f"https://hdl.huntington.org/digital/api/search/collection/all/searchterm/{encoded_query}/field/all/mode/all/conn/and/order/nosort/ad/asc/row/50/start/1/format/json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("Successfully queried Huntington API!")
            items = data.get('results', [])
            print(f"Total results: {data.get('pager', {}).get('total', 0)}")
            print(f"Retrieved {len(items)} items:")
            for idx, item in enumerate(items[:5]):
                print(f"  Item {idx + 1}:")
                print(f"    Title: {item.get('title')}")
                print(f"    ID (pointer): {item.get('pointer')}")
                print(f"    Collection: {item.get('collection')}")
                # Manifest URL format for CONTENTdm:
                # https://hdl.huntington.org/iiif/info/{collection}/{pointer}/manifest.json
                coll = item.get('collection', '').strip('/')
                pointer = item.get('pointer')
                manifest = f"https://hdl.huntington.org/iiif/info/{coll}/{pointer}/manifest.json"
                print(f"    Manifest URL: {manifest}")
    except Exception as e:
        print(f"Error querying Huntington: {e}")

def search_getty(query):
    print(f"\n--- Searching J. Paul Getty Trust for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.getty.edu/gateway/search?q={encoded_query}&cat=highlight&rows=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            print(f"Getty response status: {response.status}, HTML length: {len(html)}")
            if "No results found" in html or "No Records Found" in html:
                print("No results found.")
            else:
                import re
                links = set(re.findall(r'href="([^"]*getty\.edu[^"]*)"', html))
                print(f"Found {len(links)} getty.edu links:")
                for l in list(links)[:5]:
                    print(f"  {l}")
    except Exception as e:
        print(f"Error querying Getty: {e}")

if __name__ == "__main__":
    search_huntington("jinan")
    search_huntington("tsinan")
    search_getty("jinan")
    search_getty("tsinan")
