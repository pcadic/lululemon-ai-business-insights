import os
import pandas as pd

# -----------------------------
# Configuration
# -----------------------------
INPUT_PATH = "data/processed/topic_enriched.csv"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = "business_insights.csv"

# -----------------------------
# Main logic
# -----------------------------
def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)

    # -----------------------------
    # KPIs par thème
    # -----------------------------
    themes = set()
    for topics in df["predicted_topics"].dropna():
        for t in topics.split(", "):
            themes.add(t)

    insights = []
    for theme in themes:
        theme_df = df[df["predicted_topics"].str.contains(theme, na=False)]
        total = len(theme_df)
        positive = len(theme_df[theme_df["sentiment_label"] == "POSITIVE"])
        negative = len(theme_df[theme_df["sentiment_label"] == "NEGATIVE"])
        neutral = total - positive - negative

        insights.append({
            "theme": theme,
            "total_mentions": total,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "percent_positive": round(100 * positive / total, 1) if total else 0,
            "percent_negative": round(100 * negative / total, 1) if total else 0,
            "percent_neutral": round(100 * neutral / total, 1) if total else 0
        })

    insights_df = pd.DataFrame(insights)

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    insights_df.to_csv(output_path, index=False)

    print(f"Business insights saved to {output_path}")
    print("\nSample insights:")
    print(insights_df.head())


if __name__ == "__main__":
    main()
