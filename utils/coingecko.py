"""
CoinGecko API — the only place this app talks to CoinGecko.

All pages call these functions. Do not call requests.get() elsewhere.

  Dashboard (app.py)     -> get_market_data, get_ohlc
  Market (pages/market)  -> get_market_data, get_global_stats, get_price_history
  Trending (pages/trending) -> get_trending_coins

Docs: https://docs.coingecko.com/v3.0.1/reference/introduction
"""

import os

import pandas as pd
import requests
import streamlit as st

BASE_URL = "https://api.coingecko.com/api/v3"

# CoinGecko OHLC only allows these day values
OHLC_DAYS = [1, 7, 14, 30, 90, 180, 365]

DAY_OPTIONS = {
    "1 Day": 1,
    "7 Days": 7,
    "14 Days": 14,
    "30 Days": 30,
    "90 Days": 90,
    "1 Year": 365,
}

# Display name -> CoinGecko coin id
COIN_IDS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Solana": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
}


def _api_key():
    """Read key from Streamlit secrets, then from environment. Empty is OK (public rate limit)."""
    try:
        key = st.secrets.get("COINGECKO_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("COINGECKO_API_KEY", "")


def get_data(endpoint, params=None):
    """GET a CoinGecko endpoint. Returns JSON, or None on error."""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    key = _api_key()
    if key:
        headers["x-cg-demo-api-key"] = key

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        st.error(f"CoinGecko API error: {error}")
        return None


@st.cache_data(ttl=60)
def get_market_data(per_page=50):
    """Top coins by market cap. GET /coins/markets"""
    data = get_data(
        "/coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        },
    )
    return data if isinstance(data, list) else []


@st.cache_data(ttl=300)
def get_global_stats():
    """Whole-market totals. GET /global  ->  response['data']"""
    data = get_data("/global")
    if not isinstance(data, dict):
        return {}
    return data.get("data", {})


@st.cache_data(ttl=300)
def get_trending_coins():
    """Coins people are searching. GET /search/trending  ->  response['coins']"""
    data = get_data("/search/trending")
    if not isinstance(data, dict):
        return []
    return data.get("coins", [])


@st.cache_data(ttl=60)
def get_ohlc(coin_id, days=30):
    """
    Candlestick rows. GET /coins/{id}/ohlc

    CoinGecko list: [timestamp_ms, open, high, low, close]
    Returns a DataFrame with Date, Open, High, Low, Close.
    """
    data = get_data(
        f"/coins/{coin_id}/ohlc",
        {"vs_currency": "usd", "days": days},
    )
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=["Timestamp", "Open", "High", "Low", "Close"])
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms")
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Date", "Open", "High", "Low", "Close"]).reset_index(drop=True)


@st.cache_data(ttl=60)
def get_price_history(coin_id, days=30):
    """
    Line-chart prices. GET /coins/{id}/market_chart

    Returns a DataFrame with Date, Price.
    """
    data = get_data(
        f"/coins/{coin_id}/market_chart",
        {"vs_currency": "usd", "days": days},
    )
    if not isinstance(data, dict):
        return pd.DataFrame()

    prices = data.get("prices") or []
    if not prices:
        return pd.DataFrame()

    df = pd.DataFrame(prices, columns=["Timestamp", "Price"])
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    return df.dropna(subset=["Date", "Price"])[["Date", "Price"]].reset_index(drop=True)
