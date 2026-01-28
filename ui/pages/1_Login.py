import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
API="http://127.0.0.1:8000"

st.markdown("<div class='title-center'>🔐 Login</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Access your personalized news</div>", unsafe_allow_html=True)

with st.form("login"):
    username=st.text_input("Username")
    password=st.text_input("Password",type="password")
    submit=st.form_submit_button("Login")

if submit:
    if not username or not password:
        st.error("Fill all fields")
    else:
        r=requests.post(f"{API}/auth/login",
                        json={"username":username,"password":password})

        if r.status_code!=200:
            st.error("Invalid credentials")
        else:
            s=requests.post(f"{API}/session/start",json={
                "anonymous_id":username,
                "device_type":"web",
                "app_version":"streamlit",
                "user_agent":"ui",
                "referrer":"direct"
            })

            st.session_state["user"]=username
            st.session_state["session_id"]=s.json()["session_id"]

            st.success("Login successful")
            st.switch_page("pages/3_Home.py")

st.markdown("---")
if st.button("Create Account"):
    st.switch_page("pages/2_Register.py")
