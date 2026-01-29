import streamlit as st

def badge(text: str):
    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background:rgba(100,100,100,0.15);
            font-size:12px;
            margin-right:6px;">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )

def fmt(x):
    try:
        return f"{float(x):.6f}"
    except Exception:
        return "—" if x is None else str(x)

def score_strip(item: dict):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("retrieval_score", fmt(item.get("retrieval_score")))
    c2.metric("rank_score", fmt(item.get("rank_score")))
    c3.metric("final_score", fmt(item.get("final_score")))
    c4.metric("position", str(item.get("position", "—")))

def news_card(item: dict, impression_id: str, on_click):
    title = item.get("title", "(no title)")
    item_id = item.get("item_id")
    position = item.get("position")

    with st.container(border=True):
        st.markdown(f"### {position}. {title}")
        st.caption(f"item_id: `{item_id}` • impression_id: `{impression_id}`")
        score_strip(item)

        a, b = st.columns([1, 6])
        with a:
            if st.button("✅ Click", key=f"click_{impression_id}_{item_id}"):
                on_click(item_id, position)
        with b:
            st.write("")
