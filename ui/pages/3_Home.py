import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

st.markdown(f"<div class='title-center'>Welcome {st.session_state.user}</div>",
            unsafe_allow_html=True)

st.markdown("### Categories")

cats=["Technology","Sports","Politics","Business","Health","Entertainment"]

cols=st.columns(3)
for i,c in enumerate(cats):
    with cols[i%3]:
        if st.button(c):
            st.session_state["category"]=c
            st.switch_page("pages/4_Recommendations.py")

st.markdown("---")

if st.button("🎯 Personalized Feed"):
    st.session_state["category"]="For You"
    st.switch_page("pages/4_Recommendations.py")
