"""
build_database.py
Bluestock Fintech Capstone - Day 2
Creates SQLite database, loads all cleaned data into tables.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

PROCESSED_DIR = "data/processed"
DB_PATH       = "data/db/bluestock_mf.db"
os.makedirs("data/db", exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")


# -------------------------------------------------
# STEP 1: CREATE SCHEMA
# -------------------------------------------------
def create_schema():
    print("\n[1/3] Creating database schema ...")

    schema_sql = """
    -- Dimension: Fund Master
    CREATE TABLE IF NOT EXISTS dim_fund (
        amfi_code        TEXT PRIMARY KEY,
        fund_house       TEXT,
        scheme_name      TEXT,
        category         TEXT,
        sub_category     TEXT,
        plan             TEXT,
        launch_date      TEXT,
        benchmark        TEXT,
        expense_ratio_pct REAL,
        exit_load_pct    REAL,
        fund_manager     TEXT,
        risk_category    TEXT,
        sebi_category_code TEXT
    );

    -- Dimension: Date
    CREATE TABLE IF NOT EXISTS dim_date (
        date_id   TEXT PRIMARY KEY,
        year      INTEGER,
        month     INTEGER,
        quarter   INTEGER,
        month_name TEXT,
        is_weekday INTEGER
    );

    -- Fact: NAV History
    CREATE TABLE IF NOT EXISTS fact_nav (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code        TEXT,
        date             TEXT,
        nav              REAL,
        daily_return_pct REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    -- Fact: Investor Transactions
    CREATE TABLE IF NOT EXISTS fact_transactions (
        tx_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        investor_id        TEXT,
        amfi_code          TEXT,
        transaction_date   TEXT,
        transaction_type   TEXT,
        amount_inr         REAL,
        state              TEXT,
        city               TEXT,
        city_tier          TEXT,
        age_group          TEXT,
        gender             TEXT,
        annual_income_lakh REAL,
        payment_mode       TEXT,
        kyc_status         TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    -- Fact: Scheme Performance
    CREATE TABLE IF NOT EXISTS fact_performance (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code         TEXT,
        return_1yr_pct    REAL,
        return_3yr_pct    REAL,
        return_5yr_pct    REAL,
        benchmark_3yr_pct REAL,
        alpha             REAL,
        beta              REAL,
        sharpe_ratio      REAL,
        sortino_ratio     REAL,
        std_dev_ann_pct   REAL,
        max_drawdown_pct  REAL,
        morningstar_rating INTEGER,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    -- Fact: AUM by Fund House
    CREATE TABLE IF NOT EXISTS fact_aum (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        fund_house  TEXT,
        date        TEXT,
        aum_crore   REAL,
        num_schemes INTEGER
    );

    -- Fact: SIP Industry Inflows
    CREATE TABLE IF NOT EXISTS fact_sip_industry (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        month                   TEXT,
        sip_inflow_crore        REAL,
        active_sip_accounts_crore REAL,
        new_sip_accounts_lakh   REAL,
        sip_aum_lakh_crore      REAL,
        yoy_growth_pct          REAL
    );

    -- Fact: Portfolio Holdings
    CREATE TABLE IF NOT EXISTS fact_portfolio (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code    TEXT,
        stock_symbol TEXT,
        weight_pct   REAL,
        sector       TEXT,
        date         TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );

    -- Fact: Benchmark Indices
    CREATE TABLE IF NOT EXISTS fact_benchmark (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        date        TEXT,
        index_name  TEXT,
        close_value REAL
    );
    """

    with engine.connect() as conn:
        for statement in schema_sql.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()

    print("  Schema created successfully.")


# -------------------------------------------------
# STEP 2: LOAD DATA INTO TABLES
# -------------------------------------------------
def load_data():
    print("\n[2/3] Loading cleaned data into database ...")

    # 1. dim_fund
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        if "amfi_code" in df.columns:
            df["amfi_code"] = df["amfi_code"].astype(str)
        df.to_sql("dim_fund", engine, if_exists="replace",
                  index=False)
        print(f"  dim_fund          : {len(df)} rows loaded")
    except Exception as e:
        print(f"  dim_fund ERROR    : {e}")

    # 2. fact_nav
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav_history.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df["amfi_code"] = df["amfi_code"].astype(str)
        df.to_sql("fact_nav", engine, if_exists="replace",
                  index=False, chunksize=5000)
        print(f"  fact_nav          : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_nav ERROR    : {e}")

    # 3. fact_transactions
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df.to_sql("fact_transactions", engine, if_exists="replace",
                  index=False, chunksize=5000)
        print(f"  fact_transactions : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_transactions ERROR: {e}")

    # 4. fact_performance
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_performance.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df.to_sql("fact_performance", engine, if_exists="replace",
                  index=False)
        print(f"  fact_performance  : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_performance ERROR: {e}")

    # 5. fact_aum
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_aum_by_fund_house.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df.to_sql("fact_aum", engine, if_exists="replace",
                  index=False)
        print(f"  fact_aum          : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_aum ERROR    : {e}")

    # 6. fact_sip_industry
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_monthly_sip_inflows.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df.to_sql("fact_sip_industry", engine, if_exists="replace",
                  index=False)
        print(f"  fact_sip_industry : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_sip_industry ERROR: {e}")

    # 7. fact_portfolio
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_portfolio_holdings.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df.to_sql("fact_portfolio", engine, if_exists="replace",
                  index=False)
        print(f"  fact_portfolio    : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_portfolio ERROR: {e}")

    # 8. fact_benchmark
    try:
        df = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_benchmark_indices.csv"))
        df.columns = [c.lower().strip() for c in df.columns]
        df.to_sql("fact_benchmark", engine, if_exists="replace",
                  index=False)
        print(f"  fact_benchmark    : {len(df)} rows loaded")
    except Exception as e:
        print(f"  fact_benchmark ERROR: {e}")


# -------------------------------------------------
# STEP 3: VERIFY DATABASE
# -------------------------------------------------
def verify_database():
    print("\n[3/3] Verifying database ...")

    with engine.connect() as conn:
        tables = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )).fetchall()

        print(f"\n  {'Table':<25} {'Rows':>8}")
        print(f"  {'-'*35}")
        for (table,) in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table:<25} {count:>8,}")

    db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n  Database size : {db_size:.2f} MB")
    print(f"  Database path : {DB_PATH}")


# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  Bluestock Fintech - Day 2: Database Build")
    print("=" * 60)

    create_schema()
    load_data()
    verify_database()

    print("\n" + "=" * 60)
    print("  Database ready: data/db/bluestock_mf.db")
    print("=" * 60)