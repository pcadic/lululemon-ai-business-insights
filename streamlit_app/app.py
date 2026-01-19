import streamlit as st
import pandas as pd

# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="Lululemon – AI Business Insights",
    layout="wide"
)

st.title("Lululemon – AI Business Insights (Vancouver)")
st.caption(
    "Automated analysis of Google Maps customer reviews using NLP "
    "(Sentiment Analysis & Topic Classification via Hugging Face)."
)

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
    topics = pd.read_csv("data/processed/topic_enriched.csv")
    insights = pd.read_csv("data/processed/business_insights.csv")
    return sentiment, topics, insights

sentiment_df, topics_df, insights_df = load_data()

# -----------------------------
# Executive Summary
# -----------------------------
st.subheader("📌 Executive Summary")

total_reviews = len(sentiment_df)
positive_pct = (
    (sentiment_df["sentiment"] == "POSITIVE").mean() * 100
)

st.markdown(f"""
- **Total reviews analyzed:** {total_reviews}
- **Positive sentiment:** {positive_pct:.1f}%
- **Scope:** Lululemon stores in Vancouver
- **Data source:** Google Maps Reviews
""")

st.divider()

# -----------------------------
# Store selector
# -----------------------------
stores = sorted(sentiment_df["store_name"].unique())
selected_store = st.selectbox("Select a store", stores)

store_sentiment = sentiment_df[
    sentiment_df["store_name"] == selected_store
]
store_topics = topics_df[
    topics_df["store_name"] == selected_store
]
store_insights = insights_df[
    insights_df["store_name"] == selected_store
]

# -----------------------------
# Sentiment section
# -----------------------------
st.subheader("🙂 Customer Sentiment")

sentiment_counts = (
    store_sentiment["sentiment"]
    .value_counts()
    .rename_axis("sentiment")
    .reset_index(name="count")
)

st.bar_chart(
    sentiment_counts.set_index("sentiment")
)

# -----------------------------
# Topics section
# -----------------------------
st.subheader("🧠 Key Topics Identified")

top_topics = (
    store_topics["topic"]
    .value_counts()
    .head(5)
    .reset_index()
    .rename(columns={"index": "Topic", "topic": "Mentions"})
)

st.dataframe(top_topics, use_container_width=True)

# -----------------------------
# Business insights
# -----------------------------
st.subheader("📊 Business Insights")

st.dataframe(
    store_insights.sort_values("count", ascending=False),
    use_container_width=True
)

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "Pipeline fully automated via GitHub Actions • "
    "Updated weekly • No manual intervention"
)
