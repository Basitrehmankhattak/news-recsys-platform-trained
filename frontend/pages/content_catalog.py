"""
Content Catalog page - Browse and filter articles
"""
import streamlit as st
import pandas as pd
from utils.ui_helpers import create_header, create_badge

# Sample articles data
ARTICLES_DB = pd.DataFrame({
    'ID': ['N1001', 'N1002', 'N1003', 'N1004', 'N1005', 'N1006', 'N1007', 'N1008', 'N1009', 'N1010',
           'N1011', 'N1012', 'N1013', 'N1014', 'N1015', 'N1016', 'N1017', 'N1018', 'N1019', 'N1020'],
    'Title': [
        'AI Models in Medical Diagnosis', 'Stock Market All-Time High', 'Battery Technology Breakthrough',
        'Championship Victory in Final', 'Cloud Computing in Enterprise', 'Climate Summit Targets',
        'Quantum Computing Advances', 'Tech Startup Funding', 'Healthcare Innovation', 'Sports League Rules',
        '5G Network Expansion', 'Market Correction Analysis', 'EV Market Growth', 'Olympic Games Preview',
        'Cybersecurity Threats Report', 'E-commerce Trends 2025', 'Space Exploration News', 'FDA Approval',
        'Merger & Acquisition Deal', 'Gaming Industry Report'
    ],
    'Category': ['Technology', 'Business', 'Technology', 'Sports', 'Technology', 'World',
                 'Technology', 'Business', 'Health', 'Sports', 'Technology', 'Business',
                 'Technology', 'Sports', 'Technology', 'Business', 'Science', 'Health',
                 'Business', 'Technology'],
    'Entity': [
        'AI/Healthcare', 'Finance/Market', 'Energy/Tech', 'Sports/Soccer', 'Cloud/Enterprise',
        'Climate/Environment', 'Quantum/Computing', 'Startups/Tech', 'Healthcare/Innovation', 'Sports/Rules',
        '5G/Network', 'Finance/Market', 'EV/Energy', 'Sports/Olympics', 'Cybersecurity/Tech',
        'E-commerce/Retail', 'Space/Science', 'FDA/Health', 'Business/M&A', 'Gaming/Tech'
    ],
    'Published Date': ['2025-01-27', '2025-01-27', '2025-01-27', '2025-01-27', '2025-01-27',
                       '2025-01-27', '2025-01-26', '2025-01-26', '2025-01-26', '2025-01-26',
                       '2025-01-25', '2025-01-25', '2025-01-25', '2025-01-25', '2025-01-24',
                       '2025-01-24', '2025-01-24', '2025-01-24', '2025-01-23', '2025-01-23'],
    'Views': [2345, 3456, 1234, 5678, 2341, 1123, 890, 1234, 2345, 3456,
              4567, 2345, 3456, 4567, 2341, 3456, 1234, 2345, 5678, 1234],
    'Engagement': [0.92, 0.88, 0.85, 0.82, 0.87, 0.84, 0.81, 0.79, 0.86, 0.78,
                   0.89, 0.76, 0.91, 0.77, 0.88, 0.74, 0.80, 0.85, 0.75, 0.83]
})

def render_page():
    """Render content catalog page"""
    create_header(
        "Content Catalog",
        "Browse, filter, and explore all available articles from the MIND dataset"
    )
    
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
        category_filter = st.multiselect(
            "Category",
            ["Technology", "Business", "Sports", "World", "Health", "Science"],
            default=None,
            key="catalog_category"
        )
    
    with col3:
        date_filter = st.selectbox(
            "Published",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last Year"],
            key="catalog_date"
        )
    
    st.divider()
    
    # Advanced filters expander
    with st.expander("Advanced Filters"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            entity_filter = st.multiselect(
                "Entities",
                ["AI", "Healthcare", "Finance", "Cloud", "Energy", "Sports"],
                key="catalog_entity"
            )
        
        with col2:
            min_views = st.number_input(
                "Min Views",
                min_value=0,
                value=0,
                step=100,
                key="catalog_views"
            )
        
        with col3:
            min_engagement = st.slider(
                "Min Engagement",
                0.0, 1.0, 0.0,
                step=0.05,
                key="catalog_engagement"
            )
        
        with col4:
            sort_by = st.selectbox(
                "Sort By",
                ["Recent", "Most Views", "Engagement", "Title"],
                key="catalog_sort"
            )
    
    st.divider()
    
    # Filter articles
    filtered_df = ARTICLES_DB.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Title'].str.contains(search_term, case=False, na=False)]
    
    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    
    if min_views > 0:
        filtered_df = filtered_df[filtered_df['Views'] >= min_views]
    
    if min_engagement > 0:
        filtered_df = filtered_df[filtered_df['Engagement'] >= min_engagement]
    
    # Sort
    if 'sort_by' in st.session_state:
        sort_mapping = {
            "Recent": ("Published Date", False),
            "Most Views": ("Views", False),
            "Engagement": ("Engagement", False),
            "Title": ("Title", True)
        }
        if sort_by in sort_mapping:
            col, ascending = sort_mapping[sort_by]
            filtered_df = filtered_df.sort_values(by=col, ascending=ascending)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Results", len(filtered_df))
    with col2:
        st.metric("Avg Views", f"{filtered_df['Views'].mean():.0f}")
    with col3:
        st.metric("Avg Engagement", f"{filtered_df['Engagement'].mean():.2f}")
    with col4:
        st.metric("Date Range", f"{filtered_df['Published Date'].min()} to {filtered_df['Published Date'].max()}")
    
    st.divider()
    
    # Display mode selector
    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
    
    with col1:
        st.markdown(f"### Showing {len(filtered_df)} articles")
    
    with col2:
        view_mode = st.radio("View", ["List", "Grid"], horizontal=True, key="catalog_view")
    
    with col3:
        items_per_page = st.selectbox(
            "Per Page",
            [10, 20, 50],
            index=0,
            key="catalog_items"
        )
    
    st.divider()
    
    if len(filtered_df) == 0:
        st.warning("No articles found matching your criteria. Try adjusting your filters.")
    else:
        if view_mode == "List":
            render_list_view(filtered_df, items_per_page)
        else:
            render_grid_view(filtered_df, items_per_page)

def render_list_view(df: pd.DataFrame, items_per_page: int):
    """Render articles as list"""
    for idx, row in df.head(items_per_page).iterrows():
        col1, col2 = st.columns([0.8, 0.2])
        
        with col1:
            with st.container(border=True):
                # Title
                st.markdown(f"### {row['Title']}")
                
                # Metadata
                col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
                with col_meta1:
                    st.caption(f"{row['Published Date']}")
                with col_meta2:
                    st.caption(f"{row['Views']:,} views")
                with col_meta3:
                    st.caption(f"{row['Engagement']:.2f}")
                with col_meta4:
                    st.caption(f"ID: {row['ID']}")
                
                # Category and Entity
                st.markdown(f"**Category:** {create_badge(row['Category'], 'primary')} " +
                           f"**Entity:** {create_badge(row['Entity'], 'warning')}", unsafe_allow_html=True)
        
        with col2:
            if st.button("Read", key=f"read_{row['ID']}", use_container_width=True):
                st.info(f"Opening: {row['Title']}")
            if st.button("Save", key=f"save_{row['ID']}", use_container_width=True):
                st.success("Saved!")

def render_grid_view(df: pd.DataFrame, items_per_page: int):
    """Render articles as grid"""
    cols = st.columns(3)
    
    for idx, row in df.head(items_per_page).iterrows():
        col_idx = idx % 3
        
        with cols[col_idx]:
            with st.container(border=True):
                st.markdown(f"### Article")
                st.markdown(f"**{row['Title'][:40]}...**")
                st.caption(f"{row['Published Date']}")
                st.caption(f"{row['Views']:,} | {row['Engagement']:.2f}")
                st.markdown(f"__{row['Category']}__")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.button("Read", key=f"grid_read_{row['ID']}", use_container_width=True)
                with col_btn2:
                    st.button("Save", key=f"grid_save_{row['ID']}", use_container_width=True)

# Data Statistics Section
def render_statistics():
    """Render dataset statistics"""
    st.markdown("### MIND Dataset Statistics")
    
    stats_data = {
        'Total Articles': '160,000+',
        'Total Users': '1,000,000+',
        'Impression Logs': '15,000,000+',
        'Languages': 'English',
        'Data Collection': 'Microsoft News Website',
        'Time Period': '2019-2020'
    }
    
    col1, col2, col3 = st.columns(3)
    
    for idx, (key, value) in enumerate(stats_data.items()):
        if idx % 3 == 0:
            col_to_use = col1
        elif idx % 3 == 1:
            col_to_use = col2
        else:
            col_to_use = col3
        
        with col_to_use:
            st.metric(key, value)
