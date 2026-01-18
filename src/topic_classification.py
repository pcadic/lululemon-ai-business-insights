import os
import pandas as pd
from transformers import pipeline

# -----------------------------
# Configuration
# -----------------------------
INPUT_PATH = "data/processed/sentiment_enriched.csv"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = "topic_enriched.csv"

# Thèmes business pertinents
TOPICS = [
    "product quality",
    "pricing",
    "comfort and fit",
    "sustainability",
    "brand image",
    "customer service",
    "store experience",
    "supply chain"
]

MODEL_NAME = "facebook/bart-large-mnli"

# -----------------------------
# Main logic
# -----------------------------
def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading zero-shot topic classification model...")
    classifier = pipeline("zero-shot-classification", model=MODEL_NAME)

    df = pd.read_csv(INPUT_PATH)

    topics_assigned = []

    print(f"Running zero-shot topic classification on {len(df)} texts...")
    for text in df["text"]:
        result = classifier(text, candidate_labels=TOPICS)
        topics_assigned.append(", ".join(result["labels"][:2]))  # top 2 topics

    df["predicted_topics"] = topics_assigned

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"Topic-enriched data saved to {output_path}")


if __name__ == "__main__":
    main()
