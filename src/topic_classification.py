import pandas as pd
from transformers import pipeline

INPUT = "data/processed/sentiment_enriched.csv"
OUTPUT = "data/processed/topic_enriched.csv"

LABELS = [
    "Product Quality",
    "Customer Service",
    "Store Experience",
    "Pricing",
    "Brand Image"
]

def main():
    df = pd.read_csv(INPUT)
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    df["topic"] = df["text"].apply(
        lambda x: classifier(x[:512], LABELS)["labels"][0]
    )

    df.to_csv(OUTPUT, index=False)
    print("Topic classification completed")

if __name__ == "__main__":
    main()
