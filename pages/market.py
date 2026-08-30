"""
Market page.

  Overview + table + analytics  -> get_market_data()   -> GET /coins/markets
  Totals (cap / volume)         -> get_global_stats()  -> GET /global
  Price line chart              -> get_price_history() -> GET /coins/{id}/market_chart
"""

import pandas as pd
import streamlit as st

from components.sidebar import sidebar
from components.ui import load_css, show_header
from graphs import (
    create_market_cap_chart,
    create_performance_chart,
    create_price_chart,
)
from utils.coingecko import (
    COIN_IDS,
    DAY_OPTIONS,
    get_global_stats,
    get_market_data,
    get_price_history,
)

st.set_page_config(
    page_title="MARKET - CryptoVision",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
sidebar()
show_header(title_image="market.png", image_width=200)

st.markdown(
    """
    <h1 style="color:#F0B90B;">Welcome to CryptoVision Market</h1>
    <p style="color:#F5F7FA; font-size:18px;">
        Track prices, market cap, and 24-hour moves.
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()


def format_money(value):
    if value is None or pd.isna(value):
        return "N/A"
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value:,.2f}"
    return f"${value:.2f}"


def format_price(value):
    if value is None or pd.isna(value):
        return "N/A"
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"
    if value >= 1:
        return f"${value:,.2f}"
    return f"${value:.6f}"


def usd_from_global(stats, key):
    """CoinGecko /global stores totals as {'usd': 123, 'btc': ...}."""
    if not isinstance(stats, dict):
        return None
    raw = stats.get(key)
    if isinstance(raw, dict):
        return raw.get("usd")
    if isinstance(raw, (int, float)):
        return raw
    return None


def market_table(raw_list):
    """Rename CoinGecko /coins/markets fields to short column names."""
    if not raw_list:
        return pd.DataFrame()

    df = pd.DataFrame(raw_list).rename(
        columns={
            "name": "Coin",
            "symbol": "Symbol",
            "current_price": "Price",
            "price_change_percentage_24h": "24h %",
            "market_cap": "Market Cap",
            "total_volume": "Volume",
            "market_cap_rank": "Rank",
        }
    )
    if "Symbol" in df.columns:
        df["Symbol"] = df["Symbol"].astype(str).str.upper()

    for col in ["Price", "24h %", "Market Cap", "Volume", "Rank"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df.drop_duplicates(subset=["id"]) if "id" in df.columns else df


with st.spinner("Loading market data..."):
    market_df = market_table(get_market_data(per_page=50))
    global_stats = get_global_stats()

if market_df.empty:
    st.error("No market data from CoinGecko. Check your API key and connection.")
    st.stop()

st.subheader("Market Overview")
btc_rows = market_df[market_df["id"].astype(str).str.lower() == "bitcoin"]
btc_change = float(btc_rows["24h %"].iloc[0]) if not btc_rows.empty else 0.0

c1, c2, c3, c4 = st.columns(4)
with c1:
    total_cap = usd_from_global(global_stats, "total_market_cap")
    if total_cap is None:
        total_cap = market_df["Market Cap"].sum()
    st.metric("Total Market Cap", format_money(total_cap))
with c2:
    top = market_df.iloc[0]
    st.metric("Top Coin", str(top["Coin"]), format_price(top["Price"]))
with c3:
    st.metric("BTC 24h Change", f"{btc_change:.2f}%")
with c4:
    total_volume = usd_from_global(global_stats, "total_volume")
    if total_volume is None:
        total_volume = market_df["Volume"].sum()
    st.metric("24h Trading Volume", format_money(total_volume))

st.divider()
st.subheader("Market Table")

search = st.text_input("Search by coin name or symbol", placeholder="bitcoin, eth, sol...")
shown = market_df
if search.strip():
    q = search.strip().lower()
    shown = market_df[
        market_df["Coin"].astype(str).str.lower().str.contains(q, na=False)
        | market_df["Symbol"].astype(str).str.lower().str.contains(q, na=False)
    ]

table = shown[["Coin", "Symbol", "Price", "24h %", "Market Cap", "Volume", "Rank"]].copy()
table["Price"] = table["Price"].apply(format_price)
table["Market Cap"] = table["Market Cap"].apply(format_money)
table["Volume"] = table["Volume"].apply(format_money)
table["24h %"] = table["24h %"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
st.dataframe(table, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Price Analysis")

p1, p2 = st.columns(2)
with p1:
    selected_coin = st.selectbox("Select cryptocurrency", list(COIN_IDS.keys()))
with p2:
    selected_period = st.selectbox("Select time period", list(DAY_OPTIONS.keys()), index=3)

with st.spinner(f"Loading {selected_coin} price chart..."):
    price_df = get_price_history(COIN_IDS[selected_coin], DAY_OPTIONS[selected_period])

if price_df.empty:
    st.warning("Price chart data is not available right now.")
else:
    st.plotly_chart(
        create_price_chart(price_df, selected_coin),
        use_container_width=True,
    )

st.divider()
st.subheader("Market Analytics")

a1, a2 = st.columns(2)
with a1:
    top_coins = (
        market_df.sort_values("Market Cap", ascending=False)
        .head(8)[["Coin", "Market Cap"]]
        .copy()
    )
    if top_coins.empty:
        st.warning("Market cap chart data is not available.")
    else:
        st.plotly_chart(create_market_cap_chart(top_coins), use_container_width=True)

with a2:
    names = {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "binancecoin": "BNB",
        "solana": "SOL",
        "ripple": "XRP",
        "cardano": "ADA",
        "dogecoin": "DOGE",
    }
    performance = market_df[market_df["id"].isin(names)].copy()
    performance["Coin"] = performance["id"].map(names)
    performance = performance[["Coin", "24h %"]].dropna()
    if performance.empty:
        st.warning("24h performance data is not available.")
    else:
        st.plotly_chart(create_performance_chart(performance), use_container_width=True)

st.caption("Live data powered by CoinGecko API")
