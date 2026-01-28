import streamlit as st

def load_css():
    st.markdown("""
        <style>

        /* Main background */
        .stApp {
            background-color: #0e1117;
        }

        /* Headings */
        h1, h2, h3 {
            color: #ffffff;
        }

        /* Input boxes */
        input {
            background-color: #1f2933 !important;
            color: white !important;
            border-radius: 8px !important;
        }

        /* Buttons */
        button {
            background-color: #4f46e5 !important;
            color: white !important;
            border-radius: 8px !important;
            height: 45px;
            width: 100%;
            font-size: 16px;
        }

        button:hover {
            background-color: #6366f1 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #111827;
        }

        /* Cards */
        .card {
            background-color: #1f2933;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
        }

        </style>
    """, unsafe_allow_html=True)
