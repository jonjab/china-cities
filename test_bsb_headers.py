import urllib.request
import urllib.parse
import json

def test_bsb_with_headers(query):
    params = {
        'query': query,
        'handler': 'simple-all',
        'ocrContext': 'false'
    }
    url = "https://www.digitale-sammlungen.de/api/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.digitale-sammlungen.de/en/search'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print("Success!")
            data = json.loads(response.read().decode('utf-8'))
            print(json.dumps(data, indent=2)[:500])
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        try:
            body = e.read().decode('utf-8')
            print("Error body preview:")
            print(body[:500])
        except Exception as read_err:
            print(f"Could not read body: {read_err}")
    except Exception as e:
        print(f"Other Error: {e}")

if __name__ == "__main__":
    test_bsb_with_headers("jinan")
