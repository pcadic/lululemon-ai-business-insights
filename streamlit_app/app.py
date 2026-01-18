import streamlit as st
import pandas as pd

# ======================================
# Configuration
# ======================================
INSIGHTS_FILE = "data/processed/business_insights.csv"
SENTIMENT_FILE = "data/processed/sentiment_enriched.csv"
TOPIC_FILE = "data/processed/topic_enriched.csv"

# ======================================
# Titre
# ======================================
st.set_page_config(page_title="Lululemon Business Insights", layout="wide")
st.title("Lululemon Business Insights Dashboard")
st.markdown("Analyse des avis clients par magasin (Google Maps) – pipeline 100% cloud")

# ======================================
# Lecture des fichiers
# ======================================
df_insights = pd.read_csv(INSIGHTS_FILE)
df_sentiment = pd.read_csv(SENTIMENT_FILE)
df_topic = pd.read_csv(TOPIC_FILE)

# ======================================
# Sélection du magasin
# ======================================
stores = df_insights["store_name"].tolist()
store_selected = st.selectbox("Sélectionnez un magasin", stores)

if store_selected == "Lululemon Total":
    df_store_sentiment = df_sentiment
    df_store_topic = df_topic
else:
    df_store_sentiment = df_sentiment[df_sentiment["store_name"] == store_selected]
    df_store_topic = df_topic[df_topic["store_name"] == store_selected]

# ======================================
# KPIs
# ======================================
st.subheader("KPIs")
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("Total reviews", len(df_store_sentiment))
pos_ratio = round((df_store_sentiment["sentiment_label"]=="POSITIVE").mean()*100, 2)
neg_ratio = round((df_store_sentiment["sentiment_label"]=="NEGATIVE").mean()*100, 2)
kpi2.metric("Positive ratio (%)", pos_ratio)
kpi3.metric("Negative ratio (%)", neg_ratio)

# ======================================
# Graphique des sentiments
# ======================================
st.subheader("Distribution des sentiments")
sentiment_counts = df_store_sentiment["sentiment_label"].value_counts()
st.bar_chart(sentiment_counts)

# ======================================
# Graphique des topics
# ======================================
st.subheader("Top topics")
topic_counts = df_store_topic["topic_label"].value_counts().head(10)
st.bar_chart(topic_counts)

# ======================================
# Aperçu des avis
# ======================================
st.subheader("Exemples d'avis")
st.dataframe(df_store_sentiment[["text", "sentiment_label", "rating"]].head(10))
