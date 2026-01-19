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
st.caption("Retail intelligence from Google Maps reviews – automated & business-ready")

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
    st.error("Processed CSV files not found in the repository.")
    st.stop()

# -----------------------------
# Actionable logic
# -----------------------------
ACTIONABLE_KEYWORDS = [
    "staff",
    "service",
    "return",
    "checkout",
    "price",
    "fitting"
]

def is_actionable(topic: str) -> bool:
    topic = str(topic).lower()
    return any(k in topic for k in ACTIONABLE_KEYWORDS)

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
network_actionable_rate = topics_df["topic"].apply(is_actionable).mean()

# =====================================================
# NETWORK VIEW
# =====================================================
if selected_store == "All Stores (Network View)":

    st.header("🌍 Network Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(sentiment_df))
    col2.metric("Positive Sentiment Rate", f"{network_positive_rate*100:.1f}%")
    col3.metric("Stores Covered", len(stores))

    st.divider()

    # -----------------------------
    # Network Store Scores
    # -----------------------------
    st.subheader("🏬 Store Performance Scores")

    scores = []

    for store in stores:
        s_df = sentiment_df[sentiment_df["store_name"] == store]
        t_df = topics_df[topics_df["store_name"] == store]

        pos_rate = (s_df["sentiment"] == "POSITIVE").mean()
        neg_rate = (s_df["sentiment"] == "NEGATIVE").mean()
        actionable_rate = t_df["topic"].apply(is_actionable).mean()

        score = (
            pos_rate * 60 +
            actionable_rate * 40 -
            neg_rate * 20
        )

        score = max(0, min(100, round(score * 100)))

        scores.append({
            "store_name": store,
            "score": score,
            "positive_rate": pos_rate,
            "actionable_rate": actionable_rate
        })

    score_df = pd.DataFrame(scores).sort_values("score", ascending=False)

    st.dataframe(score_df, use_container_width=True)

    st.divider()

    # -----------------------------
    # Underperforming Stores
    # -----------------------------
    st.subheader("🚨 Underperforming Stores")

    alerts = score_df[
        (score_df["positive_rate"] < network_positive_rate) |
        (score_df["actionable_rate"] < network_actionable_rate) |
        (score_df["score"] < 60)
    ]

    if alerts.empty:
        st.success("No underperforming stores detected.")
    else:
        st.dataframe(alerts, use_container_width=True)

    st.divider()

    # -----------------------------
    # Network topics
    # -----------------------------
    st.subheader("📊 Main Topics Across Network")

    topic_dist = (
        topics_df.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
    )

    st.bar_chart(topic_dist.set_index("topic"), use_container_width=True)

# =====================================================
# STORE VIEW
# =====================================================
else:
    st.header(f"🏬 Store Analysis — {selected_store}")

    store_df = sentiment_df[sentiment_df["store_name"] == selected_store]
    store_topics_df = topics_df[topics_df["store_name"] == selected_store]

    pos_rate = (store_df["sentiment"] == "POSITIVE").mean()
    neg_rate = (store_df["sentiment"] == "NEGATIVE").mean()
    actionable_rate = store_topics_df["topic"].apply(is_actionable).mean()

    score = (
        pos_rate * 60 +
        actionable_rate * 40 -
        neg_rate * 20
    )
    score = max(0, min(100, round(score * 100)))

    delta_vs_network = pos_rate - network_positive_rate

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Reviews", len(store_df))
    col2.metric("Positive Sentiment", f"{pos_rate*100:.1f}%")
    col3.metric("Delta vs Network", f"{delta_vs_network*100:+.1f}%")
    col4.metric("Store Score", score)

    st.divider()

    # -----------------------------
    # Topic distribution
    # -----------------------------
    st.subheader("🗂️ Topic Distribution")

    topic_dist = (
        store_topics_df.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
    )

    st.bar_chart(topic_dist.set_index("topic"), use_container_width=True)

    st.divider()

    # -----------------------------
    # Top Irritants (negative + actionable)
    # -----------------------------
    st.subheader("⚠️ Top Customer Irritants")

    negative_reviews = store_df[store_df["sentiment"] == "NEGATIVE"]

    negative_topics = store_topics_df[
        store_topics_df["topic"].apply(is_actionable)
    ]

    irritants = (
        negative_topics.groupby("topic")
        .size()
        .reset_index(name="mentions")
        .sort_values("mentions", ascending=False)
        .head(3)
    )

    if irritants.empty:
        st.success("No major customer irritants detected.")
    else:
        st.dataframe(irritants, use_container_width=True)

    st.divider()

    # -----------------------------
    # Actionable Insight KPI
    # -----------------------------
    st.subheader("🎯 Actionable Insight Rate")

    col1, col2, col3 = st.columns(3)

    col1.metric("Store Actionable %", f"{actionable_rate*100:.1f}%")
    col2.metric("Network Actionable %", f"{network_actionable_rate*100:.1f}%")
    col3.metric(
        "Gap",
        f"{(actionable_rate - network_actionable_rate)*100:+.1f}%"
    )

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "📌 Weekly Google Maps data • Hugging Face NLP • "
    "Automated with GitHub Actions • Streamlit Cloud"
)
