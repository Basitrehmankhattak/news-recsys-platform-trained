import streamlit as st
import pandas as pd
from ui_db import fetch_all, fetch_one

st.set_page_config(page_title="Metrics", layout="wide")
st.title("Metrics & Analytics")

# -----------------------------
# Time window filter
# -----------------------------
st.sidebar.header("Time window")

window = st.sidebar.selectbox(
    "Select window",
    ["Last 1 hour", "Last 24 hours", "Last 7 days", "All time"],
    index=1,
)

# Build WHERE clause for served_at / clicked_at
time_filter_sql = ""
params = []

if window == "Last 1 hour":
    time_filter_sql = "WHERE served_at >= NOW() - INTERVAL '1 hour'"
elif window == "Last 24 hours":
    time_filter_sql = "WHERE served_at >= NOW() - INTERVAL '24 hours'"
elif window == "Last 7 days":
    time_filter_sql = "WHERE served_at >= NOW() - INTERVAL '7 days'"
else:
    time_filter_sql = ""
    params = []

# For clicks we need clicked_at filter
click_time_filter_sql = ""
if window == "Last 1 hour":
    click_time_filter_sql = "WHERE clicked_at >= NOW() - INTERVAL '1 hour'"
elif window == "Last 24 hours":
    click_time_filter_sql = "WHERE clicked_at >= NOW() - INTERVAL '24 hours'"
elif window == "Last 7 days":
    click_time_filter_sql = "WHERE clicked_at >= NOW() - INTERVAL '7 days'"
else:
    click_time_filter_sql = ""

st.sidebar.divider()
min_impressions = st.sidebar.number_input(
    "Min impressions (for CTR leaderboard)",
    min_value=1,
    value=20,
    step=1,
)

# -----------------------------
# KPI Row
# -----------------------------
# Sessions (no ended_at requirement; just count sessions table)
sessions_row = fetch_one("SELECT COUNT(*)::bigint AS n FROM sessions;")
total_sessions = int(sessions_row["n"]) if sessions_row else 0

# Impressions in window
imp_row = fetch_one(
    f"SELECT COUNT(*)::bigint AS n FROM impressions_served {time_filter_sql};"
)
total_impressions = int(imp_row["n"]) if imp_row else 0

# Clicks in window
clk_row = fetch_one(
    f"SELECT COUNT(*)::bigint AS n FROM clicks {click_time_filter_sql};"
)
total_clicks = int(clk_row["n"]) if clk_row else 0

ctr = (total_clicks / total_impressions) if total_impressions else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sessions (all time)", f"{total_sessions:,}")
c2.metric(f"Impressions ({window})", f"{total_impressions:,}")
c3.metric(f"Clicks ({window})", f"{total_clicks:,}")
c4.metric(f"CTR ({window})", f"{ctr:.3%}")

st.divider()

# -----------------------------
# Time series charts
# -----------------------------
st.subheader("Time series")

# Choose bucket size
bucket = st.selectbox("Bucket", ["hour", "day"], index=0)

# Impressions series
impressions_series = fetch_all(
    f"""
    SELECT date_trunc(%s, served_at) AS t, COUNT(*)::bigint AS impressions
    FROM impressions_served
    {time_filter_sql}
    GROUP BY 1
    ORDER BY 1;
    """,
    (bucket,) if time_filter_sql else (bucket,),
)

# Clicks series
clicks_series = fetch_all(
    f"""
    SELECT date_trunc(%s, clicked_at) AS t, COUNT(*)::bigint AS clicks
    FROM clicks
    {click_time_filter_sql}
    GROUP BY 1
    ORDER BY 1;
    """,
    (bucket,),
)

df_imp = pd.DataFrame(impressions_series)
df_clk = pd.DataFrame(clicks_series)

if df_imp.empty and df_clk.empty:
    st.info("No time series data in the selected window yet.")
else:
    # Merge time axes
    if df_imp.empty:
        df_imp = pd.DataFrame({"t": df_clk["t"], "impressions": 0})
    if df_clk.empty:
        df_clk = pd.DataFrame({"t": df_imp["t"], "clicks": 0})

    df = pd.merge(df_imp, df_clk, on="t", how="outer").fillna(0).sort_values("t")
    df["ctr"] = df.apply(lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] else 0.0, axis=1)

    left, right = st.columns(2)
    with left:
        st.line_chart(df.set_index("t")[["impressions", "clicks"]])
    with right:
        st.line_chart(df.set_index("t")[["ctr"]])

st.divider()

# -----------------------------
# Top-K tables
# -----------------------------
st.subheader("Top items")

colA, colB = st.columns(2)

# Top shown items: impression_items joined through impressions_served time window
# (Filter by impressions_served window because impression_items doesn't carry served_at)
top_shown = fetch_all(
    f"""
    SELECT ii.item_id,
           MAX(it.title) AS title,
           COUNT(*)::bigint AS impressions
    FROM impression_items ii
    JOIN impressions_served imps ON imps.impression_id = ii.impression_id
    JOIN items it ON it.item_id = ii.item_id
    {time_filter_sql}
    GROUP BY ii.item_id
    ORDER BY impressions DESC
    LIMIT 20;
    """
)

# Top clicked items: clicks filtered directly by clicked_at window
top_clicked = fetch_all(
    f"""
    SELECT c.item_id,
           MAX(it.title) AS title,
           COUNT(*)::bigint AS clicks
    FROM clicks c
    JOIN items it ON it.item_id = c.item_id
    {click_time_filter_sql}
    GROUP BY c.item_id
    ORDER BY clicks DESC
    LIMIT 20;
    """
)

with colA:
    st.markdown("### Most shown items")
    if top_shown:
        st.dataframe(pd.DataFrame(top_shown), use_container_width=True, hide_index=True)
    else:
        st.info("No shown-item data yet for this window.")

with colB:
    st.markdown("### Most clicked items")
    if top_clicked:
        st.dataframe(pd.DataFrame(top_clicked), use_container_width=True, hide_index=True)
    else:
        st.info("No click data yet for this window.")

st.divider()

st.markdown("### Highest CTR items (with minimum impressions)")

# CTR leaderboard in the same window
ctr_rows = fetch_all(
    f"""
    WITH shown AS (
        SELECT ii.item_id, COUNT(*)::bigint AS impressions
        FROM impression_items ii
        JOIN impressions_served imps ON imps.impression_id = ii.impression_id
        {time_filter_sql}
        GROUP BY ii.item_id
    ),
    clicked AS (
        SELECT c.item_id, COUNT(*)::bigint AS clicks
        FROM clicks c
        {click_time_filter_sql}
        GROUP BY c.item_id
    )
    SELECT s.item_id,
           MAX(it.title) AS title,
           s.impressions,
           COALESCE(k.clicks, 0) AS clicks,
           (COALESCE(k.clicks, 0)::float / NULLIF(s.impressions, 0)) AS ctr
    FROM shown s
    JOIN items it ON it.item_id = s.item_id
    LEFT JOIN clicked k ON k.item_id = s.item_id
    WHERE s.impressions >= %s
    GROUP BY s.item_id, s.impressions, k.clicks
    ORDER BY ctr DESC
    LIMIT 20;
    """,
    (int(min_impressions),),
)

if ctr_rows:
    df_ctr = pd.DataFrame(ctr_rows)
    df_ctr["ctr"] = df_ctr["ctr"].astype(float)
    st.dataframe(df_ctr, use_container_width=True, hide_index=True)
else:
    st.info("Not enough data to compute CTR leaderboard for this window.")