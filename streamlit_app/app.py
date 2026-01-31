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
    # Chargement direct du fichier source
    df = pd.read_csv(INSIGHTS_PATH)
    df.columns = df.columns.str.strip()
    # Force le type entier pour la colonne count
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

df_source = load_data()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_source["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

# -----------------------------
# Filtrage de la donnée source
# -----------------------------
if selected_store == "Tous les magasins":
    # On garde tout, y compris le nom du magasin
    display_df = df_source.copy()
    chart_title = "Analyse Globale - Tous les magasins"
else:
    # On filtre sur le magasin sélectionné
    display_df = df_source[df_source["store_name"] == selected_store].copy()
    chart_title = f"Analyse Spécifique - {selected_store}"

# -----------------------------
# GRAPHIQUE (Source directe du DataFrame)
# -----------------------------
st.subheader(f"📊 {chart_title}")

if not display_df.empty:
    # On crée le graphique à partir du display_df SANS agrégation supplémentaire
    # pour être sûr que Robson ou West Van affichent exactement leurs lignes.
    fig = px.bar(
        display_df,
        x='count',
        y='topic',
        color='sentiment',
        orientation='h',
        barmode='stack',
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
        text='count',
        hover_data=['store_name'] if selected_store == "Tous les magasins" else None,
        labels={'count': "Nombre d'avis", 'topic': "Sujet", 'sentiment': "Sentiment"}
    )

    fig.update_layout(
        xaxis=dict(tickformat='d', dtick=1), # Axe en nombres entiers
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée trouvée.")

# -----------------------------
# DATAFRAME (Le miroir du graphe)
# -----------------------------
st.subheader("📋 Récapitulatif des données")

# hide_index=True supprime la première colonne de numéros (index)
st.dataframe(display_df, use_container_width=True, hide_index=True)

# -----------------------------
# KPIs Rapides
# -----------------------------
st.divider()
total_avis = display_df["count"].sum()
pos_avis = display_df[display_df["sentiment"] == "POSITIVE"]["count"].sum()
taux = (pos_avis / total_avis * 100) if total_avis > 0 else 0

c1, c2 = st.columns(2)
c1.metric("Total Avis cumulés", int(total_avis))
c2.metric("Taux de Satisfaction", f"{taux:.1f}%")
