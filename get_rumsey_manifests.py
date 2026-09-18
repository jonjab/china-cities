import urllib.request
import urllib.parse
import json

def get_rumsey_manifests(query):
    print(f"\n--- Manifests for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.davidrumsey.com/luna/servlet/as/search?os=0&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read())
            results = data.get('results', [])
            for idx, res in enumerate(results):
                title = "No Title"
                # Extract title from fieldValues
                for field in res.get('fieldValues', []):
                    if 'Short Title' in field:
                        title = field['Short Title'][0]
                        break
                    elif 'Full Title' in field:
                        title = field['Full Title'][0]
                        break
                
                manifest = res.get('iiifManifest')
                print(f"Title: {title}")
                print(f"Manifest URL: {manifest}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_rumsey_manifests("jinan")
    get_rumsey_manifests("tsinan")
