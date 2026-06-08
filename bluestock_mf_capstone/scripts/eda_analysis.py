"""
Bluestock Fintech Capstone - Day 3
Exploratory Data Analysis - 15 charts
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# Config
PROCESSED_DIR = "data/processed"
CHARTS_DIR    = "reports/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# Style
plt.rcParams.update({
    "figure.facecolor" : "#0f1117",
    "axes.facecolor"   : "#1a1d2e",
    "axes.edgecolor"   : "#444",
    "axes.labelcolor"  : "#cccccc",
    "xtick.color"      : "#aaaaaa",
    "ytick.color"      : "#aaaaaa",
    "text.color"       : "#eeeeee",
    "grid.color"       : "#2a2d3e",
    "grid.linestyle"   : "--",
    "grid.alpha"       : 0.5,
    "font.family"      : "DejaVu Sans",
    "font.size"        : 10,
})

COLORS = ["#4e9af1","#f1c94e","#f17c4e","#4ef1a0",
          "#c44ef1","#f14e7c","#4ef1e8","#f1844e"]

def save(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=plt.rcParams["figure.facecolor"])
    plt.close()
    print("  Saved: " + path)


# Load data 
print("Loading datasets ...")
nav   = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav_history.csv"),
                    parse_dates=["date"])
funds = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"))
aum   = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_aum_by_fund_house.csv"))
sip   = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_monthly_sip_inflows.csv"))
cat   = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_category_inflows.csv"))
folio = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_industry_folio_count.csv"))
perf  = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_performance.csv"))
tx    = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"))
port  = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_portfolio_holdings.csv"))
bench = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_benchmark_indices.csv"))

# Standardise amfi_code to string in all dataframes
for df in [nav, funds, perf]:
    if "amfi_code" in df.columns:
        df["amfi_code"] = df["amfi_code"].astype(str).str.strip()

# Merge perf with fund metadata safely
merge_cols = ["amfi_code"]
for col in ["scheme_name", "fund_house", "category", "sub_category"]:
    if col in funds.columns:
        merge_cols.append(col)

perf_merged = perf.merge(funds[merge_cols], on="amfi_code", how="left")

print("All datasets loaded.")
print("=" * 55)


# CHART 1: NAV Trend Lines
print("\n[1/15] NAV Trend Lines ...")
selected = ["125497", "119551", "120503", "118632", "119092", "120841"]
labels = {
    "125497": "HDFC Top 100",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon LargeCap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}

fig, ax = plt.subplots(figsize=(14, 6))
for i, code in enumerate(selected):
    df_f = nav[nav["amfi_code"] == code].copy()
    if df_f.empty:
        continue
    df_f = df_f.sort_values("date")
    df_f["nav_norm"] = df_f["nav"] / df_f["nav"].iloc[0] * 100
    ax.plot(df_f["date"], df_f["nav_norm"],
            label=labels.get(code, code),
            color=COLORS[i % len(COLORS)], linewidth=1.5)

ax.set_title("NAV Growth Trend (Normalised to 100) - 2022 to 2026",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Date")
ax.set_ylabel("Normalised NAV (Base = 100)")
ax.legend(loc="upper left", fontsize=9,
          facecolor="#1a1d2e", edgecolor="#444")
ax.grid(True)
save("01_nav_trend_lines.png")


# CHART 2: AUM Growth by Fund House
print("[2/15] AUM Growth by Fund House ...")
print("  AUM columns: " + str(list(aum.columns)))

aum_col = next((c for c in aum.columns if "aum" in c.lower()), None)
fh_col  = next((c for c in aum.columns if "fund" in c.lower() or "house" in c.lower() or "amc" in c.lower()), None)

if aum_col and fh_col:
    aum[aum_col] = pd.to_numeric(aum[aum_col], errors="coerce")
    aum_latest = aum.groupby(fh_col)[aum_col].max().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.barh(aum_latest.index[::-1], aum_latest.values[::-1],
                   color=COLORS[:len(aum_latest)])
    ax.set_title("Top Fund Houses by Peak AUM",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("AUM (Crore)")
    for bar, val in zip(bars, aum_latest.values[::-1]):
        ax.text(bar.get_width() * 1.01,
                bar.get_y() + bar.get_height() / 2,
                str(round(val, 0)), va="center", fontsize=9)
    ax.grid(True, axis="x")
    save("02_aum_by_fund_house.png")
else:
    print("  Skipped - could not detect AUM columns")


# CHART 3: SIP Inflow Trend
print("[3/15] SIP Inflow Trend ...")
print("  SIP columns: " + str(list(sip.columns)))

sip_col = next((c for c in sip.columns if "inflow" in c.lower()), None)
mon_col = next((c for c in sip.columns if "month" in c.lower() or "date" in c.lower()), None)

if sip_col and mon_col:
    sip[sip_col] = pd.to_numeric(sip[sip_col], errors="coerce")
    sip[mon_col] = pd.to_datetime(sip[mon_col], errors="coerce")
    sip_clean = sip.dropna(subset=[sip_col, mon_col]).sort_values(mon_col)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(sip_clean[mon_col], sip_clean[sip_col],
                    alpha=0.3, color="#4e9af1")
    ax.plot(sip_clean[mon_col], sip_clean[sip_col],
            color="#4e9af1", linewidth=2)
    ax.set_title("Monthly SIP Inflow Trend (Rs. Crore) - 2022 to 2026",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("SIP Inflow (Rs. Crore)")

    max_idx = sip_clean[sip_col].idxmax()
    ax.annotate(
        "All-time high\nRs." + str(round(sip_clean[sip_col].max(), 0)) + " Cr",
        xy=(sip_clean[mon_col][max_idx], sip_clean[sip_col].max()),
        xytext=(sip_clean[mon_col][max_idx], sip_clean[sip_col].max() * 0.85),
        arrowprops=dict(arrowstyle="->", color="#f1c94e"),
        color="#f1c94e", fontsize=9, ha="center"
    )
    ax.grid(True)
    save("03_sip_inflow_trend.png")


# CHART 4: Category Inflow Heatmap
print("[4/15] Category Inflow Heatmap ...")
print("  Category columns: " + str(list(cat.columns)))

cat_col    = next((c for c in cat.columns if "category" in c.lower() or "cat" in c.lower()), None)
inflow_col = next((c for c in cat.columns if "inflow" in c.lower() or "net" in c.lower()), None)
month_col2 = next((c for c in cat.columns if "month" in c.lower() or "date" in c.lower()), None)

if cat_col and inflow_col:
    cat[inflow_col] = pd.to_numeric(cat[inflow_col], errors="coerce")

    if month_col2:
        cat[month_col2] = pd.to_datetime(cat[month_col2], errors="coerce")
        cat["month_str"] = cat[month_col2].dt.strftime("%Y-%m")
        pivot = cat.pivot_table(index=cat_col, columns="month_str",
                                values=inflow_col, aggfunc="sum").fillna(0)
    else:
        pivot = cat.pivot_table(index=cat_col, columns=cat.columns[1],
                                values=inflow_col, aggfunc="sum").fillna(0)

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(pivot, ax=ax, cmap="RdYlGn", center=0,
                linewidths=0.3, linecolor="#1a1d2e",
                cbar_kws={"label": "Net Inflow (Crore)"})
    ax.set_title("Category-wise Net Inflows Heatmap",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("Fund Category")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    save("04_category_inflow_heatmap.png")


# CHART 5: Investor Age Group Distribution
print("[5/15] Investor Age Distribution ...")
age_col = next((c for c in tx.columns if "age" in c.lower()), None)
amt_col = next((c for c in tx.columns if "amount" in c.lower()), None)

if age_col:
    age_counts = tx[age_col].value_counts().sort_index()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    wedges, texts, autotexts = ax1.pie(
        age_counts.values,
        labels=age_counts.index,
        autopct="%1.1f%%",
        colors=COLORS[:len(age_counts)],
        startangle=90,
        wedgeprops={"edgecolor": "#0f1117", "linewidth": 2}
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax1.set_title("Age Group Distribution", fontsize=12, fontweight="bold")

    if amt_col:
        type_col = next((c for c in tx.columns if "type" in c.lower()), None)
        sip_tx = tx[tx[type_col] == "Sip"] if type_col else tx
        age_order = sorted(tx[age_col].dropna().unique())
        data_by_age = [sip_tx[sip_tx[age_col] == age][amt_col].dropna().values
                       for age in age_order]
        bp = ax2.boxplot(data_by_age, labels=age_order,
                         patch_artist=True,
                         medianprops={"color": "#f1c94e", "linewidth": 2})
        for patch, color in zip(bp["boxes"], COLORS):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax2.set_title("SIP Amount by Age Group", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Age Group")
        ax2.set_ylabel("SIP Amount (Rs.)")
        ax2.grid(True, axis="y")

    plt.suptitle("Investor Demographics Analysis",
                 fontsize=14, fontweight="bold", y=1.02)
    save("05_investor_demographics.png")


# CHART 6: Geographic Distribution
print("[6/15] Geographic Distribution ...")
state_col = next((c for c in tx.columns if "state" in c.lower()), None)
amt_col2  = next((c for c in tx.columns if "amount" in c.lower()), None)

if state_col and amt_col2:
    state_aum = tx.groupby(state_col)[amt_col2].sum().sort_values(ascending=True).tail(12)

    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(state_aum.index, state_aum.values, color=COLORS[0])
    ax.set_title("Total Investment Amount by State",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Total Amount (Rs.)")
    for bar, val in zip(bars, state_aum.values):
        ax.text(bar.get_width() * 1.01,
                bar.get_y() + bar.get_height() / 2,
                "Rs." + str(round(val / 1e7, 1)) + "Cr",
                va="center", fontsize=8)
    ax.grid(True, axis="x")
    save("06_geographic_distribution.png")


# CHART 7: Folio Count Growth
print("[7/15] Folio Count Growth ...")
print("  Folio columns: " + str(list(folio.columns)))

folio_col = next((c for c in folio.columns if "total" in c.lower() or "folio" in c.lower()), None)
date_col2 = next((c for c in folio.columns if "date" in c.lower() or "month" in c.lower() or "period" in c.lower()), None)

if folio_col:
    folio[folio_col] = pd.to_numeric(folio[folio_col], errors="coerce")
    fig, ax = plt.subplots(figsize=(12, 5))

    if date_col2:
        folio[date_col2] = pd.to_datetime(folio[date_col2], errors="coerce")
        folio_s = folio.dropna(subset=[folio_col, date_col2]).sort_values(date_col2)
        ax.plot(folio_s[date_col2], folio_s[folio_col],
                color="#4ef1a0", linewidth=2.5, marker="o", markersize=5)
        ax.fill_between(folio_s[date_col2], folio_s[folio_col],
                        alpha=0.2, color="#4ef1a0")
    else:
        ax.plot(range(len(folio)), folio[folio_col],
                color="#4ef1a0", linewidth=2.5, marker="o", markersize=5)

    ax.set_title("Mutual Fund Folio Count Growth (Crore)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Total Folios (Crore)")
    ax.grid(True)
    save("07_folio_count_growth.png")


# CHART 8: Correlation Matrix
print("[8/15] Correlation Matrix ...")
top10 = nav["amfi_code"].unique()[:10]
pivot_nav = nav[nav["amfi_code"].isin(top10)].pivot_table(
    index="date", columns="amfi_code", values="daily_return_pct"
).dropna()

code_name = funds.set_index("amfi_code")["scheme_name"].to_dict() if "scheme_name" in funds.columns else {}
pivot_nav.columns = [code_name.get(str(c), str(c))[:18] for c in pivot_nav.columns]

corr = pivot_nav.corr()
fig, ax = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, ax=ax, mask=mask, annot=True, fmt=".2f",
            cmap="coolwarm", center=0,
            linewidths=0.5, linecolor="#1a1d2e",
            annot_kws={"size": 8})
ax.set_title("NAV Return Correlation Matrix (Top 10 Funds)",
             fontsize=14, fontweight="bold", pad=15)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(rotation=0, fontsize=8)
save("08_correlation_matrix.png")


# CHART 9: Sector Allocation Donut
print("[9/15] Sector Allocation ...")
print("  Portfolio columns: " + str(list(port.columns)))

sector_col = next((c for c in port.columns if "sector" in c.lower()), None)
weight_col = next((c for c in port.columns if "weight" in c.lower() or "pct" in c.lower()), None)

if sector_col and weight_col:
    port[weight_col] = pd.to_numeric(port[weight_col], errors="coerce")
    sector_wt = port.groupby(sector_col)[weight_col].sum().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        sector_wt.values,
        labels=sector_wt.index,
        autopct="%1.1f%%",
        colors=COLORS * 2,
        startangle=90,
        pctdistance=0.75,
        wedgeprops={"width": 0.6, "edgecolor": "#0f1117", "linewidth": 2}
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Sector Allocation across Equity Fund Portfolios",
                 fontsize=14, fontweight="bold", pad=15)
    save("09_sector_allocation_donut.png")


# CHART 10: Risk vs Return Scatter
print("[10/15] Risk vs Return Scatter ...")

ret_col = next((c for c in perf_merged.columns if "return_3yr" in c.lower()), None)
std_col = next((c for c in perf_merged.columns if "std_dev" in c.lower()), None)
cat_col2 = "category" if "category" in perf_merged.columns else None

if ret_col and std_col:
    fig, ax = plt.subplots(figsize=(11, 7))

    if cat_col2:
        for i, cat_name in enumerate(perf_merged[cat_col2].dropna().unique()):
            sub = perf_merged[perf_merged[cat_col2] == cat_name]
            ax.scatter(sub[std_col], sub[ret_col],
                       label=cat_name, color=COLORS[i % len(COLORS)],
                       s=80, alpha=0.8, edgecolors="#0f1117", linewidth=0.5)
    else:
        ax.scatter(perf_merged[std_col], perf_merged[ret_col],
                   color=COLORS[0], s=80, alpha=0.8)

    ax.axhline(0, color="#666", linestyle="--", linewidth=0.8)
    ax.set_title("Risk vs Return - 3-Year CAGR vs Annualised Std Dev",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Risk (Annualised Std Dev %)")
    ax.set_ylabel("3-Year CAGR (%)")
    ax.legend(facecolor="#1a1d2e", edgecolor="#444", fontsize=9)
    ax.grid(True)
    save("10_risk_vs_return_scatter.png")


# CHART 11: Sharpe Ratio Rankings
print("[11/15] Sharpe Ratio Rankings ...")

sharpe_col  = next((c for c in perf_merged.columns if "sharpe" in c.lower()), None)
name_col    = "scheme_name" if "scheme_name" in perf_merged.columns else None
cat_col3    = "category"    if "category"    in perf_merged.columns else None

if sharpe_col:
    keep_cols = [sharpe_col]
    if name_col:
        keep_cols.append(name_col)
    if cat_col3:
        keep_cols.append(cat_col3)

    top_sharpe = perf_merged.nlargest(15, sharpe_col)[keep_cols].dropna()
    top_sharpe["short_name"] = (top_sharpe[name_col].str[:30]
                                if name_col else top_sharpe.index.astype(str))

    fig, ax = plt.subplots(figsize=(12, 7))
    bar_colors = []
    for _, row in top_sharpe.iterrows():
        c = row.get(cat_col3, "Equity") if cat_col3 else "Equity"
        idx = ["Equity", "Debt", "Hybrid"].index(c) if c in ["Equity","Debt","Hybrid"] else 0
        bar_colors.append(COLORS[idx % len(COLORS)])

    ax.barh(top_sharpe["short_name"][::-1],
            top_sharpe[sharpe_col][::-1],
            color=bar_colors[::-1])
    ax.set_title("Top 15 Funds by Sharpe Ratio",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Sharpe Ratio")
    ax.axvline(1, color="#f1c94e", linestyle="--",
               linewidth=1.2, label="Sharpe = 1 (Good)")
    ax.legend(facecolor="#1a1d2e", edgecolor="#444")
    ax.grid(True, axis="x")
    save("11_sharpe_ratio_rankings.png")


# CHART 12: Max Drawdown Comparison
print("[12/15] Max Drawdown Comparison ...")

dd_col   = next((c for c in perf_merged.columns if "drawdown" in c.lower()), None)
name_col2 = "scheme_name" if "scheme_name" in perf_merged.columns else None

if dd_col:
    keep_cols2 = [dd_col]
    if name_col2:
        keep_cols2.append(name_col2)

    dd = perf_merged.nsmallest(15, dd_col)[keep_cols2].dropna()
    dd["short_name"] = (dd[name_col2].str[:30]
                        if name_col2 else dd.index.astype(str))

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(dd["short_name"][::-1], dd[dd_col][::-1],
            color="#f14e7c", alpha=0.8)
    ax.set_title("Top 15 Funds by Maximum Drawdown",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Max Drawdown (%)")
    ax.grid(True, axis="x")
    save("12_max_drawdown_comparison.png")


# CHART 13: Monthly Transaction Volume
print("[13/15] Monthly Transaction Volume ...")

date_col3 = next((c for c in tx.columns if "date" in c.lower()), None)
amt_col3  = next((c for c in tx.columns if "amount" in c.lower()), None)

if date_col3 and amt_col3:
    tx[date_col3] = pd.to_datetime(tx[date_col3], errors="coerce")
    tx["month"] = tx[date_col3].dt.to_period("M").astype(str)
    monthly = tx.groupby("month")[amt_col3].sum().reset_index()
    monthly = monthly.sort_values("month").tail(24)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(monthly["month"], monthly[amt_col3],
           color="#4e9af1", alpha=0.8, width=0.7)
    ax.set_title("Monthly Transaction Volume (Last 24 Months)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Amount (Rs.)")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    ax.grid(True, axis="y")
    save("13_monthly_transaction_volume.png")


# CHART 14: Fund Category Distribution
print("[14/15] Fund Category Distribution ...")

if "category" in funds.columns:
    cat_counts = funds["category"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        cat_counts.values,
        labels=cat_counts.index,
        autopct="%1.1f%%",
        colors=COLORS[:len(cat_counts)],
        startangle=90,
        wedgeprops={"edgecolor": "#0f1117", "linewidth": 2}
    )
    ax.set_title("Fund Category Distribution (40 Schemes)",
                 fontsize=14, fontweight="bold", pad=15)
    save("14_fund_category_distribution.png")


# CHART 15: Benchmark Index Trend
print("[15/15] Benchmark Index Trend ...")
print("  Benchmark columns: " + str(list(bench.columns)))

idx_col   = next((c for c in bench.columns if "index" in c.lower() or "name" in c.lower() or "symbol" in c.lower()), None)
val_col   = next((c for c in bench.columns if "close" in c.lower() or "value" in c.lower() or "price" in c.lower()), None)
bdate_col = next((c for c in bench.columns if "date" in c.lower()), None)

if val_col and bdate_col:
    bench[bdate_col] = pd.to_datetime(bench[bdate_col], errors="coerce")
    bench[val_col]   = pd.to_numeric(bench[val_col], errors="coerce")

    fig, ax = plt.subplots(figsize=(14, 6))

    if idx_col:
        for i, idx_name in enumerate(bench[idx_col].dropna().unique()[:5]):
            sub = bench[bench[idx_col] == idx_name].sort_values(bdate_col).dropna(subset=[val_col])
            if sub.empty:
                continue
            sub_norm = sub[val_col] / sub[val_col].iloc[0] * 100
            ax.plot(sub[bdate_col], sub_norm,
                    label=str(idx_name),
                    color=COLORS[i % len(COLORS)], linewidth=1.8)
    else:
        bench_s = bench.sort_values(bdate_col).dropna(subset=[val_col])
        norm = bench_s[val_col] / bench_s[val_col].iloc[0] * 100
        ax.plot(bench_s[bdate_col], norm, color=COLORS[0], linewidth=1.8)

    ax.set_title("Benchmark Index Performance (Normalised to 100)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Date")
    ax.set_ylabel("Index Value (Base = 100)")
    ax.legend(facecolor="#1a1d2e", edgecolor="#444", fontsize=9)
    ax.grid(True)
    save("15_benchmark_index_trend.png")


# SUMMARY
print("\n" + "=" * 55)
print("  EDA Complete! Charts saved to reports/charts/")
charts = os.listdir(CHARTS_DIR)
print("  Total charts generated: " + str(len(charts)))
for c in sorted(charts):
    print("    - " + c)
print("=" * 55)