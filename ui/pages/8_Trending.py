import sys
import os
import streamlit as st
import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import load_css

load_css()

# AUTH
# -----------------------

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/1_Login.py")
    st.stop()

if "anonymous_id" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

# -----------------------
# IMPORTS
# -----------------------

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_css()

API = "http://127.0.0.1:8000"
anonymous_id = st.session_state["anonymous_id"]

# -----------------------
# HEADER
# -----------------------

st.markdown("<div class='title-center'>🔥 Trending Now</div>", unsafe_allow_html=True)

# -----------------------
# FETCH
# -----------------------

with st.spinner("Loading trending articles..."):
    r = requests.get(f"{API}/trending")

if r.status_code != 200:
    st.error("Failed loading trending")
    st.stop()

items = r.json()

if not items:
    st.info("No trending data yet")
    st.stop()

# -----------------------
# DISPLAY
# -----------------------

for idx, t in enumerate(items, 1):

    with st.container(border=True):

        st.markdown(f"### #{idx}")
        st.markdown(f"**{t['title']}**")
        st.caption(f"🔥 {t['clicks']} clicks")

        if st.button("Open Article", key=f"trend_{t['item_id']}"):

            # 🔒 LOG CLICK
            requests.post(
                f"{API}/click",
                json={
                    "impression_id": "trending",
                    "item_id": t["item_id"],
                    "position": idx,
                    "anonymous_id": anonymous_id,
                    "open_type": "trending"
                }
            )

            st.session_state["open_item"] = t["item_id"]
            st.session_state["open_position"] = idx
            st.session_state["open_impression"] = "trending"

            st.switch_page("pages/9_Article.py")

# -----------------------
# NAV
# -----------------------

if st.button("🏠 Back to Home", use_container_width=True):
    st.switch_page("pages/3_Home.py")
