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
    # On s'assure que count est un nombre
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0)
    return df

df_insights = load_data()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(df_insights["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

# Filtrage par magasin
if selected_store == "Tous les magasins":
    display_df = df_insights
else:
    display_df = df_insights[df_insights["store_name"] == selected_store]

# -----------------------------
# Agrégation Spécifique (Somme par Topic et Sentiment)
# -----------------------------
# Cette étape garantit que POSITIF et NEGATIF restent des entités distinctes
chart_data = display_df.groupby(['topic', 'sentiment'])['count'].sum().reset_index()

# -----------------------------
# Graphique Empilé (Stacked)
# -----------------------------
st.subheader(f"📊 Volume d'activité par sujet : {selected_store}")



fig = px.bar(
    chart_data,
    x='count',
    y='topic',
    color='sentiment',
    orientation='h',
    # barmode='stack' empêche l'annulation : ils s'empilent !
    barmode='stack', 
    color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
    text_auto='.0f', # Affiche les nombres entiers sur les segments
    labels={'count': "Nombre total d'avis", 'topic': "Sujets analysés"}
)

fig.update_layout(
    xaxis=dict(tickformat='d', dtick=1), # Axe en nombres entiers (1, 2, 3...)
    yaxis={'categoryorder':'total ascending'},
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Table de vérification
# -----------------------------
with st.expander("🔍 Vérification des calculs (Sommes par sentiment)"):
    st.write("Voici comment les données sont additionnées pour le graphique :")
    st.dataframe(chart_data)
