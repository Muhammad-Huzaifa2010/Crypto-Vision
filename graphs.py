"""
Plotly charts only. Pages fetch data, then pass a DataFrame here.

  Dashboard -> create_candlestick_chart  (OHLC from get_ohlc)
  Market    -> create_price_chart, create_market_cap_chart, create_performance_chart
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.coingecko import COIN_IDS, OHLC_DAYS, get_ohlc

BG = "#0B0E11"
CARD = "#181D25"
BORDER = "#2B3139"
GOLD = "#F0B90B"
TEXT = "#F5F7FA"
MUTED = "#848E9C"
GREEN = "#0ECB81"
RED = "#F6465D"


def _layout(title, height=450):
    return dict(
        title=dict(text=title, font=dict(color=GOLD, size=16)),
        template="plotly_dark",
        height=height,
        paper_bgcolor=BG,
        plot_bgcolor=CARD,
        font=dict(color=TEXT, size=12),
        hovermode="x unified",
        margin=dict(l=50, r=30, t=60, b=40),
        xaxis=dict(gridcolor=BORDER, showgrid=True),
        yaxis=dict(gridcolor=BORDER, showgrid=True),
        legend=dict(bgcolor=CARD, bordercolor=BORDER, borderwidth=1),
    )


def create_price_chart(df, coin_name):
    """Line chart. Needs columns: Date, Price (from get_price_history)."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Price"],
            mode="lines",
            name=coin_name,
            line=dict(color=GOLD, width=2),
            hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>Price: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout(f"{coin_name} Price Chart", height=500),
        xaxis_title="Date / Time",
        yaxis_title="Price (USD)",
    )
    return fig


def create_market_cap_chart(df):
    """Horizontal bars. Needs columns: Coin, Market Cap."""
    chart_df = df.sort_values("Market Cap", ascending=True)
    fig = px.bar(
        chart_df,
        x="Market Cap",
        y="Coin",
        orientation="h",
        color_discrete_sequence=[GOLD],
    )
    fig.update_layout(
        **_layout("Top Cryptocurrencies by Market Cap", height=450),
        xaxis_title="Market Cap (USD)",
        yaxis_title="",
        showlegend=False,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Market Cap: $%{x:,.0f}<extra></extra>")
    return fig


def create_performance_chart(df):
    """24h % bars. Needs columns: Coin, 24h %."""
    chart_df = df.sort_values("24h %", ascending=True)
    colors = [GREEN if value >= 0 else RED for value in chart_df["24h %"]]
    fig = go.Figure(
        data=[
            go.Bar(
                x=chart_df["Coin"],
                y=chart_df["24h %"],
                marker_color=colors,
                hovertemplate="<b>%{x}</b><br>24h Change: %{y:.2f}%<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        **_layout("24-Hour Price Performance", height=450),
        xaxis_title="Coin",
        yaxis_title="24h Change (%)",
        showlegend=False,
    )
    fig.add_hline(y=0, line_color=MUTED, line_width=1)
    return fig


def create_candlestick_chart(df, coin_name):
    """Candles. Needs columns: Date, Open, High, Low, Close (from get_ohlc)."""
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name=coin_name,
                increasing_line_color=GREEN,
                decreasing_line_color=RED,
            )
        ]
    )
    fig.update_layout(
        **_layout(f"{coin_name} Candlestick Chart", height=560),
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
    )
    return fig


def dashboard_graphs():
    """Dashboard: coin picker + one full-width candlestick from CoinGecko OHLC."""
    coin_name = st.selectbox("Select coin", list(COIN_IDS.keys()), index=0)
    days = st.select_slider("Time range (days)", options=OHLC_DAYS, value=30)

    ohlc_df = get_ohlc(COIN_IDS[coin_name], days)
    if ohlc_df.empty:
        st.error("Unable to load candlestick data from CoinGecko. Try again later.")
        return

    st.plotly_chart(create_candlestick_chart(ohlc_df, coin_name), use_container_width=True)
    st.caption(f"Live OHLC from CoinGecko · {coin_name} · last {days} days")
