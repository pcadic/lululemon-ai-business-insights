import pandas as pd
from transformers import pipeline
import os

INPUT = "data/processed/sentiment_enriched.csv"
OUTPUT = "data/processed/topic_enriched.csv"

TOPICS = [
    "Product quality",
    "Pricing",
    "Customer service",
    "Store experience",
    "Sustainability",
    "Brand perception"
]

def main():
    df = pd.read_csv(INPUT)

    classifier = pipeline("zero-shot-classification")

    df["topic"] = df["text"].apply(
        lambda x: classifier(x[:512], TOPICS)["labels"][0]
    )

    df.to_csv(OUTPUT, index=False)
    print(f"Saved topics → {OUTPUT}")

if __name__ == "__main__":
    main()
