import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
API = "http://127.0.0.1:8000"

# -----------------------
# Auth Guard
# -----------------------
if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

# -----------------------
# Refresh Button
# -----------------------
if st.button("🔄 Refresh History"):
    st.rerun()

# -----------------------
# Title
# -----------------------
st.markdown(
    "<div class='title-center'>📜 Click History</div>",
    unsafe_allow_html=True
)

# -----------------------
# Fetch History
# -----------------------
r = requests.get(f"{API}/history/{st.session_state.session_id}")


if r.status_code != 200:
    st.error("Failed loading history")
    st.stop()

data = r.json()

if not data:
    st.info("No clicks yet")
    st.stop()

# -----------------------
# Display
# -----------------------
for i, h in enumerate(data, start=1):
    st.markdown(
        f"""
        <div class='card'>
            <b>{i}. {h['title']}</b><br>
            <small>{h['clicked_at']}</small>
        </div>
        """,
        unsafe_allow_html=True
    )
