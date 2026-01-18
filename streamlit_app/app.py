import pandas as pd
import streamlit as st

# -----------------------------
# Load business insights
# -----------------------------
INSIGHTS_PATH = "../data/processed/business_insights.csv"
TOPICS_PATH = "../data/processed/topic_enriched.csv"

try:
    insights_df = pd.read_csv(INSIGHTS_PATH)
    topics_df = pd.read_csv(TOPICS_PATH)
except FileNotFoundError:
    st.error("Data files not found. Run the GitHub Actions pipeline first.")
    st.stop()

# -----------------------------
# Streamlit Layout
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("Lululemon AI-driven Business Insights")

st.header("Theme-wise Sentiment KPIs")
st.dataframe(insights_df)

st.header("Texts with Predicted Topics & Sentiment")
st.dataframe(topics_df[["date", "source", "title", "predicted_topics", "sentiment_label"]])

# -----------------------------
# KPI summaries
# -----------------------------
st.header("Summary Metrics")
st.metric("Total Texts", len(topics_df))
st.metric("Positive Texts", len(topics_df[topics_df["sentiment_label"]=="POSITIVE"]))
st.metric("Negative Texts", len(topics_df[topics_df["sentiment_label"]=="NEGATIVE"]))
