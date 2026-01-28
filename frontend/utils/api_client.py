"""
API client for backend integration
"""
import requests
import streamlit as st
from typing import Optional, Dict, List

# Configuration
BACKEND_URL = "http://localhost:8000"  # Update based on your backend URL

class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def start_session(self, anonymous_id: str, device_type: str = "web", 
                     user_agent: str = None, referrer: str = None) -> Optional[str]:
        """Start a new session"""
        try:
            response = self.session.post(
                f"{self.base_url}/session/start",
                json={
                    "anonymous_id": anonymous_id,
                    "device_type": device_type,
                    "user_agent": user_agent,
                    "referrer": referrer
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("session_id")
        except requests.RequestException as e:
            # Backend session is optional - silently fail
            # st.error(f"Error starting session: {str(e)}")
            return None

    def get_recommendations(self, session_id: str, user_id: int = None, 
                          anonymous_id: str = None, limit: int = 10) -> Optional[Dict]:
        """Get personalized recommendations"""
        try:
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "anonymous_id": anonymous_id,
                "page_size": limit,
                "surface": "home"
            }
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=payload,
                timeout=10
            )
            # Handle 400 bad request (e.g. cold start with no items) gracefully if needed
            if response.status_code == 400:
                st.warning("No recommendations available at this time.")
                return None
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Backend recommendations are optional - silently fail
            # st.error(f"Error fetching recommendations: {str(e)}")
            return None
    
    def record_click(self, impression_id: str, item_id: str, position: int, 
                    dwell_ms: int = 0, open_type: str = "click") -> bool:
        """Record user click on article"""
        try:
            response = self.session.post(
                f"{self.base_url}/click",
                json={
                    "impression_id": impression_id,
                    "item_id": item_id,
                    "position": position,
                    "dwell_ms": dwell_ms,
                    "open_type": open_type
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            # Silent fail for analytics is often better than error popup
            print(f"Could not record click: {str(e)}")
            return False
    
    def get_user_history(self, user_id: int, limit: int = 50) -> Optional[List[Dict]]:
        """Get user interaction history"""
        # This endpoint might need updates later, depending on backend implementation
        # For now keeping as is but aware it might fail if backend changed
        try:
            response = self.session.get(
                f"{self.base_url}/session/{user_id}/history",
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # st.error(f"Error fetching history: {str(e)}") 
            return None
    
    def get_content_info(self, article_id: str) -> Optional[Dict]:
        """Get article information"""
        try:
            response = self.session.get(
                f"{self.base_url}/content/{article_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # st.error(f"Error fetching content: {str(e)}")
            return None
    
    def get_user_history(self, anonymous_id: str, limit: int = 50) -> Optional[List[Dict]]:
        """Get user reading history"""
        try:
            response = self.session.get(
                f"{self.base_url}/users/{anonymous_id}/history",
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def get_user_analytics(self, anonymous_id: str) -> Optional[Dict]:
        """Get personalized analytics"""
        try:
            response = self.session.get(
                f"{self.base_url}/users/{anonymous_id}/analytics",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def get_system_analytics(self) -> Optional[Dict]:
        """Get system-wide analytics"""
        try:
            response = self.session.get(
                f"{self.base_url}/analytics/system",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def get_trending_analytics(self) -> Optional[Dict]:
        """Get trending analytics"""
        try:
            response = self.session.get(
                f"{self.base_url}/analytics/trending",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def search_items(self, q: str = None, category: str = None, sort_by: str = "recent", page: int = 1, size: int = 20) -> Optional[Dict]:
        """Search and filter items"""
        try:
            params = {
                "sort_by": sort_by,
                "page": page,
                "size": size
            }
            if q:
                params["q"] = q
            if category:
                params["category"] = category
                
            response = self.session.get(
                f"{self.base_url}/items",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def get_user_stats(self, anonymous_id: str) -> Optional[Dict]:
        """Get user statistics"""
        try:
            response = self.session.get(
                f"{self.base_url}/users/{anonymous_id}/stats",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return None

    def get_user_settings(self, anonymous_id: str) -> Optional[Dict]:
        """Get user settings"""
        try:
            response = self.session.get(
                f"{self.base_url}/settings/{anonymous_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def update_user_settings(self, anonymous_id: str, settings: Dict) -> bool:
        """Update user settings"""
        try:
            # ensure anonymous_id is in payload
            settings['anonymous_id'] = anonymous_id
            
            response = self.session.post(
                f"{self.base_url}/settings/{anonymous_id}",
                json=settings,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False


@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance"""
    return APIClient()
