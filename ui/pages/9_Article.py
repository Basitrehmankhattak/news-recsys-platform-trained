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
load_css()

API = "http://127.0.0.1:8000"

# -----------------------
# PAGE STYLE
# -----------------------

st.markdown("""
<style>
.page-wrap{
    max-width:900px;
    margin:auto;
}
.article-card{
    background:#111111;
    padding:2rem;
    border-radius:16px;
    box-shadow:0 0 25px rgba(0,0,0,0.25);
}
.article-title{
    font-size:28px;
    font-weight:700;
}
.meta{
    opacity:0.7;
    margin-top:0.3rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# CONTEXT
# -----------------------

item_id = st.session_state.get("open_item")

if not item_id:
    st.warning("Select an article first")
    st.stop()

# -----------------------
# FETCH ARTICLE (READ ONLY)
# -----------------------

try:
    r = requests.get(f"{API}/articles/{item_id}", timeout=5)
except Exception:
    st.error("Backend not reachable")
    st.stop()

if r.status_code != 200:
    st.error("Failed loading article")
    st.stop()

a = r.json()

# -----------------------
# HEADER
# -----------------------

h1, h2 = st.columns([6,1])

with h1:
    st.markdown("<div class='title-center'>📰 Article</div>", unsafe_allow_html=True)

with h2:
    if st.button("⬅ Back"):
        st.switch_page("pages/3_Home.py")

# -----------------------
# ARTICLE CARD
# -----------------------

st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)

st.image(
    "https://via.placeholder.com/900x350?text=News+Article",
    use_container_width=True
)

st.markdown(f"""
<div class="article-card">
    <div class="article-title">{a['title']}</div>
    <div class="meta">Category: {a['category']}</div>
    <hr>
    <p>{a['abstract']}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
