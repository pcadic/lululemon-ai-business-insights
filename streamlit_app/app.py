import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")

DATA_DIR = Path("data/processed")
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(INSIGHTS_PATH)
    df.columns = df.columns.str.strip()
    # On s'assure que count est bien un entier
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

df_source = load_data()

# -----------------------------
# Sidebar & Filtrage
# -----------------------------
stores = sorted(df_source["store_name"].unique())
selected_store = st.sidebar.selectbox("Choisir un magasin", ["Tous les magasins"] + stores)

if selected_store == "Tous les magasins":
    display_df = df_source.copy()
    cols_to_show = ["store_name", "topic", "sentiment", "count"]
else:
    display_df = df_source[df_source["store_name"] == selected_store].copy()
    cols_to_show = ["topic", "sentiment", "count"]

# -----------------------------
# Préparation des données (L'étape de vérité)
# -----------------------------
# On agrège pour être certain de ce qu'on envoie au graphe
chart_data = display_df.groupby(['topic', 'sentiment'], as_index=False)['count'].sum()

# -----------------------------
# Affichage
# -----------------------------
st.title(f"📊 {selected_store}")

# Affichage du DataFrame de contrôle (ce que le graphe DOIT afficher)
st.subheader("🛠️ Données d'entrée du graphique (Vérification)")
st.dataframe(chart_data, hide_index=True, use_container_width=True)

if not chart_data.empty:
    # Création du graphique
    # On utilise 'topic' pour l'axe Y et 'sentiment' pour la séparation des couleurs
    fig = px.bar(
        chart_data,
        x='count',
        y='topic',
        color='sentiment',
        orientation='h',
        barmode='stack', # Empile POSITIVE et NEGATIVE sur la même ligne de topic
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
        text='count',
        category_orders={"sentiment": ["NEGATIVE", "POSITIVE"]}, # Garde le rouge à gauche, vert à droite
        labels={'count': "Nombre d'avis", 'topic': "Thématique"}
    )

    # Sécurité sur les axes
    fig.update_layout(
        xaxis=dict(tickformat='d', dtick=1), # Forcer les entiers
        yaxis=dict(type='category', categoryorder='total ascending'), # Force le mode texte pour éviter les bugs d'échelle
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# Tableau final épuré
st.subheader("📋 Récapitulatif complet")
st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)

# -----------------------------
# Métriques (KPIs)
# -----------------------------
st.divider()
total_v = display_df["count"].sum()
pos_v = display_df[display_df["sentiment"] == "POSITIVE"]["count"].sum()
taux = (pos_v / total_v * 100) if total_v > 0 else 0

c1, c2 = st.columns(2)
c1.metric("Total Avis cumulés", int(total_v))
c2.metric("Taux de Satisfaction", f"{taux:.1f}%")
