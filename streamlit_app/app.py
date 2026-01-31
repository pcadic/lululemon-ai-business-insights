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
# Helper function for topic sentiment chart
# -----------------------------
def topic_sentiment_chart(df_topics, df_sentiment, store_name=None):
    if store_name and store_name != "All Stores":
        df = df_topics[df_topics["store_name"] == store_name].copy()
    else:
        df = df_topics.copy()
    
    # Calcul des scores positifs et négatifs par topic
    grouped = df.groupby("topic")["sentiment_score"].apply(list).reset_index()
    
    fig = go.Figure()
    
    for _, row in grouped.iterrows():
        topic = row["topic"]
        scores = row["sentiment_score"]
        neg_scores = [s for s in scores if s < 0]
        pos_scores = [s for s in scores if s > 0]

        # Somme des scores négatifs pour barre gauche
        fig.add_trace(go.Bar(
            y=[topic],
            x=[sum(neg_scores)],
            orientation='h',
            name='Negative',
            marker_color='tomato',
            hovertemplate=f"Topic: {topic}<br>Negative Sum: %{x}<extra></extra>"
        ))
        
        # Somme des scores positifs pour barre droite
        fig.add_trace(go.Bar(
            y=[topic],
            x=[sum(pos_scores)],
            orientation='h',
            name='Positive',
            marker_color='mediumseagreen',
            hovertemplate=f"Topic: {topic}<br>Positive Sum: %{x}<extra></extra>"
        ))

    fig.update_layout(
        barmode='relative',
        title="Topic Sentiment Diverging Chart",
        xaxis_title="Cumulative Sentiment Score (-ve left, +ve right)",
        yaxis_title="Topics",
        yaxis={'autorange':'reversed'},
        height=500 + 30*len(grouped),
        bargap=0.15,
        legend=dict(orientation='h', x=0, y=1.1)
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
    fig = topic_sentiment_chart(topics_df, sentiment_df)
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
    fig = topic_sentiment_chart(store_topics_df, store_df, store_name=selected_store)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.caption(
    "📌 Data collected weekly via Google Maps • "
    "Analysis automated with GitHub Actions • "
    "Dashboard hosted on Streamlit Cloud"
)
