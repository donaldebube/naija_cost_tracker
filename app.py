"""
Naija Cost Tracker — Main App
==============================
Nigerian Cost of Living Intelligence Platform
Redesigned: dark theme, high contrast, fully readable
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import (
    load_inflation,
    load_food_prices,
    load_state_inflation,
    load_exchange_rates,
    load_macro_indicators,
    load_live_rate,
    compute_hardship_index,
)

st.set_page_config(
    page_title="Naija Cost Tracker",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded",
)

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-base:      #0D1F14;
    --bg-card:      #132A1C;
    --bg-sidebar:   #0A1910;
    --green-bright: #2ECC7A;
    --green-mid:    #1A8A4A;
    --gold:         #F0C040;
    --brick:        #E05A30;
    --cream:        #F5F0E8;
    --cream-dim:    #B8B0A0;
    --white:        #FFFFFF;
    --border:       rgba(46,204,122,0.18);
    --border-gold:  rgba(240,192,64,0.25);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--cream) !important;
}
.stApp { background-color: var(--bg-base) !important; }

[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-gold) !important;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] .stSelectbox label {
    color: var(--gold) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.68rem !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(46,204,122,0.08) !important;
    border: 1px solid var(--border) !important;
    color: var(--cream) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div > div { color: var(--cream) !important; }

[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
    border-top: 3px solid var(--green-bright) !important;
}
[data-testid="metric-container"] label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: var(--cream-dim) !important;
    font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--white) !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    color: var(--green-bright) !important;
}

h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: var(--white) !important; }
p, li { color: var(--cream) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    border-radius: 7px !important;
    color: var(--cream-dim) !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] { background: var(--green-mid) !important; color: var(--white) !important; }

[data-testid="stMultiSelect"] label {
    color: var(--cream) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMultiSelect"] > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-testid="stNumberInput"] label { color: var(--cream) !important; font-size: 0.82rem !important; }
[data-testid="stNumberInput"] input {
    background: var(--bg-card) !important;
    color: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

.stAlert {
    background: rgba(240,192,64,0.1) !important;
    border: 1px solid var(--border-gold) !important;
    border-left: 4px solid var(--gold) !important;
    border-radius: 10px !important;
}
.stAlert p { color: var(--cream) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

.eyebrow {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--green-bright);
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--white);
    line-height: 1.1;
    margin: 0 0 0.6rem 0;
}
.page-subtitle { font-size: 0.92rem; color: var(--cream-dim); line-height: 1.6; max-width: 580px; }
.label-sm {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--cream-dim);
    font-weight: 700;
}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)

CHART = {
    "paper_bgcolor": "#132A1C",
    "plot_bgcolor":  "#132A1C",
    "font":   {"family": "Inter, sans-serif", "color": "#F5F0E8", "size": 12},
    "margin": {"t": 50, "b": 40, "l": 55, "r": 20},
    "colorway": ["#2ECC7A", "#F0C040", "#E05A30", "#1A8A4A", "#C49A28"],
    "xaxis":  {"gridcolor": "rgba(46,204,122,0.1)", "linecolor": "rgba(46,204,122,0.2)", "tickfont": {"color": "#B8B0A0"}},
    "yaxis":  {"gridcolor": "rgba(46,204,122,0.1)", "linecolor": "rgba(46,204,122,0.2)", "tickfont": {"color": "#B8B0A0"}},
    "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": "#F5F0E8"}},
    "title":  {"font": {"family": "Syne, sans-serif", "color": "#FFFFFF", "size": 14}},
}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1.6rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:0.62rem;text-transform:uppercase;
                    letter-spacing:0.18em;color:#2ECC7A;font-weight:700;margin-bottom:0.6rem;">🇳🇬 Nigeria</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#FFFFFF;line-height:1.1;">
            Naija Cost<br>Tracker
        </div>
        <div style="font-size:0.75rem;color:#B8B0A0;margin-top:0.5rem;line-height:1.5;">
            Cost of living intelligence<br>for everyday Nigerians
        </div>
    </div>
    <hr style="border-color:rgba(46,204,122,0.18);margin:0 0 1.2rem 0;">
    """, unsafe_allow_html=True)

    page = st.selectbox(
        "NAVIGATE",
        ["🏠 Overview", "📈 Inflation", "🛒 Food Prices", "💵 Exchange Rates", "🔥 Hardship Index"],
    )

    st.markdown("<hr style='border-color:rgba(46,204,122,0.18);margin:1.2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem;color:#B8B0A0;line-height:1.8;">
        <div style="font-family:'Syne',sans-serif;color:#F0C040;font-size:0.62rem;text-transform:uppercase;
                    letter-spacing:0.12em;margin-bottom:0.5rem;font-weight:700;">Data Sources</div>
        National Bureau of Statistics<br>
        Central Bank of Nigeria<br>
        World Bank Open Data<br>
        ExchangeRate-API
    </div>
    <div style="font-size:0.65rem;color:rgba(184,176,160,0.4);margin-top:1rem;">Historical data · 2020–2024</div>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_all_data():
    inflation = load_inflation()
    food      = load_food_prices()
    states    = load_state_inflation()
    fx        = load_exchange_rates()
    macro     = load_macro_indicators()
    live      = load_live_rate()
    hardship  = compute_hardship_index(inflation, fx)
    return inflation, food, states, fx, macro, live, hardship

inflation, food, states, fx, macro, live, hardship = get_all_data()
latest_inf      = inflation.iloc[-1]
latest_fx       = fx.iloc[-1]
latest_hardship = hardship.iloc[-1]


# ═══════════════════════════════════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Nigerian Cost of Living Intelligence</div>
        <div class="page-title">What is ₦1,000 worth<br>in Nigeria today?</div>
        <div class="page-subtitle">Real data. Real impact. Tracking how inflation, food prices, and
        exchange rates affect everyday Nigerians — from Lagos to Kano.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Headline Inflation", f"{latest_inf['headline_inflation_pct']:.1f}%",
                  f"{latest_inf['headline_inflation_pct'] - inflation.iloc[-2]['headline_inflation_pct']:+.1f}% MoM")
    with col2:
        st.metric("Food Inflation", f"{latest_inf['food_inflation_pct']:.1f}%",
                  f"{latest_inf['food_inflation_pct'] - inflation.iloc[-2]['food_inflation_pct']:+.1f}% MoM")
    with col3:
        st.metric("USD / NGN Rate", f"₦{latest_fx['cbn_official_rate']:,.0f}",
                  f"₦{latest_fx['cbn_official_rate'] - fx.iloc[-2]['cbn_official_rate']:+,.0f} vs prev")
    with col4:
        hi = latest_hardship["hardship_index"]
        st.metric("Hardship Index", f"{hi:.0f} / 100", latest_hardship["hardship_label"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="label-sm" style="margin-bottom:0.6rem;">Purchasing Power Erosion — ₦10,000 Over Time</div>', unsafe_allow_html=True)
        baseline_inf = inflation[inflation["date"].dt.year == 2020]["headline_inflation_pct"].mean()
        inflation["purchasing_power"] = 10000 / (1 + (inflation["headline_inflation_pct"] - baseline_inf) / 100)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=inflation["date"], y=inflation["purchasing_power"],
            mode="lines", fill="tozeroy", line=dict(color="#2ECC7A", width=2.5),
            fillcolor="rgba(46,204,122,0.08)", name="Real value"))
        fig.add_hline(y=10000, line_dash="dot", line_color="#F0C040",
                      annotation_text="₦10,000 baseline (2020)",
                      annotation_font_color="#F0C040", annotation_font_size=11)
        fig.update_layout(**CHART, height=290, showlegend=False, yaxis_title="Real Value (₦)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="label-sm" style="margin-bottom:0.6rem;">Headline vs Food Inflation</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=inflation["date"], y=inflation["headline_inflation_pct"],
            name="Headline", line=dict(color="#2ECC7A", width=2.5)))
        fig2.add_trace(go.Scatter(x=inflation["date"], y=inflation["food_inflation_pct"],
            name="Food", line=dict(color="#E05A30", width=2.5)))
        fig2.update_layout(**CHART, height=290, yaxis_title="%", legend=dict(orientation="h", y=1.1, x=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class="label-sm" style="margin-bottom:0.4rem;">💡 Remote Worker / Freelancer Salary Calculator</div>
    <div style="font-size:0.84rem;color:#B8B0A0;margin-bottom:1rem;">See what your USD income is really worth in Nigeria over time</div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        salary_usd = st.number_input("Monthly income (USD)", min_value=100, max_value=50000, value=1000, step=100)
    fx["salary_ngn"] = fx["cbn_official_rate"] * salary_usd
    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=fx["label"], y=fx["salary_ngn"],
            marker_color="#1A8A4A", marker_line_color="#2ECC7A", marker_line_width=0.5,
            text=[f"₦{v/1000:.0f}k" for v in fx["salary_ngn"]],
            textposition="outside", textfont=dict(size=9, color="#F5F0E8")))
        fig3.update_layout(**CHART, height=240, showlegend=False, yaxis_title="₦ NGN", xaxis_tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)

    current_ngn  = latest_fx["cbn_official_rate"] * salary_usd
    year_ago_ngn = fx[fx["date"].dt.year == 2022]["cbn_official_rate"].mean() * salary_usd
    diff = current_ngn - year_ago_ngn
    st.info(f"💬  Your ${salary_usd:,}/month was worth ₦{year_ago_ngn:,.0f} in 2022. "
            f"Today it converts to ₦{current_ngn:,.0f} — ₦{abs(diff):,.0f} {'more' if diff>0 else 'less'} "
            f"in naira terms, but real purchasing power has fallen sharply due to food inflation.")


# ═══════════════════════════════════════════════════════════════════════
# INFLATION
# ═══════════════════════════════════════════════════════════════════════
elif page == "📈 Inflation":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">National Bureau of Statistics · Monthly CPI Data</div>
        <div class="page-title">Inflation Tracker</div>
        <div class="page-subtitle">Headline, food, and core inflation trends for Nigeria (2020–2024)</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Headline", f"{latest_inf['headline_inflation_pct']:.1f}%",
                f"{latest_inf['headline_inflation_pct'] - inflation.iloc[-13]['headline_inflation_pct']:+.1f}% YoY")
    col2.metric("Latest Food", f"{latest_inf['food_inflation_pct']:.1f}%",
                f"{latest_inf['food_inflation_pct'] - inflation.iloc[-13]['food_inflation_pct']:+.1f}% YoY")
    col3.metric("Core Inflation", f"{latest_inf['core_inflation_pct']:.1f}%",
                f"{latest_inf['core_inflation_pct'] - inflation.iloc[-13]['core_inflation_pct']:+.1f}% YoY")

    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure()
    for col_name, label, color in [
        ("headline_inflation_pct", "Headline", "#2ECC7A"),
        ("food_inflation_pct",     "Food",     "#E05A30"),
        ("core_inflation_pct",     "Core",     "#F0C040"),
    ]:
        fig.add_trace(go.Scatter(x=inflation["date"], y=inflation[col_name],
            name=label, mode="lines+markers",
            line=dict(color=color, width=2.5), marker=dict(size=4, color=color)))
    fig.add_vrect(x0="2023-06-01", x1="2023-08-01", fillcolor="rgba(224,90,48,0.08)", line_width=0,
                  annotation_text="FX Unification", annotation_font_color="#E05A30", annotation_font_size=10)
    fig.add_vrect(x0="2023-05-01", x1="2023-06-01", fillcolor="rgba(240,192,64,0.08)", line_width=0,
                  annotation_text="Subsidy Removal", annotation_font_color="#F0C040", annotation_font_size=10)
    fig.update_layout(**CHART, height=380, title="Nigeria Inflation Rates (%)",
                      yaxis_title="Inflation Rate (%)", legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="label-sm" style="margin:1.2rem 0 0.8rem 0;">State-Level Inflation (2024)</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        s = states.sort_values("inflation_2024_pct", ascending=True)
        fig2 = go.Figure(go.Bar(x=s["inflation_2024_pct"], y=s["state"], orientation="h",
            marker=dict(color=s["inflation_2024_pct"],
                        colorscale=[[0,"#1A8A4A"],[0.5,"#F0C040"],[1,"#E05A30"]],
                        showscale=True,
                        colorbar=dict(title="%", tickfont={"color":"#F5F0E8"}, titlefont={"color":"#F5F0E8"}))))
        fig2.update_layout(**CHART, height=440, title="2024 Inflation by State (%)", xaxis_title="%", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
    with col_b:
        states["yoy_change"] = states["inflation_2024_pct"] - states["inflation_2023_pct"]
        s2 = states.sort_values("yoy_change", ascending=True)
        fig3 = go.Figure(go.Bar(x=s2["yoy_change"], y=s2["state"], orientation="h",
            marker_color=["#E05A30" if v > 0 else "#2ECC7A" for v in s2["yoy_change"]]))
        fig3.update_layout(**CHART, height=440, title="Year-on-Year Change (2023 → 2024)",
                           xaxis_title="Percentage points", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="label-sm" style="margin-bottom:0.8rem;">Annual Averages</div>', unsafe_allow_html=True)
    annual = inflation.groupby("year")[["headline_inflation_pct","food_inflation_pct","core_inflation_pct"]]\
                      .mean().round(1).reset_index()
    annual.columns = ["Year","Headline (%)","Food (%)","Core (%)"]
    st.dataframe(annual, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════
# FOOD PRICES
# ═══════════════════════════════════════════════════════════════════════
elif page == "🛒 Food Prices":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">NBS Selected Food Prices Watch</div>
        <div class="page-title">Food Price Tracker</div>
        <div class="page-subtitle">Track what Nigerians actually pay for staples — garri, rice, tomatoes, and more</div>
    </div>
    """, unsafe_allow_html=True)

    food_items = {
        "rice_50kg_ngn":      "Rice (50kg bag)",
        "garri_50kg_ngn":     "Garri (50kg bag)",
        "tomatoes_1kg_ngn":   "Tomatoes (1kg)",
        "cooking_oil_5l_ngn": "Cooking Oil (5L)",
        "eggs_crate_ngn":     "Eggs (1 crate)",
        "bread_loaf_ngn":     "Bread (1 loaf)",
        "beef_1kg_ngn":       "Beef (1kg)",
    }
    first_food  = food.iloc[0]
    latest_food = food.iloc[-1]

    st.markdown('<div class="label-sm" style="margin-bottom:0.8rem;">Price Changes: Jan 2022 → Latest</div>', unsafe_allow_html=True)
    items_list = list(food_items.items())
    cols = st.columns(4)
    for i, (col_name, label) in enumerate(items_list[:4]):
        pct = ((latest_food[col_name] - first_food[col_name]) / first_food[col_name]) * 100
        cols[i].metric(label, f"₦{latest_food[col_name]:,.0f}", f"+{pct:.0f}% since 2022")
    cols2 = st.columns(3)
    for i, (col_name, label) in enumerate(items_list[4:]):
        pct = ((latest_food[col_name] - first_food[col_name]) / first_food[col_name]) * 100
        cols2[i].metric(label, f"₦{latest_food[col_name]:,.0f}", f"+{pct:.0f}% since 2022")

    st.markdown("<br>", unsafe_allow_html=True)
    selected_items = st.multiselect("Select food items to compare",
        options=list(food_items.keys()),
        default=["rice_50kg_ngn","garri_50kg_ngn","tomatoes_1kg_ngn"],
        format_func=lambda x: food_items[x])

    if selected_items:
        colors = ["#2ECC7A","#E05A30","#F0C040","#1A8A4A","#C49A28","#80C0A0","#B8B0A0"]
        fig = go.Figure()
        for i, item in enumerate(selected_items):
            fig.add_trace(go.Scatter(x=food["date"], y=food[item],
                name=food_items[item], mode="lines+markers",
                line=dict(color=colors[i % len(colors)], width=2.5), marker=dict(size=6)))
        fig.update_layout(**CHART, height=360, title="Food Price Trends (₦)",
                          yaxis_title="Price (₦)", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class="label-sm" style="margin-bottom:0.4rem;">🧺 Monthly Food Basket Calculator</div>
    <div style="font-size:0.84rem;color:#B8B0A0;margin-bottom:1rem;">Estimate what a typical household spends on food per month</div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    qty_rice  = c1.number_input("Rice bags/month",   0.0, 10.0, 0.5, 0.5)
    qty_garri = c2.number_input("Garri bags/month",  0.0, 10.0, 0.5, 0.5)
    qty_eggs  = c3.number_input("Egg crates/month",  0, 20, 4)
    qty_oil   = c4.number_input("Oil bottles/month", 0, 10, 1)
    total = (qty_rice * latest_food["rice_50kg_ngn"] + qty_garri * latest_food["garri_50kg_ngn"]
           + qty_eggs * latest_food["eggs_crate_ngn"] + qty_oil * latest_food["cooking_oil_5l_ngn"])
    total_2022 = (qty_rice * first_food["rice_50kg_ngn"] + qty_garri * first_food["garri_50kg_ngn"]
                + qty_eggs * first_food["eggs_crate_ngn"] + qty_oil * first_food["cooking_oil_5l_ngn"])
    r1, r2, r3 = st.columns(3)
    r1.metric("Basket Cost Today",       f"₦{total:,.0f}/month")
    r2.metric("Same basket in Jan 2022", f"₦{total_2022:,.0f}/month")
    r3.metric("Increase",                f"₦{total - total_2022:,.0f}", f"+{((total-total_2022)/total_2022*100):.0f}%")


# ═══════════════════════════════════════════════════════════════════════
# EXCHANGE RATES
# ═══════════════════════════════════════════════════════════════════════
elif page == "💵 Exchange Rates":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">CBN Official · Parallel Market · Fuel Prices</div>
        <div class="page-title">Exchange Rate Intelligence</div>
        <div class="page-subtitle">How the naira has moved — official rate, parallel market, and the gap between them</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CBN Official Rate", f"₦{latest_fx['cbn_official_rate']:,.0f}/$",
                f"₦{latest_fx['cbn_official_rate'] - fx.iloc[-2]['cbn_official_rate']:+,.0f}")
    col2.metric("Parallel Market",   f"₦{latest_fx['parallel_market_rate']:,.0f}/$",
                f"₦{latest_fx['parallel_market_rate'] - fx.iloc[-2]['parallel_market_rate']:+,.0f}")
    col3.metric("Market Spread",     f"₦{latest_fx['spread']:,.0f}", f"{latest_fx['spread_pct']:.1f}% premium")
    col4.metric("Fuel Price",        f"₦{latest_fx['fuel_price_per_litre_ngn']:,.0f}/L",
                f"₦{latest_fx['fuel_price_per_litre_ngn'] - fx.iloc[-2]['fuel_price_per_litre_ngn']:+,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])
    with col_l:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fx["date"], y=fx["cbn_official_rate"], name="CBN Official",
            mode="lines", line=dict(color="#2ECC7A", width=2.5),
            fill="tozeroy", fillcolor="rgba(46,204,122,0.06)"))
        fig.add_trace(go.Scatter(x=fx["date"], y=fx["parallel_market_rate"], name="Parallel Market",
            mode="lines", line=dict(color="#E05A30", width=2, dash="dot")))
        fig.add_vrect(x0="2023-06-15", x1="2023-07-01", fillcolor="rgba(240,192,64,0.1)", line_width=0,
                      annotation_text="FX Unification", annotation_font_color="#F0C040", annotation_font_size=9)
        fig.update_layout(**CHART, height=320, title="USD/NGN Exchange Rates Over Time",
                          yaxis_title="₦ per $1", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        fig2 = go.Figure(go.Bar(x=fx["label"], y=fx["spread"],
            marker=dict(color=fx["spread"], colorscale=[[0,"#1A8A4A"],[0.5,"#F0C040"],[1,"#E05A30"]]),
            text=[f"₦{v:,.0f}" for v in fx["spread"]],
            textposition="outside", textfont=dict(size=8, color="#F5F0E8")))
        fig2.update_layout(**CHART, height=320, title="Parallel Market Premium (₦ spread)",
                           yaxis_title="₦ spread", showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=fx["date"], y=fx["fuel_price_per_litre_ngn"], name="Fuel (₦/L)",
        mode="lines+markers", line=dict(color="#F0C040", width=2.5), yaxis="y1"))
    fig3.add_trace(go.Scatter(x=fx["date"], y=fx["cbn_official_rate"], name="USD/NGN",
        mode="lines+markers", line=dict(color="#2ECC7A", width=2, dash="dot"), yaxis="y2"))
    fig3.update_layout(**CHART, height=300, title="Fuel Price vs USD/NGN Rate — The Correlation",
        yaxis=dict(title="Fuel ₦/L", gridcolor="rgba(46,204,122,0.1)", tickfont={"color":"#B8B0A0"}),
        yaxis2=dict(title="₦ per $1", overlaying="y", side="right", tickfont={"color":"#B8B0A0"}),
        legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# HARDSHIP INDEX
# ═══════════════════════════════════════════════════════════════════════
elif page == "🔥 Hardship Index":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Composite Economic Stress Indicator</div>
        <div class="page-title">Nigeria Hardship Index</div>
        <div class="page-subtitle">A single number capturing how hard life is for the average Nigerian —
        combining food inflation (45%), headline inflation (30%), and exchange rate pressure (25%).</div>
    </div>
    """, unsafe_allow_html=True)

    latest_hi   = hardship.iloc[-1]
    hi_score    = latest_hi["hardship_index"]
    score_color = "#2ECC7A" if hi_score <= 50 else "#F0C040" if hi_score <= 70 else "#E05A30"

    st.markdown(f"""
    <div style="background:#132A1C;border:1px solid rgba(46,204,122,0.2);border-radius:16px;
                padding:2rem 2.5rem;margin-bottom:1.5rem;border-top:3px solid {score_color};">
        <div style="display:flex;gap:3rem;align-items:center;flex-wrap:wrap;">
            <div>
                <div class="label-sm">Current Hardship Index</div>
                <div style="font-family:'Syne',sans-serif;font-size:5.5rem;font-weight:800;
                            color:{score_color};line-height:1;margin:0.2rem 0;">{hi_score:.0f}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;color:{score_color};
                            font-weight:700;letter-spacing:0.04em;">{latest_hi['hardship_label']}</div>
            </div>
            <div style="flex:1;min-width:280px;">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem;margin-bottom:1rem;">
                    <div>
                        <div class="label-sm">Food Pressure</div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#E05A30;">
                            {latest_hi['food_score']:.0f}<span style="font-size:0.9rem;color:#B8B0A0;">/100</span></div>
                    </div>
                    <div>
                        <div class="label-sm">Inflation Pressure</div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#F0C040;">
                            {latest_hi['inf_score']:.0f}<span style="font-size:0.9rem;color:#B8B0A0;">/100</span></div>
                    </div>
                    <div>
                        <div class="label-sm">FX Pressure</div>
                        <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#2ECC7A;">
                            {latest_hi['fx_score']:.0f}<span style="font-size:0.9rem;color:#B8B0A0;">/100</span></div>
                    </div>
                </div>
                <div style="font-size:0.75rem;color:#B8B0A0;line-height:1.7;
                            border-top:1px solid rgba(46,204,122,0.15);padding-top:0.8rem;">
                    <span style="color:#2ECC7A;font-weight:600;">0–30 Stable</span> &nbsp;·&nbsp;
                    <span style="color:#F0C040;font-weight:600;">31–70 Moderate / High</span> &nbsp;·&nbsp;
                    <span style="color:#E05A30;font-weight:600;">71–100 Severe / Crisis</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hardship["date"], y=hardship["hardship_index"],
        mode="lines", line=dict(color="#2ECC7A", width=3),
        fill="tozeroy", fillcolor="rgba(46,204,122,0.07)", name="Hardship Index"))
    for level, label, color in [(30,"Moderate threshold","#F0C040"),(70,"Severe threshold","#E05A30")]:
        fig.add_hline(y=level, line_dash="dot", line_color=color,
                      annotation_text=label, annotation_font_color=color, annotation_font_size=10)
    fig.update_layout(**CHART, height=340, title="Nigeria Hardship Index Over Time (0–100)",
                      yaxis_title="Index Score", yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="label-sm" style="margin:1rem 0 0.8rem 0;">Component Breakdown Over Time</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for col_name, label, color in [
        ("food_score", "Food Pressure (45%)",      "#E05A30"),
        ("inf_score",  "Inflation Pressure (30%)", "#F0C040"),
        ("fx_score",   "FX Pressure (25%)",        "#2ECC7A"),
    ]:
        fig2.add_trace(go.Scatter(x=hardship["date"], y=hardship[col_name],
            name=label, mode="lines", line=dict(color=color, width=2), stackgroup="one"))
    fig2.update_layout(**CHART, height=300, yaxis_title="Score component",
                       legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#132A1C;border:1px solid rgba(240,192,64,0.2);border-radius:12px;
                padding:1.4rem 1.6rem;border-left:4px solid #F0C040;">
        <div class="label-sm" style="color:#F0C040;margin-bottom:0.5rem;">Methodology Note</div>
        <p style="font-size:0.86rem;color:#B8B0A0;line-height:1.8;margin:0;">
            The Hardship Index is a weighted composite of three normalized indicators:
            <span style="color:#E05A30;font-weight:600;">food inflation</span> (45% weight — the single largest
            household expenditure for most Nigerians),
            <span style="color:#F0C040;font-weight:600;">headline CPI inflation</span> (30%), and
            <span style="color:#2ECC7A;font-weight:600;">exchange rate pressure</span> (25%, measured as
            depreciation from a ₦360/$1 baseline). Each component is normalized to a 0–100 scale.
            Data sourced from NBS monthly CPI reports and CBN official rate publications.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.2rem 0;border-top:1px solid rgba(46,204,122,0.18);
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-size:0.72rem;color:#B8B0A0;">
        🇳🇬 <span style="color:#2ECC7A;font-weight:600;">Naija Cost Tracker</span>
        &nbsp;—&nbsp; Built with Streamlit · Python · dbt
    </div>
    <div style="font-size:0.7rem;color:#B8B0A0;">Data: NBS · CBN · World Bank · ExchangeRate-API</div>
</div>
""", unsafe_allow_html=True)