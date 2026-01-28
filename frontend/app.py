"""
Main Streamlit Application - News Recommendation System
Multi-page professional UI with authentication
"""
import streamlit as st
from pathlib import Path
import sys

# Add frontend directory to path
frontend_dir = Path(__file__).parent
sys.path.insert(0, str(frontend_dir))

from database.db_init import init_db
from utils.auth import init_session_state, is_authenticated, logout_user
from utils.ui_helpers import apply_custom_css

# Page configuration
st.set_page_config(
    page_title="MIND Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "**MIND News Recommendation System** - Powered by High-Dimensional Similarity Search"
    }
)

# Initialize
apply_custom_css()
init_session_state()
init_db()

# Sidebar Navigation
with st.sidebar:

    
    if not is_authenticated():
        st.markdown("### Authentication")
        auth_option = st.radio("Choose action:", ["Login", "Sign Up"], key="auth_radio")
        
        if auth_option == "Login":
            st.session_state.page = "Login"
        else:
            st.session_state.page = "Sign Up"
    
    else:
        st.markdown(f"### Welcome, {st.session_state.full_name or st.session_state.username}!")
        
        st.markdown("### Navigation")
        page_options = [
            "Home",
            "News Feed",
            "My History",
            "Content Catalog",
            "Analytics",
            "Settings"
        ]
        
        selected_page = st.radio("Go to:", page_options, key="page_nav")
        st.session_state.page = selected_page
        
        st.divider()
        
        # Quick stats
        st.markdown("### Quick Stats")
        
        # Fetch real stats
        try:
            client = get_api_client()
            if 'anonymous_id' in st.session_state:
                stats = client.get_user_stats(st.session_state.anonymous_id)
            else:
                stats = None
        except Exception:
            stats = None

        col1, col2 = st.columns(2)
        with col1:
             val = str(stats.get('total_clicks', 0)) if stats else "0"
             st.metric("Articles Read", val)
        with col2:
             val = str(stats.get('active_days', 0)) if stats else "0"
             st.metric("Active Days", val)
        
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()

# Main Content Area
def render_auth_pages():
    """Render authentication pages"""
    if st.session_state.page == "Login":
        from pages.auth import render_login_page
        render_login_page()
    elif st.session_state.page == "Sign Up":
        from pages.auth import render_signup_page
        render_signup_page()

def render_app_pages():
    """Render application pages"""
    pages = {
        "Home": "pages.home",
        "News Feed": "pages.news_feed",
        "My History": "pages.user_history",
        "Content Catalog": "pages.content_catalog",
        "Analytics": "pages.analytics",
        "Settings": "pages.settings"
    }
    
    page_module = pages.get(st.session_state.page)
    
    if page_module:
        try:
            module = __import__(page_module, fromlist=['render_page'])
            module.render_page()
        except ImportError as e:
            st.error(f"Error loading page: {str(e)}")

# Route to appropriate page
if not is_authenticated() and st.session_state.page in ["Login", "Sign Up"]:
    render_auth_pages()
elif not is_authenticated():
    # Redirect to login if not authenticated and trying to access app pages
    from pages.auth import render_login_page
    render_login_page()
else:
    # Render app pages
    render_app_pages()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #666; font-size: 0.9rem;'>
        <p>© 2026 MIND Recommendation System | Powered by High-Dimensional Similarity Search</p>

    </div>
""", unsafe_allow_html=True)
