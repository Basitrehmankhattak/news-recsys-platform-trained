import streamlit as st
import pandas as pd

st.title("📊 Admin Analytics")

df = pd.DataFrame({
    "Metric": ["Impressions", "Clicks", "CTR"],
    "Value": [1500, 320, 0.21]
})

st.bar_chart(df.set_index("Metric"))
