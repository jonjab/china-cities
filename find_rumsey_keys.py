import urllib.request
import urllib.parse
import json

def find_rumsey_manifest_keys():
    encoded_query = urllib.parse.quote("jinan")
    url = f"https://www.davidrumsey.com/luna/servlet/as/search?os=0&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read())
            results = data.get('results', [])
            if results:
                # Print all keys of the first result
                print("Keys in result:")
                print(results[0].keys())
                # Let's print the value of recordId, isSelected, identity, etc.
                for key in ['recordId', 'identity', 'isSid', 'mediaId', 'name', 'serviceId', 'collectionId']:
                    print(f"{key}: {results[0].get(key)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_rumsey_manifest_keys()
