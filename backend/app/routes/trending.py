from fastapi import APIRouter
from backend.app.db import get_conn

router = APIRouter(prefix="/trending", tags=["trending"])

@router.get("")
def get_trending(limit: int = 20):

    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    it.item_id,
                    it.title,
                    COUNT(c.item_id) AS clicks
                FROM items it
                LEFT JOIN clicks c
                    ON c.item_id = it.item_id
                GROUP BY it.item_id, it.title
                ORDER BY
                    COUNT(c.item_id) DESC,
                    MOD(
                        ABS(
                            hashtext(
                                it.item_id ||
                                FLOOR(EXTRACT(EPOCH FROM NOW()) / 1800)::text
                            )
                        ),
                        100000
                    )
                LIMIT %s
            """, (limit,))

            rows = cur.fetchall()

    return [
        {
            "item_id": r[0],
            "title": r[1],
            "clicks": r[2]
        }
        for r in rows
    ]
