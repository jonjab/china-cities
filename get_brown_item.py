import urllib.request
import re

def get_brown_item_manifest(item_path):
    url = f"https://repository.library.brown.edu{item_path}"
    print(f"Fetching Brown item page: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            manifest_matches = re.findall(r'https?://[^"\']*manifest[^"\']*', html, re.IGNORECASE)
            print("Found potential manifest links:")
            for m in set(manifest_matches):
                print(f"  {m}")
                
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if title_match:
                print(f"Title: {title_match.group(1).strip()}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_brown_item_manifest("/studio/item/bdr:445321/")
