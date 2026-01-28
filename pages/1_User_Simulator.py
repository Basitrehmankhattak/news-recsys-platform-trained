import streamlit as st
import requests
from ui_config import BACKEND_URL

st.title("User Simulator / News Feed")

# --- Helper: get current user from session state ---
username = st.session_state.get("username")
anonymous_id = st.session_state.get("anonymous_id")

if not username or not anonymous_id:
    st.warning(
        "No active user. Please go to the **Login** page first and choose a username."
    )
    st.stop()

st.success(f"Active user: {username!r} (anonymous_id={anonymous_id!r})")

# Initialize session-related state
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "last_impression_id" not in st.session_state:
    st.session_state["last_impression_id"] = None
if "last_items" not in st.session_state:
    st.session_state["last_items"] = []

# --- Section 1: Start session ---
st.subheader("1. Start a session")

col1, col2 = st.columns(2)
with col1:
    device_type = st.selectbox("Device type", ["web", "mobile"], index=0)
    app_version = st.text_input("App version", value="1.0.0")
with col2:
    user_agent = st.text_input("User agent", value="streamlit-ui")
    referrer = st.text_input("Referrer", value="streamlit-demo")

if st.button("Start new session"):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/session/start",
            json={
                "anonymous_id": anonymous_id,
                "device_type": device_type,
                "app_version": app_version,
                "user_agent": user_agent,
                "referrer": referrer,
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        st.session_state["session_id"] = data["session_id"]
        st.success(f"New session started: {data['session_id']}")
    except Exception as e:
        st.error(f"Failed to start session: {e}")

if st.session_state["session_id"]:
    st.info(f"Current session_id: {st.session_state['session_id']}")
else:
    st.stop()  # cannot proceed without a session

# --- Section 2: Request recommendations ---
st.subheader("2. Get recommendations")

page_size = st.slider(
    "How many items to show?",
    min_value=5,
    max_value=30,
    value=10,
    step=1,
)
surface = st.selectbox("Surface", ["home", "article"], index=0)
locale = st.text_input("Locale (optional)", value="en-US")

if st.button("Get recommendations"):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/recommendations",
            json={
                "session_id": st.session_state["session_id"],
                "user_id": None,               # could be real user_id in a full system
                "anonymous_id": anonymous_id,
                "surface": surface,
                "page_size": page_size,
                "locale": locale or None,
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        st.session_state["last_impression_id"] = data["impression_id"]
        st.session_state["last_items"] = data["items"]
        st.success(
            f"Received {len(data['items'])} items for impression_id={data['impression_id']}"
        )
    except Exception as e:
        st.error(f"Failed to get recommendations: {e}")

impression_id = st.session_state["last_impression_id"]
items = st.session_state["last_items"]

# --- Section 3: Show feed and log clicks ---
st.subheader("3. News feed")

if not impression_id or not items:
    st.info("No items yet. Click **Get recommendations** above.")
    st.stop()

st.write(f"Impression ID: `{impression_id}`")

for item in items:
    item_id = item["item_id"]
    title = item.get("title") or "(no title)"
    position = item["position"]

    with st.container():
        st.markdown(f"**[{position}] {title}**  \n`item_id={item_id}`")
        cols = st.columns(2)
        with cols[0]:
            st.caption(
                f"Scores — retrieval: {item.get('retrieval_score')}, "
                f"rank: {item.get('rank_score')}, final: {item.get('final_score')}"
            )
        with cols[1]:
            if st.button("Click / Open", key=f"click_{impression_id}_{item_id}"):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/click",
                        json={
                            "impression_id": impression_id,
                            "item_id": item_id,
                            "position": position,
                            "dwell_ms": None,
                            "open_type": "streamlit",
                        },
                        timeout=5,
                    )
                    resp.raise_for_status()
                    click_data = resp.json()
                    st.success(f"Click logged (status={click_data.get('status')})")
                except Exception as e:
                    st.error(f"Failed to log click: {e}")

        st.markdown("---")