import urllib.request
import urllib.parse
import re
import sys

def search_bl(query):
    print(f"Searching British Library for: {query}")
    encoded_query = urllib.parse.quote(query)
    # Primo search URL
    url = f"https://explore.bl.uk/primo_library/libweb/action/search.do?fn=search&ct=search&initialSearch=true&mode=Basic&tab=local&indx=1&dum=true&srt=rank&vid=BLVU1&frbg=&vl(freeText0)={encoded_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            titles = re.findall(r'class="title"[^>]*>(.*?)</a>', html, re.DOTALL)
            hrefs = re.findall(r'href="([^"]*docId=[^"]*)"', html)
            
            for idx, title in enumerate(titles[:10]):
                clean_title = re.sub(r'<[^>]+>', ' ', title).strip()
                # Extract docId
                doc_id = ""
                if idx < len(hrefs):
                    doc_match = re.search(r'docId=([^&]*)', hrefs[idx])
                    if doc_match:
                        doc_id = doc_match.group(1)
                
                # British Library manifest format is typically derived from the docId or similar, but since we may not have the manifest URL directly,
                # let's represent the item as having a potential manifest or build the standard IIIF link if known.
                # For BL, some items are on the universal viewer with doc_id:
                manifest_url = f"https://api.bl.uk/metadata/iiif/{doc_id}" if doc_id else ""
                
                results.append({
                    'title': clean_title,
                    'manifest': manifest_url,
                    'collection': 'British Library',
                    'metadata': f"Doc ID: {doc_id}"
                })
    except Exception as e:
        print(f"Error searching British Library: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_bl(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
