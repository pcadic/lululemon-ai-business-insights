import os
import pandas as pd
from transformers import pipeline

INPUT_FILE = "data/raw/reviews_raw.csv"
OUTPUT_FILE = "data/processed/sentiment_enriched.csv"

def main():
    df = pd.read_csv(INPUT_FILE)
    sentiment_pipeline = pipeline("sentiment-analysis")

    df['sentiment_label'] = df['text'].apply(lambda x: sentiment_pipeline(x)[0]['label'])
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Sentiment added: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
