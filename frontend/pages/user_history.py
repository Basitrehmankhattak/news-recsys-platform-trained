"""
User History / Debugger page - Track and analyze user interactions
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.ui_helpers import create_header
from utils.api_client import get_api_client

def render_page():
    """Render user history page"""
    create_header(
        "My Reading History",
        "Track your interactions and analyze your reading patterns"
    )
    
    if 'anonymous_id' not in st.session_state:
        st.warning("Please sign in to view history.")
        return

    # Fetch real history
    client = get_api_client()
    with st.spinner("Loading history..."):
        history_data = client.get_user_history(st.session_state.anonymous_id, limit=100)
    
    if not history_data:
        st.info("No history found. Start reading articles to see them here!")
        # Empty history list for consistent rendering if needed
        history_data = []

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Timeline", "Export", "Debugger"])
    
    with tab1:
        render_timeline_view(history_data)
    
    with tab2:
        render_export_view(history_data)
        
    with tab3:
        render_debugger_view(history_data)

def render_timeline_view(history_data):
    """Render timeline view of history"""
    st.markdown("### Reading Timeline")
    
    if not history_data:
        st.write("No activity recorded yet.")
        return

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        # Get unique actions safely
        actions = list(set([h.get('action') for h in history_data]))
        action_filter = st.selectbox(
            "Action Type",
            ["All"] + actions,
            key="action_filter"
        )
    
    with col2:
        # Get unique categories safely
        categories = list(set([h.get('category') for h in history_data]))
        category_filter = st.selectbox(
            "Category",
            ["All"] + categories,
            key="category_filter"
        )
    
    st.divider()
    
    # Filter and display history
    filtered_history = history_data
    
    if action_filter != "All":
        filtered_history = [h for h in filtered_history if h.get('action') == action_filter]
    
    if category_filter != "All":
        filtered_history = [h for h in filtered_history if h.get('category') == category_filter]
    
    if not filtered_history:
        st.info("No items match your filters.")
        return

    # Display timeline
    for idx, item in enumerate(filtered_history):
        col1, col2 = st.columns([0.15, 0.85])
        
        # Parse timestamp string if possible, or use raw
        ts_str = item.get('timestamp', '')
        # Try to make it readable if it's full ISO format
        try:
            # Assuming format might differ, keeping simple slice for now or use pd.to_datetime logic if desired
            # backend typically returns readable string or iso
            if 'T' in ts_str:
                ts_display = ts_str.split('T')[1][:5]
                date_display = ts_str.split('T')[0]
            else:
                ts_display = ts_str
                date_display = ""
        except:
            ts_display = ts_str
            date_display = ""

        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: #f0f0f0; border-radius: 8px;'>
                <p style='margin: 0; font-size: 0.7rem; color: #666;'>{date_display}</p>
                <p style='margin: 0; font-size: 0.9rem; color: #333;'>{ts_display}</p>
                <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>
                    {item.get('action', 'Viewed')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='padding: 1rem; background: white; border-radius: 8px; border-left: 4px solid #0066cc;'>
                <h4 style='margin: 0;'>{item.get('article', 'Unknown Title')}</h4>
                <div style='margin-top: 0.5rem;'>
                    <span style='display: inline-block; background: #e8f0ff; padding: 0.25rem 0.5rem; 
                    border-radius: 4px; font-size: 0.85rem; margin-right: 0.5rem;'>
                    {item.get('category', 'General')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if idx < len(filtered_history) - 1:
            st.markdown("")

def render_export_view(history_data):
    """Render export view"""
    st.markdown("### Export Data")
    
    if not history_data:
        st.info("No data to export.")
        return

    st.markdown("Download your reading history.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export as CSV", use_container_width=True):
            df = pd.DataFrame(history_data)
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
            json_data = json.dumps(history_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="reading_history.json",
                mime="application/json"
            )

def render_debugger_view(history_data):
    """Render simple debugger view"""
    st.markdown("### Debugger")
    
    st.subheader("Raw History Data")
    if history_data:
        st.json(history_data)
    else:
        st.write("No history data.")
