"""
Analytics / Metrics page - System and personal analytics
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.ui_helpers import create_header

def render_page():
    """Render analytics page"""
    create_header(
        "Analytics & Metrics",
        "View system metrics, recommendations performance, and personalized insights"
    )
    
    # Tabs for different analytics sections
    tab1, tab2, tab3, tab4 = st.tabs(["Personal", "System", "Recommendations", "Trends"])
    
    with tab1:
        render_personal_analytics()
    
    with tab2:
        render_system_analytics()
    
    with tab3:
        render_recommendations_analytics()
    
    with tab4:
        render_trends_analytics()

def render_personal_analytics():
    """Render personal analytics"""
    st.markdown("### Your Personal Analytics")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reads", "47", "↑ 12 this week")
    with col2:
        st.metric("Avg Reading Time", "3m 18s", "↑ 45s")
    with col3:
        st.metric("Engagement Score", "0.82", "↑ 0.05")
    with col4:
        st.metric("Streak Days", "8", "Keep going!")
    
    st.divider()
    
    # Reading patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Reading Timeline")
        
        # Generate sample data for last 7 days
        dates = [(datetime.now() - timedelta(days=i)).strftime("%a") for i in range(7, 0, -1)]
        reads = [3, 5, 4, 6, 8, 5, 4]
        
        chart_data = pd.DataFrame({
            'Date': dates,
            'Articles Read': reads
        })
        
        st.bar_chart(chart_data.set_index('Date'))
    
    with col2:
        st.markdown("#### Category Distribution")
        
        category_data = pd.DataFrame({
            'Category': ['Technology', 'Business', 'Sports', 'Health', 'Science'],
            'Count': [28, 10, 5, 3, 1]
        })
        
        st.pie_chart(category_data.set_index('Category')['Count'])
    
    st.divider()
    
    # Engagement by time of day
    st.markdown("#### Peak Reading Times")
    
    hours = ['6AM', '9AM', '12PM', '3PM', '6PM', '9PM', '12AM', '3AM']
    engagement = [0.2, 0.4, 0.6, 0.5, 0.8, 0.9, 0.7, 0.1]
    
    time_data = pd.DataFrame({
        'Hour': hours,
        'Engagement': engagement
    })
    
    st.line_chart(time_data.set_index('Hour'))
    
    st.info("You're most active between 6-9 PM. Best time for recommendations!")

def render_system_analytics():
    """Render system analytics"""
    st.markdown("### System Performance Analytics")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Uptime", "99.9%", "↑ Last 30 days")
    with col2:
        st.metric("Avg Response Time", "156ms", "↓ 12ms")
    with col3:
        st.metric("Active Users", "127,450", "↑ 2.3%")
    with col4:
        st.metric("API Calls Today", "4.2M", "↑ 15%")
    
    st.divider()
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Response Time Trend")
        
        response_times = [150, 152, 151, 155, 156, 154, 158, 156]
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Today']
        
        response_data = pd.DataFrame({
            'Day': days,
            'Response Time (ms)': response_times
        })
        
        st.line_chart(response_data.set_index('Day'))
    
    with col2:
        st.markdown("#### Recommendation Accuracy")
        
        metrics = ['Precision', 'Recall', 'F1-Score', 'NDCG@10']
        scores = [0.87, 0.85, 0.86, 0.89]
        
        accuracy_data = pd.DataFrame({
            'Metric': metrics,
            'Score': scores
        })
        
        st.bar_chart(accuracy_data.set_index('Metric'))
    
    st.divider()
    
    # System health
    st.markdown("#### System Health")
    
    health_metrics = pd.DataFrame({
        'Component': ['API Server', 'Database', 'Cache', 'ML Engine', 'Message Queue'],
        'Status': ['Healthy', 'Healthy', 'Healthy', 'Healthy', 'Healthy'],
        'CPU': ['45%', '32%', '12%', '67%', '8%'],
        'Memory': ['62%', '78%', '55%', '85%', '22%'],
        'Load': ['0.8', '0.6', '0.2', '1.2', '0.1']
    })
    
    st.dataframe(health_metrics, use_container_width=True, hide_index=True)

def render_recommendations_analytics():
    """Render recommendations analytics"""
    st.markdown("### Recommendation Performance")
    
    # Recommendation metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Recommendations", "4,827", "↑ 12%")
    with col2:
        st.metric("Click-Through Rate", "18.2%", "↑ 2.1%")
    with col3:
        st.metric("Avg Recommendation Relevance", "0.84", "↑ 0.03")
    with col4:
        st.metric("Diversity Score", "0.76", "→ Stable")
    
    st.divider()
    
    # Recommendation quality
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recommendation Method Distribution")
        
        method_data = pd.DataFrame({
            'Method': ['Similarity Search', 'Collaborative Filtering', 'Content-Based', 'Hybrid'],
            'Percentage': [65, 20, 10, 5]
        })
        
        st.pie_chart(method_data.set_index('Method')['Percentage'])
    
    with col2:
        st.markdown("#### Recommendation Quality by Category")
        
        category_quality = pd.DataFrame({
            'Category': ['Technology', 'Business', 'Sports', 'Health'],
            'Relevance': [0.89, 0.82, 0.76, 0.81],
            'CTR': [21, 16, 12, 15]
        })
        
        st.bar_chart(category_quality.set_index('Category')['Relevance'])
    
    st.divider()
    
    # A/B Testing Results
    st.markdown("#### A/B Testing Results")
    
    ab_test_data = pd.DataFrame({
        'Variant': ['Control (Old)', 'Treatment (New)'],
        'Users': [50000, 50000],
        'CTR': ['16.8%', '18.2%'],
        'Avg Time': ['3m 15s', '3m 45s'],
        'Engagement': [0.81, 0.84],
        'Conversion': ['4.2%', '5.1%']
    })
    
    st.dataframe(ab_test_data, use_container_width=True, hide_index=True)
    
    st.success("Treatment variant shows 8.3% improvement. Rollout scheduled for next week.")

def render_trends_analytics():
    """Render trends analytics"""
    st.markdown("### Trends & Insights")
    
    # Key insights
    st.markdown("#### Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Trending Topic:** Artificial Intelligence & Machine Learning
        - 34% increase in related articles this week
        - High engagement (0.89 relevance score)
        - Recommended to 45% of users
        """)
    
    with col2:
        st.info("""
        **Rising Category:** Climate & Sustainability
        - 67% increase in searches
        - Growing user interest
        - Consider personalizing recommendations
        """)
    
    st.divider()
    
    # Topic trends
    st.markdown("#### Topic Trends (Last 30 Days)")
    
    topics = ['AI/ML', 'Climate', 'Crypto', 'Healthcare', 'Space Tech', 'EV']
    week1 = [100, 45, 78, 65, 52, 88]
    week2 = [145, 67, 72, 71, 58, 95]
    week3 = [189, 95, 68, 78, 65, 102]
    week4 = [234, 134, 61, 85, 73, 115]
    
    trends_data = pd.DataFrame({
        'Topic': topics,
        'Week 1': week1,
        'Week 2': week2,
        'Week 3': week3,
        'Week 4': week4
    })
    
    st.line_chart(trends_data.set_index('Topic'))
    
    st.divider()
    
    # User engagement trends
    st.markdown("#### User Engagement Trends")
    
    engagement_stages = ['New Users', 'Casual Readers', 'Regular Users', 'Power Users']
    user_count = [8234, 45678, 67890, 12345]
    engagement_score = [0.42, 0.68, 0.85, 0.95]
    
    engagement_trends = pd.DataFrame({
        'User Segment': engagement_stages,
        'Count': user_count,
        'Engagement': engagement_score
    })
    
    st.bar_chart(engagement_trends.set_index('User Segment')['Engagement'])
    
    st.markdown("""
    **Recommendations:**
    - Focus retention efforts on casual readers (boost to regular user segment)
    - Implement gamification for power users to increase frequency
    - Improve onboarding for new users to accelerate engagement
    """)
