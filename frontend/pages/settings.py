"""
Settings page - User preferences and account management
"""
import streamlit as st
from utils.ui_helpers import create_header, create_alert
from utils.auth import logout_user
from database.db_init import update_user_profile

def render_page():
    """Render settings page"""
    create_header("Settings", "Manage your account and preferences")
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Profile", "Preferences", "Privacy", "Notifications", "Account"])
    
    with tab1:
        render_profile_settings()
    
    with tab2:
        render_preferences_settings()
    
    with tab3:
        render_privacy_settings()
    
    with tab4:
        render_notifications_settings()
    
    with tab5:
        render_account_settings()

def render_profile_settings():
    """Render profile settings"""
    st.markdown("### Profile Settings")
    
    col1, col2 = st.columns([0.3, 0.7])
    
    with col1:
        st.markdown("#### Profile Picture")
        st.markdown("""
        <div style='width: 150px; height: 150px; background: #0066cc; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; color: white; font-size: 60px;'>
        U
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload new picture", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.success("Profile picture updated!")
    
    with col2:
        st.markdown("#### Basic Information")
        
        with st.form("profile_form"):
            username = st.text_input(
                "Username",
                value=st.session_state.username,
                disabled=True,
                help="Username cannot be changed"
            )
            
            email = st.text_input(
                "Email Address",
                value=st.session_state.email,
                disabled=True,
                help="Email is verified and cannot be changed from here"
            )
            
            full_name = st.text_input(
                "Full Name",
                value=st.session_state.full_name or "",
                placeholder="Enter your full name"
            )
            
            bio = st.text_area(
                "Bio",
                value="",
                placeholder="Tell us about yourself (max 500 chars)",
                max_chars=500,
                height=100
            )
            
            location = st.text_input(
                "Location",
                placeholder="Your location (optional)"
            )
            
            if st.form_submit_button("Save Changes", use_container_width=True):
                result = update_user_profile(
                    st.session_state.user_id,
                    full_name=full_name
                )
                if result['success']:
                    st.session_state.full_name = full_name
                    create_alert("Profile updated successfully!", "success")
                    st.rerun()
                else:
                    create_alert(result['message'], "error")

def render_preferences_settings():
    """Render preferences settings"""
    st.markdown("### Content Preferences")
    
    # Interest preferences
    st.markdown("#### Your Interests")
    
    interests = st.multiselect(
        "Select topics you're interested in",
        ["Technology", "Business", "Sports", "Science", "Health", "Politics", "Entertainment", "World News"],
        default=["Technology", "Business"],
        help="These help us personalize your recommendations"
    )
    
    st.markdown("#### Reading Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        article_length = st.selectbox(
            "Preferred Article Length",
            ["Short (< 3 min read)", "Medium (3-7 min)", "Long (> 7 min)", "No preference"]
        )
    
    with col2:
        update_frequency = st.selectbox(
            "How often to update recommendations",
            ["Every 1 hour", "Every 4 hours", "Every 12 hours", "Daily"]
        )
    
    st.markdown("#### Language & Region")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
    
    with col2:
        region = st.selectbox("Region", ["North America", "Europe", "Asia", "Other"])
    
    st.divider()
    
    # Save preferences
    if st.button("Save Preferences", use_container_width=True):
        create_alert("Preferences saved successfully!", "success")

def render_privacy_settings():
    """Render privacy settings"""
    st.markdown("### Privacy & Data")
    
    st.markdown("#### Data Collection")
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.markdown("**Allow analytics tracking**")
        st.caption("Help us improve by allowing anonymous usage data collection")
    with col2:
        analytics_enabled = st.toggle("Enabled", value=True, key="analytics_toggle")
    
    st.divider()
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.markdown("**Personalization enabled**")
        st.caption("Use your reading history to personalize recommendations")
    with col2:
        personalization_enabled = st.toggle("Enabled", value=True, key="personalization_toggle")
    
    st.divider()
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.markdown("**Share data with partners**")
        st.caption("Allow sharing anonymized data with research partners")
    with col2:
        share_data = st.toggle("Enabled", value=False, key="share_toggle")
    
    st.divider()
    
    st.markdown("#### Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download My Data", use_container_width=True):
            st.info("Your data download will be prepared and sent to your email")
    
    with col2:
        if st.button("Clear History", use_container_width=True):
            if st.button("Confirm Clear", key="confirm_clear"):
                st.success("Reading history cleared!")
    
    with col3:
        if st.button("Delete Account", use_container_width=True):
            st.warning("This will permanently delete your account and all data")
            if st.button("Confirm Delete", key="confirm_delete"):
                st.error("Account deletion is not implemented yet")
    
    st.divider()
    
    if st.button("Save Privacy Settings", use_container_width=True):
        create_alert("Privacy settings updated!", "success")

def render_notifications_settings():
    """Render notifications settings"""
    st.markdown("### Notifications")
    
    st.markdown("#### Email Notifications")
    
    notification_settings = {
        "Personalized recommendations": True,
        "Trending topics in your interests": True,
        "Weekly digest": True,
        "Product updates": False,
        "Marketing emails": False,
    }
    
    for notification, enabled in notification_settings.items():
        col1, col2 = st.columns([0.7, 0.3])
        
        with col1:
            st.markdown(f"**{notification}**")
        
        with col2:
            st.toggle(f"", value=enabled, key=f"notif_{notification}")
    
    st.divider()
    
    st.markdown("#### Push Notifications")
    
    push_settings = {
        "Important news alerts": True,
        "Recommendations": True,
        "Comments replies": False,
        "System updates": True,
    }
    
    for setting, enabled in push_settings.items():
        col1, col2 = st.columns([0.7, 0.3])
        
        with col1:
            st.markdown(f"**{setting}**")
        
        with col2:
            st.toggle(f"", value=enabled, key=f"push_{setting}")
    
    st.divider()
    
    st.markdown("#### Notification Frequency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quiet_hours = st.time_input(
            "Quiet hours start",
            value=None,
            help="Don't send notifications during these hours"
        )
    
    with col2:
        quiet_hours_end = st.time_input(
            "Quiet hours end",
            value=None
        )
    
    st.divider()
    
    if st.button("Save Notification Settings", use_container_width=True):
        create_alert("Notification settings updated!", "success")

def render_account_settings():
    """Render account settings"""
    st.markdown("### Account Management")
    
    st.markdown("#### Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password (min 8 characters)"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm new password"
        )
        
        if st.form_submit_button("Change Password", use_container_width=True):
            if len(new_password) < 8:
                create_alert("Password must be at least 8 characters", "error")
            elif new_password != confirm_password:
                create_alert("Passwords don't match", "error")
            else:
                create_alert("Password changed successfully!", "success")
    
    st.divider()
    
    st.markdown("#### Active Sessions")
    
    sessions_data = {
        'Device': ['Chrome on Windows', 'Safari on iPhone', 'Chrome on Linux'],
        'Location': ['New York, USA', 'San Francisco, USA', 'London, UK'],
        'Last Active': ['Just now', '2 hours ago', '3 days ago'],
        'Status': ['Active', 'Active', 'Inactive']
    }
    
    import pandas as pd
    sessions_df = pd.DataFrame(sessions_data)
    st.dataframe(sessions_df, use_container_width=True, hide_index=True)
    
    if st.button("Logout All Other Sessions", use_container_width=True):
        create_alert("All other sessions logged out", "success")
    
    st.divider()
    
    st.markdown("#### Account Info")
    
    account_info = {
        'Account Created': 'Jan 15, 2025',
        'Last Login': '2 minutes ago',
        'Account Status': 'Active',
        'Verification Status': 'Verified',
        'Email Verified': 'Yes',
        'Phone Verified': 'No'
    }
    
    for key, value in account_info.items():
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            st.caption(key)
        with col2:
            st.caption(value)
    
    st.divider()
    
    st.markdown("#### Danger Zone")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Logout Now", use_container_width=True, type="secondary"):
            logout_user()
            create_alert("Logged out successfully", "success")
            st.rerun()
    
    with col2:
        if st.button("Delete Account", use_container_width=True, type="secondary", key="delete_account_danger_zone"):
            st.warning("This action cannot be undone. All your data will be permanently deleted.")
            if st.checkbox("I understand the consequences"):
                if st.button("Confirm Delete Account", type="secondary"):
                    st.error("Account deletion initiated. You will be logged out.")
