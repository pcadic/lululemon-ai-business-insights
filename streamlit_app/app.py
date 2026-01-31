import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Lululemon AI Insights", layout="wide")
st.title("🧠 Lululemon AI Business Insights")
st.caption("Retail sentiment & topic analysis powered by Google Maps reviews")

# -----------------------------
# Paths
# -----------------------------
DATA_DIR = Path("data/processed")
SENTIMENT_PATH = DATA_DIR / "sentiment_enriched.csv"
TOPIC_PATH = DATA_DIR / "topic_enriched.csv"
INSIGHTS_PATH = DATA_DIR / "business_insights.csv"

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    sentiment = pd.read_csv(SENTIMENT_PATH)
    topics = pd.read_csv(TOPIC_PATH)
    insights = pd.read_csv(INSIGHTS_PATH)
    return sentiment, topics, insights

try:
    sentiment_df, topics_df, insights_df = load_data()
except FileNotFoundError:
    st.error("Processed CSV files not found.")
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
stores = sorted(sentiment_df["store_name"].unique())
selected_store = st.sidebar.selectbox("Select store", ["All Stores"] + stores)

# -----------------------------
# Network metrics
# -----------------------------
network_positive_rate = (sentiment_df["sentiment"] == "POSITIVE").mean()
network_review_count = len(sentiment_df)

# -----------------------------
# Helper: Diverging Topic Sentiment Chart
# -----------------------------
def topic_sentiment_diverging(df, height=500):
    """
    Crée un graphique horizontal divergeant : 
    avis négatifs à gauche, positifs à droite
    """
    # On compte les avis positifs et négatifs par topic
    counts = df.groupby(['topic', 'sentiment']).size().unstack(fill_value=0)
    
    # S'assurer que les colonnes existent
    counts['NEGATIVE'] = -counts.get('NEGATIVE', 0)  # Négatif à gauche
    counts['POSITIVE'] = counts.get('POSITIVE', 0)

    counts = counts.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=counts['topic'],
        x=counts['NEGATIVE'],
        orientation='h',
        name='Negative',
        marker_color='tomato',
        hovertemplate="Topic: %{y}<br>Negative Reviews: %{customdata}<extra></extra>",
        customdata=-counts['NEGATIVE']  # valeur positive pour le hover
    ))

    fig.add_trace(go.Bar(
        y=counts['topic'],
        x=counts['POSITIVE'],
        orientation='h',
        name='Positive',
        marker_color='mediumseagreen',
        hovertemplate="Topic: %{y}<br>Positive Reviews: %{x}<extra></extra>"
    ))

    fig.update_layout(
        barmode='relative',
        height=height,
        yaxis_autorange='reversed',  # topics du plus important en haut
        xaxis=dict(title="Number of Reviews", zeroline=True),
        bargap=0.05,
        legend_orientation='h',
        legend_x=-0.05,
        legend_y=1.1,
        title="Topic Sentiment Diverging Chart"
    )

    return fig

# -----------------------------
# Network View
# -----------------------------
if selected_store == "All Stores":
    st.header("🌍 Network Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", network_review_count)
    col2.metric("Positive Sentiment Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.subheader("📊 Topic Sentiment — Network")
    fig = topic_sentiment_diverging(topics_df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df, use_container_width=True)

# -----------------------------
# Store View
# -----------------------------
else:
    st.header(f"🏬 Store Analysis — {selected_store}")

    store_topics_df = topics_df[topics_df["store_name"] == selected_store]
    store_sentiment_df = sentiment_df[sentiment_df["store_name"] == selected_store]

    store_positive_rate = (store_sentiment_df["sentiment"] == "POSITIVE").mean()
    delta_vs_network = store_positive_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Reviews", len(store_sentiment_df))
    col2.metric("Positive Sentiment", f"{store_positive_rate*100:.1f}%")
    col3.metric("Delta vs Network", f"{delta_vs_network*100:+.1f}%")

    st.subheader("📊 Topic Sentiment — Store")
    fig = topic_sentiment_diverging(store_topics_df)
    st.plotly_chart(fig, use_container_width=True)

st.caption("📌 Data collected weekly via Google Maps • Analysis automated with GitHub Actions • Dashboard hosted on Streamlit Cloud")
