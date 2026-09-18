#!/usr/bin/env python3
"""
get_contained_maps.py

Queries the Allmaps Annotation API to retrieve all georeferenced maps
that fall completely within a specified bounding box or GeoJSON polygon.

Outputs the results to a CSV file.
"""

import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request

# Default bounding box from user's GeoJSON polygon
DEFAULT_MIN_LAT = 29.936143044744
DEFAULT_MIN_LNG = 99.58303232804826
DEFAULT_MAX_LAT = 37.72766388073677
DEFAULT_MAX_LNG = 115.01522661092787

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_CSV = os.path.join(BASE_DIR, "contained_maps.csv")


def extract_label(label_obj) -> str:
    """Extracts a readable string from a IIIF language-map or plain string."""
    if not label_obj:
        return ""
    if isinstance(label_obj, str):
        return label_obj.strip()
    if isinstance(label_obj, list):
        return "; ".join([extract_label(x) for x in label_obj if x])
    if isinstance(label_obj, dict):
        parts = []
        for values in label_obj.values():
            if isinstance(values, list):
                parts.extend([str(v) for v in values if v])
            elif values:
                parts.append(str(values))
        return "; ".join(parts).strip()
    return str(label_obj).strip()


def parse_geojson_bounds(geojson_data):
    """Calculates [min_lat, min_lng, max_lat, max_lng] from GeoJSON."""
    coords = []
    geom = geojson_data.get("geometry", geojson_data)
    gtype = geom.get("type", "")

    def collect(c_list):
        if not c_list:
            return
        if isinstance(c_list[0], (int, float)):
            coords.append(c_list[:2])
        else:
            for sub in c_list:
                collect(sub)

    collect(geom.get("coordinates", []))

    if not coords:
        raise ValueError("No coordinates found in GeoJSON.")

    lons = [pt[0] for pt in coords]
    lats = [pt[1] for pt in coords]

    return min(lats), min(lons), max(lats), max(lons)


def query_allmaps_contained(min_lat, min_lng, max_lat, max_lng, limit=200):
    """
    Queries Allmaps API using containedBy parameter.
    Order: containedBy=minLat,minLng,maxLat,maxLng (South, West, North, East)
    """
    url = (
        f"https://annotations.allmaps.org/maps.geojson?"
        f"containedBy={min_lat},{min_lng},{max_lat},{max_lng}&limit={limit}"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AllmapsContainedMaps/1.0)",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def process_features(features):
    """Processes GeoJSON features into clean dictionary records."""
    records = []

    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {})

        # Extract map ID
        full_id = props.get("id", "")
        map_id_match = re.search(r"maps/([a-f0-9]{16})", full_id)
        map_id = map_id_match.group(1) if map_id_match else full_id

        # Resource / Image Service
        res = props.get("resource", {})
        image_uri = res.get("id") or res.get("uri") or ""

        # Manifest and Titles
        manifest_url = ""
        title = ""
        part_of = res.get("partOf", [])
        if part_of:
            canvas = part_of[0]
            manifest_list = canvas.get("partOf", [])
            if manifest_list:
                manifest_url = manifest_list[0].get("id", "")
                title = extract_label(manifest_list[0].get("label"))
            if not title:
                title = extract_label(canvas.get("label"))

        if not title and image_uri:
            # Fallback title from the image URI filename
            title = urllib.parse.unquote(image_uri.rstrip("/").split("/")[-1])

        # Compute geometry bounds and center
        bounds_str = ""
        center_str = ""
        coords = geom.get("coordinates", [])
        if coords and coords[0]:
            poly_points = coords[0]
            lons = [p[0] for p in poly_points if len(p) >= 2]
            lats = [p[1] for p in poly_points if len(p) >= 2]
            if lons and lats:
                min_lon, max_lon = min(lons), max(lons)
                min_l, max_l = min(lats), max(lats)
                bounds_str = json.dumps([round(min_lon, 6), round(min_l, 6), round(max_lon, 6), round(max_l, 6)])
                center_str = json.dumps([round((min_lon + max_lon) / 2, 6), round((min_l + max_l) / 2, 6)])

        # URLs
        annotation_url = f"https://annotations.allmaps.org/maps/{map_id}"
        viewer_url = f"https://viewer.allmaps.org/?url={annotation_url}"
        editor_url = f"https://editor.allmaps.org/images?url={urllib.parse.quote(image_uri, safe='')}/info.json" if image_uri else ""
        xyz_arcgis = f"https://allmaps.xyz/maps/{map_id}/{{level}}/{{col}}/{{row}}.png"
        xyz_standard = f"https://allmaps.xyz/maps/{map_id}/{{z}}/{{x}}/{{y}}.png"
        tilejson_url = f"https://allmaps.xyz/maps/{map_id}/tiles.json"

        # Scale & Area
        allmaps_meta = props.get("_allmaps", {})
        area_m2 = allmaps_meta.get("area")
        scale = allmaps_meta.get("scale")

        records.append({
            "map_id": map_id,
            "title": title,
            "manifest_url": manifest_url,
            "image_service_url": image_uri,
            "area_sq_m": f"{area_m2:.2f}" if isinstance(area_m2, (int, float)) else "",
            "scale": f"{scale:.2f}" if isinstance(scale, (int, float)) else "",
            "bounds": bounds_str,
            "center": center_str,
            "viewer_url": viewer_url,
            "editor_url": editor_url,
            "xyz_tile_url_arcgis": xyz_arcgis,
            "xyz_tile_url_standard": xyz_standard,
            "tilejson_url": tilejson_url,
            "annotation_url": annotation_url,
        })

    # Sort by title, then map_id
    records.sort(key=lambda x: (x["title"].lower(), x["map_id"]))
    return records


def main():
    parser = argparse.ArgumentParser(
        description="Query Allmaps API for maps completely contained within a bounding box."
    )
    parser.add_argument("--min-lat", type=float, default=DEFAULT_MIN_LAT, help="South latitude")
    parser.add_argument("--min-lng", type=float, default=DEFAULT_MIN_LNG, help="West longitude")
    parser.add_argument("--max-lat", type=float, default=DEFAULT_MAX_LAT, help="North latitude")
    parser.add_argument("--max-lng", type=float, default=DEFAULT_MAX_LNG, help="East longitude")
    parser.add_argument("--geojson", type=str, help="Path to GeoJSON file to derive bounding box from")
    parser.add_argument("--limit", type=int, default=200, help="Max results from Allmaps API (default 200)")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_CSV, help="Output CSV path")

    args = parser.parse_args()

    min_lat = args.min_lat
    min_lng = args.min_lng
    max_lat = args.max_lat
    max_lng = args.max_lng

    if args.geojson:
        with open(args.geojson, "r", encoding="utf-8") as f:
            data = json.load(f)
        min_lat, min_lng, max_lat, max_lng = parse_geojson_bounds(data)
        print(f"Extracted bounding box from {args.geojson}:")

    print(f"Querying Allmaps API for maps strictly contained in:")
    print(f"  Latitude:  [{min_lat:.6f}, {max_lat:.6f}]")
    print(f"  Longitude: [{min_lng:.6f}, {max_lng:.6f}]")

    data = query_allmaps_contained(min_lat, min_lng, max_lat, max_lng, limit=args.limit)
    features = data.get("features", [])
    print(f"\nFound {len(features)} maps completely within the area.")

    records = process_features(features)

    # Write CSV
    fieldnames = [
        "map_id",
        "title",
        "manifest_url",
        "image_service_url",
        "area_sq_m",
        "scale",
        "bounds",
        "center",
        "viewer_url",
        "editor_url",
        "xyz_tile_url_arcgis",
        "xyz_tile_url_standard",
        "tilejson_url",
        "annotation_url",
    ]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} maps to: {args.output}\n")

    # Display preview table
    print("=" * 100)
    print(f"{'#':<3} | {'MAP ID':<18} | {'AREA (m²)':<12} | {'TITLE':<40} | {'VIEWER URL'}")
    print("=" * 100)
    for idx, r in enumerate(records[:15], 1):
        title_snippet = (r['title'][:37] + "...") if len(r['title']) > 40 else r['title']
        print(f"{idx:<3} | {r['map_id']:<18} | {r['area_sq_m']:<12} | {title_snippet:<40} | {r['viewer_url']}")

    if len(records) > 15:
        print(f"... and {len(records) - 15} more maps in {args.output}")
    print("=" * 100)


if __name__ == "__main__":
    main()
