import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import sys

def search_gallica(query_term):
    print(f"Searching Gallica for: {query_term}")
    query = f'(dc.type all "carte") and (gallica all "{query_term}")'
    params = {
        'operation': 'searchRetrieve',
        'version': '1.2',
        'query': query,
        'maximumRecords': '20'
    }
    url = 'https://gallica.bnf.fr/SRU?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    results = []
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            namespaces = {
                'srw': 'http://www.loc.gov/zing/srw/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'
            }
            records = root.findall('.//srw:record', namespaces)
            for record in records:
                identifier = record.find('.//dc:identifier', namespaces)
                title = record.find('.//dc:title', namespaces)
                
                identifier_text = identifier.text if identifier is not None else ""
                title_text = title.text if title is not None else "No Title"
                
                if "ark:" in identifier_text:
                    ark_start = identifier_text.find("ark:")
                    ark_id = identifier_text[ark_start:]
                    manifest_url = f"https://gallica.bnf.fr/iiif/{ark_id}/manifest.json"
                    results.append({
                        'title': title_text,
                        'manifest': manifest_url,
                        'collection': 'Bibliothèque nationale de France (BnF) / Gallica',
                        'metadata': f"Ark ID: {ark_id}"
                    })
    except Exception as e:
        print(f"Error searching Gallica: {e}")
    return results

if __name__ == "__main__":
    queries = [sys.argv[1]] if len(sys.argv) > 1 else ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"]
    all_results = []
    for q in queries:
        all_results.extend(search_gallica(q))
    
    for r in all_results:
        print(f"[KUNMING_MAP] Title: {r['title']} | Manifest: {r['manifest']} | Collection: {r['collection']} | Metadata: {r['metadata']}")
