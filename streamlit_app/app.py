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

@st.cache_data
def load_data():
    # On se base sur le fichier validé
    df = pd.read_csv(DATA_DIR / "business_insights.csv")
    df.columns = df.columns.str.strip()
    return df

df_insights = load_data()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_insights["store_name"].unique())
selected_store = st.sidebar.selectbox("Sélectionner un magasin", ["Tous les magasins"] + stores)

# Filtrage
if selected_store == "Tous les magasins":
    display_df = df_insights
else:
    display_df = df_insights[df_insights["store_name"] == selected_store]

# -----------------------------
# KPIs (Calculés sur la colonne 'count' validée)
# -----------------------------
total_v = display_df["count"].sum()
pos_v = display_df[display_df["sentiment"] == "POSITIVE"]["count"].sum()
neg_v = display_df[display_df["sentiment"] == "NEGATIVE"]["count"].sum()
sat_rate = (pos_v / total_v * 100) if total_v > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total Avis", int(total_v))
c2.metric("Satisfaction", f"{sat_rate:.1f}%")
c3.metric("Volume Négatif", int(neg_v))

# -----------------------------
# GRAPHIQUE : Stacked Bar Chart (Empilé)
# -----------------------------
st.subheader(f"📊 Analyse des thématiques : {selected_store}")

# Agrégation par topic pour le graphique
chart_data = display_df.groupby(['topic', 'sentiment'])['count'].sum().reset_index()



fig = px.bar(
    chart_data,
    x='count',
    y='topic',
    color='sentiment',
    orientation='h',
    title="Volume d'avis par sujet et sentiment",
    color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
    text_auto=True # Affiche le chiffre exact sur la barre
)

fig.update_layout(
    barmode='stack',
    xaxis_title="Nombre d'avis",
    yaxis_title="",
    yaxis={'categoryorder':'total ascending'},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLEAU DE VÉRIFICATION
# -----------------------------
with st.expander("🔍 Voir les données sources (Fichier Insights)"):
    st.dataframe(display_df)

st.divider()
st.caption("✅ Source de données : business_insights.csv (Validé)")
