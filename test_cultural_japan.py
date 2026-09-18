import urllib.request
import urllib.parse
import json

def test_cultural_japan(query):
    print(f"Searching Cultural Japan for: {query}")
    # Cultural Japan often uses api.cultural.jp or search.cultural.jp
    # Let's try searching their main search endpoint: https://cultural.jp/search?q=...
    encoded_query = urllib.parse.quote(query)
    url = f"https://cultural.jp/search?q={encoded_query}"
    # Wait, they might have an API: https://api.cultural.jp/search?q=...
    # Let's check both or test the main page first
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
            print(f"Main page response length: {len(content)}")
            # Let's see if we can find any references to maps or items
            # Or let's try the api endpoint: https://cultural.jp/api/search
            # Actually, let's try to query: https://api.cultural.jp/search?q={encoded_query}
            # Or https://api.cultural.jp/v1/search?q={encoded_query}
    except Exception as e:
        print(f"Main page error: {e}")
        
    api_url = f"https://api.cultural.jp/search?q={encoded_query}"
    req_api = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req_api, timeout=15) as response:
            content = response.read().decode('utf-8')
            print("API response preview:")
            print(content[:500])
    except Exception as e:
        print(f"API error: {e}")

if __name__ == "__main__":
    test_cultural_japan("jinan")
    test_cultural_japan("tsinan")
