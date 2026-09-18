import urllib.request
import urllib.parse
import json

def inspect_rumsey_results(query):
    print(f"\n--- Results for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.davidrumsey.com/luna/servlet/as/search?os=0&q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read())
            results = data.get('results', [])
            for idx, res in enumerate(results):
                print(f"\nResult {idx + 1}:")
                # Print all keys to see what's available
                # print(list(res.keys()))
                title = res.get('title')
                author = res.get('author')
                pub_date = res.get('pubDate')
                # Let's see some other potential fields
                img_url = res.get('url')
                # Try to extract details or identify where the manifest is
                print(f"  Title: {title}")
                print(f"  Author: {author}")
                print(f"  PubDate: {pub_date}")
                print(f"  Url: {img_url}")
                # Print the entire record or key fields
                # Let's inspect some other interesting keys
                for key in ['pubListNo', 'recordId', 'fieldValues', 'attributes']:
                    if key in res:
                        print(f"  {key}: {res[key]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_rumsey_results("jinan")
    inspect_rumsey_results("tsinan")
