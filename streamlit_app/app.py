import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Config
st.set_page_config(page_title="Google Maps Sentiment Analysis", layout="wide")

# Chargement sécurisé
DATA_PATH = Path("data/processed/business_insights.csv")

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return None
    return pd.read_csv(DATA_PATH)

df = load_data()

if df is None:
    st.error("Fichier de données introuvable. Veuillez lancer le pipeline d'analyse d'abord.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("📊 Filtres")
stores = sorted(df["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

# --- HEADER ---
st.title("🏬 Analyse des avis Google Maps")
st.markdown(f"Analyse IA des thématiques et sentiments pour **{selected_store}**")

# --- LOGIQUE D'AFFICHAGE ---

if selected_store == "Tous les magasins":
    # --- VUE GLOBALE ---
    col1, col2, col3 = st.columns(3)
    total_reviews = df["count"].sum()
    pos_rate = (df[df["sentiment"] == "POSITIVE"]["count"].sum() / total_reviews) * 100
    
    col1.metric("Total Avis", total_reviews)
    col2.metric("% Positif", f"{pos_rate:.1f}%")
    col3.metric("Magasins analysés", len(stores))

    st.subheader("Comparaison des performances par magasin")
    fig_global = px.bar(
        df, x="store_name", y="count", color="sentiment",
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#CC0036', 'NEUTRAL': '#ff7b00'},
        barmode="group"
    )
    st.plotly_chart(fig_global, use_container_width=True)

else:
    # --- VUE PAR MAGASIN ---
    store_df = df[df["store_name"] == selected_store]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Récapitulatif")
        st.dataframe(store_df.pivot_table(index="topic", columns="sentiment", values="count", fill_value=0))

    with col2:
        st.subheader("Sentiments par thématique")
        fig_store = px.bar(
            store_df, y="topic", x="count", color="sentiment",
            orientation='h',
            color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#CC0036', 'NEUTRAL': '#ff7b00'},
            category_orders={"sentiment": ["NEGATIVE", "POSITIVE", "NEUTRAL"]}
        )
        st.plotly_chart(fig_store, use_container_width=True)

st.divider()
st.caption("Projet réalisé avec Hugging Face (BART & BERT) et Streamlit.")
