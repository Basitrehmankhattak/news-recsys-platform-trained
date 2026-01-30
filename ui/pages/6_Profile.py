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
anonymous_id = st.session_state["anonymous_id"]

# -----------------------
# FETCH PROFILE
# -----------------------

with st.spinner("Loading profile..."):
    res = requests.get(f"{API}/profile/{anonymous_id}")

if res.status_code != 200:
    st.error("Failed to load profile")
    st.stop()

p = res.json()

# -----------------------
# FORMAT
# -----------------------

created = p["created_at"][:19] if p["created_at"] else "N/A"
last_login = p["last_login"][:19] if p["last_login"] else "First Login"

icon = "🔥" if p["status"] == "Warm User" else "🧊"

# -----------------------
# HEADER
# -----------------------

st.markdown("<div class='title-center'>👤 Profile</div>", unsafe_allow_html=True)

# -----------------------
# CARD
# -----------------------

st.markdown(f"""
<div class="card">

### {icon} {anonymous_id}

**Badge:** {p["badge"]}  
**User Type:** {p["status"]}  
**Total Clicks:** {p["total_clicks"]}  

---

📅 **Account Created:** {created}  
🕒 **Last Login:** {last_login}

</div>
""", unsafe_allow_html=True)

# -----------------------
# MESSAGE
# -----------------------

if p["status"] == "Cold User":
    st.info("Start clicking articles to personalize your feed.")
else:
    st.success("Your feed is actively personalized based on your activity.")

# -----------------------
# NAV
# -----------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/3_Home.py")

with col2:
    if st.button("📜 History", use_container_width=True):
        st.switch_page("pages/7_History.py")
