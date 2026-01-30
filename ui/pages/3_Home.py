import sys
import os
import streamlit as st
import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import load_css

load_css()


# -----------------------
# AUTH GUARD
# -----------------------

if "logged_in" not in st.session_state or not st.session_state.logged_in:
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
# PAGE STYLE
# -----------------------

st.markdown("""
<style>
.home-wrap{
    max-width:900px;
    margin:auto;
}
.section{
    margin-top:2rem;
}
.big-card{
    background:#111;
    padding:1.5rem;
    border-radius:16px;
    box-shadow:0 0 20px rgba(0,0,0,.25);
}
.big-card h4{
    margin-bottom:0.3rem;
}
.card-btn{
    margin-top:0.7rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------

st.markdown(
    f"<div class='title-center'>👋 Welcome, {anonymous_id}</div>",
    unsafe_allow_html=True
)

st.markdown("<div class='home-wrap'>", unsafe_allow_html=True)

# ==================================================
# SEARCH
# ==================================================

st.markdown("<div class='section'><h3>🔍 Search News</h3></div>", unsafe_allow_html=True)

q = st.text_input("Search articles...")

if q:

    r = requests.get(f"{API}/search", params={"q": q})

    if r.status_code == 200:

        results = r.json()

        if not results:
            st.info("No results found")

        for a in results:

            if st.button(a["title"], key=f"s_{a['item_id']}"):

                # 🔒 LOG CLICK
                requests.post(
                    f"{API}/click",
                    json={
                        "impression_id": "search",
                        "item_id": a["item_id"],
                        "position": a["position"],
                        "anonymous_id": anonymous_id,
                        "open_type": "search"
                    }
                )

                st.session_state["open_item"] = a["item_id"]
                st.session_state["open_position"] = a["position"]
                st.session_state["open_impression"] = "search"

                st.switch_page("pages/9_Article.py")

# ==================================================
# BROWSE
# ==================================================

st.markdown("<div class='section'><h3>📂 Browse Articles</h3></div>", unsafe_allow_html=True)

if st.button("Browse By Category →", use_container_width=True):
    st.switch_page("pages/4_Recommendations.py")

# ==================================================
# DISCOVER
# ==================================================

st.markdown("<div class='section'><h3>✨ Discover</h3></div>", unsafe_allow_html=True)

st.markdown("""
<div class="big-card">
<h4>🔥 Trending Now</h4>
<p>Most clicked articles across platform</p>
</div>
""", unsafe_allow_html=True)

if st.button("Open Trending", use_container_width=True):
    st.switch_page("pages/8_Trending.py")

st.markdown("</div>", unsafe_allow_html=True)
