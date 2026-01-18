import os
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================
# Configuration
# ======================================

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise EnvironmentError("GOOGLE_MAPS_API_KEY not set")

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

QUERY = "Lululemon Robson Street Vancouver Canada"
MAX_STORES = 5          # Sécurité quota
SLEEP_SECONDS = 1       # Respect API

OUTPUT_DIR = "data/raw"
OUTPUT_FILE = "reviews_raw.csv"

# ======================================
# Helpers
# ======================================

def text_search_stores():
    params = {
        "query": QUERY,
        "key": GOOGLE_API_KEY
    }
    response = requests.get(TEXT_SEARCH_URL, params=params)
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[:MAX_STORES]


def fetch_place_reviews(place_id):
    params = {
        "place_id": place_id,
        "fields": "name,reviews,rating",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(PLACE_DETAILS_URL, params=params)
    response.raise_for_status()
    result = response.json().get("result", {})
    return result.get("reviews", []), result.get("name")


# ======================================
# Main
# ======================================

def main():
    if not GOOGLE_API_KEY:
        raise EnvironmentError("GOOGLE_MAPS_API_KEY not set")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    stores = text_search_stores()
    all_reviews = []

    for store in stores:
        place_id = store.get("place_id")
        store_name = store.get("name")

        reviews, detailed_name = fetch_place_reviews(place_id)

        for r in reviews:
            all_reviews.append({
                "store_name": detailed_name or store_name,
                "author": r.get("author_name"),
                "rating": r.get("rating"),
                "text": r.get("text"),
                "time": datetime.utcfromtimestamp(
                    r.get("time", 0)
                ).date(),
                "source": "Google Maps"
            })

        time.sleep(SLEEP_SECONDS)

    if not all_reviews:
        raise ValueError("No reviews fetched from Google Maps API")

    df = pd.DataFrame(all_reviews)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"{len(df)} reviews saved to {output_path}")


if __name__ == "__main__":
    main()
