from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{anonymous_id}")
def get_click_history(anonymous_id: str):

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.clicked_at,
                    it.item_id,
                    it.title
                FROM clicks c
                JOIN impressions_served i
                    ON i.impression_id = c.impression_id
                JOIN items it
                    ON it.item_id = c.item_id
                WHERE i.anonymous_id = %s
                ORDER BY c.clicked_at DESC
                LIMIT 50
                """,
                (anonymous_id,),
            )

            rows = cur.fetchall()

    return [
        {
            "item_id": r[1],
            "title": r[2],
            "clicked_at": r[0],
        }
        for r in rows
    ]
