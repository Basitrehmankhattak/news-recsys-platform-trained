import json
import streamlit as st

from api_client import ApiClient
from state import ensure_state, start_dwell, get_dwell_ms

# ---------- Login guard ----------
if not st.session_state.get("anonymous_id"):
    st.warning("Please login first from the **Account** page.")
    st.stop()

# ---------- Init ----------
ensure_state()
api = ApiClient()

st.title("Browse")
st.caption(f"Active user: `{st.session_state.anonymous_id}`")

with st.sidebar:
    st.subheader("Session")
    st.write(f"anonymous_id: {st.session_state.anonymous_id}")
    st.write(f"session_id: {st.session_state.session_id}")
    st.session_state.dev_mode = st.toggle("Dev mode", value=st.session_state.dev_mode)


def _extract_clicks(obj):
    """
    Your /users/{anonymous_id}/recent_clicks returns:
      { "anonymous_id": "...", "recent_clicks": ["N123", ...] }
    This function supports that + other shapes.
    """
    if isinstance(obj, dict):
        if "recent_clicks" in obj and isinstance(obj["recent_clicks"], list):
            return obj["recent_clicks"]
        if "items" in obj and isinstance(obj["items"], list):
            return obj["items"]
    if isinstance(obj, list):
        return obj
    return []


def _extract_items(resp):
    """
    Robustly extract items list from response.
    Expected from your backend:
      { "impression_id": "...", "items": [ {...}, ... ] }
    """
    if not isinstance(resp, dict):
        return []
    if isinstance(resp.get("items"), list):
        return resp["items"]
    # fallbacks
    for key in ["recommendations", "results", "data"]:
        val = resp.get(key)
        if isinstance(val, list):
            return val
        if isinstance(val, dict) and isinstance(val.get("items"), list):
            return val["items"]
    return []


def _get_item_id_title(item):
    """
    Your item structure looks like:
      {
        "item_id": "N23299",
        "position": 1,
        "retrieval_score": 0.78,
        "rank_score": 0.001,
        "final_score": 0.001,
        "title": "..."
      }
    """
    if item is None:
        return None, "Untitled"

    if isinstance(item, str):
        return item, item

    if isinstance(item, (list, tuple)) and len(item) > 0:
        item_id = item[0]
        title = item[1] if len(item) > 1 else str(item_id)
        return str(item_id), str(title)

    if isinstance(item, dict):
        item_id = item.get("item_id") or item.get("news_id") or item.get("id")
        title = item.get("title") or item.get("headline") or str(item_id)
        return (str(item_id) if item_id is not None else None), str(title)

    return None, str(item)


# ---------- Warm/Cold detection ----------
recent = None
click_ids = []

try:
    recent = api.get_recent_clicks(st.session_state.anonymous_id, limit=1)
    click_ids = _extract_clicks(recent)
    st.session_state.user_status = "warm" if len(click_ids) >= 1 else "cold"
except Exception as e:
    st.session_state.user_status = "unknown"
    if st.session_state.dev_mode:
        st.write("recent_clicks fetch error:", str(e))

last_clicked = click_ids[0] if click_ids else None

st.info(f"User status: {st.session_state.user_status}")

if st.session_state.dev_mode and recent is not None:
    st.write("Recent clicks response:")
    st.code(json.dumps(recent, ensure_ascii=False, indent=2))


# ---------- Controls ----------
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    page_size = st.number_input("page_size", min_value=5, max_value=50, value=10, step=1)
with c2:
    surface = st.selectbox("surface", ["home", "explore", "sports", "finance"], index=0)
with c3:
    locale = st.selectbox("locale", ["en-US", "fr-FR"], index=0)

refresh = st.button("Get recommendations")


# ---------- Fetch recommendations ----------
if refresh or not st.session_state.last_recs:
    payload = {
        "anonymous_id": st.session_state.anonymous_id,
        "session_id": st.session_state.session_id,
        "device_type": "web",
        "app_version": "streamlit-v1",
        "user_agent": "streamlit",
        "referrer": "streamlit_browse",
        "page_size": int(page_size),
        "surface": surface,
        "locale": locale,
    }

    try:
        resp = api.recommend(payload)
        st.session_state.last_impression_id = resp.get("impression_id")
        st.session_state.last_recs = _extract_items(resp)
        st.success("Recommendations loaded")

        if st.session_state.dev_mode:
            st.write("RAW RESPONSE:")
            st.code(json.dumps(resp, ensure_ascii=False, indent=2))
    except Exception as e:
        st.error(f"/recommendations failed: {e}")
        st.stop()

impression_id = st.session_state.last_impression_id
items = st.session_state.last_recs

if st.session_state.dev_mode:
    st.write(f"impression_id: {impression_id}")
    st.write(f"items: {len(items)}")
    if items and isinstance(items[0], dict):
        st.write("First item:")
        st.code(json.dumps(items[0], ensure_ascii=False, indent=2))

if not items:
    st.warning("No items returned.")
    st.stop()

# ---------- Render ----------
st.subheader("Recommended items")

for pos, it in enumerate(items):
    item_id, title = _get_item_id_title(it)

    # scores if present
    retrieval_score = it.get("retrieval_score") if isinstance(it, dict) else None
    rank_score = it.get("rank_score") if isinstance(it, dict) else None
    final_score = it.get("final_score") if isinstance(it, dict) else None

    # start dwell timer on first render
    if item_id and item_id not in st.session_state.dwell_start:
        start_dwell(item_id)

    with st.container(border=True):
        st.markdown(f"**{pos+1}. {title}**")

        # Reason line
        if st.session_state.user_status == "warm" and last_clicked:
            st.caption(f"Reason: because you clicked {last_clicked}")
        elif st.session_state.user_status == "cold":
            st.caption("Reason: cold-start fallback")
        else:
            st.caption("Reason: recommendation engine output")

        # Dev-mode scores
        if st.session_state.dev_mode:
            st.caption(
                f"retrieval_score={retrieval_score} | rank_score={rank_score} | final_score={final_score}"
            )

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            open_btn = st.button("Open", key=f"open_{impression_id}_{item_id}_{pos}")
        with c2:
            st.caption(f"position: {pos}")
        with c3:
            st.caption(f"dwell_ms: {get_dwell_ms(item_id) if item_id else 0}")

        if open_btn:
            dwell_ms = get_dwell_ms(item_id) if item_id else 0

            click_payload = {
                "impression_id": impression_id,
                "item_id": item_id,
                "position": int(pos),
                "dwell_ms": int(dwell_ms),
                "open_type": "card",
            }

            try:
                api.log_click(click_payload)
                st.success(f"Click logged (dwell_ms={dwell_ms})")
                st.info("Click **Get recommendations** again to refresh warm-user behavior.")
            except Exception as e:
                st.error(f"/click failed: {e}")
