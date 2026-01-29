import streamlit as st
import json
from pathlib import Path

# ---------------------------
# Page Config
# ---------------------------

st.set_page_config(page_title="Model Evaluation", layout="centered")

st.markdown(
    "<h2 style='text-align:center'>📈 Ranking Model Evaluation</h2>",
    unsafe_allow_html=True
)

# ---------------------------
# Resolve Project Root
# ---------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "data" / "models" / "rankers" / "ranker_lgbm_v2_metrics.json"

# ---------------------------
# Load Metrics
# ---------------------------

if not METRICS_PATH.exists():
    st.error("Metrics file not found. Train model first.")
    st.stop()

with open(METRICS_PATH) as f:
    metrics = json.load(f)

# ---------------------------
# KPI Cards
# ---------------------------

c1, c2, c3 = st.columns(3)
c1.metric("AUC", round(metrics["auc_val"], 3))
c2.metric("NDCG@10", round(metrics["ndcg10_val"], 3))
c3.metric("MRR@10", round(metrics["mrr10_val"], 3))

st.divider()

c4, c5 = st.columns(2)
c4.metric("Train Rows", metrics["rows_train"])
c5.metric("Validation Rows", metrics["rows_val"])

c6, c7 = st.columns(2)
c6.metric("Train Clicks", metrics["clicks_train"])
c7.metric("Validation Clicks", metrics["clicks_val"])

st.divider()

# ---------------------------
# Extra Info
# ---------------------------

st.subheader("Features Used")
st.write(metrics["features"])

st.subheader("Dataset")
st.code(metrics["data_path"])

# ---------------------------
# Interpretation
# ---------------------------

st.info("""
AUC > 0.6  → decent early model  
NDCG@10 → ranking quality  
MRR@10 → first-click position  

Metrics improve automatically as more clicks arrive.
""")
