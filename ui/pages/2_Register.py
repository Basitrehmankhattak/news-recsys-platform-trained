import sys
import os
import streamlit as st
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
API="http://127.0.0.1:8000"

st.markdown("<div class='title-center'>🆕 Register</div>", unsafe_allow_html=True)

with st.form("reg"):
    username=st.text_input("Username")
    password=st.text_input("Password",type="password")
    submit=st.form_submit_button("Create Account")

if submit:
    if not username or not password:
        st.error("Fill all fields")
    else:
        r=requests.post(f"{API}/auth/register",
                        json={"username":username,"password":password})

        if r.status_code!=200:
            st.error("Username already exists")
        else:
            st.success("Account created!")
            st.switch_page("pages/1_Login.py")
