"""Shared page chrome: CSS, logo header. Used by every page."""

from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def load_css():
    css_path = ASSETS / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def show_header(title_image=None, title_text=None, image_width=250):
    """Logo on the left, name image or text title on the right."""
    left, right = st.columns([1, 15])
    logo = ASSETS / "l.png"

    with left:
        if logo.exists():
            st.image(str(logo), width=100)

    with right:
        if title_image:
            image_path = ASSETS / title_image
            if image_path.exists():
                st.image(str(image_path), width=image_width)
                return
        if title_text:
            st.title(title_text)
