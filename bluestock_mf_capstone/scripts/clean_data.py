"""
Bluestock Fintech Capstone - Day 2
Cleans all 10 datasets and saves them to data/processed/
"""

import os
import pandas as pd
import numpy as np

RAW_DIR       = "data/raw"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


def detect_column(df, candidates):
    """Find the first matching column name from a list of candidates."""
    for c in candidates:
        if c in df.columns:
            return c
    return None



def clean_nav_history():
    print("\n[1/5] Cleaning nav_history.csv ...")
    df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    print(f"  Columns found : {list(df.columns)}")
    print(f"  Before        : {df.shape}")

    # Auto-detect column names
    code_col = detect_column(df, ["amfi_code", "scheme_code", "code", "schemeCode", "AMFI_Code"])
    date_col = detect_column(df, ["date", "Date", "nav_date", "DATE"])
    nav_col  = detect_column(df, ["nav", "NAV", "Nav", "nav_value"])

    print(f"  Detected cols : code={code_col}, date={date_col}, nav={nav_col}")

    if not all([code_col, date_col, nav_col]):
        print("  ERROR: Could not detect required columns. Check column names above.")
        return None

    # Rename to standard names
    df = df.rename(columns={code_col: "amfi_code", date_col: "date", nav_col: "nav"})

    # Keep only needed columns + any extras
    core_cols = ["amfi_code", "date", "nav"]
    extra_cols = [c for c in df.columns if c not in core_cols]
    df = df[core_cols + extra_cols]

    # Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Ensure amfi_code is string
    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()

    # Ensure nav is numeric
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # Sort
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Remove duplicates
    df = df.drop_duplicates(subset=["amfi_code", "date"])

    # Remove invalid NAV
    df = df[df["nav"] > 0]

    # Forward fill missing business days per fund
    all_funds = []
    for code, group in df.groupby("amfi_code"):
        group = group.set_index("date")
        full_range = pd.date_range(group.index.min(), group.index.max(), freq="B")
        group = group.reindex(full_range).ffill().reset_index()
        group = group.rename(columns={"index": "date"})
        group["amfi_code"] = code
        all_funds.append(group)

    df = pd.concat(all_funds, ignore_index=True)

    # Compute daily return %
    df["daily_return_pct"] = (
        df.groupby("amfi_code")["nav"]
        .pct_change() * 100
    ).round(4)

    print(f"  After         : {df.shape}")
    print(f"  Null NAV      : {df['nav'].isnull().sum()}")
    print(f"  Unique funds  : {df['amfi_code'].nunique()}")

    out = os.path.join(PROCESSED_DIR, "clean_nav_history.csv")
    df.to_csv(out, index=False)
    print(f"  Saved         : {out}")
    return df



def clean_transactions():
    print("\n[2/5] Cleaning investor_transactions.csv ...")
    df = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    print(f"  Columns found : {list(df.columns)}")
    print(f"  Before        : {df.shape}")

    # Auto-detect columns
    type_col   = detect_column(df, ["transaction_type", "type", "tx_type", "Type"])
    amount_col = detect_column(df, ["amount_inr", "amount", "Amount", "amount_INR"])
    date_col   = detect_column(df, ["transaction_date", "date", "Date", "tx_date"])

    print(f"  Detected cols : type={type_col}, amount={amount_col}, date={date_col}")

    # Standardise transaction type
    if type_col:
        df[type_col] = df[type_col].astype(str).str.strip().str.title()
        valid_types = ["Sip", "Lumpsum", "Redemption"]
        before_filter = len(df)
        df = df[df[type_col].isin(valid_types)]
        print(f"  Removed {before_filter - len(df)} rows with invalid transaction type")

    # Validate amount > 0
    if amount_col:
        df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
        df = df[df[amount_col] > 0]

    # Parse date
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

    # Fix KYC status
    kyc_col = detect_column(df, ["kyc_status", "kyc", "KYC"])
    if kyc_col:
        df[kyc_col] = df[kyc_col].astype(str).str.strip().str.title()

    # Drop full duplicates
    df = df.drop_duplicates()

    print(f"  After         : {df.shape}")
    if type_col:
        print(f"  Tx types      : {df[type_col].value_counts().to_dict()}")

    out = os.path.join(PROCESSED_DIR, "clean_transactions.csv")
    df.to_csv(out, index=False)
    print(f"  Saved         : {out}")
    return df



def clean_performance():
    print("\n[3/5] Cleaning scheme_performance.csv ...")
    df = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))
    print(f"  Columns found : {list(df.columns)}")
    print(f"  Before        : {df.shape}")

    # Validate expense ratio
    exp_col = detect_column(df, ["expense_ratio_pct", "expense_ratio", "expense"])
    if exp_col:
        df[exp_col] = pd.to_numeric(df[exp_col], errors="coerce")
        bad = df[(df[exp_col] < 0.1) | (df[exp_col] > 2.5)]
        if len(bad) > 0:
            print(f"  Warning: {len(bad)} rows with unusual expense ratio (outside 0.1-2.5%)")

    # Make numeric columns correct type
    num_candidates = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "sharpe_ratio", "sortino_ratio", "alpha", "beta",
        "std_dev_ann_pct", "max_drawdown_pct", "benchmark_3yr_pct"
    ]
    for col in num_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag negative Sharpe
    sharpe_col = detect_column(df, ["sharpe_ratio", "sharpe"])
    if sharpe_col:
        neg = df[df[sharpe_col] < 0]
        print(f"  Negative Sharpe funds : {len(neg)}")

    df = df.drop_duplicates()

    print(f"  After         : {df.shape}")

    out = os.path.join(PROCESSED_DIR, "clean_performance.csv")
    df.to_csv(out, index=False)
    print(f"  Saved         : {out}")
    return df



def clean_fund_master():
    print("\n[4/5] Cleaning fund_master.csv ...")
    df = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    print(f"  Columns found : {list(df.columns)}")
    print(f"  Before        : {df.shape}")

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # Parse launch date
    date_col = detect_column(df, ["launch_date", "date", "inception_date"])
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Remove duplicates on amfi_code
    code_col = detect_column(df, ["amfi_code", "scheme_code", "code"])
    if code_col:
        df = df.drop_duplicates(subset=[code_col])

    print(f"  After         : {df.shape}")

    out = os.path.join(PROCESSED_DIR, "clean_fund_master.csv")
    df.to_csv(out, index=False)
    print(f"  Saved         : {out}")
    return df



def clean_remaining():
    print("\n[5/5] Cleaning remaining datasets ...")

    files = {
        "03_aum_by_fund_house.csv"   : "clean_aum_by_fund_house.csv",
        "04_monthly_sip_inflows.csv" : "clean_monthly_sip_inflows.csv",
        "05_category_inflows.csv"    : "clean_category_inflows.csv",
        "06_industry_folio_count.csv": "clean_industry_folio_count.csv",
        "09_portfolio_holdings.csv"  : "clean_portfolio_holdings.csv",
        "10_benchmark_indices.csv"   : "clean_benchmark_indices.csv",
    }

    for raw_file, clean_file in files.items():
        try:
            df = pd.read_csv(os.path.join(RAW_DIR, raw_file))
            before = df.shape

            # Strip whitespace from string columns
            str_cols = df.select_dtypes(include=["object"]).columns
            for col in str_cols:
                df[col] = df[col].astype(str).str.strip()

            # Remove full duplicates
            df = df.drop_duplicates()

            # Remove completely empty rows
            df = df.dropna(how="all")

            # Parse date/month columns
            for col in df.columns:
                if any(kw in col.lower() for kw in ["date", "month", "period"]):
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            out = os.path.join(PROCESSED_DIR, clean_file)
            df.to_csv(out, index=False)
            print(f"  {raw_file:<35} {str(before):<15} -> {str(df.shape):<15} Saved")

        except Exception as e:
            print(f"  ERROR processing {raw_file}: {e}")



if __name__ == "__main__":
    print("=" * 60)
    print("  Bluestock Fintech - Day 2: Data Cleaning")
    print("=" * 60)

    clean_fund_master()
    clean_nav_history()
    clean_transactions()
    clean_performance()
    clean_remaining()

    print("\n" + "=" * 60)
    print("  All datasets cleaned and saved to data/processed/")
    print("=" * 60)