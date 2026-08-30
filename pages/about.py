"""About page. No CoinGecko calls — static text from assets/about.txt."""

from pathlib import Path

import streamlit as st

from components.sidebar import sidebar
from components.ui import load_css

st.set_page_config(
    page_title="ABOUT - CryptoVision",
    page_icon="assets/favicon.png",
    layout="wide",
)

load_css()
sidebar()

about_file = Path(__file__).resolve().parent.parent / "assets" / "about.txt"
if about_file.exists():
    st.markdown(about_file.read_text(), unsafe_allow_html=True)
else:
    st.info("About text is missing.")
st.divider()
