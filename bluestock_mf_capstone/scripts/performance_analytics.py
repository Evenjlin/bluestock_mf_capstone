"""
Bluestock Fintech Capstone - Day 4
Fund Performance Analytics - Returns, Risk Metrics, Scorecard
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Config ────────────────────────────────────
PROCESSED_DIR = "data/processed"
CHARTS_DIR    = "reports/charts"
OUTPUTS_DIR   = "data/processed"
os.makedirs(CHARTS_DIR, exist_ok=True)

RISK_FREE_RATE = 0.065   # RBI repo rate proxy 6.5%
TRADING_DAYS   = 252

def save(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight",
                facecolor="#0f1117")
    plt.close()
    print("  Saved chart: " + path)

# Style ─────────────────────────────────────
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
    "font.size"        : 10,
})
COLORS = ["#4e9af1","#f1c94e","#f17c4e","#4ef1a0",
          "#c44ef1","#f14e7c","#4ef1e8","#f1844e"]

# Load Data ─────────────────────────────────
print("=" * 60)
print("  Bluestock Fintech - Day 4: Performance Analytics")
print("=" * 60)

print("\nLoading datasets ...")
nav   = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav_history.csv"),
                    parse_dates=["date"])
funds = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"))
bench = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_benchmark_indices.csv"),
                    parse_dates=["date"])

nav["amfi_code"]   = nav["amfi_code"].astype(str).str.strip()
funds["amfi_code"] = funds["amfi_code"].astype(str).str.strip()
nav = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
print("Datasets loaded.\n")


# TASK 1: Compute Daily Returns
print("[1/7] Computing daily returns ...")

nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
nav = nav.dropna(subset=["daily_return"])

out = os.path.join(OUTPUTS_DIR, "returns_computed.csv")
nav.to_csv(out, index=False)
print("  Rows with returns : " + str(len(nav)))
print("  Saved: " + out)


# TASK 2: Compute CAGR
print("\n[2/7] Computing CAGR ...")

def compute_cagr(group, years):
    """Compute CAGR for a given number of years."""
    end_date   = group["date"].max()
    start_date = end_date - pd.DateOffset(years=years)
    subset = group[group["date"] >= start_date]
    if len(subset) < 30:
        return np.nan
    nav_start = subset["nav"].iloc[0]
    nav_end   = subset["nav"].iloc[-1]
    if nav_start <= 0:
        return np.nan
    actual_years = (subset["date"].iloc[-1] - subset["date"].iloc[0]).days / 365.25
    if actual_years <= 0:
        return np.nan
    return (nav_end / nav_start) ** (1 / actual_years) - 1

cagr_records = []
for code, group in nav.groupby("amfi_code"):
    group = group.sort_values("date")
    cagr_records.append({
        "amfi_code"    : code,
        "cagr_1yr_pct" : round(compute_cagr(group, 1) * 100, 2),
        "cagr_3yr_pct" : round(compute_cagr(group, 3) * 100, 2),
        "cagr_5yr_pct" : round(compute_cagr(group, 5) * 100, 2),
    })

cagr_df = pd.DataFrame(cagr_records)
cagr_df = cagr_df.merge(funds[["amfi_code","scheme_name","category"]]
                        if "scheme_name" in funds.columns
                        else funds[["amfi_code"]], on="amfi_code", how="left")

out = os.path.join(OUTPUTS_DIR, "cagr_report.csv")
cagr_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(cagr_df)))
print("  Sample CAGR (3yr):")
print(cagr_df[["amfi_code","cagr_3yr_pct"]].dropna().head(5).to_string(index=False))
print("  Saved: " + out)


# TASK 3: Compute Sharpe Ratio
print("\n[3/7] Computing Sharpe Ratio ...")

daily_rf = RISK_FREE_RATE / TRADING_DAYS

sharpe_records = []
for code, group in nav.groupby("amfi_code"):
    returns = group["daily_return"].dropna()
    if len(returns) < 30:
        continue
    excess  = returns - daily_rf
    std_dev = returns.std()
    if std_dev == 0:
        continue
    sharpe_ann = (excess.mean() / std_dev) * np.sqrt(TRADING_DAYS)
    sharpe_records.append({
        "amfi_code"   : code,
        "sharpe_ratio": round(sharpe_ann, 4),
        "ann_return"  : round(returns.mean() * TRADING_DAYS * 100, 2),
        "ann_std_dev" : round(std_dev * np.sqrt(TRADING_DAYS) * 100, 2),
    })

sharpe_df = pd.DataFrame(sharpe_records)
out = os.path.join(OUTPUTS_DIR, "sharpe_values.csv")
sharpe_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(sharpe_df)))
print("  Top 5 by Sharpe:")
print(sharpe_df.nlargest(5, "sharpe_ratio")[["amfi_code","sharpe_ratio"]].to_string(index=False))
print("  Saved: " + out)


# TASK 4: Compute Sortino Ratio
print("\n[4/7] Computing Sortino Ratio ...")

sortino_records = []
for code, group in nav.groupby("amfi_code"):
    returns = group["daily_return"].dropna()
    if len(returns) < 30:
        continue
    excess        = returns - daily_rf
    downside      = returns[returns < 0]
    downside_std  = downside.std()
    if downside_std == 0 or np.isnan(downside_std):
        continue
    sortino_ann = (excess.mean() / downside_std) * np.sqrt(TRADING_DAYS)
    sortino_records.append({
        "amfi_code"    : code,
        "sortino_ratio": round(sortino_ann, 4),
        "downside_std" : round(downside_std * np.sqrt(TRADING_DAYS) * 100, 2),
    })

sortino_df = pd.DataFrame(sortino_records)
out = os.path.join(OUTPUTS_DIR, "sortino_values.csv")
sortino_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(sortino_df)))
print("  Top 5 by Sortino:")
print(sortino_df.nlargest(5, "sortino_ratio")[["amfi_code","sortino_ratio"]].to_string(index=False))
print("  Saved: " + out)


# TASK 5: Compute Alpha & Beta vs Benchmark
print("\n[5/7] Computing Alpha and Beta ...")

# Detect benchmark columns
date_col  = next((c for c in bench.columns if "date" in c.lower()), None)
val_col   = next((c for c in bench.columns if "close" in c.lower() or "value" in c.lower()), None)
idx_col   = next((c for c in bench.columns if "index" in c.lower() or "name" in c.lower()), None)

print("  Benchmark columns: " + str(list(bench.columns)))

alpha_beta_records = []

if date_col and val_col:
    # Use Nifty 100 or first available index as benchmark
    if idx_col:
        available = bench[idx_col].dropna().unique()
        print("  Available indices: " + str(list(available)))
        bm_name = next((x for x in available
                        if "nifty 100" in str(x).lower() or
                           "nifty100" in str(x).lower() or
                           "nifty 50" in str(x).lower()), available[0])
        bm_data = bench[bench[idx_col] == bm_name].copy()
        print("  Using benchmark: " + str(bm_name))
    else:
        bm_data = bench.copy()

    bm_data[date_col] = pd.to_datetime(bm_data[date_col], errors="coerce")
    bm_data[val_col]  = pd.to_numeric(bm_data[val_col], errors="coerce")
    bm_data = bm_data.dropna(subset=[date_col, val_col]).sort_values(date_col)
    bm_data["bm_return"] = bm_data[val_col].pct_change()
    bm_data = bm_data.dropna(subset=["bm_return"])
    bm_data = bm_data.set_index(date_col)["bm_return"]

    for code, group in nav.groupby("amfi_code"):
        group = group.set_index("date")["daily_return"].dropna()

        # Align fund and benchmark dates
        aligned = pd.concat([group, bm_data], axis=1, join="inner").dropna()
        aligned.columns = ["fund", "benchmark"]

        if len(aligned) < 60:
            continue

        x = aligned["benchmark"].values
        y = aligned["fund"].values
        n = len(x)
        slope     = (n * np.sum(x*y) - np.sum(x)*np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        intercept = (np.sum(y) - slope * np.sum(x)) / n
        y_pred    = slope * x + intercept
        ss_res    = np.sum((y - y_pred)**2)
        ss_tot    = np.sum((y - np.mean(y))**2)
        r_val     = np.sqrt(1 - ss_res/ss_tot) if ss_tot != 0 else 0

        beta  = round(slope, 4)
        alpha = round(intercept * TRADING_DAYS * 100, 4)  # annualised %

        alpha_beta_records.append({
            "amfi_code": code,
            "alpha"    : alpha,
            "beta"     : beta,
            "r_squared": round(r_val ** 2, 4),
        })

alpha_beta_df = pd.DataFrame(alpha_beta_records)
out = os.path.join(OUTPUTS_DIR, "alpha_beta.csv")
alpha_beta_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(alpha_beta_df)))
print("  Sample Alpha/Beta:")
print(alpha_beta_df.head(5).to_string(index=False))
print("  Saved: " + out)


# TASK 6: Compute Maximum Drawdown
print("\n[6/7] Computing Maximum Drawdown ...")

drawdown_records = []
for code, group in nav.groupby("amfi_code"):
    group = group.sort_values("date")
    nav_series    = group["nav"]
    rolling_max   = nav_series.cummax()
    drawdown      = (nav_series - rolling_max) / rolling_max * 100
    max_dd        = drawdown.min()
    try:
        min_idx = drawdown.values.argmin()
        max_dd_date = group["date"].iloc[min_idx]
    except:
        max_dd_date = None

    drawdown_records.append({
        "amfi_code"      : code,
        "max_drawdown_pct": round(max_dd, 4),
        "max_dd_date"    : max_dd_date,
    })

drawdown_df = pd.DataFrame(drawdown_records)
out = os.path.join(OUTPUTS_DIR, "max_drawdown.csv")
drawdown_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(drawdown_df)))
print("  Worst drawdowns:")
print(drawdown_df.nsmallest(5, "max_drawdown_pct")[["amfi_code","max_drawdown_pct"]].to_string(index=False))
print("  Saved: " + out)


# TASK 7: Build Fund Scorecard
print("\n[7/7] Building Fund Scorecard ...")

# Merge all metrics
scorecard = funds[["amfi_code"] +
                  [c for c in ["scheme_name","fund_house","category",
                               "expense_ratio_pct","risk_category"]
                   if c in funds.columns]].copy()

scorecard = scorecard.merge(cagr_df[["amfi_code","cagr_3yr_pct"]], on="amfi_code", how="left")
scorecard = scorecard.merge(sharpe_df[["amfi_code","sharpe_ratio","ann_std_dev"]], on="amfi_code", how="left")
scorecard = scorecard.merge(sortino_df[["amfi_code","sortino_ratio"]], on="amfi_code", how="left")
scorecard = scorecard.merge(alpha_beta_df[["amfi_code","alpha","beta"]], on="amfi_code", how="left")
scorecard = scorecard.merge(drawdown_df[["amfi_code","max_drawdown_pct"]], on="amfi_code", how="left")

# Composite Score (0-100)
# 30% 3yr return rank + 25% Sharpe rank + 20% Alpha rank
# + 15% Expense ratio rank (inverse) + 10% Max DD rank (inverse)
def rank_pct(series, ascending=True):
    """Rank series and normalise to 0-100."""
    return series.rank(ascending=ascending, pct=True) * 100

scorecard["score_return"]  = rank_pct(scorecard["cagr_3yr_pct"])
scorecard["score_sharpe"]  = rank_pct(scorecard["sharpe_ratio"])
scorecard["score_alpha"]   = rank_pct(scorecard["alpha"])
scorecard["score_expense"] = rank_pct(scorecard["expense_ratio_pct"], ascending=False)
scorecard["score_drawdown"]= rank_pct(scorecard["max_drawdown_pct"],  ascending=False)

scorecard["composite_score"] = (
    0.30 * scorecard["score_return"]  +
    0.25 * scorecard["score_sharpe"]  +
    0.20 * scorecard["score_alpha"]   +
    0.15 * scorecard["score_expense"] +
    0.10 * scorecard["score_drawdown"]
).round(2)

scorecard = scorecard.sort_values("composite_score", ascending=False).reset_index(drop=True)
scorecard["rank"] = scorecard.index + 1

out = os.path.join(OUTPUTS_DIR, "fund_scorecard.csv")
scorecard.to_csv(out, index=False)

print("  Fund Scorecard (Top 10):")
display_cols = ["rank","amfi_code","composite_score","cagr_3yr_pct","sharpe_ratio","alpha"]
if "scheme_name" in scorecard.columns:
    display_cols.insert(2, "scheme_name")
print(scorecard[display_cols].head(10).to_string(index=False))
print("  Saved: " + out)


# CHART A: Benchmark Comparison
print("\nGenerating benchmark comparison chart ...")

selected_codes = ["125497","119551","120503","118632","119092"]
fig, ax = plt.subplots(figsize=(14, 6))

# Plot top 5 funds
for i, code in enumerate(selected_codes):
    df_f = nav[nav["amfi_code"] == code].sort_values("date")
    if df_f.empty:
        continue
    start_nav = df_f["nav"].iloc[0]
    norm = df_f["nav"] / start_nav * 100
    label = code
    if "scheme_name" in funds.columns:
        name = funds[funds["amfi_code"] == code]["scheme_name"].values
        if len(name) > 0:
            label = str(name[0])[:22]
    ax.plot(df_f["date"], norm, label=label,
            color=COLORS[i], linewidth=1.5)

# Plot benchmark
if date_col and val_col and not alpha_beta_df.empty:
    if idx_col:
        bm_plot = bench[bench[idx_col] == bm_name].copy()
    else:
        bm_plot = bench.copy()
    bm_plot[date_col] = pd.to_datetime(bm_plot[date_col], errors="coerce")
    bm_plot[val_col]  = pd.to_numeric(bm_plot[val_col], errors="coerce")
    bm_plot = bm_plot.dropna().sort_values(date_col)
    bm_norm = bm_plot[val_col] / bm_plot[val_col].iloc[0] * 100
    ax.plot(bm_plot[date_col], bm_norm,
            label="Benchmark", color="#ffffff",
            linewidth=2, linestyle="--")

ax.set_title("Top 5 Funds vs Benchmark (Normalised to 100)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Date")
ax.set_ylabel("Normalised Value (Base = 100)")
ax.legend(facecolor="#1a1d2e", edgecolor="#444", fontsize=8)
ax.grid(True)
save("16_benchmark_comparison.png")


# CHART B: Fund Scorecard Bar Chart
print("Generating scorecard chart ...")
top15 = scorecard.head(15).copy()
if "scheme_name" in top15.columns:
    top15["label"] = top15["scheme_name"].str[:28]
else:
    top15["label"] = top15["amfi_code"]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top15["label"][::-1],
               top15["composite_score"][::-1],
               color=COLORS[0], alpha=0.85)
for bar, val in zip(bars, top15["composite_score"][::-1]):
    ax.text(bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            str(round(val, 1)), va="center", fontsize=9)
ax.set_title("Fund Scorecard - Top 15 by Composite Score (0-100)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Composite Score")
ax.grid(True, axis="x")
save("17_fund_scorecard.png")


# CHART C: Alpha Distribution
print("Generating alpha distribution chart ...")
alpha_plot = alpha_beta_df.merge(
    funds[["amfi_code","scheme_name"]] if "scheme_name" in funds.columns
    else funds[["amfi_code"]], on="amfi_code", how="left"
).sort_values("alpha", ascending=False)

if "scheme_name" in alpha_plot.columns:
    alpha_plot["label"] = alpha_plot["scheme_name"].str[:25]
else:
    alpha_plot["label"] = alpha_plot["amfi_code"]

fig, ax = plt.subplots(figsize=(12, 8))
colors_alpha = ["#4ef1a0" if a > 0 else "#f14e7c"
                for a in alpha_plot["alpha"]]
ax.barh(alpha_plot["label"][::-1],
        alpha_plot["alpha"][::-1],
        color=colors_alpha[::-1], alpha=0.85)
ax.axvline(0, color="#ffffff", linewidth=1.2, linestyle="--")
ax.set_title("Alpha vs Benchmark (Annualised %) - All Funds",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Alpha (%)")
ax.grid(True, axis="x")
save("18_alpha_distribution.png")


# SUMMARY
print("\n" + "=" * 60)
print("  Day 4 Complete!")
print("  Output files saved to data/processed/:")
for f in ["returns_computed.csv","cagr_report.csv","sharpe_values.csv",
          "sortino_values.csv","alpha_beta.csv","max_drawdown.csv",
          "fund_scorecard.csv"]:
    path = os.path.join(OUTPUTS_DIR, f)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print("    " + f + " - " + str(len(df)) + " rows")
print("  Charts: 16_benchmark_comparison.png, 17_fund_scorecard.png, 18_alpha_distribution.png")
print("=" * 60)