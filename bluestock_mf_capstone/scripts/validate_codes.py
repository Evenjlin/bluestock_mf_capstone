"""
validate_codes.py
Check that all AMFI codes in fund_master exist in nav_history.
"""

import pandas as pd

fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav_history = pd.read_csv("data/raw/02_nav_history.csv")

master_codes = set(fund_master["amfi_code"].astype(str))
nav_codes    = set(nav_history["amfi_code"].astype(str))

missing_in_nav    = master_codes - nav_codes
missing_in_master = nav_codes - master_codes

print("=" * 55)
print("  AMFI Code Validation Report")
print("=" * 55)
print(f"\n  Codes in fund_master  : {len(master_codes)}")
print(f"  Codes in nav_history  : {len(nav_codes)}")

if missing_in_nav:
    print(f"\n  ✗ In master but MISSING from nav_history:")
    for c in missing_in_nav:
        print(f"    - {c}")
else:
    print(f"\n  ✓ All master codes exist in nav_history")

if missing_in_master:
    print(f"\n  ⚠ In nav_history but NOT in master (extra):")
    for c in missing_in_master:
        print(f"    - {c}")
else:
    print(f"  ✓ No extra codes in nav_history")

print("\n  ✅ Validation complete.")