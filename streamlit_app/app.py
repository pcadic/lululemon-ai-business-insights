import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("🧠 Lululemon AI Business Insights")
st.caption("Analyse des sentiments et thématiques basée sur les avis Google Maps")

# -----------------------------
# Chargement des données
# -----------------------------
@st.cache_data
def load_data():
    # J'utilise test.csv comme source unique ici selon votre exemple
    df = pd.read_csv("test.csv")
    # S'assurer que les noms de colonnes sont propres
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df_main = load_data()
except FileNotFoundError:
    st.error("Le fichier test.csv est introuvable.")
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_main["store_name"].unique())
selected_store = st.sidebar.selectbox("Sélectionner un magasin", ["Tous les magasins"] + stores)

# Filtrage des données
if selected_store == "Tous les magasins":
    df_filtered = df_main.copy()
else:
    df_filtered = df_main[df_main["store_name"] == selected_store]

# -----------------------------
# Calcul des KPIs (CORRIGÉ)
# -----------------------------
# On utilise la somme de la colonne 'count' et non le nombre de lignes
total_reviews = df_filtered["count"].sum()
positive_reviews = df_filtered[df_filtered["sentiment"] == "POSITIVE"]["count"].sum()
negative_reviews = df_filtered[df_filtered["sentiment"] == "NEGATIVE"]["count"].sum()

# Taux de sentiment positif global (pour le benchmark)
network_total = df_main["count"].sum()
network_positive = df_main[df_main["sentiment"] == "POSITIVE"]["count"].sum()
network_rate = network_positive / network_total if network_total > 0 else 0

current_rate = positive_reviews / total_reviews if total_reviews > 0 else 0
delta = current_rate - network_rate

# -----------------------------
# Fonction de graphique divergent (CORRIGÉE)
# -----------------------------
def topic_sentiment_chart(df):
    # Pivot en faisant la SOMME de la colonne 'count'
    pivot = df.pivot_table(
        index='topic',
        columns='sentiment',
        values='count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # S'assurer que les colonnes existent pour éviter les erreurs
    if 'NEGATIVE' not in pivot.columns: pivot['NEGATIVE'] = 0
    if 'POSITIVE' not in pivot.columns: pivot['POSITIVE'] = 0

    # Inversion des valeurs négatives pour l'affichage à gauche
    pivot['NEGATIVE_PLOT'] = -pivot['NEGATIVE']

    # Tri par volume total pour un meilleur rendu
    pivot['total'] = pivot['POSITIVE'] + pivot['NEGATIVE']
    pivot = pivot.sort_values('total', ascending=True)

    fig = go.Figure()
    
    # Barre Négative (Rouge)
    fig.add_trace(go.Bar(
        y=pivot['topic'],
        x=pivot['NEGATIVE_PLOT'],
        name='Négatif',
        orientation='h',
        marker_color='#EF553B',
        customdata=pivot['NEGATIVE'],
        hovertemplate="Sujet: %{y}<br>Avis négatifs: %{customdata}<extra></extra>"
    ))
    
    # Barre Positive (Vert)
    fig.add_trace(go.Bar(
        y=pivot['topic'],
        x=pivot['POSITIVE'],
        name='Positif',
        orientation='h',
        marker_color='#00CC96',
        hovertemplate="Sujet: %{y}<br>Avis positifs: %{x}<extra></extra>"
    ))

    fig.update_layout(
        barmode='relative',
        xaxis=dict(title="Nombre d'avis", zeroline=True, zerolinewidth=2, zerolinecolor='Black'),
        yaxis=dict(title="Thématiques"),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# -----------------------------
# Affichage
# -----------------------------
st.header(f"📊 Analyse : {selected_store}")

col1, col2, col3 = st.columns(3)
col1.metric("Total Avis", int(total_reviews))
col2.metric("Taux Positif", f"{current_rate*100:.1f}%")
col3.metric("Delta vs Réseau", f"{delta*100:+.1f}%")

st.subheader("🗂️ Répartition des sentiments par thématique")
if total_reviews > 0:
    fig = topic_sentiment_chart(df_filtered)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée disponible pour ce filtre.")

# Pied de page
st.divider()
st.caption("Données corrigées : prise en compte des volumes (colonne 'count').")
