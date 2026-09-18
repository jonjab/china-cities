import urllib.request
import re

def print_js_api_search_context():
    url = "https://www.digitale-sammlungen.de/static/assets/api-GMRnckp_.js"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            matches = [m.start() for m in re.finditer(r'/api/search', content)]
            for idx in matches:
                start = max(0, idx - 50)
                end = min(len(content), idx + 1000)
                print("CONTEXT:")
                print(content[start:end])
                print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print_js_api_search_context()
