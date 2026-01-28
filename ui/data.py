import random

def mock_recommendations():
    return [
        {
            "item_id": i,
            "title": f"Sample News Article {i}",
            "retrieval_score": round(random.random(), 3),
            "rank_score": round(random.random(), 3)
        }
        for i in range(1, 11)
    ]
