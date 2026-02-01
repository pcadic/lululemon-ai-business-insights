import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Config
st.set_page_config(page_title="Google Maps Sentiment Analysis", layout="wide")

# Définir l'ordre et les couleurs de manière globale
SENTIMENT_ORDER = ["NEGATIVE", "NEUTRAL", "POSITIVE"]
COLOR_MAP = {
    "NEGATIVE": "#EF553B", # Rouge
    "NEUTRAL": "#636EFA",  # Bleu/Gris
    "POSITIVE": "#00CC96"  # Vert
}

# Chargement sécurisé
DATA_PATH = Path("data/processed/business_insights.csv")

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return None
    return pd.read_csv(DATA_PATH)

df = load_data()

if df is None:
    st.error("Data file not found. Please run the analysis pipeline first.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("📊 Filtres")
stores = sorted(df["store_name"].unique())
selected_store = st.sidebar.selectbox("Select a store", ["All stores"] + stores)

# --- HEADER ---
st.title("🏬 Analysis of Google Maps reviews")
st.markdown(f"AI analysis of themes and sentiments for **{selected_store}**")

# --- LOGIQUE D'AFFICHAGE ---

if selected_store == "All stores":
    # --- VUE GLOBALE ---
    col1, col2, col3 = st.columns(3)
    total_reviews = df["count"].sum()
    pos_rate = (df[df["sentiment"] == "POSITIVE"]["count"].sum() / total_reviews) * 100
    
    col1.metric("Total Reviews", total_reviews)
    col2.metric("% Positive", f"{pos_rate:.1f}%")
    col3.metric("Stores analyzed Reviews", len(stores))

    st.subheader("Comparison of store performance")
    fig_global = px.bar(
            df, 
            x="store_name", 
            y="count", 
            color="sentiment",
            color_discrete_map=COLOR_MAP,
            category_orders={"sentiment": SENTIMENT_ORDER},
            barmode="group" # Les barres sont côte à côte par magasin
        )
    
    # --- AJOUT DES SÉPARATEURS ---
    fig_global.update_xaxes(
        showgrid=True, 
        gridwidth=2, 
        gridcolor='rgba(128, 128, 128, 0.2)', # Couleur grise légère
        ticks="outside", # Petit picot sous l'axe
        tickson="boundaries", # Force le picot ET la ligne ENTRE les catégories
        ticklen=10
    )
    
    fig_global.update_layout(
        xaxis_title="",
        legend_title="Sentiment",
        # Optionnel : alternance de couleur de fond (bandes)
        xaxis=dict(showspikes=True, spikethickness=1, spikedash='dot', spikecolor="#999999")
    )
    
    st.plotly_chart(fig_global, use_container_width=True)

else:
    # --- VUE PAR MAGASIN ---
    store_df = df[df["store_name"] == selected_store]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Summary")
        st.dataframe(store_df.pivot_table(index="topic", columns="sentiment", values="count", fill_value=0))

    with col2:
        st.subheader("Sentiments by themes")
        fig_store = px.bar(
            store_df, y="topic", x="count", color="sentiment",
            orientation='h',
            category_orders={"sentiment": SENTIMENT_ORDER}, 
            color_discrete_map=COLOR_MAP
        )
        st.plotly_chart(fig_store, use_container_width=True)

st.divider()
st.caption("Project completed with Hugging Face (BART & BERT) and Streamlit.")
