import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Lululemon – AI Business Insights")

sentiment = pd.read_csv("data/processed/sentiment_enriched.csv")
topics = pd.read_csv("data/processed/topic_enriched.csv")
insights = pd.read_csv("data/processed/business_insights.csv")

store = st.selectbox("Select Store", sentiment["store_name"].unique())

st.subheader("Sentiment Overview")
st.bar_chart(
    sentiment[sentiment["store_name"] == store]["sentiment"].value_counts()
)

st.subheader("Top Topics")
st.dataframe(
    topics[topics["store_name"] == store][["topic"]].value_counts().head(5)
)

st.subheader("Business Insights")
st.dataframe(insights[insights["store_name"] == store])
