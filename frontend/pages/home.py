"""
Home / Dashboard page
"""
import streamlit as st
from datetime import datetime
from utils.ui_helpers import create_header, create_metric_card
from utils.api_client import get_api_client

def render_page():
    """Render home page"""
    create_header(
        "Welcome to MIND Recommendation System",
        "Microsoft News Dataset - Personalized News Recommendations",
        st.session_state.get('full_name') or st.session_state.get('username')
    )
    
    client = get_api_client()
    
    # fetch system analytics
    with st.spinner("Loading system stats..."):
        system_stats = client.get_system_analytics()
    
    # Key Statistics
    st.markdown("## Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    if system_stats:
        total_arts = system_stats.get('total_articles', 0)
        total_users = system_stats.get('total_users', 0)
        total_inters = system_stats.get('total_interactions', 0)
        
        with col1:
            st.metric("Total Articles", f"{total_arts:,}", "MIND Dataset")
        with col2:
            st.metric("Total Users", f"{total_users:,}", "Registered/Anon")
        with col3:
            st.metric("Interactions", f"{total_inters:,}", "Clicks & Views")
        with col4:
            st.metric("System Status", "Online", "🟢 Healthy")
    else:
        st.warning("Could not load system statistics.")
    
    st.divider()
    
    # System Overview
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.markdown("### System Overview")
        st.info("""
        **MIND (Microsoft News Dataset) Platform** is an industrial-grade recommendation system 
        built on high-dimensional similarity search for news personalization.
        
        **Real-Time Data Features:**
        - Live recommendation generation
        - Real-time click tracking
        - Dynamic user profiling
        - Instant analytics updates
        """)
    
    with col2:
        st.markdown("### Quick Start")
        with st.container(border=True):
            st.markdown("""
            **Get Started:**
            
            1. **News Feed**: View your personalized recommendations.
            2. **History**: Track what you've read.
            3. **Analytics**: See your reading habits analysis.
            """)
    
    st.divider()
    
    # Recent Activity (Real)
    st.markdown("### Your Recent Activity")
    
    if st.session_state.get('anonymous_id'):
        history = client.get_user_history(st.session_state.anonymous_id, limit=5)
        
        if history:
            for activity in history:
                col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
                # format timestamp roughly
                ts = activity.get('timestamp', '').replace('T', ' ')[:16]
                
                with col1:
                    st.caption(ts)
                with col2:
                    st.write(f"**{activity.get('action')}**: {activity.get('article')}")
                with col3:
                    st.caption(activity.get('category'))
                st.divider()
        else:
            st.info("No recent activity found. Go read some news!")
    else:
        st.warning("Please sign in to view your activity.")
    
    # Featured Sections
    st.markdown("### Explore")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### News Feed")
            if st.button("→ Go to News Feed", key="btn_feed", use_container_width=True):
                st.session_state.page = "News Feed"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown("#### Content Catalog")
            if st.button("→ Explore Catalog", key="btn_catalog", use_container_width=True):
                st.session_state.page = "Content Catalog"
                st.rerun()
    
    with col3:
        with st.container(border=True):
            st.markdown("#### My Analytics")
            if st.button("→ View Analytics", key="btn_analytics", use_container_width=True):
                st.session_state.page = "Analytics"
                st.rerun()
