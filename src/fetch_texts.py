import os
import requests
import pandas as pd
from datetime import datetime

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

STORES = [
    "Lululemon Robson Street Vancouver",
    "Lululemon Georgia Street Pacific Centre Vancouver",
    "Lululemon Kitsilano Vancouver",
    "Lululemon Metropolis at Metrotown",
    "Lululemon Richmond at Richmon Centre",
    "Lululemon Burnaby Brentwood",
    "Lululemon West Vancouver Park Royal",
]

RAW_DIR = "data/raw"
OUTPUT_FILE = f"{RAW_DIR}/reviews_raw.csv"

def text_search(query):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": API_KEY}
    return requests.get(url, params=params).json()

def place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,reviews",
        "key": API_KEY,
    }
    return requests.get(url, params=params).json()

def main():
    if not API_KEY:
        raise EnvironmentError("GOOGLE_MAPS_API_KEY not set")

    os.makedirs(RAW_DIR, exist_ok=True)
    records = []

    for store in STORES:
        print(f"Fetching: {store}")
        search = text_search(store)

        if not search.get("results"):
            print(f"⚠️ No Text Search result for {store}")
            continue

        place_id = search["results"][0]["place_id"]
        details = place_details(place_id)

        reviews = details.get("result", {}).get("reviews", [])
        print(f"→ {len(reviews)} reviews")

        for r in reviews:
            records.append({
                "date": datetime.utcnow().date(),
                "store_name": store,
                "rating": r.get("rating"),
                "text": r.get("text"),
            })

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} reviews → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
