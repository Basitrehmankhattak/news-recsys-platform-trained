import os
import time
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

def api_headers():
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def ensure_anon_id():
    if "anonymous_id" not in st.session_state:
        st.session_state["anonymous_id"] = f"anon_{uuid.uuid4().hex[:12]}"

def api_post(path: str, payload: dict):
    r = requests.post(f"{API_BASE}{path}", json=payload, headers=api_headers(), timeout=20)
    return r

def api_get(path: str):
    r = requests.get(f"{API_BASE}{path}", headers=api_headers(), timeout=20)
    return r

def is_logged_in():
    return bool(st.session_state.get("token"))

def fetch_recent_clicks(limit=10):
    anon = st.session_state["anonymous_id"]
    r = api_get(f"/users/{anon}/recent_clicks?limit={limit}")
    if r.ok:
        return r.json()
    return []

def fetch_recommendations(surface: str, page_size: int = 10):
    anon = st.session_state["anonymous_id"]
    payload = {
        "anonymous_id": anon,
        "device_type": "streamlit",
        "app_version": "1.0",
        "user_agent": "streamlit",
        "referrer": "streamlit",
        "surface": surface,
        "page_size": page_size,
    }
    r = api_post("/recommendations", payload)
    if not r.ok:
        raise RuntimeError(f"Recommendations failed: {r.status_code} {r.text}")
    return r.json()

def log_click(impression_id: str, item_id: str, dwell_seconds: float):
    anon = st.session_state["anonymous_id"]
    payload = {
        "anonymous_id": anon,
        "impression_id": impression_id,
        "item_id": item_id,
        "dwell_seconds": float(dwell_seconds),
    }
    r = api_post("/click", payload)
    return r

st.set_page_config(page_title="NewsFlix", page_icon="📰", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
.news-card {
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 14px;
  background: rgba(255,255,255,0.03);
}
.small-muted {color: rgba(255,255,255,0.65); font-size: 0.9rem;}
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  font-size: 0.85rem;
  margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

ensure_anon_id()
if "selected_item" not in st.session_state:
    st.session_state["selected_item"] = None
if "open_time" not in st.session_state:
    st.session_state["open_time"] = None
if "dev_mode" not in st.session_state:
    st.session_state["dev_mode"] = False

with st.sidebar:
    st.markdown("## 📰 NewsFlix")
    st.caption("FastAPI + FAISS + LTR + MMR • Streamlit UI")
    st.markdown("---")
    st.markdown("**anonymous_id**")
    st.code(st.session_state["anonymous_id"])
    st.session_state["dev_mode"] = st.toggle("Dev Mode", value=st.session_state["dev_mode"])
    st.markdown("---")

    if is_logged_in():
        me = api_get("/auth/me")
        if me.ok:
            st.write("✅ Logged in")
            st.caption(me.json().get("email"))
        else:
            st.warning("Token invalid/expired. Please login again.")

        if st.button("Logout"):
            st.session_state["token"] = None
            st.session_state["selected_item"] = None
            st.session_state["open_time"] = None
            st.rerun()
    else:
        st.write("🔒 Not logged in")

if not is_logged_in():
    st.title("Welcome to NewsFlix")
    st.write("Login or create an account to get personalized recommendations.")
    tab1, tab2 = st.tabs(["Login", "Create account"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            r = api_post("/auth/login", {"email": email, "password": password})
            if r.ok:
                st.session_state["token"] = r.json()["access_token"]
                st.success("Logged in ✅")
                st.rerun()
            else:
                st.error(f"Login failed: {r.status_code} {r.text}")

    with tab2:
        email2 = st.text_input("Email", key="reg_email")
        password2 = st.text_input("Password", type="password", key="reg_password")
        if st.button("Create account", use_container_width=True):
            r = api_post("/auth/register", {"email": email2, "password": password2})
            if r.ok:
                st.session_state["token"] = r.json()["access_token"]
                st.success("Account created ✅")
                st.rerun()
            else:
                st.error(f"Register failed: {r.status_code} {r.text}")

else:
    st.title("🎬 Browse")
    st.caption("Top 10 personalized recommendations. Click → logs → becomes warm user.")

    clicks = fetch_recent_clicks(limit=10)
    warm = len(clicks) > 0

    left, right = st.columns([3, 1])
    with left:
        st.markdown(
            f"<span class='badge'>User: {'Warm' if warm else 'Cold'}</span>"
            f"<span class='badge'>Recent clicks: {len(clicks)}</span>",
            unsafe_allow_html=True
        )
    with right:
        if st.button("🔄 Refresh feed", use_container_width=True):
            st.session_state["selected_item"] = None
            st.session_state["open_time"] = None
            st.rerun()

    surface = "because_you_clicked" if warm else "top_picks"

    try:
        rec = fetch_recommendations(surface=surface, page_size=10)
    except Exception as e:
        st.error(str(e))
        st.stop()

    impression_id = rec.get("impression_id")
    items = rec.get("items", [])

    if st.session_state["dev_mode"]:
        st.info(f"impression_id: {impression_id} • surface: {surface}")

    st.markdown("---")

    cols = st.columns(5)
    for i, it in enumerate(items):
        with cols[i % 5]:
            st.markdown("<div class='news-card'>", unsafe_allow_html=True)
            st.subheader((it.get("title") or "Untitled")[:80])
            st.markdown(f"<div class='small-muted'>Item: {it.get('item_id')}</div>", unsafe_allow_html=True)

            if st.session_state["dev_mode"]:
                st.caption(
                    f"pos={it.get('position')} final={it.get('final_score')} "
                    f"retr={it.get('retrieval_score')} rank={it.get('rank_score')}"
                )

            if st.button("Open", key=f"open_{it.get('item_id')}", use_container_width=True):
                st.session_state["selected_item"] = {**it, "impression_id": impression_id}
                st.session_state["open_time"] = time.time()
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["selected_item"]:
        st.markdown("---")
        it = st.session_state["selected_item"]
        st.header("📰 Now reading")
        st.subheader(it.get("title", "Untitled"))

        url = it.get("url")
        if url:
            st.write("Link:", url)
        else:
            st.info("No URL available (depends on what fields your API returns).")

        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            if st.button("✅ Read (log click)", use_container_width=True):
                start = st.session_state.get("open_time") or time.time()
                dwell = max(1.0, time.time() - start)
                r = log_click(it["impression_id"], it["item_id"], dwell)
                if r.ok:
                    st.success(f"Click logged ✅ (dwell: {dwell:.1f}s)")
                    st.session_state["selected_item"] = None
                    st.session_state["open_time"] = None
                    st.rerun()
                else:
                    st.error(f"Click failed: {r.status_code} {r.text}")
        with c2:
            if st.button("Close", use_container_width=True):
                st.session_state["selected_item"] = None
                st.session_state["open_time"] = None
                st.rerun()
        with c3:
            st.caption("Tip: After 1 click you become a Warm user and feed improves.")
