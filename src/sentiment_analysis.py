import os
import pandas as pd
from transformers import pipeline

# ======================================
# Configuration
# ======================================

INPUT_FILE = "data/raw/reviews_raw.csv"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = "sentiment_enriched.csv"

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

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

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME
    )

    sentiments = sentiment_pipeline(
        df["text"].astype(str).tolist(),
        truncation=True
    )

    df["sentiment_label"] = [s["label"] for s in sentiments]
    df["sentiment_score"] = [s["score"] for s in sentiments]

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"Sentiment analysis completed: {output_path}")
    print(df.groupby("store_name")["sentiment_label"].value_counts())


if __name__ == "__main__":
    main()
