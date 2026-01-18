import os
import pandas as pd
from transformers import pipeline

# ======================================
# Configuration
# ======================================

INPUT_FILE = "data/processed/sentiment_enriched.csv"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = "topic_enriched.csv"

# Les topics business que tu veux suivre
TOPICS = [
    "Customer Service",
    "Product Quality",
    "Pricing",
    "Store Experience",
    "Online Shopping",
    "Sustainability",
    "Delivery",
    "Returns"
]

MODEL_NAME = "facebook/bart-large-mnli"  # zero-shot classifier

# ======================================
# Main
# ======================================

def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"{INPUT_FILE} not found")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("Input CSV is empty")

    classifier = pipeline("zero-shot-classification", model=MODEL_NAME)

    # Fonction d'analyse zero-shot
    def classify_text(text):
        result = classifier(text, candidate_labels=TOPICS)
        # On prend le topic avec le score le plus élevé
        return result["labels"][0], result["scores"][0]

    topics = df["text"].astype(str).apply(classify_text)
    df["topic_label"] = topics.apply(lambda x: x[0])
    df["topic_score"] = topics.apply(lambda x: x[1])

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"Topic classification completed: {output_path}")
    print(df.groupby(["store_name", "topic_label"]).size())


if __name__ == "__main__":
    main()
