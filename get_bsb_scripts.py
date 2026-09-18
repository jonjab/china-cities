import urllib.request
import urllib.parse
import re

def get_bsb_scripts():
    url = "https://www.digitale-sammlungen.de/en/search?query=jinan"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            scripts = re.findall(r'<script[^>]*src="([^"]+)"', html)
            print("BSB Script files:")
            for s in scripts:
                print(s)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_bsb_scripts()
