import urllib.request
import urllib.parse
import json

def test_bl_site_search(query):
    print(f"\n--- BL Site Search for: {query} ---")
    encoded_query = urllib.parse.quote(query)
    # British Library web search (often powered by a search API or Google Custom Search)
    # Let's see if we can query their main website search:
    url = f"https://www.bl.uk/search?q={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            print(f"Success! HTML length: {len(html)}")
            # Check for results or error messages
            if "No results found" in html:
                print("No results found on site search.")
            else:
                # Find some links
                import re
                links = re.findall(r'href="([^"]*)"', html)
                print(f"Found {len(links)} links. Top 10:")
                for l in list(set(links))[:10]:
                    print(f"  {l}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bl_site_search("jinan")
    test_bl_site_search("tsinan")
