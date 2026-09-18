import urllib.request
import urllib.parse
import re

def test_europeana_search(query):
    print(f"\n--- Europeana Search for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.europeana.eu/en/search?query={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            print(f"Status: {response.status}, HTML length: {len(html)}")
            # Let's search for some text like "no results" or look for results
            if "No results" in html or "didn't return any results" in html:
                print("No results found.")
            else:
                # Find some item links
                item_links = set(re.findall(r'href="([^"]*/item/[^"]*)"', html))
                print(f"Found {len(item_links)} item links:")
                for l in list(item_links)[:5]:
                    print(f"  {l}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_europeana_search("jinan")
    test_europeana_search("tsinan")
