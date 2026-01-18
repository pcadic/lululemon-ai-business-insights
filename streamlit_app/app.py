import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Customer Reviews Business Insights",
    layout="wide"
)

# =========================
# DATA LOADING
# =========================

@st.cache_data
def load_data():
    sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
    topics = pd.read_csv("data/processed/topic_enriched.csv")
    insights = pd.read_csv("data/processed/business_insights.csv")
    return sentiment, topics, insights


sentiment_df, topic_df, insights_df = load_data()

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Filters")

store_list = sorted(topic_df["place_name"].unique())
selected_store = st.sidebar.selectbox(
    "Select a store",
    ["ALL_STORES"] + store_list
)

# =========================
# HEADER
# =========================

st.title("📊 Customer Reviews Analysis")
st.markdown(
    """
    This dashboard analyzes **real Google Maps customer reviews**
    using **NLP and AI models**, aggregated automatically via a cloud pipeline.
    """
)

# =========================
# GLOBAL VIEW
# =========================

st.header("Executive Overview")

if selected_store == "ALL_STORES":
    global_df = insights_df[insights_df["level"] == "GLOBAL"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Overall Sentiment Distribution")
        sentiment_cols = [c for c in global_df.columns if c not in ["topic", "place_name", "level"]]
        st.bar_chart(global_df.set_index("topic")[sentiment_cols])

    with col2:
        st.subheader("Top Topics (All Stores)")
        topic_counts = topic_df["topic"].value_counts()
        st.bar_chart(topic_counts)

# =========================
# STORE VIEW
# =========================

else:
    st.header(f"Store Analysis – {selected_store}")

    store_insights = insights_df[
        (insights_df["place_name"] == selected_store) &
        (insights_df["level"] == "STORE")
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sentiment by Topic")
        sentiment_cols = [c for c in store_insights.columns if c not in ["topic", "place_name", "level"]]
        st.bar_chart(store_insights.set_index("topic")[sentiment_cols])

    with col2:
        st.subheader("Topic Distribution")
        topic_counts = topic_df[topic_df["place_name"] == selected_store]["topic"].value_counts()
        st.bar_chart(topic_counts)

# =========================
# DRILL DOWN
# =========================

st.header("Detailed Reviews")

filtered_reviews = topic_df.copy()

if selected_store != "ALL_STORES":
    filtered_reviews = filtered_reviews[
        filtered_reviews["place_name"] == selected_store
    ]

st.dataframe(
    filtered_reviews[["place_name", "rating", "sentiment", "topic", "text"]],
    use_container_width=True,
    height=400
)

# =========================
# FOOTER
# =========================

st.markdown("---")
st.caption(
    "Data pipeline runs automatically via GitHub Actions. "
    "Dashboard displays precomputed insights for fast recruiter review."
)
