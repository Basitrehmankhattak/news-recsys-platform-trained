import streamlit as st
from state import ensure_state

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
ensure_state()

st.title("🏠 Home")
st.subheader("Industry-Grade News Recommendation System (Backend + UI)")

st.write("""
### What this UI does
- Calls your FastAPI backend:
  - `POST /recommendations` to fetch a ranked feed
  - `POST /click` to log clicks (idempotent per impression/item)
- Displays scores per item:
  - retrieval_score, rank_score, final_score
- Uses your real request fields:
  - anonymous_id, session_id, device_type, app_version, user_agent, referrer, page_size, surface, locale
""")

st.info("Go to **Feed** to generate recommendations and simulate clicks.")
