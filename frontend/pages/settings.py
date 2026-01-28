"""
Settings page - User preferences and account management
"""
import streamlit as st
import json
from utils.ui_helpers import create_header, create_alert
from utils.api_client import get_api_client
from utils.auth import logout_user

def render_page():
    """Render settings page"""
    create_header("Settings", "Manage your account and preferences")
    
    if 'anonymous_id' not in st.session_state:
        st.warning("Please sign in or start a session to manage settings.")
        return

    client = get_api_client()
    
    # Load current settings from backend
    # We use session state to cached settings so we don't refetch on every interaction, 
    # but initially we should fetch.
    if 'user_settings' not in st.session_state:
        with st.spinner("Loading settings..."):
            settings = client.get_user_settings(st.session_state.anonymous_id)
            if settings:
                st.session_state.user_settings = settings
            else:
                st.error("Could not load settings.")
                st.session_state.user_settings = {}

    current_settings = st.session_state.user_settings
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Profile", "Preferences", "Privacy", "Notifications", "Account"])
    
    with tab1:
        render_profile_settings(current_settings)
    
    with tab2:
        render_preferences_settings(client, current_settings)
    
    with tab3:
        render_privacy_settings(client, current_settings)
    
    with tab4:
        render_notifications_settings(client, current_settings)
    
    with tab5:
        render_account_settings()

def render_profile_settings(settings):
    """Render profile settings"""
    st.markdown("### Profile Settings")
    
    col1, col2 = st.columns([0.3, 0.7])
    
    with col1:
        st.markdown("""
        <div style='width: 150px; height: 150px; background: #0066cc; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; color: white; font-size: 60px;'>
        U
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Basic Information")
        st.info("Profile updates are currently managed via authentication provider. Preferences below are local to this session.")
        
        st.text_input("Anonymous ID", value=st.session_state.anonymous_id, disabled=True)
        st.text_input("Username", value=st.session_state.get('username', 'Guest'), disabled=True)

def render_preferences_settings(client, settings):
    """Render preferences settings"""
    st.markdown("### Content Preferences")
    
    # Interest preferences
    st.markdown("#### Your Interests")
    
    current_interests = settings.get('interests', [])
    
    updated_interests = st.multiselect(
        "Select topics you're interested in",
        ["Technology", "Business", "Sports", "Science", "Health", "Politics", "Entertainment", "World News"],
        default=[i for i in current_interests if i in ["Technology", "Business", "Sports", "Science", "Health", "Politics", "Entertainment", "World News"]], 
        help="These help us personalize your recommendations"
    )
    
    st.divider()
    
    if st.button("Save Preferences", use_container_width=True):
        new_settings = settings.copy()
        new_settings['interests'] = updated_interests
        
        if client.update_user_settings(st.session_state.anonymous_id, new_settings):
            st.session_state.user_settings = new_settings
            create_alert("Preferences saved successfully!", "success")
        else:
            create_alert("Failed to save preferences.", "error")

def render_privacy_settings(client, settings):
    """Render privacy settings"""
    st.markdown("### Privacy & Data")
    
    privacy = settings.get('privacy', {})
    
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("**Allow analytics tracking**")
    with col2:
        analytics_enabled = st.toggle("Enabled", value=privacy.get('analytics', True), key="analytics_toggle")
    
    st.divider()
    
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("**Personalization enabled**")
    with col2:
        personalization_enabled = st.toggle("Enabled", value=privacy.get('personalization', True), key="personalization_toggle")
    
    st.divider()
    
    if st.button("Save Privacy Settings", use_container_width=True):
        new_settings = settings.copy()
        if 'privacy' not in new_settings: new_settings['privacy'] = {}
        
        new_settings['privacy']['analytics'] = analytics_enabled
        new_settings['privacy']['personalization'] = personalization_enabled
        
        if client.update_user_settings(st.session_state.anonymous_id, new_settings):
            st.session_state.user_settings = new_settings
            create_alert("Privacy settings updated!", "success")
        else:
            create_alert("Failed to update privacy settings.", "error")

def render_notifications_settings(client, settings):
    """Render notifications settings"""
    st.markdown("### Notifications")
    
    notifs = settings.get('notifications', {})
    
    st.markdown("#### Email Notifications")
    
    email_rec = st.toggle("Personalized recommendations", value=notifs.get('email_recommendations', True))
    email_digest = st.toggle("Weekly digest", value=notifs.get('email_digest', True))
    
    st.divider()
    
    if st.button("Save Notification Settings", use_container_width=True):
        new_settings = settings.copy()
        if 'notifications' not in new_settings: new_settings['notifications'] = {}
        
        new_settings['notifications']['email_recommendations'] = email_rec
        new_settings['notifications']['email_digest'] = email_digest
        
        if client.update_user_settings(st.session_state.anonymous_id, new_settings):
            st.session_state.user_settings = new_settings
            create_alert("Notification settings updated!", "success")
        else:
            create_alert("Failed to update notification settings.", "error")

def render_account_settings():
    """Render account settings"""
    st.markdown("### Account Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()
            
    with col2:
        st.warning("Account deletion is permanent.")
        if st.button("Delete Account", use_container_width=True, type="primary"):
            st.error("Please contact support to delete your account.")
