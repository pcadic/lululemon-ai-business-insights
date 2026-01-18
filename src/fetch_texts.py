import os
import pandas as pd
from datetime import datetime
import requests

# -----------------------------
# Configuration
# -----------------------------
OUTPUT_DIR = "data/raw"
OUTPUT_FILE = "reviews_raw.csv"
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")  # clé Google Cloud
CITY = "Vancouver"
BRAND = "Lululemon"
PLACE_IDS = [
    # Exemples d’IDs Google Places de quelques magasins Lululemon à Vancouver
    "ChIJN1t_tDeuEmsRUsoyG83frY4",
    "ChIJN2t_tDeuEmsRUsoyG83frY5",
]

# -----------------------------
# Fonction pour récupérer les avis d’un place_id
# -----------------------------
def get_place_reviews(place_id):
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=name,rating,reviews&key={API_KEY}"
    )
    r = requests.get(url)
    data = r.json()
    reviews = data.get("result", {}).get("reviews", [])
    output = []
    for rev in reviews:
        output.append({
            "place_id": place_id,
            "place_name": data.get("result", {}).get("name", ""),
            "author_name": rev.get("author_name"),
            "rating": rev.get("rating"),
            "text": rev.get("text"),
            "time": rev.get("time")
        })
    return output

# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_reviews = []

    for pid in PLACE_IDS:
        reviews = get_place_reviews(pid)
        all_reviews.extend(reviews)

    df = pd.DataFrame(all_reviews)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} reviews to {output_path}")

if __name__ == "__main__":
    main()
