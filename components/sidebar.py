"""Left navigation. Hides Streamlit's auto page list and uses our buttons."""

from pathlib import Path

import streamlit as st

LOGO = Path(__file__).resolve().parent.parent / "assets" / "l.png"


def sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=200)

        if st.button("🏠 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.switch_page("app.py")
        if st.button("📈 Market", use_container_width=True, key="nav_market"):
            st.switch_page("pages/market.py")
        if st.button("🔥 Trending", use_container_width=True, key="nav_trending"):
            st.switch_page("pages/trending.py")
        if st.button("ℹ️ About", use_container_width=True, key="nav_about"):
            st.switch_page("pages/about.py")
