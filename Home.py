import streamlit as st

st.set_page_config(
    page_title="News Recsys Platform",
    page_icon="📰",
    layout="wide",
)

st.title("News Recsys Platform – Overview")

st.markdown(
    """
    ## What is this?

    This is an **industry-style news recommendation system** built as my final-year project.

    **Key components:**
    - MIND-Large dataset (Microsoft News)
    - Multi-stage pipeline:
      - Candidate retrieval (deep model)
      - Ranking (deep click-prediction model)
      - Re-ranking (diversity, freshness)
    - Backend: FastAPI + PostgreSQL
    - UI: Streamlit

    **How to use this UI:**
    - Go to **'1_User_Simulator'** to:
      - Start a session
      - Request recommendations
      - Click on items (events logged to the backend)
    - Other pages:
      - **Content Catalog** – browse items
      - **Metrics** – system statistics
      - **User History** – inspect a specific user's activity.
    """
)