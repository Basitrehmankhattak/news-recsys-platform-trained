import streamlit as st

st.set_page_config(layout="centered")
st.title("🆕 Register")

st.text_input("Username")
st.text_input("Password", type="password")

if st.button("Create Account"):
    st.success("Account created (demo mode)")
