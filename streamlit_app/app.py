import pandas as pd
import streamlit as st
from transformers import pipeline

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

# -----------------------------
# KPI Table
# -----------------------------
st.header("Theme-wise Sentiment KPIs")
st.dataframe(insights_df)

# -----------------------------
# Graphiques
# -----------------------------
st.header("Sentiment Distribution by Theme")
for theme in insights_df['theme']:
    theme_data = insights_df[insights_df['theme'] == theme]
    chart_data = pd.DataFrame({
        'Positive': [theme_data['percent_positive'].values[0]],
        'Negative': [theme_data['percent_negative'].values[0]],
        'Neutral': [theme_data['percent_neutral'].values[0]]
    })
    st.subheader(theme)
    st.bar_chart(chart_data)

# -----------------------------
# Texts with Topics & Sentiment
# -----------------------------
st.header("Texts with Predicted Topics & Sentiment")
st.dataframe(topics_df[["date", "source", "title", "predicted_topics", "sentiment_label"]])

# -----------------------------
# Hugging Face Summarization
# -----------------------------
st.header("Automatic Summary of Texts")

summary_model_name = "facebook/bart-large-cnn"
try:
    summarizer = pipeline("summarization", model=summary_model_name)
except Exception as e:
    st.warning(f"Could not load summarizer: {e}")
    summarizer = None

if summarizer:
    texts_to_summarize = " ".join(topics_df["text"].tolist())
    if len(texts_to_summarize.strip()) > 0:
        summary = summarizer(texts_to_summarize, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        st.write(summary)
    else:
        st.write("No texts available for summarization.")
