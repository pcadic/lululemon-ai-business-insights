import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")

# Chemins des fichiers
DATA_DIR = Path("data/processed")
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(INSIGHTS_PATH)
    df.columns = df.columns.str.strip()
    # On garantit que 'count' est un entier pur
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
    # On garde toutes les colonnes pour la vue globale
    cols_to_show = ["store_name", "topic", "sentiment", "count"]
else:
    # On filtre sur le magasin choisi
    display_df = df_source[df_source["store_name"] == selected_store].copy()
    # On enlève 'store_name' du tableau final car il est en titre
    cols_to_show = ["topic", "sentiment", "count"]

# -----------------------------
# Préparation des données du graphique (L'étape clé)
# -----------------------------
# On regroupe pour être certain que POSITIF et NÉGATIF ne s'annulent pas
# et s'affichent bien comme des blocs distincts sur la même barre.
chart_data = display_df.groupby(['topic', 'sentiment'], as_index=False)['count'].sum()

# -----------------------------
# Affichage
# -----------------------------
st.title(f"📊 {selected_store}")

# Bloc de vérification (Debug)
with st.expander("🔍 Vérification : Données envoyées au graphique", expanded=True):
    st.write("Le graphique ci-dessous utilise EXCLUSIVEMENT ces données :")
    st.dataframe(chart_data, hide_index=True, use_container_width=True)

if not chart_data.empty:
    # Création du graphique en barres empilées
    fig = px.bar(
        chart_data,
        x='count',
        y='topic',
        color='sentiment',
        orientation='h',
        barmode='stack', # Empile les segments au lieu de les soustraire
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
        text='count',    # Affiche le chiffre exact à l'intérieur du segment
        labels={'count': "Nombre d'avis", 'topic': "Thématiques", 'sentiment': "Sentiment"}
    )

    # Réglages de l'axe et de la légende
    fig.update_layout(
        xaxis=dict(
            tickformat='d', # Force les nombres entiers (pas de 0.5, 1.0...)
            dtick=1         # Une graduation pour chaque unité
        ),
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

# Tableau récapitulatif final
st.subheader("📋 Tableau récapitulatif détaillé")
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
