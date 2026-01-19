import streamlit as st
import pandas as pd
from pathlib import Path

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
    return (
        pd.read_csv(SENTIMENT_PATH),
        pd.read_csv(TOPIC_PATH),
        pd.read_csv(INSIGHTS_PATH),
    )

try:
    sentiment_df, topics_df, insights_df = load_data()
except FileNotFoundError:
    st.error("Processed CSV files not found.")
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
# Network metrics
# -----------------------------
network_positive_rate = (sentiment_df["sentiment"] == "POSITIVE").mean()
network_review_count = len(sentiment_df)

# =============================
# NETWORK VIEW
# =============================
if selected_store == "All Stores (Network View)":

    st.header("🌍 Network Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", network_review_count)
    col2.metric("Positive Sentiment Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.divider()

    st.subheader("📊 Main Topics Across All Stores")

    topic_dist = (
        topics_df.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
    )

    st.bar_chart(topic_dist.set_index("topic"), use_container_width=True)

    st.divider()

    st.subheader("🧩 Key Business Insights")
    st.dataframe(insights_df, use_container_width=True)

# =============================
# STORE VIEW
# =============================
else:
    st.header(f"🏬 Store Analysis — {selected_store}")

    store_df = sentiment_df[sentiment_df["store_name"] == selected_store]
    store_topics_df = topics_df[topics_df["store_name"] == selected_store]

    store_positive_rate = (store_df["sentiment"] == "POSITIVE").mean()
    delta_vs_network = store_positive_rate - network_positive_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Store Reviews", len(store_df))
    col2.metric("Positive Sentiment", f"{store_positive_rate*100:.1f}%")
    col3.metric(
        "Delta vs Network",
        f"{delta_vs_network*100:+.1f}%",
        delta=f"{delta_vs_network*100:+.1f}%"
    )

    st.divider()

    # -----------------------------
    # Topic distribution
    # -----------------------------
    st.subheader("🗂️ Topic Distribution — Store")

    store_topic_dist = (
        store_topics_df.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
    )

    st.bar_chart(store_topic_dist.set_index("topic"), use_container_width=True)

    st.divider()

    # -----------------------------
    # Strengths / Weaknesses
    # -----------------------------
    st.subheader("💪 Strengths & ⚠️ Weaknesses")

    network_topics = topics_df.groupby("topic").size()
    store_topics = store_topics_df.groupby("topic").size()

    comparison = (
        pd.concat([store_topics, network_topics], axis=1)
        .fillna(0)
        .rename(columns={0: "store_mentions", 1: "network_mentions"})
    )

    comparison["lift_vs_network"] = (
        comparison["store_mentions"] /
        comparison["network_mentions"].replace(0, 1)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💪 Strengths")
        st.dataframe(
            comparison.sort_values("lift_vs_network", ascending=False).head(3),
            use_container_width=True
        )

    with col2:
        st.markdown("### ⚠️ Weaknesses")
        st.dataframe(
            comparison.sort_values("lift_vs_network").head(3),
            use_container_width=True
        )

    st.divider()

    # -----------------------------
    # Actionable Insight Rate
    # -----------------------------
    st.subheader("🎯 Actionable Insight Rate")

    actionable_keywords = [
        "staff",
        "service",
        "return",
        "checkout",
        "price",
        "fitting"
    ]

    def is_actionable(topic):
        topic_lower = topic.lower()
        return any(k in topic_lower for k in actionable_keywords)

    store_actionable_rate = (
        store_topics_df["topic"].apply(is_actionable).mean()
    )

    network_actionable_rate = (
        topics_df["topic"].apply(is_actionable).mean()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Store Actionable %",
        f"{store_actionable_rate*100:.1f}%"
    )

    col2.metric(
        "Network Actionable %",
        f"{network_actionable_rate*100:.1f}%"
    )

    col3.metric(
        "Gap",
        f"{(store_actionable_rate - network_actionable_rate)*100:+.1f}%"
    )

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "📌 Google Maps reviews • Weekly automated analysis • "
    "GitHub Actions + Streamlit Cloud"
)
