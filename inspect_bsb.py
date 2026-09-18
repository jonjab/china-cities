import urllib.request
import urllib.parse
import re

def inspect_bsb_html():
    url = "https://www.digitale-sammlungen.de/en/search?query=jinan"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            # Look for body text
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
            if body_match:
                body = body_match.group(1)
                # Strip scripts and styles
                body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
                body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)
                # Strip tags
                text = re.sub(r'<[^>]+>', ' ', body)
                text = re.sub(r'\s+', ' ', text).strip()
                print("BSB Text Preview:")
                print(text[:1000])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_bsb_html()
