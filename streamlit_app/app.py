import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(
    page_title="Lululemon AI Business Insights",
    layout="wide"
)

st.title("🧠 Lululemon AI Business Insights")
st.caption("Retail sentiment & topic analysis powered by Google Maps reviews")

# -----------------------------
# Paths (CSV committed in repo)
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
    st.error("Processed CSV files not found. Please check the repository.")
    st.stop()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("🔍 View Options")
stores = sorted(sentiment_df["store_name"].unique())
selected_store = st.sidebar.selectbox(
    "Select a store",
    ["All Stores (Network View)"] + stores
)

# -----------------------------
# Network-level metrics
# -----------------------------
network_positive_rate = (sentiment_df["sentiment"] == "POSITIVE").mean()
network_review_count = len(sentiment_df)

# -----------------------------
# NETWORK VIEW
# -----------------------------
if selected_store == "All Stores (Network View)":

    st.header("🌍 Network Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", f"{network_review_count}")
    col2.metric("Positive Sentiment Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.divider()

    # Network topic distribution (Plotly)
    st.subheader("📊 Main Topics Across All Stores")
    topic_dist = (
        topics_df.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
    )
    fig = px.bar(topic_dist, x="topic", y="mentions", title="Network Topic Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Business insights (network)
    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df, use_container_width=True)

# -----------------------------
# STORE VIEW
# -----------------------------
else:
    st.header(f"🏬 Store Analysis — {selected_store}")

    store_df = sentiment_df[sentiment_df["store_name"] == selected_store]
    store_topics_df = topics_df[topics_df["store_name"] == selected_store]
    store_positive_rate = (store_df["sentiment"] == "POSITIVE").mean()

    # Store KPIs
    st.subheader("📈 Store Performance")
    delta_vs_network = store_positive_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Reviews", len(store_df))
    col2.metric("Positive Sentiment", f"{store_positive_rate*100:.1f}%")
    col3.metric("Delta vs Network", f"{delta_vs_network*100:+.1f}%", delta=f"{delta_vs_network*100:+.1f}%")

    st.divider()

    # Topic distribution (store) — Plotly
    st.subheader("🗂️ Topic Distribution — Store")
    store_topic_dist = (
        store_topics_df.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
    )
    fig = px.bar(store_topic_dist, x="topic", y="mentions", title=f"Topics for {selected_store}")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Strengths & Weaknesses
    st.subheader("💪 Strengths & ⚠️ Weaknesses")
    network_topics = topics_df.groupby("topic").size().rename("network_mentions")
    store_topics = store_topics_df.groupby("topic").size().rename("store_mentions")
    comparison = pd.concat([store_topics, network_topics], axis=1).fillna(0)
    comparison["lift_vs_network"] = comparison["store_mentions"] / comparison["network_mentions"].replace(0, 1)
    strengths = comparison.sort_values("lift_vs_network", ascending=False).head(3).reset_index()
    weaknesses = comparison.sort_values("lift_vs_network", ascending=True).head(3).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Strengths")
        st.dataframe(strengths, use_container_width=True)
    with col2:
        st.markdown("### ⚠️ Weaknesses")
        st.dataframe(weaknesses, use_container_width=True)

    st.divider()

    # Actionable Insights KPI
    st.subheader("🎯 Actionable Insight Rate")
    actionable_topics = ["staff","service","returns","checkout","pricing","fitting_room"]

    network_actionable_reviews = topics_df[topics_df["topic"].isin(actionable_topics)]
    network_actionable_rate = network_actionable_reviews.shape[0] / topics_df.shape[0]

    store_actionable_reviews = store_topics_df[topics_df["topic"].isin(actionable_topics)]
    store_actionable_rate = store_actionable_reviews.shape[0] / store_topics_df.shape[0] if store_topics_df.shape[0] > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Actionable %", f"{store_actionable_rate*100:.1f}%")
    col2.metric("Network Actionable %", f"{network_actionable_rate*100:.1f}%")
    col3.metric("Gap", f"{(store_actionable_rate-network_actionable_rate)*100:+.1f}%")

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "📌 Data collected weekly via Google Maps • "
    "Analysis automated with GitHub Actions • "
    "Dashboard hosted on Streamlit"
)

# -----------------------------
