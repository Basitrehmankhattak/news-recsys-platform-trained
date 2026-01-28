"""
UI styling and layout utilities
"""
import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        :root {
            --primary-color: #0066cc;
            --secondary-color: #00a8e8;
            --success-color: #2ecc71;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
            --light-bg: #f8f9fa;
            --dark-text: #2c3e50;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
        }
        
        .main {
            padding: 2rem;
        }
        
        .stButton > button {
            width: 100%;
            padding: 0.75rem;
            font-size: 1rem;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .stTextInput > div > div > input,
        .stPasswordInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            padding: 0.75rem;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
            border-radius: 12px;
            color: white;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        
        .alert-box {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid;
        }
        
        .alert-success {
            background-color: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        
        .alert-error {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        
        .alert-info {
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
            color: #0c5460;
        }
        
        .card-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .news-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .news-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }
        
        .news-card-header {
            padding: 1rem;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .news-card-body {
            padding: 1rem;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .badge-primary {
            background-color: #0066cc;
            color: white;
        }
        
        .badge-success {
            background-color: #28a745;
            color: white;
        }
        
        .badge-warning {
            background-color: #ffc107;
            color: #333;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .sidebar-header {
            padding: 1.5rem;
            background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .metric-box {
            text-align: center;
            padding: 1.5rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0066cc;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            font-weight: 500;
        }

        /* Hide Streamlit Header Anchor Links */
        .stMarkdown a.anchor-link,
        [data-testid="stMarkdownContainer"] a.anchor-link,
        .stMarkdown h1 a,
        .stMarkdown h2 a,
        .stMarkdown h3 a,
        .stMarkdown h4 a,
        .stMarkdown h5 a,
        .stMarkdown h6 a,
        [data-testid="stHeaderActionElements"] {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
            border-right: none !important;
        }
        
        /* Hide sidebar resize handle */
        div[data-testid="stSidebarUserContent"] {
            padding-top: 2rem;
        }
        
        div[data-testid="stSidebar"] > div:first-child {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

def create_header(title: str, subtitle: str = "", user_name: str = ""):
    """Create a professional header"""
    col1, col2 = st.columns([0.8, 0.2])
    
    with col1:
        st.markdown(f"""
            <div style='padding: 2rem; background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%); 
            border-radius: 12px; color: white; margin-bottom: 2rem;'>
                <h1 style='margin: 0; font-size: 2.5rem;'>{title}</h1>
                {f"<p style='margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;'>{subtitle}</p>" if subtitle else ""}
            </div>
        """, unsafe_allow_html=True)
    
    if user_name:
        with col2:
            st.markdown(f"""
                <div style='padding: 2rem; background: white; border-radius: 12px; 
                text-align: right; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);'>
                    <p style='margin: 0; color: #666;'>Welcome back</p>
                    <h3 style='margin: 0.5rem 0 0 0; color: #0066cc;'>{user_name}</h3>
                </div>
            """, unsafe_allow_html=True)

def create_metric_card(label: str, value, unit: str = "", color: str = "primary"):
    """Create a metric card"""
    colors = {
        "primary": "#0066cc",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545"
    }
    
    return st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 10px; 
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); margin: 0.5rem 0;'>
            <p style='margin: 0; color: #666; font-size: 0.9rem;'>{label}</p>
            <h2 style='margin: 0.5rem 0 0 0; color: {colors.get(color, "#0066cc")}; font-size: 2rem;'>
                {value}{unit}
            </h2>
        </div>
    """, unsafe_allow_html=True)

def create_alert(message: str, alert_type: str = "info"):
    """Create an alert box"""
    icons = {
        "success": "",
        "error": "",
        "warning": "",
        "info": ""
    }
    
    colors = {
        "success": "#d4edda",
        "error": "#f8d7da",
        "warning": "#fff3cd",
        "info": "#d1ecf1"
    }
    
    border_colors = {
        "success": "#28a745",
        "error": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8"
    }
    
    st.markdown(f"""
        <div style='background-color: {colors.get(alert_type, colors["info"])}; 
        border-left: 4px solid {border_colors.get(alert_type, border_colors["info"])}; 
        padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
            <strong>{alert_type.upper()}</strong><br>
            {message}
        </div>
    """, unsafe_allow_html=True)

def create_badge(text: str, badge_type: str = "primary"):
    """Create a badge"""
    colors = {
        "primary": "#0066cc",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545"
    }
    
    text_color = "white" if badge_type != "warning" else "#333"
    
    return f"""
    <span style='display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; 
    font-size: 0.85rem; font-weight: 600; background-color: {colors.get(badge_type, colors["primary"])}; 
    color: {text_color};'>{text}</span>
    """
