import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Streamlit config
# -----------------------------
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
# Diverging topic chart function
# -----------------------------
def topic_sentiment_chart(topics_df, store_name=None):
    """
    Crée un graphique divergente des topics selon les sentiments.
    store_name=None → réseau entier
    store_name=nom du magasin → store spécifique
    """
    df = topics_df.copy()
    
    if store_name and store_name != "All Stores":
        df = df[df['store_name'] == store_name]
    
    pivot = df.pivot_table(index='topic',
                           columns='sentiment',
                           aggfunc='size',
                           fill_value=0)
    
    if 'NEGATIVE' in pivot.columns:
        pivot['NEGATIVE'] = -pivot['NEGATIVE']  # négatif à gauche
    else:
        pivot['NEGATIVE'] = 0
    if 'POSITIVE' not in pivot.columns:
        pivot['POSITIVE'] = 0
    
    pivot = pivot.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=pivot['topic'],
        x=-pivot['NEGATIVE'],
        name='Negative',
        orientation='h',
        marker_color='tomato',
        customdata=-pivot['NEGATIVE'],
        hovertemplate="Topic: %{y}<br>Negative Reviews: %{customdata}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=pivot['topic'],
        x=pivot['POSITIVE'],
        name='Positive',
        orientation='h',
        marker_color='mediumseagreen',
        customdata=pivot['POSITIVE'],
        hovertemplate="Topic: %{y}<br>Positive Reviews: %{customdata}<extra></extra>"
    ))
    
    fig.update_layout(
        barmode='relative',
        xaxis=dict(title="Number of Reviews", zeroline=True),
        yaxis_autorange='reversed',
        height=400 + 30*len(pivot),
        title=f"Topic Sentiment — {'Store: '+store_name if store_name and store_name != 'All Stores' else 'Network'}"
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

    st.subheader("📊 Topics Across Network")
    fig = topic_sentiment_chart(topics_df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df, use_container_width=True)

# -----------------------------
# Store View
# -----------------------------
else:
    st.header(f"🏬 Store Analysis — {selected_store}")
    store_df = sentiment_df[sentiment_df["store_name"] == selected_store]
    store_topics_df = topics_df[topics_df["store_name"] == selected_store]
    store_positive_rate = (store_df["sentiment"] == "POSITIVE").mean()
    delta_vs_network = store_positive_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Reviews", len(store_df))
    col2.metric("Positive Sentiment", f"{store_positive_rate*100:.1f}%")
    col3.metric("Delta vs Network", f"{delta_vs_network*100:+.1f}%")

    st.subheader("🗂️ Topic Distribution — Store")
    fig = topic_sentiment_chart(topics_df, store_name=selected_store)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧩 Key Business Insights — Store")
    st.dataframe(insights_df, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.caption(
    "📌 Data collected weekly via Google Maps • "
    "Analysis automated with GitHub Actions • Dashboard hosted on Streamlit Cloud"
)
