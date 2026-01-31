import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Page config
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
# Helper: Diverging bar chart
# -----------------------------
def plot_diverging_topic_sentiment(topics_df, sentiment_df, title):
    # Join via store_name (niveau magasin)
    merged = topics_df.merge(
        sentiment_df[["store_name", "sentiment"]],
        on="store_name",
        how="left"
    )

    topic_sentiment = (
        merged
        .groupby(["topic", "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    topic_sentiment["NEGATIVE"] = -topic_sentiment.get("NEGATIVE", 0)
    topic_sentiment["POSITIVE"] = topic_sentiment.get("POSITIVE", 0)

    max_value = max(
        topic_sentiment["POSITIVE"].max(),
        abs(topic_sentiment["NEGATIVE"].min())
    )

    fig = go.Figure()

    fig.add_bar(
        y=topic_sentiment["topic"],
        x=topic_sentiment["NEGATIVE"],
        orientation="h",
        name="Negative reviews",
        marker_color="tomato"
    )

    fig.add_bar(
        y=topic_sentiment["topic"],
        x=topic_sentiment["POSITIVE"],
        orientation="h",
        name="Positive reviews",
        marker_color="mediumseagreen"
    )

    fig.update_layout(
        title=title,
        barmode="relative",
        xaxis=dict(
            title="Number of reviews",
            range=[-max_value, max_value],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black"
        ),
        yaxis=dict(title="Topic"),
        legend=dict(orientation="h", y=-0.25),
        height=500,
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

    st.subheader("📊 Topic Sentiment Balance — Network")
    fig = plot_diverging_topic_sentiment(
        topics_df,
        sentiment_df,
        title="Positive vs Negative Reviews by Topic (Network)"
    )
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

    st.subheader("🗂️ Topic Sentiment Balance — Store")
    fig = plot_diverging_topic_sentiment(
        store_topics_df,
        store_df,
        title=f"Positive vs Negative Reviews by Topic — {selected_store}"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.caption(
    "📌 Data collected weekly via Google Maps • "
    "Analysis automated with GitHub Actions • "
    "Dashboard hosted on Streamlit"
)
