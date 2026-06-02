"""
explore_fund_master.py
Understand the fund master dataset — categories, fund houses, risk grades.
"""

import pandas as pd
import os

df = pd.read_csv("data/raw/01_fund_master.csv")

print("=" * 55)
print("  Fund Master — Quick Exploration")
print("=" * 55)

print(f"\nTotal schemes : {len(df)}")
print(f"Columns       : {list(df.columns)}")

print("\n--- Unique Fund Houses ---")
print(df["fund_house"].value_counts().to_string())

print("\n--- Categories ---")
print(df["category"].value_counts().to_string())

print("\n--- Sub-categories ---")
print(df["sub_category"].value_counts().to_string())

print("\n--- Risk Grades ---")
print(df["risk_category"].value_counts().to_string())

print("\n--- Plan Types (Direct/Regular) ---")
print(df["plan"].value_counts().to_string())

print("\n--- Expense Ratio Stats ---")
print(df["expense_ratio_pct"].describe())