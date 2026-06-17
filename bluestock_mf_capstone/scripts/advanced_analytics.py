"""
Bluestock Fintech Capstone - Day 6
Advanced Analytics + Risk Metrics
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

PROCESSED_DIR = "data/processed"
CHARTS_DIR    = "reports/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor" : "#FFFFFF",
    "axes.facecolor"   : "#FAFBFC",
    "axes.edgecolor"   : "#E2E8F0",
    "axes.labelcolor"  : "#475569",
    "xtick.color"      : "#94A3B8",
    "ytick.color"      : "#94A3B8",
    "text.color"       : "#334155",
    "grid.color"       : "#F1F5F9",
    "grid.linestyle"   : "--",
    "grid.alpha"       : 0.8,
    "font.family"      : "DejaVu Sans",
    "font.size"        : 10,
})

BLUE   = "#0052CC"
GREEN  = "#10B981"
RED    = "#EF4444"
AMBER  = "#F59E0B"
PURPLE = "#8B5CF6"

def save(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  Saved: " + path)

print("=" * 60)
print("  Bluestock Fintech - Day 6: Advanced Analytics")
print("=" * 60)

# ── Load ──────────────────────────────────────
print("\nLoading datasets ...")
nav = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav_history.csv"),
                  parse_dates=["date"])
fund = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"))
tx   = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"))
port = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_portfolio_holdings.csv"))
sc   = pd.read_csv(os.path.join(PROCESSED_DIR, "fund_scorecard.csv"))

nav["amfi_code"]  = nav["amfi_code"].astype(str).str.strip()
fund["amfi_code"] = fund["amfi_code"].astype(str).str.strip()
sc["amfi_code"]   = sc["amfi_code"].astype(str).str.strip()

nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
print("Datasets loaded.\n")


# TASK 1: Historical VaR (95%) and CVaR
# ─────────────────────────────────────────────
print("[1/6] Computing VaR and CVaR ...")

var_records = []
for code, group in nav.groupby("amfi_code"):
    returns = group["daily_return"].dropna()
    if len(returns) < 60:
        continue

    var_95  = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()
    var_99  = np.percentile(returns, 1)
    cvar_99 = returns[returns <= var_99].mean()

    var_records.append({
        "amfi_code"   : code,
        "var_95_pct"  : round(var_95 * 100, 4),
        "cvar_95_pct" : round(cvar_95 * 100, 4),
        "var_99_pct"  : round(var_99 * 100, 4),
        "cvar_99_pct" : round(cvar_99 * 100, 4),
        "n_days"      : len(returns),
    })

var_df = pd.DataFrame(var_records)
var_df = var_df.merge(
    fund[["amfi_code"] + [c for c in ["scheme_name","category"] if c in fund.columns]],
    on="amfi_code", how="left"
)

out = os.path.join(PROCESSED_DIR, "var_cvar_report.csv")
var_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(var_df)))
print("  Worst VaR (95%) :")
print(var_df.nsmallest(5,"var_95_pct")[["amfi_code","var_95_pct","cvar_95_pct"]].to_string(index=False))
print("  Saved: " + out)

# Chart 19 — VaR vs CVaR
fig, ax = plt.subplots(figsize=(13, 6))
x      = range(len(var_df))
lbl_col = "scheme_name" if "scheme_name" in var_df.columns else "amfi_code"
labels  = var_df[lbl_col].astype(str).str[:20].tolist()

ax.bar(x, var_df["var_95_pct"],  color=AMBER,  alpha=0.8, label="VaR 95%",  width=0.35,
       align="center")
ax.bar([i+0.37 for i in x], var_df["cvar_95_pct"], color=RED, alpha=0.8,
       label="CVaR 95%", width=0.35, align="center")
ax.set_xticks([i+0.18 for i in x])
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
ax.set_title("Historical VaR (95%) vs CVaR (95%) — All Funds",
             fontsize=13, fontweight="bold", pad=12)
ax.set_ylabel("Daily Loss % (negative = bad)")
ax.axhline(0, color="#E2E8F0", linewidth=0.8)
ax.legend(facecolor="white", edgecolor="#E2E8F0")
ax.grid(True, axis="y")
plt.tight_layout()
save("19_var_cvar_comparison.png")


# TASK 2: Rolling 90-day Sharpe Ratio
# ─────────────────────────────────────────────
print("\n[2/6] Computing Rolling 90-day Sharpe ...")

RISK_FREE_DAILY = 0.065 / 252
SELECTED = ["125497","119551","120503","118632","119092"]
LABELS   = {
    "125497":"HDFC Top 100",
    "119551":"SBI Bluechip",
    "120503":"ICICI Bluechip",
    "118632":"Nippon LargeCap",
    "119092":"Axis Bluechip",
}
COLORS_ = [BLUE, GREEN, AMBER, PURPLE, RED]

rolling_records = []
fig, ax = plt.subplots(figsize=(14, 6))

for i, code in enumerate(SELECTED):
    group = nav[nav["amfi_code"] == code].sort_values("date").copy()
    if group.empty:
        continue
    r = group["daily_return"].dropna()

    roll_mean  = r.rolling(90).mean()
    roll_std   = r.rolling(90).std()
    roll_sharpe = (roll_mean - RISK_FREE_DAILY) / roll_std * np.sqrt(252)
    roll_sharpe = roll_sharpe.bfill()

    dates = group.loc[r.index, "date"] if "date" in group.columns else group["date"]

    ax.plot(group["date"].values[-len(roll_sharpe):],
            roll_sharpe.values,
            label=LABELS.get(code, code),
            color=COLORS_[i], linewidth=1.8)

    rolling_records.append({
        "amfi_code"           : code,
        "scheme_name"         : LABELS.get(code, code),
        "latest_rolling_sharpe": round(float(roll_sharpe.dropna().iloc[-1]), 4) if len(roll_sharpe.dropna())>0 else None
    })

ax.axhline(y=1,  color="#94A3B8", linestyle="--", linewidth=1, label="Sharpe = 1")
ax.axhline(y=0,  color="#E2E8F0", linestyle="-",  linewidth=0.8)
ax.set_title("Rolling 90-Day Sharpe Ratio — 5 Selected Funds",
             fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Date")
ax.set_ylabel("Rolling Sharpe Ratio (annualised)")
ax.legend(facecolor="white", edgecolor="#E2E8F0", fontsize=9)
ax.grid(True)
plt.tight_layout()
save("20_rolling_sharpe_chart.png")

rolling_df = pd.DataFrame(rolling_records)
out = os.path.join(PROCESSED_DIR, "rolling_sharpe.csv")
rolling_df.to_csv(out, index=False)
print("  Funds processed : " + str(len(rolling_df)))
print("  Saved: " + out)


# TASK 3: Investor Cohort Analysis
# ─────────────────────────────────────────────
print("\n[3/6] Investor Cohort Analysis ...")

date_col = next((c for c in tx.columns if "date" in c.lower()), None)
amt_col  = next((c for c in tx.columns if "amount" in c.lower()), None)
inv_col  = "investor_id" if "investor_id" in tx.columns else None
age_col  = next((c for c in tx.columns if "age" in c.lower()), None)
type_col = next((c for c in tx.columns if "type" in c.lower()), None)

if date_col and amt_col and inv_col:
    tx[date_col] = pd.to_datetime(tx[date_col], errors="coerce")
    tx[amt_col]  = pd.to_numeric(tx[amt_col],  errors="coerce")

    # First transaction year per investor
    first_tx = tx.groupby(inv_col)[date_col].min().dt.year.rename("cohort_year")
    tx_cohort = tx.merge(first_tx.reset_index(), on=inv_col, how="left")

    cohort = tx_cohort.groupby("cohort_year").agg(
        investors        = (inv_col,  "nunique"),
        total_invested   = (amt_col,  "sum"),
        avg_sip_amount   = (amt_col,  "mean"),
        total_txns       = (inv_col,  "count"),
    ).reset_index()
    cohort["avg_invested_per_investor"] = (
        cohort["total_invested"] / cohort["investors"]
    ).round(2)

    out = os.path.join(PROCESSED_DIR, "cohort_analysis.csv")
    cohort.to_csv(out, index=False)
    print("  Cohort breakdown:")
    print(cohort.to_string(index=False))
    print("  Saved: " + out)

    # Chart 21 — Cohort
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax_obj, col, title, color in [
        (axes[0], "investors",    "Unique Investors by Cohort",       BLUE),
        (axes[1], "avg_sip_amount","Avg SIP Amount by Cohort (Rs.)",  GREEN),
        (axes[2], "total_txns",   "Total Transactions by Cohort",     PURPLE),
    ]:
        ax_obj.bar(cohort["cohort_year"].astype(str),
                   cohort[col], color=color, alpha=0.8)
        ax_obj.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax_obj.set_xlabel("Cohort Year")
        ax_obj.grid(True, axis="y")
        for bar in ax_obj.patches:
            ax_obj.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() * 1.01,
                        f"{bar.get_height():,.0f}",
                        ha="center", va="bottom", fontsize=9, color="#475569")

    plt.suptitle("Investor Cohort Analysis — Behaviour by First Transaction Year",
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    save("21_cohort_analysis.png")
else:
    print("  Skipped — required columns not found")


# TASK 4: SIP Continuity Analysis
# ─────────────────────────────────────────────
print("\n[4/6] SIP Continuity Analysis ...")

if date_col and amt_col and inv_col and type_col:
    sip_tx = tx[tx[type_col] == "Sip"].copy()
    sip_tx = sip_tx.sort_values([inv_col, date_col])

    sip_tx["prev_date"] = sip_tx.groupby(inv_col)[date_col].shift(1)
    sip_tx["gap_days"]  = (sip_tx[date_col] - sip_tx["prev_date"]).dt.days

    continuity = sip_tx.groupby(inv_col).agg(
        num_sips    = (amt_col,   "count"),
        avg_gap_days= ("gap_days","mean"),
        avg_amount  = (amt_col,   "mean"),
        total_sip   = (amt_col,   "sum"),
    ).reset_index()

    continuity = continuity[continuity["num_sips"] >= 6]
    continuity["at_risk"] = continuity["avg_gap_days"] > 35
    continuity["avg_gap_days"] = continuity["avg_gap_days"].round(1)

    out = os.path.join(PROCESSED_DIR, "sip_continuity.csv")
    continuity.to_csv(out, index=False)

    at_risk_count  = continuity["at_risk"].sum()
    healthy_count  = (~continuity["at_risk"]).sum()
    print("  Investors with 6+ SIPs : " + str(len(continuity)))
    print("  At-risk (gap > 35 days): " + str(at_risk_count))
    print("  Healthy SIP investors  : " + str(healthy_count))
    print("  Saved: " + out)

    # Chart 22 — SIP continuity
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Pie
    axes[0].pie([healthy_count, at_risk_count],
                labels=["Healthy SIP", "At Risk (gap>35d)"],
                colors=[GREEN, RED], autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor":"white","linewidth":2})
    axes[0].set_title("SIP Continuity — Healthy vs At-Risk",
                      fontsize=11, fontweight="bold", pad=8)

    # Gap distribution
    axes[1].hist(continuity["avg_gap_days"].dropna(), bins=25,
                 color=BLUE, alpha=0.75, edgecolor="white")
    axes[1].axvline(x=35, color=RED, linestyle="--", linewidth=1.5,
                    label="At-risk threshold (35 days)")
    axes[1].axvline(x=30, color=GREEN, linestyle="--", linewidth=1.5,
                    label="Ideal monthly gap (30 days)")
    axes[1].set_title("Distribution of Avg Gap Between SIPs",
                      fontsize=11, fontweight="bold", pad=8)
    axes[1].set_xlabel("Avg Gap Days")
    axes[1].set_ylabel("Number of Investors")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, axis="y")

    plt.suptitle("SIP Continuity Analysis — 5,000 Investors",
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    save("22_sip_continuity.png")
else:
    print("  Skipped — required columns not found")


# TASK 5: Fund Recommendation Engine
# ─────────────────────────────────────────────
print("\n[5/6] Fund Recommendation Engine ...")

def recommend_funds(risk_appetite, top_n=3):
    """
    Recommend top N funds based on investor risk appetite.
    Risk appetite: Low / Moderate / High
    """
    risk_map = {
        "Low"      : ["Low", "Moderate"],
        "Moderate" : ["Moderate"],
        "High"     : ["High", "Very High"],
    }

    allowed_risk = risk_map.get(risk_appetite, ["Moderate"])

    # Join scorecard with fund master
    sc_fund = sc.merge(
        fund[["amfi_code"] + [c for c in ["scheme_name","fund_house",
              "category","risk_category","expense_ratio_pct"] if c in fund.columns]],
        on="amfi_code", how="left"
    )

    if "risk_category" in sc_fund.columns:
        filtered = sc_fund[sc_fund["risk_category"].isin(allowed_risk)]
    else:
        filtered = sc_fund

    if "composite_score" in filtered.columns:
        top = filtered.nlargest(top_n, "composite_score")
    else:
        top = filtered.head(top_n)

    return top

print("\n  --- Fund Recommendations ---")
for appetite in ["Low", "Moderate", "High"]:
    recs = recommend_funds(appetite)
    print(f"\n  Risk Appetite: {appetite}")
    print(f"  {'Fund':<35} {'Category':<12} {'Score':>8} {'3yr CAGR':>10}")
    print(f"  {'-'*70}")
    for _,r in recs.iterrows():
        nm  = str(r.get("scheme_name","N/A"))[:34]
        cat = str(r.get("category","N/A"))[:11]
        sc_ = r.get("composite_score",0) or 0
        rt  = r.get("cagr_3yr_pct",0) or 0
        print(f"  {nm:<35} {cat:<12} {sc_:>8.1f} {rt:>9.2f}%")

# Save recommender output
all_recs = []
for appetite in ["Low","Moderate","High"]:
    recs = recommend_funds(appetite, top_n=5)
    recs = recs.copy()
    recs["risk_appetite"] = appetite
    all_recs.append(recs)

recs_df = pd.concat(all_recs, ignore_index=True)
out = os.path.join(PROCESSED_DIR, "fund_recommendations.csv")
recs_df.to_csv(out, index=False)
print("\n  Saved: " + out)

# Chart 23 — Recommendations
fig, axes = plt.subplots(1, 3, figsize=(15, 6))
for i, (appetite, color) in enumerate([("Low",GREEN),("Moderate",BLUE),("High",RED)]):
    recs = recommend_funds(appetite, top_n=5)
    ax   = axes[i]
    lbl_col = "scheme_name" if "scheme_name" in recs.columns else "amfi_code"
    labels  = recs[lbl_col].astype(str).str[:22].tolist()
    scores  = recs["composite_score"].tolist() if "composite_score" in recs.columns else [0]*5

    bars = ax.barh(labels[::-1], scores[::-1], color=color, alpha=0.8)
    ax.set_title(f"{appetite} Risk Appetite\nTop 5 Recommended Funds",
                 fontsize=10, fontweight="bold", pad=8)
    ax.set_xlabel("Composite Score")
    ax.set_xlim(0, 110)
    for bar, val in zip(bars, scores[::-1]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{val:.0f}", va="center", fontsize=9, color="#475569")
    ax.grid(True, axis="x")

plt.suptitle("Fund Recommendation Engine — By Risk Appetite",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
save("23_fund_recommendations.png")


# TASK 6: Sector HHI — Concentration Risk
# ─────────────────────────────────────────────
print("\n[6/6] Sector HHI Concentration Analysis ...")

sec_col = next((c for c in port.columns if "sector" in c.lower()), None)
wt_col  = next((c for c in port.columns if "weight" in c.lower() or "pct" in c.lower()), None)
fc_col  = next((c for c in port.columns if "amfi" in c.lower() or "code" in c.lower()), None)

if sec_col and wt_col and fc_col:
    port[wt_col] = pd.to_numeric(port[wt_col], errors="coerce")

    hhi_records = []
    for code, group in port.groupby(fc_col):
        weights  = group[wt_col].dropna()
        weights  = weights / weights.sum() * 100  # normalise to %
        hhi      = (weights ** 2).sum()
        n_sectors = group[sec_col].nunique()

        hhi_records.append({
            "amfi_code"   : str(code),
            "hhi_score"   : round(hhi, 2),
            "n_sectors"   : n_sectors,
            "concentration": "High" if hhi > 2500 else "Moderate" if hhi > 1500 else "Low",
        })

    hhi_df = pd.DataFrame(hhi_records)
    hhi_df = hhi_df.merge(
        fund[["amfi_code"] + [c for c in ["scheme_name"] if c in fund.columns]],
        on="amfi_code", how="left"
    ).sort_values("hhi_score", ascending=False)

    out = os.path.join(PROCESSED_DIR, "sector_hhi.csv")
    hhi_df.to_csv(out, index=False)
    print("  Funds analysed  : " + str(len(hhi_df)))
    print("  High concentration  : " + str((hhi_df["concentration"]=="High").sum()))
    print("  Moderate concentration: " + str((hhi_df["concentration"]=="Moderate").sum()))
    print("  Low concentration   : " + str((hhi_df["concentration"]=="Low").sum()))
    print("  Saved: " + out)

    # Chart 24 — HHI
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # Bar chart
    lbl_col = "scheme_name" if "scheme_name" in hhi_df.columns else "amfi_code"
    hhi_df["label"] = hhi_df[lbl_col].astype(str).str[:24]
    clrs = [RED if c=="High" else AMBER if c=="Moderate" else GREEN
            for c in hhi_df["concentration"]]

    axes[0].barh(hhi_df["label"][::-1], hhi_df["hhi_score"][::-1],
                 color=clrs[::-1], alpha=0.8)
    axes[0].axvline(x=2500, color=RED, linestyle="--", linewidth=1.5,
                    label="High (>2500)")
    axes[0].axvline(x=1500, color=AMBER, linestyle="--", linewidth=1.5,
                    label="Moderate (>1500)")
    axes[0].set_title("HHI Score by Fund\n(Higher = More Concentrated)",
                      fontsize=11, fontweight="bold", pad=8)
    axes[0].set_xlabel("HHI Score")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, axis="x")

    # Pie
    conc_counts = hhi_df["concentration"].value_counts()
    axes[1].pie(
        conc_counts.values,
        labels=conc_counts.index,
        colors=[GREEN if c=="Low" else AMBER if c=="Moderate" else RED
                for c in conc_counts.index],
        autopct="%1.0f%%", startangle=90,
        wedgeprops={"edgecolor":"white","linewidth":2}
    )
    axes[1].set_title("Concentration Risk Distribution\nacross Portfolio Funds",
                      fontsize=11, fontweight="bold", pad=8)

    plt.suptitle("Herfindahl-Hirschman Index (HHI) — Sector Concentration Risk",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    save("24_sector_hhi.png")
else:
    print("  Skipped — portfolio columns not detected")


# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Day 6 Complete!")
print("\n  Output files:")
for f in ["var_cvar_report.csv","rolling_sharpe.csv","cohort_analysis.csv",
          "sip_continuity.csv","fund_recommendations.csv","sector_hhi.csv"]:
    path = os.path.join(PROCESSED_DIR, f)
    if os.path.exists(path):
        df_t = pd.read_csv(path)
        print(f"    {f} — {len(df_t)} rows")

print("\n  Charts saved:")
for c in ["19_var_cvar_comparison.png","20_rolling_sharpe_chart.png",
          "21_cohort_analysis.png","22_sip_continuity.png",
          "23_fund_recommendations.png","24_sector_hhi.png"]:
    print(f"    {c}")
print("=" * 60)