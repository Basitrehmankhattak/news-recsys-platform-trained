import os
import requests
from typing import Any, Dict

DEFAULT_TIMEOUT = 15

class ApiClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def recommend(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(self._url("/recommendations"), json=payload, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def log_click(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(self._url("/click"), json=payload, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def get_recent_clicks(self, anonymous_id: str, limit: int = 1) -> Any:
        r = requests.get(self._url(f"/users/{anonymous_id}/recent_clicks"), params={"limit": limit}, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()
