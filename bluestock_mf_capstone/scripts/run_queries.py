"""
 Day 2
Runs all 10 SQL queries and prints results.
"""

import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "data/db/bluestock_mf.db"
engine  = create_engine(f"sqlite:///{DB_PATH}")

queries = {
    "Q1 - Top 5 Funds by Latest NAV": """
        SELECT f.scheme_name, f.fund_house, f.category,
               ROUND(n.nav, 2) AS latest_nav
        FROM dim_fund f
        JOIN fact_nav n ON f.amfi_code = n.amfi_code
        WHERE n.date = (SELECT MAX(date) FROM fact_nav WHERE amfi_code = f.amfi_code)
        ORDER BY latest_nav DESC LIMIT 5
    """,
    "Q2 - Monthly Avg NAV (HDFC Top 100, last 12 months)": """
        SELECT SUBSTR(date,1,7) AS month,
               ROUND(AVG(nav),2) AS avg_nav,
               ROUND(MIN(nav),2) AS min_nav,
               ROUND(MAX(nav),2) AS max_nav
        FROM fact_nav WHERE amfi_code = '125497'
        GROUP BY SUBSTR(date,1,7)
        ORDER BY month DESC LIMIT 12
    """,
    "Q3 - SIP Inflow Year-on-Year": """
        SELECT SUBSTR(month,1,4) AS year,
               ROUND(SUM(sip_inflow_crore),2) AS total_sip_crore,
               ROUND(AVG(sip_inflow_crore),2) AS avg_monthly_crore
        FROM fact_sip_industry
        GROUP BY SUBSTR(month,1,4) ORDER BY year
    """,
    "Q4 - Top 10 States by Transaction Amount": """
        SELECT state, COUNT(*) AS transactions,
               ROUND(SUM(amount_inr),2) AS total_amount,
               ROUND(AVG(amount_inr),2) AS avg_amount
        FROM fact_transactions
        GROUP BY state ORDER BY total_amount DESC LIMIT 10
    """,
    "Q5 - Funds with Expense Ratio < 1%": """
        SELECT scheme_name, fund_house, category, expense_ratio_pct
        FROM dim_fund WHERE expense_ratio_pct < 1.0
        ORDER BY expense_ratio_pct ASC
    """,
    "Q6 - Top 5 Funds by 3-Year Return": """
        SELECT f.scheme_name, f.fund_house, f.category,
               ROUND(p.return_3yr_pct,2) AS return_3yr,
               ROUND(p.sharpe_ratio,2)   AS sharpe,
               ROUND(p.alpha,2)          AS alpha
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.return_3yr_pct DESC LIMIT 5
    """,
    "Q7 - SIP vs Lumpsum vs Redemption Split": """
        SELECT transaction_type, COUNT(*) AS count,
               ROUND(SUM(amount_inr),2) AS total_amount,
               ROUND(AVG(amount_inr),2) AS avg_amount
        FROM fact_transactions
        GROUP BY transaction_type ORDER BY total_amount DESC
    """,
    "Q8 - AUM by Fund House per Year": """
        SELECT fund_house, SUBSTR(date,1,4) AS year,
               ROUND(SUM(aum_crore),2) AS total_aum_crore
        FROM fact_aum
        GROUP BY fund_house, SUBSTR(date,1,4)
        ORDER BY fund_house, year
    """,
    "Q9 - Best Sharpe Ratio per Category": """
        SELECT f.category, f.scheme_name,
               ROUND(p.sharpe_ratio,3)   AS sharpe,
               ROUND(p.return_3yr_pct,2) AS return_3yr,
               ROUND(p.max_drawdown_pct,2) AS max_drawdown
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        WHERE p.sharpe_ratio = (
            SELECT MAX(p2.sharpe_ratio)
            FROM fact_performance p2
            JOIN dim_fund f2 ON p2.amfi_code = f2.amfi_code
            WHERE f2.category = f.category)
        ORDER BY p.sharpe_ratio DESC
    """,
    "Q10 - SIP Amount by Age Group and Gender": """
        SELECT age_group, gender, COUNT(*) AS transactions,
               ROUND(AVG(amount_inr),2) AS avg_sip_amount,
               ROUND(SUM(amount_inr),2) AS total_invested
        FROM fact_transactions
        WHERE transaction_type = 'Sip'
        GROUP BY age_group, gender
        ORDER BY age_group, gender
    """,
}

if __name__ == "__main__":
    print("=" * 60)
    print("  Bluestock Fintech - Day 2: SQL Query Results")
    print("=" * 60)

    for title, sql in queries.items():
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        try:
            df = pd.read_sql(sql, engine)
            print(df.to_string(index=False))
            print(f"\n  Rows returned: {len(df)}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    print("  All 10 queries executed successfully.")
    print("=" * 60)