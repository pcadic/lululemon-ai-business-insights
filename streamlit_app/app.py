import pandas as pd
import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("Lululemon AI Business Insights Dashboard")

# -----------------------------
# Charger les CSV déjà générés par GitHub Actions
# -----------------------------
df_sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
df_topic = pd.read_csv("data/processed/topic_enriched.csv")
df_insights = pd.read_csv("data/processed/business_insights.csv")

# -----------------------------
# Affichage
# -----------------------------
st.subheader("Business Insights")
st.dataframe(df_insights)

st.subheader("Sentiment Distribution")
st.bar_chart(df_sentiment['sentiment_label'].value_counts())

st.subheader("Topic Distribution")
st.bar_chart(df_topic['topic'].value_counts())

# -----------------------------
# Résumé automatique Hugging Face
# -----------------------------
st.subheader("Résumé AI des insights")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

combined_text = " ".join(df_insights.apply(lambda row: " ".join(map(str,row)), axis=1).tolist())
summary = summarizer(combined_text, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
st.write(summary)
