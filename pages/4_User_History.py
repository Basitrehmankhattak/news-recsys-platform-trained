import streamlit as st
import pandas as pd
from ui_db import fetch_all, fetch_one

st.set_page_config(page_title="User History", layout="wide")
st.title("User History / Debugger")

# -----------------------------
# Identify user (from Login page)
# -----------------------------
active_user = st.session_state.get("anonymous_id")

st.sidebar.header("User selection")

# Allow manual input + default to active logged-in user
anonymous_id = st.sidebar.text_input(
    "anonymous_id",
    value=active_user or "",
    help="This should match the anonymous_id you used in the Login page (e.g., Mohsin).",
).strip()

if not anonymous_id:
    st.warning("Please enter an anonymous_id in the sidebar (or login first).")
    st.stop()

# -----------------------------
# Time window
# -----------------------------
window = st.sidebar.selectbox(
    "Time window",
    ["Last 1 hour", "Last 24 hours", "Last 7 days", "All time"],
    index=1,
)

def time_clause(col: str) -> str:
    if window == "Last 1 hour":
        return f"{col} >= NOW() - INTERVAL '1 hour'"
    if window == "Last 24 hours":
        return f"{col} >= NOW() - INTERVAL '24 hours'"
    if window == "Last 7 days":
        return f"{col} >= NOW() - INTERVAL '7 days'"
    return "TRUE"

# We'll assume these timestamp columns exist (typical in your schema):
# sessions.started_at, impressions_served.served_at, clicks.clicked_at
sess_time_filter = time_clause("started_at")
imp_time_filter = time_clause("served_at")
clk_time_filter = time_clause("clicked_at")

st.sidebar.divider()
max_rows = st.sidebar.selectbox("Rows to display", [20, 50, 100, 200], index=1)

# -----------------------------
# KPI summary for this user
# -----------------------------
try:
    sess_row = fetch_one(
        f"""
        SELECT COUNT(*)::bigint AS n
        FROM sessions
        WHERE anonymous_id = %s AND {sess_time_filter};
        """,
        (anonymous_id,),
    )
    imp_row = fetch_one(
        f"""
        SELECT COUNT(*)::bigint AS n
        FROM impressions_served
        WHERE anonymous_id = %s AND {imp_time_filter};
        """,
        (anonymous_id,),
    )
    clk_row = fetch_one(
        f"""
        SELECT COUNT(*)::bigint AS n
        FROM clicks c
        JOIN impressions_served imps ON imps.impression_id = c.impression_id
        WHERE imps.anonymous_id = %s AND {clk_time_filter};
        """,
        (anonymous_id,),
    )

    sessions_n = int(sess_row["n"]) if sess_row else 0
    impressions_n = int(imp_row["n"]) if imp_row else 0
    clicks_n = int(clk_row["n"]) if clk_row else 0
    ctr = (clicks_n / impressions_n) if impressions_n else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Sessions ({window})", f"{sessions_n:,}")
    c2.metric(f"Impressions ({window})", f"{impressions_n:,}")
    c3.metric(f"Clicks ({window})", f"{clicks_n:,}")
    c4.metric(f"CTR ({window})", f"{ctr:.3%}")
except Exception as e:
    st.error(
        f"DB query failed. This usually means timestamp column names differ in your schema.\n\nError: {e}"
    )
    st.stop()

st.divider()

tabs = st.tabs(["Sessions", "Impressions", "Clicks", "Impression Drilldown"])

# -----------------------------
# Tab 1: Sessions
# -----------------------------
with tabs[0]:
    st.subheader("Sessions")

    try:
        sessions = fetch_all(
            f"""
            SELECT session_id, started_at, ended_at, device_type, app_version, user_agent, referrer
            FROM sessions
            WHERE anonymous_id = %s AND {sess_time_filter}
            ORDER BY started_at DESC
            LIMIT %s;
            """,
            (anonymous_id, max_rows),
        )
        if not sessions:
            st.info("No sessions found for this user in this window.")
        else:
            st.dataframe(pd.DataFrame(sessions), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Failed to load sessions: {e}")

# -----------------------------
# Tab 2: Impressions (served)
# -----------------------------
with tabs[1]:
    st.subheader("Impressions (served)")

    try:
        impressions = fetch_all(
            f"""
            SELECT impression_id, session_id, served_at, surface, page_size, locale
            FROM impressions_served
            WHERE anonymous_id = %s AND {imp_time_filter}
            ORDER BY served_at DESC
            LIMIT %s;
            """,
            (anonymous_id, max_rows),
        )

        if not impressions:
            st.info("No impressions found for this user in this window.")
            st.stop()

        df_imp = pd.DataFrame(impressions)

        # Add counts: items shown + clicks per impression
        imp_ids = df_imp["impression_id"].tolist()

        shown_counts = fetch_all(
            """
            SELECT impression_id, COUNT(*)::bigint AS shown
            FROM impression_items
            WHERE impression_id = ANY(%s)
            GROUP BY impression_id;
            """,
            (imp_ids,),
        )
        shown_map = {r["impression_id"]: int(r["shown"]) for r in shown_counts}

        click_counts = fetch_all(
            """
            SELECT impression_id, COUNT(*)::bigint AS clicks
            FROM clicks
            WHERE impression_id = ANY(%s)
            GROUP BY impression_id;
            """,
            (imp_ids,),
        )
        click_map = {r["impression_id"]: int(r["clicks"]) for r in click_counts}

        df_imp["shown_items"] = df_imp["impression_id"].map(lambda x: shown_map.get(x, 0))
        df_imp["clicks"] = df_imp["impression_id"].map(lambda x: click_map.get(x, 0))

        st.dataframe(
            df_imp,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as e:
        st.error(f"Failed to load impressions: {e}")

# -----------------------------
# Tab 3: Clicks
# -----------------------------
with tabs[2]:
    st.subheader("Clicks")

    try:
        clicks = fetch_all(
            f"""
            SELECT c.click_id, c.impression_id, c.item_id, it.title, c.position, c.clicked_at, c.dwell_ms, c.open_type
            FROM clicks c
            JOIN impressions_served imps ON imps.impression_id = c.impression_id
            LEFT JOIN items it ON it.item_id = c.item_id
            WHERE imps.anonymous_id = %s AND {clk_time_filter}
            ORDER BY c.clicked_at DESC
            LIMIT %s;
            """,
            (anonymous_id, max_rows),
        )

        if not clicks:
            st.info("No clicks found for this user in this window.")
        else:
            st.dataframe(pd.DataFrame(clicks), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Failed to load clicks: {e}")

# -----------------------------
# Tab 4: Impression Drilldown (items shown + clicked)
# -----------------------------
with tabs[3]:
    st.subheader("Impression Drilldown")
    st.caption("Pick an impression_id to see the ranked list and click labels (industry-style debugging).")

    try:
        recent_imp_ids = fetch_all(
            f"""
            SELECT impression_id
            FROM impressions_served
            WHERE anonymous_id = %s AND {imp_time_filter}
            ORDER BY served_at DESC
            LIMIT 200;
            """,
            (anonymous_id,),
        )
        imp_choices = [r["impression_id"] for r in recent_imp_ids]

        if not imp_choices:
            st.info("No impressions available to drill down.")
            st.stop()

        selected_imp = st.selectbox("impression_id", imp_choices)

        # Query shown items + whether clicked
        rows = fetch_all(
            """
            SELECT
              ii.position,
              ii.item_id,
              it.title,
              ii.retrieval_score,
              ii.rank_score,
              ii.final_score,
              (c.click_id IS NOT NULL) AS clicked,
              c.clicked_at,
              c.dwell_ms
            FROM impression_items ii
            LEFT JOIN items it ON it.item_id = ii.item_id
            LEFT JOIN clicks c
              ON c.impression_id = ii.impression_id AND c.item_id = ii.item_id
            WHERE ii.impression_id = %s
            ORDER BY ii.position ASC;
            """,
            (selected_imp,),
        )

        if not rows:
            st.warning("No impression_items found for this impression_id.")
            st.stop()

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Failed to drill down impression: {e}")