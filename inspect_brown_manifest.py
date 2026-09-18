import urllib.request
import json

def inspect_manifest(manifest_url):
    print(f"Fetching manifest: {manifest_url}")
    req = urllib.request.Request(manifest_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("Successfully parsed manifest!")
            # Print label
            print("Label:", data.get('label'))
            # Print description
            print("Description:", data.get('description'))
            # Print metadata
            metadata = data.get('metadata', [])
            print("Metadata:")
            for m in metadata:
                print(f"  {m.get('label')}: {m.get('value')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_manifest("https://repository.library.brown.edu/iiif/presentation/bdr:445321/manifest.json")
