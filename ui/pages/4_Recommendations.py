import streamlit as st
import requests

st.title("🎯 Recommended News")

if "user" not in st.session_state:
    st.warning("Please login first")
    st.stop()

payload = {
    "user_id": st.session_state["user"],
    "session_id": st.session_state["session_id"],
    "surface": "home",
    "page_size": 5,
    "locale": "en-US"
}

res = requests.post(
    "http://127.0.0.1:8000/recommendations",
    json=payload
)

if res.status_code == 200:
    items = res.json()["items"]

    for i, item in enumerate(items, 1):
        st.subheader(f"{i}. {item['title']}")
        if st.button(f"Click {i}"):
            requests.post(
                "http://127.0.0.1:8000/clicks",
                json={
                    "impression_id": item["impression_id"],
                    "item_id": item["item_id"],
                    "position": i
                }
            )
else:
    st.error("Backend error")
