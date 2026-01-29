import os
from dotenv import load_dotenv
import streamlit as st

from state import ensure_state

load_dotenv()
ensure_state()

APP_NAME = os.getenv("APP_NAME", "News Recommendation System")

st.set_page_config(page_title=APP_NAME, page_icon="🗞️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
h1,h2,h3 {letter-spacing: -0.02em;}
</style>
""", unsafe_allow_html=True)

st.title(f"🗞️ {APP_NAME}")
st.write("Use the sidebar to navigate pages (we will add pages next).")
st.info("Step-by-step UI build in progress ✅")
