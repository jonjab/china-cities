#!/usr/bin/env python3
"""
check_allmaps_georef.py

Queries the Allmaps Annotation API to determine which IIIF manifests
in `iiif_endpoints.csv` have already been georeferenced.

For each georeferenced map found, extracts:
- Allmaps Map ID
- ArcGIS Online XYZ Tile URL ({level}/{col}/{row}.png)
- Standard XYZ Tile URL ({z}/{x}/{y}.png)
- TileJSON metadata URL
- W3C Georeference Annotation URL
- Allmaps Interactive Web Viewer URL
- Spatial bounding box / center coordinates

Outputs results to `georeferenced_maps.csv` and prints a summary.
"""

import csv
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "iiif_endpoints.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "georeferenced_maps.csv")


def compute_allmaps_id(uri: str) -> str:
    """Computes the 16-character SHA-1 Allmaps identifier for a URI."""
    return hashlib.sha1(uri.strip().encode("utf-8")).hexdigest()[:16]


def get_candidate_endpoints(collection: str, manifest_url: str):
    """Generates candidate (endpoint_type, uri, allmaps_id) tuples to query in Allmaps."""
    candidates = []

    # 1. Manifest-level query
    m_id = compute_allmaps_id(manifest_url)
    candidates.append(("manifests", manifest_url, m_id))

    # 2. Image-level queries based on collection URL conventions
    # David Rumsey
    if "davidrumsey" in manifest_url:
        img_url = manifest_url.replace("/m/", "/").rstrip("/manifest")
        candidates.append(("images", img_url, compute_allmaps_id(img_url)))
        candidates.append(("images", img_url + "/info.json", compute_allmaps_id(img_url + "/info.json")))

    # Gallica (BnF)
    elif "gallica.bnf.fr" in manifest_url:
        base = manifest_url.replace("/manifest.json", "")
        candidates.append(("images", f"{base}/f1", compute_allmaps_id(f"{base}/f1")))
        candidates.append(("images", f"{base}/f1/info.json", compute_allmaps_id(f"{base}/f1/info.json")))

    # Digital Commonwealth
    elif "digitalcommonwealth.org" in manifest_url:
        match = re.search(r"commonwealth:([a-z0-9]+)", manifest_url)
        if match:
            cid = match.group(0)
            img_url = f"https://iiif.digitalcommonwealth.org/iiif/2/{cid}"
            candidates.append(("images", img_url, compute_allmaps_id(img_url)))
            candidates.append(("images", f"{img_url}/info.json", compute_allmaps_id(f"{img_url}/info.json")))

    # Internet Archive
    elif "archivelab.org" in manifest_url or "archive.org" in manifest_url:
        match = re.search(r"iiif/([^/]+)/manifest\.json", manifest_url)
        if match:
            item_id = match.group(1)
            img2 = f"https://iiif.archive.org/image/iiif/2/{item_id}"
            img3 = f"https://iiif.archive.org/image/iiif/3/{item_id}"
            candidates.append(("images", img2, compute_allmaps_id(img2)))
            candidates.append(("images", f"{img2}/info.json", compute_allmaps_id(f"{img2}/info.json")))
            candidates.append(("images", img3, compute_allmaps_id(img3)))

    return candidates


def fetch_json(url: str, timeout: int = 8):
    """Fetches and decodes JSON from a URL with browser headers."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AllmapsGeoRefChecker/1.0)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_manifest(item):
    """Checks Allmaps for annotations associated with a manifest record."""
    city, collection, title, manifest_url = item
    candidates = get_candidate_endpoints(collection, manifest_url)

    matched_maps = []
    seen_map_ids = set()

    for ep_type, target_uri, allmaps_id in candidates:
        anno_url = f"https://annotations.allmaps.org/{ep_type}/{allmaps_id}"
        try:
            data = fetch_json(anno_url, timeout=8)
            items = data.get("items", [])
            # Also handle if data is a single Annotation object rather than AnnotationPage
            if not items and data.get("type") == "Annotation":
                items = [data]

            for it in items:
                map_url = it.get("id", "")
                map_id_match = re.search(r"maps/([a-f0-9]{16})", map_url)
                map_id = map_id_match.group(1) if map_id_match else allmaps_id

                if map_id in seen_map_ids:
                    continue
                seen_map_ids.add(map_id)

                # Fetch tilejson to obtain real-world bounds and zoom levels
                tilejson_url = f"https://allmaps.xyz/maps/{map_id}/tiles.json"
                bounds_str = ""
                center_str = ""
                try:
                    tj = fetch_json(tilejson_url, timeout=5)
                    if "bounds" in tj:
                        bounds_str = json.dumps(tj["bounds"])
                    if "center" in tj:
                        center_str = json.dumps(tj["center"])
                except Exception:
                    pass

                # ArcGIS Online XYZ Tile Layer URL template uses {level}/{col}/{row}.png
                xyz_arcgis = f"https://allmaps.xyz/maps/{map_id}/{{level}}/{{col}}/{{row}}.png"
                xyz_standard = f"https://allmaps.xyz/maps/{map_id}/{{z}}/{{x}}/{{y}}.png"
                map_anno_url = f"https://annotations.allmaps.org/maps/{map_id}"
                viewer_url = f"https://viewer.allmaps.org/?url={map_anno_url}"

                matched_maps.append(
                    {
                        "city": city,
                        "collection": collection,
                        "title": title,
                        "manifest_url": manifest_url,
                        "allmaps_id": allmaps_id,
                        "map_id": map_id,
                        "xyz_tile_url_arcgis": xyz_arcgis,
                        "xyz_tile_url_standard": xyz_standard,
                        "tilejson_url": tilejson_url,
                        "annotation_url": map_anno_url,
                        "viewer_url": viewer_url,
                        "bounds": bounds_str,
                        "center": center_str,
                    }
                )
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
        except Exception:
            continue

    return matched_maps


def run_checker():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        sys.exit(1)

    records = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row and len(row) >= 4:
                records.append([c.strip() for c in row[:4]])

    print(f"Loaded {len(records)} IIIF endpoints from {INPUT_CSV}")
    print("Checking Allmaps Annotation API for existing georeferencing...")

    georeferenced_maps = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(check_manifest, rec) for rec in records]
        for fut in as_completed(futures):
            res_list = fut.result()
            if res_list:
                for res in res_list:
                    georeferenced_maps.append(res)
                    print(
                        f"  [FOUND] {res['city']}: \"{res['title'][:40]}\" -> Map ID: {res['map_id']}"
                    )

    # Sort results by city then title
    georeferenced_maps.sort(key=lambda x: (x["city"], x["title"]))

    # Write out to CSV
    fieldnames = [
        "city",
        "title",
        "collection",
        "map_id",
        "xyz_tile_url_arcgis",
        "xyz_tile_url_standard",
        "tilejson_url",
        "annotation_url",
        "viewer_url",
        "bounds",
        "center",
        "manifest_url",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(georeferenced_maps)

    print(f"\nSuccessfully wrote {len(georeferenced_maps)} georeferenced maps to: {OUTPUT_CSV}")

    # Display clear table for the user
    print("\n" + "=" * 90)
    print("                  ALLMAPS GEOREFERENCED MAPS FOR ARCGIS ONLINE")
    print("=" * 90)
    for idx, m in enumerate(georeferenced_maps, 1):
        print(f"\n{idx}. City: {m['city']} | Title: {m['title']}")
        print(f"   - Collection:          {m['collection']}")
        print(f"   - Map ID:              {m['map_id']}")
        print(f"   - ArcGIS Online XYZ:   {m['xyz_tile_url_arcgis']}")
        print(f"   - Standard XYZ:        {m['xyz_tile_url_standard']}")
        print(f"   - Allmaps Viewer:      {m['viewer_url']}")
        print(f"   - TileJSON:            {m['tilejson_url']}")
        if m["bounds"]:
            print(f"   - Bounding Box:        {m['bounds']}")
    print("\n" + "=" * 90)


if __name__ == "__main__":
    run_checker()
