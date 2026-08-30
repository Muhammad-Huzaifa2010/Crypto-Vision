import streamlit as st


def footer():
    st.markdown(
        """
        <div style="color:#F0B90B; text-align:center; font-size:14px; padding:20px;">
            Made by M.Huzaifa · Python | Streamlit<br>
            Powered by CoinGecko API<br>
            © 2026 CryptoVision
        </div>
        """,
        unsafe_allow_html=True,
    )
