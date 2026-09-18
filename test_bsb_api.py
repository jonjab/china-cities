import urllib.request
import urllib.parse
import json

def test_bsb_api_endpoints():
    endpoints = [
        "https://api.digitale-sammlungen.de/search",
        "https://api.digitale-sammlungen.de/core/search",
        "https://api.digitale-sammlungen.de/iiif/presentation/v2/search",
        "https://api.digitale-sammlungen.de/core/v1/search",
        "https://api.digitale-sammlungen.de/search/v1",
    ]
    for ep in endpoints:
        url = ep + "?q=jinan"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"Endpoint {ep} -> 200 OK! Content preview:")
                print(response.read()[:500])
        except Exception as e:
            print(f"Endpoint {ep} -> {e}")

if __name__ == "__main__":
    test_bsb_api_endpoints()
