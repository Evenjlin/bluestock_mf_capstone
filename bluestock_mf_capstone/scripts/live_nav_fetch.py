"""
live_nav_fetch.py
Bluestock Fintech Capstone - Day 1
Fetches live historical NAV for 5 schemes from mfapi.in
with retry logic and error handling.
"""

import os
import time
import requests
import pandas as pd

# Config
RAW_DATA_DIR = "data/raw"
BASE_URL = "https://api.mfapi.in/mf/{code}"

SCHEMES = {
    "125497": "HDFC_Top_100",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_LargeCap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}


def fetch_and_save(scheme_code, scheme_name, retries=3):
    """
    Fetch NAV history from mfapi.in for a given scheme code.
    Retries up to retries times on failure with a 5-second gap.
    """
    url = BASE_URL.format(code=scheme_code)
    print("\n  Fetching: " + scheme_name + " (AMFI Code: " + scheme_code + ")")
    print("  URL     : " + url)

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            meta = data.get("meta", {})
            nav_records = data.get("data", [])

            if not nav_records:
                print("  WARNING: No NAV records returned for " + scheme_name)
                return None

            # Build DataFrame
            df = pd.DataFrame(nav_records)
            df["amfi_code"] = scheme_code
            df["scheme_name"] = meta.get("scheme_name", scheme_name)
            df["fund_house"] = meta.get("fund_house", "N/A")
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
            df = df.sort_values("date").reset_index(drop=True)
            df = df[["amfi_code", "scheme_name", "fund_house", "date", "nav"]]

            # Save individual CSV
            os.makedirs(RAW_DATA_DIR, exist_ok=True)
            filename = "live_nav_" + scheme_name + "_" + scheme_code + ".csv"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            df.to_csv(filepath, index=False)

            print("  Fund      : " + str(meta.get("scheme_name", "N/A")))
            print("  Rows      : " + str(len(df)))
            print("  Date range: " + str(df["date"].min().date()) + " to " + str(df["date"].max().date()))
            print("  Latest NAV: " + str(round(df["nav"].iloc[-1], 4)))
            print("  [SUCCESS] Saved to " + filepath)
            return df

        except requests.exceptions.ConnectionError as e:
            print("  [WARNING] Attempt " + str(attempt) + "/" + str(retries) + " - Connection error: " + str(e))
        except requests.exceptions.HTTPError as e:
            print("  [WARNING] Attempt " + str(attempt) + "/" + str(retries) + " - HTTP error: " + str(e))
        except requests.exceptions.Timeout:
            print("  [WARNING] Attempt " + str(attempt) + "/" + str(retries) + " - Request timed out.")
        except Exception as e:
            print("  [WARNING] Attempt " + str(attempt) + "/" + str(retries) + " - Unexpected error: " + str(e))

        if attempt < retries:
            print("  Waiting 5 seconds before retry...")
            time.sleep(5)

    print("  [FAILED] All " + str(retries) + " attempts failed for " + scheme_name)
    return None


def main():
    print("=" * 60)
    print("  Bluestock Fintech - Live NAV Fetch (mfapi.in)")
    print("=" * 60)

    all_dfs = []
    success = []
    failed = []

    for code, name in SCHEMES.items():
        df = fetch_and_save(code, name, retries=3)
        if df is not None:
            all_dfs.append(df)
            success.append(name)
        else:
            failed.append(name)

    # Save combined CSV
    print("\n" + "=" * 60)
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        combined_path = os.path.join(RAW_DATA_DIR, "live_nav_all_schemes_combined.csv")
        combined.to_csv(combined_path, index=False)
        print("  [SUCCESS] Combined CSV saved to " + combined_path)
        print("  Total rows : " + str(len(combined)))
        print("  Funds      : " + str(combined["scheme_name"].nunique()))

    # Summary
    print("\n  SUMMARY")
    print("  -------")
    if success:
        print("  SUCCESS (" + str(len(success)) + ") : " + ", ".join(success))
    else:
        print("  SUCCESS (0) : None")

    if failed:
        print("  FAILED  (" + str(len(failed)) + ") : " + ", ".join(failed))
        print("\n  NOTE: Failed schemes can be retried later.")
        print("  The 02_nav_history.csv dataset covers all 40 funds.")
    else:
        print("  FAILED  (0) : None")

    print("=" * 60)


if __name__ == "__main__":
    main()