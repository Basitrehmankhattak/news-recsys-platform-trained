"""
News Feed / User Simulator page - Browse and interact with recommendations
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.ui_helpers import create_header, create_badge
from utils.api_client import get_api_client

# Sample news data (removed in favor of backend data)

def render_article_card(article: dict, col_num: int = 1):
    """Render a single article card"""
    client = get_api_client()
    
    with st.container(border=True):
        # Header
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.markdown(f"### {article.get('title', 'Untitled')}")
        with col2:
            score = article.get('score', 0.0)
            st.caption(f"Score: {score:.2f}")
        
        # Category badges (using defaults if missing)
        category = article.get('category', 'General')
        subcategory = article.get('subcategory', 'News')
        
        st.markdown(f"{create_badge(category, 'primary')} " + 
                   f"{create_badge(subcategory, 'success')}", 
                   unsafe_allow_html=True)
        
        # Abstract
        abstract = article.get('abstract', 'No preview available.')
        st.markdown(f"_{abstract}_")
        
        # Metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.caption(f"{article.get('source', 'Unknown Source')}")
        with col2:
            st.caption(f"{article.get('date', 'Just now')}")
        with col3:
            st.caption(f"{category}")
        with col4:
            st.caption(f"ID: {article.get('id', 'N/A')}")
        
        # Entities
        entities = article.get('entities', [])
        if entities:
            entities_html = " ".join([create_badge(e, 'warning') for e in entities])
            st.markdown(f"**Entities:** {entities_html}", unsafe_allow_html=True)
        
        # Actions
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Read Full", key=f"read_{article['id']}", use_container_width=True):
                # Record click
                if 'session_id' in st.session_state and 'impression_id' in st.session_state:
                     # We need impression_id from the recommendations response
                     # stored in the article dict for convenience? 
                     # Or we should have stored it in session state when fetching.
                     # But each page load might have different impression. 
                     # Using the one attached to the article if available.
                     imp_id = article.get('impression_id')
                     if imp_id:
                         client.record_click(
                             impression_id=imp_id,
                             item_id=article['id'],
                             position=article.get('position', 0),
                             open_type="read_full"
                         )
                     
                st.session_state.selected_article = article
                st.rerun()
        with col2:
            if st.button("Like", key=f"like_{article['id']}", use_container_width=True):
                st.success(f"Liked: {article.get('title', '')[:30]}...")
        with col3:
            if st.button("Save", key=f"save_{article['id']}", use_container_width=True):
                st.info(f"Saved for later")
        with col4:
            if st.button("Share", key=f"share_{article['id']}", use_container_width=True):
                st.info("Share options would appear here")

def render_page():
    """Render news feed page"""
    create_header(
        "News Feed",
        "Discover personalized news recommendations tailored to your interests"
    )
    
    # Check if viewing single article
    if 'selected_article' in st.session_state and st.session_state.selected_article:
        render_article_detail()
        if st.button("← Back to Feed"):
            st.session_state.selected_article = None
            st.rerun()
        return
    
    # Fetch Recommendations
    client = get_api_client()
    
    # Store impression id for current view
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = []
    
    # We trigger fetch if list is empty or user manually refreshes (could add refresh button)
    # For now, let's fetch if empty.
    
    # Filters (Frontend only for now, as backend only takes basic params)
    st.markdown("### Filters & Preferences")
    col1, col2, col3, col4 = st.columns(4)
    with col4:
        limit = st.selectbox("Show", [10, 20, 50], index=0, key="feed_limit")
        if st.button("Refresh Feed", use_container_width=True):
            st.session_state.current_recommendations = [] # clear to force refetch
            st.rerun()

    st.divider()

    recommendations = st.session_state.get('current_recommendations', [])
    
    if not recommendations and 'session_id' in st.session_state:
        with st.spinner("Fetching personalized recommendations..."):
            resp = client.get_recommendations(
                session_id=st.session_state.session_id,
                anonymous_id=st.session_state.get('anonymous_id'),
                limit=limit
            )
            
            if resp:
                impression_id = resp.get('impression_id')
                items = resp.get('items', [])
                
                # Map backend items to frontend format
                mapped_items = []
                for item in items:
                    mapped_items.append({
                        "id": item.get('item_id'),
                        "title": item.get('title') or "Untitled Article",
                        "abstract": "Click to read more...", # Backend doesn't provide abstract yet
                        "category": "General", # Backend doesn't provide category yet
                        "subcategory": "",
                        "source": "MIND News",
                        "score": item.get('final_score') or 0.0,
                        "date": "Recently",
                        "image": "",
                        "entities": [],
                        "body_preview": "Full content not available in preview.",
                        "impression_id": impression_id,
                        "position": item.get('position')
                    })
                
                st.session_state.current_recommendations = mapped_items
                recommendations = mapped_items

    # Display articles
    if recommendations:
        st.markdown(f"### Top Picks for You")
        st.divider()
        
        # Display in grid/list
        for idx, article in enumerate(recommendations):
            render_article_card(article)
            if idx < len(recommendations) - 1:
                st.markdown("")
    else:
        if 'session_id' not in st.session_state:
            st.error("Session not initialized. Please refresh the page.")
        else:
            st.info("No recommendations found. Try adjusting filters or refreshing.")

def render_article_detail():
    """Render detailed article view"""
    article = st.session_state.selected_article
    
    st.markdown(f"## {article.get('title', 'Untitled')}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Score", f"{article.get('score', 0):.2f}")
    with col2:
        st.metric("Category", article.get('category', 'N/A'))
    with col3:
        st.metric("Source", article.get('source', 'N/A'))
    with col4:
        st.metric("Published", article.get('date', 'N/A'))
    
    st.divider()
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.markdown("### Full Article")
        st.markdown(f"""
        **Abstract:**
        {article.get('abstract', '')}
        
        **Content:**
        {article.get('body_preview', '')}
        """)
    
    with col2:
        st.markdown("### Article Info")
        with st.container(border=True):
            st.write(f"- ID: {article.get('id')}")
            st.write(f"- Position: {article.get('position')}")
    
    st.divider()
    
    # Interactions
    col1, col2, col3 = st.columns(3)
    with col1:
    with col1:
        if st.button("I Like This", use_container_width=True):
             # FIXED: Now actually correctly records the data to backend.db
             if 'impression_id' in article:
                 client = get_api_client()
                 client.record_click(
                     impression_id=article['impression_id'],
                     item_id=article['id'],
                     position=article.get('position', 0),
                     open_type="like"
                 )
                 st.success("Feedback recorded!")
             else:
                 st.warning("Could not record feedback (missing impression ID)")
    with col2:
        if st.button("Not Interested", use_container_width=True):
            st.info("We'll show you fewer similar articles")
    with col3:
        if st.button("Save Article", use_container_width=True):
            st.success("Article saved to your collection")

