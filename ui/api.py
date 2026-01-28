import requests

BACKEND_URL = "http://localhost:8000"

def get_recommendations(user_id, session_id, page_size=10):
    payload = {
        "anonymous_id": user_id,
        "session_id": session_id,
        "page_size": page_size
    }

    try:
        r = requests.post(f"{BACKEND_URL}/recommendations", json=payload, timeout=3)
        if r.status_code == 200:
            return r.json()["items"]
    except Exception:
        pass

    return []
