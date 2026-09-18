import subprocess
import os
import csv
import re
import sys
import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1osrZXOP9br9ADsk1X8HljCJ8mergHiaEPwVHld8AprA/export?format=csv"
)

COLLECTIONS = [
    "bsb",
    "gallica",
    "bl",
    "cultural_japan",
    "rumsey",
    "digital_commonwealth",
    "europeana",
    "harvard",
    "huntington",
    "ia",
    "getty",
    "loc",
    "finna",
    "bodleian",
    "wellcome",
    "wikidata",
]

# Historical, Wade-Giles, and postal romanization aliases for Chinese cities
CITY_ALIASES = {
    "Baicheng": ["baicheng", "paicheng"],
    "Baoding": ["baoding", "paoting", "paoting-fu"],
    "Binzhou": ["binzhou", "pinchow"],
    "Chengdu": ["chengdu", "chengtu", "chengtu-fu"],
    "Dandong": ["dandong", "antung", "an-tung"],
    "Datong": ["datong", "tatung", "tatung-fu"],
    "Dongying": ["dongying"],
    "Fuxin": ["fuxin", "fushin"],
    "Guilin": ["guilin", "kweilin", "kweilin-fu"],
    "Haikou": ["haikou", "hoihow"],
    "Harbin": ["harbin", "kharbin"],
    "Heyuan": ["heyuan", "hoyun"],
    "Hohhot": ["hohhot", "kweisui", "kuei-sui"],
    "Hotan": ["hotan", "khotan"],
    "Huangshan": ["huangshan", "huizhou"],
    "Hunchun": ["hunchun", "hun-ch'un"],
    "Jinan": ["jinan", "tsinan", "tsi-nan"],
    "Jining": ["jining", "tsining"],
    "Kashgar": ["kashgar", "kashi"],
    "Korla": ["korla", "kurla"],
    "Kunming": ["kunming", "yunnanfou", "yunnan fu", "yunnan-fu"],
    "Lanzhou": ["lanzhou", "lanchow"],
    "Lianyungang": ["lianyungang", "haizhou"],
    "Liaocheng": ["liaocheng", "dongchang"],
    "Liaoyuan": ["liaoyuan"],
    "Luzhou": ["luzhou", "luchow"],
    "Nanchang": ["nanchang", "nan-ch'ang"],
    "Panjin": ["panjin"],
    "Shenzhen": ["shenzhen", "shumchum", "shamchun"],
    "Shijiazhuang": ["shijiazhuang", "shikiachwang"],
    "Taishan": ["taishan", "toishan"],
    "Taizhou": ["taizhou", "taichow"],
    "Tieling": ["tieling", "t'ie-ling"],
    "Ulanqab": ["ulanqab"],
    "Urumqi": ["urumqi", "tihwa", "tihua"],
    "Weihai": ["weihai", "weihaiwei"],
    "Wuhan": ["wuhan", "hankow", "wuchang", "hanyang"],
    "Wuhu": ["wuhu", "wu-hu"],
    "Wuwei": ["wuwei", "liangchow"],
    "Xiamen": ["xiamen", "amoy"],
    "Xi'an": ["xi'an", "sian", "singan", "sianfu"],
    "Yangzhou": ["yangzhou", "yangchow"],
    "Yichang": ["yichang", "ichang"],
    "Zhangjiajie": ["zhangjiajie", "dayong"],
    "Zhengzhou": ["zhengzhou", "chengchow"],
    "Zhuhai": ["zhuhai", "xiangshan"],
    "Zibo": ["zibo", "zhangdian"],
}


def fetch_cities_from_google(url=DEFAULT_GOOGLE_SHEET_URL, local_fallback=None):
    """Fetches the city list dynamically from Google Sheets CSV export URL.

    Falls back to a local CSV file or CITY_ALIASES keys if network is unavailable.
    """
    cities = []
    # 1. Fetch from Google Sheets
    try:
        print(f"Fetching city list directly from Google Sheets: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            reader = csv.reader(content.splitlines())
            for row in reader:
                if not row:
                    continue
                city = row[0].strip()
                # Skip header lines if present
                if not city or city.lower() in ("city", "name", "cities", "city name"):
                    continue
                if city not in cities:
                    cities.append(city)
            if cities:
                print(f"Successfully loaded {len(cities)} cities from Google Sheets.")
                return cities
    except Exception as e:
        print(f"Warning: Could not fetch from Google Sheets ({e}). Falling back.")

    # 2. Fallback to local file if provided
    if local_fallback and os.path.exists(local_fallback):
        with open(local_fallback, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                city = row[0].strip()
                if not city or city.lower() in ("city", "name", "cities", "city name"):
                    continue
                if city not in cities:
                    cities.append(city)
        print(f"Loaded {len(cities)} cities from local fallback {local_fallback}.")
        return cities

    # 3. Fallback to known city aliases
    print(f"Loaded {len(CITY_ALIASES)} cities from default city list.")
    return list(CITY_ALIASES.keys())


def get_city_queries(city):
    """Returns search query keywords for a city (using aliases if available)."""
    return CITY_ALIASES.get(city, [city.lower()])


def run_single_search(coll, q):
    """Executes search script for a collection with a specific query."""
    script_name = f"search_{coll}.py"
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        return []

    try:
        res = subprocess.run(["python3", script_path, q], capture_output=True, text=True, timeout=15)
        stdout = res.stdout
        results = []
        for line in stdout.split("\n"):
            if line.startswith("[KUNMING_MAP]") or line.startswith("[MAP]") or "[KUNMING_MAP]" in line:
                match = re.search(
                    r"Title:\s*(.*?)\s*\|\s*Manifest:\s*(.*?)\s*\|\s*Collection:\s*(.*?)\s*\|\s*Metadata:\s*(.*)",
                    line,
                )
                if match:
                    results.append(
                        {
                            "title": match.group(1).strip(),
                            "manifest": match.group(2).strip(),
                            "collection": match.group(3).strip(),
                            "metadata": match.group(4).strip(),
                            "query": q,
                        }
                    )
        return results
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass
    return []


def write_outputs(cities, processed_city_maps):
    """Writes results to iiif_endpoints.csv and maps.txt."""
    all_cities_ordered = list(cities)

    # 1. Write to iiif_endpoints.csv
    csv_path = os.path.join(BASE_DIR, "iiif_endpoints.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "collection", "title", "manifest_url"])
        for city in all_cities_ordered:
            maps = processed_city_maps.get(city, [])
            for m in maps:
                if m.get("manifest"):
                    writer.writerow([city, m["collection"], m["title"], m["manifest"]])
    print(f"\nWrote all IIIF manifest URLs to: {csv_path}")

    # 2. Write narrative results to maps.txt
    txt_path = os.path.join(BASE_DIR, "maps.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("================================================================================\n")
        f.write(f"                       MAPS OF {len(all_cities_ordered)} CHINESE CITIES\n")
        f.write("================================================================================\n\n")

        for city in all_cities_ordered:
            maps = processed_city_maps.get(city, [])
            f.write("================================================================================\n")
            f.write(f"  {city.upper()} (Found {len(maps)} maps)\n")
            f.write("================================================================================\n\n")

            if not maps:
                f.write("No maps found for this city.\n\n")
                continue

            for idx, m in enumerate(maps):
                f.write(f"{idx + 1}. {m['title']}\n")
                f.write(f"   - Collection: {m['collection']}\n")
                f.write(f"   - IIIF Manifest: {m['manifest'] if m['manifest'] else 'N/A'}\n")
                f.write(f"   - Metadata: {m['metadata']}\n")
                f.write(f"   - Matching query: '{m.get('query', '')}'\n\n")

    print(f"Wrote narrative results to: {txt_path}")


def run(sheet_url=DEFAULT_GOOGLE_SHEET_URL, local_file=None, max_workers=24):
    """Executes the search workflow."""
    cities = fetch_cities_from_google(url=sheet_url, local_fallback=local_file)
    if not cities:
        print("Error: No cities found to search.")
        return

    print(f"Starting concurrent Map Search across {len(COLLECTIONS)} API collections for {len(cities)} cities...")

    all_city_maps = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {}
        for city in cities:
            queries = get_city_queries(city)
            for coll in COLLECTIONS:
                for q in queries:
                    future = executor.submit(run_single_search, coll, q)
                    future_to_task[future] = (city, coll, q)

        print(f"Submitted {len(future_to_task)} search tasks to thread pool.")

        for future in as_completed(future_to_task):
            city, coll, q = future_to_task[future]
            try:
                res_list = future.result()
                if res_list:
                    if city not in all_city_maps:
                        all_city_maps[city] = []
                    all_city_maps[city].extend(res_list)
            except Exception:
                pass

    # Process, filter, and deduplicate results
    processed_city_maps = {}
    total_maps_found = 0
    for city in cities:
        raw_maps = all_city_maps.get(city, [])
        seen_manifests = set()
        seen_titles = set()
        filtered_maps = []

        for r in raw_maps:
            title = r["title"]
            manifest = r["manifest"]
            collection = r["collection"]
            metadata = r["metadata"]

            # Deduplicate
            if manifest:
                if manifest in seen_manifests:
                    continue
                seen_manifests.add(manifest)
            else:
                unique_key = f"{title}||{collection}"
                if unique_key in seen_titles:
                    continue
                seen_titles.add(unique_key)

            # Filter for maps
            text_to_check = (title + " " + metadata).lower()
            is_map = any(
                kw in text_to_check
                for kw in [
                    "map",
                    "carte",
                    "plan",
                    "atlas",
                    "karte",
                    "chart",
                    "topograph",
                    "geograph",
                    "road",
                    "route",
                    "survey",
                ]
            )
            if "David Rumsey" in collection or "Digital Commonwealth" in collection:
                is_map = True

            if is_map:
                filtered_maps.append(r)

        processed_city_maps[city] = filtered_maps
        total_maps_found += len(filtered_maps)

    # Write all outputs
    write_outputs(cities, processed_city_maps)

    print("\n================================================================================")
    print("                      SUMMARY OF SEARCH FINDINGS")
    print("================================================================================")
    for city in cities:
        maps = processed_city_maps.get(city, [])
        if maps:
            print(f"{city}: Found {len(maps)} maps.")
            for idx, m in enumerate(maps[:2]):
                print(f"  [{idx + 1}] {m['title']} ({m['collection']})")
                if m["manifest"]:
                    print(f"      Manifest: {m['manifest']}")


def populate_from_existing():
    """Populates maps.txt and iiif_endpoints.csv directly using previously saved results."""
    cities = fetch_cities_from_google()

    # Load from iiif_endpoints.csv
    endpoints_file = os.path.join(BASE_DIR, "iiif_endpoints.csv")
    processed_city_maps = {}
    if os.path.exists(endpoints_file):
        with open(endpoints_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 4:
                    continue
                c, coll, title, manifest = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
                if c not in processed_city_maps:
                    processed_city_maps[c] = []
                processed_city_maps[c].append(
                    {
                        "collection": coll,
                        "title": title,
                        "manifest": manifest,
                        "metadata": "",
                        "query": "",
                    }
                )

    write_outputs(cities, processed_city_maps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search IIIF Collections for Chinese City Maps")
    parser.add_argument(
        "--sheet-url",
        default=DEFAULT_GOOGLE_SHEET_URL,
        help="Google Sheet CSV URL to fetch city list from",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Local CSV file containing city list (overrides Google Sheet fetch)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=24,
        help="Number of concurrent search workers (default: 24)",
    )
    parser.add_argument(
        "--populate-only",
        action="store_true",
        help="Rebuild maps.txt and iiif_endpoints.csv from existing iiif_endpoints.csv without re-running search APIs",
    )

    args = parser.parse_args()

    if args.populate_only:
        populate_from_existing()
    else:
        run(sheet_url=args.sheet_url, local_file=args.file, max_workers=args.workers)
