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
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

df_source = load_data()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_source["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

# -----------------------------
# Préparation des données & colonnes à afficher
# -----------------------------
if selected_store == "Tous les magasins":
    display_df = df_source.copy()
    # On garde toutes les colonnes pour la vue globale
    cols_to_show = ["store_name", "topic", "sentiment", "count"]
    chart_title = "Analyse Globale - Tous les magasins"
else:
    # On filtre sur le magasin
    display_df = df_source[df_source["store_name"] == selected_store].copy()
    # On enlève 'store_name' car il est déjà dans le titre
    cols_to_show = ["topic", "sentiment", "count"]
    chart_title = f"Analyse : {selected_store}"

# -----------------------------
# GRAPHIQUE (Source directe)
# -----------------------------
st.subheader(f"📊 {chart_title}")

if not display_df.empty:
    fig = px.bar(
        display_df,
        x='count',
        y='topic',
        color='sentiment',
        orientation='h',
        barmode='stack',
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
        text='count',
        labels={'count': "Nombre d'avis", 'topic': "Sujet"}
    )

    fig.update_layout(
        xaxis=dict(tickformat='d', dtick=1),
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée disponible.")

# -----------------------------
# DATAFRAME (SANS INDEX et SANS STORE_NAME si filtré)
# -----------------------------
st.subheader("📋 Récapitulatif des données")

# Affichage avec les colonnes dynamiques
st.dataframe(
    display_df[cols_to_show], 
    use_container_width=True, 
    hide_index=True
)

# -----------------------------
# KPIs
# -----------------------------
st.divider()
total_v = display_df["count"].sum()
pos_v = display_df[display_df["sentiment"] == "POSITIVE"]["count"].sum()
taux = (pos_v / total_v * 100) if total_v > 0 else 0

c1, c2 = st.columns(2)
c1.metric("Total Avis", int(total_v))
c2.metric("Satisfaction", f"{taux:.1f}%")
