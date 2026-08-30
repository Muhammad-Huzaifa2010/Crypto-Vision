"""
Dashboard (home page).

Data:
  KPI cards  -> get_market_data()  -> GET /coins/markets
  Chart      -> get_ohlc()         -> GET /coins/{id}/ohlc
"""

import pandas as pd
import streamlit as st

from components.KPI import kpi_cards
from components.footer import footer
from components.sidebar import sidebar
from components.ui import load_css, show_header
from graphs import dashboard_graphs
from utils.coingecko import get_market_data

st.set_page_config(
    page_title="DASHBOARD - CryptoVision",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
sidebar()

st.markdown(
    '<p style="color:#D4AF37; font-size:24px; font-style:italic;">'
    "See Today · Trade Tomorrow · Own The Future</p>",
    unsafe_allow_html=True,
)
show_header(title_image="name.png")
st.markdown("Welcome to **CryptoVision**. Live prices and a candlestick chart from CoinGecko.")

market_data = get_market_data()
market_df = pd.DataFrame(market_data)

kpi_cards(market_df)
dashboard_graphs()
st.divider()
footer()
