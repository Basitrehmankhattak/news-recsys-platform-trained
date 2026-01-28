import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()

if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

st.markdown("<div class='title-center'>👤 Profile</div>",unsafe_allow_html=True)

st.markdown(f"""
<div class='card'>
<b>Username:</b> {st.session_state.user}<br>
<b>User Type:</b> Warm<br>
<b>Language:</b> EN<br>
<b>Status:</b> Active
</div>
""",unsafe_allow_html=True)
