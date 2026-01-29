import sys
import os
import streamlit as st
import requests
from style import load_css

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_css()

API = "http://127.0.0.1:8000"

# ----------------------------
# Auth Guard
# ----------------------------
if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

st.markdown(
    "<div class='title-center'>🎯 Recommendations</div>",
    unsafe_allow_html=True
)

# ----------------------------
# State Init
# ----------------------------
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"

if "rec_items" not in st.session_state:
    st.session_state.rec_items = None

if "rec_impression_id" not in st.session_state:
    st.session_state.rec_impression_id = None

# ----------------------------
# Category UI
# ----------------------------
categories = [
    "All",
    "Technology",
    "Sports",
    "Business",
    "Politics",
    "Health",
    "Entertainment"
]

selected_category = st.selectbox(
    "📂 Choose Category",
    categories,
    index=categories.index(st.session_state.selected_category)
)

# ----------------------------
# Detect Category Change
# ----------------------------
if selected_category != st.session_state.selected_category:
    st.session_state.selected_category = selected_category
    st.session_state.rec_items = None
    st.session_state.rec_impression_id = None

# ----------------------------
# Fetch Recommendations
# ----------------------------
if st.session_state.rec_items is None:

    payload = {
        "session_id": st.session_state.session_id,
        "user_id": None,
        "anonymous_id": st.session_state.session_id,
        "surface": "recommendations",
        "page_size": 10,
        "locale": "en-US",
        "category": None if selected_category == "All" else selected_category
    }

    res = requests.post(
        f"{API}/recommendations",
        json=payload,
        timeout=10
    )

    if res.status_code != 200:
        st.error(res.text)
        st.stop()

    data = res.json()
    st.session_state.rec_items = data["items"]
    st.session_state.rec_impression_id = data["impression_id"]

items = st.session_state.rec_items or []

# ----------------------------
# Display + Open Article
# ----------------------------
for rec in items:

    if st.button(rec["title"], key=f"rec_{rec['item_id']}"):

        # ✅ log click (now always valid)
        requests.post(
            f"{API}/click",
            json={
                "impression_id": st.session_state.rec_impression_id,
                "item_id": rec["item_id"],
                "position": rec["position"],
                "dwell_ms": 0,
                "open_type": "ui"
            }
        )

        st.session_state["open_item"] = rec["item_id"]
        st.switch_page("pages/9_Article.py")
