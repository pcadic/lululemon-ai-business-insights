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
# Helper: diverging topic chart
# -----------------------------
def plot_diverging_topic_chart(df, title):
    topic_sentiment = (
        df.groupby(["topic", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for col in ["POSITIVE", "NEGATIVE"]:
        if col not in topic_sentiment.columns:
            topic_sentiment[col] = 0

    topic_sentiment["NEGATIVE"] = -topic_sentiment["NEGATIVE"]

    fig = go.Figure()

    fig.add_bar(
        y=topic_sentiment["topic"],
        x=topic_sentiment["NEGATIVE"],
        orientation="h",
        name="Negative reviews",
        marker_color="#ef4444",
    )

    fig.add_bar(
        y=topic_sentiment["topic"],
        x=topic_sentiment["POSITIVE"],
        orientation="h",
        name="Positive reviews",
        marker_color="#22c55e",
    )

    fig.update_layout(
        title=title,
        barmode="relative",
        xaxis_title="Number of reviews",
        yaxis_title="Topic",
        xaxis=dict(
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
        ),
        legend=dict(orientation="h", y=-0.2),
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Network View
# -----------------------------
if selected_store == "All Stores":
    st.header("🌍 Network Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", network_review_count)
    col2.metric("Positive Sentiment Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.subheader("📊 Topic Sentiment Across Network")
    plot_diverging_topic_chart(topics_df, "Network Topic Sentiment")

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

    st.subheader("🗂️ Topic Sentiment — Store")
    plot_diverging_topic_chart(store_topics_df, f"Topic Sentiment — {selected_store}")

st.caption(
    "📌 Data collected weekly via Google Maps • Analysis automated with GitHub Actions • Dashboard hosted on Streamlit Cloud"
)
