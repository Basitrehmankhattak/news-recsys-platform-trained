import streamlit as st

# --------------------------------
# Login
# --------------------------------

def login(anonymous_id: str, session_id: str):
    st.session_state["logged_in"] = True
    st.session_state["anonymous_id"] = anonymous_id
    st.session_state["session_id"] = session_id

# --------------------------------
# Logout
# --------------------------------

def logout():
    keys = [
        "logged_in",
        "anonymous_id",
        "session_id",
        "open_item",
        "open_position",
        "open_impression"
    ]
    for k in keys:
        st.session_state.pop(k, None)

# --------------------------------
# Status
# --------------------------------

def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)
