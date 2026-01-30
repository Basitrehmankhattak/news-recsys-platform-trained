import sys
import os
import streamlit as st
import requests
from style import load_css

# --------------------------------------------------
# AUTH GUARD
# --------------------------------------------------

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/1_Login.py")
    st.stop()

if "anonymous_id" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_css()

API = "http://127.0.0.1:8000"
anonymous_id = st.session_state["anonymous_id"]
session_id = st.session_state["session_id"]

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown("<div class='title-center'>🏠 Home</div>", unsafe_allow_html=True)

st.caption(f"Session: {session_id}")

# --------------------------------------------------
# FETCH RECOMMENDATIONS
# --------------------------------------------------

payload = {
    "session_id": session_id,
    "anonymous_id": anonymous_id,
    "surface": "home",
    "page_size": 10,
    "locale": "en-US"
}

with st.spinner("Loading recommendations..."):
    resp = requests.post(
        f"{API}/recommendations",
        json=payload
    )

if resp.status_code != 200:
    st.error("Backend error")
    st.stop()

data = resp.json()
items = data["items"]
impression_id = data["impression_id"]

# --------------------------------------------------
# DISPLAY
# --------------------------------------------------

st.subheader("Recommended for you")

if not items:
    st.info("No recommendations available.")
    st.stop()

for rec in items:

    with st.container(border=True):

        st.markdown(f"**{rec['title']}**")
        st.caption(f"Position: {rec['position']}")

        if st.button("Open Article", key=f"home_{rec['item_id']}"):

            # 🔒 LOG CLICK
            requests.post(
                f"{API}/click",
                json={
                    "impression_id": impression_id,
                    "item_id": rec["item_id"],
                    "position": rec["position"],
                    "anonymous_id": anonymous_id,
                    "open_type": "home"
                }
            )

            st.session_state["open_item"] = rec["item_id"]
            st.session_state["open_position"] = rec["position"]
            st.session_state["open_impression"] = impression_id

            st.switch_page("pages/9_Article.py")
