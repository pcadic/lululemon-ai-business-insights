import os
import requests
import pandas as pd

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_PLACES_API_KEY not set")

OUTPUT_DIR = "data/raw"
OUTPUT_FILE = "reviews_raw.csv"

QUERY = "lululemon store Vancouver"
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def text_search():
    params = {
        "query": QUERY,
        "key": API_KEY
    }
    response = requests.get(TEXT_SEARCH_URL, params=params)
    return response.json().get("results", [])


def get_place_reviews(place_id):
    params = {
        "place_id": place_id,
        "fields": "name,rating,reviews",
        "key": API_KEY
    }
    response = requests.get(DETAILS_URL, params=params)
    result = response.json().get("result", {})
    reviews = result.get("reviews", [])

    rows = []
    for r in reviews:
        rows.append({
            "place_id": place_id,
            "place_name": result.get("name"),
            "rating": r.get("rating"),
            "text": r.get("text")
        })
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_rows = []

    places = text_search()
    for place in places:
        place_id = place["place_id"]
        all_rows.extend(get_place_reviews(place_id))

    df = pd.DataFrame(all_rows)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"{len(df)} reviews saved to {output_path}")

    if df.empty:
        raise ValueError("No reviews fetched from Google Maps API")



if __name__ == "__main__":
    main()
    
