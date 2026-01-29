import sys
import os
import streamlit as st
import requests

with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("pages/1_Login.py")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
API = "http://127.0.0.1:8000"

# -----------------------
# Auth Guard
# -----------------------
if "user" not in st.session_state:
    st.switch_page("pages/1_Login.py")

# -----------------------
# Header
# -----------------------
st.markdown(
    f"<div class='title-center'>Welcome {st.session_state.user}</div>",
    unsafe_allow_html=True
)

# =====================================================
# 🔍 SEARCH BAR
# =====================================================

query = st.text_input("🔍 Search news")

if query:
    res = requests.get(f"{API}/search", params={"q": query})

    if res.status_code == 200:
        for r in res.json():
            if st.button(r["title"], key=f"search_{r['item_id']}"):
                st.session_state["open_item"] = r["item_id"]
                st.switch_page("pages/9_Article.py")

st.markdown("---")

# =====================================================
# 📂 Browse by Category
# =====================================================

st.markdown("### 📂 Browse by Category")

cats = ["Technology", "Sports", "Politics", "Business", "Health", "Entertainment"]

cols = st.columns(3)
for i, c in enumerate(cats):
    with cols[i % 3]:
        if st.button(c):
            st.session_state["selected_category"] = c
            st.switch_page("pages/4_Recommendations.py")

st.markdown("---")

# =====================================================
# 🎯 Personalized Feed
# =====================================================

if st.button("🎯 Personalized Feed"):
    st.session_state["selected_category"] = "All"
    st.switch_page("pages/4_Recommendations.py")

# =====================================================
# 🔥 TRENDING BUTTON
# =====================================================

if st.button("🔥 Trending Now"):
    st.switch_page("pages/8_Trending.py")
