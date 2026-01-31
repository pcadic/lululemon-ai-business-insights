import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
st.set_page_config(page_title="Lululemon AI Insights", layout="wide")

# -----------------------------
# Chargement des données (Source de vérité)
# -----------------------------
DATA_DIR = Path("data/processed")
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(INSIGHTS_PATH)
    df.columns = df.columns.str.strip()
    # On s'assure que count est un entier
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df

df_source = load_data()

# -----------------------------
# Sidebar - Le déclencheur du "Refresh"
# -----------------------------
st.sidebar.header("Filtres")
stores = sorted(df_source["store_name"].unique())
selected_store = st.sidebar.selectbox(
    "Choisir un magasin", 
    ["Tous les magasins"] + stores,
    key="store_selector" # Une clé unique force parfois Streamlit à mieux suivre l'état
)

# -----------------------------
# Logique de Filtrage (S'exécute à chaque changement)
# -----------------------------
if selected_store == "Tous les magasins":
    display_df = df_source.copy()
    cols_to_show = ["store_name", "topic", "sentiment", "count"]
    title_prefix = "Vue Globale"
else:
    # On filtre strictement sur le magasin
    display_df = df_source[df_source["store_name"] == selected_store].copy()
    # On enlève la colonne store_name comme demandé
    cols_to_show = ["topic", "sentiment", "count"]
    title_prefix = f"Analyse : {selected_store}"

# -----------------------------
# Affichage Principal
# -----------------------------
st.title(f"🧠 {title_prefix}")

if not display_df.empty:
    # 1. Graphique
    st.subheader("📊 Graphique des Sentiments")
    
    # On agrège par topic/sentiment pour le graphe pour éviter les doublons visuels
    chart_data = display_df.groupby(['topic', 'sentiment'], as_index=False)['count'].mean()
    
    fig = px.bar(
        chart_data,
        x='count',
        y='topic',
        color='sentiment',
        orientation='h',
        barmode='stack',
        color_discrete_map={'POSITIVE': '#00CC96', 'NEGATIVE': '#EF553B'},
        text='count',
        labels={'count': "Nombre d'avis", 'topic': "Thématique"}
    )

    fig.update_layout(
        xaxis=dict(tickformat='d', dtick=1),
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 2. Tableau (Strictement identique au graphe)
    st.subheader("📋 Tableau de données")
    # hide_index=True enlève la colonne 0,1,2...
    st.dataframe(
        display_df[cols_to_show], 
        use_container_width=True, 
        hide_index=True
    )

    # 3. Métriques
    st.divider()
    c1, c2 = st.columns(2)
    total_count = display_df['count'].sum()
    pos_count = display_df[display_df['sentiment'] == 'POSITIVE']['count'].sum()
    
    c1.metric("Total Avis", total_count)
    c2.metric("Satisfaction", f"{(pos_count/total_count*100):.1f}%" if total_count > 0 else "0%")
    
else:
    st.error("Aucune donnée trouvée pour cette sélection.")
