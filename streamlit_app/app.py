# app.py
import streamlit as st
import pandas as pd

# -----------------------------
# Titre de l'app
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("Lululemon AI Business Insights Dashboard")

# -----------------------------
# Charger les CSV
# -----------------------------
@st.cache_data
def load_data():
    try:
        sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
        topics = pd.read_csv("data/processed/topic_enriched.csv")
        insights = pd.read_csv("data/processed/business_insights.csv")
        return sentiment, topics, insights
    except Exception as e:
        st.error(f"Erreur lors du chargement des CSV : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

sentiment_df, topics_df, insights_df = load_data()

# -----------------------------
# Sélection du magasin
# -----------------------------
stores = sentiment_df["store_name"].unique() if not sentiment_df.empty else []
selected_store = st.selectbox("Sélectionner un magasin", options=stores)

if selected_store:
    st.subheader(f"Analyses pour {selected_store}")

    # -----------------------------
    # Sentiment
    # -----------------------------
    store_sentiment = sentiment_df[sentiment_df["store_name"] == selected_store]
    if not store_sentiment.empty:
        st.write("### Sentiment des avis")
        st.bar_chart(store_sentiment["sentiment_score"])
    else:
        st.info("Pas de données de sentiment pour ce magasin.")

    # -----------------------------
    # Topics
    # -----------------------------
    store_topics = topics_df[topics_df["store_name"] == selected_store]
    if not store_topics.empty:
        st.write("### Topics identifiés")
        st.dataframe(store_topics[["topic", "score"]])
    else:
        st.info("Pas de topics disponibles pour ce magasin.")

    # -----------------------------
    # Business Insights
    # -----------------------------
    store_insights = insights_df[insights_df["store_name"] == selected_store]
    if not store_insights.empty:
        st.write("### Insights Business")
        st.dataframe(store_insights)
    else:
        st.info("Pas d'insights disponibles pour ce magasin.")
else:
    st.info("Aucun magasin disponible dans les données.")
