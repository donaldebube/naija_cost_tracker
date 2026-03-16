"""
Naija Cost Tracker — Real-Time Nigerian Cost of Living Intelligence
"""
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
:root{--bg:#0D1F14;--card:#132A1C;--sidebar:#0A1910;--green:#2ECC7A;--gmid:#1A8A4A;--gold:#F0C040;--brick:#E05A30;--cream:#F5F0E8;--dim:#B8B0A0;--white:#FFFFFF;--b:rgba(46,204,122,0.18);--bg2:rgba(240,192,64,0.25);}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--cream)!important;}
.stApp{background:var(--bg)!important;}
[data-testid="stSidebar"]{background:var(--sidebar)!important;border-right:1px solid var(--bg2)!important;}
[data-testid="stSidebar"] *{color:var(--cream)!important;}
[data-testid="stSidebar"] .stSelectbox label{color:var(--gold)!important;font-family:'Syne',sans-serif!important;font-size:0.68rem!important;text-transform:uppercase;letter-spacing:0.12em;font-weight:700!important;}
[data-testid="stSidebar"] .stSelectbox > div > div{background:rgba(46,204,122,0.08)!important;border:1px solid var(--b)!important;color:var(--cream)!important;border-radius:8px!important;}
[data-testid="stSidebar"] .stSelectbox > div > div > div{color:var(--cream)!important;}
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--b)!important;border-radius:12px!important;padding:1.2rem 1.4rem!important;border-top:3px solid var(--green)!important;}
[data-testid="metric-container"] label{font-family:'Syne',sans-serif!important;font-size:0.68rem!important;text-transform:uppercase!important;letter-spacing:0.12em!important;color:var(--dim)!important;font-weight:600!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;font-size:2rem!important;font-weight:800!important;color:var(--white)!important;}
[data-testid="metric-container"] [data-testid="stMetricDelta"]{font-size:0.78rem!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--white)!important;}
p,li{color:var(--cream)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--card)!important;border-radius:10px!important;padding:4px!important;border:1px solid var(--b)!important;}
.stTabs [data-baseweb="tab"]{font-family:'Syne',sans-serif!important;font-size:0.75rem!important;text-transform:uppercase!important;letter-spacing:0.06em!important;border-radius:7px!important;color:var(--dim)!important;font-weight:600!important;}
.stTabs [aria-selected="true"]{background:var(--gmid)!important;color:var(--white)!important;}
[data-testid="stMultiSelect"] label,[data-testid="stNumberInput"] label{color:var(--cream)!important;font-size:0.82rem!important;}
[data-testid="stMultiSelect"] > div > div,[data-testid="stNumberInput"] input{background:var(--card)!important;border:1px solid var(--b)!important;border-radius:8px!important;color:var(--white)!important;}
.stAlert{background:rgba(240,192,64,0.1)!important;border:1px solid var(--bg2)!important;border-left:4px solid var(--gold)!important;border-radius:10px!important;}
.stAlert p{color:var(--cream)!important;}
[data-testid="stDataFrame"]{border:1px solid var(--b)!important;border-radius:10px!important;}
hr{border:none!important;border-top:1px solid var(--b)!important;margin:1.5rem 0!important;}
#MainMenu,footer,header{visibility:hidden;}
.eyebrow{font-family:'Syne',sans-serif;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--green);font-weight:700;margin-bottom:0.5rem;}
.page-title{font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;color:var(--white);line-height:1.1;margin:0 0 0.6rem 0;}
.page-sub{font-size:0.92rem;color:var(--dim);line-height:1.6;max-width:600px;}
.lbl{font-family:'Syne',sans-serif;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.14em;color:var(--dim);font-weight:700;margin-bottom:0.5rem;}
</style>
""", unsafe_allow_html=True)

# Chart theme helper — fixes the legend duplicate keyword bug
_BASE_CHART = dict(
    paper_bgcolor="#132A1C", plot_bgcolor="#132A1C",
    font=dict(family="Inter, sans-serif", color="#F5F0E8", size=12),
    margin=dict(t=50, b=40, l=55, r=20),
    colorway=["#2ECC7A","#F0C040","#E05A30","#1A8A4A","#C49A28"],
    xaxis=dict(gridcolor="rgba(46,204,122,0.1)", linecolor="rgba(46,204,122,0.2)", tickfont=dict(color="#B8B0A0")),
    yaxis=dict(gridcolor="rgba(46,204,122,0.1)", linecolor="rgba(46,204,122,0.2)", tickfont=dict(color="#B8B0A0")),
    title_font=dict(family="Syne, sans-serif", color="#FFFFFF", size=14),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F5F0E8")),
)

def C(**overrides):
    t = dict(_BASE_CHART)
    if "legend" in overrides:
        t["legend"] = {**_BASE_CHART["legend"], **overrides.pop("legend")}
    if "xaxis" in overrides:
        t["xaxis"] = {**_BASE_CHART["xaxis"], **overrides.pop("xaxis")}
    if "yaxis" in overrides:
        t["yaxis"] = {**_BASE_CHART["yaxis"], **overrides.pop("yaxis")}
    t.update(overrides)
    return t

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1.4rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.18em;color:#2ECC7A;font-weight:700;margin-bottom:0.5rem;">🇳🇬 Nigeria</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;color:#FFFFFF;line-height:1.1;">Naija Cost<br>Tracker</div>
        <div style="font-size:0.73rem;color:#B8B0A0;margin-top:0.4rem;line-height:1.5;">Real-time cost of living<br>intelligence for Nigeria</div>
    </div>
    <hr style="border-color:rgba(46,204,122,0.18);margin:0 0 1rem 0;">
    """, unsafe_allow_html=True)

    page = st.selectbox("NAVIGATE", ["🏠 Overview","📈 Inflation","🛒 Food Prices","💵 Exchange Rates","🔥 Hardship Index","📖 Methodology"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Live Rate", use_container_width=True):
        st.cache_data.clear()

    st.markdown("<hr style='border-color:rgba(46,204,122,0.18);margin:1rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem;color:#B8B0A0;line-height:1.8;">
        <div style="font-family:'Syne',sans-serif;color:#F0C040;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;font-weight:700;">Data Sources</div>
        NBS CPI Reports (2024=100 base)<br>CBN NFEM Official Rates<br>Open Exchange Rates API<br>NNPC Fuel Price Data
    </div>
    <div style="font-size:0.62rem;color:rgba(184,176,160,0.4);margin-top:1rem;">Inflation: Jan 2020–Jan 2026<br>FX: Jan 2020–live</div>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
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

inflation, food, states, fx, macro, live, hardship = get_all_data()
li = inflation.iloc[-1]; lf = fx.iloc[-1]; lh = hardship.iloc[-1]
live_rate = float(live.get("rate", lf["cbn_official_rate"]))
is_live   = live.get("is_live", False)
live_src  = str(live.get("source","cached"))
live_date = str(live.get("date","N/A"))


# ═══════════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════════
if page == "🏠 Overview":
    badge = '<span style="background:rgba(46,204,122,0.15);color:#2ECC7A;border:1px solid rgba(46,204,122,0.35);border-radius:20px;padding:2px 10px;font-size:0.68rem;font-family:Syne,sans-serif;font-weight:700;">● LIVE</span>' if is_live else '<span style="background:rgba(240,192,64,0.15);color:#F0C040;border:1px solid rgba(240,192,64,0.35);border-radius:20px;padding:2px 10px;font-size:0.68rem;font-family:Syne,sans-serif;font-weight:700;">● CACHED</span>'
    st.markdown(f"""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Nigerian Cost of Living Intelligence Platform</div>
        <div class="page-title">What is ₦1,000 worth<br>in Nigeria today?</div>
        <div class="page-sub">Real data. Real impact. Tracking how inflation, food prices, and exchange rates affect everyday Nigerians.</div>
        <div style="margin-top:0.8rem;font-size:0.75rem;color:#B8B0A0;">FX Rate: {badge} &nbsp;·&nbsp; {live_src} &nbsp;·&nbsp; {live_date}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Headline Inflation",f"{li['headline_inflation_pct']:.2f}%",f"{li['headline_inflation_pct']-inflation.iloc[-2]['headline_inflation_pct']:+.2f}pp MoM")
    c2.metric("Food Inflation",f"{li['food_inflation_pct']:.2f}%",f"{li['food_inflation_pct']-inflation.iloc[-2]['food_inflation_pct']:+.2f}pp MoM")
    c3.metric("Live USD/NGN",f"₦{live_rate:,.0f}",f"₦{live_rate-fx.iloc[-2]['cbn_official_rate']:+,.0f} vs prev")
    c4.metric("Hardship Index",f"{lh['hardship_index']:.0f}/100",lh["hardship_label"])

    st.markdown("<br>", unsafe_allow_html=True)
    c5,c6,c7,c8 = st.columns(4)
    yoy = li['headline_inflation_pct']-inflation.iloc[-13]['headline_inflation_pct']
    c5.metric("Inflation YoY",f"{yoy:+.1f}pp","Improving 📉" if yoy<0 else "Worsening 📈")
    c6.metric("Parallel Mkt Premium",f"₦{lf['spread']:,.0f}",f"{lf['spread_pct']:.1f}% above CBN")
    c7.metric("Petrol Pump Price",f"₦{lf['fuel_price_per_litre_ngn']:,.0f}/L",f"₦{lf['fuel_price_per_litre_ngn']-fx.iloc[-2]['fuel_price_per_litre_ngn']:+,.0f}")
    c8.metric("Core Inflation",f"{li['core_inflation_pct']:.2f}%",f"{li['core_inflation_pct']-inflation.iloc[-2]['core_inflation_pct']:+.2f}pp MoM")

    st.markdown("<br>", unsafe_allow_html=True)
    cl,cr = st.columns([3,2])
    with cl:
        st.markdown('<div class="lbl">Purchasing Power — ₦10,000 (2020 Baseline)</div>', unsafe_allow_html=True)
        base = inflation[inflation["date"].dt.year==2020]["headline_inflation_pct"].mean()
        inflation["pp"] = 10000/(1+(inflation["headline_inflation_pct"]-base)/100)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=inflation["date"],y=inflation["pp"],mode="lines",fill="tozeroy",line=dict(color="#2ECC7A",width=2.5),fillcolor="rgba(46,204,122,0.08)"))
        fig.add_hline(y=10000,line_dash="dot",line_color="#F0C040",annotation_text="₦10,000 baseline (2020)",annotation_font_color="#F0C040",annotation_font_size=11)
        fig.update_layout(**C(height=290,showlegend=False,yaxis_title="Real Value (₦)"))
        st.plotly_chart(fig,use_container_width=True)
    with cr:
        st.markdown('<div class="lbl">Headline vs Food Inflation</div>', unsafe_allow_html=True)
        fig2=go.Figure()
        fig2.add_trace(go.Scatter(x=inflation["date"],y=inflation["headline_inflation_pct"],name="Headline",line=dict(color="#2ECC7A",width=2.5)))
        fig2.add_trace(go.Scatter(x=inflation["date"],y=inflation["food_inflation_pct"],name="Food",line=dict(color="#E05A30",width=2.5)))
        fig2.update_layout(**C(height=290,yaxis_title="%",legend=dict(orientation="h",y=1.1,x=0)))
        st.plotly_chart(fig2,use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin-bottom:0.4rem;">💡 Freelancer / Remote Worker Salary Calculator</div><div style="font-size:0.84rem;color:#B8B0A0;margin-bottom:1rem;">See what your USD income is worth in naira — then vs now</div>', unsafe_allow_html=True)
    ca,cb=st.columns([1,3])
    with ca:
        salary=st.number_input("Monthly income (USD)",100,50000,1000,100)
    fx["sal"]=fx["cbn_official_rate"]*salary
    with cb:
        fig3=go.Figure()
        fig3.add_trace(go.Bar(x=fx["label"],y=fx["sal"],marker_color="#1A8A4A",marker_line_color="#2ECC7A",marker_line_width=0.5,text=[f"₦{v/1000:.0f}k" for v in fx["sal"]],textposition="outside",textfont=dict(size=9,color="#F5F0E8")))
        fig3.update_layout(**C(height=240,showlegend=False,yaxis_title="₦ NGN",xaxis=dict(tickangle=-30,gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0"))))
        st.plotly_chart(fig3,use_container_width=True)
    ngn_now=live_rate*salary; ngn_2022=fx[fx["date"].dt.year==2022]["cbn_official_rate"].mean()*salary; diff=ngn_now-ngn_2022
    st.info(f"💬  In 2022 your ${salary:,}/month was worth ₦{ngn_2022:,.0f}. At today's live rate of ₦{live_rate:,.0f}/$, that's now **₦{ngn_now:,.0f}** — ₦{abs(diff):,.0f} {'more' if diff>0 else 'less'} in naira. But real purchasing power has fallen significantly due to cumulative inflation.")

# ═══════════════════════════════════════════════
# INFLATION
# ═══════════════════════════════════════════════
elif page == "📈 Inflation":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">NBS CPI Reports · Base Year 2024=100</div>
        <div class="page-title">Inflation Tracker</div>
        <div class="page-sub">Nigeria's inflation peaked at ~34% in 2024, falling to 15.10% in January 2026 — a 5-year low. Note: NBS rebased CPI methodology in late 2024.</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Headline (Jan 2026)",f"{li['headline_inflation_pct']:.2f}%",f"{li['headline_inflation_pct']-inflation.iloc[-13]['headline_inflation_pct']:+.1f}pp YoY")
    c2.metric("Food (Jan 2026)",f"{li['food_inflation_pct']:.2f}%",f"{li['food_inflation_pct']-inflation.iloc[-13]['food_inflation_pct']:+.1f}pp YoY")
    c3.metric("Core (Jan 2026)",f"{li['core_inflation_pct']:.2f}%",f"{li['core_inflation_pct']-inflation.iloc[-13]['core_inflation_pct']:+.1f}pp YoY")
    c4.metric("Peak (2024)",f"{inflation['headline_inflation_pct'].max():.1f}%","Jun 2024 all-time high")

    st.markdown("<br>", unsafe_allow_html=True)
    fig=go.Figure()
    for cn,lb,co in [("headline_inflation_pct","Headline","#2ECC7A"),("food_inflation_pct","Food","#E05A30"),("core_inflation_pct","Core","#F0C040")]:
        fig.add_trace(go.Scatter(x=inflation["date"],y=inflation[cn],name=lb,mode="lines+markers",line=dict(color=co,width=2.5),marker=dict(size=4,color=co)))
    for x0,x1,txt in [("2023-05-01","2023-06-01","Subsidy Removal"),("2023-06-15","2023-07-15","FX Unification"),("2024-12-01","2025-01-15","CPI Rebase")]:
        fig.add_vrect(x0=x0,x1=x1,fillcolor="rgba(240,192,64,0.07)",line_width=0,annotation_text=txt,annotation_font_size=9,annotation_font_color="#B8B0A0")
    fig.update_layout(**C(height=400,title="Nigeria Inflation Rates — Jan 2020 to Jan 2026 (%)",yaxis_title="Rate (%)",legend=dict(orientation="h",y=1.08)))
    st.plotly_chart(fig,use_container_width=True)
    st.info("⚠️  **NBS Rebase Note:** In late 2024 NBS changed the CPI base year from 2009 to 2024=100. The drop from ~34% to ~15% reflects BOTH genuine disinflation AND this methodological change. 2020–2024 data uses the old methodology; 2025–2026 uses the new.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin-bottom:0.8rem;">State-Level Inflation (2025)</div>', unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        s=states.sort_values("inflation_2025_pct",ascending=True)
        fig2=go.Figure(go.Bar(x=s["inflation_2025_pct"],y=s["state"],orientation="h",marker=dict(color=s["inflation_2025_pct"],colorscale=[[0,"#1A8A4A"],[0.5,"#F0C040"],[1,"#E05A30"]],showscale=True,colorbar=dict(title="%",tickfont=dict(color="#F5F0E8"),titlefont=dict(color="#F5F0E8")))))
        fig2.update_layout(**C(height=440,title="2025 Inflation by State (%)",xaxis=dict(title="%",gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0")),yaxis=dict(title="",gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0"))))
        st.plotly_chart(fig2,use_container_width=True)
    with cb:
        states["ch"]=states["inflation_2025_pct"]-states["inflation_2024_pct"]
        s2=states.sort_values("ch",ascending=True)
        fig3=go.Figure(go.Bar(x=s2["ch"],y=s2["state"],orientation="h",marker_color=["#2ECC7A" if v<0 else "#E05A30" for v in s2["ch"]]))
        fig3.update_layout(**C(height=440,title="YoY Change 2024→2025 (pp)",xaxis=dict(title="pp",gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0")),yaxis=dict(title="",gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0"))))
        st.plotly_chart(fig3,use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin-bottom:0.8rem;">Annual Summary</div>', unsafe_allow_html=True)
    ann=inflation.groupby("year")[["headline_inflation_pct","food_inflation_pct","core_inflation_pct"]].mean().round(2).reset_index()
    ann.columns=["Year","Headline (%)","Food (%)","Core (%)"]
    st.dataframe(ann,use_container_width=True,hide_index=True)

# ═══════════════════════════════════════════════
# FOOD PRICES
# ═══════════════════════════════════════════════
elif page == "🛒 Food Prices":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">NBS Selected Food Prices Watch</div>
        <div class="page-title">Food Price Tracker</div>
        <div class="page-sub">Food prices peaked in mid-2024 and have moderated since — but remain far above 2022 levels.</div>
    </div>""", unsafe_allow_html=True)

    ITEMS={"rice_50kg_ngn":"Rice (50kg)","garri_50kg_ngn":"Garri (50kg)","tomatoes_1kg_ngn":"Tomatoes (1kg)","cooking_oil_5l_ngn":"Cooking Oil (5L)","eggs_crate_ngn":"Eggs (crate)","bread_loaf_ngn":"Bread (loaf)","beef_1kg_ngn":"Beef (1kg)"}
    f0=food.iloc[0]; fl=food.iloc[-1]
    st.markdown('<div class="lbl" style="margin-bottom:0.8rem;">Current Prices vs Jan 2022</div>', unsafe_allow_html=True)
    items=list(ITEMS.items())
    cols=st.columns(4)
    for i,(k,v) in enumerate(items[:4]):
        pct=(fl[k]-f0[k])/f0[k]*100; cols[i].metric(v,f"₦{fl[k]:,.0f}",f"+{pct:.0f}% since Jan 2022")
    cols2=st.columns(3)
    for i,(k,v) in enumerate(items[4:]):
        pct=(fl[k]-f0[k])/f0[k]*100; cols2[i].metric(v,f"₦{fl[k]:,.0f}",f"+{pct:.0f}% since Jan 2022")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin-bottom:0.8rem;">Peak Price vs Current Price</div>', unsafe_allow_html=True)
    pd_list=[{"item":v,"peak":food[k].max(),"current":fl[k]} for k,v in ITEMS.items()]
    pdf=pd.DataFrame(pd_list)
    figp=go.Figure()
    figp.add_trace(go.Bar(name="Peak",x=pdf["item"],y=pdf["peak"],marker_color="#E05A30",opacity=0.8))
    figp.add_trace(go.Bar(name="Current",x=pdf["item"],y=pdf["current"],marker_color="#2ECC7A"))
    figp.update_layout(**C(height=320,title="Peak vs Current Food Prices (₦)",yaxis_title="Price (₦)",barmode="group",legend=dict(orientation="h",y=1.08)))
    st.plotly_chart(figp,use_container_width=True)

    sel=st.multiselect("Select items for trend",options=list(ITEMS.keys()),default=["rice_50kg_ngn","garri_50kg_ngn","beef_1kg_ngn"],format_func=lambda x:ITEMS[x])
    if sel:
        COLS=["#2ECC7A","#E05A30","#F0C040","#1A8A4A","#C49A28","#80C0A0","#B8B0A0"]
        fig4=go.Figure()
        for i,k in enumerate(sel):
            fig4.add_trace(go.Scatter(x=food["date"],y=food[k],name=ITEMS[k],mode="lines+markers",line=dict(color=COLS[i%len(COLS)],width=2.5),marker=dict(size=6)))
        fig4.update_layout(**C(height=320,title="Food Price Trends (₦)",yaxis_title="Price (₦)",legend=dict(orientation="h",y=1.1)))
        st.plotly_chart(fig4,use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin-bottom:0.4rem;">🧺 Monthly Food Basket Calculator</div><div style="font-size:0.84rem;color:#B8B0A0;margin-bottom:1rem;">Estimate a household monthly food spend</div>', unsafe_allow_html=True)
    b1,b2,b3,b4=st.columns(4)
    qr=b1.number_input("Rice bags/month",0.0,10.0,0.5,0.5)
    qg=b2.number_input("Garri bags/month",0.0,10.0,0.5,0.5)
    qe=b3.number_input("Egg crates/month",0,20,4)
    qo=b4.number_input("Oil bottles/month",0,10,1)
    tot=qr*fl["rice_50kg_ngn"]+qg*fl["garri_50kg_ngn"]+qe*fl["eggs_crate_ngn"]+qo*fl["cooking_oil_5l_ngn"]
    t22=qr*f0["rice_50kg_ngn"]+qg*f0["garri_50kg_ngn"]+qe*f0["eggs_crate_ngn"]+qo*f0["cooking_oil_5l_ngn"]
    r1,r2,r3=st.columns(3)
    r1.metric("Basket Today",f"₦{tot:,.0f}/month"); r2.metric("Same basket Jan 2022",f"₦{t22:,.0f}/month")
    if t22>0: r3.metric("Total Increase",f"₦{tot-t22:,.0f}",f"+{(tot-t22)/t22*100:.0f}%")


# ═══════════════════════════════════════════════
# EXCHANGE RATES
# ═══════════════════════════════════════════════
elif page == "💵 Exchange Rates":
    st.markdown(f"""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">CBN NFEM Official · Parallel Market · Live Feed</div>
        <div class="page-title">Exchange Rate Intelligence</div>
        <div class="page-sub">The naira hit ₦1,620/$ in late 2024, recovering to ~₦1,400/$ by March 2026 driven by stronger oil revenues and CBN market reforms.</div>
        <div style="margin-top:0.8rem;font-size:0.75rem;color:#B8B0A0;">Live source: {live_src} · Updated: {live_date}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Live CBN Rate",f"₦{live_rate:,.0f}/$",f"Source: {live_src[:18]}")
    c2.metric("Parallel Market",f"₦{lf['parallel_market_rate']:,.0f}/$",f"₦{lf['parallel_market_rate']-fx.iloc[-2]['parallel_market_rate']:+,.0f}")
    c3.metric("Market Spread",f"₦{lf['spread']:,.0f}",f"{lf['spread_pct']:.1f}% above CBN")
    c4.metric("Fuel Pump Price",f"₦{lf['fuel_price_per_litre_ngn']:,.0f}/L",f"₦{lf['fuel_price_per_litre_ngn']-fx.iloc[-2]['fuel_price_per_litre_ngn']:+,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    c5,c6,c7,c8=st.columns(4)
    deval=(lf["cbn_official_rate"]-360)/360*100
    c5.metric("Devaluation vs 2020",f"{deval:.0f}%","From ₦360/$ baseline")
    c6.metric("$500 in Naira Today",f"₦{live_rate*500:,.0f}","Was ₦180,000 in 2020")
    peak_r=fx["cbn_official_rate"].max()
    c7.metric("Peak Rate (2024)",f"₦{peak_r:,.0f}/$","All-time high")
    rec=(peak_r-live_rate)/peak_r*100
    c8.metric("Recovery from Peak",f"{rec:.1f}%",f"₦{peak_r-live_rate:,.0f} stronger")

    st.markdown("<br>", unsafe_allow_html=True)
    cl,cr=st.columns([3,2])
    with cl:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=fx["date"],y=fx["cbn_official_rate"],name="CBN Official",mode="lines",line=dict(color="#2ECC7A",width=2.5),fill="tozeroy",fillcolor="rgba(46,204,122,0.06)"))
        fig.add_trace(go.Scatter(x=fx["date"],y=fx["parallel_market_rate"],name="Parallel Market",mode="lines",line=dict(color="#E05A30",width=2,dash="dot")))
        fig.add_hline(y=live_rate,line_dash="dash",line_color="#F0C040",annotation_text=f"Live: ₦{live_rate:,.0f}",annotation_font_color="#F0C040")
        fig.add_vrect(x0="2023-06-15",x1="2023-07-01",fillcolor="rgba(240,192,64,0.1)",line_width=0,annotation_text="FX Unification",annotation_font_color="#F0C040",annotation_font_size=9)
        fig.update_layout(**C(height=340,title="USD/NGN Exchange Rates 2020–2026",yaxis_title="₦ per $1",legend=dict(orientation="h",y=1.1)))
        st.plotly_chart(fig,use_container_width=True)
    with cr:
        fig2=go.Figure(go.Bar(x=fx["label"],y=fx["spread"],marker=dict(color=fx["spread"],colorscale=[[0,"#1A8A4A"],[0.5,"#F0C040"],[1,"#E05A30"]]),text=[f"₦{v:,.0f}" for v in fx["spread"]],textposition="outside",textfont=dict(size=8,color="#F5F0E8")))
        fig2.update_layout(**C(height=340,title="Parallel Market Premium (₦)",yaxis_title="₦ spread",showlegend=False,xaxis=dict(tickangle=-45,gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0"))))
        st.plotly_chart(fig2,use_container_width=True)

    fig3=go.Figure()
    fig3.add_trace(go.Scatter(x=fx["date"],y=fx["fuel_price_per_litre_ngn"],name="Fuel (₦/L)",mode="lines+markers",line=dict(color="#F0C040",width=2.5),yaxis="y1"))
    fig3.add_trace(go.Scatter(x=fx["date"],y=fx["cbn_official_rate"],name="USD/NGN",mode="lines+markers",line=dict(color="#2ECC7A",width=2,dash="dot"),yaxis="y2"))
    fig3.update_layout(**C(height=300,title="Fuel Price vs USD/NGN — The Correlation",yaxis=dict(title="Fuel ₦/L",gridcolor="rgba(46,204,122,0.1)",tickfont=dict(color="#B8B0A0")),yaxis2=dict(title="₦ per $1",overlaying="y",side="right",tickfont=dict(color="#B8B0A0")),legend=dict(orientation="h",y=1.1)))
    st.plotly_chart(fig3,use_container_width=True)

# ═══════════════════════════════════════════════
# HARDSHIP INDEX
# ═══════════════════════════════════════════════
elif page == "🔥 Hardship Index":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Composite Economic Stress Indicator</div>
        <div class="page-title">Nigeria Hardship Index</div>
        <div class="page-sub">A proprietary composite score (0–100) measuring economic stress from food inflation (45%), headline inflation (30%), and FX pressure (25%).</div>
    </div>""", unsafe_allow_html=True)

    hi=lh["hardship_index"]; sc="#2ECC7A" if hi<=50 else "#F0C040" if hi<=70 else "#E05A30"
    st.markdown(f"""
    <div style="background:#132A1C;border:1px solid rgba(46,204,122,0.2);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;border-top:3px solid {sc};">
        <div style="display:flex;gap:3rem;align-items:center;flex-wrap:wrap;">
            <div>
                <div class="lbl">Current Hardship Index</div>
                <div style="font-family:'Syne',sans-serif;font-size:5.5rem;font-weight:800;color:{sc};line-height:1;margin:0.2rem 0;">{hi:.0f}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;color:{sc};font-weight:700;">{lh['hardship_label']}</div>
            </div>
            <div style="flex:1;min-width:280px;">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem;margin-bottom:1rem;">
                    <div><div class="lbl">Food Pressure</div><div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#E05A30;">{lh['food_score']:.0f}<span style="font-size:0.9rem;color:#B8B0A0;">/100</span></div></div>
                    <div><div class="lbl">Inflation Pressure</div><div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#F0C040;">{lh['inf_score']:.0f}<span style="font-size:0.9rem;color:#B8B0A0;">/100</span></div></div>
                    <div><div class="lbl">FX Pressure</div><div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#2ECC7A;">{lh['fx_score']:.0f}<span style="font-size:0.9rem;color:#B8B0A0;">/100</span></div></div>
                </div>
                <div style="font-size:0.75rem;color:#B8B0A0;border-top:1px solid rgba(46,204,122,0.15);padding-top:0.8rem;">
                    <span style="color:#2ECC7A;font-weight:600;">0–30 Stable</span> · <span style="color:#F0C040;font-weight:600;">31–50 Moderate</span> · <span style="color:#F0C040;font-weight:600;">51–70 High</span> · <span style="color:#E05A30;font-weight:600;">71–85 Severe</span> · <span style="color:#E05A30;font-weight:600;">86–100 Crisis</span>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hardship["date"],y=hardship["hardship_index"],mode="lines",line=dict(color="#2ECC7A",width=3),fill="tozeroy",fillcolor="rgba(46,204,122,0.07)"))
    for lv,lb,co in [(30,"Moderate","#F0C040"),(70,"Severe","#E05A30")]:
        fig.add_hline(y=lv,line_dash="dot",line_color=co,annotation_text=lb,annotation_font_color=co,annotation_font_size=10)
    fig.update_layout(**C(height=340,showlegend=False,title="Nigeria Hardship Index — Jan 2020 to Jan 2026",yaxis_title="Index Score",yaxis=dict(range=[0,100],gridcolor="rgba(46,204,122,0.1)",linecolor="rgba(46,204,122,0.2)",tickfont=dict(color="#B8B0A0"))))
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="lbl" style="margin:1rem 0 0.8rem 0;">Component Breakdown Over Time</div>', unsafe_allow_html=True)
    fig2=go.Figure()
    for cn,lb,co in [("food_score","Food (45%)","#E05A30"),("inf_score","Inflation (30%)","#F0C040"),("fx_score","FX (25%)","#2ECC7A")]:
        fig2.add_trace(go.Scatter(x=hardship["date"],y=hardship[cn],name=lb,mode="lines",line=dict(color=co,width=2),stackgroup="one"))
    fig2.update_layout(**C(height=280,yaxis_title="Score",legend=dict(orientation="h",y=1.1)))
    st.plotly_chart(fig2,use_container_width=True)

# ═══════════════════════════════════════════════
# METHODOLOGY
# ═══════════════════════════════════════════════
elif page == "📖 Methodology":
    st.markdown("""
    <div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid rgba(46,204,122,0.18);">
        <div class="eyebrow">Transparency · Sources · Design Decisions</div>
        <div class="page-title">Methodology</div>
        <div class="page-sub">Everything about how this platform was built — data sources, processing, indicator definitions, and design philosophy.</div>
    </div>""", unsafe_allow_html=True)

    def mcard(border_color, title_color, title, content):
        st.markdown(f"""<div style="background:#132A1C;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:1.6rem 2rem;margin-bottom:1.2rem;border-left:4px solid {border_color};">
        <div style="font-family:'Syne',sans-serif;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.14em;color:{title_color};font-weight:700;margin-bottom:0.8rem;">{title}</div>
        {content}</div>""", unsafe_allow_html=True)

    mcard("#2ECC7A","#2ECC7A","About This Project","""<p style="font-size:0.88rem;color:#F5F0E8;line-height:1.8;margin:0;">
    The <strong style="color:#2ECC7A;">Naija Cost Tracker</strong> is a real-time Nigerian cost of living intelligence platform built to make economic data accessible to everyday Nigerians, policymakers, researchers, and businesses. It was built using Python, Streamlit, and dbt — a modern open-source data stack — and draws exclusively on official Nigerian government and international data sources. The project's primary goal is public interest: to tell the honest story of how inflation, food prices, and currency depreciation have affected Nigerian households since 2020.</p>""")

    mcard("#F0C040","#F0C040","Data Sources","""
    <div style="margin-bottom:1rem;"><div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">1. National Bureau of Statistics (NBS) — nigerianstat.gov.ng</div>
    <p style="font-size:0.84rem;color:#B8B0A0;line-height:1.8;margin:0;">Monthly CPI reports covering headline, food, and core inflation. <strong style="color:#F5F0E8;">Critical note:</strong> NBS rebased the CPI in late 2024 (base year 2009 → 2024=100, COICOP 2018 framework, 934 product varieties). All figures from Dec 2024 onward use the new methodology and are NOT directly comparable to earlier data. Latest confirmed release: January 2026 — Headline 15.10%, Food 8.89%, Core 17.72%.</p></div>
    <div style="margin-bottom:1rem;"><div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">2. Central Bank of Nigeria (CBN) — cbn.gov.ng</div>
    <p style="font-size:0.84rem;color:#B8B0A0;line-height:1.8;margin:0;">NFEM (Nigerian Foreign Exchange Market) rate — a daily volume-weighted average of willing-buyer-willing-seller FX transactions. This is the official exchange rate. Confirmed March 2026 rate: ₦1,398–1,406/$.</p></div>
    <div style="margin-bottom:1rem;"><div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">3. Open Exchange Rates API — open.er-api.com</div>
    <p style="font-size:0.84rem;color:#B8B0A0;line-height:1.8;margin:0;">Free public API providing live USD/NGN rates, fetched on every app load and cached for 5 minutes. Falls back to latest confirmed CBN rate if unavailable.</p></div>
    <div><div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;color:#FFFFFF;margin-bottom:0.3rem;">4. NNPC / Market Reports — Fuel Pump Prices</div>
    <p style="font-size:0.84rem;color:#B8B0A0;line-height:1.8;margin:0;">Fuel subsidy removal in May 2023 caused pump price to jump from ₦165/L to ₦617/L overnight — one of the largest cost-of-living shocks in the dataset.</p></div>""")

    mcard("#2ECC7A","#2ECC7A","Data Processing Pipeline","""
    <p style="font-size:0.84rem;color:#B8B0A0;line-height:1.8;margin:0 0 1rem 0;">Three-stage pipeline: Python ingest → dbt transform → Streamlit present.</p>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
        <div style="background:#0D1F14;border:1px solid rgba(46,204,122,0.15);border-radius:8px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;color:#2ECC7A;margin-bottom:0.4rem;">STAGE 1 — INGEST</div>
            <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Python scraper scripts fetch NBS, CBN, and live FX data. Saved as CSV files. Exchange rate updates live every 5 minutes. Inflation data updated monthly when NBS releases figures.</p>
        </div>
        <div style="background:#0D1F14;border:1px solid rgba(240,192,64,0.15);border-radius:8px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;color:#F0C040;margin-bottom:0.4rem;">STAGE 2 — TRANSFORM (dbt)</div>
            <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">dbt models clean raw data into staging and mart layers. Staging handles typing and renaming. Mart models (mart_hardship_index, mart_inflation_trends) apply all business logic and derived metrics.</p>
        </div>
        <div style="background:#0D1F14;border:1px solid rgba(224,90,48,0.15);border-radius:8px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;color:#E05A30;margin-bottom:0.4rem;">STAGE 3 — PRESENT</div>
            <p style="font-size:0.79rem;color:#B8B0A0;line-height:1.6;margin:0;">Streamlit reads processed data and renders the dashboard. Plotly for all charts. 5-minute cache balances freshness with performance. Deployable to Streamlit Cloud as a free public URL.</p>
        </div>
    </div>""")

    mcard("#E05A30","#E05A30","Nigeria Hardship Index — How It's Calculated",f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;margin-bottom:1rem;">
        <div><div style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;color:#FFFFFF;margin-bottom:0.5rem;">Component Weights</div>
        <div style="font-size:0.82rem;color:#B8B0A0;line-height:2.2;"><span style="color:#E05A30;font-weight:600;">Food Inflation → 45%</span><br><span style="color:#F0C040;font-weight:600;">Headline Inflation → 30%</span><br><span style="color:#2ECC7A;font-weight:600;">FX Depreciation → 25%</span></div></div>
        <div><div style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;color:#FFFFFF;margin-bottom:0.5rem;">Normalization Ceilings</div>
        <div style="font-size:0.82rem;color:#B8B0A0;line-height:2.2;">Food: 0%=0, 45%=100<br>Headline: 0%=0, 40%=100<br>FX: ₦360=0, ₦2,000=100</div></div>
    </div>
    <div style="font-size:0.82rem;color:#B8B0A0;border-top:1px solid rgba(224,90,48,0.15);padding-top:0.8rem;line-height:1.7;">
    <strong style="color:#FFFFFF;">Score bands:</strong> 0–30 Stable 🟢 · 31–50 Moderate 🟡 · 51–70 High Pressure 🟠 · 71–85 Severe 🔴 · 86–100 Crisis ⚫<br>
    <strong style="color:#FFFFFF;">Current score: {lh['hardship_index']:.0f}/100 — {lh['hardship_label']}</strong> (driven primarily by FX pressure normalizing as naira strengthens)
    </div>""")

    mcard("#2ECC7A","#2ECC7A","Dashboard Design Philosophy","""<p style="font-size:0.85rem;color:#B8B0A0;line-height:1.8;margin:0;">
    The app uses a dark forest green theme (<span style="color:#2ECC7A;">#0D1F14</span>) inspired by the Nigerian flag and the earthy palette of Lagos markets. Gold accents reference Ankara fabric patterns; brick red signals inflation and economic stress. Typography pairs <strong style="color:#F5F0E8;">Syne</strong> (geometric bold — headings and numbers) with <strong style="color:#F5F0E8;">Inter</strong> (clean — body text). The colour system creates instant visual intuition: green = improving/low risk, gold = caution/moderate, red = pressure/high risk. Every design decision prioritises readability and analytical clarity over decoration.</p>""")

    mcard("#F0C040","#F0C040","Known Limitations & Caveats","""<ul style="font-size:0.84rem;color:#B8B0A0;line-height:2;margin:0;padding-left:1.2rem;">
    <li>Inflation data for 2020–2024 uses the old NBS methodology (base 2009). From 2025 onward, data uses the rebased CPI (2024=100). These series are not directly comparable across the break.</li>
    <li>Food prices are quarterly estimates from NBS Food Prices Watch and market reports — not real-time per-unit retail scanner data.</li>
    <li>Parallel market exchange rate is approximated from publicly reported sources and may differ from any specific location or transaction.</li>
    <li>The Hardship Index is a proprietary composite — not an official government statistic.</li>
    <li>State-level inflation figures are approximations and may differ from NBS official state indices.</li>
    </ul>""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:3rem;padding:1.2rem 0;border-top:1px solid rgba(46,204,122,0.18);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-size:0.72rem;color:#B8B0A0;">🇳🇬 <span style="color:#2ECC7A;font-weight:600;">Naija Cost Tracker</span> &nbsp;—&nbsp; Built with Streamlit · Python · dbt</div>
    <div style="font-size:0.7rem;color:#B8B0A0;">FX: {live_src} · Inflation: NBS (Jan 2026) · {datetime.now().strftime('%b %d, %Y')}</div>
</div>""", unsafe_allow_html=True)