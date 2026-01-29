import streamlit as st
import requests
from style import load_css

load_css()
API="http://127.0.0.1:8000"

item_id = st.session_state.get("open_item")

if not item_id:
    st.warning("Select an article first")
    st.stop()

r = requests.get(f"{API}/articles/{item_id}")

if r.status_code!=200:
    st.error("Failed loading article")
else:
    a=r.json()
    st.markdown(f"<h2>{a['title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"**Category:** {a['category']}")
    st.markdown("---")
    st.write(a["abstract"])
