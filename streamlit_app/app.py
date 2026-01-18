import streamlit as st
import pandas as pd
from transformers import pipeline

# -----------------------------
# Streamlit page configuration
# -----------------------------
st.set_page_config(
    page_title="Lululemon AI Business Insights",
    layout="wide",
)

st.title("Lululemon AI Business Insights Dashboard")

# -----------------------------
# Load CSVs
# -----------------------------
sentiment_file = "data/processed/sentiment_enriched.csv"
topic_file = "data/processed/topic_enriched.csv"
insights_file = "data/processed/business_insights.csv"

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

try:
    df_sentiment = load_csv(sentiment_file)
    df_topic = load_csv(topic_file)
    df_insights = load_csv(insights_file)
except FileNotFoundError as e:
    st.error(f"CSV not found: {e}")
    st.stop()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")
sources = df_sentiment['source'].unique()
selected_sources = st.sidebar.multiselect("Select source(s):", sources, default=list(sources))

df_sentiment_filtered = df_sentiment[df_sentiment['source'].isin(selected_sources)]
df_topic_filtered = df_topic[df_topic['source'].isin(selected_sources)]

# -----------------------------
# Display business insights
# -----------------------------
st.subheader("Aggregated Business Insights")
st.dataframe(df_insights.style.format("{:.2f}"))

# -----------------------------
# Sentiment distribution
# -----------------------------
st.subheader("Sentiment Distribution by Source")
sentiment_counts = df_sentiment_filtered.groupby(['source', 'sentiment_label']).size().unstack(fill_value=0)
st.bar_chart(sentiment_counts)

# -----------------------------
# Topic distribution
# -----------------------------
st.subheader("Topic Distribution")
topic_counts = df_topic_filtered.groupby(['topic']).size().sort_values(ascending=False)
st.bar_chart(topic_counts)

# -----------------------------
# Sample texts with sentiment and topic
# -----------------------------
st.subheader("Sample Texts")
merged = pd.merge(df_sentiment_filtered, df_topic_filtered, on=['date', 'source', 'title', 'text'])
st.dataframe(merged[['date', 'source', 'title', 'text', 'sentiment_label', 'sentiment_score', 'topic', 'topic_score']])

# -----------------------------
# Hugging Face automatic summary
# -----------------------------
st.subheader("Automatic Business Summary")

@st.cache_resource
def get_summary(texts):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    combined_text = " ".join(texts.tolist())
    # limit length for large texts
    combined_text = combined_text[:3000]
    summary = summarizer(combined_text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

summary_text = get_summary(df_sentiment_filtered['text'])
st.write(summary_text)
