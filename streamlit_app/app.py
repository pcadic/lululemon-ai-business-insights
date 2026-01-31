import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("🧠 Lululemon AI Business Insights")

DATA_DIR = Path("data/processed")
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(INSIGHTS_PATH)
    df.columns = df.columns.str.strip()
    # Conversion forcée en numérique pour la colonne count
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df_insights = load_data()
except Exception as e:
    st.error(f"Erreur de lecture : {e}")
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_insights["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

# Filtrage strict
if selected_store == "Tous les magasins":
    display_df = df_insights.copy()
else:
    display_df = df_insights[df_insights["store_name"] == selected_store].copy()

# -----------------------------
# Calculs et Graphe
# -----------------------------
st.subheader(f"📊 Analyse détaillée : {selected_store}")

# ÉTAPE CRUCIALE : On regroupe par Topic ET Sentiment en additionnant 'count'
# Cela empêche l'écrasement des données pour Robson ou West Van
chart_data = display_df.groupby(['topic', 'sentiment'], as_index=False)['count'].sum()

# Création du graphique Stacked Bar
fig = px.bar(
    chart_data,
    x='count',
    y='topic',
    color='sentiment',
    orientation='h',
    barmode='stack', # Empile les segments (ex: 2 pos + 1 neg = barre de 3)
    color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
    text='count',    # Affiche le chiffre à l'intérieur de la barre
    labels={'count': "Nombre d'avis", 'topic': "Catégorie", 'sentiment': "Sentiment"}
)

# Réglages de l'affichage
fig.update_layout(
    xaxis=dict(tickformat='d', dtick=1), # Axe en nombres entiers uniquement
    yaxis={'categoryorder':'total ascending'},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    uniformtext_minsize=8, 
    uniformtext_mode='hide'
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Table de Contrôle (Pour Robson, vous verrez bien vos 3 lignes ici)
# -----------------------------
with st.expander("🔍 Vérifier le tableau de données source"):
    st.write(f"Données utilisées pour {selected_store} :")
    st.dataframe(chart_data)
