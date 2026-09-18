import urllib.request
import urllib.parse
import re

def inspect_getty_results(query):
    print(f"\n--- Inspecting Getty search for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.getty.edu/gateway/search?q={encoded_query}&cat=highlight&rows=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            # Look for "No Records Found" or actual search result items
            # In Getty Gateway, results are often listed with class="record-title" or similar
            matches = re.findall(r'<a class="[^"]*" href="[^"]*">([^<]*)</a>', html)
            print(f"Found {len(matches)} links with text:")
            # Find all titles/records
            record_titles = re.findall(r'class="record-title"[^>]*>(.*?)</a>', html, re.DOTALL)
            print(f"Record titles found: {len(record_titles)}")
            for t in record_titles:
                print(f"  Record Title: {t.strip()}")
                
            # Let's see if the word "jinan" or "tsinan" appears in the page text other than the query
            # Strip tags and see if query appears
            text = re.sub(r'<[^>]+>', ' ', html)
            occurrences = len(re.findall(re.escape(query), text, re.IGNORECASE))
            print(f"Occurrences of keyword '{query}' in body text: {occurrences}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_getty_results("jinan")
    inspect_getty_results("tsinan")
