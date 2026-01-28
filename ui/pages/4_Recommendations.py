import sys
import os
import streamlit as st
import requests
from style import load_css

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_css()

API = "http://127.0.0.1:8000"

# -----------------------
# Auth Guard
# -----------------------
if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

# -----------------------
# Page Title
# -----------------------
st.markdown("<div class='title-center'>🎯 Recommendations</div>", unsafe_allow_html=True)

# -----------------------
# Category
# -----------------------
if "selected_category" in st.session_state:
    default_category = st.session_state["selected_category"]
else:
    default_category = "All"

categories = ["All", "Technology", "Sports", "Business", "Politics", "Health", "Entertainment"]

selected_category = st.selectbox(
    "📂 Choose Category",
    categories,
    index=categories.index(default_category)
)


# Reset cache when category changes
if st.session_state.selected_category != selected_category:
    st.session_state.selected_category = selected_category
    st.session_state.pop("rec_items", None)
    st.session_state.pop("rec_impression_id", None)

# -----------------------
# Build Payload
# -----------------------
payload = {
    "session_id": st.session_state.session_id,
    "user_id": None,
    "anonymous_id": st.session_state.session_id,
    "surface": "recommendations",
    "page_size": 10,
    "locale": "en-US",
    "category": None if selected_category == "All" else selected_category
}


# -----------------------
# Fetch Recommendations
# -----------------------
if "rec_items" not in st.session_state:

    res = requests.post(f"{API}/recommendations", json=payload)

    if res.status_code != 200:
        st.error("Backend error")
        st.stop()

    data = res.json()
    st.session_state.rec_impression_id = data["impression_id"]
    st.session_state.rec_items = data["items"]

items = st.session_state.rec_items

# -----------------------
# Display
# -----------------------
for rec in items:

    with st.container():
        if st.button(
            f"{rec['position']}. {rec['title']}",
            key=f"rec_{rec['item_id']}"
        ):

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

            st.success("Clicked!")
