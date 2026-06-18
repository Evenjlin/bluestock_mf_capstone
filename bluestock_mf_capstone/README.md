# Bluestock Fintech — Mutual Fund Analytics Platform

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56-red)
![SQLite](https://img.shields.io/badge/SQLite-3.0-green)
![License](https://img.shields.io/badge/License-Educational-orange)

## Project Overview

A full-stack **Mutual Fund Analytics Platform** built during a 7-day individual
capstone internship at **Bluestock Fintech Pvt. Ltd.** The platform ingests
publicly available data from AMFI India, transforms it through a robust ETL
pipeline, stores it in a SQLite database, and presents insights via an
interactive Streamlit dashboard.

---

## Key Features

- **ETL Pipeline** — Automated ingestion of 10 datasets + live NAV from mfapi.in
- **SQLite Database** — 8-table star schema with 87,000+ rows
- **EDA** — 18 publication-quality charts (NAV trends, AUM, SIP, demographics)
- **Performance Metrics** — CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown
- **Advanced Analytics** — VaR, CVaR, Rolling Sharpe, Cohort Analysis, HHI
- **Fund Recommender** — Risk-appetite based fund recommendation engine
- **Interactive Dashboard** — 6-page Streamlit app with Bluestock branding

---

## Project Structure

bluestock_mf_capstone/

├── data/

│   ├── raw/                    ← Original CSVs + live NAV fetches

│   ├── processed/              ← Cleaned datasets + computed metrics

│   └── db/                     ← SQLite database (bluestock_mf.db)

├── notebooks/                  ← Jupyter notebooks for EDA

├── scripts/

│   ├── data_ingestion.py       ← Load all 10 CSV datasets

│   ├── live_nav_fetch.py       ← Fetch live NAV from mfapi.in

│   ├── validate_codes.py       ← AMFI code validation

│   ├── explore_fund_master.py  ← Fund master exploration

│   ├── clean_data.py           ← Clean all 10 datasets

│   ├── build_database.py       ← Build SQLite database

│   ├── run_queries.py          ← Run 10 SQL analytical queries

│   ├── eda_analysis.py         ← Generate 18 EDA charts

│   ├── performance_analytics.py← CAGR, Sharpe, Alpha, Beta, Scorecard

│   └── advanced_analytics.py  ← VaR, CVaR, Cohort, HHI, Recommender

├── sql/

│   ├── schema.sql              ← CREATE TABLE statements

│   └── queries.sql             ← 10 analytical SQL queries

├── dashboard/

│   └── app.py                  ← Streamlit dashboard (6 pages)

├── reports/

│   └── charts/                 ← 24 PNG charts

├── requirements.txt

└── README.md

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Evenjlin/bluestock_mf_capstone.git
cd bluestock_mf_capstone
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the full ETL pipeline
```bash
py -3.11 scripts/data_ingestion.py
py -3.11 scripts/live_nav_fetch.py
py -3.11 scripts/clean_data.py
py -3.11 scripts/build_database.py
py -3.11 scripts/performance_analytics.py
py -3.11 scripts/advanced_analytics.py
```

### 4. Launch the dashboard
```bash
py -3.11 -m streamlit run dashboard/app.py
```

---

## Data Sources

| Source | URL | Data |
|--------|-----|------|
| AMFI India | amfiindia.com | NAV, AUM, SIP flows |
| mfapi.in | api.mfapi.in | Live historical NAV |
| NSE India | nseindia.com | Benchmark indices |
| BSE India | bseindia.com | BSE SmallCap index |

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.11 |
| Data | Pandas, NumPy, SciPy |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Database | SQLite, SQLAlchemy |
| Dashboard | Streamlit |
| Version Control | Git, GitHub |
| API | mfapi.in (REST) |

---

## Key Results

| Metric | Value |
|--------|-------|
| Schemes Analysed | 40 |
| NAV Records | 46,000+ |
| Investor Transactions | 32,778 |
| Database Size | 5.46 MB |
| EDA Charts | 18 |
| Advanced Analytics Charts | 6 |
| Best 3yr CAGR | 32.4% |
| Best Sharpe Ratio | 1.45 |

---

## Internship Details

- **Company:** Bluestock Fintech Pvt. Ltd.
- **Role:** Data Analyst Intern
- **Duration:** 7 Working Days (June 2026)
- **Intern:** Evenjlin
- **Supervisor:** Bluestock Fintech Team

---

*This project is for educational purposes only and does not constitute
financial advice. All data sourced from publicly available AMFI India records.*