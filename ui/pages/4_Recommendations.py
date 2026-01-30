import sys
import os
import streamlit as st
import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import load_css

load_css()

# --------------------------------------------------
# AUTH
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

# --------------------------------------------------
# HEADER
# --------------------------------------------------

h1, h2 = st.columns([6,1])

with h1:
    st.markdown(
        "<div class='title-center'>🎯 Recommendations</div>",
        unsafe_allow_html=True
    )

with h2:
    if st.button("🏠 Home"):
        st.switch_page("pages/3_Home.py")

# --------------------------------------------------
# STATE INIT
# --------------------------------------------------

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "news"

if "rec_items" not in st.session_state:
    st.session_state.rec_items = None

if "rec_impression_id" not in st.session_state:
    st.session_state.rec_impression_id = None

# --------------------------------------------------
# CATEGORY GRID
# --------------------------------------------------

st.markdown("### 📂 Choose Category")

categories = [
    "news","sports","entertainment","finance",
    "health","movies","tv","music",
    "travel","foodanddrink","weather","kids",
    "autos","lifestyle"
]

cols = st.columns(4)

for i, cat in enumerate(categories):
    with cols[i % 4]:
        if st.button(cat.title(), use_container_width=True):

            if cat != st.session_state.selected_category:
                st.session_state.selected_category = cat
                st.session_state.rec_items = None
                st.session_state.rec_impression_id = None
                st.rerun()

category = st.session_state.selected_category

# --------------------------------------------------
# FETCH RECOMMENDATIONS
# --------------------------------------------------

if st.session_state.rec_items is None:

    payload = {
        "session_id": st.session_state.session_id,
        "anonymous_id": anonymous_id,
        "page_size": 10,
        "surface": "recommendations",
        "locale": "en-US",
        "category": category
    }

    with st.spinner("Loading recommendations..."):
        r = requests.post(
            f"{API}/recommendations",
            json=payload,
            timeout=10
        )

    if r.status_code != 200:
        st.error("Failed to load recommendations")
        st.stop()

    data = r.json()
    st.session_state.rec_items = data.get("items", [])
    st.session_state.rec_impression_id = data.get("impression_id")

items = st.session_state.rec_items
impression_id = st.session_state.rec_impression_id

# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

if not items:
    st.warning("No recommendations found.")
    st.stop()

# --------------------------------------------------
# SHOW ARTICLES
# --------------------------------------------------

st.markdown("### 📰 Articles")

for rec in items:

    with st.container(border=True):

        c1, c2 = st.columns([1,3])

        with c1:
            st.image(
                "https://via.placeholder.com/300x180?text=News",
                use_container_width=True
            )

        with c2:
            st.markdown(f"**{rec['title']}**")
            st.caption(f"Category: {category.capitalize()}")
            st.caption(f"Position: {rec['position']}")

            if st.button("Open Article", key=f"rec_{rec['item_id']}"):

                # 🔒 LOG CLICK
                requests.post(
                    f"{API}/click",
                    json={
                        "impression_id": impression_id,
                        "item_id": rec["item_id"],
                        "position": rec["position"],
                        "anonymous_id": anonymous_id,
                        "open_type": "recommendations"
                    }
                )

                # Pass context to article page
                st.session_state["open_item"] = rec["item_id"]
                st.session_state["open_position"] = rec["position"]
                st.session_state["open_impression"] = impression_id

                st.switch_page("pages/9_Article.py")
