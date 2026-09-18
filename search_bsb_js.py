import urllib.request
import re

def search_js_for_api():
    url = "https://www.digitale-sammlungen.de/static/assets/api-GMRnckp_.js"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            print(f"JS Length: {len(content)}")
            
            # Find URLs or domain references
            urls = re.findall(r'https?://[^"\']+', content)
            print("Found URLs in JS:")
            for u in list(set(urls))[:20]:
                print(f"  {u}")
                
            # Search for api paths like /core/ or /api/
            api_paths = re.findall(r'/[a-zA-Z0-9_-]+/api/[a-zA-Z0-9_-]+', content)
            print("Found potential API paths in JS:")
            for ap in list(set(api_paths))[:20]:
                print(f"  {ap}")
                
            # Let's search for some strings like "search" or "/search"
            matches = [m.start() for m in re.finditer(r'/search', content)]
            print(f"Occurrences of '/search': {len(matches)}")
            for idx in matches:
                start = max(0, idx - 50)
                end = min(len(content), idx + 100)
                print(f"Context: {content[start:end]}")
                
            # Let's search for "api" or "http" or "v1" or "v2"
            matches_api = [m.start() for m in re.finditer(r'api\.digitale', content)]
            print(f"Occurrences of 'api.digitale': {len(matches_api)}")
            for idx in matches_api:
                start = max(0, idx - 50)
                end = min(len(content), idx + 100)
                print(f"Context: {content[start:end]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_js_for_api()
