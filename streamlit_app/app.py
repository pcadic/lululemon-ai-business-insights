import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# 1. CONFIGURATION ET STYLE
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")

# CSS pour épurer l'affichage si besoin
st.markdown("""
    <style>
    .main { padding-top: 0rem; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# 2. CHARGEMENT DES DONNÉES
# -----------------------------
DATA_DIR = Path("data/processed")
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

@st.cache_data
def load_data():
    # Chargement du fichier que tu as validé
    df = pd.read_csv(INSIGHTS_PATH)
    # Nettoyage des noms de colonnes (espaces invisibles)
    df.columns = df.columns.str.strip()
    # Conversion forcée en entier pour la colonne count
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df_source = load_data()
except Exception as e:
    st.error(f"Erreur de lecture du fichier CSV : {e}")
    st.stop()

# -----------------------------
# 3. BARRE LATÉRALE (FILTRES)
# -----------------------------
st.sidebar.header("Navigation")
stores = sorted(df_source["store_name"].unique())
selected_store = st.sidebar.selectbox(
    "Choisir un magasin", 
    ["Tous les magasins"] + stores,
    key="store_selector"
)

# -----------------------------
# 4. LOGIQUE DE FILTRAGE
# -----------------------------
if selected_store == "Tous les magasins":
    # Vue globale : on garde tout
    display_df = df_source.copy()
    cols_to_show = ["store_name", "topic", "sentiment", "count"]
    chart_title = "Analyse Globale du Réseau"
else:
    # Vue spécifique : on filtre et on prépare les colonnes
    display_df = df_source[df_source["store_name"] == selected_store].copy()
    cols_to_show = ["topic", "sentiment", "count"]
    chart_title = f"Analyse : {selected_store}"

# -----------------------------
# 5. PRÉPARATION DU GRAPHIQUE (CHART_DATA)
# -----------------------------
# On crée chart_data pour être l'entrée exacte du graphique
chart_data = display_df.groupby(['topic', 'sentiment'], as_index=False)['count'].sum()

# -----------------------------
# 6. AFFICHAGE PRINCIPAL
# -----------------------------
st.title(f"🧠 {chart_title}")

# SECTION DEBUG : Pour vérifier que le code reçoit bien les bons chiffres
with st.expander("🔍 Voir les données injectées dans le graphique (chart_data)", expanded=True):
    st.write("Le graphique ci-dessous est construit strictement avec ces données :")
    st.dataframe(chart_data, hide_index=True, use_container_width=True)

# SECTION GRAPHIQUE
if not chart_data.empty:
    # Création du bar chart empilé
    fig = px.bar(
        chart_data,
        x='count',
        y='topic',
        color='sentiment',
        orientation='h',
        barmode='stack',
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
        text='count',  # Affiche le chiffre sur la barre
        labels={'count': "Nombre d'avis", 'topic': "Thématiques", 'sentiment': "Sentiment"},
        hover_data={'topic': True, 'count': True, 'sentiment': True}
    )

    # Forcer l'axe X en nombres entiers (0, 1, 2...)
    fig.update_layout(
        xaxis=dict(tickformat='d', dtick=1),
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée disponible pour cette sélection.")

# SECTION TABLEAU RÉCAPITULATIF
st.subheader("📋 Récapitulatif détaillé")
# Affiche display_df avec les colonnes choisies, sans l'index
st.dataframe(
    display_df[cols_to_show], 
    use_container_width=True, 
    hide_index=True
)

# SECTION KPIs
st.divider()
c1, c2, c3 = st.columns(3)
total_reviews = display_df['count'].sum()
pos_reviews = display_df[display_df['sentiment'] == 'POSITIVE']['count'].sum()
sat_rate = (pos_reviews / total_reviews * 100) if total_reviews > 0 else 0

c1.metric("Total Avis", total_reviews)
c2.metric("Taux Satisfaction", f"{sat_rate:.1f}%")
c3.metric("Nb de Lignes", len(display_df))
