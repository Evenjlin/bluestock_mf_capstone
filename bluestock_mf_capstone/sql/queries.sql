-- ============================================
-- Bluestock Fintech - Day 2: SQL Queries
-- Database: bluestock_mf.db
-- ============================================


-- Query 1: Top 5 funds by latest NAV value
-- Shows which funds have the highest NAV currently
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    ROUND(n.nav, 2) AS latest_nav
FROM dim_fund f
JOIN fact_nav n ON f.amfi_code = n.amfi_code
WHERE n.date = (
    SELECT MAX(date) FROM fact_nav
    WHERE amfi_code = f.amfi_code
)
ORDER BY latest_nav DESC
LIMIT 5;


-- Query 2: Average NAV per month for a specific fund (HDFC Top 100)
-- Useful for spotting monthly trend
SELECT
    SUBSTR(date, 1, 7)   AS month,
    ROUND(AVG(nav), 2)   AS avg_nav,
    ROUND(MIN(nav), 2)   AS min_nav,
    ROUND(MAX(nav), 2)   AS max_nav
FROM fact_nav
WHERE amfi_code = '125497'
GROUP BY SUBSTR(date, 1, 7)
ORDER BY month DESC
LIMIT 12;


-- Query 3: SIP inflow year-on-year growth
-- Shows how SIP inflows grew each year
SELECT
    SUBSTR(month, 1, 4)             AS year,
    ROUND(SUM(sip_inflow_crore), 2) AS total_sip_inflow_crore,
    ROUND(AVG(sip_inflow_crore), 2) AS avg_monthly_sip_crore
FROM fact_sip_industry
GROUP BY SUBSTR(month, 1, 4)
ORDER BY year;


-- Query 4: Total transaction amount by state
-- Geographic distribution of investor money
SELECT
    state,
    COUNT(*)                          AS total_transactions,
    ROUND(SUM(amount_inr), 2)         AS total_amount_inr,
    ROUND(AVG(amount_inr), 2)         AS avg_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC
LIMIT 10;


-- Query 5: Funds with expense ratio less than 1%
-- Helps identify low-cost funds
SELECT
    scheme_name,
    fund_house,
    category,
    sub_category,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;


-- Query 6: Top 5 best performing funds by 3-year return
-- Core metric for long-term investors
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    ROUND(p.return_3yr_pct, 2)  AS return_3yr_pct,
    ROUND(p.sharpe_ratio, 2)    AS sharpe_ratio,
    ROUND(p.alpha, 2)           AS alpha
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 5;


-- Query 7: SIP vs Lumpsum vs Redemption split
-- Investor behaviour breakdown
SELECT
    transaction_type,
    COUNT(*)                        AS num_transactions,
    ROUND(SUM(amount_inr), 2)       AS total_amount_inr,
    ROUND(AVG(amount_inr), 2)       AS avg_amount_inr,
    ROUND(100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM fact_transactions), 2) AS pct_of_total
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;


-- Query 8: AUM growth by fund house over years
-- Tracks which AMCs are growing fastest
SELECT
    fund_house,
    SUBSTR(date, 1, 4)          AS year,
    ROUND(SUM(aum_crore), 2)    AS total_aum_crore
FROM fact_aum
GROUP BY fund_house, SUBSTR(date, 1, 4)
ORDER BY fund_house, year;


-- Query 9: Funds with highest Sharpe ratio per category
-- Best risk-adjusted return in each category
SELECT
    f.category,
    f.scheme_name,
    f.fund_house,
    ROUND(p.sharpe_ratio, 3)     AS sharpe_ratio,
    ROUND(p.return_3yr_pct, 2)   AS return_3yr_pct,
    ROUND(p.max_drawdown_pct, 2) AS max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio = (
    SELECT MAX(p2.sharpe_ratio)
    FROM fact_performance p2
    JOIN dim_fund f2 ON p2.amfi_code = f2.amfi_code
    WHERE f2.category = f.category
)
ORDER BY p.sharpe_ratio DESC;


-- Query 10: Transaction breakdown by age group and gender
-- Demographic insights
SELECT
    age_group,
    gender,
    COUNT(*)                    AS num_transactions,
    ROUND(AVG(amount_inr), 2)   AS avg_sip_amount,
    ROUND(SUM(amount_inr), 2)   AS total_invested
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY age_group, gender
ORDER BY age_group, gender;