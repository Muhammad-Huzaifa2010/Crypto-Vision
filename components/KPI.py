"""Top-of-dashboard price cards. Expects raw CoinGecko /coins/markets rows."""

import streamlit as st

COINS = [
    ("bitcoin", "🟠 Bitcoin"),
    ("ethereum", "🔵 Ethereum"),
    ("solana", "🟢 Solana"),
]


def kpi_cards(market_df):
    if market_df is None or market_df.empty:
        st.warning("No market data available.")
        return

    needed = {"id", "current_price", "price_change_percentage_24h"}
    if not needed.issubset(market_df.columns):
        st.error("Market data is missing price columns from CoinGecko.")
        return

    cols = st.columns(len(COINS))
    for column, (coin_id, label) in zip(cols, COINS):
        row = market_df[market_df["id"] == coin_id]
        with column:
            if row.empty:
                st.metric(label, "N/A")
                continue
            price = row.iloc[0]["current_price"]
            change = row.iloc[0]["price_change_percentage_24h"]
            st.metric(label, f"${price:,.2f}", f"{change:.2f}%")
