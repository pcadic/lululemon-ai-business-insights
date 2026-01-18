import os
import pandas as pd

# ======================================
# Configuration
# ======================================

SENTIMENT_FILE = "data/processed/sentiment_enriched.csv"
TOPIC_FILE = "data/processed/topic_enriched.csv"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = "business_insights.csv"

# ======================================
# Main
# ======================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Lecture des fichiers intermédiaires
    df_sentiment = pd.read_csv(SENTIMENT_FILE)
    df_topic = pd.read_csv(TOPIC_FILE)

    # Fusion par magasin + texte
    df = pd.merge(
        df_sentiment,
        df_topic[["store_name", "text", "topic_label"]],
        on=["store_name", "text"],
        how="left"
    )

    # ======================================
    # KPI par magasin
    # ======================================

    insights = []

    for store in df["store_name"].unique():
        df_store = df[df["store_name"] == store]

        total_reviews = len(df_store)
        pos_reviews = len(df_store[df_store["sentiment_label"] == "POSITIVE"])
        neg_reviews = len(df_store[df_store["sentiment_label"] == "NEGATIVE"])
        pos_ratio = pos_reviews / total_reviews if total_reviews else 0
        neg_ratio = neg_reviews / total_reviews if total_reviews else 0

        # Top topics
        top_topics = df_store["topic_label"].value_counts().head(3).to_dict()

        insights.append({
            "store_name": store,
            "total_reviews": total_reviews,
            "positive_ratio": round(pos_ratio, 2),
            "negative_ratio": round(neg_ratio, 2),
            "top_topics": ", ".join(top_topics.keys())
        })

    df_insights = pd.DataFrame(insights)

    # ======================================
    # KPI global Lululemon
    # ======================================

    total_reviews = len(df)
    pos_reviews = len(df[df["sentiment_label"] == "POSITIVE"])
    neg_reviews = len(df[df["sentiment_label"] == "NEGATIVE"])
    pos_ratio = pos_reviews / total_reviews if total_reviews else 0
    neg_ratio = neg_reviews / total_reviews if total_reviews else 0
    top_topics_global = df["topic_label"].value_counts().head(5).to_dict()

    df_insights.loc[len(df_insights)] = {
        "store_name": "Lululemon Total",
        "total_reviews": total_reviews,
        "positive_ratio": round(pos_ratio, 2),
        "negative_ratio": round(neg_ratio, 2),
        "top_topics": ", ".join(top_topics_global.keys())
    }

    # ======================================
    # Export CSV final
    # ======================================

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df_insights.to_csv(output_path, index=False)

    print(f"Business insights generated: {output_path}")
    print(df_insights)


if __name__ == "__main__":
    main()
