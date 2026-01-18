# Lululemon Customer Reviews – AI Business Insights

## 📌 Project Overview

This project delivers **real, business-oriented insights from Google Maps customer reviews** for selected **Lululemon stores**, using a **fully cloud-based data pipeline**.

The goal is to demonstrate how a Data Analyst can:

* Collect real-world, external data
* Apply NLP techniques to extract value
* Automate analysis workflows
* Present insights clearly to non-technical stakeholders

➡️ **No local execution required.**
➡️ **Everything runs in the cloud.**

---

## 🧠 What This Project Shows (Recruiter-Focused)

✔ Real external data (Google Maps reviews)
✔ Automated weekly pipeline (GitHub Actions)
✔ NLP-powered sentiment & topic analysis
✔ Store-level and global insights
✔ Interactive dashboard (Streamlit Cloud)
✔ Clean separation between data processing and visualization

This is a **business project**, not a toy or academic exercise.

---

## 🏗️ Architecture (High-Level)

```
Google Maps Reviews
        ↓
GitHub Actions (Weekly)
        ↓
Python NLP Pipeline
        ↓
Processed CSV files
        ↓
Streamlit Cloud Dashboard
```

* **Heavy computation** happens offline (GitHub Actions)
* **Dashboard** only reads precomputed data
* Result: fast, clean, recruiter-friendly UX

---

## 📂 Repository Structure

```
.
├── app.py                  # Streamlit dashboard
├── src/                     # Data pipeline scripts
│   ├── fetch_reviews.py     # Google Maps Text Search + Reviews
│   ├── sentiment_analysis.py
│   ├── topic_classification.py
│   └── business_insights.py
│
├── data/
│   ├── raw/                 # Raw reviews (CSV)
│   └── processed/           # Enriched analysis outputs
│
├── .github/workflows/
│   └── pipeline.yml         # Automated GitHub Actions workflow
│
├── requirements.txt
└── README.md
```

---

## 🔁 Automated Pipeline (GitHub Actions)

* Runs **manually or weekly**
* Fetches **real Google Maps reviews** using Text Search
* Applies NLP models from **Hugging Face**
* Generates updated CSV files
* Commits updated outputs to the repository

📌 **No manual intervention required.**

---

## 🧪 NLP & Analysis

### Sentiment Analysis

* Positive / Neutral / Negative classification
* Aggregated by store and globally

### Topic Classification

* Key customer themes (e.g. product quality, staff, pricing)
* Automatically inferred using transformer models

### Business Insights

* Executive-level summaries
* Comparison across locations
* Actionable signals for decision-makers

---

## 📊 Dashboard (Streamlit Cloud)

The Streamlit app is designed for **non-technical users**:

* Global overview across all stores
* Store-by-store comparison
* Interactive filters
* Drill-down to individual customer reviews

⚡ Loads instantly (no live API calls)

---

## 🔐 API Key Management

* Google Maps API key is stored securely as a **GitHub Secret**
* Never hard-coded
* Safe for public repositories

---

## 🆓 Cost & Limits

* Google Maps API free tier respected
* Limited number of stores & reviews per run
* Designed to stay within free quotas

---

## 🎯 Why This Project Matters

This project demonstrates:

* End-to-end data ownership
* Real-world data challenges
* Cloud automation
* Business-first analytics mindset

It mirrors how **modern data teams actually work**.

---

## 🚀 Future Improvements

* Add time-series trend analysis
* Expand to competitor brands
* Add keyword-based alerting
* Store clustering by customer sentiment

---

## 👤 Author

**Philip**
Aspiring Data Analyst | Python | SQL | NLP | Business Analytics

📍 Vancouver, Canada

---

*This project is intentionally designed to be simple to review, fast to load, and focused on business impact.*
