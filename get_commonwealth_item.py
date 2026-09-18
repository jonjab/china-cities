import urllib.request
import re
import json

def inspect_commonwealth_item(item_id):
    url = f"https://www.digitalcommonwealth.org{item_id}"
    print(f"Fetching item: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', html)
            if title_match:
                print("Title:", title_match.group(1).strip())
            
            # Print manifest URL
            manifest_url = f"https://www.digitalcommonwealth.org{item_id}/manifest"
            print("Manifest URL:", manifest_url)
            
            # Let's fetch the manifest to verify!
            print("\nFetching and verifying manifest...")
            with urllib.request.urlopen(urllib.request.Request(manifest_url, headers={'User-Agent': 'Mozilla/5.0'})) as mf_resp:
                manifest_data = json.loads(mf_resp.read().decode('utf-8'))
                print("Label:", manifest_data.get('label'))
                print("Description:", manifest_data.get('description'))
                # Print metadata
                metadata = manifest_data.get('metadata', [])
                for m in metadata:
                    print(f"  {m.get('label')}: {m.get('value')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_commonwealth_item("/search/commonwealth:7s75jr08r")
