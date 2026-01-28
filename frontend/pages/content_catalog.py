"""
Content Catalog page - Browse and filter articles
"""
import streamlit as st
import pandas as pd
from utils.ui_helpers import create_header, create_badge
from utils.api_client import get_api_client

def render_page():
    """Render content catalog page"""
    create_header(
        "Content Catalog",
        "Browse, filter, and explore all available articles from the MIND dataset"
    )
    
    client = get_api_client()
    
    # Initialize session state for filters if not present
    if 'catalog_page' not in st.session_state:
        st.session_state.catalog_page = 1
        
    # Search and filters
    st.markdown("### Search & Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input(
            "Search articles",
            placeholder="Search by title or keywords",
            key="catalog_search"
        )
    
    with col2:
        # We could fetch these categories dynamically if we had an endpoint
        categories = ["news", "sports", "finance", "lifestyle", "weather", "travel", "autos"] 
        category_filter = st.selectbox(
            "Category",
            ["All"] + categories,
            key="catalog_category"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["recent", "popular", "title"],
            key="catalog_sort"
        )
    
    st.divider()
    
    # Pagination controls
    items_per_page = 20
    current_page = st.session_state.catalog_page
    
    # Fetch Data
    category_param = None if category_filter == "All" else category_filter
    
    with st.spinner("Searching catalog..."):
        data = client.search_items(
            q=search_term,
            category=category_param,
            sort_by=sort_by,
            page=current_page,
            size=items_per_page
        )
        
    if not data:
        st.error("Failed to load catalog items.")
        return

    items = data.get('items', [])
    total_items = data.get('total', 0)
    
    # Display statistics
    st.caption(f"Found {total_items} articles (Page {current_page} of {max(1, (total_items + items_per_page - 1) // items_per_page)})")
    
    if not items:
        st.info("No articles found matching your criteria.")
    else:
        # Render Grid
        cols = st.columns(3)
        for idx, item in enumerate(items):
            col_idx = idx % 3
            with cols[col_idx]:
                with st.container(border=True):
                    # Title
                    title = item.get('title', 'Untitled')
                    if len(title) > 60:
                        title = title[:57] + "..."
                        
                    st.markdown(f"**{title}**")
                    
                    # Metadata
                    cat = item.get('category', 'General')
                    subcat = item.get('subcategory')
                    cat_display = f"{cat} > {subcat}" if subcat else cat
                    
                    st.caption(f"{item.get('views', 0)} views")
                    st.markdown(create_badge(cat_display, "primary"), unsafe_allow_html=True)
                    
                    st.write("") # spacer
                    
                    if st.button("Read", key=f"read_{item.get('item_id')}", use_container_width=True):
                        # Simple read action - in real app would go to detail page
                         st.info(f"Opening article: {item.get('item_id')}")
    
    st.divider()
    
    # Pagination Buttons
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if current_page > 1:
                if st.button("←", key="prev_page"):
                    st.session_state.catalog_page -= 1
                    st.rerun()
        with c2:
            if current_page < total_pages:
                if st.button("→", key="next_page"):
                    st.session_state.catalog_page += 1
                    st.rerun()

