import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Configuration Streamlit
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("🧠 Lululemon AI Business Insights")
st.caption("Analyse des sentiments & thématiques via Google Maps (Données agrégées)")

# -----------------------------
# Constantes / Chemins (Paths)
# -----------------------------
DATA_DIR = Path("data/processed")
SENTIMENT_PATH = DATA_DIR / "sentiment_enriched.csv"
TOPIC_PATH = DATA_DIR / "topic_enriched.csv"
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

# -----------------------------
# Chargement des données (CORRIGÉ)
# -----------------------------
@st.cache_data
def load_data():
    # On charge les fichiers CSV
    sentiment = pd.read_csv(SENTIMENT_PATH)
    topics = pd.read_csv(TOPIC_PATH)
    insights = pd.read_csv(INSIGHTS_PATH)
    
    # Nettoyage rapide des colonnes au cas où
    for df in [sentiment, topics, insights]:
        df.columns = [c.strip() for c in df.columns]
        
    return sentiment, topics, insights

try:
    sentiment_df, topics_df, insights_df = load_data()
except FileNotFoundError:
    st.error(f"Fichiers CSV introuvables dans {DATA_DIR}. Vérifiez les chemins.")
    st.stop()

# -----------------------------
# Logique de calcul Global (KPIs Réseau)
# -----------------------------
# IMPORTANT : On utilise .sum() sur la colonne 'count'
network_total_reviews = sentiment_df["count"].sum()
network_pos_reviews = sentiment_df[sentiment_df["sentiment"] == "POSITIVE"]["count"].sum()
network_positive_rate = network_pos_reviews / network_total_reviews if network_total_reviews > 0 else 0

# -----------------------------
# Fonction de graphique divergent (CORRIGÉE)
# -----------------------------
def topic_sentiment_chart(df, store_name=None):
    working_df = df.copy()
    
    if store_name and store_name != "All Stores":
        working_df = working_df[working_df['store_name'] == store_name]
    
    # Pivot en faisant la SOMME de 'count'
    pivot = working_df.pivot_table(
        index='topic',
        columns='sentiment',
        values='count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Sécurité si une colonne de sentiment manque
    if 'NEGATIVE' not in pivot.columns: pivot['NEGATIVE'] = 0
    if 'POSITIVE' not in pivot.columns: pivot['POSITIVE'] = 0
    
    # Pour le graphique divergent : les négatifs partent vers la gauche (valeurs négatives)
    pivot['NEG_VAL'] = -pivot['NEGATIVE']
    
    # Tri par volume total pour la lisibilité
    pivot['total_vol'] = pivot['POSITIVE'] + pivot['NEGATIVE']
    pivot = pivot.sort_values('total_vol', ascending=True)
    
    fig = go.Figure()
    
    # Barre Négative
    fig.add_trace(go.Bar(
        y=pivot['topic'],
        x=pivot['NEG_VAL'],
        name='Négatif',
        orientation='h',
        marker_color='#EF553B',
        customdata=pivot['NEGATIVE'],
        hovertemplate="Topic: %{y}<br>Négatifs: %{customdata}<extra></extra>"
    ))
    
    # Barre Positive
    fig.add_trace(go.Bar(
        y=pivot['topic'],
        x=pivot['POSITIVE'],
        name='Positif',
        orientation='h',
        marker_color='#00CC96',
        hovertemplate="Topic: %{y}<br>Positifs: %{x}<extra></extra>"
    ))
    
    fig.update_layout(
        barmode='relative',
        xaxis=dict(title="Volume d'avis (Somme)", zeroline=True, zerolinewidth=2),
        yaxis=dict(title="Sujets évoqués"),
        height=400 + (25 * len(pivot)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(sentiment_df["store_name"].unique())
selected_store = st.sidebar.selectbox("Select store", ["All Stores"] + stores)

# -----------------------------
# Affichage : Vue Réseau ou Magasin
# -----------------------------
if selected_store == "All Stores":
    st.header("🌍 Network Overview")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews (Sum)", int(network_total_reviews))
    col2.metric("Positive Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.subheader("📊 Topics Across Network")
    st.plotly_chart(topic_sentiment_chart(topics_df), use_container_width=True)

    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df, use_container_width=True)

else:
    st.header(f"🏬 Store Analysis — {selected_store}")
    
    # Filtrage
    store_sent_df = sentiment_df[sentiment_df["store_name"] == selected_store]
    
    # KPIs magasin corrigés
    store_total = store_sent_df["count"].sum()
    store_pos = store_sent_df[store_sent_df["sentiment"] == "POSITIVE"]["count"].sum()
    store_rate = store_pos / store_total if store_total > 0 else 0
    delta = store_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Reviews", int(store_total))
    col2.metric("Positive Sentiment", f"{store_rate*100:.1f}%")
    col3.metric("Delta vs Network", f"{delta*100:+.1f}%")

    st.subheader("🗂️ Topic Distribution")
    st.plotly_chart(topic_sentiment_chart(topics_df, store_name=selected_store), use_container_width=True)

    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df[insights_df['store_name'] == selected_store], use_container_width=True)

st.divider()
st.caption("📌 Analyse basée sur les fréquences agrégées (colonne 'count').")
