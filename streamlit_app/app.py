import streamlit as st
import pandas as pd
import plotly.express as px
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
# Network View
# -----------------------------
if selected_store == "All Stores":
    st.header("🌍 Network Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", network_review_count)
    col2.metric("Positive Sentiment Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.subheader("📊 Topics Across Network")
    topic_dist = topics_df.groupby("topic").size().reset_index(name="mentions")
    fig = px.bar(topic_dist.sort_values("mentions", ascending=False),
                 x="topic", y="mentions", text="mentions")
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
    store_topic_dist = store_topics_df.groupby("topic").size().reset_index(name="mentions")
    fig = px.bar(store_topic_dist.sort_values("mentions", ascending=False),
                 x="topic", y="mentions", text="mentions")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🎯 Actionable Insight Rate")
    actionable_topics = ["staff","service","returns","checkout","pricing","fitting_room"]
    store_actionable_rate = store_topics_df[store_topics_df["topic"].isin(actionable_topics)].shape[0] / max(len(store_topics_df),1)
    network_actionable_rate = topics_df[topics_df["topic"].isin(actionable_topics)].shape[0] / max(len(topics_df),1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Actionable %", f"{store_actionable_rate*100:.1f}%")
    col2.metric("Network Actionable %", f"{network_actionable_rate*100:.1f}%")
    col3.metric("Gap", f"{(store_actionable_rate-network_actionable_rate)*100:+.1f}%")

st.caption("📌 Data collected weekly via Google Maps • Analysis automated with GitHub Actions • Dashboard hosted on Streamlit Cloud")
