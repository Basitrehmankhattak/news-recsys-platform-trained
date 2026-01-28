"""
User History / Debugger page - Track and analyze user interactions
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.ui_helpers import create_header

# Sample history data
SAMPLE_HISTORY = [
    {"timestamp": "2025-01-27 14:30", "action": "Clicked", "article": "AI Models Show Promise in Medical Diagnosis", "category": "Technology", "dwell_time": 245, "sentiment": "Positive"},
    {"timestamp": "2025-01-27 14:15", "action": "Viewed", "article": "Stock Market Reaches All-Time High", "category": "Business", "dwell_time": 0, "sentiment": "Neutral"},
    {"timestamp": "2025-01-27 13:45", "action": "Clicked", "article": "Battery Technology Breakthrough", "category": "Technology", "dwell_time": 180, "sentiment": "Positive"},
    {"timestamp": "2025-01-27 13:20", "action": "Viewed", "article": "Championship Team Claims Victory", "category": "Sports", "dwell_time": 0, "sentiment": "Positive"},
    {"timestamp": "2025-01-27 12:50", "action": "Clicked", "article": "Cloud Computing in Enterprise", "category": "Technology", "dwell_time": 320, "sentiment": "Positive"},
    {"timestamp": "2025-01-27 12:00", "action": "Viewed", "article": "Climate Summit Emissions Targets", "category": "World", "dwell_time": 0, "sentiment": "Neutral"},
    {"timestamp": "2025-01-26 18:30", "action": "Clicked", "article": "Quantum Computing Advances", "category": "Technology", "dwell_time": 150, "sentiment": "Positive"},
    {"timestamp": "2025-01-26 15:45", "action": "Viewed", "article": "New Tech Startup Funding", "category": "Business", "dwell_time": 0, "sentiment": "Positive"},
    {"timestamp": "2025-01-26 14:20", "action": "Clicked", "article": "Healthcare Innovation Report", "category": "Health", "dwell_time": 210, "sentiment": "Positive"},
    {"timestamp": "2025-01-26 11:00", "action": "Viewed", "article": "Sports League Rule Changes", "category": "Sports", "dwell_time": 0, "sentiment": "Neutral"},
]

def render_page():
    """Render user history page"""
    create_header(
        "My Reading History",
        "Track your interactions and analyze your reading patterns"
    )
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Timeline", "Analytics", "Debugger", "Export"])
    
    with tab1:
        render_timeline_view()
    
    with tab2:
        render_analytics_view()
    
    with tab3:
        render_debugger_view()
    
    with tab4:
        render_export_view()

def render_timeline_view():
    """Render timeline view of history"""
    st.markdown("### Reading Timeline")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action_filter = st.selectbox(
            "Action Type",
            ["All", "Clicked", "Viewed", "Saved", "Shared"],
            key="action_filter"
        )
    
    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All", "Technology", "Business", "Sports", "World", "Health"],
            key="category_filter"
        )
    
    with col3:
        days_filter = st.selectbox(
            "Time Range",
            ["Last 24h", "Last 7 days", "Last 30 days", "All time"],
            key="time_filter"
        )
    
    st.divider()
    
    # Filter and display history
    history = SAMPLE_HISTORY.copy()
    
    if action_filter != "All":
        history = [h for h in history if h['action'] == action_filter]
    
    if category_filter != "All":
        history = [h for h in history if h['category'] == category_filter]
    
    # Display timeline
    for idx, item in enumerate(history):
        col1, col2 = st.columns([0.15, 0.85])
        
        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 8px;'>
                <p style='margin: 0; font-size: 0.8rem; color: #666;'>{item['timestamp'].split()[1]}</p>
                <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>
                    {item['action']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            sentiment_icon = {"Positive": "😊", "Neutral": "😐", "Negative": "😞"}.get(item['sentiment'], "😐")
            
            st.markdown(f"""
            <div style='padding: 1rem; background: white; border-radius: 8px; border-left: 4px solid #0066cc;'>
                <h4 style='margin: 0;'>{item['article']}</h4>
                <div style='margin-top: 0.5rem;'>
                    <span style='display: inline-block; background: #e8f0ff; padding: 0.25rem 0.5rem; 
                    border-radius: 4px; font-size: 0.85rem; margin-right: 0.5rem;'>
                    {item['category']}
                    </span>
                    <span style='display: inline-block; background: #f0f0f0; padding: 0.25rem 0.5rem; 
                    border-radius: 4px; font-size: 0.85rem; margin-right: 0.5rem;'>
                    {item['dwell_time']}s
                    </span>
                    <span style='display: inline-block; background: #fff0f0; padding: 0.25rem 0.5rem; 
                    border-radius: 4px; font-size: 0.85rem;'>
                    {item['sentiment']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if idx < len(history) - 1:
            st.markdown("")

def render_analytics_view():
    """Render analytics view"""
    st.markdown("### Reading Analytics")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interactions", "47", "↑ 12 this week")
    with col2:
        st.metric("Avg Dwell Time", "198s", "↓ 15s yesterday")
    with col3:
        st.metric("Favorite Category", "Technology", "65% of reads")
    with col4:
        st.metric("Reading Streak", "8 days", "🔥 Keep it up!")
    
    st.divider()
    
    # Category distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Reading by Category")
        category_data = pd.DataFrame({
            'Category': ['Technology', 'Business', 'Sports', 'World', 'Health'],
            'Articles Read': [31, 8, 4, 2, 2],
            'Percentage': [68.9, 17.8, 8.9, 4.4, 4.4]
        })
        
        st.bar_chart(category_data.set_index('Category')['Articles Read'])
        
        st.dataframe(category_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Engagement Metrics")
        engagement_data = pd.DataFrame({
            'Metric': ['Very Engaged (>300s)', 'Engaged (150-300s)', 'Casual (<150s)', 'Not Engaged (Viewed only)'],
            'Count': [12, 18, 10, 7],
            'Percentage': [25.5, 38.3, 21.3, 14.9]
        })
        
        colors = ['#28a745', '#0066cc', '#ffc107', '#e0e0e0']
        st.bar_chart(engagement_data.set_index('Metric')['Percentage'])
    
    st.divider()
    
    # Time-based analysis
    st.markdown("#### Reading Pattern")
    
    time_data = pd.DataFrame({
        'Hour': ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM', '12 AM'],
        'Articles': [2, 5, 8, 6, 12, 8, 3]
    })
    
    st.line_chart(time_data.set_index('Hour')['Articles'])
    
    st.markdown("You're most active in the **evening (6-9 PM)**. Consider setting notifications during this time!")

def render_debugger_view():
    """Render debugger view for advanced analysis"""
    st.markdown("### Advanced Debugger")
    
    st.info("""
    This section provides detailed debugging information about the recommendation system's behavior, 
    user profiling, and recommendation generation process.
    """)
    
    # Debugger tabs
    debug_tab1, debug_tab2, debug_tab3 = st.tabs(["User Profile", "Recommendation Log", "System Debug"])
    
    with debug_tab1:
        st.markdown("#### User Profile Information")
        
        user_profile = {
            "User ID": st.session_state.user_id,
            "Username": st.session_state.username,
            "Email": st.session_state.email,
            "Full Name": st.session_state.full_name,
            "Total Interactions": 47,
            "Average Engagement Score": 0.78,
            "Primary Interest": "Technology",
            "Secondary Interests": "Business, Science",
            "Account Created": "2025-01-15",
            "Last Active": "2025-01-27 14:30",
            "Session Duration": "2h 15m"
        }
        
        profile_df = pd.DataFrame(list(user_profile.items()), columns=['Property', 'Value'])
        st.dataframe(profile_df, use_container_width=True, hide_index=True)
        
        st.markdown("**User Embedding Vector (sample):**")
        embedding_sample = "[0.234, 0.891, 0.123, -0.445, 0.678, 0.234, -0.123, 0.567, ...]"
        st.code(embedding_sample, language="python")
    
    with debug_tab2:
        st.markdown("#### Recent Recommendations Log")
        
        recommendations_log = pd.DataFrame({
            'Timestamp': ['2025-01-27 14:30', '2025-01-27 14:00', '2025-01-27 13:30', '2025-01-27 13:00'],
            'Article ID': ['N1001', 'N1002', 'N1003', 'N1004'],
            'Title': ['AI Models Medical', 'Stock Market High', 'Battery Tech', 'Championship Victory'],
            'Score': [0.924, 0.856, 0.845, 0.812],
            'Method': ['Similarity Search', 'Similarity Search', 'Similarity Search', 'Popularity'],
            'Rank': [1, 2, 3, 4],
            'User Clicked': ['Yes', 'No', 'Yes', 'No']
        })
        
        st.dataframe(recommendations_log, use_container_width=True, hide_index=True)
        
        st.markdown("**Recommendation Generation Details:**")
        with st.expander("View Algorithm Details"):
            st.markdown("""
            - **Algorithm**: High-Dimensional Similarity Search
            - **Embedding Model**: MIND-specific embeddings (1024-dim)
            - **Similarity Metric**: Cosine similarity
            - **Time Complexity**: O(log n)
            - **Space Complexity**: O(n log n)
            - **Personalization Factor**: 0.85
            - **Diversity Factor**: 0.15
            """)
    
    with debug_tab3:
        st.markdown("#### System Debug Information")
        
        debug_info = {
            "Backend Status": "Connected",
            "Database Status": "Active",
            "Cache Status": "Warm",
            "API Response Time": "145ms",
            "Last Sync": "2 minutes ago",
            "Error Count (24h)": "0",
            "Warning Count (24h)": "2",
            "Session Token": f"{st.session_state.get('session_token', 'N/A')[:20]}...",
            "Browser": "Chrome 120.0",
            "IP Address": "192.168.1.100 (hidden)"
        }
        
        debug_df = pd.DataFrame(list(debug_info.items()), columns=['Parameter', 'Value'])
        st.dataframe(debug_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Refresh Embeddings"):
                st.success("User embeddings refreshed successfully!")
        with col2:
            if st.button("Clear Cache"):
                st.info("Cache cleared. Next request will refresh data.")

def render_export_view():
    """Render export view"""
    st.markdown("### Export Data")
    
    st.markdown("""
    Download your reading history and personal data in various formats.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export as CSV", use_container_width=True):
            # Create CSV
            df = pd.DataFrame(SAMPLE_HISTORY)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="reading_history.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export as JSON", use_container_width=True):
            import json
            json_data = json.dumps(SAMPLE_HISTORY, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="reading_history.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("Export as Excel", use_container_width=True):
            st.info("Excel export requires openpyxl library")
    
    st.divider()
    
    st.markdown("#### Data Summary")
    summary = pd.DataFrame({
        'Item': ['Total Interactions', 'Total Articles Read', 'Time Spent', 'Export Date'],
        'Value': ['47', '24', '2h 45m', datetime.now().strftime('%Y-%m-%d %H:%M')]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)
