import subprocess
import os
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

collections = [
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
    "wikidata"
]

city_keywords = {
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
    "Zibo": ["zibo", "zhangdian"]
}

def run_single_search(coll, q):
    script_name = f"search_{coll}.py"
    script_path = os.path.join("/home/coder/iiif", script_name)
    if not os.path.exists(script_path):
        return []
        
    try:
        res = subprocess.run(["python3", script_path, q], capture_output=True, text=True, timeout=12)
        stdout = res.stdout
        results = []
        for line in stdout.split('\n'):
            if line.startswith("[KUNMING_MAP]") or line.startswith("[MAP]") or "[KUNMING_MAP]" in line:
                match = re.search(r'Title:\s*(.*?)\s*\|\s*Manifest:\s*(.*?)\s*\|\s*Collection:\s*(.*?)\s*\|\s*Metadata:\s*(.*)', line)
                if match:
                    results.append({
                        'title': match.group(1).strip(),
                        'manifest': match.group(2).strip(),
                        'collection': match.group(3).strip(),
                        'metadata': match.group(4).strip(),
                        'query': q
                    })
        return results
    except subprocess.TimeoutExpired:
        # Silently skip timeouts to keep execution moving smoothly
        pass
    except Exception:
        pass
    return []

def run():
    print("Starting concurrent Map Search across 16 API collections for 38 cities...")
    
    # Store all maps found grouped by city
    all_city_maps = {}
    
    with ThreadPoolExecutor(max_workers=24) as executor:
        future_to_task = {}
        for city, queries in city_keywords.items():
            for coll in collections:
                for q in queries:
                    future = executor.submit(run_single_search, coll, q)
                    future_to_task[future] = (city, coll, q)
                    
        print(f"Submitted {len(future_to_task)} search tasks to thread pool.")
        
        # Gather results as they complete
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
                
    # Now, process, filter and deduplicate results for each city
    processed_city_maps = {}
    total_maps_found = 0
    for city in city_keywords.keys():
        raw_maps = all_city_maps.get(city, [])
        seen_manifests = set()
        seen_titles = set()
        filtered_maps = []
        
        for r in raw_maps:
            title = r['title']
            manifest = r['manifest']
            collection = r['collection']
            metadata = r['metadata']
            
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
            is_map = any(kw in text_to_check for kw in ["map", "carte", "plan", "atlas", "karte", "chart", "topograph", "geograph", "road", "route", "survey"])
            if "David Rumsey" in collection or "Digital Commonwealth" in collection:
                is_map = True
                
            if is_map:
                filtered_maps.append(r)
                
        processed_city_maps[city] = filtered_maps
        total_maps_found += len(filtered_maps)
        print(f"City {city}: found {len(filtered_maps)} maps after deduplication.")
        
    # Write to iiif_endpoints.csv
    csv_path = "/home/coder/iiif/iiif_endpoints.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["city", "collection", "title", "manifest_url"])
        for city, maps in processed_city_maps.items():
            for m in maps:
                if m['manifest']:
                    writer.writerow([city, m['collection'], m['title'], m['manifest']])
    print(f"\nWrote all IIIF manifest URLs to: {csv_path}")
    
    # Write to maps.txt
    txt_path = "/home/coder/iiif/maps.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("                       MAPS OF 38 CHINESE CITIES\n")
        f.write("================================================================================\n\n")
        
        for city, maps in processed_city_maps.items():
            f.write("================================================================================\n")
            f.write(f"  {city.upper()} (Found {len(maps)} maps)\n")
            f.write("================================================================================\n\n")
            
            if not maps:
                f.write("No maps found for this city.\n\n")
                continue
                
            for idx, m in enumerate(maps):
                f.write(f"{idx+1}. {m['title']}\n")
                f.write(f"   - Collection: {m['collection']}\n")
                f.write(f"   - IIIF Manifest: {m['manifest'] if m['manifest'] else 'N/A'}\n")
                f.write(f"   - Metadata: {m['metadata']}\n")
                f.write(f"   - Matching query: '{m['query']}'\n\n")
                
    print(f"Wrote narrative results to: {txt_path}")
    
    # Print a summary of findings to the screen
    print("\n================================================================================")
    print("                      SUMMARY OF SEARCH FINDINGS")
    print("================================================================================")
    for city, maps in processed_city_maps.items():
        if maps:
            print(f"{city}: Found {len(maps)} maps.")
            for idx, m in enumerate(maps[:2]):
                print(f"  [{idx+1}] {m['title']} ({m['collection']})")
                if m['manifest']:
                    print(f"      Manifest: {m['manifest']}")

if __name__ == "__main__":
    run()
