import urllib.request
import urllib.parse
import json

def test_rumsey(query):
    print(f"Searching David Rumsey Map Collection for: {query}")
    # Try different search URLs
    encoded_query = urllib.parse.quote(query)
    # LUNA search endpoints:
    # 1. HTML search page
    # 2. JSON search endpoint
    url = f"https://www.davidrumsey.com/luna/servlet/as/search?os=0&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read()
            # print first 500 chars
            print("Response preview:")
            print(content[:1000].decode('utf-8', errors='ignore'))
            
            # Let's try to load as JSON
            try:
                data = json.loads(content)
                print(f"Loaded as JSON! Found keys: {list(data.keys())}")
                if 'results' in data:
                    print(f"Found {len(data['results'])} results.")
                    for item in data['results'][:3]:
                        print(item.get('title'), item.get('url'))
            except Exception as json_err:
                print(f"Not JSON: {json_err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rumsey("jinan")
    test_rumsey("tsinan")
