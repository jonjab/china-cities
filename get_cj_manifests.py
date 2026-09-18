import urllib.request
import urllib.parse
import json

def fetch_cultural_japan_results(query):
    print(f"\n--- Cultural Japan Results for keyword='{query}' ---")
    params = {'keyword': query}
    url = "https://api.cultural.jp/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            hits = data.get('hits', {}).get('hits', [])
            print(f"Total Hits: {len(hits)}")
            for idx, hit in enumerate(hits):
                # Extract details
                title_ja = hit.get('title', {}).get('ja', [''])[0] if isinstance(hit.get('title'), dict) else ''
                title_en = hit.get('title', {}).get('en', [''])[0] if isinstance(hit.get('title'), dict) else ''
                manifest = hit.get('manifest', [])
                source = hit.get('source', {}).get('en', [''])[0] if isinstance(hit.get('source'), dict) else ''
                print(f"\nHit {idx + 1}:")
                print(f"  Title EN: {title_en}")
                print(f"  Title JA: {title_ja}")
                print(f"  Source: {source}")
                print(f"  Manifest: {manifest}")
                
    except Exception as e:
        print(f"Error fetching results: {e}")

if __name__ == "__main__":
    fetch_cultural_japan_results("jinan")
    fetch_cultural_japan_results("tsinan")
