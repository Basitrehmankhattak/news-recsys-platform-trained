import streamlit as st
import pandas as pd
from ui_db import fetch_all, fetch_one

st.set_page_config(page_title="Content Catalog", layout="wide")
st.title("Content Catalog")

# ---------------------------
# Detect if REAL items exist (MIND items typically start with 'N')
# IMPORTANT: do NOT use 'N%' literally in SQL with psycopg -> pass as param
# ---------------------------
has_real_row = fetch_one(
    "SELECT EXISTS (SELECT 1 FROM items WHERE item_id LIKE %s) AS has_real;",
    ("N%",),
)
has_real_items = bool(has_real_row["has_real"]) if has_real_row else False

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("Filters")

include_demo = st.sidebar.checkbox(
    "Include DEMO items",
    value=not has_real_items,  # default: hide demo if real items exist
)

if has_real_items and not include_demo:
    st.sidebar.success("Showing REAL items only (N%).")
elif has_real_items and include_demo:
    st.sidebar.warning("Including DEMO items in catalog view.")
else:
    st.sidebar.info("No real items detected yet; showing DEMO items.")

search = st.sidebar.text_input("Search title (ILIKE)", value="")
page_size = st.sidebar.selectbox("Page size", [10, 20, 50, 100], index=1)

sort_mode = st.sidebar.selectbox(
    "Sort by",
    ["Newest (ingested_at desc)", "Title (A→Z)"],
    index=0,
)

show_engagement = st.sidebar.checkbox(
    "Show engagement stats (impressions/clicks)", value=False
)

st.sidebar.divider()
st.sidebar.caption("Tip: engagement stats are optional because they can be expensive on large data.")

# ---------------------------
# Base scope filter for dropdowns (ONLY real-items scope)
# ---------------------------
scope_where_sql = ""
scope_params = []
if has_real_items and not include_demo:
    scope_where_sql = "WHERE item_id LIKE %s"
    scope_params = ["N%"]

# Load categories for dropdown (scoped)
categories = fetch_all(
    f"""
    SELECT DISTINCT COALESCE(category, '(null)') AS category
    FROM items
    {scope_where_sql}
    ORDER BY 1;
    """,
    tuple(scope_params),
)
category_options = ["(all)"] + [r["category"] for r in categories]
selected_category = st.sidebar.selectbox("Category", category_options, index=0)

# ---------------------------
# Build WHERE clause for main query (scope + filters)
# ---------------------------
where_clauses = []
params = []

# Apply scope: if real items exist and demo is not included, show only N%
if has_real_items and not include_demo:
    where_clauses.append("item_id LIKE %s")
    params.append("N%")

# Search filter
if search.strip():
    where_clauses.append("title ILIKE %s")
    params.append(f"%{search.strip()}%")

# Category filter
if selected_category != "(all)":
    if selected_category == "(null)":
        where_clauses.append("category IS NULL")
    else:
        where_clauses.append("category = %s")
        params.append(selected_category)

where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

# ---------------------------
# Summary KPIs
# ---------------------------
count_row = fetch_one(f"SELECT COUNT(*) AS n FROM items {where_sql};", tuple(params))
total_items = int(count_row["n"]) if count_row else 0

last_ingest = fetch_one("SELECT MAX(ingested_at) AS last_ingested_at FROM items;")

k1, k2 = st.columns(2)
k1.metric("Items (filtered)", f"{total_items:,}")
k2.metric("Last ingested_at", str(last_ingest["last_ingested_at"]) if last_ingest else "N/A")

st.divider()

if total_items == 0:
    st.warning("No items match the current filters.")
    st.stop()

# ---------------------------
# Pagination
# ---------------------------
total_pages = max(1, (total_items + page_size - 1) // page_size)
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
offset = (page - 1) * page_size

order_sql = "ingested_at DESC" if sort_mode.startswith("Newest") else "title ASC"

# ---------------------------
# Query items
# ---------------------------
items = fetch_all(
    f"""
    SELECT item_id, category, subcategory, title, abstract, ingested_at
    FROM items
    {where_sql}
    ORDER BY {order_sql}
    LIMIT %s OFFSET %s;
    """,
    tuple(params + [page_size, offset]),
)

df = pd.DataFrame(items)

# ---------------------------
# Optional engagement enrichment (per page only)
# ---------------------------
if show_engagement and not df.empty:
    item_ids = df["item_id"].tolist()

    imp = fetch_all(
        """
        SELECT item_id, COUNT(*)::bigint AS impressions
        FROM impression_items
        WHERE item_id = ANY(%s)
        GROUP BY item_id;
        """,
        (item_ids,),
    )
    imp_map = {r["item_id"]: int(r["impressions"]) for r in imp}

    clk = fetch_all(
        """
        SELECT item_id, COUNT(*)::bigint AS clicks
        FROM clicks
        WHERE item_id = ANY(%s)
        GROUP BY item_id;
        """,
        (item_ids,),
    )
    clk_map = {r["item_id"]: int(r["clicks"]) for r in clk}

    df["impressions"] = df["item_id"].map(lambda x: imp_map.get(x, 0))
    df["clicks"] = df["item_id"].map(lambda x: clk_map.get(x, 0))
    df["ctr"] = df.apply(
        lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] else 0.0,
        axis=1,
    )

# ---------------------------
# Display
# ---------------------------
st.subheader("Items")
st.caption(f"Showing page {page} / {total_pages} — {len(df)} rows")

if df.empty:
    st.info("No rows on this page. Try changing filters or reset page to 1.")
    st.stop()

display_cols = ["item_id", "category", "subcategory", "title", "ingested_at"]
if show_engagement:
    display_cols += ["impressions", "clicks", "ctr"]

st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

st.divider()
st.subheader("Item details")

selected_item_id = st.selectbox("Select an item_id to inspect", df["item_id"].tolist())
selected = df[df["item_id"] == selected_item_id].iloc[0].to_dict()

st.markdown(f"### {selected.get('title')}")
st.write(f"**item_id:** `{selected.get('item_id')}`")
st.write(f"**category:** {selected.get('category')}")
st.write(f"**subcategory:** {selected.get('subcategory')}")
st.write(f"**ingested_at:** {selected.get('ingested_at')}")

abstract = selected.get("abstract") or ""
if abstract:
    st.write("**abstract:**")
    st.write(abstract)
else:
    st.info("No abstract available.")

if show_engagement:
    st.write("**engagement (current page stats):**")
    st.json(
        {
            "impressions": int(selected.get("impressions", 0)),
            "clicks": int(selected.get("clicks", 0)),
            "ctr": float(selected.get("ctr", 0.0)),
        }
    )