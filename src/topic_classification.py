import os
import pandas as pd
from transformers import pipeline

INPUT_FILE = "data/processed/sentiment_enriched.csv"
OUTPUT_FILE = "data/processed/topic_enriched.csv"

CANDIDATE_LABELS = ["Revenue", "Sustainability", "Customer Experience", "Product Quality", "Store Experience"]

def main():
    df = pd.read_csv(INPUT_FILE)
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    df['topic'] = df['text'].apply(lambda x: classifier(x, CANDIDATE_LABELS)['labels'][0])
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Topics added: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
