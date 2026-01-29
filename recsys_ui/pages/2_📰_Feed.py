import streamlit as st
from api_client import APIClient
from state import ensure_state, new_session, normalize_items, get_impression_id
from ui_components import news_card, badge

st.set_page_config(page_title="Feed", page_icon="📰", layout="wide")
ensure_state()

api = APIClient()
d = st.session_state["demo"]

st.title("📰 Feed")
st.caption("Fetch recommendations and log clicks using your FastAPI endpoints.")

with st.sidebar:
    st.subheader("Identity")
    d["anonymous_id"] = st.text_input("anonymous_id", d["anonymous_id"])
    d["session_id"] = st.text_input("session_id", d["session_id"])
    if st.button("New session_id"):
        new_session()
        st.rerun()

    st.subheader("Request")
    d["page_size"] = st.slider("page_size", 5, 30, int(d["page_size"]))
    d["surface"] = st.selectbox("surface", ["home", "for_you", "trending"], index=0)
    d["locale"] = st.selectbox("locale", ["en-US", "fr-FR", "en-GB"], index=0)

    st.subheader("Device")
    d["device_type"] = st.selectbox("device_type", ["web", "mobile", "tablet"], index=0)
    d["app_version"] = st.text_input("app_version", d["app_version"])
    d["user_agent"] = st.text_input("user_agent", d["user_agent"])
    d["referrer"] = st.text_input("referrer", d["referrer"])

    st.subheader("Click extras (optional)")
    d["dwell_ms"] = st.number_input("dwell_ms", min_value=0, max_value=600000, value=int(d.get("dwell_ms", 0)))
    d["open_type"] = st.text_input("open_type", d.get("open_type", "feed"))

top = st.columns([1, 1, 2])

if top[0].button("🚀 Get recommendations", type="primary"):
    payload = {
        "anonymous_id": d["anonymous_id"],
        "session_id": d["session_id"],
        "device_type": d["device_type"],
        "app_version": d["app_version"],
        "user_agent": d["user_agent"],
        "referrer": d["referrer"],
        "page_size": d["page_size"],
        "surface": d["surface"],
        "locale": d["locale"],
    }
    try:
        res = api.recommendations(payload)
        st.session_state["last_rec"] = res
    except Exception as e:
        st.error(f"/recommendations failed: {e}")

if top[1].button("Clear"):
    st.session_state.pop("last_rec", None)
    st.rerun()

res = st.session_state.get("last_rec")
if not res:
    st.info("Click **Get recommendations** to load your feed.")
    st.stop()

impression_id = get_impression_id(res)
items = normalize_items(res)

badge(f"impression_id: {impression_id}")
st.write(f"Returned items: **{len(items)}**")

def handle_click(item_id, position):
    click_payload = {
        "impression_id": impression_id,
        "item_id": str(item_id),
        "position": int(position) if position is not None else 0,
        "dwell_ms": int(d.get("dwell_ms", 0)) if d.get("dwell_ms", 0) else None,
        "open_type": d.get("open_type") or None,
    }
    # remove None fields (clean payload)
    click_payload = {k: v for k, v in click_payload.items() if v is not None}

    try:
        resp = api.click(click_payload)
        st.success(f"Click logged ✅ status: {resp.get('status', 'ok')}")
    except Exception as e:
        st.error(f"/click failed: {e}")

for it in items:
    news_card(it, impression_id, on_click=handle_click)
