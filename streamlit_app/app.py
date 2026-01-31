import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Configuration Streamlit
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("🧠 Lululemon AI Business Insights")

# -----------------------------
# Chemins (Paths)
# -----------------------------
DATA_DIR = Path("data/processed")
SENTIMENT_PATH = DATA_DIR / "sentiment_enriched.csv"
TOPIC_PATH = DATA_DIR / "topic_enriched.csv"
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

# -----------------------------
# Chargement des données
# -----------------------------
@st.cache_data
def load_data():
    # Chargement des fichiers bruts
    sentiment = pd.read_csv(SENTIMENT_PATH)
    topics = pd.read_csv(TOPIC_PATH)
    # Note: insights_df semble avoir une structure différente, on le charge classiquement
    insights = pd.read_csv(INSIGHTS_PATH)
    
    # Nettoyage des noms de colonnes
    sentiment.columns = sentiment.columns.str.strip()
    topics.columns = topics.columns.str.strip()
    insights.columns = insights.columns.str.strip()
    
    return sentiment, topics, insights

try:
    sentiment_df, topics_df, insights_df = load_data()
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

# -----------------------------
# Calcul des KPIs Réseau (Basé sur le nombre de lignes)
# -----------------------------
network_review_count = len(sentiment_df)
network_positive_count = len(sentiment_df[sentiment_df["sentiment"] == "POSITIVE"])
network_positive_rate = network_positive_count / network_review_count if network_review_count > 0 else 0

# -----------------------------
# Fonction Graphique Divergent (CORRIGÉE)
# -----------------------------
def topic_sentiment_chart(df, store_name=None):
    working_df = df.copy()
    
    if store_name and store_name != "All Stores":
        working_df = working_df[working_df['store_name'] == store_name]
    
    # On utilise 'size' car ici 1 ligne = 1 avis
    pivot = working_df.pivot_table(
        index='topic',
        columns='sentiment',
        aggfunc='size',
        fill_value=0
    ).reset_index()
    
    # Sécurité colonnes
    if 'NEGATIVE' not in pivot.columns: pivot['NEGATIVE'] = 0
    if 'POSITIVE' not in pivot.columns: pivot['POSITIVE'] = 0
    
    # Valeur négative pour l'axe de gauche
    pivot['NEG_PLOT'] = -pivot['NEGATIVE']
    
    # Tri pour le visuel
    pivot = pivot.sort_values(by='POSITIVE', ascending=True)
    
    fig = go.Figure()
    
    # Négatifs (Gauche)
    fig.add_trace(go.Bar(
        y=pivot['topic'], x=pivot['NEG_PLOT'],
        name='Négatif', orientation='h', marker_color='#EF553B',
        customdata=pivot['NEGATIVE'],
        hovertemplate="Négatifs: %{customdata}"
    ))
    
    # Positifs (Droite)
    fig.add_trace(go.Bar(
        y=pivot['topic'], x=pivot['POSITIVE'],
        name='Positif', orientation='h', marker_color='#00CC96',
        hovertemplate="Positifs: %{x}"
    ))
    
    fig.update_layout(
        barmode='relative',
        xaxis=dict(title="Nombre d'avis", zeroline=True, zerolinewidth=2),
        yaxis=dict(title=""),
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    return fig

# -----------------------------
# Sidebar & Navigation
# -----------------------------
stores = sorted(sentiment_df["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["All Stores"] + stores)

if selected_store == "All Stores":
    st.header("🌍 Vue Globale du Réseau")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Avis", network_review_count)
    col2.metric("Taux Positif", f"{network_positive_rate*100:.1f}%")
    col3.metric("Magasins", len(stores))

    st.subheader("📊 Sentiments par Thématique (Réseau)")
    st.plotly_chart(topic_sentiment_chart(topics_df), use_container_width=True)
    
    st.subheader("🧩 Business Insights")
    st.dataframe(insights_df, use_container_width=True)

else:
    st.header(f"🏬 Analyse : {selected_store}")
    
    store_df = sentiment_df[sentiment_df["store_name"] == selected_store]
    store_review_count = len(store_df)
    store_pos_count = len(store_df[store_df["sentiment"] == "POSITIVE"])
    store_rate = store_pos_count / store_review_count if store_review_count > 0 else 0
    delta = store_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Avis Magasin", store_review_count)
    col2.metric("Taux Positif", f"{store_rate*100:.1f}%")
    col3.metric("vs Réseau", f"{delta*100:+.1f}%")

    st.subheader("🗂️ Répartition Thématique")
    st.plotly_chart(topic_sentiment_chart(topics_df, selected_store), use_container_width=True)

    st.subheader("🧩 Insights Spécifiques")
    # Filtrage des insights si la colonne existe dans business_insights.csv
    if 'store_name' in insights_df.columns:
        st.dataframe(insights_df[insights_df['store_name'] == selected_store], use_container_width=True)
    else:
        st.dataframe(insights_df, use_container_width=True)
