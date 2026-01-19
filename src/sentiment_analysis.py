import pandas as pd
from transformers import pipeline
import os

INPUT = "data/raw/reviews_raw.csv"
OUTPUT = "data/processed/sentiment_enriched.csv"

def main():
    df = pd.read_csv(INPUT)
    if df.empty:
        raise ValueError("Input CSV is empty")

    classifier = pipeline("sentiment-analysis")

    df["sentiment"] = df["text"].apply(
        lambda x: classifier(x[:512])[0]["label"]
    )
    df["sentiment_score"] = df["text"].apply(
        lambda x: classifier(x[:512])[0]["score"]
    )

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Saved sentiment → {OUTPUT}")

if __name__ == "__main__":
    main()
