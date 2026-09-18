import urllib.request
import urllib.parse
import re

def search_shantung_dc():
    print("\n--- Searching Digital Commonwealth for: shantung ---")
    encoded_query = urllib.parse.quote("shantung")
    url = f"https://www.digitalcommonwealth.org/search?utf8=%E2%9C%93&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            matches = set(re.findall(r'href="(/search/commonwealth:[a-zA-Z0-9]+)"', html))
            print(f"Found {len(matches)} item links:")
            for m in list(matches)[:10]:
                print(f"  {m}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_shantung_dc()
