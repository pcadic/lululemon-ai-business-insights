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
    # On s'assure que count est un entier
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

df_insights = load_data()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_insights["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

# -----------------------------
# Préparation des données (La source du graphe et du tableau)
# -----------------------------
if selected_store == "Tous les magasins":
    # On groupe par Topic/Sentiment pour agréger tout le réseau 
    # et on enlève la colonne store_name pour la clarté
    display_df = df_insights.groupby(['topic', 'sentiment'], as_index=False)['count'].sum()
else:
    # On filtre sur le magasin et on garde les colonnes pertinentes
    display_df = df_insights[df_insights["store_name"] == selected_store][['topic', 'sentiment', 'count']]

# -----------------------------
# Graphique : Reflet exact du DataFrame
# -----------------------------
st.subheader(f"📊 Analyse : {selected_store}")



fig = px.bar(
    display_df,
    x='count',
    y='topic',
    color='sentiment',
    orientation='h',
    barmode='stack',
    color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
    text='count', # Affiche le chiffre exact du tableau
    labels={'count': "Nombre d'avis", 'topic': "Catégorie"}
)

fig.update_layout(
    xaxis=dict(tickformat='d', dtick=1), # Uniquement des entiers
    yaxis={'categoryorder':'total ascending'},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Affichage du DataFrame (La source)
# -----------------------------
st.subheader("📋 Données sources (Synthèse)")
st.dataframe(display_df, use_container_width=True)

# -----------------------------
# KPIs
# -----------------------------
st.divider()
total_v = display_df["count"].sum()
pos_v = display_df[display_df["sentiment"] == "POSITIVE"]["count"].sum()
sat_rate = (pos_v / total_v * 100) if total_v > 0 else 0

c1, c2 = st.columns(2)
c1.metric("Total Avis", int(total_v))
c2.metric("Satisfaction Globale", f"{sat_rate:.1f}%")
