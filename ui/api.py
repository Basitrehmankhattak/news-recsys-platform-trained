import requests

BACKEND_URL = "http://localhost:8000"

def get_recommendations(
    anonymous_id: str,
    session_id: str,
    page_size: int = 10,
    surface: str = "home",
    category: str | None = None
):
    payload = {
        "anonymous_id": anonymous_id,
        "session_id": session_id,
        "page_size": page_size,
        "surface": surface,
        "category": category
    }

    try:
        r = requests.post(
            f"{BACKEND_URL}/recommendations",
            json=payload,
            timeout=5
        )

        if r.status_code == 200:
            data = r.json()
            return data.get("items", []), data.get("impression_id")

    except Exception as e:
        print("Recommendation error:", e)

    return [], None
