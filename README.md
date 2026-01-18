# Lululemon AI-driven Business Insights

[![Built with real public APIs](https://img.shields.io/badge/API-Public-blue)](https://huggingface.co)

## Overview

This project demonstrates an end-to-end **AI-powered business insights pipeline** applied to **Lululemon textual data**. It is designed for **data analysts and business managers** to extract actionable insights from business communications and brand-related texts.  

The pipeline uses:
- **Hugging Face models** for sentiment analysis, topic classification, and summarization.
- **GitHub Actions** for automation and reproducibility.
- **Streamlit** for interactive visualization.

> This project is a portfolio showcase demonstrating **real-world AI usage** in a business context.

---

## Features

1. **Text Ingestion**  
   - Simulated real business texts from investor communications, press releases, and brand statements.  
   - Stored in `data/raw/texts.csv`.

2. **Sentiment Analysis**  
   - Using `distilbert-base-uncased-finetuned-sst-2-english` from Hugging Face.  
   - Adds `sentiment_label` (POSITIVE/NEGATIVE) and `sentiment_score`.

3. **Zero-Shot Topic Classification**  
   - Using `facebook/bart-large-mnli`.  
   - Detects business-relevant themes such as `sustainability`, `pricing`, `customer service`, etc.

4. **Business Insights Generation**  
   - Aggregates sentiment and topics to produce **KPIs per theme**.  
   - Outputs `business_insights.csv` with counts and percentages.

5. **Interactive Visualization with Streamlit**  
   - Shows KPIs, sentiment distributions per theme, texts with topics, and an automatic summary.

---

## Repository Structure

