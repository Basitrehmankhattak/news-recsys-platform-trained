"""
Home / Dashboard page
"""
import streamlit as st
from datetime import datetime
from utils.ui_helpers import create_header, create_metric_card

def render_page():
    """Render home page"""
    create_header(
        "Welcome to MIND Recommendation System",
        "Microsoft News Dataset - Personalized News Recommendations",
        st.session_state.full_name or st.session_state.username
    )
    
    # Key Statistics
    st.markdown("## Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", "160,000+", "MIND Dataset")
    with col2:
        st.metric("Total Users", "1,000,000+", "Anonymized")
    with col3:
        st.metric("Recommendations", "15,000,000+", "Impression Logs")
    with col4:
        st.metric("Accuracy", "87.5%", "↑ 3.2%")
    
    st.divider()
    
    # System Overview
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.markdown("### System Overview")
        st.info("""
        **MIND (Microsoft News Dataset) Platform** is an industrial-grade recommendation system 
        built on high-dimensional similarity search for news personalization.
        
        **Key Features:**
        - 160K English news articles with rich metadata
        - 1 Million anonymized users
        - 15+ Million impression logs for accurate training
        - Advanced ML algorithms for personalization
        - Real-time recommendation generation
        """)
    
    with col2:
        st.markdown("### Quick Start")
        with st.container(border=True):
            st.markdown("""
            **Get Started in 3 Steps:**
            
            1. **Browse News Feed**
               - View personalized recommendations
               - Explore trending articles
            
            2. **Track History**
               - See your reading patterns
               - Analyze your interests
            
            3. **View Analytics**
               - Personalized insights
               - Recommendation performance
            """)
    
    st.divider()
    
    # Recent Activity
    st.markdown("### Recent Activity")
    
    activity_data = [
        {"time": "2 hours ago", "action": "Viewed 5 articles", "category": "Technology"},
        {"time": "4 hours ago", "action": "Clicked on Business news", "category": "Business"},
        {"time": "Yesterday", "action": "Completed reading session", "category": "Sports"},
        {"time": "2 days ago", "action": "Updated preferences", "category": "Settings"},
    ]
    
    for activity in activity_data:
        col1, col2, col3 = st.columns([0.5, 0.35, 0.15])
        with col1:
            st.caption(f"{activity['time']}")
        with col2:
            st.caption(activity['action'])
        with col3:
            st.caption(f"{activity['category']}")
        st.divider()
    
    # Featured Sections
    st.markdown("### Featured Sections")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### News Feed")
            st.markdown("Get personalized news recommendations based on your interests and reading history.")
            st.button("→ Go to News Feed", key="btn_feed", use_container_width=True)
    
    with col2:
        with st.container(border=True):
            st.markdown("#### Content Catalog")
            st.markdown("Browse and filter articles by category, topic, entities, and more.")
            st.button("→ Explore Catalog", key="btn_catalog", use_container_width=True)
    
    with col3:
        with st.container(border=True):
            st.markdown("#### My Analytics")
            st.markdown("View detailed analytics about your reading patterns and preferences.")
            st.button("→ View Analytics", key="btn_analytics", use_container_width=True)
    
    st.divider()
    
    # System Information
    with st.expander("About MIND Dataset & System Architecture"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### MIND Dataset Details
            
            **Dataset Size:**
            - 160K English news articles
            - 1 Million anonymized users
            - 15 Million+ impression logs
            
            **Article Features:**
            - Title and abstract
            - Full body content
            - Category classification
            - Named entities
            - Rich metadata
            
            **User Data:**
            - Anonymous user IDs
            - Click events
            - Non-click events
            - Historical reading behavior
            """)
        
        with col2:
            st.markdown("""
            ### System Architecture
            
            **Components:**
            - **Backend**: FastAPI service
            - **Frontend**: Streamlit UI
            - **Database**: SQLite (production: PostgreSQL)
            - **ML Engine**: Similarity Search
            - **API**: RESTful endpoints
            
            **Technologies:**
            - Python, FastAPI, Streamlit
            - High-dimensional similarity search
            - Real-time processing
            - User session management
            """)
    
    # Footer CTA
    st.markdown("---")
    col1, col2, col3 = st.columns([0.33, 0.33, 0.33])
    
    with col1:
        if st.button("Read Full Documentation", use_container_width=True):
            st.info("Documentation link would open here")
    
    with col2:
        if st.button("Contact Support", use_container_width=True):
            st.info("Support contact form would appear here")
    
    with col3:
        if st.button("Go to Settings", use_container_width=True):
            st.session_state.page = "Settings"
            st.rerun()
