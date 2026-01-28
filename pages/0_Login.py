import streamlit as st

st.title("Login / Choose Profile")

st.markdown(
    """
    Use this page to **choose a user profile** for the demo.

    For this project UI, we use a **simple login**:
    - You type a username (e.g., "alice", "bob")
    - The app treats this as your identity (`anonymous_id`)
    - All sessions and recommendations will be associated with this name

    (In a production system, this would be replaced with real registration + password.)
    """
)

# Initialize state if not present
if "username" not in st.session_state:
    st.session_state["username"] = None
if "anonymous_id" not in st.session_state:
    st.session_state["anonymous_id"] = None

with st.form("login_form"):
    username = st.text_input(
        "Username",
        value=st.session_state["username"] or "",
        max_chars=50,
    )
    submitted = st.form_submit_button("Set active user")

if submitted:
    username = username.strip()
    if not username:
        st.error("Please enter a non-empty username.")
    else:
        st.session_state["username"] = username
        # For now we just reuse the username as anonymous_id
        st.session_state["anonymous_id"] = username
        st.success(f"Logged in as: {username}")

# Show current status (simplified to avoid f-string issues)
if st.session_state["username"]:
    current_user_text = repr(st.session_state["username"])
else:
    current_user_text = "None"

st.info(f"Current active user: {current_user_text}")

if st.session_state["username"]:
    st.markdown(
        """
        Now you can go to **User Simulator** in the sidebar to:
        - Start a session as this user
        - Request recommendations
        - Click items
        """
    )