import streamlit as st
import requests
from auth import is_logged_in, logout

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="News Recommendation System", layout="wide")

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.title("📰 NewsRecSys")

    if is_logged_in():
        st.write(f"User: {st.session_state['user']}")

        if st.button("Logout"):
            logout()
            st.switch_page("pages/1_Login.py")

# ----------------------------
# Auth guard
# ----------------------------
if not is_logged_in():
    st.switch_page("pages/1_Login.py")

# ----------------------------
# Page
# ----------------------------
st.title("🏠 Home")

st.write(f"Session ID: {st.session_state.session_id}")

# ----------------------------
# Fetch Recommendations
# ----------------------------
payload = {
    "session_id": st.session_state.session_id,
    "user_id": None,
    "anonymous_id": st.session_state.session_id,
    "surface": "home",
    "page_size": 10,
    "locale": "en-US"
}

resp = requests.post(f"{API}/recommendations", json=payload)

if resp.status_code != 200:
    st.error("Backend error")
    st.stop()

data = resp.json()

st.session_state.impression_id = data["impression_id"]
recs = data["items"]

# ----------------------------
# Display + Click Tracking
# ----------------------------
st.subheader("Recommended for you")

for rec in recs:
    btn_label = f"{rec['position']}. {rec['title']}"

    if st.button(btn_label, key=f"click_{rec['item_id']}"):
        requests.post(
            "http://127.0.0.1:8000/click",
            json={
                "impression_id": st.session_state.impression_id,
                "item_id": rec["item_id"],
                "position": rec["position"],
                "dwell_ms": 0,
                "open_type": "ui"
            }
        )

        st.success(f"Clicked: {rec['item_id']}")
