import uuid
import time
import streamlit as st

def ensure_state():
    if "anonymous_id" not in st.session_state:
        st.session_state.anonymous_id = f"anon_{uuid.uuid4().hex[:10]}"

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "dev_mode" not in st.session_state:
        st.session_state.dev_mode = False

    if "user_status" not in st.session_state:
        st.session_state.user_status = "unknown"

    if "last_impression_id" not in st.session_state:
        st.session_state.last_impression_id = None

    if "last_recs" not in st.session_state:
        st.session_state.last_recs = []

    if "dwell_start" not in st.session_state:
        st.session_state.dwell_start = {}

def start_dwell(item_id: str):
    st.session_state.dwell_start[item_id] = time.time()

def get_dwell_ms(item_id: str) -> int:
    start = st.session_state.dwell_start.get(item_id)
    if not start:
        return 0
    return int(max(0.0, (time.time() - start) * 1000))
