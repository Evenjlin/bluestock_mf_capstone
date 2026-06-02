"""
live_nav_fetch.py
Bluestock Fintech Capstone — Day 1
Fetches live historical NAV for 5 schemes from mfapi.in
"""

import requests
import pandas as pd
import os

RAW_DATA_DIR = "data/raw"

# 5 schemes specified in the capstone document
SCHEMES = {
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_LargeCap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}

BASE_URL = "https://api.mfapi.in/mf/{code}"

def fetch_and_save(scheme_code, scheme_name):
    """Fetch NAV history from mfapi.in and save as CSV."""
    url = BASE_URL.format(code=scheme_code)
    print(f"\n  Fetching: {scheme_name} (code: {scheme_code})")
    print(f"  URL: {url}")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Extract metadata
        meta = data.get("meta", {})
        nav_records = data.get("data", [])

        print(f"  Fund    : {meta.get('scheme_name', 'N/A')}")
        print(f"  Records : {len(nav_records)} NAV entries")

        # Build DataFrame
        df = pd.DataFrame(nav_records)
        df["amfi_code"]    = scheme_code
        df["scheme_name"]  = meta.get("scheme_name", scheme_name)
        df["fund_house"]   = meta.get("fund_house", "N/A")
        df["date"]         = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"]          = pd.to_numeric(df["nav"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)

        # Reorder columns
        df = df[["amfi_code", "scheme_name", "fund_house", "date", "nav"]]

        # Save
        filename = f"live_nav_{scheme_name}.csv"
        filepath = os.path.join(RAW_DATA_DIR, filename)
        df.to_csv(filepath, index=False)

        print(f"  Date Range: {df['date'].min().date()} → {df['date'].max().date()}")
        print(f"  Latest NAV: ₹{df['nav'].iloc[-1]:.4f}")
        print(f"  ✓ Saved → {filepath}")

        return df

    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection failed. Check internet connection.")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def main():
    print("=" * 55)
    print("  Bluestock Fintech: Live NAV Fetch (mfapi.in)")
    print("=" * 55)

    all_dfs = []

    for code, name in SCHEMES.items():
        df = fetch_and_save(code, name)
        if df is not None:
            all_dfs.append(df)

    # Save combined file
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        combined_path = os.path.join(RAW_DATA_DIR, "live_nav_all_5_schemes.csv")
        combined.to_csv(combined_path, index=False)
        print(f"\n{'='*55}")
        print(f"✅ All done! Combined file saved.")
        print(f"   File  : {combined_path}")
        print(f"   Rows  : {len(combined)}")
        print(f"   Funds : {combined['scheme_name'].nunique()}")
    else:
        print("\n✗ No data fetched. Check your internet connection.")


if __name__ == "__main__":
    main()