import pandas as pd
import os

INPUT = "data/processed/topic_enriched.csv"
OUTPUT = "data/processed/business_insights.csv"

def main():
    df = pd.read_csv(INPUT)

    # Normalisation sentiment
    df["sentiment"] = df["sentiment"].str.upper()

    # Aggregation par magasin + topic
    store_level = (
        df
        .groupby(["place_name", "topic", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    store_level["level"] = "STORE"

    # Aggregation globale
    global_level = (
        df
        .groupby(["topic", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    global_level["place_name"] = "ALL_STORES"
    global_level["level"] = "GLOBAL"

    final_df = pd.concat([store_level, global_level], ignore_index=True)

    os.makedirs("data/processed", exist_ok=True)
    final_df.to_csv(OUTPUT, index=False)

    print("Business insights generated")

if __name__ == "__main__":
    main()
