"""
Bluestock Fintech Capstone - Day 7
Master script to run the complete ETL pipeline end to end.
"""

import subprocess
import sys
import time

PYTHON = sys.executable

scripts = [
    ("Data Ingestion",          "scripts/data_ingestion.py"),
    ("Live NAV Fetch",          "scripts/live_nav_fetch.py"),
    ("Data Cleaning",           "scripts/clean_data.py"),
    ("Build Database",          "scripts/build_database.py"),
    ("Run SQL Queries",         "scripts/run_queries.py"),
    ("EDA Analysis",            "scripts/eda_analysis.py"),
    ("Performance Analytics",   "scripts/performance_analytics.py"),
    ("Advanced Analytics",      "scripts/advanced_analytics.py"),
]

print("=" * 60)
print("  Bluestock Fintech - Complete ETL Pipeline")
print("=" * 60)

results = []
for name, script in scripts:
    print(f"\nRunning: {name} ...")
    start = time.time()
    result = subprocess.run([PYTHON, script], capture_output=True, text=True)
    elapsed = round(time.time() - start, 1)

    if result.returncode == 0:
        print(f"  SUCCESS in {elapsed}s")
        results.append((name, "SUCCESS", elapsed))
    else:
        print(f"  FAILED in {elapsed}s")
        print(f"  Error: {result.stderr[-200:]}")
        results.append((name, "FAILED", elapsed))

print("\n" + "=" * 60)
print("  Pipeline Summary")
print("=" * 60)
for name, status, elapsed in results:
    icon = "OK" if status == "SUCCESS" else "FAIL"
    print(f"  [{icon}] {name:<30} {elapsed}s")
print("=" * 60)
print("\nTo launch dashboard:")
print("  py -3.11 -m streamlit run dashboard/app.py")