import urllib.request
import urllib.parse
import json

def test_cj_api_params():
    # Test different query params
    params_options = [
        {'q': 'jinan'},
        {'keyword': 'jinan'},
        {'query': 'jinan'},
        {'term': 'jinan'},
    ]
    
    for params in params_options:
        url = "https://api.cultural.jp/search?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
                total = data.get('hits', {}).get('total', {}).get('value', 0)
                first_hit = data.get('hits', {}).get('hits', [{}])[0]
                first_title = first_hit.get('title', {}).get('en', [''])[0] if isinstance(first_hit.get('title'), dict) else ''
                print(f"Params {params} -> Total: {total}, First Title: {first_title}")
        except Exception as e:
            print(f"Params {params} Error: {e}")

if __name__ == "__main__":
    test_cj_api_params()
