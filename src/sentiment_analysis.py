import os
import pandas as pd
from transformers import pipeline

INPUT = "data/raw/texts.csv"
OUTPUT = "data/processed/sentiment_enriched.csv"

def main():
    if not os.path.exists(INPUT):
        raise FileNotFoundError(f"{INPUT} does not exist")

    df = pd.read_csv(INPUT)

    if df.empty:
        raise ValueError("Input CSV is empty. No texts to analyze.")

    if "text" not in df.columns:
        raise ValueError("Missing 'text' column in input CSV")

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    df["sentiment"] = df["text"].apply(
        lambda x: sentiment_pipeline(x[:512])[0]["label"]
    )

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print(f"Sentiment analysis saved to {OUTPUT}")

if __name__ == "__main__":
    main()
