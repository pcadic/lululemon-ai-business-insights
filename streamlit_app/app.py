import streamlit as st
import pandas as pd

# --------------------------------
# Page config
# --------------------------------
st.set_page_config(
    page_title="Lululemon – AI Business Insights",
    layout="wide"
)

st.title("🧠 Lululemon – AI Business Insights")
st.caption("Real Google Maps reviews · Hugging Face NLP · Automated weekly pipeline")

# --------------------------------
# Load data (pre-computed)
# --------------------------------
@st.cache_data
def load_data():
    sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
    topics = pd.read_csv("data/processed/topic_enriched.csv")
    insights = pd.read_csv("data/processed/business_insights.csv")
    return sentiment, topics, insights

sentiment_df, topic_df, insights_df = load_data()

# --------------------------------
# KPI section
# --------------------------------
st.subheader("📊 Executive KPIs")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Reviews Analyzed",
        len(sentiment_df)
    )

with col2:
    positive_rate = (
        (sentiment_df["sentiment_label"] == "POSITIVE").mean() * 100
    )
    st.metric(
        "Positive Sentiment",
        f"{positive_rate:.1f}%"
    )

with col3:
    st.metric(
        "Topics Detected",
        topic_df["topic"].nunique()
    )

st.divider()

# --------------------------------
# Sentiment analysis
# --------------------------------
st.subheader("😊 Sentiment Distribution")

sentiment_counts = sentiment_df["sentiment_label"].value_counts()
st.bar_chart(sentiment_counts)

# --------------------------------
# Topic analysis
# --------------------------------
st.subheader("🏷️ Topic Distribution")

topic_counts = topic_df["topic"].value_counts()
st.bar_chart(topic_counts)

# --------------------------------
# Business insights table
# --------------------------------
st.subheader("📈 Business Insights by Topic")
st.dataframe(insights_df, use_container_width=True)

# --------------------------------
# Raw review explorer (optional)
# --------------------------------
with st.expander("🔍 Explore Raw Reviews"):
    st.dataframe(
        sentiment_df[["place_name", "rating", "sentiment_label", "text"]],
        use_container_width=True
    )

st.divider()

# --------------------------------
# Footer
# --------------------------------
st.caption(
    "Pipeline automated via GitHub Actions · Data updated weekly · "
    "No real-time API calls during visualization"
)
