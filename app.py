"""
Naija Cost Tracker — Main App
==============================
Entry point for the Nigerian Cost of Living Intelligence Platform.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Naija Cost Tracker",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── THEME: Nigerian Aesthetic ───────────────────────────────────────────────
# Colors drawn from Nigerian flag, Ankara fabric patterns, Lagos energy
# Deep forest green · Warm white · Earthy gold · Brick red accent

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --green-deep:   #0A4A2F;
    --green-mid:    #1A6B45;
    --green-light:  #2E9E6B;
    --gold:         #D4A843;
    --gold-light:   #F0C96A;
    --cream:        #FAF7F0;
    --brick:        #C94B2A;
    --charcoal:     #1C1C1C;
    --grey-soft:    #E8E4DC;
    --text-main:    #1C1C1C;
    --text-muted:   #6B6456;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--text-main);
}

/* Main background */
.stApp {
    background-color: var(--cream);
    background-image:
        radial-gradient(circle at 10% 20%, rgba(10,74,47,0.04) 0%, transparent 50%),
        radial-gradient(circle at 90% 80%, rgba(212,168,67,0.06) 0%, transparent 50%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--green-deep) !important;
    border-right: 1px solid rgba(212,168,67,0.2);
}
[data-testid="stSidebar"] * {
    color: var(--cream) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {
    color: var(--gold-light) !important;
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(212,168,67,0.3) !important;
    color: var(--cream) !important;
    border-radius: 6px;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid var(--grey-soft);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    border-left: 4px solid var(--green-mid);
    transition: transform 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}
[data-testid="metric-container"] label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--green-deep) !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--green-deep) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: white;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--grey-soft);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    color: var(--text-muted);
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: var(--green-deep) !important;
    color: white !important;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid var(--grey-soft);
    margin: 1.5rem 0;
}

/* Info / alert boxes */
.stAlert {
    border-radius: 10px;
    border-left: 4px solid var(--gold);
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Custom card classes */
.naija-card {
    background: white;
    border: 1px solid var(--grey-soft);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.naija-card-green {
    background: var(--green-deep);
    color: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
}
.naija-card-gold {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
}
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}
.big-number {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    color: var(--green-deep);
}
.hardship-crisis { color: #1C1C1C; background: #1C1C1C22; }

/* Chart container */
.chart-wrap {
    background: white;
    border-radius: 14px;
    padding: 1rem;
    border: 1px solid var(--grey-soft);
}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)

# ─── PLOTLY THEME ────────────────────────────────────────────────────────────

CHART_THEME = {
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "font": {"family": "DM Sans, sans-serif", "color": "#1C1C1C", "size": 12},
    "margin": {"t": 40, "b": 40, "l": 50, "r": 20},
    "colorway": ["#1A6B45", "#D4A843", "#C94B2A", "#2E9E6B", "#0A4A2F"],
    "xaxis": {"gridcolor": "#E8E4DC", "linecolor": "#E8E4DC"},
    "yaxis": {"gridcolor": "#E8E4DC", "linecolor": "#E8E4DC"},
}


def apply_theme(fig):
    fig.update_layout(**CHART_THEME)
    return fig


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem 0;">
        <div style="font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; color: #FAF7F0; line-height: 1.1;">
            🇳🇬 Naija<br>Cost Tracker
        </div>
        <div style="font-size: 0.72rem; color: rgba(240,201,106,0.8); margin-top: 0.4rem; letter-spacing: 0.08em; text-transform: uppercase;">
            Cost of Living Intelligence
        </div>
    </div>
    <hr style="border-color: rgba(212,168,67,0.2); margin: 0 0 1.2rem 0;">
    """, unsafe_allow_html=True)

    page = st.selectbox(
        "NAVIGATE",
        ["🏠 Overview", "📈 Inflation", "🛒 Food Prices", "💵 Exchange Rates", "🔥 Hardship Index"],
    )

    st.markdown("<hr style='border-color: rgba(212,168,67,0.2);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.68rem; color: rgba(250,247,240,0.5); line-height: 1.6;">
        <div style="font-family: 'Syne', sans-serif; color: rgba(240,201,106,0.6); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem;">Data Sources</div>
        National Bureau of Statistics<br>
        Central Bank of Nigeria<br>
        World Bank Open Data<br>
        ExchangeRate-API
    </div>
    <div style="font-size: 0.62rem; color: rgba(250,247,240,0.3); margin-top: 1rem;">
        Updated monthly · 2020–2024
    </div>
    """, unsafe_allow_html=True)


# ─── LOAD DATA ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_all_data():
    inflation = load_inflation()
    food = load_food_prices()
    states = load_state_inflation()
    fx = load_exchange_rates()
    macro = load_macro_indicators()
    live = load_live_rate()
    hardship = compute_hardship_index(inflation, fx)
    return inflation, food, states, fx, macro, live, hardship

inflation, food, states, fx, macro, live, hardship = get_all_data()

latest_inf = inflation.iloc[-1]
latest_fx = fx.iloc[-1]
latest_hardship = hardship.iloc[-1]


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Overview":

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="section-label">Nigerian Cost of Living Intelligence Platform</div>
        <h1 style="font-size: 2.2rem; margin: 0; line-height: 1.1;">What is ₦1,000 worth<br>in Nigeria today?</h1>
        <p style="color: #6B6456; margin-top: 0.6rem; max-width: 600px; font-size: 0.95rem;">
            Real data. Real impact. Tracking how inflation, food prices, and exchange rates
            affect everyday Nigerians — from Lagos to Kano.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Top KPI row ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Headline Inflation",
            f"{latest_inf['headline_inflation_pct']:.1f}%",
            f"{latest_inf['headline_inflation_pct'] - inflation.iloc[-2]['headline_inflation_pct']:+.1f}% MoM",
        )
    with col2:
        st.metric(
            "Food Inflation",
            f"{latest_inf['food_inflation_pct']:.1f}%",
            f"{latest_inf['food_inflation_pct'] - inflation.iloc[-2]['food_inflation_pct']:+.1f}% MoM",
        )
    with col3:
        st.metric(
            "USD/NGN Rate",
            f"₦{latest_fx['cbn_official_rate']:,.0f}",
            f"₦{latest_fx['cbn_official_rate'] - fx.iloc[-2]['cbn_official_rate']:+,.0f} vs last period",
        )
    with col4:
        hi = latest_hardship["hardship_index"]
        st.metric(
            "Hardship Index",
            f"{hi:.0f}/100",
            latest_hardship["hardship_label"],
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── The Purchasing Power Story ──
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("#### Purchasing Power Erosion — ₦10,000 Over Time")

        # What ₦10,000 could buy relative to 2020 baseline
        baseline_inf = inflation[inflation["date"].dt.year == 2020]["headline_inflation_pct"].mean()
        inflation["purchasing_power"] = 10000 / (1 + (inflation["headline_inflation_pct"] - baseline_inf) / 100)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=inflation["date"],
            y=inflation["purchasing_power"],
            mode="lines",
            fill="tozeroy",
            name="Real value of ₦10,000",
            line=dict(color="#1A6B45", width=2.5),
            fillcolor="rgba(26,107,69,0.08)",
        ))
        fig.add_hline(y=10000, line_dash="dot", line_color="#D4A843",
                      annotation_text="₦10,000 baseline (2020)", annotation_position="top left")
        fig.update_layout(
            **CHART_THEME,
            height=280,
            showlegend=False,
            yaxis_title="Real Value (₦)",
            xaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("#### Inflation vs Food Inflation")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=inflation["date"], y=inflation["headline_inflation_pct"],
            name="Headline", line=dict(color="#1A6B45", width=2),
        ))
        fig2.add_trace(go.Scatter(
            x=inflation["date"], y=inflation["food_inflation_pct"],
            name="Food", line=dict(color="#C94B2A", width=2),
        ))
        fig2.update_layout(
            **CHART_THEME,
            height=280,
            yaxis_title="%",
            legend=dict(orientation="h", y=1.1, x=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Salary calculator ──
    st.markdown("#### 💡 Remote Worker / Freelancer Salary Calculator")
    st.markdown("<p style='color: #6B6456; font-size: 0.88rem;'>See what your USD income is really worth in Nigeria over time</p>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        salary_usd = st.number_input("Monthly income (USD)", min_value=100, max_value=50000, value=1000, step=100)

    fx["salary_ngn"] = fx["cbn_official_rate"] * salary_usd
    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=fx["label"], y=fx["salary_ngn"],
            marker_color="#1A6B45",
            text=[f"₦{v:,.0f}" for v in fx["salary_ngn"]],
            textposition="outside",
            textfont=dict(size=9),
        ))
        fig3.update_layout(
            **CHART_THEME,
            height=240,
            showlegend=False,
            yaxis_title="₦ NGN",
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig3, use_container_width=True)

    current_ngn = latest_fx["cbn_official_rate"] * salary_usd
    year_ago_ngn = fx[fx["date"].dt.year == 2022]["cbn_official_rate"].mean() * salary_usd
    st.info(f"💬 Your ${salary_usd:,}/month was worth ₦{year_ago_ngn:,.0f} in 2022. Today it's **₦{current_ngn:,.0f}** — a {'gain' if current_ngn > year_ago_ngn else 'loss'} of ₦{abs(current_ngn - year_ago_ngn):,.0f} in nominal terms, but **real purchasing power has fallen** due to food inflation.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: INFLATION
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📈 Inflation":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="section-label">National Bureau of Statistics · Monthly CPI Data</div>
        <h1 style="font-size: 2rem; margin: 0;">Inflation Tracker</h1>
        <p style="color: #6B6456; margin-top: 0.4rem; font-size: 0.9rem;">
            Headline, food, and core inflation trends for Nigeria (2020–2024)
        </p>
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

    # Multi-line inflation chart
    fig = go.Figure()
    for col, name, color in [
        ("headline_inflation_pct", "Headline", "#1A6B45"),
        ("food_inflation_pct", "Food", "#C94B2A"),
        ("core_inflation_pct", "Core", "#D4A843"),
    ]:
        fig.add_trace(go.Scatter(
            x=inflation["date"], y=inflation[col],
            name=name, mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=4),
        ))

    # Annotate major events
    fig.add_vrect(x0="2023-06-01", x1="2023-08-01",
                  fillcolor="rgba(201,75,42,0.07)", line_width=0,
                  annotation_text="FX Unification", annotation_position="top left",
                  annotation_font_size=10)
    fig.add_vrect(x0="2023-05-01", x1="2023-06-01",
                  fillcolor="rgba(212,168,67,0.1)", line_width=0,
                  annotation_text="Subsidy Removal", annotation_position="top right",
                  annotation_font_size=10)

    fig.update_layout(
        **CHART_THEME,
        height=360,
        title="Nigeria Inflation Rates (%)",
        yaxis_title="Inflation Rate (%)",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # State inflation heatmap
    st.markdown("#### State-Level Inflation (2024)")
    col_a, col_b = st.columns(2)

    with col_a:
        states_sorted = states.sort_values("inflation_2024_pct", ascending=True)
        fig2 = go.Figure(go.Bar(
            x=states_sorted["inflation_2024_pct"],
            y=states_sorted["state"],
            orientation="h",
            marker=dict(
                color=states_sorted["inflation_2024_pct"],
                colorscale=[[0, "#2E9E6B"], [0.5, "#D4A843"], [1, "#C94B2A"]],
                showscale=True,
                colorbar=dict(title="%"),
            ),
        ))
        fig2.update_layout(
            **CHART_THEME, height=440,
            title="2024 Inflation by State (%)",
            xaxis_title="%", yaxis_title="",
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        states["yoy_change"] = states["inflation_2024_pct"] - states["inflation_2023_pct"]
        fig3 = go.Figure(go.Bar(
            x=states.sort_values("yoy_change", ascending=True)["yoy_change"],
            y=states.sort_values("yoy_change", ascending=True)["state"],
            orientation="h",
            marker_color=states.sort_values("yoy_change", ascending=True)["yoy_change"].apply(
                lambda x: "#C94B2A" if x > 0 else "#1A6B45"
            ),
        ))
        fig3.update_layout(
            **CHART_THEME, height=440,
            title="Year-on-Year Change (2023 → 2024)",
            xaxis_title="Percentage points", yaxis_title="",
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Annual Averages")
    annual = inflation.groupby("year")[["headline_inflation_pct", "food_inflation_pct", "core_inflation_pct"]].mean().round(1).reset_index()
    annual.columns = ["Year", "Headline (%)", "Food (%)", "Core (%)"]
    st.dataframe(annual, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FOOD PRICES
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🛒 Food Prices":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="section-label">NBS Selected Food Prices Watch</div>
        <h1 style="font-size: 2rem; margin: 0;">Food Price Tracker</h1>
        <p style="color: #6B6456; margin-top: 0.4rem; font-size: 0.9rem;">
            Track what Nigerians actually pay for staples — garri, rice, tomatoes, and more
        </p>
    </div>
    """, unsafe_allow_html=True)

    food_items = {
        "rice_50kg_ngn": "Rice (50kg bag)",
        "garri_50kg_ngn": "Garri (50kg bag)",
        "tomatoes_1kg_ngn": "Tomatoes (1kg)",
        "cooking_oil_5l_ngn": "Cooking Oil (5L)",
        "eggs_crate_ngn": "Eggs (1 crate)",
        "bread_loaf_ngn": "Bread (1 loaf)",
        "beef_1kg_ngn": "Beef (1kg)",
    }

    # Latest vs 2022 comparison
    first = food.iloc[0]
    latest_food = food.iloc[-1]

    st.markdown("#### Price Changes: 2022 → Latest")
    cols = st.columns(4)
    items_list = list(food_items.items())
    for i, (col_name, label) in enumerate(items_list[:4]):
        pct_change = ((latest_food[col_name] - first[col_name]) / first[col_name]) * 100
        cols[i].metric(label, f"₦{latest_food[col_name]:,.0f}", f"+{pct_change:.0f}% since Jan 2022")

    cols2 = st.columns(3)
    for i, (col_name, label) in enumerate(items_list[4:]):
        pct_change = ((latest_food[col_name] - first[col_name]) / first[col_name]) * 100
        cols2[i].metric(label, f"₦{latest_food[col_name]:,.0f}", f"+{pct_change:.0f}% since Jan 2022")

    st.markdown("<br>", unsafe_allow_html=True)

    # Price trend selector
    selected_items = st.multiselect(
        "Select food items to compare",
        options=list(food_items.keys()),
        default=["rice_50kg_ngn", "garri_50kg_ngn", "tomatoes_1kg_ngn"],
        format_func=lambda x: food_items[x],
    )

    if selected_items:
        colors = ["#1A6B45", "#C94B2A", "#D4A843", "#2E9E6B", "#0A4A2F", "#8B4513", "#6B6456"]
        fig = go.Figure()
        for i, item in enumerate(selected_items):
            fig.add_trace(go.Scatter(
                x=food["date"], y=food[item],
                name=food_items[item],
                mode="lines+markers",
                line=dict(color=colors[i % len(colors)], width=2.5),
                marker=dict(size=6),
            ))
        fig.update_layout(
            **CHART_THEME,
            height=350,
            title="Food Price Trends (₦)",
            yaxis_title="Price (₦)",
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Basket of goods calculator
    st.markdown("#### 🧺 Monthly Food Basket Calculator")
    st.markdown("<p style='color: #6B6456; font-size: 0.88rem;'>Estimate what a typical household spends on food per month</p>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    qty_rice = c1.number_input("Rice bags/month", 0.0, 10.0, 0.5, 0.5)
    qty_garri = c2.number_input("Garri bags/month", 0.0, 10.0, 0.5, 0.5)
    qty_eggs = c3.number_input("Egg crates/month", 0, 20, 4)
    qty_oil = c4.number_input("Oil bottles/month", 0, 10, 1)

    total = (
        qty_rice * latest_food["rice_50kg_ngn"] +
        qty_garri * latest_food["garri_50kg_ngn"] +
        qty_eggs * latest_food["eggs_crate_ngn"] +
        qty_oil * latest_food["cooking_oil_5l_ngn"]
    )
    total_2022 = (
        qty_rice * first["rice_50kg_ngn"] +
        qty_garri * first["garri_50kg_ngn"] +
        qty_eggs * first["eggs_crate_ngn"] +
        qty_oil * first["cooking_oil_5l_ngn"]
    )

    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Basket Cost Today", f"₦{total:,.0f}/month")
    col_res2.metric("Same basket in Jan 2022", f"₦{total_2022:,.0f}/month")
    col_res3.metric("Increase", f"₦{total - total_2022:,.0f}", f"+{((total-total_2022)/total_2022*100):.0f}%")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXCHANGE RATES
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "💵 Exchange Rates":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="section-label">CBN Official · Parallel Market · Fuel Prices</div>
        <h1 style="font-size: 2rem; margin: 0;">Exchange Rate Intelligence</h1>
        <p style="color: #6B6456; margin-top: 0.4rem; font-size: 0.9rem;">
            How the naira has moved — official rate, parallel market, and the gap between them
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CBN Official Rate", f"₦{latest_fx['cbn_official_rate']:,.0f}/$",
                f"₦{latest_fx['cbn_official_rate'] - fx.iloc[-2]['cbn_official_rate']:+,.0f}")
    col2.metric("Parallel Market", f"₦{latest_fx['parallel_market_rate']:,.0f}/$",
                f"₦{latest_fx['parallel_market_rate'] - fx.iloc[-2]['parallel_market_rate']:+,.0f}")
    col3.metric("Market Spread", f"₦{latest_fx['spread']:,.0f}",
                f"{latest_fx['spread_pct']:.1f}% premium")
    col4.metric("Fuel Price", f"₦{latest_fx['fuel_price_per_litre_ngn']:,.0f}/L",
                f"₦{latest_fx['fuel_price_per_litre_ngn'] - fx.iloc[-2]['fuel_price_per_litre_ngn']:+,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Official vs parallel market
    col_l, col_r = st.columns([3, 2])

    with col_l:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fx["date"], y=fx["cbn_official_rate"],
            name="CBN Official", mode="lines",
            line=dict(color="#1A6B45", width=2.5),
            fill="tozeroy", fillcolor="rgba(26,107,69,0.06)",
        ))
        fig.add_trace(go.Scatter(
            x=fx["date"], y=fx["parallel_market_rate"],
            name="Parallel Market", mode="lines",
            line=dict(color="#C94B2A", width=2, dash="dot"),
        ))
        fig.add_vrect(x0="2023-06-15", x1="2023-07-01",
                      fillcolor="rgba(212,168,67,0.15)", line_width=0,
                      annotation_text="FX Unification", annotation_font_size=9)
        fig.update_layout(
            **CHART_THEME, height=320,
            title="USD/NGN Exchange Rates Over Time",
            yaxis_title="₦ per $1",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        fig2 = go.Figure(go.Bar(
            x=fx["label"], y=fx["spread"],
            marker=dict(
                color=fx["spread"],
                colorscale=[[0, "#2E9E6B"], [0.5, "#D4A843"], [1, "#C94B2A"]],
            ),
            text=[f"₦{v:,.0f}" for v in fx["spread"]],
            textposition="outside", textfont=dict(size=8),
        ))
        fig2.update_layout(
            **CHART_THEME, height=320,
            title="Parallel Market Premium (₦ spread)",
            yaxis_title="₦ spread", showlegend=False,
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Fuel vs FX correlation
    st.markdown("#### Fuel Price vs Exchange Rate")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=fx["date"], y=fx["fuel_price_per_litre_ngn"],
        name="Fuel (₦/L)", mode="lines+markers",
        line=dict(color="#D4A843", width=2.5),
        yaxis="y1",
    ))
    fig3.add_trace(go.Scatter(
        x=fx["date"], y=fx["cbn_official_rate"],
        name="USD/NGN", mode="lines+markers",
        line=dict(color="#1A6B45", width=2, dash="dot"),
        yaxis="y2",
    ))
    fig3.update_layout(
        **CHART_THEME,
        height=300,
        title="Fuel Price vs USD/NGN Rate — The Correlation",
        yaxis=dict(title="Fuel ₦/L", gridcolor="#E8E4DC"),
        yaxis2=dict(title="₦ per $1", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HARDSHIP INDEX
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🔥 Hardship Index":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="section-label">Composite Economic Stress Indicator</div>
        <h1 style="font-size: 2rem; margin: 0;">Nigeria Hardship Index</h1>
        <p style="color: #6B6456; margin-top: 0.4rem; font-size: 0.9rem;">
            A single number that captures how hard life is for the average Nigerian —
            combining food inflation (45%), headline inflation (30%), and exchange rate pressure (25%).
        </p>
    </div>
    """, unsafe_allow_html=True)

    latest_hi = hardship.iloc[-1]
    hi_score = latest_hi["hardship_index"]

    # Big score display
    score_color = "#1A6B45" if hi_score <= 50 else "#D4A843" if hi_score <= 70 else "#C94B2A"
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
                border: 1px solid #E8E4DC; display: flex; align-items: center; gap: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
        <div>
            <div class="section-label">Current Hardship Index</div>
            <div style="font-family: 'Syne', sans-serif; font-size: 5rem; font-weight: 800;
                        color: {score_color}; line-height: 1;">{hi_score:.0f}</div>
            <div style="font-family: 'Syne', sans-serif; font-size: 1.1rem; color: {score_color};
                        font-weight: 600;">{latest_hi['hardship_label']}</div>
        </div>
        <div style="flex: 1; padding-left: 2rem; border-left: 1px solid #E8E4DC;">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                <div>
                    <div class="section-label">Food Pressure</div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 700; color: #C94B2A;">{latest_hi['food_score']:.0f}<span style="font-size: 0.9rem">/100</span></div>
                </div>
                <div>
                    <div class="section-label">Inflation Pressure</div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 700; color: #D4A843;">{latest_hi['inf_score']:.0f}<span style="font-size: 0.9rem">/100</span></div>
                </div>
                <div>
                    <div class="section-label">FX Pressure</div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 700; color: #1A6B45;">{latest_hi['fx_score']:.0f}<span style="font-size: 0.9rem">/100</span></div>
                </div>
            </div>
            <div style="margin-top: 1rem; font-size: 0.82rem; color: #6B6456; line-height: 1.6;">
                <b>Scale:</b> 0–30 Stable 🟢 · 31–50 Moderate 🟡 · 51–70 High Pressure 🟠 · 71–85 Severe 🔴 · 86–100 Crisis ⚫
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hardship over time
    fig = go.Figure()
    colors_hi = hardship["hardship_index"].apply(
        lambda x: "#2E9E6B" if x <= 30 else "#D4A843" if x <= 50 else "#E8833A" if x <= 70 else "#C94B2A"
    )
    fig.add_trace(go.Scatter(
        x=hardship["date"], y=hardship["hardship_index"],
        mode="lines",
        line=dict(color="#1A6B45", width=3),
        fill="tozeroy",
        fillcolor="rgba(26,107,69,0.07)",
        name="Hardship Index",
    ))
    # Threshold lines
    for level, label, color in [(30, "Moderate threshold", "#D4A843"),
                                  (70, "Severe threshold", "#C94B2A")]:
        fig.add_hline(y=level, line_dash="dot", line_color=color,
                      annotation_text=label, annotation_font_size=10)

    fig.update_layout(
        **CHART_THEME,
        height=340,
        title="Nigeria Hardship Index Over Time (0–100)",
        yaxis_title="Index Score",
        yaxis_range=[0, 100],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Component breakdown over time
    st.markdown("#### Component Breakdown Over Time")
    fig2 = go.Figure()
    for col, name, color in [
        ("food_score", "Food Pressure (45%)", "#C94B2A"),
        ("inf_score", "Inflation Pressure (30%)", "#D4A843"),
        ("fx_score", "FX Pressure (25%)", "#1A6B45"),
    ]:
        fig2.add_trace(go.Scatter(
            x=hardship["date"], y=hardship[col],
            name=name, mode="lines",
            line=dict(color=color, width=2),
            stackgroup="one",
            groupnorm="",
        ))
    fig2.update_layout(
        **CHART_THEME,
        height=300,
        yaxis_title="Score component",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class="naija-card">
        <div style="font-family: 'Syne', sans-serif; font-size: 0.8rem; text-transform: uppercase;
                    letter-spacing: 0.1em; color: #6B6456; margin-bottom: 0.5rem;">Methodology Note</div>
        <p style="font-size: 0.88rem; color: #1C1C1C; line-height: 1.7; margin: 0;">
            The Hardship Index is a weighted composite of three normalized indicators:
            <b>food inflation</b> (weighted 45% — the single largest household expenditure for most Nigerians),
            <b>headline CPI inflation</b> (30%), and <b>exchange rate pressure</b> (25%, measured as depreciation
            from a ₦360/$1 baseline). Each component is normalized to a 0–100 scale.
            Data sourced from NBS monthly CPI reports and CBN official rate publications.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top: 3rem; padding: 1.5rem 0; border-top: 1px solid #E8E4DC;
            display: flex; justify-content: space-between; align-items: center;">
    <div style="font-size: 0.75rem; color: #6B6456;">
        🇳🇬 <b>Naija Cost Tracker</b> — Built with Streamlit, Python & dbt
    </div>
    <div style="font-size: 0.72rem; color: #6B6456;">
        Data: NBS · CBN · World Bank Open Data · ExchangeRate-API
    </div>
</div>
""", unsafe_allow_html=True)