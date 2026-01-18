import os
import pandas as pd
from transformers import pipeline

# -----------------------------
# Configuration
# -----------------------------
INPUT_PATH = "data/raw/texts.csv"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = "sentiment_enriched.csv"

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

# -----------------------------
# Main logic
# -----------------------------
def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading sentiment analysis model...")
    sentiment_pipeline = pipeline(
        task="sentiment-analysis",
        model=MODEL_NAME,
        truncation=True
    )

    df = pd.read_csv(INPUT_PATH)

    sentiments = []
    scores = []

    print(f"Running sentiment analysis on {len(df)} texts...")
    for text in df["text"]:
        result = sentiment_pipeline(text)[0]
        sentiments.append(result["label"])
        scores.append(result["score"])

    df["sentiment_label"] = sentiments
    df["sentiment_score"] = scores

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"Sentiment-enriched data saved to {output_path}")


if __name__ == "__main__":
    main()
