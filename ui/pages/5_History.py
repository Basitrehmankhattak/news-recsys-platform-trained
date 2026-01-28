import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
API="http://127.0.0.1:8000"

if "session_id" not in st.session_state:
    st.switch_page("pages/1_Login.py")

st.markdown("<div class='title-center'>📜 Click History</div>",
            unsafe_allow_html=True)

r=requests.get(f"{API}/history/{st.session_state.session_id}")

if r.status_code!=200:
    st.error("Failed loading history")
else:
    data=r.json()
    if not data:
        st.info("No clicks yet")
    else:
        for h in data:
            st.markdown(f"<div class='card'>{h['title']}</div>",
                        unsafe_allow_html=True)
