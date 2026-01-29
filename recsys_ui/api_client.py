import os
import requests

class APIClient:
    def __init__(self):
        self.base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    def recommendations(self, payload: dict) -> dict:
        url = f"{self.base}/recommendations"
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def click(self, payload: dict) -> dict:
        url = f"{self.base}/click"
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        # Your ClickResponse is {"status": "..."}
        return r.json() if r.content else {"status": "ok"}
