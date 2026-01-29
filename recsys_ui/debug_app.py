import uuid
import streamlit as st
import psycopg2

# 1. Page Config
st.set_page_config(page_title="Account", page_icon="👤", layout="wide")

DB_URL = "postgresql://newsrec:newsrec@localhost:5433/newsrec"

# 2. Session State
if "anonymous_id" not in st.session_state:
    st.session_state.anonymous_id = None
if "account_view" not in st.session_state:
    st.session_state.account_view = "choice"

# 3. DB Helpers
def get_db_conn():
    return psycopg2.connect(DB_URL)

def normalize_handle(x: str) -> str:
    return x.strip().lower()

def get_anon_id_by_handle(handle: str) -> str | None:
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT anonymous_id FROM anon_accounts WHERE handle=%s", (handle,))
                row = cur.fetchone()
                return row[0] if row else None
    except: return None

def create_account(handle: str):
    existing = get_anon_id_by_handle(handle)
    if existing: return existing, False
    new_id = f"{handle}_{uuid.uuid4().hex[:10]}"
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO anon_accounts(handle, anonymous_id) VALUES (%s, %s)", (handle, new_id))
        conn.commit()
    return new_id, True

# 4. CSS with AGGRESSIVE ghost box removal
def apply_netflix_ui():
    st.markdown(
        """
        <style>
        /* Hide all empty containers */
        [data-testid="stVerticalBlock"]:empty,
        [data-testid="stHorizontalBlock"]:empty,
        [data-testid="column"]:empty {
            display: none !important;
        }
        
        /* Hide empty text input containers */
        [data-testid="stTextInput"]:has(input[value=""]):not(:focus-within) {
            display: none !important;
        }
        
        .block-container { max-width: 1100px; padding-top: 2.5rem; }
        .hero { display: flex; justify-content: center; margin-top: 1.0rem; }
        .card { 
            width: 520px; border: 1px solid rgba(255,255,255,0.1); 
            border-radius: 18px; padding: 26px 22px; 
            background: rgba(255,255,255,0.03); 
            box-shadow: 0 12px 40px rgba(0,0,0,0.4); 
        }
        .brand { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; }
        .brand h1 { font-size: 32px; margin: 0; color: white; }
        .subtle { color: rgba(255,255,255,0.6); font-size: 14px; margin-bottom: 20px; }
        .divider { height: 1px; background: rgba(255,255,255,0.1); margin: 20px 0; }
        .pill { 
            display: inline-block; font-size: 12px; padding: 4px 12px; 
            border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); 
            background: rgba(255,255,255,0.05); color: white; margin-right: 8px; 
        }
        .muted { color: rgba(255,255,255,0.5); font-size: 13px; }
        
        div[data-testid="stTextInput"] > div {
            background-color: transparent !important;
        }
        input {
            border-radius: 10px !important;
            background-color: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown("🔴 CHECKPOINT 1: Before CSS", unsafe_allow_html=True)
apply_netflix_ui()
st.markdown("🔴 CHECKPOINT 2: After CSS", unsafe_allow_html=True)

# 5. Header
st.markdown("🔴 CHECKPOINT 3: Before Header", unsafe_allow_html=True)
st.markdown('<div class="brand"><div style="font-size:34px;">📰</div><h1>News Recommendation System</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">A personalized news feed. Start anonymous, become warm as you click.</div>', unsafe_allow_html=True)

if st.session_state.anonymous_id:
    st.markdown(f'<span class="pill">Logged in</span><span class="pill">{st.session_state.anonymous_id}</span>', unsafe_allow_html=True)

st.markdown("🔴 CHECKPOINT 4: Before Card", unsafe_allow_html=True)

# 6. Main Logic
st.markdown('<div class="hero"><div class="card">', unsafe_allow_html=True)

if st.session_state.anonymous_id:
    st.markdown("### Welcome back")
    st.markdown('<div class="muted">Continue browsing or log out.</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Browse Feed", type="primary", use_container_width=True):
            st.switch_page("pages/1_browse.py")
    with c2:
        if st.button("Log out", type="secondary", use_container_width=True):
            st.session_state.anonymous_id = None
            st.session_state.account_view = "choice"
            st.rerun()

elif st.session_state.account_view == "choice":
    st.markdown("### Sign in or create an account")
    st.markdown('<div class="muted">No passwords. Just a unique username.</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Sign In", type="primary", use_container_width=True):
            st.session_state.account_view = "login"
            st.rerun()
    with b2:
        if st.button("Create Account", type="secondary", use_container_width=True):
            st.session_state.account_view = "create"
            st.rerun()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">• New user → cold-start<br/>• Click articles → personalization</div>', unsafe_allow_html=True)

elif st.session_state.account_view == "login":
    st.markdown("### Sign In")
    handle = st.text_input("Username", placeholder="e.g. basit1")
    st.markdown('<div style="text-align:center; margin:5px" class="muted">OR</div>', unsafe_allow_html=True)
    anonymous = st.text_input("Account ID", placeholder="Full ID here")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back", use_container_width=True):
            st.session_state.account_view = "choice"
            st.rerun()
    with c2:
        if st.button("Continue", type="primary", use_container_width=True):
            if handle.strip():
                res = get_anon_id_by_handle(normalize_handle(handle))
                if res: st.session_state.anonymous_id = res; st.rerun()
                else: st.error("User not found.")
            elif anonymous.strip():
                st.session_state.anonymous_id = anonymous.strip()
                st.rerun()

elif st.session_state.account_view == "create":
    st.markdown("### Create Account")
    new_handle = st.text_input("Choose username", placeholder="basit1")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back", use_container_width=True):
            st.session_state.account_view = "choice"
            st.rerun()
    with c2:
        if st.button("Create", type="primary", use_container_width=True):
            if new_handle.strip():
                aid, created = create_account(normalize_handle(new_handle))
                if created: st.session_state.anonymous_id = aid; st.rerun()
                else: st.error("Handle taken.")

st.markdown("</div></div>", unsafe_allow_html=True)