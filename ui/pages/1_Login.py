import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys
import os
import streamlit as st
import requests
from style import load_css

load_css()





# -----------------------
# Page Config
# -----------------------

st.set_page_config(
    page_title="Login",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}

body {
    background-color: #0e0e0e;
}

.login-card {
    max-width: 420px;
    margin: auto;
    margin-top: 80px;
    padding: 2.5rem;
    border-radius: 14px;
    background: #111111;
    box-shadow: 0 0 25px rgba(0,0,0,0.35);
}

.login-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.login-sub {
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
# Session Defaults
# -----------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "anonymous_id" not in st.session_state:
    st.session_state.anonymous_id = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# -----------------------
# UI
# -----------------------

st.markdown("""
<div class="login-card">
  <div class="login-title">🔐 Login</div>
  <div class="login-sub">Access your personalized news</div>
</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

# -----------------------
# Login Action
# -----------------------

if submit:

    if not username or not password:
        st.error("Please fill all fields")
        st.stop()

    with st.spinner("Authenticating..."):

        r = requests.post(
            f"{API}/auth/login",
            json={"username": username, "password": password}
        )

    if r.status_code != 200:
        st.error("Invalid username or password")
        st.stop()

    login_data = r.json()

    anonymous_id = login_data["anonymous_id"]   # 🔒 FROM BACKEND

    # -----------------------
    # Start Session
    # -----------------------

    s = requests.post(
        f"{API}/session/start",
        json={
            "anonymous_id": anonymous_id,
            "device_type": "web",
            "app_version": "streamlit",
            "user_agent": "streamlit-ui",
            "referrer": "direct"
        }
    )

    if s.status_code != 200:
        st.error("Session start failed")
        st.stop()

    st.session_state.logged_in = True
    st.session_state.anonymous_id = anonymous_id
    st.session_state.session_id = s.json()["session_id"]

    st.success("Login successful")
    st.switch_page("pages/3_Home.py")

# -----------------------
# Register Link
# -----------------------

st.markdown("---")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("Create Account", use_container_width=True):
        st.switch_page("pages/2_Register.py")
