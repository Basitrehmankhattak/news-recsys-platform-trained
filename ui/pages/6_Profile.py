import streamlit as st

st.title("👤 Profile")

if "user" not in st.session_state:
    st.warning("Please login first")
    st.switch_page("pages/1_Login.py")

st.write("Username:", st.session_state["user"])
st.write("User Type: Warm")
st.write("Language: EN")
