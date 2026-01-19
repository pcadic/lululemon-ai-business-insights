import pandas as pd
import os

INPUT = "data/processed/topic_enriched.csv"
OUTPUT = "data/processed/business_insights.csv"

def main():
    df = pd.read_csv(INPUT)

    insights = (
        df.groupby(["store_name", "topic", "sentiment"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    insights.to_csv(OUTPUT, index=False)
    print(f"Saved insights → {OUTPUT}")

if __name__ == "__main__":
    main()
