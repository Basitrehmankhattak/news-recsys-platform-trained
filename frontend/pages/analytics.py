"""
Analytics / Metrics page - System and personal analytics
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.ui_helpers import create_header
from utils.api_client import get_api_client

def render_page():
    """Render analytics page"""
    create_header(
        "Analytics & Metrics",
        "View system metrics, recommendations performance, and personalized insights"
    )
    
    # Initialize API client
    client = get_api_client()
    
    # Tabs for different analytics sections
    tab1, tab2, tab3 = st.tabs(["Personal", "System", "Trends"])
    
    with tab1:
        if 'anonymous_id' in st.session_state:
            with st.spinner("Loading personal data..."):
                user_analytics = client.get_user_analytics(st.session_state.anonymous_id)
                user_stats = client.get_user_stats(st.session_state.anonymous_id)
                render_personal_analytics(user_analytics, user_stats)
        else:
            st.warning("Please sign in to view personal analytics.")
    
    with tab2:
        with st.spinner("Loading system data..."):
            system_data = client.get_system_analytics()
            render_system_analytics(system_data)
    
    with tab3:
        with st.spinner("Loading trends..."):
            trending_data = client.get_trending_analytics()
            render_trends_analytics(trending_data)

def render_personal_analytics(analytics, stats):
    """Render personal analytics"""
    st.markdown("### Your Personal Analytics")
    
    if not analytics:
        st.info("No personal analytics available yet.")
        return

    # Overview metrics
    col1, col2, col3 = st.columns(3)
    
    total_reads = stats.get('total_clicks', 0) if stats else 0
    active_days = stats.get('active_days', 0) if stats else 0
    total_sessions = stats.get('total_sessions', 0) if stats else 0

    with col1:
        st.metric("Total Reads", str(total_reads))
    with col2:
        st.metric("Active Days", str(active_days))
    with col3:
        st.metric("Total Sessions", str(total_sessions))
    
    st.divider()
    
    # Reading patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Activity Last 7 Days")
        daily_activity = analytics.get('daily_activity', {})
        if daily_activity:
            chart_data = pd.DataFrame(list(daily_activity.items()), columns=['Date', 'Articles Read'])
            st.bar_chart(chart_data.set_index('Date'))
        else:
            st.write("No activity in the last 7 days.")
    
    with col2:
        st.markdown("#### Category Preferences")
        cat_dist = analytics.get('category_distribution', {})
        if cat_dist:
            category_data = pd.DataFrame(list(cat_dist.items()), columns=['Category', 'Count'])
            st.bar_chart(category_data.set_index('Category')['Count'])
        else:
            st.write("No category data available.")
            
    st.divider()
    
    # Hourly Activity
    st.markdown("#### Hourly Activity")
    hourly_act = analytics.get('hourly_activity', {})
    if hourly_act:
        # Fill missing hours
        full_hours = {f"{h:02d}": 0 for h in range(24)}
        for h, count in hourly_act.items():
            full_hours[h] = count
            
        hourly_data = pd.DataFrame(list(full_hours.items()), columns=['Hour', 'Reads'])
        hourly_data = hourly_data.sort_values('Hour')
        st.line_chart(hourly_data.set_index('Hour'))
    else:
        st.write("No hourly data available.")

def render_system_analytics(data):
    """Render system analytics"""
    st.markdown("### System Performance Analytics")
    
    if not data:
        st.error("Could not fetch system analytics.")
        return
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", str(data.get('total_users', 0)))
    with col2:
        st.metric("Total Articles", str(data.get('total_articles', 0)))
    with col3:
        st.metric("Total Interactions", str(data.get('total_interactions', 0)))
    with col4:
        st.metric("Avg Dwell Time (s)", f"{data.get('avg_dwell_time_ms', 0) / 1000:.1f}")
    
    st.info("These metrics are calculated in real-time from the backend database.")

def render_trends_analytics(data):
    """Render trends analytics"""
    st.markdown("### Trends & Insights")
    
    if not data:
        st.error("Could not fetch trending data.")
        return
    
    # Top Categories
    st.markdown("#### Top Categories (Global)")
    top_cats = data.get('top_categories', {})
    if top_cats:
        cat_df = pd.DataFrame(list(top_cats.items()), columns=['Category', 'Views'])
        st.bar_chart(cat_df.set_index('Category'))
    else:
        st.write("No category data.")

    st.divider()

    # Top Articles
    st.markdown("#### Most Popular Articles")
    top_articles = data.get('top_articles', [])
    
    if top_articles:
        for idx, article in enumerate(top_articles, 1):
            st.markdown(f"""
            **{idx}. {article['title']}**  
            *{article['category']}* • {article['clicks']} reads
            """)
    else:
        st.write("No trending articles yet.")
