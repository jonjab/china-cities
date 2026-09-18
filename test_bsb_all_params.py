import urllib.request
import urllib.parse
import json

def test_bsb_all_params():
    # Let's test combinations of startPage, pageSize, ocrContext, etc.
    combinations = [
        {'query': 'jinan', 'handler': 'simple-all', 'ocrContext': 'false', 'startPage': '0', 'pageSize': '10'},
        {'query': 'jinan', 'handler': 'simple-all', 'ocrContext': 'true', 'startPage': '0', 'pageSize': '10'},
        {'query': 'jinan', 'handler': 'simple-all', 'ocrContext': 'false', 'startPage': '1', 'pageSize': '10'},
        {'query': 'jinan', 'handler': 'simple-all', 'ocrContext': 'false', 'startPage': '1', 'pageSize': '24'},
        {'query': 'jinan', 'handler': 'simple-all', 'ocrContext': 'false'},
    ]
    
    for idx, params in enumerate(combinations):
        url = "https://www.digitale-sammlungen.de/api/search?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        })
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"Combination {idx} {params} -> Success!")
                print(response.read().decode('utf-8')[:500])
                return
        except urllib.error.HTTPError as e:
            print(f"Combination {idx} {params} -> HTTP Error {e.code}: {e.reason}")
            try:
                # check if there's any details
                body = e.read().decode('utf-8')
                if "Illegal search parameters" not in body:
                    print(body[:200])
            except:
                pass
        except Exception as e:
            print(f"Combination {idx} {params} -> Other Error: {e}")

if __name__ == "__main__":
    test_bsb_all_params()
