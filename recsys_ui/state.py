import os
import uuid
import streamlit as st

def ensure_state():
    st.session_state.setdefault("demo", {})
    d = st.session_state["demo"]

    d.setdefault("anonymous_id", f"anon_{uuid.uuid4().hex[:6]}")
    d.setdefault("session_id", str(uuid.uuid4()))

    d.setdefault("device_type", "web")
    d.setdefault("app_version", "v1")
    d.setdefault("user_agent", "streamlit-ui")
    d.setdefault("referrer", "ui_demo")

    d.setdefault("page_size", int(os.getenv("DEFAULT_PAGE_SIZE", "10")))
    d.setdefault("surface", os.getenv("DEFAULT_SURFACE", "home"))
    d.setdefault("locale", os.getenv("DEFAULT_LOCALE", "en-US"))

    # click extras
    d.setdefault("dwell_ms", 0)
    d.setdefault("open_type", "feed")

def new_session():
    st.session_state["demo"]["session_id"] = str(uuid.uuid4())
    st.session_state.pop("last_rec", None)

def normalize_items(rec_json: dict):
    # Your backend returns `items`
    return rec_json.get("items", [])

def get_impression_id(rec_json: dict) -> str:
    return str(rec_json.get("impression_id", "unknown"))
