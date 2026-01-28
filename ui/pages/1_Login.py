import streamlit as st
import requests

st.title("🔐 Login")

username = st.text_input("Username")
login_btn = st.button("Login")

if login_btn:
    if not username.strip():
        st.error("Enter username")
        st.stop()

    payload = {
        "anonymous_id": username,
        "device_type": "web",
        "app_version": "streamlit",
        "user_agent": "streamlit_ui",
        "referrer": "direct"
    }

    try:
        res = requests.post(
            "http://127.0.0.1:8000/session/start",
            json=payload,
            timeout=5
        )

        if res.status_code != 200:
            st.error(f"Backend error {res.status_code}")
            st.code(res.text)
            st.stop()

        data = res.json()
        st.session_state["user"] = username
        st.session_state["session_id"] = data["session_id"]

        st.success("Login successful")
        st.switch_page("pages/3_Home.py")


    except Exception as e:
        st.error("Backend not reachable")
        st.exception(e)
