import sys
import os
import streamlit as st
import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import load_css

load_css()

# -----------------------
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
from style import load_css
load_css()

API = "http://127.0.0.1:8000"
anonymous_id = st.session_state["anonymous_id"]

# -----------------------
# HEADER
# -----------------------

st.markdown(
    "<div class='title-center'>📜 Click History</div>",
    unsafe_allow_html=True
)

# -----------------------
# FETCH HISTORY
# -----------------------

with st.spinner("Loading history..."):

    r = requests.get(f"{API}/history/{anonymous_id}")

if r.status_code != 200:
    st.error("Failed loading history")
    st.stop()

data = r.json()

if not data:
    st.info("No clicks yet")
    st.stop()

# -----------------------
# DISPLAY
# -----------------------

for idx, h in enumerate(data, 1):

    with st.container(border=True):

        st.markdown(f"**{idx}. {h['title']}**")
        st.caption(f"Category: {h['category']}")
        st.caption(f"Clicked at: {h['clicked_at']}")

        if st.button("Open Article", key=f"hist_{h['item_id']}"):

            # 🔒 LOG CLICK
            requests.post(
                f"{API}/click",
                json={
                    "impression_id": "history",
                    "item_id": h["item_id"],
                    "position": idx,
                    "anonymous_id": anonymous_id,
                    "open_type": "history"
                }
            )

            st.session_state["open_item"] = h["item_id"]
            st.session_state["open_position"] = idx
            st.session_state["open_impression"] = "history"

            st.switch_page("pages/9_Article.py")
