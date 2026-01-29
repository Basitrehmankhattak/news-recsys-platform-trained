import streamlit as st

def load_css():
    st.markdown("""
    <style>

    body {
        background-color:#0e1117;
        color:white;
    }

    .title-center{
        text-align:center;
        font-size:34px;
        font-weight:700;
        margin-bottom:10px;
    }

    .sub{
        text-align:center;
        color:#9aa0a6;
        margin-bottom:25px;
    }

    .card{
        background:#1f2933;
        padding:14px;
        border-radius:12px;
        margin-bottom:12px;
        box-shadow:0 0 6px rgba(0,0,0,0.4);
    }

    button[kind="secondary"]{
        width:100%;
        background:#2563eb;
        color:white;
        border-radius:8px;
        padding:8px;
    }

    button:hover{
        background:#1d4ed8;
        color:white;
    }

    .stTextInput input{
        border-radius:8px;
    }

    .stButton button{
        width:100%;
        border-radius:10px;
        font-weight:600;
    }

    </style>
    """, unsafe_allow_html=True)
