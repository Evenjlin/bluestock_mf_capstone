"""
app.py
Bluestock Fintech Capstone - Day 5
Clean, Organized Mutual Fund Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Bluestock | MF Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family:'Inter',sans-serif; box-sizing:border-box; }
.stApp { background:#F0F4F8; }
.block-container { padding:0 !important; max-width:100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background:#0A1628 !important;
    border-right:none !important;
    width:240px !important;
}
section[data-testid="stSidebar"] > div { padding:0 !important; }

/* ── Logo ── */
.logo-area {
    padding:20px 16px 16px;
    border-bottom:1px solid #0F2040;
    background:#071020;
}
.logo-row { display:flex; align-items:center; gap:10px; margin-bottom:4px; }
.logo-icon-box {
    width:38px; height:38px;
    background:linear-gradient(135deg,#0052CC,#0A7AFF);
    border-radius:8px;
    display:flex; align-items:center; justify-content:center;
}
.logo-bars { display:flex; align-items:flex-end; gap:2px; height:20px; }
.lb { width:4px; border-radius:2px 2px 0 0; background:rgba(255,255,255,0.9); }
.logo-text-block { line-height:1; }
.logo-name {
    font-size:1rem; font-weight:800; color:#FFFFFF;
    letter-spacing:2px; text-transform:uppercase;
    display:flex; align-items:baseline; gap:0;
}
.logo-tm  { font-size:0.4rem; color:rgba(255,255,255,0.4); vertical-align:super; margin-left:1px; }
.logo-dot { color:#0A7AFF; font-size:1rem; line-height:1; }
.logo-in  { font-size:0.65rem; color:rgba(255,255,255,0.35); font-weight:400; }
.logo-sub { font-size:0.58rem; color:#1A4A7A; text-transform:uppercase;
            letter-spacing:1.5px; margin-top:4px; }

/* ── Nav label ── */
.nav-label {
    font-size:0.55rem; font-weight:700; color:#0F2A4A;
    text-transform:uppercase; letter-spacing:2px;
    padding:14px 16px 6px;
}

/* ── Info box ── */
.sb-info {
    margin:8px 12px;
    background:#071020;
    border:1px solid #0F2040;
    border-radius:8px;
    padding:12px;
    font-size:0.6rem;
    color:#1A4A7A;
    line-height:1.8;
}
.sb-info b { color:#2A6AAA; }

/* ── Top bar ── */
.topbar {
    background:#FFFFFF;
    border-bottom:1px solid #E2E8F0;
    padding:0 24px;
    height:56px;
    display:flex; align-items:center; justify-content:space-between;
    position:sticky; top:0; z-index:100;
}
.topbar-title {
    font-size:1rem; font-weight:600; color:#1A2A3A;
    display:flex; align-items:center; gap:8px;
}
.topbar-breadcrumb { font-size:0.72rem; color:#94A3B8; margin-top:1px; }
.topbar-right { display:flex; align-items:center; gap:16px; }
.tb-badge {
    font-size:0.6rem; font-weight:600; padding:4px 10px;
    border-radius:20px; letter-spacing:0.5px;
}
.tb-live  { background:#DCFCE7; color:#166534; border:1px solid #BBF7D0; }
.tb-date  { font-size:0.65rem; color:#94A3B8; font-family:monospace; }

/* ── Page content area ── */
.page-body { padding:20px 24px; background:#F0F4F8; min-height:100vh; }

/* ── Section header ── */
.section-hd {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:14px;
}
.section-title {
    font-size:0.8rem; font-weight:700; color:#334155;
    display:flex; align-items:center; gap:8px;
    text-transform:uppercase; letter-spacing:0.5px;
}
.section-dot { width:4px; height:16px; background:#0052CC;
               border-radius:2px; flex-shrink:0; }
.section-sub { font-size:0.65rem; color:#94A3B8; font-weight:400;
               text-transform:none; letter-spacing:0; margin-left:12px; }

/* ── KPI cards ── */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:20px; }
.kpi-card {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:16px 18px;
    position:relative; overflow:hidden;
    transition:box-shadow .2s, transform .15s;
    cursor:default;
}
.kpi-card:hover { box-shadow:0 4px 20px rgba(0,82,204,0.1); transform:translateY(-2px); }
.kpi-accent { position:absolute; top:0;left:0;bottom:0; width:3px; border-radius:12px 0 0 12px; }
.ka-blue   { background:linear-gradient(180deg,#0052CC,#0A7AFF); }
.ka-green  { background:linear-gradient(180deg,#059669,#10B981); }
.ka-amber  { background:linear-gradient(180deg,#D97706,#F59E0B); }
.ka-purple { background:linear-gradient(180deg,#7C3AED,#8B5CF6); }
.ka-red    { background:linear-gradient(180deg,#DC2626,#EF4444); }
.kpi-label { font-size:0.62rem; color:#94A3B8; text-transform:uppercase;
             letter-spacing:1px; font-weight:600; margin-bottom:6px; }
.kpi-value { font-size:1.5rem; font-weight:700; color:#1E293B; letter-spacing:-0.5px; }
.kpi-delta { font-size:0.68rem; margin-top:6px; font-weight:500;
             display:flex; align-items:center; gap:4px; }
.delta-up   { color:#059669; }
.delta-down { color:#DC2626; }
.delta-flat { color:#D97706; }
.kpi-icon { position:absolute; top:14px; right:14px;
            font-size:1.4rem; opacity:0.15; }

/* ── Chart card ── */
.chart-card {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:18px 18px 10px;
    margin-bottom:16px;
    box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.cc-title {
    font-size:0.75rem; font-weight:700; color:#334155;
    text-transform:uppercase; letter-spacing:0.5px;
    padding-bottom:12px; border-bottom:1px solid #F1F5F9;
    margin-bottom:4px;
    display:flex; align-items:center; gap:8px;
}
.cc-dot { width:3px; height:14px; border-radius:2px;
          background:#0052CC; flex-shrink:0; }
.cc-sub { font-size:0.62rem; color:#94A3B8; font-weight:400;
          text-transform:none; letter-spacing:0; }

/* ── Two-col grid ── */
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.three-col { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }

/* ── Fund table card ── */
.fund-row {
    display:flex; align-items:center; justify-content:space-between;
    padding:10px 14px;
    border-bottom:1px solid #F1F5F9;
    transition:background .15s;
}
.fund-row:hover { background:#F8FAFC; }
.fund-row:last-child { border-bottom:none; }
.fr-rank { font-size:0.65rem; font-weight:700; color:#94A3B8; width:24px; }
.fr-info { flex:1; margin:0 12px; }
.fr-name { font-size:0.78rem; font-weight:600; color:#1E293B; }
.fr-meta { font-size:0.62rem; color:#94A3B8; margin-top:1px; }
.fr-cat  { font-size:0.6rem; padding:2px 7px; border-radius:10px; margin-right:6px; }
.cat-eq  { background:#DBEAFE; color:#1D4ED8; }
.cat-dt  { background:#D1FAE5; color:#065F46; }
.cat-hy  { background:#FEF3C7; color:#92400E; }
.fr-metrics { text-align:right; }
.fr-ret { font-size:0.9rem; font-weight:700; }
.fr-ret-up { color:#059669; }
.fr-ret-dn { color:#DC2626; }
.fr-sh  { font-size:0.62rem; color:#94A3B8; margin-top:1px; }

/* ── Info strip ── */
.info-strip {
    background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
    border:1px solid #BFDBFE;
    border-radius:10px;
    padding:12px 16px;
    margin-bottom:16px;
    display:flex; align-items:center; gap:12px;
}
.is-icon { font-size:1.2rem; }
.is-text { font-size:0.72rem; color:#1D4ED8; font-weight:500; }
.is-sub  { font-size:0.62rem; color:#3B82F6; margin-top:2px; }

/* ── Metric pill ── */
.metric-pills { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }
.mpill {
    background:#F8FAFC; border:1px solid #E2E8F0;
    border-radius:8px; padding:8px 12px;
    min-width:90px; text-align:center;
}
.mp-lbl { font-size:0.58rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.8px; }
.mp-val { font-size:0.9rem; font-weight:700; color:#1E293B; margin-top:2px; }

/* ── Streamlit overrides ── */
div[data-testid="stMetricContainer"],
div[data-testid="metric-container"] {
    background:#FFFFFF !important;
    border:1px solid #E2E8F0 !important;
    border-radius:10px !important;
    padding:14px 16px !important;
    box-shadow:0 1px 3px rgba(0,0,0,0.04) !important;
}
div[data-testid="stMetricValue"] {
    color:#1E293B !important; font-weight:700 !important; font-size:1.2rem !important;
}
div[data-testid="stMetricLabel"] {
    color:#94A3B8 !important; font-size:0.6rem !important;
    text-transform:uppercase; letter-spacing:0.8px;
}
.stRadio > div { gap:2px !important; }
.stRadio > div > label {
    background:#071020 !important; border:1px solid #0F2040 !important;
    border-radius:8px !important; padding:9px 14px !important;
    font-size:0.78rem !important; color:#2A5A8A !important;
    margin-bottom:2px; display:block; width:100%;
    transition:all .15s;
}
.stRadio > div > label:hover {
    background:#0A1E3A !important;
    border-color:#0052CC !important; color:#A0C4E0 !important;
}
div[data-testid="stSelectbox"] > div > div {
    background:#071020 !important; border-color:#0F2040 !important;
    color:#A0C4E0 !important; border-radius:8px !important;
    font-size:0.8rem !important;
}
.stMultiSelect > div > div {
    background:#FFFFFF !important; border-color:#E2E8F0 !important;
    border-radius:8px !important; color:#1E293B !important;
}
.stMultiSelect span { color:#1E293B !important; }
div[data-testid="stSelectbox"] > label,
.stMultiSelect > label,
.stRadio > label { color:#2A5A8A !important; font-size:0.65rem !important; }
hr { border-color:#E2E8F0 !important; }
h1,h2,h3 { color:#1E293B !important; }
.stDataFrame { border-radius:10px; overflow:hidden; }
.stDataFrame th { background:#F8FAFC !important; color:#64748B !important;
                  font-size:0.65rem !important; text-transform:uppercase; }
</style>
""", unsafe_allow_html=True)

# ── Plotly light theme ────────────────────────
PT = dict(
    template="plotly_white",
    paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
    font=dict(family="Inter", color="#64748B", size=11),
    margin=dict(l=8,r=8,t=32,b=8),
    xaxis=dict(gridcolor="#F1F5F9",linecolor="#E2E8F0",
               zeroline=False,tickfont=dict(size=10,color="#94A3B8")),
    yaxis=dict(gridcolor="#F1F5F9",linecolor="#E2E8F0",
               zeroline=False,tickfont=dict(size=10,color="#94A3B8")),
    legend=dict(bgcolor="#FFFFFF",bordercolor="#E2E8F0",
                borderwidth=1,font=dict(size=10)),
    colorway=["#0052CC","#059669","#D97706","#7C3AED",
               "#DC2626","#0891B2","#DB2777","#65A30D"]
)

def th(fig, h=340, title=""):
    fig.update_layout(**PT, height=h)
    if title:
        fig.update_layout(title=dict(
            text=title,
            font=dict(size=11,color="#64748B",weight="normal"),
            x=0, pad=dict(l=4,b=4)
        ))
    return fig

def gcol(df,*kws):
    for k in kws:
        c = next((x for x in df.columns if k in x.lower()),None)
        if c: return c
    return None

P = "data/processed"

@st.cache_data
def load():
    nav  = pd.read_csv(f"{P}/clean_nav_history.csv",     parse_dates=["date"])
    fund = pd.read_csv(f"{P}/clean_fund_master.csv")
    aum  = pd.read_csv(f"{P}/clean_aum_by_fund_house.csv")
    sip  = pd.read_csv(f"{P}/clean_monthly_sip_inflows.csv")
    tx   = pd.read_csv(f"{P}/clean_transactions.csv")
    sc   = pd.read_csv(f"{P}/fund_scorecard.csv")
    bm   = pd.read_csv(f"{P}/clean_benchmark_indices.csv")
    ab   = pd.read_csv(f"{P}/alpha_beta.csv")
    fol  = pd.read_csv(f"{P}/clean_industry_folio_count.csv")
    cat  = pd.read_csv(f"{P}/clean_category_inflows.csv")
    sha  = pd.read_csv(f"{P}/sharpe_values.csv")
    mdd  = pd.read_csv(f"{P}/max_drawdown.csv")
    srt  = pd.read_csv(f"{P}/sortino_values.csv")
    cagr = pd.read_csv(f"{P}/cagr_report.csv")
    port = pd.read_csv(f"{P}/clean_portfolio_holdings.csv")

    for df in [nav,fund,sc,ab,sha,mdd,srt,cagr]:
        if "amfi_code" in df.columns:
            df["amfi_code"] = df["amfi_code"].astype(str).str.strip()

    mc = ["amfi_code"]+[c for c in ["scheme_name","category","fund_house",
          "risk_category","expense_ratio_pct","sub_category",
          "benchmark","fund_manager","plan"] if c in fund.columns]
    if "scheme_name" not in sc.columns:
        sc = sc.merge(fund[mc],on="amfi_code",how="left")

    master = sc.copy()
    for df2,cols in [
        (sha, ["amfi_code","sharpe_ratio","ann_return","ann_std_dev"]),
        (srt, ["amfi_code","sortino_ratio"]),
        (ab,  ["amfi_code","alpha","beta","r_squared"]),
        (mdd, ["amfi_code","max_drawdown_pct"]),
        (cagr,["amfi_code","cagr_1yr_pct","cagr_3yr_pct","cagr_5yr_pct"])
    ]:
        avail = [c for c in cols if c in df2.columns]
        new_c = [c for c in avail if c not in master.columns or c=="amfi_code"]
        if len(new_c)>1:
            master = master.merge(df2[new_c],on="amfi_code",how="left")

    return nav,fund,aum,sip,tx,sc,bm,ab,fol,cat,sha,mdd,srt,cagr,port,master

nav,fund,aum,sip,tx,sc,bm,ab,fol,cat,sha,mdd,srt,cagr,port,master = load()


# ── Sidebar ───────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='logo-area'>
      <div class='logo-row'>
        <div class='logo-icon-box'>
          <div class='logo-bars'>
            <div class='lb' style='height:7px'></div>
            <div class='lb' style='height:13px'></div>
            <div class='lb' style='height:9px'></div>
            <div class='lb' style='height:18px'></div>
            <div class='lb' style='height:11px'></div>
          </div>
        </div>
        <div class='logo-text-block'>
          <div class='logo-name'>
            BLUESTOCK<span class='logo-tm'>TM</span><span class='logo-dot'>.</span><span class='logo-in'>in</span>
          </div>
        </div>
      </div>
      <div class='logo-sub'>Mutual Fund Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='nav-label'>Menu</div>", unsafe_allow_html=True)
    page = st.radio("", [
        "🏠  Market Overview",
        "📈  Fund Performance",
        "💼  Portfolio & Holdings",
        "👥  Investor Insights",
        "📊  SIP Trends",
        "🔍  Fund Explorer",
    ], label_visibility="collapsed")

    st.markdown("<div class='nav-label'>Filters</div>", unsafe_allow_html=True)
    fh_list  = ["All"]+sorted(fund["fund_house"].dropna().unique().tolist()) if "fund_house" in fund.columns else ["All"]
    cat_list = ["All"]+sorted(fund["category"].dropna().unique().tolist())   if "category"  in fund.columns else ["All"]
    sfh = st.selectbox("Fund House", fh_list,  label_visibility="visible")
    scl = st.selectbox("Category",   cat_list, label_visibility="visible")

    st.markdown("""
    <div class='sb-info'>
      <b>Data Sources</b><br>
      AMFI India · mfapi.in<br>
      NSE India · BSE India<br><br>
      <b>Coverage</b><br>
      40 Schemes · 10 AMCs<br>
      Jan 2022 – May 2026<br><br>
      <b>Intern</b><br>
      Evenjlin · Jun 2026<br><br>
      <span style='color:#0A1E35;font-size:0.55rem'>
      Educational use only.<br>Not financial advice.
      </span>
    </div>
    """, unsafe_allow_html=True)


def flt(df):
    if sfh!="All" and "fund_house" in df.columns: df=df[df["fund_house"]==sfh]
    if scl!="All" and "category"   in df.columns: df=df[df["category"]  ==scl]
    return df

PAGE_TITLES = {
    "Market Overview":   ("Market Overview",   "Indian MF Industry · AMFI India · December 2025"),
    "Fund Performance":  ("Fund Performance",  "Risk-Adjusted Returns · CAGR · Sharpe · Alpha · Scorecard"),
    "Portfolio & Holdings":("Portfolio & Holdings","Sector Allocation · Top Stock Holdings · Concentration Analysis"),
    "Investor Insights": ("Investor Insights", "Demographics · Geographic Distribution · Transaction Behaviour"),
    "SIP Trends":        ("SIP Trends",        "Monthly Inflows · YoY Growth · Benchmark Indices · Category Flows"),
    "Fund Explorer":     ("Fund Explorer",     "Deep-dive any scheme · NAV history · Peer comparison · Rank"),
}
pg_key = next((k for k in PAGE_TITLES if k in page),"Market Overview")
pg_title, pg_sub = PAGE_TITLES[pg_key]

# ── Top bar ───────────────────────────────────
st.markdown(f"""
<div class='topbar'>
  <div>
    <div class='topbar-title'>📊 {pg_title}</div>
    <div class='topbar-breadcrumb'>{pg_sub}</div>
  </div>
  <div class='topbar-right'>
    <span class='tb-live tb-badge'>● Live Data</span>
    <span class='tb-date'>AMFI · Dec 2025</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='padding:16px 24px 0'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 1 — MARKET OVERVIEW
# ══════════════════════════════════════════════
if "Market" in page:

    # KPI row
    st.markdown("""
    <div class='kpi-grid'>
      <div class='kpi-card'>
        <div class='kpi-accent ka-blue'></div>
        <div class='kpi-icon'>🏦</div>
        <div class='kpi-label'>Industry AUM</div>
        <div class='kpi-value'>Rs. 81L Cr</div>
        <div class='kpi-delta delta-up'>↑ +12% YoY &nbsp;·&nbsp; Oct peak Rs.79.9L Cr</div>
      </div>
      <div class='kpi-card'>
        <div class='kpi-accent ka-green'></div>
        <div class='kpi-icon'>💰</div>
        <div class='kpi-label'>SIP Inflow Dec 2025</div>
        <div class='kpi-value'>Rs. 31,002 Cr</div>
        <div class='kpi-delta delta-up'>↑ All-time High &nbsp;·&nbsp; +22% YoY</div>
      </div>
      <div class='kpi-card'>
        <div class='kpi-accent ka-amber'></div>
        <div class='kpi-icon'>📁</div>
        <div class='kpi-label'>Total Folios</div>
        <div class='kpi-value'>26.12 Crore</div>
        <div class='kpi-delta delta-up'>↑ +18% YoY &nbsp;·&nbsp; 1,908 schemes</div>
      </div>
      <div class='kpi-card'>
        <div class='kpi-accent ka-purple'></div>
        <div class='kpi-icon'>🔄</div>
        <div class='kpi-label'>Active SIP Accounts</div>
        <div class='kpi-value'>9.35 Crore</div>
        <div class='kpi-delta delta-up'>↑ Systematic investing at scale</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Row 1: AUM bar + Category pie
    c1,c2 = st.columns([3,2], gap="medium")

    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>AUM by Fund House <span class='cc-sub'>Peak quarterly AUM in Rs. Crore</span></div>", unsafe_allow_html=True)
        ac_ = gcol(aum,"aum"); fhc = gcol(aum,"fund","house","amc")
        if ac_ and fhc:
            aum[ac_] = pd.to_numeric(aum[ac_],errors="coerce")
            top = aum.groupby(fhc)[ac_].max().sort_values().tail(10)
            fig = go.Figure(go.Bar(
                x=top.values, y=top.index, orientation="h",
                marker=dict(
                    color=list(range(len(top))),
                    colorscale=[[0,"#DBEAFE"],[0.5,"#3B82F6"],[1,"#0052CC"]],
                    line=dict(width=0)
                ),
                text=[f"Rs.{v:,.0f}" for v in top.values],
                textposition="outside", textfont=dict(size=9,color="#64748B")
            ))
            th(fig,320)
            fig.update_layout(yaxis=dict(tickfont=dict(size=10,color="#475569")))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Category Mix <span class='cc-sub'>40 schemes</span></div>", unsafe_allow_html=True)
        if "category" in fund.columns:
            cc = fund["category"].value_counts()
            fig = go.Figure(go.Pie(
                values=cc.values, labels=cc.index, hole=0.6,
                marker=dict(
                    colors=["#0052CC","#059669","#D97706","#7C3AED"],
                    line=dict(color="#FFFFFF",width=3)
                ),
                textfont=dict(size=11), textinfo="label+percent"
            ))
            th(fig,320)
            fig.add_annotation(
                text="<b>40</b><br><span style='font-size:10px;color:#94A3B8'>FUNDS</span>",
                x=0.5,y=0.5,showarrow=False,font=dict(size=14,color="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 2: Folio growth + Risk grades
    c1,c2 = st.columns([3,2], gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Folio Count Growth <span class='cc-sub'>India's MF penetration journey · 2022–2026</span></div>", unsafe_allow_html=True)
        fcc = gcol(fol,"total","folio"); dcc = gcol(fol,"month","date","period")
        if fcc and dcc:
            fol[dcc] = pd.to_datetime(fol[dcc],errors="coerce")
            fol[fcc] = pd.to_numeric(fol[fcc],errors="coerce")
            fs = fol.dropna(subset=[fcc,dcc]).sort_values(dcc)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fs[dcc], y=fs[fcc], mode="lines+markers",
                fill="tozeroy", fillcolor="rgba(0,82,204,0.05)",
                line=dict(color="#0052CC",width=2.5),
                marker=dict(size=6,color="#0052CC",line=dict(color="#FFFFFF",width=2)),
                hovertemplate="<b>%{y:.2f} Cr Folios</b><br>%{x|%b %Y}<extra></extra>"
            ))
            th(fig,280)
            fig.update_layout(yaxis_title="Folios (Crore)")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Risk Grade Breakdown</div>", unsafe_allow_html=True)
        if "risk_category" in fund.columns:
            rc = fund["risk_category"].value_counts()
            cm = {"Low":"#059669","Moderate":"#D97706","High":"#EA580C","Very High":"#DC2626"}
            fig = go.Figure(go.Bar(
                x=rc.index, y=rc.values,
                marker_color=[cm.get(r,"#0052CC") for r in rc.index],
                text=rc.values, textposition="outside",
                textfont=dict(color="#64748B",size=11)
            ))
            th(fig,280,"Schemes by SEBI Risk Grade")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Top funds quick view
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cc-title'><div class='cc-dot'></div>Top 10 Funds by Composite Score</div>", unsafe_allow_html=True)
    top10 = flt(master.copy()).head(10)
    cat_cls = {"Equity":"cat-eq","Debt":"cat-dt","Hybrid":"cat-hy"}
    for i,r in top10.iterrows():
        nm  = str(r.get("scheme_name",""))[:38]
        fh  = str(r.get("fund_house",""))[:22]
        ct  = str(r.get("category",""))
        ret = r.get("cagr_3yr_pct",None)
        sh  = r.get("sharpe_ratio",None)
        sc2 = r.get("composite_score",None)
        rnk = int(r.get("rank",i+1))
        ret_str = f"{ret:+.1f}%" if ret is not None and not np.isnan(ret) else "N/A"
        sh_str  = f"Sharpe {sh:.2f}" if sh  is not None and not np.isnan(sh)  else ""
        sc_str  = f"Score {sc2:.0f}" if sc2 is not None and not np.isnan(sc2) else ""
        ret_cls = "fr-ret-up" if (ret or 0)>=0 else "fr-ret-dn"
        cc_cls  = cat_cls.get(ct,"cat-eq")
        st.markdown(f"""
        <div class='fund-row'>
          <div class='fr-rank'>#{rnk}</div>
          <div class='fr-info'>
            <div class='fr-name'>{nm}</div>
            <div class='fr-meta'>
              <span class='fr-cat {cc_cls}'>{ct}</span>{fh}
            </div>
          </div>
          <div class='fr-metrics'>
            <div class='fr-ret {ret_cls}'>{ret_str} (3yr)</div>
            <div class='fr-sh'>{sh_str} &nbsp; {sc_str}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 2 — FUND PERFORMANCE
# ══════════════════════════════════════════════
elif "Performance" in page:
    mf = flt(master.copy())
    rc_ = gcol(mf,"cagr_3yr"); shc = gcol(mf,"sharpe")
    alc = gcol(mf,"alpha");    ddc = gcol(mf,"drawdown")
    src = gcol(mf,"sortino")

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    if rc_:  c1.metric("Best 3yr CAGR",    f"{mf[rc_].max():.1f}%",  f"Avg {mf[rc_].mean():.1f}%")
    if shc:  c2.metric("Best Sharpe Ratio",f"{mf[shc].max():.2f}",   f"Avg {mf[shc].mean():.2f}")
    if alc:  c3.metric("Best Alpha",       f"{mf[alc].max():.1f}%",  "vs NIFTY100 benchmark")
    if ddc:  c4.metric("Min Max Drawdown", f"{mf[ddc].max():.1f}%",  f"Worst {mf[ddc].min():.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Scorecard
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cc-title'><div class='cc-dot'></div>Fund Scorecard <span class='cc-sub'>Composite score: 30% return + 25% Sharpe + 20% Alpha + 15% Expense + 10% Drawdown</span></div>", unsafe_allow_html=True)
    show = [c for c in ["rank","scheme_name","fund_house","category","composite_score",
                         "cagr_1yr_pct","cagr_3yr_pct","cagr_5yr_pct","sharpe_ratio",
                         "sortino_ratio","alpha","beta","max_drawdown_pct",
                         "expense_ratio_pct"] if c in mf.columns]
    disp = mf[show].head(40).copy()
    disp.columns = [c.replace("_"," ").title() for c in disp.columns]
    st.dataframe(disp, use_container_width=True, height=380, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Row: Risk/Return + Sharpe bar
    c1,c2 = st.columns([3,2],gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Risk vs Return <span class='cc-sub'>Bubble size = composite score</span></div>", unsafe_allow_html=True)
        stdc = gcol(mf,"std_dev","ann_std")
        nc   = "scheme_name" if "scheme_name" in mf.columns else "amfi_code"
        catc = "category" if "category" in mf.columns else None
        if rc_ and stdc:
            pdf = mf.dropna(subset=[rc_,stdc])
            fig = go.Figure()
            cc_ = {"Equity":"#0052CC","Debt":"#059669","Hybrid":"#D97706"}
            for cn in (pdf[catc].dropna().unique() if catc else ["All"]):
                sub = pdf[pdf[catc]==cn] if catc else pdf
                sz  = sub["composite_score"]/4+8 if "composite_score" in sub.columns else 12
                fig.add_trace(go.Scatter(
                    x=sub[stdc], y=sub[rc_], mode="markers", name=str(cn),
                    marker=dict(size=sz,color=cc_.get(cn,"#7C3AED"),
                                line=dict(color="#FFFFFF",width=1.5),opacity=0.8),
                    text=sub[nc].astype(str).str[:30],
                    hovertemplate="<b>%{text}</b><br>Risk: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>"
                ))
            fig.add_hline(y=0,line_dash="dot",line_color="#E2E8F0",line_width=1.5)
            th(fig,360)
            fig.update_layout(xaxis_title="Annualised Std Dev (%)",
                              yaxis_title="3-Year CAGR (%)")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Top Funds — Sharpe Ratio</div>", unsafe_allow_html=True)
        sm = sha.merge(fund[["amfi_code"]+[c for c in ["scheme_name","category"] if c in fund.columns]],
                       on="amfi_code",how="left")
        sm = flt(sm)
        ts = sm.nlargest(10,"sharpe_ratio")
        lbl = "scheme_name" if "scheme_name" in ts.columns else "amfi_code"
        ts["label"] = ts[lbl].astype(str).str[:22]
        fig = go.Figure(go.Bar(
            y=ts["label"][::-1], x=ts["sharpe_ratio"][::-1], orientation="h",
            marker=dict(
                color=ts["sharpe_ratio"][::-1],
                colorscale=[[0,"#DBEAFE"],[0.5,"#3B82F6"],[1,"#0052CC"]],
                line=dict(width=0)
            ),
            text=[f"{v:.2f}" for v in ts["sharpe_ratio"][::-1]],
            textposition="outside",textfont=dict(size=9,color="#64748B")
        ))
        fig.add_vline(x=1,line_dash="dash",line_color="#D97706",line_width=1.5,
                      annotation=dict(text="≥1 Good",font=dict(color="#D97706",size=9)))
        th(fig,360)
        fig.update_layout(yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # NAV comparison
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cc-title'><div class='cc-dot'></div>NAV Comparison <span class='cc-sub'>Normalised to 100 at start — select up to 6 funds</span></div>", unsafe_allow_html=True)
    fl2 = fund["scheme_name"].dropna().tolist() if "scheme_name" in fund.columns else []
    sel = st.multiselect("Select funds", fl2, default=fl2[:4] if len(fl2)>=4 else fl2, max_selections=6)
    if sel:
        fig = go.Figure()
        cls_ = ["#0052CC","#059669","#D97706","#7C3AED","#DC2626","#0891B2"]
        for i,fn in enumerate(sel):
            cd = fund[fund["scheme_name"]==fn]["amfi_code"].values
            if len(cd)==0: continue
            nf = nav[nav["amfi_code"]==str(cd[0])].sort_values("date")
            if nf.empty: continue
            norm = nf["nav"]/nf["nav"].iloc[0]*100
            fig.add_trace(go.Scatter(
                x=nf["date"], y=norm, name=str(fn)[:28],
                line=dict(color=cls_[i%6],width=2),
                hovertemplate="%{fullData.name}<br>%{x|%d %b %Y}<br>%{y:.1f}<extra></extra>"
            ))
        th(fig,360)
        fig.update_layout(xaxis_title="Date",yaxis_title="Normalised Value (Base=100)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Alpha + Beta side by side
    c1,c2 = st.columns(2,gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Alpha Distribution <span class='cc-sub'>vs NIFTY100</span></div>", unsafe_allow_html=True)
        am = ab.merge(fund[["amfi_code"]+[c for c in ["scheme_name"] if c in fund.columns]],
                      on="amfi_code",how="left").sort_values("alpha",ascending=False)
        lbl2 = "scheme_name" if "scheme_name" in am.columns else "amfi_code"
        am["label"] = am[lbl2].astype(str).str[:22]
        fig = go.Figure(go.Bar(
            y=am["label"][::-1], x=am["alpha"][::-1], orientation="h",
            marker=dict(color=["#059669" if v>0 else "#DC2626" for v in am["alpha"][::-1]],
                        opacity=0.8, line=dict(width=0)),
            text=[f"{v:+.1f}%" for v in am["alpha"][::-1]],
            textposition="outside",textfont=dict(size=8,color="#64748B")
        ))
        fig.add_vline(x=0,line_color="#E2E8F0",line_width=1.5)
        th(fig,380)
        fig.update_layout(yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Beta Distribution <span class='cc-sub'>Market sensitivity vs NIFTY100</span></div>", unsafe_allow_html=True)
        if "beta" in ab.columns:
            fig = go.Figure(go.Histogram(
                x=ab["beta"].dropna(), nbinsx=20,
                marker=dict(color="#7C3AED",opacity=0.7,line=dict(color="#FFFFFF",width=1))
            ))
            fig.add_vline(x=1,line_dash="dash",line_color="#D97706",line_width=1.5,
                          annotation=dict(text="β=1",font=dict(color="#D97706",size=9)))
            th(fig,380)
            fig.update_layout(xaxis_title="Beta",yaxis_title="Number of Funds")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 3 — PORTFOLIO & HOLDINGS
# ══════════════════════════════════════════════
elif "Portfolio" in page:
    sec_c = gcol(port,"sector"); wt_c  = gcol(port,"weight","pct")
    stk_c = gcol(port,"stock","symbol","name"); fc2 = gcol(port,"amfi","code")

    c1,c2,c3 = st.columns(3)
    c1.metric("Total Holdings",  f"{len(port):,}")
    c2.metric("Unique Sectors",  f"{port[sec_c].nunique()}" if sec_c else "N/A")
    c3.metric("Unique Stocks",   f"{port[stk_c].nunique()}" if stk_c else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2 = st.columns([2,3],gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Sector Allocation</div>", unsafe_allow_html=True)
        if sec_c and wt_c:
            port[wt_c] = pd.to_numeric(port[wt_c],errors="coerce")
            sw = port.groupby(sec_c)[wt_c].sum().sort_values(ascending=False).head(10)
            fig = go.Figure(go.Pie(
                values=sw.values, labels=sw.index, hole=0.52,
                marker=dict(line=dict(color="#FFFFFF",width=3)),
                textfont=dict(size=10), textinfo="label+percent", sort=True
            ))
            th(fig,360)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Sector Weight Bar <span class='cc-sub'>Aggregate across all equity funds</span></div>", unsafe_allow_html=True)
        if sec_c and wt_c:
            sw2 = port.groupby(sec_c)[wt_c].sum().sort_values(ascending=False).head(12)
            fig = go.Figure(go.Bar(
                x=sw2.index, y=sw2.values,
                marker=dict(
                    color=list(range(len(sw2))),
                    colorscale=[[0,"#DBEAFE"],[0.5,"#3B82F6"],[1,"#0052CC"]],
                    line=dict(width=0)
                ),
                text=[f"{v:.1f}%" for v in sw2.values],
                textposition="outside",textfont=dict(size=9,color="#64748B")
            ))
            th(fig,360)
            fig.update_layout(xaxis=dict(tickangle=-35,tickfont=dict(size=9)),
                              yaxis_title="Total Weight (%)")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Top stocks
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cc-title'><div class='cc-dot'></div>Top 20 Stock Holdings <span class='cc-sub'>Aggregate weight across all equity fund portfolios</span></div>", unsafe_allow_html=True)
    if stk_c and wt_c:
        ts2 = port.groupby(stk_c)[wt_c].sum().sort_values(ascending=False).head(20)
        fig = go.Figure(go.Bar(
            x=ts2.index, y=ts2.values,
            marker=dict(color="#0052CC",opacity=0.75,line=dict(width=0)),
            text=[f"{v:.1f}%" for v in ts2.values],
            textposition="outside",textfont=dict(size=8,color="#64748B")
        ))
        th(fig,300)
        fig.update_layout(xaxis=dict(tickangle=-45,tickfont=dict(size=9)),
                          yaxis_title="Aggregate Weight (%)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Fund-specific holdings
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cc-title'><div class='cc-dot'></div>Fund-wise Holdings Explorer</div>", unsafe_allow_html=True)
    if fc2:
        fund_codes = port[fc2].dropna().unique().tolist()
        fund_names = []
        for cd in fund_codes:
            nm = fund[fund["amfi_code"]==str(cd)]["scheme_name"].values
            fund_names.append(str(nm[0]) if len(nm)>0 else str(cd))
        sel_fn = st.selectbox("Select equity fund", fund_names)
        idx2   = fund_names.index(sel_fn)
        sel_cd = str(fund_codes[idx2])
        port_f = port[port[fc2].astype(str)==sel_cd]
        if not port_f.empty and sec_c and wt_c and stk_c:
            c1,c2 = st.columns([2,3],gap="medium")
            with c1:
                fig = go.Figure(go.Pie(
                    values=port_f[wt_c].values,
                    labels=port_f[stk_c].astype(str),
                    hole=0.48,
                    marker=dict(line=dict(color="#FFFFFF",width=2)),
                    textfont=dict(size=9), textinfo="label+percent"
                ))
                th(fig,320,str(sel_fn)[:30])
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                dp = port_f[[stk_c,sec_c,wt_c]].sort_values(wt_c,ascending=False)
                dp.columns = ["Stock","Sector","Weight (%)"]
                st.dataframe(dp, use_container_width=True, height=320, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 4 — INVESTOR INSIGHTS
# ══════════════════════════════════════════════
elif "Investor" in page:
    sc2 = gcol(tx,"state"); ac2 = gcol(tx,"age")
    tc2 = gcol(tx,"type");  am2 = gcol(tx,"amount")
    tr2 = gcol(tx,"tier");  gc2 = gcol(tx,"gender")
    pm2 = gcol(tx,"payment","mode")

    # Filters in a row
    c1,c2,c3,c4 = st.columns(4)
    sts = ["All"]+sorted(tx[sc2].dropna().unique().tolist()) if sc2 else ["All"]
    ags = ["All"]+sorted(tx[ac2].dropna().unique().tolist()) if ac2 else ["All"]
    trs = ["All"]+sorted(tx[tr2].dropna().unique().tolist()) if tr2 else ["All"]
    tpc = ["All"]+sorted(tx[tc2].dropna().unique().tolist()) if tc2 else ["All"]
    ss  = c1.selectbox("State",       sts)
    sa  = c2.selectbox("Age Group",   ags)
    st3 = c3.selectbox("City Tier",   trs)
    stp = c4.selectbox("Tx Type",     tpc)

    txf = tx.copy()
    if ss !="All" and sc2: txf=txf[txf[sc2]==ss]
    if sa !="All" and ac2: txf=txf[txf[ac2]==sa]
    if st3!="All" and tr2: txf=txf[txf[tr2]==st3]
    if stp!="All" and tc2: txf=txf[txf[tc2]==stp]

    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Transactions",    f"{len(txf):,}")
    if am2:
        c2.metric("Total Invested",  f"Rs.{txf[am2].sum()/1e7:.1f} Cr")
        c3.metric("Avg Transaction", f"Rs.{txf[am2].mean():,.0f}")
    c4.metric("Unique Investors",f"{txf['investor_id'].nunique():,}" if "investor_id" in txf.columns else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1
    c1,c2,c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Transaction Type Split</div>", unsafe_allow_html=True)
        if tc2 and am2:
            td = txf.groupby(tc2)[am2].sum()
            fig = go.Figure(go.Pie(
                values=td.values, labels=td.index, hole=0.55,
                marker=dict(colors=["#0052CC","#059669","#DC2626"],
                            line=dict(color="#FFFFFF",width=3)),
                textfont=dict(size=11), textinfo="label+percent"
            ))
            th(fig,300)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>T30 vs B30 Cities</div>", unsafe_allow_html=True)
        if tr2 and am2:
            trd = txf.groupby(tr2)[am2].sum()
            fig = go.Figure(go.Pie(
                values=trd.values, labels=trd.index, hole=0.55,
                marker=dict(colors=["#0052CC","#D97706"],
                            line=dict(color="#FFFFFF",width=3)),
                textfont=dict(size=11), textinfo="label+percent"
            ))
            th(fig,300)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Payment Mode</div>", unsafe_allow_html=True)
        if pm2 and am2:
            pmd = txf.groupby(pm2)[am2].count().sort_values(ascending=False)
            fig = go.Figure(go.Bar(
                x=pmd.index, y=pmd.values,
                marker=dict(color=["#0052CC","#059669","#D97706","#7C3AED"],
                            line=dict(width=0)),
                text=pmd.values,textposition="outside",
                textfont=dict(size=10,color="#64748B")
            ))
            th(fig,300)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 2
    c1,c2 = st.columns(2,gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Investment by State <span class='cc-sub'>Top 12 states by total investment</span></div>", unsafe_allow_html=True)
        if sc2 and am2:
            sd = txf.groupby(sc2)[am2].sum().sort_values().tail(12)
            fig = go.Figure(go.Bar(
                x=sd.values, y=sd.index, orientation="h",
                marker=dict(
                    color=list(range(len(sd))),
                    colorscale=[[0,"#DBEAFE"],[1,"#0052CC"]],
                    line=dict(width=0)
                ),
                text=[f"Rs.{v/1e6:.1f}M" for v in sd.values],
                textposition="outside",textfont=dict(size=9,color="#64748B")
            ))
            th(fig,380)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Age Group & Gender Analysis</div>", unsafe_allow_html=True)
        if gc2 and am2 and ac2:
            gg = txf.groupby([ac2,gc2])[am2].sum().unstack(fill_value=0)
            fig = go.Figure()
            for i,g in enumerate(gg.columns):
                fig.add_trace(go.Bar(
                    x=gg.index, y=gg[g], name=str(g),
                    marker=dict(color=["#0052CC","#DB2777"][i%2],
                                opacity=0.8, line=dict(width=0))
                ))
            th(fig,380)
            fig.update_layout(barmode="group",
                              xaxis_title="Age Group",yaxis_title="Total Investment (Rs.)")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Monthly volume
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='cc-title'><div class='cc-dot'></div>Monthly Transaction Volume <span class='cc-sub'>Last 24 months</span></div>", unsafe_allow_html=True)
    dc3 = gcol(txf,"date")
    if dc3 and am2:
        txf2 = txf.copy()
        txf2[dc3] = pd.to_datetime(txf2[dc3],errors="coerce")
        txf2["mon"] = txf2[dc3].dt.to_period("M").astype(str)
        mon = txf2.groupby("mon")[am2].sum().reset_index().sort_values("mon").tail(24)
        fig = go.Figure(go.Bar(
            x=mon["mon"], y=mon[am2],
            marker=dict(color="#0052CC",opacity=0.7,line=dict(width=0))
        ))
        th(fig,260)
        fig.update_layout(xaxis_title="Month",yaxis_title="Total Amount (Rs.)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 5 — SIP TRENDS
# ══════════════════════════════════════════════
elif "SIP" in page:
    sipc = gcol(sip,"inflow"); monc = gcol(sip,"month","date")
    acct = gcol(sip,"account")

    if sipc and monc:
        sip[monc] = pd.to_datetime(sip[monc],errors="coerce")
        sip[sipc] = pd.to_numeric(sip[sipc],errors="coerce")
        ss3 = sip.dropna(subset=[sipc,monc]).sort_values(monc)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total SIP (All Time)",    f"Rs.{ss3[sipc].sum():,.0f} Cr")
        c2.metric("All-Time Monthly High",   f"Rs.{ss3[sipc].max():,.0f} Cr")
        c3.metric("Avg Monthly Inflow",      f"Rs.{ss3[sipc].mean():,.0f} Cr")
        if acct and acct in ss3.columns:
            ss3[acct] = pd.to_numeric(ss3[acct],errors="coerce")
            c4.metric("Latest SIP Accounts",f"{ss3[acct].iloc[-1]:.2f} Cr")

        st.markdown("<br>", unsafe_allow_html=True)

        # Main SIP chart
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Monthly SIP Inflow vs Active Accounts <span class='cc-sub'>Jan 2022 – Dec 2025</span></div>", unsafe_allow_html=True)
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(
            x=ss3[monc], y=ss3[sipc], name="SIP Inflow (Rs.Cr)",
            marker=dict(color="#0052CC",opacity=0.7,line=dict(width=0))
        ),secondary_y=False)
        if acct and acct in ss3.columns:
            fig.add_trace(go.Scatter(
                x=ss3[monc], y=ss3[acct], name="Active Accounts (Cr)",
                line=dict(color="#059669",width=2.5), mode="lines"
            ),secondary_y=True)
        mi = ss3.loc[ss3[sipc].idxmax()]
        fig.add_annotation(
            x=mi[monc], y=mi[sipc],
            text=f"ATH: Rs.{mi[sipc]:,.0f} Cr",
            showarrow=True, arrowhead=2, arrowcolor="#D97706",
            font=dict(color="#D97706",size=10),
            bgcolor="#FFFBEB", bordercolor="#D97706", borderpad=4
        )
        fig.update_layout(**PT,height=380,
            legend=dict(x=0.01,y=0.99,bgcolor="#FFFFFF",bordercolor="#E2E8F0"))
        fig.update_yaxes(title_text="SIP Inflow (Rs. Crore)",  gridcolor="#F1F5F9",secondary_y=False)
        fig.update_yaxes(title_text="Active Accounts (Crore)", gridcolor="#F1F5F9",secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c1,c2 = st.columns([3,2],gap="medium")
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Benchmark Index Performance <span class='cc-sub'>Normalised to 100</span></div>", unsafe_allow_html=True)
        dc4 = gcol(bm,"date"); vc4 = gcol(bm,"close","value"); ic4 = gcol(bm,"index","name")
        if dc4 and vc4:
            bm[dc4] = pd.to_datetime(bm[dc4],errors="coerce")
            bm[vc4] = pd.to_numeric(bm[vc4],errors="coerce")
            idxs = bm[ic4].dropna().unique().tolist() if ic4 else []
            seli = st.multiselect("Select indices",idxs,
                                  default=idxs[:4] if len(idxs)>=4 else idxs)
            fig = go.Figure()
            csi  = ["#0052CC","#059669","#D97706","#7C3AED","#DC2626","#0891B2"]
            for i,idx in enumerate(seli):
                sb = bm[bm[ic4]==idx].sort_values(dc4).dropna(subset=[vc4])
                if sb.empty: continue
                norm = sb[vc4]/sb[vc4].iloc[0]*100
                fig.add_trace(go.Scatter(
                    x=sb[dc4], y=norm, name=str(idx),
                    line=dict(color=csi[i%len(csi)],width=2),
                    hovertemplate=f"<b>{idx}</b><br>%{{x|%d %b %Y}}<br>%{{y:.1f}}<extra></extra>"
                ))
            th(fig,360)
            fig.update_layout(xaxis_title="Date",yaxis_title="Index Value (Base=100)")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>Category Net Inflows</div>", unsafe_allow_html=True)
        cc3 = gcol(cat,"category"); ic5 = gcol(cat,"inflow","net")
        if cc3 and ic5:
            cat[ic5] = pd.to_numeric(cat[ic5],errors="coerce")
            cs = cat.groupby(cc3)[ic5].sum().sort_values()
            fig = go.Figure(go.Bar(
                x=cs.values, y=cs.index, orientation="h",
                marker=dict(color=["#059669" if v>0 else "#DC2626" for v in cs.values],
                            opacity=0.8, line=dict(width=0)),
                text=[f"Rs.{v:+,.0f}" for v in cs.values],
                textposition="outside",textfont=dict(size=8,color="#64748B")
            ))
            fig.add_vline(x=0,line_color="#E2E8F0",line_width=1.5)
            th(fig,380)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # YoY
    if sipc and monc:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>SIP Inflow — Year-on-Year Growth</div>", unsafe_allow_html=True)
        ss3["year"] = pd.to_datetime(ss3[monc],errors="coerce").dt.year.astype(str)
        yoy = ss3.groupby("year")[sipc].sum().reset_index()
        fig = go.Figure(go.Bar(
            x=yoy["year"], y=yoy[sipc],
            marker=dict(
                color=list(range(len(yoy))),
                colorscale=[[0,"#DBEAFE"],[0.5,"#3B82F6"],[1,"#0052CC"]],
                line=dict(width=0)
            ),
            text=[f"Rs.{v:,.0f}" for v in yoy[sipc]],
            textposition="outside",textfont=dict(size=10,color="#64748B")
        ))
        th(fig,280)
        fig.update_layout(xaxis_title="Year",yaxis_title="Total SIP Inflow (Rs. Crore)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 6 — FUND EXPLORER
# ══════════════════════════════════════════════
elif "Explorer" in page:
    fl3 = fund["scheme_name"].dropna().tolist() if "scheme_name" in fund.columns else []

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    sel2 = st.selectbox("🔍  Search fund by name", fl3)
    st.markdown("</div>", unsafe_allow_html=True)

    cdarr = fund[fund["scheme_name"]==sel2]["amfi_code"].values if "scheme_name" in fund.columns else [sel2]
    if len(cdarr)>0:
        cd  = str(cdarr[0])
        fd  = fund[fund["amfi_code"]==cd]
        nf  = nav[nav["amfi_code"]==cd].sort_values("date")
        mf2 = master[master["amfi_code"]==cd]

        # Fund info
        if not fd.empty:
            st.markdown("""
            <div class='info-strip'>
              <div class='is-icon'>ℹ️</div>
              <div>
                <div class='is-text'>Fund Information</div>
                <div class='is-sub'>Key details about the selected scheme</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Fund House",    fd["fund_house"].values[0]       if "fund_house"       in fd.columns else "N/A")
            c2.metric("Category",      fd["category"].values[0]         if "category"         in fd.columns else "N/A")
            c3.metric("Risk Grade",    fd["risk_category"].values[0]    if "risk_category"    in fd.columns else "N/A")
            c4.metric("Expense Ratio", f"{fd['expense_ratio_pct'].values[0]:.2f}%" if "expense_ratio_pct" in fd.columns else "N/A")
            c5.metric("Fund Manager",  str(fd["fund_manager"].values[0])[:18] if "fund_manager" in fd.columns else "N/A")

        # Performance metrics
        if not mf2.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
            mets = [("cagr_1yr_pct","1yr CAGR","%.2f%%"),
                    ("cagr_3yr_pct","3yr CAGR","%.2f%%"),
                    ("cagr_5yr_pct","5yr CAGR","%.2f%%"),
                    ("sharpe_ratio","Sharpe","%.3f"),
                    ("sortino_ratio","Sortino","%.3f"),
                    ("alpha","Alpha","%.2f%%"),
                    ("max_drawdown_pct","Max Drawdown","%.2f%%")]
            for (cn,lbl,fmt),col in zip(mets,[c1,c2,c3,c4,c5,c6,c7]):
                if cn in mf2.columns:
                    v = mf2[cn].values[0]
                    if v is not None and not (isinstance(v,float) and np.isnan(v)):
                        col.metric(lbl,fmt%v)

        st.markdown("<br>", unsafe_allow_html=True)

        # NAV chart
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='cc-title'><div class='cc-dot'></div>NAV History with Daily Returns <span class='cc-sub'>Use range selector below chart</span></div>", unsafe_allow_html=True)
        if not nf.empty:
            fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                                row_heights=[0.7,0.3],vertical_spacing=0.02)
            fig.add_trace(go.Scatter(
                x=nf["date"], y=nf["nav"],
                fill="tozeroy", fillcolor="rgba(0,82,204,0.05)",
                line=dict(color="#0052CC",width=2), name="NAV (Rs.)",
                hovertemplate="<b>Rs.%{y:.4f}</b><br>%{x|%d %b %Y}<extra></extra>"
            ),row=1,col=1)
            if "daily_return_pct" in nf.columns:
                cret = ["#059669" if r>=0 else "#DC2626"
                        for r in nf["daily_return_pct"].fillna(0)]
                fig.add_trace(go.Bar(
                    x=nf["date"], y=nf["daily_return_pct"], name="Daily Return %",
                    marker=dict(color=cret,line=dict(width=0)),
                    hovertemplate="Return: %{y:.3f}%<extra></extra>"
                ),row=2,col=1)
            fig.update_layout(**PT, height=480,
                title=dict(text=str(sel2)[:55]+" — NAV History",
                           font=dict(size=11,color="#64748B")))
            fig.update_xaxes(
                rangeselector=dict(
                    buttons=[
                        dict(count=1,label="1M",step="month",stepmode="backward"),
                        dict(count=6,label="6M",step="month",stepmode="backward"),
                        dict(count=1,label="1Y",step="year", stepmode="backward"),
                        dict(count=3,label="3Y",step="year", stepmode="backward"),
                        dict(step="all",label="All")
                    ],
                    bgcolor="#F8FAFC",activecolor="#0052CC",
                    font=dict(color="#64748B",size=10),
                    bordercolor="#E2E8F0"
                ),row=1,col=1)
            fig.update_yaxes(title_text="NAV (Rs.)",     row=1,col=1,gridcolor="#F1F5F9")
            fig.update_yaxes(title_text="Daily Return %",row=2,col=1,gridcolor="#F1F5F9")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Peer + Rank
        c1,c2 = st.columns([3,2],gap="medium")
        with c1:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='cc-title'><div class='cc-dot'></div>Peer Comparison</div>", unsafe_allow_html=True)
            if not fd.empty and "category" in fd.columns:
                cn2  = fd["category"].values[0]
                peers= master[master["category"]==cn2] if "category" in master.columns else master
                sh2  = [c for c in ["rank","scheme_name","composite_score",
                                    "cagr_3yr_pct","sharpe_ratio","alpha",
                                    "max_drawdown_pct"] if c in peers.columns]
                if sh2:
                    dp2 = peers[sh2].copy()
                    dp2.columns = [c.replace("_"," ").title() for c in dp2.columns]
                    st.dataframe(dp2, use_container_width=True, height=360, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            if not mf2.empty and "composite_score" in mf2.columns and "rank" in mf2.columns:
                rnk  = int(mf2["rank"].values[0])
                scr  = float(mf2["composite_score"].values[0])
                grade= "A+" if rnk<=5 else "A" if rnk<=10 else "B+" if rnk<=20 else "B" if rnk<=30 else "C"
                gclr = "#059669" if rnk<=10 else "#D97706" if rnk<=25 else "#DC2626"
                gbg  = "#DCFCE7" if rnk<=10 else "#FEF3C7" if rnk<=25 else "#FEE2E2"
                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;
                            padding:28px 20px;text-align:center;
                            box-shadow:0 1px 4px rgba(0,0,0,0.04)'>
                    <div style='font-size:0.6rem;color:#94A3B8;text-transform:uppercase;
                                letter-spacing:1px;margin-bottom:10px'>
                        Composite Scorecard Rank
                    </div>
                    <div style='font-size:4rem;font-weight:800;color:{gclr};
                                letter-spacing:-3px;line-height:1'>
                        #{rnk}
                    </div>
                    <div style='font-size:0.85rem;color:#475569;margin-top:8px'>
                        Score: {scr:.1f} / 100
                    </div>
                    <div style='font-size:0.68rem;color:#94A3B8;margin-top:4px'>
                        out of 40 funds
                    </div>
                    <div style='margin-top:16px;display:inline-block;
                                background:{gbg};color:{gclr};
                                font-size:1.6rem;font-weight:800;
                                padding:6px 22px;border-radius:10px;
                                letter-spacing:2px;border:2px solid {gclr}33'>
                        Grade {grade}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Radar chart
                st.markdown("<br>", unsafe_allow_html=True)
                if all(c in mf2.columns for c in ["sharpe_ratio","alpha","cagr_3yr_pct","composite_score"]):
                    def nv(val,lo,hi):
                        try: return max(0,min(100,(float(val)-lo)/(hi-lo)*100))
                        except: return 0
                    cats = ["Sharpe","Sortino","Alpha","3yr Return","Score"]
                    vals = [
                        nv(mf2["sharpe_ratio"].values[0],-1,3),
                        nv(mf2.get("sortino_ratio",pd.Series([0])).values[0],-1,4),
                        nv(mf2["alpha"].values[0],-5,30),
                        nv(mf2["cagr_3yr_pct"].values[0],-5,50),
                        float(mf2["composite_score"].values[0])
                    ]
                    cats += [cats[0]]; vals += [vals[0]]
                    fig = go.Figure(go.Scatterpolar(
                        r=vals, theta=cats,
                        fill="toself",
                        fillcolor="rgba(0,82,204,0.1)",
                        line=dict(color="#0052CC",width=2),
                        marker=dict(color="#0052CC",size=6)
                    ))
                    fig.update_layout(
                        polar=dict(
                            bgcolor="#FFFFFF",
                            radialaxis=dict(visible=True,range=[0,100],
                                            gridcolor="#F1F5F9",
                                            tickfont=dict(size=8,color="#94A3B8")),
                            angularaxis=dict(gridcolor="#E2E8F0",
                                            tickfont=dict(size=10,color="#475569"))
                        ),
                        paper_bgcolor="#FFFFFF",
                        height=300, margin=dict(l=40,r=40,t=30,b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)