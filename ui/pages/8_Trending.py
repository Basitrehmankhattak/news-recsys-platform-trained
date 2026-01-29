import streamlit as st
import requests
from style import load_css

load_css()
API="http://127.0.0.1:8000"

st.markdown("<div class='title-center'>🔥 Trending Now</div>", unsafe_allow_html=True)

r = requests.get(f"{API}/trending/")

if r.status_code!=200:
    st.error("Failed to load trending")
    st.stop()

for t in r.json():
    if st.button(
        f"{t['title']}  🔥 {t['clicks']} clicks",
        key=f"trend_{t['item_id']}"
    ):
        st.session_state["open_item"] = t["item_id"]
        st.switch_page("pages/9_Article.py")
