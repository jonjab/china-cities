import urllib.request
import re

def search_index_js():
    url = "https://www.digitale-sammlungen.de/static/assets/index-BDnb4RO5.js"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            print(f"index.js Length: {len(content)}")
            matches = [m.start() for m in re.finditer(r'ocrContext', content)]
            print(f"Occurrences of 'ocrContext': {len(matches)}")
            for idx in matches[:5]:
                print(content[max(0, idx - 100):min(len(content), idx + 200)])
                print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_index_js()
