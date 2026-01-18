import pandas as pd
import os

SENTIMENT_FILE = "data/processed/sentiment_enriched.csv"
TOPIC_FILE = "data/processed/topic_enriched.csv"
OUTPUT_FILE = "data/processed/business_insights.csv"

def main():
    df = pd.read_csv(SENTIMENT_FILE)
    df_topics = pd.read_csv(TOPIC_FILE)

    df['topic'] = df_topics['topic']

    # Simple pivot pour business insights
    insights = df.groupby('topic')['sentiment_label'].value_counts().unstack(fill_value=0)
    os.makedirs("data/processed", exist_ok=True)
    insights.to_csv(OUTPUT_FILE)
    print(f"Business insights saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
