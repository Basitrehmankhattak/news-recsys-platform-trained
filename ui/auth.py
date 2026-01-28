import streamlit as st

def login(username: str):
    st.session_state["user"] = username

def logout():
    st.session_state.pop("user", None)

def is_logged_in() -> bool:
    return "user" in st.session_state
