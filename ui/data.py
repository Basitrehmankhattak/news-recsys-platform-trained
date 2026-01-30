import random
import uuid

def mock_recommendations(n: int = 10):
    """
    Generates fake recommendations matching backend schema.
    Useful for offline UI testing.
    """

    impression_id = str(uuid.uuid4())

    items = []

    for pos in range(1, n + 1):
        items.append({
            "item_id": f"MOCK_{pos}",
            "title": f"Sample News Article {pos}",
            "position": pos,
            "retrieval_score": round(random.random(), 3),
            "rank_score": round(random.random(), 3),
            "final_score": round(random.random(), 3)
        })

    return items, impression_id
