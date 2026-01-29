from fastapi import APIRouter
from backend.app.db import get_conn

router = APIRouter(prefix="/trending", tags=["Trending"])

@router.get("/")
def get_trending(limit: int = 10):

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                it.item_id,
                it.title,
                COUNT(c.click_id) AS clicks
            FROM clicks c
            JOIN impressions_served i
                ON i.impression_id = c.impression_id
            JOIN items it
                ON it.item_id = c.item_id
            GROUP BY it.item_id, it.title
            ORDER BY clicks DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()

    return [
        {"item_id": r[0], "title": r[1], "clicks": r[2]}
        for r in rows
    ]
