import streamlit as st
import requests
from style import load_css

load_css()

API = "http://127.0.0.1:8000"

if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

st.markdown("<div class='title-center'>🔥 Trending Now</div>", unsafe_allow_html=True)

res = requests.get(f"{API}/trending")

if res.status_code != 200:
    st.error("Failed to load trending")
    st.stop()

data = res.json()

if not data:
    st.info("No trending articles yet")
else:
    for i, row in enumerate(data, 1):
        st.markdown(
            f"<div class='card'>{i}. {row['title']} <span style='float:right'>🔥 {row['clicks']}</span></div>",
            unsafe_allow_html=True
        )
