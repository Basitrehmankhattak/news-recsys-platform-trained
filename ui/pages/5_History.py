import streamlit as st

st.title("📜 Click History")

history = [
    "News Article 3",
    "News Article 7",
    "News Article 10"
]

for h in history:
    st.write("•", h)
