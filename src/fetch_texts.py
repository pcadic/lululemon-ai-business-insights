import os
import pandas as pd
import requests
import json

# -----------------------------
# Config
# -----------------------------
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise EnvironmentError("GOOGLE_MAPS_API_KEY not set")

OUTPUT_DIR = "data/raw"
OUTPUT_FILE = "reviews_raw.csv"

DEBUG_DIR = os.path.join(OUTPUT_DIR, "debug")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

# Magasins à analyser
STORES = [
    "Lululemon Robson Street, Vancouver, Canada",
    "Lululemon West Edmonton Mall, Edmonton, Canada"
]

# -----------------------------
# Fonctions
# -----------------------------
def fetch_reviews_for_store(store_name):
    print(f"\nDEBUG: Start fetching reviews for '{store_name}'")

    # 1️⃣ Text Search
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": store_name, "key": API_KEY}
    resp_search = requests.get(search_url, params=params).json()
    
    # Log complet pour debug
    debug_file_search = os.path.join(DEBUG_DIR, f"debug_textsearch_{store_name.replace(' ','_')}.json")
    with open(debug_file_search, "w") as f:
        json.dump(resp_search, f, indent=2)
    print(f"DEBUG: Text Search response saved to {debug_file_search}")

    if not resp_search.get("results"):
        print(f"WARNING: Aucun résultat Text Search pour '{store_name}'")
        return []

    place_id = resp_search["results"][0]["place_id"]
    print(f"DEBUG: Found place_id={place_id} for '{store_name}'")

    # 2️⃣ Place Details
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": "name,rating,reviews", "key": API_KEY}
    resp_details = requests.get(details_url, params=params).json()

    # Log complet pour debug
    debug_file_details = os.path.join(DEBUG_DIR, f"debug_placedetails_{store_name.replace(' ','_')}.json")
    with open(debug_file_details, "w") as f:
        json.dump(resp_details, f, indent=2)
    print(f"DEBUG: Place Details response saved to {debug_file_details}")

    reviews = resp_details.get("result", {}).get("reviews", [])
    if not reviews:
        print(f"WARNING: Pas de reviews dans Place Details pour '{store_name}'")
    
    for r in reviews:
        r["store_name"] = store_name

    print(f"DEBUG: Number of reviews fetched for '{store_name}': {len(reviews)}")
    return reviews

# -----------------------------
# Main
# -----------------------------
def main():
    all_reviews = []

    for store in STORES:
        store_reviews = fetch_reviews_for_store(store)
        all_reviews.extend(store_reviews)

    # fallback si aucune review pour tous les magasins
    if not all_reviews:
        print("WARNING: Aucune review récupérée pour tous les magasins, création CSV vide.")
        df = pd.DataFrame(columns=["store_name","author_name","rating","text","time"])
    else:
        df = pd.DataFrame(all_reviews)
        # garder seulement colonnes utiles
        df = df[["store_name","author_name","rating","text","time"]]

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} reviews to {output_path}")


if __name__ == "__main__":
    main()
