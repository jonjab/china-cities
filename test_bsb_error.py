import urllib.request
import urllib.parse
import json

def test_bsb_with_body(query):
    # Try different combinations of params
    params = {
        'query': query,
        'handler': 'simple-all',
        'ocrContext': 'false'
    }
    url = "https://www.digitale-sammlungen.de/api/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print("Success!")
            print(response.read().decode('utf-8')[:500])
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        try:
            body = e.read().decode('utf-8')
            print("Error body:")
            print(body)
        except Exception as read_err:
            print(f"Could not read body: {read_err}")
    except Exception as e:
        print(f"Other Error: {e}")

if __name__ == "__main__":
    test_bsb_with_body("jinan")
