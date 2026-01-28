import sys
import os
import streamlit as st
import requests
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import load_css

load_css()
API="http://127.0.0.1:8000"

st.markdown("<div class='title-center'>📊 Admin Analytics</div>",
            unsafe_allow_html=True)

r=requests.get(f"{API}/admin/stats")

if r.status_code!=200:
    st.error("Failed to load")
    st.stop()

stats=r.json()

c1,c2,c3=st.columns(3)
c1.metric("Impressions",stats["impressions"])
c2.metric("Clicks",stats["clicks"])
c3.metric("CTR %",round(stats["ctr"],2))

df=pd.DataFrame({
 "Metric":["Impressions","Clicks"],
 "Count":[stats["impressions"],stats["clicks"]]
})

st.bar_chart(df.set_index("Metric"))
