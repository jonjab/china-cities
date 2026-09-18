import urllib.request
import urllib.parse
import json

def search_bsb_api(query):
    print(f"\n--- BSB API Search for: {query} ---")
    params = {'query': query}
    url = "https://www.digitale-sammlungen.de/api/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("Response loaded successfully.")
            # Let's inspect the keys and structure
            print("Keys:", list(data.keys()))
            if 'items' in data:
                print(f"Total items: {len(data['items'])}")
                for idx, item in enumerate(data['items'][:5]):
                    print(f"\nItem {idx + 1}:")
                    # Let's see some keys
                    print("  Keys:", list(item.keys()))
                    print("  Title:", item.get('title'))
                    print("  ID:", item.get('id'))
                    print("  Thumbnail:", item.get('thumbnail'))
                    # Let's check if there is an IIIF manifest or similar
                    print("  IIIF:", item.get('iiif'))
                    print("  Features:", item.get('features'))
            elif 'docs' in data:
                print(f"Total docs: {len(data['docs'])}")
            else:
                # print first 500 chars of JSON
                print(json.dumps(data, indent=2)[:1000])
    except Exception as e:
        print(f"Error querying API: {e}")

if __name__ == "__main__":
    search_bsb_api("jinan")
    search_bsb_api("tsinan")
