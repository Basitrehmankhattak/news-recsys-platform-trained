import os
import pandas as pd
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from state import ensure_state
import streamlit as st

if not st.session_state.get("anonymous_id"):
    st.warning("Please login first from the **Account** page.")
    st.stop()


load_dotenv()
ensure_state()

st.title("Metrics")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL is not set in recsys_ui/.env")
    st.stop()

@st.cache_data(ttl=10)
def _run_query(sql: str, params=None):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()

# Controls
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    window_hours = st.number_input("Window (hours)", min_value=1, max_value=168, value=24, step=1)
with c2:
    limit_rows = st.number_input("Recent rows", min_value=10, max_value=200, value=50, step=10)
with c3:
    refresh = st.button("Refresh")

# Time window filter (works if your tables have created_at/ts columns)
# If your column names differ, tell me and I will adjust.
time_filter = f"NOW() - INTERVAL '{int(window_hours)} hours'"

# KPI: impressions
impressions_sql = f"""
SELECT
  COUNT(*) AS impressions
FROM impressions_served
WHERE served_at >= {time_filter}
"""

# KPI: clicks
clicks_sql = f"""
SELECT
  COUNT(*) AS clicks
FROM clicks
WHERE clicked_at >= {time_filter}
"""

# KPI: CTR
ctr_sql = f"""
WITH imp AS (
  SELECT COUNT(*)::float AS impressions
  FROM impressions_served
  WHERE served_at >= {time_filter}
),
clk AS (
  SELECT COUNT(*)::float AS clicks
  FROM clicks
  WHERE clicked_at >= {time_filter}
)
SELECT
  imp.impressions,
  clk.clicks,
  CASE WHEN imp.impressions = 0 THEN 0 ELSE (clk.clicks / imp.impressions) END AS ctr
FROM imp, clk
"""

# Dwell stats
dwell_sql = f"""
SELECT
  COUNT(*) AS click_events,
  AVG(dwell_ms)::float AS avg_dwell_ms,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dwell_ms) AS median_dwell_ms,
  MAX(dwell_ms) AS max_dwell_ms
FROM clicks
WHERE clicked_at >= {time_filter}
"""

# Recent impressions (last N)
recent_impressions_sql = f"""
SELECT
  impression_id,
  anonymous_id,
  session_id,
  surface,
  locale,
  served_at
FROM impressions_served
WHERE served_at >= {time_filter}
ORDER BY served_at DESC
LIMIT {int(limit_rows)}
"""

# Recent clicks (last N)
recent_clicks_sql = f"""
SELECT
  c.impression_id,
  c.item_id,
  c.position,
  c.dwell_ms,
  c.open_type,
  c.clicked_at
FROM clicks c
WHERE c.clicked_at >= {time_filter}
ORDER BY c.clicked_at DESC
LIMIT {int(limit_rows)}
"""

# Run queries
try:
    ctr_row = _run_query(ctr_sql)[0]
    dwell_row = _run_query(dwell_sql)[0]
    imp_count = int(ctr_row["impressions"])
    clk_count = int(ctr_row["clicks"])
    ctr_val = float(ctr_row["ctr"])
except Exception as e:
    st.error(
        "Metrics queries failed. Most likely your timestamp column names differ.\n"
        f"Error: {e}"
    )
    st.stop()

# KPIs display
k1, k2, k3, k4 = st.columns(4)
k1.metric("Impressions", f"{imp_count}")
k2.metric("Clicks", f"{clk_count}")
k3.metric("CTR", f"{ctr_val*100:.2f}%")
k4.metric("Avg dwell", f"{(float(dwell_row['avg_dwell_ms'] or 0)/1000):.2f}s")

st.divider()

# Tables
st.subheader("Recent impressions")
try:
    imp_rows = _run_query(recent_impressions_sql)
    if imp_rows:
        st.dataframe(pd.DataFrame(imp_rows), use_container_width=True)
    else:
        st.info("No impressions in this time window.")
except Exception as e:
    st.warning(f"Could not load recent impressions: {e}")

st.subheader("Recent clicks")
try:
    clk_rows = _run_query(recent_clicks_sql)
    if clk_rows:
        st.dataframe(pd.DataFrame(clk_rows), use_container_width=True)
    else:
        st.info("No clicks in this time window.")
except Exception as e:
    st.warning(f"Could not load recent clicks: {e}")

st.divider()

# Optional: top clicked items
st.subheader("Top clicked items (window)")
top_clicked_sql = f"""
SELECT
  item_id,
  COUNT(*) AS clicks
FROM clicks
WHERE clicked_at >= {time_filter}
GROUP BY item_id
ORDER BY clicks DESC
LIMIT 10
"""
try:
    top_rows = _run_query(top_clicked_sql)
    if top_rows:
        st.dataframe(pd.DataFrame(top_rows), use_container_width=True)
    else:
        st.info("No top-click data yet.")
except Exception as e:
    st.warning(f"Could not load top clicked items: {e}")
