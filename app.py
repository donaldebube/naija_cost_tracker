"""Naija Cost Tracker — Real-Time Nigerian Cost of Living Intelligence"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.data_loader import (
    load_inflation, load_food_prices, load_state_inflation,
    load_exchange_rates, load_macro_indicators,
    fetch_live_rate_now, load_live_rate, compute_hardship_index,
)

st.set_page_config(page_title="Naija Cost Tracker", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
:root{--bg:#0D1F14;--card:#132A1C;--sidebar:#0A1910;--green:#2ECC7A;--gmid:#1A8A4A;--gold:#F0C040;--brick:#E05A30;--cream:#F5F0E8;--dim:#B8B0A0;--b:rgba(46,204,122,0.18);--bg2:rgba(240,192,64,0.25);}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--cream)!important;}
.stApp{background:var(--bg)!important;}
[data-testid="stSidebar"]{background:var(--sidebar)!important;border-right:1px solid var(--bg2)!important;}
[data-testid="stSidebar"] *{color:var(--cream)!important;}
[data-testid="stSidebar"] .stSelectbox label{color:var(--gold)!important;font-family:'Syne',sans-serif!important;font-size:0.68rem!important;text-transform:uppercase;letter-spacing:0.12em;font-weight:700!important;}
[data-testid="stSidebar"] .stSelectbox > div > div{background:rgba(46,204,122,0.08)!important;border:1px solid var(--b)!important;color:var(--cream)!important;border-radius:8px!important;}
[data-testid="stSidebar"] .stSelectbox > div > div > div{color:var(--cream)!important;}
[data-testid="stSidebar"] .stSlider label{color:var(--gold)!important;font-family:'Syne',sans-serif!important;font-size:0.68rem!important;text-transform:uppercase;letter-spacing:0.12em;font-weight:700!important;}
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--b)!important;border-radius:12px!important;padding:1rem 1.2rem!important;border-top:3px solid var(--green)!important;}
[data-testid="metric-container"] label{font-family:'Syne',sans-serif!important;font-size:0.65rem!important;text-transform:uppercase!important;letter-spacing:0.1em!important;color:var(--dim)!important;font-weight:600!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;font-size:1.7rem!important;font-weight:800!important;color:#FFFFFF!important;}
[data-testid="metric-container"] [data-testid="stMetricDelta"]{font-size:0.76rem!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:#FFFFFF!important;}
p,li{color:var(--cream)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--card)!important;border-radius:10px!important;padding:4px!important;border:1px solid var(--b)!important;}
.stTabs [data-baseweb="tab"]{font-family:'Syne',sans-serif!important;font-size:0.72rem!important;text-transform:uppercase!important;letter-spacing:0.06em!important;border-radius:7px!important;color:var(--dim)!important;font-weight:600!important;}
.stTabs [aria-selected="true"]{background:var(--gmid)!important;color:#FFFFFF!important;}
[data-testid="stMultiSelect"] label,[data-testid="stNumberInput"] label{color:var(--cream)!important;font-size:0.82rem!important;}
[data-testid="stMultiSelect"] > div > div,[data-testid="stNumberInput"] input{background:var(--card)!important;border:1px solid var(--b)!important;border-radius:8px!important;color:#FFFFFF!important;}
.stAlert{background:rgba(240,192,64,0.1)!important;border:1px solid var(--bg2)!important;border-left:4px solid var(--gold)!important;border-radius:10px!important;}
.stAlert p{color:var(--cream)!important;}
[data-testid="stDataFrame"]{border:1px solid var(--b)!important;border-radius:10px!important;}
hr{border:none!important;border-top:1px solid var(--b)!important;margin:1.2rem 0!important;}
#MainMenu,footer,header{visibility:hidden;}
.eyebrow{font-family:'Syne',sans-serif;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--green);font-weight:700;margin-bottom:0.4rem;}
.page-title{font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:#FFFFFF;line-height:1.1;margin:0 0 0.5rem 0;}
.page-sub{font-size:0.88rem;color:var(--dim);line-height:1.6;max-width:640px;}
.lbl{font-family:'Syne',sans-serif;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.14em;color:var(--dim);font-weight:700;margin-bottom:0.3rem;display:block;}
.desc{font-size:0.82rem;color:#B8B0A0;line-height:1.65;padding:0.7rem 0.9rem;background:#132A1C;border-radius:8px;border-left:3px solid rgba(46,204,122,0.35);margin-bottom:0.8rem;}
.insight{background:#132A1C;border:1px solid rgba(46,204,122,0.2);border-radius:8px;padding:0.75rem 1rem;margin-top:0.4rem;font-size:0.82rem;color:#F5F0E8;line-height:1.6;}
.filter-bar{background:#132A1C;border:1px solid rgba(240,192,64,0.25);border-radius:12px;padding:1rem 1.4rem;margin-bottom:1.4rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;}
</style>
""", unsafe_allow_html=True)

# ── Chart helper ──────────────────────────────────────────────────────────────
def theme(title="", height=320, showlegend=True, **kw):
    base = dict(
        paper_bgcolor="#132A1C", plot_bgcolor="#132A1C",
        font=dict(family="Inter, sans-serif", color="#F5F0E8", size=11),
        margin=dict(t=46 if title else 20, b=36, l=52, r=16),
        colorway=["#2ECC7A","#F0C040","#E05A30","#1A8A4A","#C49A28"],
        xaxis=dict(gridcolor="rgba(46,204,122,0.1)", linecolor="rgba(46,204,122,0.15)", tickfont=dict(color="#B8B0A0", size=10)),
        yaxis=dict(gridcolor="rgba(46,204,122,0.1)", linecolor="rgba(46,204,122,0.15)", tickfont=dict(color="#B8B0A0", size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F5F0E8", size=11), orientation="h", y=1.06),
        height=height, showlegend=showlegend,
    )
    if title:
        base["title"] = dict(text=title, font=dict(family="Syne, sans-serif", color="#FFFFFF", size=12), x=0)
    for k, v in kw.items():
        if k in ("xaxis","yaxis","legend") and isinstance(v, dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base

def sec(title, desc):
    st.markdown(f'<span class="lbl">{title}</span><div class="desc">{desc}</div>', unsafe_allow_html=True)

def tip(txt):
    st.markdown(f'<div class="insight"><span style="color:#2ECC7A;font-weight:700;font-size:0.75rem;">💡 INSIGHT &nbsp;</span>{txt}</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.2rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.18em;color:#2ECC7A;font-weight:700;margin-bottom:0.4rem;">🇳🇬 Nigeria</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:#FFFFFF;line-height:1.1;">Naija Cost<br>Tracker</div>
        <div style="font-size:0.72rem;color:#B8B0A0;margin-top:0.4rem;">Real-time cost of living<br>intelligence for Nigeria</div>
    </div>
    <hr style="border-color:rgba(46,204,122,0.18);margin:0 0 0.9rem 0;">
    """, unsafe_allow_html=True)

    page = st.selectbox("NAVIGATE", [
        "🏠 Overview", "📈 Inflation", "🛒 Food Prices",
        "💵 Exchange Rates", "🔥 Hardship Index", "📖 Methodology"
    ])

    st.markdown("<hr style='border-color:rgba(46,204,122,0.18);margin:0.9rem 0 0.6rem;'>", unsafe_allow_html=True)
    st.markdown('<span class="lbl" style="color:#F0C040;">🗓 Time Period Filter</span>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;color:#B8B0A0;margin-bottom:0.6rem;">Filters all charts and metrics across the entire app</div>', unsafe_allow_html=True)

    year_range = st.slider("Select year range", min_value=2020, max_value=2026, value=(2020, 2026), step=1)
    start_year, end_year = year_range

    st.markdown("<hr style='border-color:rgba(46,204,122,0.18);margin:0.9rem 0;'>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Live Rate", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style="font-size:0.68rem;color:#B8B0A0;line-height:1.8;margin-top:0.6rem;">
        <div style="font-family:'Syne',sans-serif;color:#F0C040;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;font-weight:700;">Data Sources</div>
        NBS CPI Reports (2024=100)<br>CBN NFEM Official Rates<br>Open Exchange Rates API<br>NNPC Fuel Price Data
    </div>
    <div style="font-size:0.6rem;color:rgba(184,176,160,0.35);margin-top:0.8rem;">Jan 2020 – Jan 2026 · Live FX</div>
    """, unsafe_allow_html=True)

# ── Load & filter data ────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_all_data():
    live     = fetch_live_rate_now()
    inf      = load_inflation()
    food     = load_food_prices()
    states   = load_state_inflation()
    fx       = load_exchange_rates()
    macro    = load_macro_indicators()
    hardship = compute_hardship_index(inf, fx)
    return inf, food, states, fx, macro, live, hardship

_inf_all, _food_all, states, _fx_all, macro, live, _hard_all = get_all_data()

# Apply global year filter
inflation = _inf_all[(_inf_all["date"].dt.year >= start_year) & (_inf_all["date"].dt.year <= end_year)].copy()
food      = _food_all[(_food_all["date"].dt.year >= start_year) & (_food_all["date"].dt.year <= end_year)].copy()
fx        = _fx_all[(_fx_all["date"].dt.year >= start_year) & (_fx_all["date"].dt.year <= end_year)].copy()
hardship  = _hard_all[(_hard_all["date"].dt.year >= start_year) & (_hard_all["date"].dt.year <= end_year)].copy()

# Guard: if filter leaves empty frames, fall back
if len(inflation) == 0: inflation = _inf_all.copy()
if len(food) == 0:      food      = _food_all.copy()
if len(fx) == 0:        fx        = _fx_all.copy()
if len(hardship) == 0:  hardship  = _hard_all.copy()

li = inflation.iloc[-1]
lf = fx.iloc[-1]
lh = hardship.iloc[-1]
live_rate = float(live.get("rate", lf["cbn_official_rate"]))
is_live   = bool(live.get("is_live", False))
live_src  = str(live.get("source", "cached"))
live_date = str(live.get("date", "N/A"))

# Filter period label for display
period_label = f"{start_year}" if start_year == end_year else f"{start_year} – {end_year}"


# ═══════════════════════════ OVERVIEW ═══════════════════════════════════
if page == "🏠 Overview":
    badge = '<span style="background:rgba(46,204,122,0.15);color:#2ECC7A;border:1px solid rgba(46,204,122,0.3);border-radius:20px;padding:1px 8px;font-size:0.66rem;font-weight:700;">● LIVE</span>' if is_live else '<span style="background:rgba(240,192,64,0.15);color:#F0C040;border:1px solid rgba(240,192,64,0.3);border-radius:20px;padding:1px 8px;font-size:0.66rem;font-weight:700;">● CACHED</span>'
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Nigerian Cost of Living Intelligence Platform</div>
        <div class="page-title">What is ₦1,000 worth in Nigeria today?</div>
        <div class="page-sub">Real data. Real impact. Tracking how inflation, food prices, and exchange rates affect everyday Nigerians. Data from NBS, CBN, and live FX feeds.</div>
        <div style="margin-top:0.6rem;font-size:0.73rem;color:#B8B0A0;">
            FX: {badge} {live_src} · {live_date} &nbsp;·&nbsp;
            <span style="color:#F0C040;">Showing: {period_label}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── 8 KPIs ──
    sec("Key Economic Indicators — Latest Available Data",
        f"Eight core metrics covering the most recent data points within the selected period ({period_label}). Inflation is from the NBS CPI report. Exchange rate is fetched live from Open Exchange Rates API. The Hardship Index is a proprietary composite — see the Hardship Index page for the full methodology.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Headline Inflation",  f"{li['headline_inflation_pct']:.2f}%",
              f"{li['headline_inflation_pct']-inflation.iloc[-2]['headline_inflation_pct']:+.2f}pp MoM" if len(inflation)>1 else "")
    c2.metric("Food Inflation",      f"{li['food_inflation_pct']:.2f}%",
              f"{li['food_inflation_pct']-inflation.iloc[-2]['food_inflation_pct']:+.2f}pp MoM" if len(inflation)>1 else "")
    c3.metric("Live USD/NGN",        f"₦{live_rate:,.0f}",
              f"₦{live_rate-_fx_all.iloc[-2]['cbn_official_rate']:+,.0f} vs prev period")
    c4.metric("Hardship Index",      f"{lh['hardship_index']:.0f}/100", lh["hardship_label"])

    st.markdown("<br>", unsafe_allow_html=True)
    c5,c6,c7,c8 = st.columns(4)
    yoy = li['headline_inflation_pct'] - inflation.iloc[-min(13,len(inflation))]['headline_inflation_pct']
    c5.metric("Inflation YoY",       f"{yoy:+.1f}pp",    "Improving 📉" if yoy<0 else "Worsening 📈")
    c6.metric("Parallel Premium",    f"₦{lf['spread']:,.0f}", f"{lf['spread_pct']:.1f}% above CBN")
    c7.metric("Petrol Pump Price",   f"₦{lf['fuel_price_per_litre_ngn']:,.0f}/L",
              f"₦{lf['fuel_price_per_litre_ngn']-fx.iloc[-2]['fuel_price_per_litre_ngn']:+,.0f}" if len(fx)>1 else "")
    c8.metric("Core Inflation",      f"{li['core_inflation_pct']:.2f}%",
              f"{li['core_inflation_pct']-inflation.iloc[-2]['core_inflation_pct']:+.2f}pp MoM" if len(inflation)>1 else "")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Two charts side by side ──
    sec("Purchasing Power Erosion — ₦10,000 Over Time",
        f"If you had ₦10,000 in January {start_year}, this shows its real purchasing power at each point in the selected period. A falling line means the same naira buys significantly less. The steeper the decline, the faster inflation was eating into savings.")
    col_l, col_r = st.columns(2)
    with col_l:
        base_v = inflation[inflation["date"].dt.year==start_year]["headline_inflation_pct"].mean() if not inflation[inflation["date"].dt.year==start_year].empty else inflation.iloc[0]["headline_inflation_pct"]
        inflation["pp"] = 10000 / (1 + (inflation["headline_inflation_pct"] - base_v) / 100)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=inflation["date"], y=inflation["pp"], mode="lines",
            fill="tozeroy", line=dict(color="#2ECC7A", width=2.5), fillcolor="rgba(46,204,122,0.07)"))
        fig.add_hline(y=10000, line_dash="dot", line_color="#F0C040",
            annotation_text=f"₦10,000 baseline ({start_year})", annotation_font_color="#F0C040", annotation_font_size=10)
        fig.update_layout(**theme(f"Real Value of ₦10,000 — {period_label}", height=280, showlegend=False, yaxis=dict(title="Real Value (₦)")))
        st.plotly_chart(fig, use_container_width=True)
        if len(inflation) > 1:
            pp_now = inflation.iloc[-1]["pp"]
            tip(f"₦10,000 from {start_year} now has the purchasing power of ₦{pp_now:,.0f} — a real loss of ₦{10000-pp_now:,.0f} ({(10000-pp_now)/10000*100:.0f}%) over the selected period.")

    with col_r:
        sec("Headline vs Food Inflation",
            f"Food inflation consistently runs above headline inflation in Nigeria due to FX-driven import costs and supply chain disruptions. The gap between the two lines shows the extra pressure on household food budgets during {period_label}.")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=inflation["date"], y=inflation["headline_inflation_pct"],
            name="Headline", line=dict(color="#2ECC7A", width=2.5)))
        fig2.add_trace(go.Scatter(x=inflation["date"], y=inflation["food_inflation_pct"],
            name="Food", line=dict(color="#E05A30", width=2.5)))
        fig2.update_layout(**theme("", height=280, yaxis=dict(title="%"), legend=dict(orientation="h", y=1.06, x=0)))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Salary calculator ──
    sec("Remote Worker / Freelancer Salary Calculator",
        "See how the naira value of your USD income has changed over time as the exchange rate shifted. Adjust the income below — all bars update to show what that amount was worth in naira at each point in the selected period.")
    ca, cb = st.columns([1, 3])
    with ca:
        salary = st.number_input("Monthly income (USD)", 100, 50000, 1000, 100)
    fx["sal"] = fx["cbn_official_rate"] * salary
    with cb:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=fx["label"], y=fx["sal"],
            marker_color="#1A8A4A", marker_line_color="#2ECC7A", marker_line_width=0.5,
            text=[f"₦{v/1000:.0f}k" for v in fx["sal"]],
            textposition="outside", textfont=dict(size=9, color="#F5F0E8")))
        fig3.update_layout(**theme(f"₦ Value of ${salary:,}/month — {period_label}", height=240, showlegend=False,
            yaxis=dict(title="₦ NGN"),
            xaxis=dict(tickangle=-30, gridcolor="rgba(46,204,122,0.1)", linecolor="rgba(46,204,122,0.15)", tickfont=dict(color="#B8B0A0", size=9))))
        st.plotly_chart(fig3, use_container_width=True)

    ngn_now  = live_rate * salary
    ngn_base = fx.iloc[0]["cbn_official_rate"] * salary
    diff = ngn_now - ngn_base
    st.info(f"💬  At the start of your selected period ({period_label}), ${salary:,}/month was worth ₦{ngn_base:,.0f}. "
            f"At today's live rate of ₦{live_rate:,.0f}/$, that's now **₦{ngn_now:,.0f}** — "
            f"₦{abs(diff):,.0f} {'more' if diff>0 else 'less'} in naira terms. "
            f"Real purchasing power has fallen due to cumulative inflation over this period.")


# ═══════════════════════════ INFLATION ══════════════════════════════════
elif page == "📈 Inflation":
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">NBS CPI Reports · Base Year 2024=100 · Showing: {period_label}</div>
        <div class="page-title">Inflation Tracker</div>
        <div class="page-sub">Nigeria's inflation peaked at ~34% in mid-2024, falling to 15.10% in January 2026. Two major shocks define this story: the fuel subsidy removal (May 2023) and FX unification (June 2023). The 2024 NBS CPI rebase further affected reported figures from December 2024 onward.</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric(f"Headline (latest)", f"{li['headline_inflation_pct']:.2f}%",
              f"{li['headline_inflation_pct']-inflation.iloc[-min(13,len(inflation))]['headline_inflation_pct']:+.1f}pp YoY")
    c2.metric(f"Food (latest)",    f"{li['food_inflation_pct']:.2f}%",
              f"{li['food_inflation_pct']-inflation.iloc[-min(13,len(inflation))]['food_inflation_pct']:+.1f}pp YoY")
    c3.metric(f"Core (latest)",    f"{li['core_inflation_pct']:.2f}%",
              f"{li['core_inflation_pct']-inflation.iloc[-min(13,len(inflation))]['core_inflation_pct']:+.1f}pp YoY")
    c4.metric("Peak in period",   f"{inflation['headline_inflation_pct'].max():.1f}%",
              f"{inflation.loc[inflation['headline_inflation_pct'].idxmax(),'month_label']}")

    st.markdown("<hr>", unsafe_allow_html=True)
    sec(f"Headline, Food & Core Inflation — {period_label}",
        "Three inflation measures on one chart. Headline captures all prices. Food is consistently higher due to import costs and supply chain issues. Core (excluding food & energy) shows structural price pressure — it currently sits ABOVE headline inflation, signalling persistent underlying cost pressures in services and manufacturing beyond what the headline figure suggests.")

    fig = go.Figure()
    for cn,lb,co in [("headline_inflation_pct","Headline","#2ECC7A"),("food_inflation_pct","Food","#E05A30"),("core_inflation_pct","Core","#F0C040")]:
        fig.add_trace(go.Scatter(x=inflation["date"],y=inflation[cn],name=lb,mode="lines+markers",line=dict(color=co,width=2.5),marker=dict(size=4,color=co)))
    if start_year <= 2023 <= end_year:
        fig.add_vrect(x0="2023-05-01",x1="2023-06-15",fillcolor="rgba(240,192,64,0.07)",line_width=0,annotation_text="Subsidy Removal",annotation_font_size=9,annotation_font_color="#B8B0A0")
        fig.add_vrect(x0="2023-06-15",x1="2023-07-15",fillcolor="rgba(224,90,48,0.07)",line_width=0,annotation_text="FX Unification",annotation_font_size=9,annotation_font_color="#B8B0A0")
    if start_year <= 2024 <= end_year:
        fig.add_vrect(x0="2024-11-01",x1="2025-02-01",fillcolor="rgba(46,204,122,0.05)",line_width=0,annotation_text="CPI Rebase",annotation_font_size=9,annotation_font_color="#B8B0A0")
    fig.update_layout(**theme(f"Nigeria Inflation Rates (%) — {period_label}", height=380, yaxis=dict(title="Rate (%)")))
    st.plotly_chart(fig, use_container_width=True)
    tip(f"Core inflation ({li['core_inflation_pct']:.2f}%) is higher than headline ({li['headline_inflation_pct']:.2f}%), meaning structural price pressures in services and manufacturing are more persistent than food and energy — this complicates the CBN's path to further rate cuts.")

    if 2024 <= end_year:
        st.info("⚠️  **NBS Rebase (Dec 2024):** NBS changed base year from 2009 → 2024=100. The drop from ~34% to ~15% between Nov–Dec 2024 reflects BOTH genuine disinflation AND this methodology change. Figures before and after are not directly comparable.")

    st.markdown("<hr>", unsafe_allow_html=True)
    sec("State-Level Inflation (2025) vs Year-on-Year Change",
        "Left: inflation by state in 2025 — northern states show higher rates due to food supply chain disruptions from insecurity. Right: year-on-year change from 2024 to 2025 — green bars mean inflation fell, red means it worsened. All states improved significantly, reflecting both disinflation and the CPI rebase effect.")

    ca, cb = st.columns(2)
    with ca:
        s = states.sort_values("inflation_2025_pct", ascending=True)
        fig2 = go.Figure(go.Bar(x=s["inflation_2025_pct"], y=s["state"], orientation="h",
            marker=dict(color=s["inflation_2025_pct"], colorscale=[[0,"#1A8A4A"],[0.5,"#F0C040"],[1,"#E05A30"]],
            showscale=True, colorbar=dict(title="%", tickfont=dict(color="#F5F0E8"), titlefont=dict(color="#F5F0E8")))))
        fig2.update_layout(**theme("2025 Inflation by State (%)", height=440, showlegend=False,
            xaxis=dict(title="%", gridcolor="rgba(46,204,122,0.1)", tickfont=dict(color="#B8B0A0",size=10)),
            yaxis=dict(gridcolor="rgba(46,204,122,0.1)", tickfont=dict(color="#F5F0E8",size=10))))
        st.plotly_chart(fig2, use_container_width=True)
    with cb:
        states["ch"] = states["inflation_2025_pct"] - states["inflation_2024_pct"]
        s2 = states.sort_values("ch", ascending=True)
        fig3 = go.Figure(go.Bar(x=s2["ch"], y=s2["state"], orientation="h",
            marker_color=["#2ECC7A" if v<0 else "#E05A30" for v in s2["ch"]]))
        fig3.update_layout(**theme("YoY Change 2024→2025 (pp)", height=440, showlegend=False,
            xaxis=dict(title="pp change", gridcolor="rgba(46,204,122,0.1)", tickfont=dict(color="#B8B0A0",size=10)),
            yaxis=dict(gridcolor="rgba(46,204,122,0.1)", tickfont=dict(color="#F5F0E8",size=10))))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    sec("Annual Average Summary",
        f"Average inflation across each year in the selected period. Shows at a glance how the inflationary environment has shifted year over year. An average of 33%+ in 2024 means prices were compounding at that rate throughout the entire year — not just a brief spike.")
    ann = inflation.groupby("year")[["headline_inflation_pct","food_inflation_pct","core_inflation_pct"]].mean().round(2).reset_index()
    ann.columns = ["Year","Headline (%)","Food (%)","Core (%)"]
    st.dataframe(ann, use_container_width=True, hide_index=True)


# ═══════════════════════════ FOOD PRICES ════════════════════════════════
elif page == "🛒 Food Prices":
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">NBS Selected Food Prices Watch · Quarterly · Showing: {period_label}</div>
        <div class="page-title">Food Price Tracker</div>
        <div class="page-sub">Basic food staples became 2–4x more expensive between 2022 and late 2024. Prices have since moderated but remain far above pre-crisis levels. This page tracks the seven staples that form the core of the Nigerian household food basket.</div>
    </div>""", unsafe_allow_html=True)

    ITEMS = {"rice_50kg_ngn":"Rice (50kg)","garri_50kg_ngn":"Garri (50kg)","tomatoes_1kg_ngn":"Tomatoes (1kg)",
             "cooking_oil_5l_ngn":"Cooking Oil (5L)","eggs_crate_ngn":"Eggs (crate)","bread_loaf_ngn":"Bread (loaf)","beef_1kg_ngn":"Beef (1kg)"}
    f0 = food.iloc[0]; fl = food.iloc[-1]

    sec("Current Prices vs Start of Selected Period",
        f"Each card shows the latest price and the percentage change since the start of {period_label}. Use this to quickly see which staples have risen most sharply over your chosen time window.")
    items = list(ITEMS.items())
    cols = st.columns(4)
    for i,(k,v) in enumerate(items[:4]):
        pct=(fl[k]-f0[k])/f0[k]*100; cols[i].metric(v, f"₦{fl[k]:,.0f}", f"{pct:+.0f}% since {start_year}")
    cols2 = st.columns(3)
    for i,(k,v) in enumerate(items[4:]):
        pct=(fl[k]-f0[k])/f0[k]*100; cols2[i].metric(v, f"₦{fl[k]:,.0f}", f"{pct:+.0f}% since {start_year}")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Two charts side by side
    col_a, col_b = st.columns(2)
    with col_a:
        sec("Peak Price vs Current Price",
            "Red bars show the highest recorded price for each staple within the selected period. Green bars show the most recent price. The closer the two bars, the less price relief has occurred from the peak.")
        pd_list=[{"item":v,"peak":food[k].max(),"current":fl[k],"off":(food[k].max()-fl[k])/food[k].max()*100} for k,v in ITEMS.items()]
        pdf=pd.DataFrame(pd_list)
        figp=go.Figure()
        figp.add_trace(go.Bar(name="Peak",x=pdf["item"],y=pdf["peak"],marker_color="#E05A30",opacity=0.85))
        figp.add_trace(go.Bar(name="Current",x=pdf["item"],y=pdf["current"],marker_color="#2ECC7A"))
        figp.update_layout(**theme("Peak vs Current (₦)", height=300, barmode="group",
            yaxis=dict(title="Price (₦)"), xaxis=dict(tickangle=-20, tickfont=dict(color="#B8B0A0",size=9))))
        st.plotly_chart(figp, use_container_width=True)
        best=pdf.sort_values("off",ascending=False).iloc[0]; worst=pdf.sort_values("off").iloc[0]
        tip(f"Most relief from peak: <strong>{best['item']}</strong> (-{best['off']:.0f}%). Least relief: <strong>{worst['item']}</strong> (-{worst['off']:.0f}%).")

    with col_b:
        sec("Price Trends Over Time",
            f"Select items below to compare price movements across {period_label}. All prices in absolute naira — not inflation-adjusted. Use this to see which items spiked earliest and which have recovered most.")
        sel=st.multiselect("Select items",options=list(ITEMS.keys()),default=["rice_50kg_ngn","garri_50kg_ngn","beef_1kg_ngn"],format_func=lambda x:ITEMS[x])
        if sel:
            COLS=["#2ECC7A","#E05A30","#F0C040","#1A8A4A","#C49A28","#80C0A0"]
            fig4=go.Figure()
            for i,k in enumerate(sel):
                fig4.add_trace(go.Scatter(x=food["date"],y=food[k],name=ITEMS[k],mode="lines+markers",line=dict(color=COLS[i%len(COLS)],width=2.5),marker=dict(size=6)))
            fig4.update_layout(**theme(f"Food Prices (₦) — {period_label}", height=300, yaxis=dict(title="Price (₦)")))
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    sec("Monthly Food Basket Calculator",
        f"Enter what your household typically buys each month. The calculator estimates your total food spend at current prices and compares it against the start of {period_label} — showing the exact naira impact of food inflation on your household budget.")
    b1,b2,b3,b4=st.columns(4)
    qr=b1.number_input("Rice bags/month",0.0,10.0,0.5,0.5)
    qg=b2.number_input("Garri bags/month",0.0,10.0,0.5,0.5)
    qe=b3.number_input("Egg crates/month",0,20,4)
    qo=b4.number_input("Oil bottles/month",0,10,1)
    tot=qr*fl["rice_50kg_ngn"]+qg*fl["garri_50kg_ngn"]+qe*fl["eggs_crate_ngn"]+qo*fl["cooking_oil_5l_ngn"]
    t0 =qr*f0["rice_50kg_ngn"]+qg*f0["garri_50kg_ngn"]+qe*f0["eggs_crate_ngn"]+qo*f0["cooking_oil_5l_ngn"]
    r1,r2,r3=st.columns(3)
    r1.metric("Basket Today",f"₦{tot:,.0f}/month")
    r2.metric(f"Same basket in {start_year}",f"₦{t0:,.0f}/month")
    if t0>0: r3.metric("Total Increase",f"₦{tot-t0:,.0f}",f"+{(tot-t0)/t0*100:.0f}%")
    if tot>0 and t0>0:
        tip(f"This basket costs ₦{tot-t0:,.0f} more per month than in {start_year} — that is ₦{(tot-t0)*12:,.0f} extra per year just on these four items.")

# ═══════════════════════════ EXCHANGE RATES ══════════════════════════════
elif page == "💵 Exchange Rates":
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">CBN NFEM Official · Parallel Market · Live Feed · {period_label}</div>
        <div class="page-title">Exchange Rate Intelligence</div>
        <div class="page-sub">The naira depreciated over 280% against the dollar from 2020 to its peak of ₦1,620/$ in Oct 2024. It has since recovered to ~₦1,400/$. The June 2023 FX unification was the single largest devaluation event in the dataset.</div>
        <div style="margin-top:0.5rem;font-size:0.72rem;color:#B8B0A0;">Live: {live_src} · {live_date}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Live CBN Rate",   f"₦{live_rate:,.0f}/$",  "● Live" if is_live else "● Cached")
    c2.metric("Parallel Market", f"₦{lf['parallel_market_rate']:,.0f}/$",
              f"₦{lf['parallel_market_rate']-fx.iloc[-2]['parallel_market_rate']:+,.0f}" if len(fx)>1 else "")
    c3.metric("Market Spread",   f"₦{lf['spread']:,.0f}", f"{lf['spread_pct']:.1f}% above CBN")
    c4.metric("Fuel Price",      f"₦{lf['fuel_price_per_litre_ngn']:,.0f}/L",
              f"₦{lf['fuel_price_per_litre_ngn']-fx.iloc[-2]['fuel_price_per_litre_ngn']:+,.0f}" if len(fx)>1 else "")
    st.markdown("<br>", unsafe_allow_html=True)
    c5,c6,c7,c8=st.columns(4)
    base_fx_rate=fx.iloc[0]["cbn_official_rate"]
    deval=(lf["cbn_official_rate"]-base_fx_rate)/base_fx_rate*100
    peak_r=fx["cbn_official_rate"].max()
    rec=(peak_r-live_rate)/peak_r*100
    c5.metric(f"Change vs {start_year}", f"{deval:+.0f}%", f"From ₦{base_fx_rate:,.0f}/$ baseline")
    c6.metric("$500 in Naira Today",     f"₦{live_rate*500:,.0f}", f"Was ₦{base_fx_rate*500:,.0f} in {start_year}")
    c7.metric("Peak in Period",          f"₦{peak_r:,.0f}/$", f"{fx.loc[fx['cbn_official_rate'].idxmax(),'label']}")
    c8.metric("Recovery from Peak",      f"{rec:.1f}%", f"₦{peak_r-live_rate:,.0f} stronger")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Two charts side by side
    col_l, col_r = st.columns([3,2])
    with col_l:
        sec("CBN Official vs Parallel Market Rate",
            f"The official CBN NFEM rate (green) vs the parallel/black market rate (red dashed) for {period_label}. The gold dashed line shows today's live rate. A large gap between the two lines signals dollar scarcity. Post-FX-unification (June 2023), the spread collapsed as the official rate was allowed to weaken toward market reality.")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=fx["date"],y=fx["cbn_official_rate"],name="CBN Official",mode="lines",line=dict(color="#2ECC7A",width=2.5),fill="tozeroy",fillcolor="rgba(46,204,122,0.05)"))
        fig.add_trace(go.Scatter(x=fx["date"],y=fx["parallel_market_rate"],name="Parallel Mkt",mode="lines",line=dict(color="#E05A30",width=2,dash="dot")))
        fig.add_hline(y=live_rate,line_dash="dash",line_color="#F0C040",annotation_text=f"Live: ₦{live_rate:,.0f}",annotation_font_color="#F0C040",annotation_font_size=10)
        if start_year<=2023<=end_year:
            fig.add_vrect(x0="2023-06-15",x1="2023-07-01",fillcolor="rgba(240,192,64,0.1)",line_width=0,annotation_text="FX Unification",annotation_font_color="#F0C040",annotation_font_size=9)
        fig.update_layout(**theme(f"USD/NGN — {period_label}", height=320, yaxis=dict(title="₦ per $1")))
        st.plotly_chart(fig, use_container_width=True)
        tip(f"From the start of {period_label}, the naira has {'appreciated' if deval<0 else 'depreciated'} {abs(deval):.0f}% against the dollar. At the peak of ₦{peak_r:,.0f}/$, it has since recovered {rec:.1f}%.")

    with col_r:
        sec("Parallel Market Premium",
            f"The naira premium over the official rate for each period in {period_label}. A high premium means most Nigerians cannot access dollars at the official rate. The near-collapse post-June 2023 shows how FX unification dramatically reduced the black market incentive.")
        fig2=go.Figure(go.Bar(x=fx["label"],y=fx["spread"],
            marker=dict(color=fx["spread"],colorscale=[[0,"#1A8A4A"],[0.5,"#F0C040"],[1,"#E05A30"]]),
            text=[f"₦{v:,.0f}" for v in fx["spread"]],
            textposition="outside",textfont=dict(size=8,color="#F5F0E8")))
        fig2.update_layout(**theme("Parallel Market Premium (₦)", height=320, showlegend=False,
            xaxis=dict(tickangle=-45,tickfont=dict(color="#B8B0A0",size=9)),
            yaxis=dict(title="₦ spread")))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    sec("Fuel Price vs Exchange Rate Correlation",
        f"Dual-axis chart: petrol pump price (gold, left axis) vs CBN official rate (green dashed, right axis) for {period_label}. The correlation is strong — as the naira weakens, fuel prices rise because Nigeria imports refined petroleum. The May 2023 subsidy removal created an abrupt step-change in fuel prices that temporarily broke the smooth correlation.")
    fig3=go.Figure()
    fig3.add_trace(go.Scatter(x=fx["date"],y=fx["fuel_price_per_litre_ngn"],name="Fuel (₦/L)",mode="lines+markers",line=dict(color="#F0C040",width=2.5),yaxis="y1"))
    fig3.add_trace(go.Scatter(x=fx["date"],y=fx["cbn_official_rate"],name="USD/NGN",mode="lines+markers",line=dict(color="#2ECC7A",width=2,dash="dot"),yaxis="y2"))
    fig3.update_layout(**theme(f"Fuel Price vs USD/NGN — {period_label}", height=290,
        yaxis=dict(title="Fuel ₦/L",gridcolor="rgba(46,204,122,0.1)",tickfont=dict(color="#B8B0A0",size=10)),
        yaxis2=dict(title="₦ per $1",overlaying="y",side="right",tickfont=dict(color="#B8B0A0",size=10))))
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════ HARDSHIP INDEX ══════════════════════════════
elif page == "🔥 Hardship Index":
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Composite Economic Stress Indicator · {period_label}</div>
        <div class="page-title">Nigeria Hardship Index</div>
        <div class="page-sub">A single score (0–100) combining food inflation (45%), headline inflation (30%), and exchange rate pressure (25%) into one measure of economic stress for the average Nigerian household. Higher = harder.</div>
    </div>""", unsafe_allow_html=True)

    hi=lh["hardship_index"]; sc="#2ECC7A" if hi<=50 else "#F0C040" if hi<=70 else "#E05A30"
    peak_hi=hardship["hardship_index"].max()
    peak_month=hardship.loc[hardship["hardship_index"].idxmax(),"date"].strftime("%b %Y")

    st.markdown(f"""
    <div style="background:#132A1C;border:1px solid rgba(46,204,122,0.2);border-radius:14px;padding:1.6rem 2rem;margin-bottom:1.2rem;border-top:3px solid {sc};">
        <div style="display:flex;gap:2.5rem;align-items:center;flex-wrap:wrap;">
            <div>
                <span class="lbl">Current Hardship Index — {hardship.iloc[-1]['date'].strftime('%b %Y')}</span>
                <div style="font-family:'Syne',sans-serif;font-size:5rem;font-weight:800;color:{sc};line-height:1;margin:0.2rem 0;">{hi:.0f}</div>
                <div style="font-family:'Syne',sans-serif;font-size:0.95rem;color:{sc};font-weight:700;">{lh['hardship_label']}</div>
                <div style="font-size:0.75rem;color:#B8B0A0;margin-top:0.3rem;">Peak in period: {peak_hi:.0f} ({peak_month})</div>
            </div>
            <div style="flex:1;min-width:260px;">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:0.8rem;">
                    <div><span class="lbl">Food (45%)</span>
                        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#E05A30;">{lh['food_score']:.0f}<span style="font-size:0.85rem;color:#B8B0A0;">/100</span></div>
                        <div style="font-size:0.72rem;color:#B8B0A0;">Food infl: {li['food_inflation_pct']:.1f}%</div></div>
                    <div><span class="lbl">Inflation (30%)</span>
                        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#F0C040;">{lh['inf_score']:.0f}<span style="font-size:0.85rem;color:#B8B0A0;">/100</span></div>
                        <div style="font-size:0.72rem;color:#B8B0A0;">Headline: {li['headline_inflation_pct']:.1f}%</div></div>
                    <div><span class="lbl">FX (25%)</span>
                        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#2ECC7A;">{lh['fx_score']:.0f}<span style="font-size:0.85rem;color:#B8B0A0;">/100</span></div>
                        <div style="font-size:0.72rem;color:#B8B0A0;">Rate: ₦{live_rate:,.0f}/$</div></div>
                </div>
                <div style="font-size:0.73rem;color:#B8B0A0;border-top:1px solid rgba(46,204,122,0.15);padding-top:0.7rem;line-height:1.7;">
                    <span style="color:#2ECC7A;font-weight:600;">0–30 Stable</span> · <span style="color:#F0C040;font-weight:600;">31–50 Moderate</span> · <span style="color:#F0C040;font-weight:600;">51–70 High</span> · <span style="color:#E05A30;font-weight:600;">71–85 Severe</span> · <span style="color:#E05A30;font-weight:600;">86–100 Crisis</span>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Two charts side by side
    col_l, col_r = st.columns(2)
    with col_l:
        sec(f"Hardship Index Over Time — {period_label}",
            "A rising line means conditions are worsening for the average Nigerian; falling means improvement. The threshold lines mark the boundaries between score bands. The index peaked when three shocks converged: subsidy removal, FX unification, and global food price inflation.")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hardship["date"],y=hardship["hardship_index"],mode="lines",line=dict(color="#2ECC7A",width=2.5),fill="tozeroy",fillcolor="rgba(46,204,122,0.07)"))
        for lv,lb,co in [(30,"Moderate","#F0C040"),(50,"High","#F0A820"),(70,"Severe","#E05A30")]:
            if hardship["hardship_index"].max()>=lv:
                fig.add_hline(y=lv,line_dash="dot",line_color=co,annotation_text=lb,annotation_font_color=co,annotation_font_size=9)
        fig.update_layout(**theme(f"Hardship Index — {period_label}", height=300, showlegend=False,
            yaxis=dict(range=[0,100],title="Score (0–100)")))
        st.plotly_chart(fig, use_container_width=True)
        tip(f"Index peaked at {peak_hi:.0f}/100 in {peak_month}, has since fallen to {hi:.0f}/100. The biggest driver of improvement is food inflation falling from 40%+ to {li['food_inflation_pct']:.1f}%.")

    with col_r:
        sec("Component Breakdown Over Time",
            "Stacked area showing how each component contributed to the total score. When food pressure (red) dominates the stack, food inflation is the primary hardship driver. When FX pressure (green) is large, it means currency depreciation is amplifying import costs. Use this to identify which policy levers matter most at any given time.")
        fig2=go.Figure()
        for cn,lb,co in [("food_score","Food (45%)","#E05A30"),("inf_score","Infl (30%)","#F0C040"),("fx_score","FX (25%)","#2ECC7A")]:
            fig2.add_trace(go.Scatter(x=hardship["date"],y=hardship[cn],name=lb,mode="lines",line=dict(color=co,width=2),stackgroup="one"))
        fig2.update_layout(**theme(f"Component Breakdown — {period_label}", height=300, yaxis=dict(title="Score")))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    sec("Hardship Index vs Headline Inflation",
        f"Dual-axis chart overlaying the Hardship Index against headline inflation for {period_label}. When the two lines diverge, it means food prices or FX pressure are amplifying hardship beyond what the headline CPI captures — exactly what happened during 2023–2024 when food inflation ran at 40%+ while headline was 'only' 34%.")
    merged_hi=hardship.merge(inflation[["date","headline_inflation_pct"]],on="date",how="left")
    fig3=go.Figure()
    fig3.add_trace(go.Scatter(x=merged_hi["date"],y=merged_hi["hardship_index"],name="Hardship Index",line=dict(color="#2ECC7A",width=2.5),yaxis="y1"))
    fig3.add_trace(go.Scatter(x=merged_hi["date"],y=merged_hi["headline_inflation_pct"],name="Headline Inflation %",line=dict(color="#F0C040",width=2,dash="dot"),yaxis="y2"))
    fig3.update_layout(**theme(f"Hardship Index vs Headline Inflation — {period_label}", height=290,
        yaxis=dict(title="Hardship Score",gridcolor="rgba(46,204,122,0.1)",tickfont=dict(color="#B8B0A0",size=10)),
        yaxis2=dict(title="Inflation %",overlaying="y",side="right",tickfont=dict(color="#B8B0A0",size=10))))
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════ METHODOLOGY ════════════════════════════════
elif page == "📖 Methodology":
    st.markdown("""
    <div style="margin-bottom:1.4rem;padding-bottom:1rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Transparency · Sources · Design · Limitations</div>
        <div class="page-title">Methodology</div>
        <div class="page-sub">Everything about how this platform was built — data sources, the processing pipeline, indicator definitions, design decisions, and known limitations. Built for transparency so anyone can evaluate, critique, or replicate this work.</div>
    </div>""", unsafe_allow_html=True)

    def mcard(bc,tc,title,body):
        st.markdown(f"""<div style="background:#132A1C;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:1.4rem 1.8rem;margin-bottom:1rem;border-left:4px solid {bc};">
        <div style="font-family:'Syne',sans-serif;font-size:0.66rem;text-transform:uppercase;letter-spacing:0.14em;color:{tc};font-weight:700;margin-bottom:0.7rem;">{title}</div>
        {body}</div>""", unsafe_allow_html=True)

    mcard("#2ECC7A","#2ECC7A","About This Project",
    """<p style="font-size:0.86rem;color:#F5F0E8;line-height:1.85;margin:0;">
    The <strong style="color:#2ECC7A;">Naija Cost Tracker</strong> is a real-time Nigerian cost of living intelligence platform that makes economic data accessible to everyday Nigerians, policymakers, researchers, and businesses. Built with Python, Streamlit, dbt, and Plotly — a modern open-source data stack — it draws exclusively on official Nigerian government and international data sources.<br><br>
    The platform's core belief: data should not live only in government PDFs. It should be visual, interactive, and honest. The Global Time Period Filter in the sidebar lets you isolate any year or range — all charts, metrics, and insights update dynamically to reflect only that period, so you can compare conditions across different economic eras in Nigeria's recent history.</p>""")

    mcard("#F0C040","#F0C040","Data Sources",
    """<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;">
    <div><div style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">1. NBS — nigerianstat.gov.ng</div>
    <p style="font-size:0.81rem;color:#B8B0A0;line-height:1.75;margin:0;">Monthly CPI reports (headline, food, core inflation), quarterly Selected Food Prices Watch, and state-level CPI indices. <strong style="color:#F5F0E8;">Critical note:</strong> NBS rebased CPI in late 2024 (base year 2009 → 2024=100, COICOP 2018, 934 product varieties). Figures before and after Dec 2024 are structurally different. Latest release: Jan 2026 — Headline 15.10%, Food 8.89%, Core 17.72%.</p></div>
    <div><div style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">2. CBN — cbn.gov.ng</div>
    <p style="font-size:0.81rem;color:#B8B0A0;line-height:1.75;margin:0;">NFEM (Nigerian Foreign Exchange Market) official rate — a daily volume-weighted average of willing-buyer-willing-seller FX transactions since the June 2023 FX unification policy. Pre-June 2023, CBN maintained an artificially pegged rate separate from market reality. Confirmed March 2026 rate: ₦1,398–1,406/$.</p></div>
    <div><div style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">3. Open Exchange Rates API — open.er-api.com</div>
    <p style="font-size:0.81rem;color:#B8B0A0;line-height:1.75;margin:0;">Free public API (no key required). Provides live USD/NGN rates, fetched on every app load and cached for 5 minutes. Falls back to latest confirmed CBN rate if unavailable. Green ● LIVE badge = live data; Gold ● CACHED badge = fallback.</p></div>
    <div><div style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">4. NNPC — Fuel Pump Prices</div>
    <p style="font-size:0.81rem;color:#B8B0A0;line-height:1.75;margin:0;">Petrol pump price data from NNPC official announcements. The subsidy removal on 29 May 2023 caused pump price to jump from ₦165/L to ₦617/L overnight — the single largest cost-of-living shock in this dataset. Fuel directly drives transport and food prices nationwide.</p></div>
    </div>""")

    mcard("#2ECC7A","#2ECC7A","Data Processing Pipeline",
    """<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
    <div style="background:#0D1F14;border:1px solid rgba(46,204,122,0.15);border-radius:8px;padding:0.9rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;color:#2ECC7A;margin-bottom:0.4rem;">STAGE 1 — INGEST</div>
        <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Python scripts in <code style="color:#2ECC7A;">scrapers/</code> fetch NBS, CBN, and live FX data. Raw data saved as CSV in <code style="color:#2ECC7A;">data/</code>. Exchange rate fetches live on every load. Inflation data updates when NBS publishes monthly. Historical seed data is embedded in scraper code, verified against official publications.</p>
    </div>
    <div style="background:#0D1F14;border:1px solid rgba(240,192,64,0.15);border-radius:8px;padding:0.9rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;color:#F0C040;margin-bottom:0.4rem;">STAGE 2 — TRANSFORM (dbt)</div>
        <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">dbt models clean raw data into staging and mart layers. Staging handles typing and renaming. Mart models (<code style="color:#F0C040;">mart_hardship_index</code>, <code style="color:#F0C040;">mart_inflation_trends</code>) apply business logic — weighted composites, normalization, YoY comparisons, and period classification. All models documented with column descriptions and dbt tests.</p>
    </div>
    <div style="background:#0D1F14;border:1px solid rgba(224,90,48,0.15);border-radius:8px;padding:0.9rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;color:#E05A30;margin-bottom:0.4rem;">STAGE 3 — PRESENT</div>
        <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Streamlit renders the dashboard. All charts built with Plotly for interactivity. Data cached 5 minutes via <code style="color:#E05A30;">@st.cache_data</code>. The global year filter in the sidebar dynamically re-slices all datasets — every chart, metric, and insight reflects only the selected time period. Deployable to Streamlit Cloud as a free public URL.</p>
    </div>
    </div>""")

    mcard("#E05A30","#E05A30","Nigeria Hardship Index — Calculation",
    f"""<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:0.8rem;">
    <div style="background:#0D1F14;border-radius:8px;padding:0.9rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;color:#E05A30;margin-bottom:0.3rem;">Food Inflation — 45%</div>
        <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Food is 56–60% of a typical Nigerian household's budget. Normalization: 0%=0, 45%=100. Score clipped to [0,100].</p>
    </div>
    <div style="background:#0D1F14;border-radius:8px;padding:0.9rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;color:#F0C040;margin-bottom:0.3rem;">Headline Inflation — 30%</div>
        <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Overall CPI including services, transport, healthcare. Normalization: 0%=0, 40%=100 (calibrated to Nigeria's observed worst case).</p>
    </div>
    <div style="background:#0D1F14;border-radius:8px;padding:0.9rem;">
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;color:#2ECC7A;margin-bottom:0.3rem;">FX Depreciation — 25%</div>
        <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Currency weakness raises import costs for food, fuel, medicine. Range: ₦360 (2020 baseline)=0 to ₦2,000=100.</p>
    </div>
    </div>
    <div style="background:#0D1F14;border-radius:8px;padding:0.9rem;font-size:0.81rem;color:#B8B0A0;line-height:1.75;">
        <strong style="color:#FFFFFF;">Formula:</strong> Score = (food×0.45) + (headline×0.30) + (FX×0.25) &nbsp;·&nbsp;
        <strong style="color:#FFFFFF;">Current: <span style="color:{sc}">{lh['hardship_index']:.0f}/100 — {lh['hardship_label']}</span></strong>
    </div>""")

    mcard("#2ECC7A","#2ECC7A","Design Philosophy",
    """<p style="font-size:0.83rem;color:#B8B0A0;line-height:1.85;margin:0;">
    <strong style="color:#FFFFFF;">Colour:</strong> Dark forest green base (#0D1F14) from the Nigerian flag. Gold accents from Ankara fabric patterns. Brick red signals stress. The system creates visual intuition without reading legends: green = improving, gold = caution, red = pressure.<br><br>
    <strong style="color:#FFFFFF;">Typography:</strong> Syne (geometric bold) for headings and numbers. Inter (neutral) for descriptions. Every section includes a written explanation of what the chart shows and why it matters — and an insight box drawing the key analytical conclusion.<br><br>
    <strong style="color:#FFFFFF;">Dynamic filtering:</strong> The global year range slider filters every chart, metric, and insight simultaneously — enabling comparison between economic eras (e.g. 2020–2022 = pre-crisis baseline vs 2023–2024 = peak inflation era vs 2025–2026 = recovery period).</p>""")

    mcard("#F0C040","#F0C040","Known Limitations",
    """<ul style="font-size:0.81rem;color:#B8B0A0;line-height:2;margin:0;padding-left:1.1rem;">
    <li><strong style="color:#F5F0E8;">NBS CPI rebase (Dec 2024):</strong> Data before and after Dec 2024 uses different methodologies and base years. Not directly comparable across this break.</li>
    <li><strong style="color:#F5F0E8;">Food prices are quarterly estimates</strong> from NBS surveys — not real-time retail scanner data. Prices at any specific market on any day will differ.</li>
    <li><strong style="color:#F5F0E8;">Parallel market rate is approximate</strong> — estimated from publicly reported sources. Not a precise transaction rate.</li>
    <li><strong style="color:#F5F0E8;">Hardship Index is proprietary</strong> — not an official government statistic. Should not be cited as such.</li>
    <li><strong style="color:#F5F0E8;">Historical data is manually verified</strong> against NBS and CBN publications. Minor discrepancies may exist due to source revisions.</li>
    </ul>""")

# ═══════════════════════════ FOOTER ════════════════════════════════════
st.markdown(f"""
<div style="margin-top:2.5rem;padding:1rem 0;border-top:1px solid rgba(46,204,122,0.18);
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.4rem;">
    <div style="font-size:0.7rem;color:#B8B0A0;">
        🇳🇬 <span style="color:#2ECC7A;font-weight:600;">Naija Cost Tracker</span>
        &nbsp;—&nbsp; Built with Streamlit · Python · dbt · Plotly &nbsp;·&nbsp;
        <span style="color:#F0C040;">Showing: {period_label}</span>
    </div>
    <div style="font-size:0.68rem;color:#B8B0A0;">
        FX: {live_src} · NBS: Jan 2026 · {datetime.now().strftime('%b %d, %Y %H:%M')}
    </div>
</div>""", unsafe_allow_html=True)