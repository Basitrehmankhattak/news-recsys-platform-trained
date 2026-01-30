import streamlit as st

def load_css():
    st.markdown("""
    <style>

    /* =========================
       GLOBAL
    ========================= */

    html, body {
        background-color:#0b0f1a;
        color:#e5e7eb;
        font-family: "Inter", system-ui, sans-serif;
    }

    /* Remove Streamlit padding */
    .block-container {
        padding-top:2rem;
        padding-bottom:4rem;
        max-width:1100px;
    }

    /* =========================
       HEADINGS
    ========================= */

    .title-center{
        text-align:center;
        font-size:36px;
        font-weight:800;
        letter-spacing:-0.5px;
        margin-bottom:8px;
    }

    .sub{
        text-align:center;
        color:#9ca3af;
        margin-bottom:28px;
        font-size:15px;
    }

    h3{
        font-size:20px;
        margin-bottom:10px;
    }

    /* =========================
       CARDS
    ========================= */

    .card{
        background:linear-gradient(180deg,#161b2e,#121625);
        padding:16px;
        border-radius:14px;
        margin-bottom:14px;
        box-shadow:0 8px 30px rgba(0,0,0,0.35);
        transition:0.2s;
    }

    .card:hover{
        transform:translateY(-2px);
        box-shadow:0 12px 35px rgba(0,0,0,0.5);
    }

    .big-card{
        background:linear-gradient(180deg,#1a2140,#131833);
        padding:26px;
        border-radius:18px;
        box-shadow:0 10px 35px rgba(0,0,0,0.45);
        margin-bottom:16px;
    }

    /* =========================
       BADGES / TAGS
    ========================= */

    .badge{
        display:inline-block;
        background:#1e293b;
        color:#93c5fd;
        padding:4px 10px;
        border-radius:999px;
        font-size:12px;
        margin-right:6px;
    }

    .tag{
        background:#0f172a;
        color:#60a5fa;
        padding:4px 8px;
        border-radius:8px;
        font-size:12px;
    }

    /* =========================
       BUTTONS
    ========================= */

    .stButton button{
        width:100%;
        background:linear-gradient(90deg,#2563eb,#3b82f6);
        color:white;
        border-radius:12px;
        padding:0.6rem 1rem;
        font-weight:600;
        border:none;
        transition:0.15s;
    }

    .stButton button:hover{
        background:linear-gradient(90deg,#1d4ed8,#2563eb);
        transform:scale(1.01);
    }

    .stButton button:active{
        transform:scale(0.98);
    }

    /* =========================
       INPUTS
    ========================= */

    .stTextInput input{
        background:#0f172a;
        border:1px solid #1f2937;
        border-radius:12px;
        padding:10px;
        color:white;
    }

    .stTextInput input:focus{
        border-color:#3b82f6;
        box-shadow:0 0 0 1px #3b82f6;
    }

    /* =========================
       SELECT BOX
    ========================= */

    .stSelectbox div{
        border-radius:12px;
    }

    /* =========================
       METRICS
    ========================= */

    [data-testid="stMetric"]{
        background:#111827;
        padding:18px;
        border-radius:14px;
        box-shadow:0 6px 20px rgba(0,0,0,0.4);
    }

    /* =========================
       IMAGES
    ========================= */

    img{
        border-radius:12px;
    }

    /* =========================
       DIVIDER
    ========================= */

    hr{
        border:0;
        height:1px;
        background:linear-gradient(90deg,transparent,#334155,transparent);
        margin:24px 0;
    }

    /* =========================
       LINKS
    ========================= */

    a{
        color:#60a5fa;
        text-decoration:none;
    }

    a:hover{
        text-decoration:underline;
    }

    /* =========================
       SCROLLBAR
    ========================= */

    ::-webkit-scrollbar {
        width:8px;
    }

    ::-webkit-scrollbar-thumb {
        background:#334155;
        border-radius:10px;
    }

    </style>
    """, unsafe_allow_html=True)
