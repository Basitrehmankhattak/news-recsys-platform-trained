"""
Authentication utilities for Streamlit session management
"""
import streamlit as st
from datetime import datetime
from database.db_init import (
    authenticate_user, 
    register_user, 
    verify_email,
    get_user_by_id,
    generate_verification_code
)

import uuid
from utils.api_client import get_api_client

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'
        
    # Session tracking
    if 'anonymous_id' not in st.session_state:
        st.session_state.anonymous_id = str(uuid.uuid4())
        
    if 'session_id' not in st.session_state:
        # Initialize backend session (gracefully degrade if backend unavailable)
        try:
            client = get_api_client()
            session_id = client.start_session(st.session_state.anonymous_id)
            if session_id:
                st.session_state.session_id = session_id
        except Exception:
            # Silent fail if backend is unavailable - frontend works independently
            pass


def login_user(username: str, password: str) -> bool:
    """Login user"""
    result = authenticate_user(username, password)
    
    if result['success']:
        st.session_state.authenticated = True
        st.session_state.user_id = result['user_id']
        st.session_state.username = result['username']
        st.session_state.email = result['email']
        st.session_state.full_name = result['full_name']
        st.session_state.session_token = result['session_token']
        return True
    return False

def signup_user(username: str, email: str, password: str, full_name: str) -> dict:
    """Register new user"""
    return register_user(username, email, password, full_name)

def verify_user_email(user_id: int, code: str) -> dict:
    """Verify user email"""
    return verify_email(user_id, code)

def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.full_name = None
    st.session_state.session_token = None
    st.session_state.page = 'Home'

def require_authentication():
    """Decorator to require authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error("⚠️ Please log in first to access this page.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """Get current logged-in user"""
    if st.session_state.get('authenticated', False):
        return get_user_by_id(st.session_state.user_id)
    return None

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)
