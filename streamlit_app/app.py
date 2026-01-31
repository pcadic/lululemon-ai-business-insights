import streamlit as st
import pandas as pd
import plotly.express as px
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
# Helper: Diverging topic sentiment chart
# -----------------------------
def topic_sentiment_chart(topics, sentiment):
    merged = topics.merge(
        sentiment[["store_name", "text", "sentiment"]],
        on=["store_name", "text"],
        how="inner"
    )

    agg = (
        merged
        .groupby(["topic", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    if "NEGATIVE" not in agg:
        agg["NEGATIVE"] = 0
    if "POSITIVE" not in agg:
        agg["POSITIVE"] = 0

    agg["NEGATIVE"] = -agg["NEGATIVE"]

    fig = go.Figure()
    fig.add_bar(
        y=agg["topic"],
        x=agg["NEGATIVE"],
        orientation="h",
        name="Negative",
        marker_color="tomato"
    )
    fig.add_bar(
        y=agg["topic"],
        x=agg["POSITIVE"],
        orientation="h",
        name="Positive",
        marker_color="mediumseagreen"
    )

    fig.update_layout(
        barmode="relative",
        xaxis_title="Number of reviews",
        yaxis_title="Topics",
        xaxis=dict(zeroline=True, zerolinewidth=2),
        height=500
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
    fig = topic_sentiment_chart(topics_df, sentiment_df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df, use_container_width=True)

# -----------------------------
# Store View
# -----------------------------
else:
    st.header(f"🏬 Store Analysis — {selected_store}")

    store_sentiment = sentiment_df[sentiment_df["store_name"] == selected_store]
    store_topics = topics_df[topics_df["store_name"] == selected_store]

    store_positive_rate = (store_sentiment["sentiment"] == "POSITIVE").mean()
    delta_vs_network = store_positive_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Reviews", len(store_sentiment))
    col2.metric("Positive Sentiment", f"{store_positive_rate*100:.1f}%")
    col3.metric("Delta vs Network", f"{delta_vs_network*100:+.1f}%")

    st.subheader("🗂️ Topic Sentiment — Store")
    fig = topic_sentiment_chart(store_topics, store_sentiment)
    st.plotly_chart(fig, use_container_width=True)

st.caption(
    "📌 Data collected weekly via Google Maps • "
    "Analysis automated with GitHub Actions • "
    "Dashboard hosted on Streamlit Cloud"
)
