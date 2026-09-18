import urllib.request
import urllib.parse
import json

def search_ia_broad():
    print("--- Broad Searching Internet Archive ---")
    queries = [
        "tsinan",
        "jinan"
    ]
    all_results = []
    for q in queries:
        print(f"Query: {q}")
        params = {
            'q': q,
            'fl[]': 'identifier,title,mediatype,subject',
            'rows': '10',
            'output': 'json'
        }
        url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                docs = data.get('response', {}).get('docs', [])
                print(f"  Found {len(docs)} documents.")
                for doc in docs[:5]:
                    print(f"    - ID: {doc.get('identifier')}, Title: {doc.get('title')}, Mediatype: {doc.get('mediatype')}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    search_ia_broad()
