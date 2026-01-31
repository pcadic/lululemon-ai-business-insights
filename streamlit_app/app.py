import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("🧠 Lululemon AI Business Insights")

# Utilisation des chemins originaux
DATA_DIR = Path("data/processed")
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

@st.cache_data
def load_data():
    # On se base uniquement sur le fichier que vous avez validé
    df = pd.read_csv(INSIGHTS_PATH)
    df.columns = df.columns.str.strip()
    # On s'assure que count est bien un nombre entier
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df_insights = load_data()
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_insights["store_name"].unique())
selected_store = st.sidebar.selectbox("Sélectionner un magasin", ["Tous les magasins"] + stores)

if selected_store == "Tous les magasins":
    display_df = df_insights
else:
    display_df = df_insights[df_insights["store_name"] == selected_store]

# -----------------------------
# KPIs
# -----------------------------
total_v = display_df["count"].sum()
pos_v = display_df[display_df["sentiment"] == "POSITIVE"]["count"].sum()
sat_rate = (pos_v / total_v * 100) if total_v > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total Avis", int(total_v))
c2.metric("Taux Satisfaction", f"{sat_rate:.1f}%")
c3.metric("Nb Thématiques", len(display_df['topic'].unique()))

# -----------------------------
# GRAPHIQUE : Stacked Bar (Empilé) avec Axe Entier
# -----------------------------
st.subheader(f"📊 Volume des avis par sujet : {selected_store}")

# Agrégation
chart_data = display_df.groupby(['topic', 'sentiment'])['count'].sum().reset_index()



fig = px.bar(
    chart_data,
    x='count',
    y='topic',
    color='sentiment',
    orientation='h',
    color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
    text_auto=True,
    labels={'count': "Nombre d'avis", 'topic': "Sujet", 'sentiment': "Sentiment"}
)

# CORRECTION DE L'AXE (Forcer les nombres entiers)
fig.update_layout(
    barmode='stack',
    xaxis=dict(
        tickformat='d',      # 'd' force le formatage en nombres entiers (Digit)
        dtick=1              # Force un cran tous les 1 avis
    ),
    yaxis={'categoryorder':'total ascending'},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLEAU DE DÉTAIL
# -----------------------------
st.subheader("📝 Détails des Insights")
# On affiche les colonnes utiles pour l'utilisateur
st.dataframe(display_df[['store_name', 'topic', 'sentiment', 'count']], use_container_width=True)
