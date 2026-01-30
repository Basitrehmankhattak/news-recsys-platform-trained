from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn

router = APIRouter(prefix="/personalized", tags=["personalized"])

@router.get("/{anonymous_id}")
def get_personalized(anonymous_id: str):

    if not anonymous_id:
        raise HTTPException(400, "anonymous_id required")

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    it.item_id,
                    it.title,
                    it.category,
                    MAX(c.clicked_at) AS last_click
                FROM clicks c
                JOIN items it
                    ON it.item_id = c.item_id
                WHERE c.anonymous_id = %s
                GROUP BY it.item_id, it.title, it.category
                ORDER BY last_click DESC
                LIMIT 50
            """, (anonymous_id,))

            rows = cur.fetchall()

    return [
        {
            "item_id": r[0],
            "title": r[1],
            "category": r[2]
        }
        for r in rows
    ]
