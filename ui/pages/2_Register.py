import sys
import os
import streamlit as st
import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import load_css

load_css()


# -----------------------
# Page Config
# -----------------------

st.set_page_config(
    page_title="Register",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}

body {
    background-color: #0e0e0e;
}

.register-card {
    max-width: 420px;
    margin: auto;
    margin-top: 80px;
    padding: 2.5rem;
    border-radius: 14px;
    background: #111111;
    box-shadow: 0 0 25px rgba(0,0,0,0.35);
}

.register-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.register-sub {
    text-align: center;
    opacity: 0.7;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Imports
# -----------------------

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css
load_css()

API = "http://127.0.0.1:8000"

# -----------------------
# UI
# -----------------------

st.markdown("""
<div class="register-card">
  <div class="register-title">🆕 Create Account</div>
  <div class="register-sub">Join to personalize your news feed</div>
</div>
""", unsafe_allow_html=True)

with st.form("register_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Create Account")

# -----------------------
# Register Action
# -----------------------

if submit:

    if not username or not password:
        st.error("Please fill all fields")
        st.stop()

    with st.spinner("Creating account..."):

        r = requests.post(
            f"{API}/auth/register",
            json={"username": username, "password": password}
        )

    if r.status_code != 200:
        st.error("Username already exists")
        st.stop()

    st.success("Account created successfully!")
    st.switch_page("pages/1_Login.py")

# -----------------------
# Back to Login
# -----------------------

st.markdown("---")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("⬅ Back to Login", use_container_width=True):
        st.switch_page("pages/1_Login.py")
