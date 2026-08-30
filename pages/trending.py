"""
Trending page.

  get_trending_coins() -> GET /search/trending
  Each coin lives under item: { name, symbol, market_cap_rank, score, large }
"""

import pandas as pd
import streamlit as st

from components.sidebar import sidebar
from components.ui import load_css, show_header
from utils.coingecko import get_trending_coins

st.set_page_config(
    page_title="TRENDING - CryptoVision",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
sidebar()
show_header(title_text="TRENDING - Cryptocurrencies")

st.markdown(
    """
    <p style="color:#B7BDC6; font-size:17px;">
        Coins getting the most search attention on CoinGecko right now.
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

with st.spinner("Loading trending cryptocurrencies..."):
    trending = get_trending_coins()

if not trending:
    st.error("Unable to load trending coins from CoinGecko.")
    st.stop()

coins = []
for entry in trending:
    item = entry.get("item") or {}
    coins.append(
        {
            "Name": item.get("name"),
            "Symbol": str(item.get("symbol") or "").upper(),
            "Rank": item.get("market_cap_rank"),
            "Score": item.get("score"),
        }
    )

if not coins:
    st.warning("No trending coins found.")
    st.stop()

top = coins[0]
st.subheader("🔥 Top Trending")
st.html(
    f"""
    <div style="background:linear-gradient(135deg,#181D25,#11151C);
                border:1px solid #F0B90B; border-radius:16px; padding:24px; margin:10px 0 25px 0;">
        <div style="color:#F0B90B; font-size:14px; font-weight:600;">🔥 TOP TRENDING</div>
        <div style="color:#F5F7FA; font-size:30px; font-weight:700; margin-top:8px;">{top["Name"]}</div>
        <div style="color:#848E9C; font-size:16px; margin-top:5px;">
            {top["Symbol"]} · Market Rank #{top["Rank"]}
        </div>
    </div>
    """
)

st.subheader("🚀 Trending Now")
columns = st.columns(3)
for index, coin in enumerate(coins[:6]):
    rank = coin["Rank"] if coin["Rank"] is not None else "N/A"
    with columns[index % 3]:
        st.html(
            f"""
            <div style="background:#181D25; border:1px solid #2B3139;
                        border-radius:14px; padding:20px; margin-bottom:18px;">
                <div style="color:#F0B90B; font-size:14px; font-weight:600;">🔥 Trending #{index + 1}</div>
                <div style="color:#F5F7FA; font-size:22px; font-weight:700; margin-top:8px;">{coin["Name"]}</div>
                <div style="color:#848E9C; margin-top:5px;">{coin["Symbol"]}</div>
                <div style="color:#B7BDC6; margin-top:12px;">Market Rank: #{rank}</div>
            </div>
            """
        )

st.subheader("📊 Trending List")
st.dataframe(
    pd.DataFrame(coins)[["Rank", "Name", "Symbol", "Score"]],
    width="stretch",
    hide_index=True,
)

st.subheader("🔍 Explore Trending Coin")
selected = st.selectbox("Select a cryptocurrency", [c["Name"] for c in coins])
chosen = next((c for c in coins if c["Name"] == selected), None)

if chosen:
    m1, m2, m3 = st.columns(3)
    m1.metric("Coin", chosen["Name"])
    m2.metric("Market Rank", f"#{chosen['Rank']}" if chosen["Rank"] is not None else "N/A")
    m3.metric("Trending Score", str(chosen["Score"]) if chosen["Score"] is not None else "N/A")
