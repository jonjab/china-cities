import urllib.request
import urllib.parse
import re

def parse_cultural_japan_js():
    url = "https://cultural.jp/search?q=jinan"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
            print("Searching for api or fetch calls in HTML:")
            # Find script tags or links with api
            scripts = re.findall(r'<script src="([^"]+)"', content)
            print("Script tags:")
            for s in scripts:
                print(s)
            
            # Let's search for api urls in the content
            apis = re.findall(r'https?://[^/]*cultural\.jp[^"\']+', content)
            print("Cultural Japan URLs:")
            for a in set(apis)[:10]:
                print(a)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_cultural_japan_js()
