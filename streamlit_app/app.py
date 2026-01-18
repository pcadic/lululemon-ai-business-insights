import subprocess
import pandas as pd
import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="Lululemon AI Insights", layout="wide")

st.title("Lululemon AI Business Insights Dashboard")

# -----------------------------
# 1. Génération automatique des CSV (pipeline complet)
# -----------------------------
st.info("Exécution du pipeline pour générer les données...")

with st.spinner("Pipeline en cours..."):
    subprocess.run(["python", "src/fetch_texts.py"])
    subprocess.run(["python", "src/sentiment_analysis.py"])
    subprocess.run(["python", "src/topic_classification.py"])
    subprocess.run(["python", "src/business_insights.py"])

# -----------------------------
# 2. Lecture des CSV
# -----------------------------
df_sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
df_topic = pd.read_csv("data/processed/topic_enriched.csv")
df_insights = pd.read_csv("data/processed/business_insights.csv")

st.success("Données chargées !")

# -----------------------------
# 3. Visualisations interactives
# -----------------------------
st.subheader("Business Insights")
st.dataframe(df_insights)

st.subheader("Sentiment Distribution")
st.bar_chart(df_sentiment['sentiment_label'].value_counts())

st.subheader("Topic Distribution")
st.bar_chart(df_topic['topic'].value_counts())

# -----------------------------
# 4. Résumé automatique Hugging Face
# -----------------------------
st.subheader("Résumé AI des insights")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

combined_text = " ".join(df_insights['insight'].astype(str).tolist())
summary = summarizer(combined_text, max_length=200, min_length=50, do_sample=False)[0]['summary_text']

st.write(summary)
