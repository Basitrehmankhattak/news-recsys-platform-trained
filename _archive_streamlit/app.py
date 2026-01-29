import os
from dotenv import load_dotenv
import streamlit as st
from state import ensure_state
ensure_state()

from state import ensure_state

load_dotenv()
ensure_state()

APP_NAME = os.getenv("APP_NAME", "News Recommendation System")

st.set_page_config(page_title=APP_NAME, page_icon="🗞️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
h1,h2,h3 {letter-spacing: -0.02em;}
.small-muted {color: #777; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

st.title(f"🗞️ {APP_NAME}")
st.write("Use the sidebar to navigate pages.")
st.markdown('<div class="small-muted">Streamlit demo UI (FastAPI + Postgres + FAISS + Ranker)</div>', unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Demo status")
    st.write(f"Anonymous ID: `{st.session_state.get('anonymous_id')}`")
    st.write(f"User status: **{st.session_state.get('user_status', 'unknown')}**")
    st.write(f"Dev mode: **{st.session_state.get('dev_mode', False)}**")
