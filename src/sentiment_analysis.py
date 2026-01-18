import pandas as pd
from transformers import pipeline
import os

INPUT = "data/raw/reviews_raw.csv"
OUTPUT = "data/processed/sentiment_enriched.csv"

def main():
    os.makedirs("data/processed", exist_ok=True)
    df = pd.read_csv(INPUT)

    sentiment = pipeline("sentiment-analysis")

    df["sentiment"] = df["text"].apply(
        lambda x: sentiment(x[:512])[0]["label"]
    )

    df.to_csv(OUTPUT, index=False)
    print("Sentiment analysis completed")

if __name__ == "__main__":
    main()
