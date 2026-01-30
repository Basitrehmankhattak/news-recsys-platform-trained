import sys
import os
import streamlit as st
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import load_css

load_css()

# ---------------------------
# AUTH GUARD
# ---------------------------

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/1_Login.py")
    st.stop()

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Model Evaluation",
    layout="centered"
)

# ---------------------------
# STYLE
# ---------------------------

st.markdown("""
<style>
.page-wrap{
    max-width:900px;
    margin:auto;
}
.metric-card{
    background:#111111;
    padding:1.5rem;
    border-radius:14px;
    text-align:center;
    box-shadow:0 0 20px rgba(0,0,0,0.25);
}
.section{
    margin-top:2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-center'>📈 Ranking Model Evaluation</div>", unsafe_allow_html=True)
st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)

# ---------------------------
# NAV
# ---------------------------

if st.button("🏠 Back to Home"):
    st.switch_page("pages/3_Home.py")

# ---------------------------
# PATHS
# ---------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "data/models/rankers/ranker_lgbm_v2_metrics.json"

# ---------------------------
# LOAD METRICS
# ---------------------------

if not METRICS_PATH.exists():
    st.error("Metrics file not found. Train model first.")
    st.stop()

with open(METRICS_PATH) as f:
    metrics = json.load(f)

def safe(key, default=0):
    return metrics.get(key, default)

# ---------------------------
# CORE METRICS
# ---------------------------

st.markdown("<div class='section'><h3>📊 Core Ranking Metrics</h3></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <h4>AUC</h4>
        <h2>{round(safe("auc_val"),3)}</h2>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>NDCG@10</h4>
        <h2>{round(safe("ndcg10_val"),3)}</h2>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>MRR@10</h4>
        <h2>{round(safe("mrr10_val"),3)}</h2>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# DATASET STATS
# ---------------------------

st.markdown("<div class='section'><h3>📦 Dataset Statistics</h3></div>", unsafe_allow_html=True)

stats = [
    ("Train Rows", safe("rows_train")),
    ("Val Rows", safe("rows_val")),
    ("Train Clicks", safe("clicks_train")),
    ("Val Clicks", safe("clicks_val")),
]

cols = st.columns(4)

for col, (name, val) in zip(cols, stats):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{name}</h4>
            <h2>{val}</h2>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------
# VISUALIZATION
# ---------------------------

st.markdown("<div class='section'><h3>📉 Metric Comparison</h3></div>", unsafe_allow_html=True)

df = pd.DataFrame({
    "Metric": ["AUC","NDCG@10","MRR@10"],
    "Score": [
        safe("auc_val"),
        safe("ndcg10_val"),
        safe("mrr10_val")
    ]
})

fig, ax = plt.subplots()
ax.bar(df["Metric"], df["Score"])
ax.set_ylim(0,1)
ax.set_ylabel("Score")
ax.set_title("Ranking Quality")

st.pyplot(fig)

# ---------------------------
# FEATURES
# ---------------------------

st.markdown("<div class='section'><h3>🧠 Features Used</h3></div>", unsafe_allow_html=True)
st.write(safe("features", []))

# ---------------------------
# DATASET PATH
# ---------------------------

st.markdown("<div class='section'><h3>📁 Training Dataset</h3></div>", unsafe_allow_html=True)
st.code(safe("data_path","N/A"))

# ---------------------------
# INTERPRETATION
# ---------------------------

st.markdown("<div class='section'><h3>📝 Interpretation</h3></div>", unsafe_allow_html=True)

st.info("""
• AUC > 0.6 → model separates clicked vs non-clicked well  
• NDCG@10 → quality of top-10 ranking  
• MRR@10 → how early first relevant article appears  

Metrics will improve automatically as more user clicks are collected.
""")

st.markdown("</div>", unsafe_allow_html=True)
